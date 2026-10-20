"""Observable vg-spec14 checks, executed only after source/device handoff.

Run from logs/ with common's harness.runner. The wrapper must install the freshly
built HAP, create rport 18164, set VG14_TEST_AUTHORIZED=1 and freeze production.
No device operation happens during import or offline discovery.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import threading
import time
from pathlib import Path

from hypium import BY
from hypium.model.basic_data_type import InputTextMode
from harness.driver import HarnessTestCase

from .webdav_fixture import WebDavFixture, utc

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = "io.qzz.weiyu"
IDS = {
    "home": "home_settings_entry", "entry": "settings_webdav_entry",
    "page": "webdav_config_page", "endpoint": "webdav_endpoint_input",
    "username": "webdav_username_input", "password": "webdav_password_input",
    "sync_password": "webdav_sync_password_input", "remote": "webdav_remote_root_input",
    "sync": "webdav_sync_now_button", "loading": "webdav_sync_loading",
    "result": "webdav_action_result", "back": "settings_back_button",
    "test": "webdav_test_button", "auto": "webdav_auto_sync_toggle",
    "save": "webdav_save_button",
}


def source_fingerprint() -> dict[str, str]:
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    paths = {p for p in names if p.startswith(("entry/src/", "AppScope/"))
             or p.endswith((".json5", "hvigorfile.ts"))}
    for path in (ROOT / "entry/src").rglob("*"):
        if path.is_file():
            paths.add(path.relative_to(ROOT).as_posix())
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
            for name in sorted(paths) if (ROOT / name).is_file()}


class WebDavSyncTests(HarnessTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if os.environ.get("VG14_TEST_AUTHORIZED") != "1":
            raise RuntimeError("Source freeze and device handoff required: VG14_TEST_AUTHORIZED=1")
        cls.evidence = Path(os.environ.get("VG14_EVIDENCE", ROOT / "logs/do-validation/device-run-v1"))
        cls.evidence.mkdir(parents=True, exist_ok=True)
        cls.before = source_fingerprint()
        cls.first_launch_ready = False
        (cls.evidence / "source-before.json").write_text(json.dumps(cls.before, indent=2), encoding="utf-8")
        cls.fixture = WebDavFixture(cls.evidence)
        try:
            super().setUpClass()
            cls.driver.set_implicit_wait_time(0.1)
        except BaseException:
            cls.fixture.close()
            raise

    @classmethod
    def tearDownClass(cls) -> None:
        cls.fixture.close()
        after = source_fingerprint()
        (cls.evidence / "source-after.json").write_text(json.dumps(after, indent=2), encoding="utf-8")
        if cls.before != after:
            raise AssertionError("Production fingerprint changed; affected evidence is invalid")

    def setUp(self) -> None:
        self.assertEqual(self.before, source_fingerprint(), "Source changed before test")
        self.fixture.release_all()
        try:
            self.driver.stop_app(BUNDLE)
            self.driver.start_app(BUNDLE, page_name="EntryAbility", wait_time=2)
            if not self.__class__.first_launch_ready:
                # Initial policy content loads asynchronously after the home entry.
                consent = self.find_or_none(BY.text("同意并进入"), timeout=6)
                if consent is not None:
                    self.event("first_launch_consent", text="同意并进入")
                    self.driver.click(consent)
                onboarding = self.find_or_none(BY.text("跳过"), timeout=3)
                if onboarding is not None:
                    self.event("first_launch_onboarding", text="跳过")
                    self.driver.click(onboarding)
            self.enter_from_home()
            self.__class__.first_launch_ready = True
        except BaseException:
            self.capture("setup-failed")
            raise

    def tearDown(self) -> None:
        try:
            self.fixture.release_all()
            self.capture("teardown", screenshot=False)
            self.assertEqual(self.before, source_fingerprint(), "Source changed; invalidate evidence")
        finally:
            self.fixture.release_all()

    def event(self, event: str, **values) -> dict:
        record = {"utc": utc(), "monotonic_ns": time.monotonic_ns(),
                  "test": self._testMethodName, "event": event, **values}
        with (self.evidence / "ui-events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
        return record

    def hdc(self, *arguments: str) -> str:
        args = ["hdc", "-t", self.device_sn or os.environ["HDC_DEVICE"], *arguments]
        start = utc()
        result = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=35)
        self.event("command", start=start, argv=args, exit_code=result.returncode,
                   stdout=result.stdout, stderr=result.stderr)
        self.assertEqual(result.returncode, 0, str(args) + result.stderr)
        self.assertNotRegex(result.stdout + result.stderr, r"(?i)\[fail\]|error:", "hdc failed despite zero exit")
        return result.stdout

    def component(self, name: str, scroll: bool = False):
        by = BY.key(IDS[name])
        if scroll:
            found = self.driver.find_component(by)
            if found is not None:
                return found
            # Use the documented gesture for the known form/action regions first;
            # retain the exact stable selector and native scrollSearch fallback.
            direction = "DOWN" if name in ("endpoint", "username", "password", "sync_password", "remote") else "UP"
            self.driver.swipe(direction, distance=80, area=BY.type("Scroll"), swipe_time=0.3)
            found = self.driver.find_component(by)
            if found is not None:
                return found
            found = self.driver.find_component(by, scroll_target=BY.type("Scroll"))
            if found is not None:
                return found
        return self.require_component(by, f"Missing selector {IDS[name]}", timeout=8)

    def enter_from_home(self) -> None:
        self.driver.click(self.component("home"))
        self.driver.click(self.component("entry", scroll=True))
        self.component("page")

    def configure(self, path: str = "endpoint-a", overrides: dict | None = None) -> None:
        values = {"endpoint": f"http://127.0.0.1:18164/{path}", "username": "vg14-local",
                  "password": "fixture-only", "sync_password": "fixture-sync-14", "remote": "/sync"}
        values.update(overrides or {})
        for name, value in values.items():
            comp = self.component(name, scroll=True)
            if value == "":
                self.driver.clear_text(comp)
                # clearText need not show the IME. Explicitly focus the same
                # empty input before Back, so Back dismisses only the keyboard.
                self.driver.click(self.component(name))
            else:
                self.driver.input_text(comp, value, mode=InputTextMode().paste(True))
            self.driver.go_back()  # dismiss the keyboard
        toggle = self.component("auto", scroll=True)
        if toggle.isChecked():
            self.driver.click(toggle)
        self.assertEqual(self.component("sync", scroll=True).getText(), "立即同步")
        self.event("configuration_ready", endpoint=values["endpoint"],
                   username_present=bool(values["username"].strip()), remote=values["remote"],
                   password_present=bool(values["password"]), sync_password_present=bool(values["sync_password"]))

    def capture(self, label: str, screenshot: bool = True) -> dict:
        stamp = str(time.monotonic_ns())
        stem = f"{self._testMethodName}-{label}-{stamp}"
        device_path = f"/data/local/tmp/vg14-{stamp}.json"
        start = self.event("capture_start", label=label)
        self.hdc("shell", "uitest", "dumpLayout", "-p", device_path)
        target = self.evidence / f"{stem}.json"
        self.hdc("file", "recv", device_path, str(target))
        tree = json.loads(target.read_text(encoding="utf-8-sig"))
        nodes: list[dict] = []

        def visit(node):
            if "attributes" in node:
                nodes.append(node["attributes"])
            for child in node.get("children", []):
                visit(child)

        visit(tree)
        keyed = {n.get("id"): n for n in nodes if n.get("id")}
        if screenshot:
            device_image = f"/data/local/tmp/vg14-{stamp}.jpeg"
            self.hdc("shell", "snapshot_display", "-f", device_image)
            self.hdc("file", "recv", device_image, str(self.evidence / f"{stem}.jpeg"))
        self.event("capture_end", label=label, start_ns=start["monotonic_ns"], file=target.name,
                   loading=keyed.get(IDS["loading"]), sync=keyed.get(IDS["sync"]))
        return keyed

    def assert_busy(self, label: str, require_visible_button: bool = True) -> dict:
        loading = self.component("loading")
        self.assertEqual(loading.getType(), "LoadingProgress")
        bound = loading.getBounds()
        self.assertGreater(bound.right - bound.left, 0)
        self.assertGreater(bound.bottom - bound.top, 0)
        width, height = self.driver.get_display_size()
        self.assertGreater(min(bound.right, width) - max(bound.left, 0), 0)
        self.assertGreater(min(bound.bottom, height) - max(bound.top, 0), 0)
        if require_visible_button:
            self.assertFalse(self.component("sync").isEnabled(), "Selected busy policy disables manual sync")
        keyed = self.capture(label)
        node = keyed.get(IDS["loading"])
        self.assertIsNotNone(node, "Loading component missing from raw UI tree")
        self.assertEqual(node.get("type"), "LoadingProgress")
        self.assertNotEqual(str(node.get("visible", "true")).lower(), "false")
        return keyed

    def wait_idle(self, timeout: float = 45) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            button = self.driver.find_component(BY.key(IDS["sync"]))
            loading = self.driver.find_component(BY.key(IDS["loading"]))
            if button is not None and button.isEnabled() and loading is None:
                self.event("idle_observed")
                self.capture("idle")
                return
            time.sleep(0.15)
        self.capture("idle-timeout")
        self.fail("Real operation did not restore idle within observation window")

    def begin(self, label: str, *, status: int | None = None,
              empty: bool = False, disconnect: bool = False,
              hold_seconds: float = 28) -> tuple[int, dict]:
        after = self.fixture.configure(gated=True, status=status, empty=empty, disconnect=disconnect,
                                       hold_seconds=hold_seconds)
        self.assertEqual(self.fixture.requests(after), [])
        self.event("manual_click", after_request=after, label=label)
        self.driver.click(self.component("sync", scroll=True))
        # Sample before waiting for the server, retaining a real temporal observation.
        loading = self.driver.find_component(BY.key(IDS["loading"]))
        self.event("early_loading_sample", label=label, found=loading is not None)
        request = self.fixture.wait_request(after)
        self.assert_busy(label)
        self.assertTrue(request["path"].startswith("/"))
        self.assertGreater(request["id"], after)
        return after, request

    def complete(self, reveal_button: bool = False) -> None:
        self.fixture.release_all()
        if reveal_button:
            self.component("sync", scroll=True)
        self.wait_idle()

    def test_01_first_empty_and_unchanged(self):
        self.configure()
        self.capture("configured")
        after, request = self.begin("first-empty", empty=True)
        self.assertIn("/endpoint-a/", request["path"])
        self.complete()
        self.assertTrue(self.fixture.requests(after), "Spinner without backend request is a failure")
        after, _ = self.begin("unchanged")
        self.complete()
        self.assertTrue(self.fixture.requests(after))

    def test_02_multistage(self):
        self.configure("multistage")
        _, first = self.begin("stage-one", empty=True)
        self.fixture.release(first["id"])
        second = self.fixture.wait_request(first["id"])
        self.assert_busy("stage-two")
        self.assertGreater(second["id"], first["id"])
        self.complete()
        # Fail after a successful preflight, exercising the main operation's cleanup.
        _, first = self.begin("partial-failure-first")
        self.fixture.configure(gated=True, status=500)
        self.fixture.release(first["id"])
        self.fixture.wait_request(first["id"])
        self.assert_busy("partial-failure-later")
        self.complete()
        self.begin("partial-failure-retry")
        self.complete()

    def test_03_http_failure_and_retry(self):
        self.configure("failure")
        for status in (401, 403, 500):
            with self.subTest(status=status):
                self.begin(f"http-{status}", status=status)
                self.complete()
                self.driver.click(self.component("back"))
                self.driver.click(self.component("entry", scroll=True))
                self.component("sync", scroll=True)
                after, _ = self.begin(f"retry-after-{status}")
                self.complete()
                self.assertTrue(self.fixture.requests(after))

    def test_04_disconnect_and_retry(self):
        self.configure("disconnect")
        self.begin("disconnect", disconnect=True)
        self.complete()
        self.begin("disconnect-retry")
        self.complete()

    def test_05_busy_and_rapid_clicks(self):
        self.configure("clicks")
        self.begin("repeat-before")
        button = self.component("sync")
        bounds = button.getBounds()
        coordinate = ((bounds.left + bounds.right) // 2, (bounds.top + bounds.bottom) // 2)
        for _ in range(5):
            self.driver.click(coordinate)
        self.assert_busy("repeat-after")
        self.complete()
        after = self.fixture.configure(gated=True)
        self.event("rapid_clicks", after_request=after)
        for _ in range(4):
            self.driver.click(coordinate)
        self.fixture.wait_request(after)
        self.assert_busy("rapid-clicks")
        self.complete()

    def test_06_busy_back_and_home_reentry(self):
        self.configure("reentry")
        for depth in (1, 2):
            with self.subTest(depth=depth):
                _, request = self.begin(f"before-back-{depth}")
                self.driver.click(self.component("back"))
                if depth == 2:
                    self.driver.click(self.component("back"))
                    self.driver.click(self.component("home"))
                self.driver.click(self.component("entry", scroll=True))
                self.component("page")
                request_age = (time.monotonic_ns() - request["monotonic_ns"]) / 1_000_000_000
                self.event("reentry_request_age", depth=depth, seconds=request_age)
                self.require_precondition(request_age < 16,
                                          "Navigation sampling approached existing HTTP timeout; rerun with faster observer")
                self.assertIn(request["id"], self.fixture.pending,
                              "Original request must still be held during same-process navigation")
                self.assert_busy(f"reentered-{depth}", require_visible_button=False)
                self.complete(reveal_button=True)
        _, request = self.begin("before-background")
        self.driver.swipe_to_home()
        self.driver.start_app(BUNDLE, page_name="EntryAbility", wait_time=0.5)
        self.component("page")
        request_age = (time.monotonic_ns() - request["monotonic_ns"]) / 1_000_000_000
        self.event("foreground_request_age", seconds=request_age)
        self.require_precondition(request_age < 16, "Foreground sampling approached the existing HTTP timeout")
        self.assertIn(request["id"], self.fixture.pending)
        self.assert_busy("after-foreground", require_visible_button=False)
        self.complete(reveal_button=True)

    def test_07_success_return_and_restart(self):
        self.configure("restart")
        self.begin("before-success-return")
        self.complete()
        self.driver.click(self.component("back"))
        self.driver.click(self.component("entry", scroll=True))
        self.component("sync", scroll=True)
        self.begin("after-success-return")
        self.complete()
        self.driver.stop_app(BUNDLE)
        self.driver.start_app(BUNDLE, page_name="EntryAbility", wait_time=2)
        self.enter_from_home()
        self.configure("restart-after")
        self.begin("after-restart")
        self.complete()
        self.begin("before-process-stop")
        self.driver.stop_app(BUNDLE)
        self.fixture.release_all()
        self.driver.start_app(BUNDLE, page_name="EntryAbility", wait_time=2)
        self.enter_from_home()
        self.configure("restart-after-interruption")
        self.begin("after-interrupted-restart")
        self.complete()

    def test_08_endpoint_switch(self):
        for path in ("chosen-a", "chosen-b/"):
            with self.subTest(path=path):
                self.configure(path)
                after, _ = self.begin(path.replace("/", ""))
                self.complete()
                requests = self.fixture.requests(after)
                self.assertTrue(requests)
                for request in requests:
                    self.assertTrue(request["path"].startswith("/" + path.rstrip("/") + "/"), request)

    def test_09_empty_and_spaces_recover(self):
        for value in ("", "   "):
            for field in ("endpoint", "username", "password", "sync_password", "remote"):
                self.event("invalid_group_start", field=field, value_kind="empty" if value == "" else "spaces")
                self.component("page")
                self.configure("invalid", {field: value})
                after = self.fixture.configure(gated=False)
                self.event("invalid_click", field=field, value_kind="empty" if value == "" else "spaces", after_request=after)
                self.driver.click(self.component("sync", scroll=True))
                self.wait_idle()
                self.event("invalid_result", field=field, requests=self.fixture.requests(after))
        self.configure("invalid-all", {name: "" for name in ("endpoint", "username", "password", "sync_password", "remote")})
        after = self.fixture.configure(gated=False)
        self.event("invalid_click", field="all", value_kind="empty", after_request=after)
        self.driver.click(self.component("sync", scroll=True))
        self.wait_idle()
        self.event("invalid_result", field="all", requests=self.fixture.requests(after))
        self.configure("recovered")
        self.begin("after-invalid-recovery")
        self.complete()

    def test_10_fast_response_timeline(self):
        self.configure("fast")
        proved = []
        for attempt in range(1, 6):
            after = self.fixture.configure(gated=False)
            button = self.component("sync", scroll=True)
            bounds = button.getBounds()
            display_width, display_height = self.driver.get_display_size()
            coordinate = ((bounds.left + bounds.right) // 2, (bounds.top + bounds.bottom) // 2)
            started = threading.Event()
            stopped = threading.Event()
            samples = []
            errors = []

            def sample_raw_tree():
                # An independent raw hdc observer is active BEFORE the click.
                # Record dump completion before file transfer; conservative proof
                # requires this upper bound to precede a real request receipt.
                started.set()
                while not stopped.is_set():
                    stamp = time.monotonic_ns()
                    remote = f"/data/local/tmp/vg14-fast-{stamp}.json"
                    target = self.evidence / f"fast-{attempt}-{stamp}.json"
                    try:
                        self.hdc("shell", "uitest", "dumpLayout", "-p", remote)
                        snapshot_end = time.monotonic_ns()
                        self.hdc("file", "recv", remote, str(target))
                        tree = json.loads(target.read_text(encoding="utf-8-sig"))
                        found = []

                        def visit(node):
                            attr = node.get("attributes", {})
                            if attr.get("id") == IDS["loading"]:
                                found.append(attr)
                            for child in node.get("children", []):
                                visit(child)

                        visit(tree)
                        visible = False
                        for node in found:
                            positions = [int(n) for n in re.findall(r"-?\d+", node.get("bounds", ""))]
                            visible = (node.get("type") == "LoadingProgress" and
                                       str(node.get("visible", "true")).lower() != "false" and
                                       float(node.get("opacity", "1") or "1") > 0 and
                                       len(positions) == 4 and positions[2] > positions[0] and
                                       positions[3] > positions[1] and
                                       min(positions[2], display_width) > max(positions[0], 0) and
                                       min(positions[3], display_height) > max(positions[1], 0))
                            if visible:
                                break
                        sample = self.event("fast_raw_sample", attempt=attempt, snapshot_start_ns=stamp,
                                            snapshot_end_ns=snapshot_end, loading=visible, nodes=found, file=target.name)
                        samples.append(sample)
                    except BaseException as error:
                        errors.append(repr(error))
                        self.event("fast_raw_sample_error", attempt=attempt, error=repr(error))
                        break

            worker = threading.Thread(target=sample_raw_tree, daemon=True)
            worker.start()
            self.assertTrue(started.wait(3), "Raw observer did not start")
            click = self.event("manual_click", after_request=after, label="fast", attempt=attempt)
            try:
                self.driver.click(coordinate)
                self.fixture.wait_request(after)
                self.wait_idle()
            finally:
                stopped.set()
                worker.join(timeout=40)
            self.assertFalse(worker.is_alive(), "Raw observer did not stop")
            self.assertFalse(errors, f"Raw observer failed: {errors}")
            requests = self.fixture.requests(after)
            self.assertTrue(requests, "No backend request in fast path")
            for sample in samples:
                if sample["loading"] and sample["snapshot_start_ns"] >= click["monotonic_ns"]:
                    for request in requests:
                        if sample["snapshot_end_ns"] <= request["monotonic_ns"]:
                            proved.append({"attempt": attempt, "sample": sample, "request": request})
            self.event("fast_order_result", attempt=attempt, proved=bool(proved),
                       request_count=len(requests), samples=len(samples))
            if proved:
                break
        self.assertTrue(proved, "Fast-path request-before-loading order not proved by raw samples; add frame/video evidence")

    def test_11_real_http_timeout_and_retry(self):
        self.configure("timeout")
        source = (ROOT / "entry/src/main/ets/sync/webdav/WebDavClient.ets").read_text(encoding="utf-8")
        match = re.search(r"readTimeout:\s*(\d+)", source)
        self.assertIsNotNone(match, "Read existing network timeout for test setup; do not invent a Spec threshold")
        read_seconds = int(match.group(1)) / 1000
        _, request = self.begin("timeout-initial", hold_seconds=read_seconds + 15)
        # Only this already accepted request stays unanswered. Any fallback receives
        # a prompt controlled error, allowing the whole real operation to settle.
        self.fixture.configure(gated=False, status=500)
        time.sleep(min(4, read_seconds / 4))
        self.assert_busy("timeout-still-waiting")
        self.wait_idle(timeout=read_seconds + 35)
        records = [r for r in self.fixture.records if r.get("id") == request["id"]]
        closed = [r for r in records if r["event"] == "client_closed"]
        responses = [r for r in records if r["event"] == "response"]
        self.assertTrue(closed, "No peer-close evidence for actual client timeout; inspect network/hilog before classifying")
        self.assertFalse(responses, "Server replied before timeout; this does not prove a network-timeout path")
        elapsed = (closed[0]["monotonic_ns"] - request["monotonic_ns"]) / 1_000_000_000
        self.event("real_timeout_evidence", request_id=request["id"], elapsed_seconds=elapsed,
                   configured_read_seconds=read_seconds, client_closed_without_response=True)
        self.assertGreaterEqual(elapsed, read_seconds * 0.9,
                                "Peer closed too early to attribute to the existing read timeout")
        self.begin("timeout-retry")
        self.complete()
