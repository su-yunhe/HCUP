"""vg-spec7 UI authorization boundary, using real UI and observed WebDAV I/O.

Run from logs/ through common's harness.runner, after installing the HAP built
from the frozen production sources. No app-private method is called directly.
"""
from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
import time
import unittest

from hypium import BY
from harness.driver import HarnessTestCase

from .do_support import BUNDLE, Evidence, source_fingerprint, wait_until, walk
from .webdav_fixture import WebDavFixture


class RestoreConfirmationTests(HarnessTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver.set_implicit_wait_time(0.2)
        cls.evidence = Evidence(cls.device_sn or "127.0.0.1:5555")
        versions = {}
        for name in ("test_restore_confirmation.py", "do_support.py", "webdav_fixture.py", "business_snapshot.py"):
            path = Path(__file__).parent / name
            target = cls.evidence.root / "test-sources" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(path.read_bytes())
            versions[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        cls.evidence.write("test-sources/manifest.json", versions)
        cls.initial_sources = source_fingerprint()
        cls.evidence.write("source-before.json", cls.initial_sources)
        cls.fixture = WebDavFixture(cls.evidence.root)
        cls.addClassCleanup(cls._cleanup)
        port = f"tcp:{cls.fixture.port}"
        cls.evidence.hdc("rport", port, port)

    @classmethod
    def _cleanup(cls):
        cls.fixture.close()
        port = f"tcp:{cls.fixture.port}"
        removed = cls.evidence.hdc("fport", "rm", port, port)
        if "Remove forward ruler success" not in removed.stdout:
            raise AssertionError("hdc did not confirm removal of this run's owned reverse mapping")
        after = source_fingerprint()
        cls.evidence.write("source-after.json", after)
        if cls.initial_sources != after:
            cls.evidence.write("INVALID-source-changed.json", {
                "changed": sorted(key for key in cls.initial_sources.keys() | after.keys()
                                  if cls.initial_sources.get(key) != after.get(key)),
                "consequence": "Affected app evidence must be discarded and rerun",
            })
            raise AssertionError("Production sources changed while device tests were running")

    def setUp(self):
        self.label = self._testMethodName
        self.fixture.mark("test_start", test=self.label)
        self.fixture.set_mode("empty")
        self._launch()
        self._configure()

    def tearDown(self):
        self.evidence.snapshot(self.label + "-end")
        self.fixture.mark("test_end", test=self.label)

    def _click(self, component, label):
        self.fixture.mark(label + "_dispatch", test=self.label)
        self.driver.click(component)
        return self.fixture.mark(label + "_returned", test=self.label)

    def _launch(self):
        self.evidence.hdc("shell", f"aa force-stop {BUNDLE}")
        self.evidence.hdc("shell", f"aa start -a EntryAbility -b {BUNDLE}")
        gear = self.require_component(BY.text("⚙"), "Existing home settings entry unavailable")
        self._click(gear, "open_settings")
        self._click(self.require_component(BY.text("WebDAV 配置"), "WebDAV menu unavailable"), "open_webdav")

    def _scroll_to(self, key: str, direction="UP"):
        for _ in range(8):
            component = self.driver.find_component(BY.key(key))
            if component is not None:
                bounds = component.getBounds()
                if bounds.bottom > 180 and bounds.top < 2690 and bounds.bottom > bounds.top:
                    return component
            self.driver.swipe(direction, distance=35, start_point=(0.75, 0.75))
            time.sleep(0.2)
        self.fail(f"Cannot reach stable WebDAV control {key!r}")

    def _configure(self, values: dict | None = None):
        toggle = self._scroll_to("webdavAutoSyncToggle")
        checked = toggle.isChecked()
        if checked is True or str(checked).lower() == "true":
            self._click(toggle, "disable_auto_sync")
        self.assertNotIn(str(toggle.isChecked()).lower(), {"true", "1"}, "Auto sync not disabled")
        for _ in range(3):
            self.driver.swipe("DOWN", distance=65)
        data = {
            "webdavEndpointInput": self.fixture.endpoint,
            "webdavUsernameInput": self.fixture.username,
            "webdavPasswordInput": self.fixture.password,
            "webdavSyncPasswordInput": self.fixture.sync_password,
        }
        data.update(values or {})
        for key, value in data.items():
            component = self._scroll_to(key)
            if value:
                self.driver.input_text(component, value)
            else:
                self.driver.click(component)
                self.driver.clear_text(component)
            self.evidence.hdc("shell", "uitest uiInput keyEvent Back")
        root = self._scroll_to("webdavRemoteRootInput")
        self.driver.input_text(root, self.fixture.remote_root)
        self.evidence.hdc("shell", "uitest uiInput keyEvent Back")
        self._click(self._scroll_to("webdavSaveSettingsButton"), "save_fixture_settings")
        self._scroll_to("webdavRestoreButton")
        self._drain()

    def _drain(self):
        self.assertTrue(wait_until(lambda: self.fixture.active_requests == 0, timeout=25), "Old HTTP task did not drain")
        seq = self.fixture.mark("drain_check", test=self.label)
        time.sleep(1.5)
        self.assertEqual(self.fixture.observed_since(seq), [], "Preparation did not reach a quiet window")

    def _quiet(self, since, seconds=2.5):
        time.sleep(seconds)
        observed = self.fixture.observed_since(since)
        self.assertEqual(observed, [], f"Unapproved WebDAV TCP/HTTP activity: {json.dumps(observed)}")

    def _open(self, suffix="open"):
        button = self._scroll_to("webdavRestoreButton")
        self.assertEqual(button.getText(), "从云端恢复")
        seq = self.fixture.mark("restore_entry_dispatch", test=self.label, round=suffix)
        self.driver.click(button)
        self.fixture.mark("restore_entry_returned", test=self.label, round=suffix)
        self._require_dialog()
        tree = self.evidence.snapshot(self.label + "-" + suffix)
        self._assert_dialog_context(tree)
        self._quiet(seq)
        return seq

    def _require_dialog(self):
        component = self.require_component(BY.text("继续"), "First local confirmation lacks exact Continue action", timeout=5)
        self.assertEqual(component.getText(), "继续")
        matches = self.driver.find_all_components(BY.text("继续")) or []
        self.assertEqual(len(matches), 1, "Continue action is ambiguous")
        return component

    def _assert_dialog_context(self, tree):
        # Scope actions to the current local confirmation. Native platforms may
        # omit a Dialog type, so preserve and inspect its unique title/window.
        nodes = list(walk(tree))
        continues = [node for node in nodes if node.get("text") == "继续"]
        self.assertEqual(len(continues), 1)
        titles = [node for node in nodes if node.get("text") in {"恢复确认", "⚠️ 恢复确认"}]
        self.assertTrue(titles, "Cannot identify the current confirmation title/window")
        windows = {node.get("hostWindowId") for node in continues}
        self.assertTrue(any(node.get("hostWindowId") in windows for node in titles),
                        "Continue is not in the current confirmation window")
        self.assertTrue(any(node.get("text") == "取消" and node.get("hostWindowId") in windows
                            for node in nodes), "Cancel and Continue are not in the same confirmation")

    def _cancel(self):
        component = self.require_component(BY.text("取消"), "Current confirmation cancel unavailable")
        self.assertEqual(component.getText(), "取消")
        self._click(component, "cancel_confirmation")
        self.assertTrue(wait_until(lambda: self.driver.find_component(BY.text("继续")) is None, timeout=5))

    def _continue(self):
        component = self._require_dialog()
        seq = self.fixture.mark("continue_dispatch", test=self.label)
        self.driver.click(component)
        self.fixture.mark("continue_returned", test=self.label)
        return seq

    def _assert_discovery(self, since):
        def discovered():
            return [item for item in self.fixture.ledger.since(since)
                    if item["event"] == "http_request" and "backup.json.enc" in item["path"]
                    and item["method"] in {"HEAD", "GET", "PROPFIND"}]
        requests = wait_until(discovered, timeout=25)
        self.assertTrue(requests, "No real backup discovery/acquisition request after Continue")
        for request in requests:
            self.assertTrue(request["authorization_matches"], "Saved test credentials were not used")
            self.assertTrue(request["path"].startswith(self.fixture.base_path + "/"))
            self.assertEqual(request["host"], f"127.0.0.1:{self.fixture.port}")
        self.evidence.write(self.label + "-discovery.json", requests)

    def _ready(self):
        def idle():
            component = self.driver.find_component(BY.key("webdavRestoreButton"))
            return component and component.isEnabled() and component.getText() == "从云端恢复"
        self.assertTrue(wait_until(idle, timeout=30), "Restore did not return to an operable state")
        self._drain()

    def test_01_first_open_wait_cancel_repeat(self):
        for index in range(2):
            seq = self._open(f"round-{index}")
            self._cancel()
            self._quiet(seq)
            self._ready()

    def test_02_continue_real_discovery_empty(self):
        self._open()
        seq = self._continue()
        self._assert_discovery(seq)
        self._ready()
        self.__class__.single_discovery_sequence = self._flow_sequence(seq)
        self.evidence.write("single-discovery-sequence.json", self.single_discovery_sequence)

    def test_03_system_back_and_outside_click(self):
        for action in ("back", "outside"):
            seq = self._open(action)
            if action == "back":
                self.evidence.hdc("shell", "uitest uiInput keyEvent Back")
            else:
                self._click((24, 250), "outside_dialog")
            time.sleep(0.5)
            remained = self.driver.find_component(BY.text("继续")) is not None
            self.fixture.mark("dismiss_capability", action=action, dialog_remained=remained)
            self._quiet(seq)
            if remained:
                self._cancel()
            self._ready()

    def test_04_cancel_return_and_reenter(self):
        for route in ("header", "system"):
            seq = self._open("before-return-" + route)
            self._cancel()
            if route == "header":
                self._click(self.require_component(BY.text("←"), "Existing header back unavailable"), "header_back")
            else:
                self.evidence.hdc("shell", "uitest uiInput keyEvent Back")
                gear = self.require_component(BY.text("⚙"), "System Back did not reach recorded home state")
                self._click(gear, "settings_after_system_back")
            self._click(self.require_component(BY.text("WebDAV 配置"), "Recorded settings menu unavailable"), "reenter_webdav")
            self._quiet(seq)
            seq = self._open("reentered-" + route)
            self._cancel()
            self._quiet(seq)

    def test_05_restart_without_authorization(self):
        for cancelled in (False, True):
            seq = self._open(f"before-restart-{cancelled}")
            if cancelled:
                self._cancel()
            self._launch()
            self._scroll_to("webdavRestoreButton")
            self._quiet(seq)
            seq = self._open(f"after-restart-{cancelled}")
            self._cancel()
            self._quiet(seq)

    def test_06_rapid_entry_and_continue_clicks(self):
        button = self._scroll_to("webdavRestoreButton")
        b = button.getBounds()
        point = ((b.left + b.right) // 2, (b.top + b.bottom) // 2)
        self.evidence.snapshot(self.label + "-before-rapid-entry")
        seq = self.fixture.mark("rapid_entry_dispatch", test=self.label, x=point[0], y=point[1])
        for index in range(3):
            self.fixture.mark("rapid_coordinate_input", test=self.label, index=index, x=point[0], y=point[1],
                              semantics="original entry location; later modal hit is not assumed")
            self.driver.click(point)
        tree = self.evidence.snapshot(self.label + "-after-rapid-entry")
        actions = self.driver.find_all_components(BY.text("继续")) or []
        self.assertLessEqual(len(actions), 1, "Entry coordinate sequence left stacked confirmations")
        self.fixture.mark("rapid_entry_final_state", test=self.label, dialog_count=len(actions))
        if actions:
            self._require_dialog()
            self._assert_dialog_context(tree)
        else:
            self.assertTrue(self._scroll_to("webdavRestoreButton").isEnabled(),
                            "Closed confirmation did not release pending state")
        self._quiet(seq)
        if actions:
            self._cancel()
        self._quiet(seq)
        self._ready()
        self._open("continue-repeat")
        component = self._require_dialog()
        b = component.getBounds()
        point = ((b.left + b.right) // 2, (b.top + b.bottom) // 2)
        self.fixture.set_mode("empty", delay_seconds=0.6)
        seq = self.fixture.mark("rapid_continue_dispatch", test=self.label, x=point[0], y=point[1],
                                initial_action="verified exact Continue in the new current confirmation")
        self.driver.click(point)
        self.fixture.mark("former_continue_coordinate_input", test=self.label, x=point[0], y=point[1],
                          semantics="repeat coordinate after first accepted action; no claim button is still present")
        self.driver.click(point)
        self._assert_discovery(seq)
        self._ready()
        self.assertIsNone(self.driver.find_component(BY.text("继续")), "A stale extra confirmation survived the completed flow")
        actual = self._flow_sequence(seq)
        reference = getattr(self.__class__, "single_discovery_sequence", None)
        if reference is None:
            reference_path = Path(os.environ["VG7_SINGLE_FLOW_REFERENCE"])
            reference = json.loads(reference_path.read_text(encoding="utf-8"))
        self.evidence.write("rapid-vs-single-discovery.json", {"single": reference, "rapid": actual,
                            "comparison": "same ordered discovery chain, combined with frozen synchronous busy/pending guard"})
        self.assertEqual(actual, reference, "Rapid Continue started a different or repeated discovery chain")

    def _flow_sequence(self, since):
        return [[item["method"], item["path"]] for item in self.fixture.ledger.since(since)
                if item["event"] == "http_request"]

    def test_07_empty_and_space_inputs_preserve_gate(self):
        keys = ("webdavEndpointInput", "webdavUsernameInput", "webdavPasswordInput", "webdavSyncPasswordInput")
        variants = [{key: value} for value in ("", "   ") for key in keys]
        variants += [{key: value for key in keys} for value in ("", "   ")]
        for index, values in enumerate(variants):
            with self.subTest(variant=index):
                self._launch()
                self._configure(values)
                seq = self._open(f"invalid-{index}")
                self._cancel()
                self._quiet(seq, seconds=0.5)
                self._ready()

    def test_08_encrypted_download_preview_cancel_preserves_data(self):
        from .business_snapshot import logical_snapshot
        self.fixture.set_mode("stored")
        preparation = self.fixture.mark("prepare_compatible_encrypted_backup", test=self.label)
        self._click(self._scroll_to("webdavBackupButton"), "prepare_backup_via_existing_ui")
        self.assertTrue(wait_until(lambda: any(item["event"] == "backup_uploaded"
                                              for item in self.fixture.ledger.since(preparation)), timeout=45),
                        "App did not upload a compatible encrypted backup")
        self._ready()
        database_dir = os.environ.get("VG7_DATABASE_DIR")
        before = logical_snapshot(self.evidence, "D0-before-first-confirm", database_dir) if database_dir else None
        if before is None:
            self.fixture.mark("business_snapshot_blocked", reason="No accessible bundle-scoped database directory supplied")
        seq = self._open("stored-backup-cancel")
        self._cancel()
        self._quiet(seq)
        if before is not None:
            unapproved = logical_snapshot(self.evidence, "D0-after-first-cancel", database_dir)
            self.assertEqual(before, unapproved, "Business database changed without Continue")
        self._open("stored-backup-continue")
        seq = self._continue()
        self._assert_discovery(seq)
        preview = self.require_component(BY.text("确认恢复"), "Downloaded backup did not reach original preview", timeout=35)
        self.assertEqual(preview.getText(), "确认恢复")
        tree = self.evidence.snapshot(self.label + "-downloaded-preview")
        self.assertTrue(any("将覆盖更新" in node.get("text", "") and "词" in node.get("text", "")
                            for node in walk(tree)), "Original preview statistics unavailable")
        gets = [item for item in self.fixture.ledger.since(seq) if item["event"] == "http_request"
                and item["method"] == "GET" and item["path"].endswith("/backup.json.enc")]
        self.assertTrue(gets, "Preview did not follow a real encrypted backup GET")
        responses = [item for item in self.fixture.ledger.since(seq) if item["event"] == "http_response"
                     and item["request_id"] in {request["seq"] for request in gets}]
        self.assertTrue(any(item["status"] == 200 and item["body_bytes"] > 0 for item in responses))
        self._click(self.require_component(BY.text("取消"), "Original preview cancel unavailable"), "cancel_downloaded_preview")
        self.assertTrue(wait_until(lambda: self.driver.find_component(BY.text("确认恢复")) is None, timeout=5))
        self._ready()
        if before is not None:
            after = logical_snapshot(self.evidence, "D0-after-preview-cancel", database_dir)
            self.assertEqual(before, after, "Downloaded preview cancellation changed business database")

    def test_09_controlled_http_failure_releases_busy(self):
        self.fixture.set_mode("server_error")
        self._open("controlled-500")
        seq = self._continue()
        self.assertTrue(wait_until(lambda: any(item["event"] == "http_response" and item["status"] == 500
                                              for item in self.fixture.ledger.since(seq)), timeout=25),
                        "No controlled server-side failure was actually observed after Continue")
        self._ready()
        seq = self._open("reopen-after-error")
        self._cancel()
        self._quiet(seq)


def load_tests(loader, tests, pattern):
    selected = os.environ.get("VG7_CASES", "")
    if not selected:
        return tests
    names = selected.split(",")
    available = loader.getTestCaseNames(RestoreConfirmationTests)
    if any(name not in available for name in names):
        raise ValueError("Unknown explicitly selected verification case: " + selected)
    return unittest.TestSuite(RestoreConfirmationTests(name) for name in names)

