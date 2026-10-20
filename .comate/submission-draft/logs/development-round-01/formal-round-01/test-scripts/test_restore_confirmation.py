"""R01-R28 device assertions. Formal execution requires an installed-HAP manifest.

Run only after coordinator freeze and independent clean build/reinstallation.
Preparation experiments never satisfy this gate or produce acceptance labels.
"""
from __future__ import annotations

import json
import os
import time
import unittest
from pathlib import Path

from hypium import BY
from harness.driver import HarnessTestCase

from hypium_tests.evidence import (BUNDLE, PORT, ROOT, Evidence, WebDavProbe,
    digest, flatten, read_preferences, source_fingerprint, utc, write_json, PREFS)

FIELDS = ("endpoint", "username", "password", "sync_password", "remote_root")
ACTIONS = ("save", "test", "sync", "backup", "restore")
TITLE = "⚠️ 从云端恢复"


class RestoreConfirmationTests(HarnessTestCase):
    @classmethod
    def setUpClass(cls):
        manifest_path = os.environ.get("VG_VERIFICATION_MANIFEST")
        if not manifest_path:
            raise RuntimeError("No fresh build/install manifest. Run: pwsh -File hypium_tests/run_verification.ps1 -SourceFrozen")
        manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        if not manifest.get("coordinator_frozen") or not manifest.get("installed_at"):
            raise RuntimeError("Source freeze and fresh HAP install have not been confirmed")
        cls.original_source = source_fingerprint()
        if manifest["source"] != cls.original_source:
            raise RuntimeError("Production source changed since fresh build/install; evidence invalid")
        hap = ROOT / "entry/build/default/outputs/default/entry-default-unsigned.hap"
        if digest(hap.read_bytes()) != manifest["hap_sha256"]:
            raise RuntimeError("Built HAP fingerprint changed")
        cls.out = ROOT / manifest["evidence_dir"]
        cls.audit = Evidence(cls.out)
        cls.probe = WebDavProbe(cls.out / "webdav")
        cls.probe.start()
        cls.audit.hdc("rport", f"tcp:{PORT}", f"tcp:{PORT}")
        super().setUpClass()
        cls.driver.set_implicit_wait_time(.2)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "probe"):
            cls.probe.stop()
            cls.audit.hdc("fport", "rm", f"tcp:{PORT}", f"tcp:{PORT}", check=False)
            final = source_fingerprint()
            write_json(cls.out / "source-after-tests.json", final)
            if final != cls.original_source:
                raise RuntimeError("Source changed during verification; affected evidence is INVALID")

    def setUp(self):
        self.case = self._testMethodName
        self.e = Evidence(self.out / self.case)
        self.probe.mode = "success"
        self.driver.stop_app(BUNDLE)
        self.driver.start_app(BUNDLE, "EntryAbility")
        self.enter_webdav()
        toggle = self.scroll_find("webdav_auto_sync_toggle", "DOWN")
        self.assertFalse(toggle.isChecked(), "P0: actual auto-sync toggle must be OFF")
        self.e.receive(PREFS, self.e.folder / "precondition-preferences.xml")
        prefs = read_preferences(self.e.folder / "precondition-preferences.xml")
        self.assertEqual(prefs.get("webdav_autosync_enabled"), "0", "P0: persisted auto-sync must be OFF")
        self.configure((f"http://127.0.0.1:{PORT}", "vg_user", "vg_password", "vg_spec1_sync_1234", "/weiyu_vignette"))

    def tearDown(self):
        self.e.screen("final-ui")
        write_json(self.e.folder / "source-still-frozen.json", {"equal": source_fingerprint() == self.original_source})
        self.assertEqual(source_fingerprint(), self.original_source, "Source changed; invalidate this case")

    def get(self, key: str, timeout: float = 4):
        return self.require_component(BY.key(key), f"Missing required stable component {key}", timeout)

    def present(self, key: str):
        return self.driver.find_component(BY.key(key))

    def scroll_find(self, key: str, direction: str = "UP"):
        for _ in range(9):
            c = self.present(key)
            if c is not None:
                b = c.getBounds()
                _, h = self.driver.get_display_size()
                if b.top > h * .08 and b.bottom < h * .94:
                    return c
            self.driver.swipe(direction, distance=40)
        return self.get(key)

    def enter_webdav(self):
        self.driver.click(self.get("settings_entry_button"))
        self.driver.click(self.get("settings_section_sync"))

    def configure(self, values: tuple[str, ...]):
        for name, value in zip(FIELDS, values):
            component = self.scroll_find(f"webdav_{name}_input", "DOWN")
            self.driver.click(component)
            component.clearText()
            if value:
                component.inputText(value)
            # Close the actual IME, keeping the settings page.
            self.driver.press_back()
        self.driver.click(self.scroll_find("webdav_save_button"))
        time.sleep(.4)

    def ui_state(self, name: str):
        state = {"inputs": {}, "actions": {}, "results": {}}
        for field in FIELDS:
            c = self.scroll_find(f"webdav_{field}_input", "DOWN")
            state["inputs"][field] = c.getText()
        self.scroll_find("webdav_restore_button")
        for action in ACTIONS:
            c = self.get(f"webdav_{action}_button")
            state["actions"][action] = {"text": c.getText(), "enabled": c.isEnabled()}
        for result in ("sync", "backup"):
            c = self.present(f"webdav_{result}_result")
            state["results"][result] = None if c is None else c.getText()
        write_json(self.e.folder / f"{name}-ui-state.json", state)
        self.e.screen(name)
        return state

    def first_layer(self):
        root = self.get("webdav_restore_confirm_dialog")
        self.assertEqual(self.get("webdav_restore_confirm_title").getText(), TITLE)
        message = self.get("webdav_restore_confirm_message").getText()
        self.assertIn("本地", message)
        self.assertIn("未同步", message)
        self.assertIn("学习记录", message)
        self.assertIn("丢失", message)
        for name, text in (("cancel", "取消"), ("continue", "继续")):
            c = self.get(f"webdav_restore_confirm_{name}")
            self.assertEqual(c.getText(), text)
            self.assertTrue(c.isEnabled())
        return root

    def cancel(self, mode: str):
        if mode == "button":
            self.driver.click(self.get("webdav_restore_confirm_cancel"))
        elif mode == "gesture":
            width, height = self.driver.get_display_size()
            start = (1, height // 2)
            end = (int(width * .40), height // 2)
            write_json(self.e.folder / "system-edge-gesture.json", {"started_at": utc(),
                "screen": [width, height], "start": start, "intended_end": end,
                "api": "UiDriver.swipe RIGHT; physical touch starts at screen x=1"})
            self.driver.swipe("RIGHT", distance=40, start_point=start, swipe_time=.4)
        elif mode == "outside":
            b = self.get("webdav_restore_confirm_dialog").getBounds()
            width, height = self.driver.get_display_size()
            point = (width // 2, max(int(height * .10), b.top // 2))
            self.assertLess(point[1], b.top, "Computed point must be genuinely outside dialog")
            write_json(self.e.folder / "outside-point.json", {"dialog": [b.left, b.top, b.right, b.bottom],
                "screen": [width, height], "point": point, "at": utc()})
            self.driver.click(point)
        else:
            raise ValueError(mode)
        time.sleep(.5)
        self.assertIsNone(self.present("webdav_restore_confirm_dialog"), f"{mode} failed to close first layer")

    def sentinel(self, data: dict):
        by_word = {r["word"]: r for r in data["tables"]["words"]}
        self.assertIn("vgspec1_localonly", by_word, "P0: nonempty local-only learning fixture missing")
        self.assertIn("LOCAL_CONFLICT_VALUE", by_word["vgspec1_conflict"]["definition"])
        self.assertEqual(by_word["vgspec1_conflict"]["status"], "REVIEW")
        self.assertTrue(data["tables"]["user_word_books"], "P0: local-only user book missing")

    def safe_cancel_scenario(self, mode: str, reenter=False, restart=False, wait=True):
        ui0 = self.ui_state("before")
        d0 = self.e.db_snapshot("data-before")
        self.sentinel(d0)
        start, at = len(self.probe.requests), utc()
        self.driver.click(self.get("webdav_restore_button"))
        self.first_layer()
        self.e.screen("first-layer")
        if wait:
            for index in range(3):
                time.sleep(.7)
                self.first_layer()
                self.assertEqual(len(self.probe.requests), start, "Request while user has not selected")
            waiting = self.e.db_snapshot("data-while-waiting")
            self.assertEqual(d0["tables"], waiting["tables"], "Learning data changed while waiting")
        self.cancel(mode)
        if reenter:
            self.driver.click(self.get("settings_back_button"))
            self.driver.click(self.get("settings_back_button"))
            self.enter_webdav()
        if restart:
            self.driver.stop_app(BUNDLE)
            self.driver.start_app(BUNDLE, "EntryAbility")
            self.enter_webdav()
        time.sleep(1.2)
        self.assertIsNone(self.present("webdav_restore_confirm_dialog"), "Old confirmation reappeared")
        ui1 = self.ui_state("after")
        if not reenter and not restart:
            self.assertEqual(ui0, ui1, "Cancel must preserve all original inputs, actions and result fields")
        self.assertTrue(all(v["enabled"] for v in ui1["actions"].values()), "Cancel left a busy/disabled action")
        d1 = self.e.db_snapshot("data-after")
        self.assertEqual(d0["tables"], d1["tables"], "Cancel modified real learning/user-book fields")
        self.assertEqual(self.probe.window(start, self.case, at), [], "Cancel/wait window must contain ZERO actual requests")
        self.driver.click(self.get("webdav_restore_button"))
        self.first_layer()
        self.cancel("button")
        self.assertEqual(self.probe.window(start, self.case + "-reopen", at), [], "Old/new confirmation sent late request")

    def import_local_fixture(self):
        """Use the existing real picker/import UI; no database or production writes."""
        from hypium_tests.evidence import local_fixture
        fixture = self.e.folder / "vg-spec1-local-fixture.json"
        write_json(fixture, local_fixture())
        self.e.hdc("file", "send", str(fixture), "/storage/media/100/local/files/Docs/Download/vg-spec1-local-fixture.json")
        self.driver.click(self.get("settings_back_button"))
        self.driver.click(BY.text("备份与恢复"))
        self.driver.click(BY.text("导入"))
        self.require_text("浏览", "Existing local-import picker did not open")
        self.driver.click(BY.text("浏览"))
        self.driver.click(BY.text("我的手机"))
        self.driver.click(self.require_text("Download", "Local Downloads folder missing"))
        self.driver.click(self.require_text("vg-spec1-local-fixture.json", "Synthetic fixture absent from real picker"))
        self.require_text("导入预览", "Existing import preview did not open")
        self.e.screen("fixture-import-preview")
        self.driver.click(BY.text("继续导入"))
        self.require_text("导入成功", "Existing local fixture import failed", timeout=20)
        self.sentinel(self.e.db_snapshot("fixture-imported-data"))

    def test_00_first_use_empty_local_and_cloud(self):
        """R01/R26: fresh app, empty local database and empty controlled cloud."""
        # Assigned emulator holds only synthetic vg-spec1 data. UI fixture import restores it.
        self.e.db_snapshot("before-fresh-app-backup")
        self.driver.stop_app(BUNDLE)
        self.e.hdc("uninstall", BUNDLE)
        hap = ROOT / "entry/build/default/outputs/default/entry-default-unsigned.hap"
        self.e.hdc("install", "-r", str(hap), timeout=60)
        self.driver.start_app(BUNDLE, "EntryAbility")
        self.driver.click(self.require_text("同意并进入", "Fresh app privacy consent missing"))
        self.driver.click(self.require_text("跳过", "Fresh app onboarding missing"))
        self.enter_webdav()
        toggle = self.scroll_find("webdav_auto_sync_toggle")
        if toggle.isChecked():
            self.driver.click(toggle)
        self.assertFalse(self.get("webdav_auto_sync_toggle").isChecked())
        self.configure((f"http://127.0.0.1:{PORT}", "vg_user", "vg_password", "vg_spec1_sync_1234", "/weiyu_vignette"))
        self.probe.mode = "empty"
        d0 = self.e.db_snapshot("fresh-empty-data-before")
        self.assertTrue(all(not rows for rows in d0["tables"].values()))
        ui0 = self.ui_state("fresh-before")
        start, at = len(self.probe.requests), utc()
        self.driver.click(self.get("webdav_restore_button"))
        self.first_layer()
        self.e.screen("fresh-first-layer")
        self.cancel("button")
        self.assertEqual(self.ui_state("fresh-after"), ui0)
        self.assertEqual(self.e.db_snapshot("fresh-empty-data-after")["tables"], d0["tables"])
        self.assertEqual(self.probe.window(start, self.case, at), [])
        self.probe.mode = "success"
        self.import_local_fixture()

    def test_01_wait_then_cancel_button(self):
        """R01-R10/R14-R21/R23: exact first layer, wait, cancel, real data and network."""
        self.safe_cancel_scenario("button")

    def test_02_actual_system_edge_gesture(self):
        """R11/R12/R14-R21/R23: actual edge swipe, independent data and request window."""
        self.safe_cancel_scenario("gesture")

    def test_03_actual_outside_click(self):
        """R11/R13-R21/R23: bounds-derived real outside click."""
        self.safe_cancel_scenario("outside")

    def test_04_rapid_restore_clicks(self):
        """R22: rapid real double tap cannot bypass or stack confirmation."""
        d0 = self.e.db_snapshot("data-before")
        self.sentinel(d0)
        self.scroll_find("webdav_restore_button")
        start, at = len(self.probe.requests), utc()
        self.driver.double_click(self.get("webdav_restore_button"))
        self.first_layer()
        self.assertEqual(len(self.driver.find_all_components(BY.key("webdav_restore_confirm_dialog")) or []), 1)
        self.cancel("button")
        time.sleep(2)
        self.assertIsNone(self.present("webdav_restore_confirm_dialog"), "Late/stacked second confirmation")
        self.assertEqual(self.e.db_snapshot("data-after")["tables"], d0["tables"])
        self.assertEqual(self.probe.window(start, self.case, at), [])

    def test_05_return_and_reenter(self):
        """R24: cancel then leave/reenter, no automatic resume, data persists."""
        self.safe_cancel_scenario("button", reenter=True, wait=False)

    def test_06_cancel_then_force_stop(self):
        """R25: explicit cancel remains terminal after force-stop/restart."""
        self.safe_cancel_scenario("button", restart=True, wait=False)

    def test_07_unconfirmed_force_stop(self):
        """R25: pending first layer cannot resume restore after process death."""
        self.scroll_find("webdav_restore_button")
        d0 = self.e.db_snapshot("data-before")
        self.sentinel(d0)
        start, at = len(self.probe.requests), utc()
        self.driver.click(self.get("webdav_restore_button"))
        self.first_layer()
        self.e.screen("unconfirmed-before-stop")
        self.driver.stop_app(BUNDLE)
        self.driver.start_app(BUNDLE, "EntryAbility")
        self.enter_webdav()
        time.sleep(1)
        self.assertIsNone(self.present("webdav_restore_confirm_dialog"))
        self.assertEqual(self.e.db_snapshot("data-after-restart")["tables"], d0["tables"])
        self.assertEqual(self.probe.window(start, self.case, at), [])
        self.driver.click(self.scroll_find("webdav_restore_button"))
        self.first_layer()
        self.cancel("button")

    def test_08_empty_saved_configuration(self):
        """R26 empty config: no validation/network before first confirmation."""
        self.configure(("", "", "", "", ""))
        self.safe_cancel_scenario("button", wait=False)

    def test_09_whitespace_configuration(self):
        """R26 whitespace fields: first confirmation still precedes validation."""
        self.configure(("   ", "   ", "   ", "   ", "   "))
        self.safe_cancel_scenario("outside", wait=False)

    def test_10_failing_or_delayed_server(self):
        """R27: unavailable/503/delayed server cannot block first-layer cancellation."""
        for mode in ("failure", "delay"):
            with self.subTest(server=mode):
                self.probe.mode = mode
                self.safe_cancel_scenario("button", wait=False)
        self.configure(("http://127.0.0.1:1", "vg_user", "vg_password", "vg_spec1_sync_1234", "/weiyu_vignette"))
        self.safe_cancel_scenario("outside", wait=False)

    def test_11_continue_once_and_preserve_second_confirmation(self):
        """R06/R28 plus existing download/preview/second-layer cancel regression."""
        self.scroll_find("webdav_restore_button")
        d0 = self.e.db_snapshot("data-before")
        self.sentinel(d0)
        start, at = len(self.probe.requests), utc()
        self.driver.click(self.get("webdav_restore_button"))
        self.first_layer()
        self.assertEqual(len(self.probe.requests), start)
        self.driver.double_click(self.get("webdav_restore_confirm_continue"))
        self.require_text("⚠️ 恢复确认", "Existing preview/final confirmation must remain", timeout=35)
        self.require_text("确认恢复", "Final overwrite confirmation must remain")
        self.e.screen("existing-second-confirmation")
        requests = self.probe.window(start, self.case, at)
        gets = [r for r in requests if r["method"] == "GET"]
        self.assertEqual(len(gets), 1, "Repeated continue handed off download more than once")
        self.assertEqual(gets[0]["status"], 200)
        self.assertGreater(gets[0]["response_bytes"], 0)
        heads = [r["path"] for r in requests if r["method"] == "HEAD"]
        self.assertTrue(heads, "Positive control must observe real HEAD")
        self.assertEqual(len(heads), len(set(heads)), "Repeated continue duplicated preflight")
        self.assertEqual(self.e.db_snapshot("data-before-second-confirmation")["tables"], d0["tables"])
        self.driver.click(BY.text("取消"))
        time.sleep(1)
        self.assertEqual(self.e.db_snapshot("data-after-second-cancel")["tables"], d0["tables"])
        self.assertTrue(self.get("webdav_restore_button").isEnabled())

    def test_12_existing_results_survive_all_cancels(self):
        """R18/R19/R21: existing nonempty sync AND backup result fields retained."""
        self.probe.mode = "failure"
        self.driver.click(self.scroll_find("webdav_restore_button"))
        self.first_layer()
        self.driver.click(self.get("webdav_restore_confirm_continue"))
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline and not self.get("webdav_restore_button").isEnabled():
            time.sleep(.4)
        self.assertTrue(self.get("webdav_restore_button").isEnabled(), "Failure regression left busy")
        result = self.get("webdav_backup_result").getText()
        self.assertTrue(result and "正在处理" not in result)
        self.probe.mode = "success"
        for mode in ("button", "gesture", "outside"):
            with self.subTest(cancel=mode):
                self.safe_cancel_scenario(mode, wait=False)
