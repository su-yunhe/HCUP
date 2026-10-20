"""Real UI/hdc/NetLog observations, with no application-state injection."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import time

from hypium import BY
from harness.driver import HarnessTestCase

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEVICE = "127.0.0.1:11241"
BUNDLE = "com.joker.coolmall"
GOODS_URL = "https://mall.dusksnow.top/app/goods/info/page"
TAG_LINE = re.compile(r"^\S+\s+\S+\s+(\d+)\s+\d+\s+\w\s+\S*/NetLog: ?(.*)$")
CARD_ID = re.compile(r"^gc\.goods\.(\d+)$")


def read_events(raw: str, pid: str | None = None) -> list[dict]:
    """Reassemble the existing interceptor's pretty JSON and 800-char chunks.

    Unfinished JSON stays incomplete. Concurrent identical URLs are explicitly
    ambiguous; no FIFO response claim is made for an out-of-order case.
    """
    events = []
    event = None
    for line in raw.splitlines():
        match = TAG_LINE.match(line)
        if not match or (pid and match[1] != pid):
            continue
        message = match[2]
        if message.startswith("[Network] "):
            event = {"kind": message[len("[Network] "):], "pid": match[1], "ordinal": len(events), "lines": []}
            events.append(event)
        elif event is not None:
            event["lines"].append(message)
    for event in events:
        event["data"] = None
        event["complete"] = False
        data_lines = []
        reading_data = False
        for line in event["lines"]:
            if not reading_data:
                key, sep, value = line.partition("=")
                if key in {"method", "url", "status", "params", "message"} and sep:
                    event[key] = value
                elif key == "data" and sep:
                    reading_data = True
                    data_lines.append(value)
            else:
                data_lines.append(line)
        if reading_data:
            text = "".join(data_lines)
            try:
                event["data"] = json.loads(text)
                event["complete"] = True
            except (ValueError, TypeError):
                event["data_raw"] = text
                # Undefined body is valid only for no-body requests.
                if text == "undefined":
                    event["complete"] = True
        event.pop("lines")
    return events


def page_pairs(events: list[dict]) -> list[dict]:
    pending = []
    pairs = []
    for event in events:
        if event.get("url") != GOODS_URL:
            continue
        if event["kind"] == "Request":
            pending.append(event)
        elif event["kind"] in {"Response", "Response Error"}:
            if len(pending) == 1:
                pairs.append({"request": pending.pop(), "response": event, "ambiguous": False})
            elif pending:
                pairs.append({"requests": pending.copy(), "response": event, "ambiguous": True})
                pending.clear()
    return pairs


def walk_visible(tree: dict, visible: bool = True):
    attrs = tree.get("attributes", {})
    visible = visible and attrs.get("visible", "true") != "false" and attrs.get("opacity", "1") not in {"0", "0.000000"}
    if visible:
        yield attrs
    for child in tree.get("children", []):
        yield from walk_visible(child, visible)


def rect(attrs: dict) -> tuple[int, int, int, int]:
    values = [int(x) for x in re.findall(r"-?\d+", attrs.get("bounds", ""))]
    return tuple(values) if len(values) == 4 else (0, 0, 0, 0)


def displayed(attrs: dict) -> bool:
    left, top, right, bottom = rect(attrs)
    return right > left and bottom > top and right > 0 and left < 1308 and bottom > 137 and top < 2880


class ObservedGoodsCase(HarnessTestCase):
    """A new app process and independent raw evidence directory per test."""

    @classmethod
    def setUpClass(cls):
        if cls.device_sn != DEVICE:
            raise RuntimeError(f"Only the task's isolated emulator {DEVICE} is authorized")
        receipt_path = os.environ.get("CMLSPEC24_INSTALL_RECEIPT")
        if not receipt_path:
            raise RuntimeError("Set CMLSPEC24_INSTALL_RECEIPT after installing this run's freshly built HAP")
        receipt = json.loads(pathlib.Path(receipt_path).read_text(encoding="utf-8-sig"))
        hap = pathlib.Path(receipt["hap_path"])
        if receipt.get("device") != DEVICE or receipt.get("install_exit_code") != 0:
            raise RuntimeError("Installation receipt has wrong device or unsuccessful install")
        if receipt.get("install_semantic_success") is not True:
            raise RuntimeError("Installation receipt must confirm native hdc success text, not exit code alone")
        if hashlib.sha256(hap.read_bytes()).hexdigest() != receipt["hap_sha256"]:
            raise RuntimeError("Installed-HAP receipt no longer matches the current artifact")
        cls.install_receipt = receipt
        super().setUpClass()

    def record(self, action: str, **values):
        record = {"utc": dt.datetime.now(dt.timezone.utc).isoformat(), "action": action, **values}
        with (self.out / "actions.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")

    def hdc(self, *args, check=True):
        command = [shutil.which("hdc") or "hdc", "-t", DEVICE, *args]
        started = dt.datetime.now(dt.timezone.utc).isoformat()
        result = subprocess.run(command, capture_output=True, timeout=35)
        self.command_index += 1
        label = f"command-{self.command_index:03d}"
        (self.out / (label + ".stdout.log")).write_bytes(result.stdout)
        (self.out / (label + ".stderr.log")).write_bytes(result.stderr)
        self.record("hdc", command=command, exit_code=result.returncode, started_utc=started, evidence=label)
        if check:
            self.assertEqual(result.returncode, 0, f"hdc failed: {command}; see {label}")
        return result.stdout.decode("utf-8", errors="replace")

    def setUp(self):
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        self.out = ROOT / "logs/development/hypium" / (stamp + "-" + self._testMethodName)
        self.out.mkdir(parents=True)
        self.command_index = 0
        self.stream_process = None
        self.stream_stdout = None
        self.stream_stderr = None
        self.pid = None
        self.record("installation-receipt", receipt=self.install_receipt)
        self.driver.stop_app(BUNDLE)
        self.record("stop-app", bundle=BUNDLE)
        # Preserve the old app buffer before clearing this isolated device's app logs.
        self.hdc("shell", "hilog", "-x", "-t", "app")
        self.hdc("shell", "hilog", "-r", "-t", "app")
        self.hdc("shell", "hilog", "-Q", "pidoff")
        self.hdc("shell", "hilog", "-Q", "domainoff")
        command = [shutil.which("hdc") or "hdc", "-t", DEVICE, "shell", "hilog", "-T", "NetLog"]
        self.stream_stdout = (self.out / "netlog.raw.log").open("wb")
        self.stream_stderr = (self.out / "netlog.stderr.log").open("wb")
        self.stream_process = subprocess.Popen(command, stdout=self.stream_stdout, stderr=self.stream_stderr)
        self.record("netlog-start", command=command, local_pid=self.stream_process.pid)
        time.sleep(0.3)
        self.driver.start_app(BUNDLE, "EntryAbility", wait_time=2)
        self.record("start-app", bundle=BUNDLE, ability="EntryAbility")
        self.pid = self.hdc("shell", "pidof", BUNDLE).strip().split()[0]
        self.require_component(BY.key("gc.entry.home.search"), "Home search entry missing", timeout=25)

    def tearDown(self):
        try:
            self.snapshot("final")
            events = self.events()
            (self.out / "netlog.events.json").write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding="utf-8")
            (self.out / "netlog.page-pairs.json").write_text(json.dumps(page_pairs(events), ensure_ascii=False, indent=2), encoding="utf-8")
            if self.pid:
                self.hdc("shell", "hilog", "-x", "-P", self.pid, "-L", "E,F", check=False)
        finally:
            if self.stream_process is not None:
                self.stream_process.terminate()
                try:
                    code = self.stream_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.stream_process.kill()
                    code = self.stream_process.wait(timeout=5)
                self.record("netlog-stop", local_pid=self.stream_process.pid, exit_code=code)
            if self.stream_stdout:
                self.stream_stdout.close()
            if self.stream_stderr:
                self.stream_stderr.close()
            self.hdc("shell", "hilog", "-Q", "pidon", check=False)
            self.hdc("shell", "hilog", "-Q", "domainon", check=False)

    def events(self):
        if self.stream_process is not None and self.stream_process.poll() is not None:
            self.fail("Live NetLog capture exited unexpectedly; absence of logs is not evidence of no request")
        return read_events((self.out / "netlog.raw.log").read_text(encoding="utf-8", errors="replace"), self.pid)

    def requests(self):
        return [event for event in self.events() if event.get("url") == GOODS_URL and event["kind"] == "Request"]

    def wait_page(self, expected: dict, after: int = 0, timeout=25):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            pairs = page_pairs(self.events())
            for pair in pairs:
                if pair["ambiguous"]:
                    continue
                request, response = pair["request"], pair["response"]
                all_requests = self.requests()
                if request not in all_requests[after:]:
                    continue
                body = request.get("data")
                if isinstance(body, dict) and all(body.get(k) == v for k, v in expected.items()) and response.get("complete"):
                    self.assertEqual(request.get("method"), "POST")
                    self.assertEqual(response.get("status"), "200", "App request did not return HTTP200")
                    self.assertEqual(response["data"].get("code"), 1000, "App request business failure")
                    self.last_page = pair
                    self.record("matched-real-page", request=body, pagination=response["data"]["data"].get("pagination"))
                    return pair
            self.driver.wait(0.2)
        self.fail(f"No complete, unambiguous real request/response for {expected} after request {after}; see NetLog")

    def click(self, key: str):
        component = self.require_component(BY.key(key), f"Missing {key}")
        self.record("click", key=key)
        self.driver.click(component)
        self.driver.wait(0.15)

    def input(self, key: str, value: str):
        component = self.require_component(BY.key(key), f"Missing input {key}")
        if component.getType() not in {"TextInput", "Search"}:
            bound = component.getBounds()
            candidates = []
            for child in self.driver.find_all_components(BY.type("TextInput")) or []:
                child_bound = child.getBounds()
                if child_bound.left >= bound.left and child_bound.right <= bound.right and child_bound.top >= bound.top and child_bound.bottom <= bound.bottom:
                    candidates.append(child)
            self.assertEqual(len(candidates), 1, f"{key} must contain one native TextInput")
            component = candidates[0]
        self.record("input", key=key, value=value)
        self.driver.input_text(component, value)

    def snapshot(self, label: str):
        remote = "/data/local/tmp/cmlspec24-" + label + ".json"
        self.hdc("shell", "uitest", "dumpLayout", "-p", remote)
        self.hdc("file", "recv", remote, str(self.out / (label + ".json")))
        image_remote = "/data/local/tmp/cmlspec24-" + label + ".png"
        self.hdc("shell", "uitest", "screenCap", "-p", image_remote)
        self.hdc("file", "recv", image_remote, str(self.out / (label + ".png")))
        self.assertTrue((self.out / (label + ".png")).is_file(), "Screen capture did not create the local PNG")
        return [attrs for attrs in walk_visible(json.loads((self.out / (label + ".json")).read_text(encoding="utf-8"))) if displayed(attrs)]

    def assert_top_cards(self, pair: dict, label: str):
        rows = pair["response"]["data"]["data"]["list"]
        self.assertTrue(rows, "Nonempty precondition unavailable in real response")
        self.require_component(BY.key("gc.goods." + str(rows[0]["id"])), "First real-response item missing in UI")
        nodes = self.snapshot(label)
        cards = [node for node in nodes if CARD_ID.fullmatch(node.get("key") or node.get("id", ""))]
        cards.sort(key=lambda node: (rect(node)[1], rect(node)[0]))
        actual = [int(CARD_ID.fullmatch(node.get("key") or node["id"])[1]) for node in cards]
        self.assertTrue(actual, "No visible goods cards")
        expected = [row["id"] for row in rows]
        self.assertEqual(actual, expected[:len(actual)], "Visible UI order does not match the actual response prefix")
        by_id = {(node.get("key") or node.get("id")): node for node in nodes}
        complete_cards = []
        for goods_id in actual:
            card = by_id["gc.goods." + str(goods_id)]
            if card.get("origBounds") and card["origBounds"] != card.get("bounds"):
                continue  # A clipped image-only card is valid; inspect its metadata after scrolling.
            complete_cards.append(card)
            row = next(row for row in rows if row["id"] == goods_id)
            self.assertIn("gc.image." + str(goods_id), by_id)
            self.assertEqual(by_id["gc.name." + str(goods_id)].get("text"), row["title"])
            self.assertIn("gc.price." + str(goods_id), by_id)
        self.assertTrue(complete_cards, "No complete card available for image/name/price assertions")
        return complete_cards

    def filter_tag(self, category_id: int, label: str, click=True):
        key = "gc.filter.tag." + str(category_id)
        for direction in ["UP", "DOWN"]:
            for _ in range(9):
                component = self.find_or_none(BY.key(key), timeout=0.3)
                region = self.require_component(BY.key("gc.filter.scroll"), "Missing filter scroll").getBounds()
                if component is not None:
                    bounds = component.getBounds()
                    if bounds.top >= region.top and bounds.bottom <= region.bottom and bounds.bottom > bounds.top:
                        self.snapshot(label + "-before")
                        if click:
                            self.click(key)
                            self.snapshot(label + "-after")
                            self.assertTrue(self.require_component(BY.key(key), key).isSelected(), "Selected tag needs selected semantics")
                        return self.require_component(BY.key(key), key)
                self.record("filter-scroll", direction=direction)
                self.driver.swipe(direction, distance=65, area=BY.key("gc.filter.scroll"))
        self.fail(f"Real tag {category_id} not reachable in filter scroll")

    def wait_quiet(self, seconds=0.8):
        self.driver.wait(seconds)
        self.events()  # Assert the capture is alive even for zero-request checks.

    def dismiss_keyboard(self):
        label = "keyboard-check-" + str(self.command_index)
        nodes = self.snapshot(label)
        if any(node.get("bundleName") == "com.huawei.hmos.inputmethod" for node in nodes):
            self.record("system-back", reason="Dismiss observed system IME, not filter menu")
            self.driver.press_back()
            self.driver.wait(0.3)
            self.require_component(BY.key("gc.filter.panel"), "IME dismissal unexpectedly closed filter")
            nodes = self.snapshot(label + "-dismissed")
            self.assertFalse(any(node.get("bundleName") == "com.huawei.hmos.inputmethod" for node in nodes))

    def close_filter_mask(self):
        mask = self.require_component(BY.key("gc.filter.mask"), "Mask missing").getBounds()
        panel = self.require_component(BY.key("gc.filter.panel"), "Panel missing").getBounds()
        self.assertGreater(mask.bottom, panel.bottom + 2, "No exposed mask area below dropdown")
        point = ((mask.left + mask.right) // 2, (panel.bottom + mask.bottom) // 2)
        self.record("click-mask-outside-panel", point=point)
        self.driver.click(point)

    def return_to_first(self, goods_id: int, container: str):
        before = len(self.requests())
        for _ in range(24):
            item = self.find_or_none(BY.key("gc.goods." + str(goods_id)), timeout=0.25)
            region = self.require_component(BY.key(container), container).getBounds()
            if item is not None:
                bound = item.getBounds()
                if bound.top >= region.top and bound.top < region.bottom and bound.bottom > bound.top:
                    self.assertEqual(len(self.requests()), before, "Returning to old first-page data caused a new query")
                    return
            self.driver.swipe("DOWN", distance=70, area=BY.key(container))
            self.driver.wait(0.1)
        self.fail("First-page item was lost after appending later pages")

    @staticmethod
    def visible_card_ids(nodes):
        cards = [node for node in nodes if CARD_ID.fullmatch(node.get("key") or node.get("id", ""))]
        cards.sort(key=lambda node: (rect(node)[1], rect(node)[0]))
        return [int(CARD_ID.fullmatch(node.get("key") or node["id"])[1]) for node in cards]

    def enter_home_category(self):
        before = len(self.requests())
        self.click("gc.entry.home.category.800001")
        self.require_component(BY.key("gc.page"), "Home category did not navigate to goods/category")
        return self.wait_page({"page": 1}, after=before)

    def enter_all(self):
        self.enter_home_category()
        self.click("gc.filter.trigger")
        self.click("gc.filter.reset")
        before = len(self.requests())
        self.click("gc.filter.confirm")
        pair = self.wait_page({"page": 1}, after=before)
        for key in ["typeId", "minPrice", "maxPrice", "keyWord", "featured", "recommend", "order", "sort"]:
            self.assertNotIn(key, pair["request"]["data"], f"Reset all should omit {key}")
        return pair
