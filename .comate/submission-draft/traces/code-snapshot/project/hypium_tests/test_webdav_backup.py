"""Hypium + real server assertions for vg-spec13; no business-code injection.

Run only after exclusive-device and source-freeze authorization. The runner must
have installed the just-built HAP and set VG13_EVIDENCE_DIR and VG13_RUN_TAG.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

from hypium import BY
from hypium.model.basic_data_type import InputTextMode
from harness.driver import HarnessTestCase
from hypium_tests.webdav_fixture import WebDavFixture, utc

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = "io.qzz.weiyu"
FIELDS = {
    "endpoint": "webdav_endpoint_input", "username": "webdav_username_input",
    "password": "webdav_password_input", "sync_password": "webdav_sync_password_input",
    "remote_root": "webdav_remote_root_input",
}


def fingerprint() -> dict[str, str]:
    paths = []
    for folder in ("entry/src", "AppScope"):
        paths.extend(p for p in (ROOT / folder).rglob("*") if p.is_file())
    paths.extend(p for p in ROOT.glob("*.json5") if p.is_file())
    paths.extend(p for p in (ROOT / "hvigor").rglob("*") if p.is_file())
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(paths) if p.name != "BuildProfile.ets"}


class WebDavBackupTest(HarnessTestCase):
    @classmethod
    def setUpClass(cls):
        if not os.environ.get("VG13_EVIDENCE_DIR"):
            raise RuntimeError("VG13_EVIDENCE_DIR required; no authorized run configured")
        super().setUpClass()
        cls.driver.set_implicit_wait_time(0.3)
        cls.output = Path(os.environ["VG13_EVIDENCE_DIR"]).resolve()
        cls.output.mkdir(parents=True, exist_ok=True)
        cls.tag = os.environ.get("VG13_RUN_TAG", "vg13")
        cls.hdc = shutil.which("hdc")
        cls.form_values = {}
        cls.initial_fingerprint = fingerprint()
        (cls.output / "source-before.json").write_text(json.dumps(cls.initial_fingerprint, indent=2), encoding="utf-8")
        cls.fixture_a = WebDavFixture(cls.output / "fixture-a.jsonl", 18173)
        cls.fixture_b = WebDavFixture(cls.output / "fixture-b.jsonl", 18174)

    @classmethod
    def tearDownClass(cls):
        cls.fixture_a.close()
        cls.fixture_b.close()
        after = fingerprint()
        (cls.output / "source-after.json").write_text(json.dumps(after, indent=2), encoding="utf-8")
        changed = after != cls.initial_fingerprint
        (cls.output / "source-comparison.json").write_text(json.dumps({"unchanged": not changed}), encoding="utf-8")
        if changed:
            raise AssertionError("Source fingerprint changed; affected evidence INVALID")

    def setUp(self):
        self.case = self._testMethodName
        self.step = 0
        self.events = self.output / "observations.jsonl"
        self.record(event="case_started", case=self.case)
        self.navigate()

    def tearDown(self):
        # Always release fixture-owned requests, even if an assertion fails.
        for fixture in (self.fixture_a, self.fixture_b):
            for gate in fixture.gates.values():
                gate.set()
            for gate in fixture.head_gates.values():
                gate.set()
        self.record(event="case_finished", case=self.case)
        self.assertEqual(self.initial_fingerprint, fingerprint(), "Source changed during this case; evidence invalid")

    def record(self, **data):
        data.update(utc=utc(), monotonic_ns=time.monotonic_ns(), case=self.case)
        with self.events.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(data, ensure_ascii=False) + "\n")

    def command(self, *args):
        begin = utc()
        result = subprocess.run([self.hdc, "-t", self.device_sn, *args], capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=30)
        self.record(event="hdc", command=list(args), began=begin, ended=utc(),
                    exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
        self.assertEqual(result.returncode, 0, f"hdc {args}: {result.stdout} {result.stderr}")
        return result.stdout

    def swipe(self, up=True):
        self.driver.swipe("UP" if up else "DOWN", distance=48,
                          start_point=(0.5, 0.78) if up else (0.5, 0.28), swipe_time=0.3)
        self.record(event="hypium_swipe", direction="UP" if up else "DOWN")

    def key(self, name, *, up=True, attempts=7):
        for _ in range(attempts):
            component = self.find_or_none(BY.key(name), timeout=0.5)
            if component is not None:
                bounds = component.getBounds()
                minimum_y = 150 if name == "settings_back_button" else 320
                if bounds.bottom > bounds.top and minimum_y < (bounds.top + bounds.bottom) / 2 < 2700:
                    return component
            self.swipe(up)
        return self.require_component(BY.key(name), f"Unreachable stable id {name}", timeout=1)

    def navigate(self):
        # No package reset, shell data mutation or direct route injection.
        if self.find_or_none(BY.key("webdav_settings_section"), timeout=0.5) is not None:
            return
        self.command("shell", "aa", "start", "-a", "EntryAbility", "-b", BUNDLE)
        if self.find_or_none(BY.key("webdav_settings_entry"), timeout=0.5) is None:
            cog = self.require_text("⚙", "Home settings entry absent", timeout=12)
            self.driver.click(cog)
        self.driver.click(self.key("webdav_settings_entry"))
        self.__class__.form_values = {}
        self.require_component(BY.key("webdav_settings_section"), "WebDAV page absent")
        # This is the first toggle in the baseline WebDAV form: automatic sync.
        toggles = self.driver.find_all_components(BY.type("Toggle")) or []
        for toggle in toggles[:1]:
            if toggle.isChecked():
                self.driver.click(toggle)
        self.record(event="entered_webdav")

    def configure(self, remote, *, port=18173, save=False, overrides=None):
        values = {"endpoint": f"http://127.0.0.1:{port}", "username": "vg13-fixture",
                  "password": "fixture-pass", "sync_password": "fixture-sync-pass", "remote_root": remote}
        values.update(overrides or {})
        for name, value in values.items():
            if self.__class__.form_values.get(name) == value:
                continue
            component = self.key(FIELDS[name], up=False)
            self.driver.input_text(component, value, mode=InputTextMode().paste(True))
            self.driver.press_back()
            self.__class__.form_values[name] = value
        self.record(event="configured", endpoint=values["endpoint"], remote_root=values["remote_root"],
                    empty_fields=[k for k, v in values.items() if not v.strip()], saved=save)
        if save:
            self.driver.click(self.key("webdav_save_button"))
            self.require_text("✅ WebDAV 设置已保存", "Save did not succeed")
        self.key("webdav_backup_button")

    def snapshot(self, label):
        self.step += 1
        name = f"{self.case}-{self.step:02d}-{label}"
        began = utc()
        # RPC component properties are direct UI-tree observations. Avoid
        # starting a second native uitest CLI while Hypium owns its UI agent.
        identities = ("webdav_backup_button", "webdav_backup_loading", "webdav_backup_status")
        nodes = []
        for identity in identities:
            component = self.driver.find_component(BY.key(identity))
            if component is not None:
                raw = component.getAllProperties().to_dict()
                raw["queried_stable_id"] = identity
                raw["id"] = component.getId()
                raw["type"] = component.getType()
                raw["text"] = component.getText()
                raw["enabled"] = str(component.isEnabled()).lower()
                bounds = component.getBounds()
                raw["bounds"] = f"[{bounds.left},{bounds.top}][{bounds.right},{bounds.bottom}]"
                nodes.append(raw)
        (self.output / f"{name}.json").write_text(json.dumps({"source":"Hypium UI component RPC getAllProperties", "nodes":nodes}, ensure_ascii=False, indent=2), encoding="utf-8")
        self.driver.capture_screen(str(self.output / f"{name}.jpeg"))
        ended = utc()
        self.record(event="snapshot", name=name, began=began, ended=ended,
                    targets=[n for n in nodes if n.get("id", "").startswith("webdav_")])
        return nodes, began, ended

    def attr(self, nodes, identity):
        found = [n for n in nodes if n.get("id") == identity]
        self.assertEqual(len(found), 1, f"Expected exactly one {identity}: {found}")
        return found[0]

    def visible(self, node):
        if "visible" in node:
            self.assertIn(node["visible"], (True, "true"), f"Not visible: {node}")
        self.assertGreater(float(node.get("opacity", "1")), 0)
        numbers = [int(v) for v in re.findall(r"-?\d+", node["bounds"])]
        self.assertEqual(len(numbers), 4)
        left, top, right, bottom = numbers
        self.assertGreater(right, left)
        self.assertGreater(bottom, top)
        self.assertLess(top, 2880)
        self.assertGreater(bottom, 0)

    def pending_sample(self, fixture, prefix, label):
        self.require_component(BY.key("webdav_backup_loading"), "A05 missing LoadingProgress")
        pending_before = fixture.pending(prefix)
        nodes, began, ended = self.snapshot(label)
        pending_after = fixture.pending(prefix)
        spinner = self.attr(nodes, "webdav_backup_loading")
        status = self.attr(nodes, "webdav_backup_status")
        self.assertEqual(spinner["type"], "LoadingProgress", "A05 component type")
        self.visible(spinner)
        self.visible(status)
        self.assertTrue(any(word in status.get("text", "") for word in ("正在", "处理中")), "A09 busy wording")
        self.assertEqual(self.attr(nodes, "webdav_backup_button")["enabled"], "false")
        self.assertTrue(pending_before and pending_after, "A16: UI capture not inside pending request")
        self.record(event="pending_ui_assertions_passed", prefix=prefix, began=began, ended=ended,
                    pending_before=pending_before, pending_after=pending_after)

    def wait_upload(self, fixture, prefix, timeout=15):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            requests = [r for r in fixture.matching(prefix) if r.get("upload")]
            if requests:
                return requests
            time.sleep(0.1)
        self.fail(f"A13/A15: No real backup upload reached configured endpoint: {prefix}")

    def start(self):
        button = self.key("webdav_backup_button")
        self.assertEqual(button.getText(), "立即备份")
        self.record(event="backup_click")
        self.driver.click(button)

    def settled(self, success=None, timeout=55, other_operation_rejection=False):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            button = self.find_or_none(BY.key("webdav_backup_button"), timeout=0.4)
            if button and button.getText() == "立即备份":
                break
            time.sleep(0.3)
        else:
            self.snapshot("busy-did-not-settle")
            self.fail("D01/D02/D03 busy did not settle")
        nodes, _, _ = self.snapshot("settled")
        self.assertFalse(any(n.get("id") == "webdav_backup_loading" and n.get("visible", "true") not in (False, "false") for n in nodes))
        status = self.attr(nodes, "webdav_backup_status").get("text", "")
        terminal_rejection = (other_operation_rejection and status.startswith("⚠") and
                              "同步操作正在进行中" in status and "请等待" in status and
                              "正在备份" not in status and "处理中" not in status)
        self.assertFalse(any(word in status for word in ("正在", "处理中")) and not terminal_rejection, status)
        if other_operation_rejection:
            self.assertTrue(terminal_rejection, f"Expected terminal rejection of other in-flight operation: {status}")
        self.assertEqual(self.attr(nodes, "webdav_backup_button")["enabled"], "true")
        if success is True:
            self.assertIn("✅", status)
        elif success is False:
            self.assertTrue("⚠" in status or "失败" in status or "异常" in status, status)
        return status

    def prefix(self, suffix):
        return f"/{self.tag}/{self.case.split('_')[1]}/{suffix}"

    def test_01_first_entry_and_cancel_without_backup(self):
        prefix = self.prefix("cancel-input")
        self.configure(prefix)
        before = len(self.fixture_a.events)
        self.snapshot("configured-no-backup")
        self.driver.click(self.key("settings_back_button", up=False))
        self.driver.click(self.key("webdav_settings_entry"))
        self.__class__.form_values = {}
        self.key("webdav_backup_button")
        self.snapshot("reentered-no-backup")
        self.assertEqual([], self.fixture_a.matching(prefix))
        self.record(event="cancel_input_no_requests", baseline_sequence=before)

    def test_00_unsaved_slow_backup_and_repeated_click(self):
        prefix = self.prefix("unsaved")
        gate = self.fixture_a.gate(prefix)
        self.configure(prefix)
        self.snapshot("before-click")
        self.start()
        uploads = self.wait_upload(self.fixture_a, prefix)
        self.assertTrue(uploads[0]["auth_valid"])
        self.pending_sample(self.fixture_a, prefix, "busy-1")
        # A real pointer action on the disabled button, rather than calling a handler.
        button = self.key("webdav_backup_button")
        bounds = button.getBounds()
        point = ((bounds.left + bounds.right) // 2, (bounds.top + bounds.bottom) // 2)
        self.driver.click(point)
        self.driver.click(point)
        self.pending_sample(self.fixture_a, prefix, "busy-2-after-repeat")
        self.assertEqual(len([r for r in self.fixture_a.matching(prefix) if r.get("upload")]), 1)
        gate.set()
        self.settled(True)

    def test_02_current_endpoint_snapshot_and_restart_saved_config(self):
        saved = self.prefix("saved-a")
        self.configure(saved, save=True)
        prefix = self.prefix("unsaved-b")
        gate = self.fixture_b.gate(prefix)
        self.configure(prefix, port=18174)
        self.start()
        self.wait_upload(self.fixture_b, prefix)
        self.pending_sample(self.fixture_b, prefix, "current-endpoint-b")
        self.assertEqual([], self.fixture_a.matching(prefix))
        gate.set()
        self.settled(True)
        # Explicitly persist C, then make a draft D without any action. Whether
        # the preceding backup persisted B is deliberately not an assertion.
        saved = self.prefix("explicitly-saved-c")
        self.configure(saved, save=True)
        self.configure(self.prefix("unsubmitted-draft-d"), port=18174)
        self.command("shell", "aa", "force-stop", BUNDLE)
        self.command("shell", "aa", "start", "-a", "EntryAbility", "-b", BUNDLE)
        self.navigate()
        for _ in range(3):
            self.swipe(False)
        endpoint = self.key(FIELDS["endpoint"]).getText()
        remote = self.key(FIELDS["remote_root"]).getText()
        self.assertEqual(endpoint, "http://127.0.0.1:18173")
        self.assertEqual(remote, saved)
        self.snapshot("restart-restored-explicit-c")

    def test_03_return_during_pending_then_second_backup(self):
        prefix = self.prefix("return")
        gate = self.fixture_a.gate(prefix)
        self.configure(prefix, save=True)
        self.start()
        self.wait_upload(self.fixture_a, prefix)
        self.driver.click(self.key("settings_back_button", up=False))
        self.driver.click(self.key("webdav_settings_entry"))
        self.key("webdav_backup_loading")
        self.pending_sample(self.fixture_a, prefix, "reentered-still-pending")
        gate.set()
        self.settled(True)
        count = len([r for r in self.fixture_a.matching(prefix) if r.get("upload")])
        self.start()
        self.settled(True)
        self.assertEqual(len([r for r in self.fixture_a.matching(prefix) if r.get("upload")]), count + 1)

    def test_04_empty_and_space_fields_no_requests(self):
        for field in ("endpoint", "username", "password", "sync_password"):
            for value in ("", "    "):
                with self.subTest(field=field, value=repr(value)):
                    prefix = self.prefix(f"invalid-{field}-{len(value)}")
                    self.configure(prefix, overrides={field: value})
                    self.start()
                    self.settled(False)
                    self.assertEqual([], self.fixture_a.matching(prefix), f"Invalid {field} sent request")
        for short in ("a", "abc"):
            prefix = self.prefix(f"short-sync-{len(short)}")
            self.configure(prefix, overrides={"sync_password": short})
            self.start()
            self.settled(False)
            self.assertEqual([], self.fixture_a.matching(prefix))
        prefix = self.prefix("four-char-sync")
        self.configure(prefix, overrides={"sync_password": "abcd"})
        self.start()
        self.wait_upload(self.fixture_a, prefix)
        self.settled(True)
        for partial in (False, True):
            prefix = self.prefix(f"all-empty-or-partial-{partial}")
            overrides = {name: "" for name in FIELDS if name != "remote_root"}
            if partial:
                overrides["endpoint"] = "http://127.0.0.1:18173"
            self.configure(prefix, overrides=overrides)
            self.start()
            self.settled(False)
            self.assertEqual([], self.fixture_a.matching(prefix))

    def test_05_restore_cancel_and_close_no_requests(self):
        prefix = self.prefix("restore-cancel")
        self.configure(prefix)
        self.driver.click(self.key("webdav_restore_button"))
        self.driver.click(self.require_text("取消", "Restore confirmation cancel absent"))
        self.snapshot("restore-cancelled")
        self.assertEqual([], self.fixture_a.matching(prefix))
        self.driver.click(self.key("webdav_restore_button"))
        self.require_text("取消", "Restore confirmation absent")
        self.command("shell", "uitest", "uiInput", "keyEvent", "Back")
        self.snapshot("restore-dialog-closed")
        self.assertEqual([], self.fixture_a.matching(prefix))

    def test_06_http_failure_codes_release_busy(self):
        for code in (401, 403, 404, 409, 500):
            with self.subTest(status=code):
                prefix = self.prefix(f"status-{code}")
                self.configure(prefix)
                self.start()
                self.wait_upload(self.fixture_a, prefix)
                self.settled(False)
                replies = self.fixture_a.matching(prefix, "responded")
                self.assertTrue(any(r.get("method") == "PUT" and r["status"] == code for r in replies), replies)

    def test_07_auth_rejection_then_recovery(self):
        prefix = self.prefix("bad-auth")
        self.configure(prefix, overrides={"password": "wrong-fixture-pass"})
        self.start()
        self.settled(False)
        self.assertTrue(any(r["status"] == 401 for r in self.fixture_a.matching(prefix, "responded")))
        prefix = self.prefix("auth-recovered")
        self.configure(prefix)
        self.start()
        self.wait_upload(self.fixture_a, prefix)
        self.settled(True)

    def test_08_network_read_timeout_then_late_response(self):
        prefix = self.prefix("read-timeout")
        gate = self.fixture_a.gate(prefix)
        self.configure(prefix)
        self.start()
        self.wait_upload(self.fixture_a, prefix)
        self.pending_sample(self.fixture_a, prefix, "timeout-pending")
        self.settled(False, timeout=65)
        self.record(event="ui_settled_before_fixture_release", pending=self.fixture_a.pending(prefix))
        gate.set()
        time.sleep(1)
        self.snapshot("late-response-after-network-timeout")
        prefix = self.prefix("after-timeout")
        self.configure(prefix)
        self.start()
        self.wait_upload(self.fixture_a, prefix)
        self.settled(True)

    def test_09_connection_refused_releases_busy(self):
        prefix = self.prefix("connection-refused")
        self.configure(prefix, port=18175)
        self.start()
        self.settled(False)
        self.assertEqual([], self.fixture_a.matching(prefix))
        self.assertEqual([], self.fixture_b.matching(prefix))

    def test_10_fast_success_and_default_remote_directory(self):
        self.configure("", overrides={"remote_root": "   "})
        before = len(self.fixture_a.matching("/weiyu_sync"))
        self.start()
        self.settled(True)
        self.assertGreater(len(self.fixture_a.matching("/weiyu_sync")), before)

    def test_11_empty_local_data_structural_backup(self):
        prefix = self.prefix("empty-local-data")
        self.configure(prefix)
        before = self.command("shell", "hilog", "-x")
        self.start()
        self.wait_upload(self.fixture_a, prefix)
        self.settled(True)
        after = self.command("shell", "hilog", "-x")
        previous = set(before.splitlines())
        fresh = "\n".join(line for line in after.splitlines() if line not in previous)
        (self.output / "empty-data-app-hilog.log").write_text(fresh, encoding="utf-8")
        self.require_precondition("Exporting 0 words in batches" in fresh,
                                  "Current local learned-word data not independently confirmed empty")
        self.require_precondition("Fetched 0 word books" in fresh,
                                  "Current local user-book data not independently confirmed empty")

    def test_12_system_return_background_and_inflight_restart(self):
        prefix = self.prefix("lifecycle")
        gate = self.fixture_a.gate(prefix)
        self.configure(prefix, save=True)
        self.start()
        self.wait_upload(self.fixture_a, prefix)
        self.command("shell", "uitest", "uiInput", "keyEvent", "Back")
        self.command("shell", "uitest", "uiInput", "keyEvent", "Back")
        self.navigate()
        self.key("webdav_backup_loading")
        self.pending_sample(self.fixture_a, prefix, "full-settings-reentry")
        self.command("shell", "uitest", "uiInput", "keyEvent", "Home")
        self.command("shell", "aa", "start", "-a", "EntryAbility", "-b", BUNDLE)
        self.navigate()
        self.key("webdav_backup_loading")
        self.pending_sample(self.fixture_a, prefix, "background-resume")
        self.command("shell", "aa", "force-stop", BUNDLE)
        gate.set()
        time.sleep(1)
        count = len([r for r in self.fixture_a.matching(prefix) if r.get("upload")])
        self.command("shell", "aa", "start", "-a", "EntryAbility", "-b", BUNDLE)
        self.navigate()
        self.key("webdav_backup_button")
        nodes, _, _ = self.snapshot("restarted-after-inflight-stop")
        self.assertEqual(self.attr(nodes, "webdav_backup_button")["enabled"], "true")
        self.assertFalse(any(n.get("id") == "webdav_backup_loading" for n in nodes))
        self.assertEqual(len([r for r in self.fixture_a.matching(prefix) if r.get("upload")]), count)
        self.start()
        self.settled(True)
        self.assertEqual(len([r for r in self.fixture_a.matching(prefix) if r.get("upload")]), count + 1)

    def test_13_preflight_snapshot_and_conflicting_controls(self):
        prefix = self.prefix("snapshot-preflight")
        gate = self.fixture_a.gate_head(prefix)
        self.configure(prefix)
        self.start()
        deadline = time.monotonic() + 10
        while not self.fixture_a.pending(prefix) and time.monotonic() < deadline:
            time.sleep(0.1)
        self.assertTrue(self.fixture_a.pending(prefix), "Preflight did not reach controlled HEAD gate")
        self.pending_sample(self.fixture_a, prefix, "preflight-pending")
        for identity in ("webdav_save_button", "webdav_test_button", "webdav_sync_button", "webdav_restore_button"):
            component = self.key(identity, up=False)
            self.assertFalse(component.isEnabled(), f"Conflicting action still enabled: {identity}")
        endpoint = self.key(FIELDS["endpoint"], up=False)
        if endpoint.isEnabled():
            self.driver.input_text(endpoint, "http://127.0.0.1:18174")
            self.command("shell", "uitest", "uiInput", "keyEvent", "Back")
            self.record(event="edited_endpoint_during_preflight")
        else:
            self.record(event="endpoint_locked_during_preflight")
        gate.set()
        self.wait_upload(self.fixture_a, prefix)
        self.key("webdav_backup_button")
        self.settled(True)
        self.assertEqual([], self.fixture_b.matching(prefix), "One operation crossed configured endpoints")

    def test_14_other_testing_task_survives_page_reentry(self):
        prefix = self.prefix("other-testing")
        gate = self.fixture_a.gate_head(prefix)
        self.configure(prefix)
        self.driver.click(self.key("webdav_test_button", up=False))
        deadline = time.monotonic() + 10
        while not self.fixture_a.pending(prefix) and time.monotonic() < deadline:
            time.sleep(0.1)
        self.assertTrue(self.fixture_a.pending(prefix), "Connection test HEAD not pending")
        self.driver.click(self.key("settings_back_button", up=False))
        self.driver.click(self.key("webdav_settings_entry"))
        endpoint = self.key(FIELDS["endpoint"], up=False)
        if endpoint.isEnabled():
            self.driver.input_text(endpoint, "http://127.0.0.1:18174")
            self.command("shell", "uitest", "uiInput", "keyEvent", "Back")
        backup = self.key("webdav_backup_button")
        if backup.isEnabled():
            self.start()
            self.settled(False, other_operation_rejection=True)
        else:
            bounds = backup.getBounds()
            self.driver.click(((bounds.left + bounds.right) // 2, (bounds.top + bounds.bottom) // 2))
            self.snapshot("backup-blocked-by-other-testing")
        self.assertTrue(self.fixture_a.pending(prefix), "Original TESTING task ended before conflict assertion")
        self.assertEqual([], self.fixture_b.matching(prefix), "Rejected backup changed active TESTING configuration")
        self.assertEqual([], [r for r in self.fixture_a.matching(prefix) if r.get("upload")])
        gate.set()
        time.sleep(0.5)
        recovered = self.prefix("after-testing")
        self.configure(recovered, port=18174)
        self.start()
        self.wait_upload(self.fixture_b, recovered)
        self.settled(True)

    def test_15_other_actions_then_backup_and_failed_reentry(self):
        for action in ("webdav_test_button", "webdav_sync_button"):
            prefix = self.prefix(action)
            self.configure(prefix)
            self.record(event="other_action_click", action=action)
            self.driver.click(self.key(action, up=False))
            self.key("webdav_backup_button")
            deadline = time.monotonic() + 55
            while time.monotonic() < deadline:
                button = self.driver.find_component(BY.key("webdav_backup_button"))
                if button is not None and button.getText() == "立即备份":
                    break
                time.sleep(.2)
            else:
                self.fail(f"Other WebDAV action did not end: {action}")
            config_result = self.driver.find_component(BY.key("webdav_config_result"))
            self.record(event="other_action_ended", action=action,
                        result=config_result.getText() if config_result else "")
            self.assertIsNone(self.driver.find_component(BY.key("webdav_backup_loading")),
                              "Other action incorrectly presented as manual backup")
            previous = len([r for r in self.fixture_a.matching(prefix) if r.get("upload")])
            self.start()
            self.settled(True)
            self.assertEqual(len([r for r in self.fixture_a.matching(prefix) if r.get("upload")]), previous + 1)
        prefix = self.prefix("status-500")
        self.configure(prefix)
        self.start()
        self.wait_upload(self.fixture_a, prefix)
        self.settled(False)
        self.driver.press_back()
        self.driver.press_back()
        self.navigate()
        recovered = self.prefix("after-failed-route-reentry")
        self.configure(recovered)
        self.start()
        self.wait_upload(self.fixture_a, recovered)
        self.settled(True)

    def test_16_fast_double_click_single_task(self):
        prefix = self.prefix("fast-double")
        gate = self.fixture_a.gate(prefix)
        self.configure(prefix)
        button = self.key("webdav_backup_button")
        self.assertEqual(button.getText(), "立即备份")
        bounds = button.getBounds()
        point = ((bounds.left + bounds.right) // 2, (bounds.top + bounds.bottom) // 2)
        self.record(event="rapid_double_click_begin")
        self.driver.double_click(point)
        self.driver.click(point)
        self.wait_upload(self.fixture_a, prefix)
        self.pending_sample(self.fixture_a, prefix, "rapid-double-pending")
        self.assertEqual(len([r for r in self.fixture_a.matching(prefix) if r.get("upload")]), 1)
        gate.set()
        self.settled(True)

