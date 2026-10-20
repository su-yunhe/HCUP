"""Real-device restoration acceptance. Run only after fresh HAP installation."""
from __future__ import annotations

import json
import os
import re
import time

from harness.driver import HarnessTestCase
from hypium import BY
from hypium.model.basic_data_type import InputTextMode

from .restore_support import (BUNDLE, DEVICE, OUT, PASSWORD, PORT, SYNC_PASSWORD, USERNAME, WORD_PREFIX,
                              ControlledDav, event, hdc, snapshot, visible)


class RestoreAcceptance(HarnessTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver.set_implicit_wait_time(0.2)
        cls.dav = ControlledDav()
        cls.dav.start()
        cls.results = []

    @classmethod
    def tearDownClass(cls):
        cls.dav.stop()
        (OUT / "scenario-results.json").write_text(json.dumps(cls.results, ensure_ascii=False, indent=2), encoding="utf-8")

    def setUp(self):
        selected = os.environ.get("VG15_CASES", "")
        if selected and self._testMethodName not in selected.split(","):
            self.skipTest("Not selected in this explicitly installed execution")
        self.started = time.monotonic()
        self._last_values = {}
        self.dav.release()
        event("test_begin", test=self._testMethodName)
        self.driver.stop_app(BUNDLE)
        self.driver.start_app(BUNDLE, "EntryAbility", wait_time=1)
        # Privacy consent has already been explicitly authorized by the human.
        consent = self.driver.find_component(BY.text("同意并进入"))
        if consent:
            self.driver.click(consent)
        self.click_id("home_settings_entry")
        self.click_id("settings_section_sync")
        self.require_component(BY.key("webdav_endpoint"), "WebDAV configuration unavailable")
        self.disable_auto_sync()

    def tearDown(self):
        self.dav.release()
        if hasattr(self, "started"):
            try:
                snapshot(self._testMethodName + "-end")
            finally:
                event("test_end", test=self._testMethodName, seconds=time.monotonic() - self.started)

    def mark(self, name, requirements, **facts):
        row = event("verified_scenario", test=self._testMethodName, name=name,
                    requirements=requirements, status="pass", **facts)
        self.results.append(row)

    def scroll_top(self):
        for _ in range(3):
            self.driver.swipe("DOWN", distance=75)

    def get(self, key, scroll=True):
        component = self.driver.find_component(BY.key(key))
        if component is not None:
            return component
        if scroll:
            for _ in range(5):
                self.driver.swipe("UP", distance=55)
                component = self.driver.find_component(BY.key(key))
                if component is not None:
                    return component
            self.scroll_top()
            for _ in range(5):
                component = self.driver.find_component(BY.key(key))
                if component is not None:
                    return component
                self.driver.swipe("UP", distance=45)
        self.fail(f"Missing stable id {key}")

    def click_id(self, key):
        component = self.stable_enabled(key)
        self.driver.click(component)

    def stable_enabled(self, key, timeout=8):
        self.get(key)
        previous, consecutive = None, 0
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            component = self.driver.find_component(BY.key(key))
            if component is not None and component.isEnabled():
                b = component.getBounds()
                bounds = (b.left, b.top, b.right, b.bottom)
                consecutive = consecutive + 1 if previous == bounds else 1
                previous = bounds
                if consecutive >= 3:
                    event("stable_enabled_target", key=key, bounds=bounds, observations=consecutive)
                    return component
            else:
                consecutive = 0
            time.sleep(0.15)
        self.fail(f"{key} did not become stably enabled")

    def disable_auto_sync(self):
        toggle = self.get("webdav_auto_sync_enabled")
        if toggle.isChecked():
            self.driver.click(toggle)
        self.assertFalse(self.get("webdav_auto_sync_enabled").isChecked())
        self.scroll_top()

    def input(self, key, value):
        component = self.get(key)
        if component.getText() == value:
            event("input_already_equal", key=key, value=value)
            return
        self.driver.input_text(component, value, mode=InputTextMode().paste(True))
        self.driver.press_back()
        event("input", key=key, value=value, fake_credentials=True)

    def fill(self, profile="B", overrides=None):
        self.scroll_top()
        values = {"webdav_endpoint": f"http://127.0.0.1:{PORT}/{profile}",
                  "webdav_username": USERNAME, "webdav_password": PASSWORD,
                  "webdav_sync_password": SYNC_PASSWORD, "webdav_remote_root": "/restore-fixture"}
        values.update(overrides or {})
        for key, value in values.items():
            if self._last_values.get(key) != value:
                self.input(key, value)
        self._last_values = values.copy()
        for key in ("webdav_endpoint", "webdav_username", "webdav_remote_root"):
            self.assertEqual(self.get(key).getText(), values[key])
        event("form_filled", profile=profile, values=values)
        return values

    def dialog(self, text):
        # Native dialogs can animate; compare two actual visible bounds before tap.
        previous = None
        for _ in range(6):
            component = self.driver.find_component(BY.text(text))
            if component is not None:
                bounds = component.getBounds()
                current = (bounds.left, bounds.top, bounds.right, bounds.bottom)
                if current == previous:
                    event("dialog_action", text=text, bounds=current)
                    self.driver.click(component)
                    return current
                previous = current
            time.sleep(0.15)
        self.fail(f"Native dialog action {text!r} failed to stabilize")

    def open_first(self):
        self.click_id("webdav_restore_from_cloud")
        self.require_text("继续", "First confirmation absent")
        event("first_dialog_open")

    def wait_first_closed(self, timeout=8):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            present = self.driver.find_component(BY.text("继续")) is not None
            event("first_dialog_close_observation", present=present)
            if not present:
                self.stable_enabled("webdav_restore_from_cloud")
                return
            time.sleep(0.15)
        self.fail("First confirmation did not actually disappear within bounded UI wait")

    def start_restore(self):
        self.open_first()
        event("first_continue_before")
        bounds = self.dialog("继续")
        event("first_continue_after")
        return bounds

    def wait_request(self, cursor, backup=True, timeout=12):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            rows = self.dav.rows[cursor:]
            selected = [r for r in rows if not backup or "backup" in r["path"].lower()]
            if selected:
                return selected
            time.sleep(0.05)
        self.fail("Genuine restoration request never reached controlled WebDAV")

    def pending_samples(self, name, cursor, profile="B"):
        requests = self.wait_request(cursor)
        self.assertTrue(all(r["auth_matches"] for r in self.dav.rows[cursor:]))
        self.assertTrue(all(r["path"].startswith(f"/{profile}/") for r in self.dav.rows[cursor:]))
        for sample in range(3):
            # UI tree visibility, component TYPE and id; hidden nodes are insufficient.
            items = snapshot(f"{name}-pending-{sample}")
            loading = [n for n in items if n.get("id") == "webdav_restore_loading" and visible(n)]
            status = [n for n in items if n.get("id") == "webdav_restore_status" and visible(n)]
            self.assertEqual(len(loading), 1, "No visible real restore loading node")
            self.assertEqual(loading[0]["type"], "LoadingProgress")
            self.assertEqual(len(status), 1, "Restore progress status not visible")
            self.assertRegex(status[0].get("text", ""), r"正在|处理中")
            self.assertFalse(self.get("webdav_restore_from_cloud").isEnabled())
            self.assertFalse(self.dav.gate.is_set(), "Controlled real request already released")
            self.assertTrue(any(r["request_id"] in self.dav.active for r in requests), "No genuine request remains pending at sample")
            event("pending_ui_asserted", name=name, sample=sample, loading=loading, status=status,
                  request_ids=[r["request_id"] for r in requests])
        self.dav.release()

    def terminal(self, contains=None, timeout=60):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            button = self.driver.find_component(BY.key("webdav_restore_from_cloud"))
            if button is not None and button.isEnabled():
                status = self.get("webdav_restore_status").getText()
                if contains:
                    self.assertIn(contains, status)
                items = snapshot("terminal")
                self.assertFalse(any(n.get("id") == "webdav_restore_loading" and visible(n) for n in items),
                                 "Spinner remained after genuine completion")
                event("terminal_asserted", status=status)
                return status
            time.sleep(0.15)
        self.fail("Restore never released actual busy state")

    def wait_second(self, timeout=75):
        self.require_text("确认恢复", "Valid encrypted backup did not reach second confirmation", timeout=timeout)
        items = snapshot("second-confirmation")
        self.assertFalse(any(n.get("id") == "webdav_restore_loading" and visible(n) for n in items))
        self.assertFalse(any(n.get("id") == "webdav_restore_status" and visible(n)
                             and re.search(r"正在|处理中", n.get("text", "")) for n in items))

    def actual_export(self):
        old = len(self.dav.exports)
        self.click_id("webdav_backup_now")
        deadline = time.monotonic() + 100
        while len(self.dav.exports) == old and time.monotonic() < deadline:
            time.sleep(0.1)
        self.assertGreater(len(self.dav.exports), old, "Actual backup export was not received")
        deadline = time.monotonic() + 15
        while not self.get("webdav_backup_now").isEnabled() and time.monotonic() < deadline:
            time.sleep(0.1)
        self.assertTrue(self.get("webdav_backup_now").isEnabled())
        return self.dav.exports[-1]

    def test_01_first_entry_direct_configuration(self):
        # Explicitly persist invalid settings first, removing valid baseline config pollution.
        self.fill(overrides={k: "" for k in ("webdav_endpoint", "webdav_username", "webdav_password", "webdav_sync_password")})
        self.click_id("webdav_save_settings")
        time.sleep(0.4)
        self.driver.stop_app(BUNDLE)
        self.driver.start_app(BUNDLE, "EntryAbility", wait_time=1)
        self.click_id("home_settings_entry")
        self.click_id("settings_section_sync")
        self.assertEqual(self.get("webdav_endpoint").getText(), "")
        self.fill()
        cursor = self.dav.configure("fresh-direct", hold=True)
        self.start_restore()
        self.pending_samples("fresh-direct", cursor)
        self.terminal("暂无备份")
        self.mark("fresh-direct-404", [f"A{i:02d}" for i in range(1, 14)] + ["A20", "A26", "A27"])

    def test_00_input_binding_diagnostic(self):
        readings = []
        for paste in (True, False):
            self.scroll_top()
            value = f"http://127.0.0.1:{PORT}/" + ("PASTE" if paste else "CHARS")
            self.driver.input_text(self.get("webdav_endpoint"), value, mode=InputTextMode().paste(paste))
            self.driver.press_back()
            self.assertEqual(self.get("webdav_endpoint").getText(), value)
            snapshot("binding-before-save-" + str(paste))
            self.click_id("webdav_save_settings")
            time.sleep(0.5)
            self.driver.stop_app(BUNDLE)
            self.driver.start_app(BUNDLE, "EntryAbility", wait_time=1)
            self.click_id("home_settings_entry")
            self.click_id("settings_section_sync")
            saved = self.get("webdav_endpoint").getText()
            readings.append({"paste":paste,"entered":value,"after_restart":saved})
            event("binding_readback", **readings[-1])
            snapshot("binding-after-restart-" + str(paste))
            self.assertEqual(saved, value, "Explicit Save/restart lost entered endpoint")
        (OUT / "input-binding-diagnostic.json").write_text(json.dumps(readings,indent=2),encoding="utf-8")
        self.mark("input-modes-save-and-restart", ["A02", "A25", "A27"])

    def test_00a_first_confirm_form_diagnostic(self):
        values = self.fill("UNSAVED")
        self.scroll_top()
        self.click_id("webdav_password_toggle")
        self.assertEqual(self.get("webdav_password").getText(), PASSWORD, "Visibility toggle lost live password")
        self.assertEqual(self.get("webdav_endpoint").getText(), values["webdav_endpoint"])
        self.click_id("webdav_password_toggle")
        self.click_id("webdav_sync_password_toggle")
        self.assertEqual(self.get("webdav_sync_password").getText(), SYNC_PASSWORD, "Visibility toggle lost live sync password")
        self.click_id("webdav_sync_password_toggle")
        password_before = self.get("webdav_password").getText()
        sync_before = self.get("webdav_sync_password").getText()
        snapshot("form-before-first-dialog")
        self.open_first()
        snapshot("form-during-first-dialog")
        self.dialog("取消")
        self.scroll_top()
        snapshot("form-after-first-cancel")
        actual = {k: self.get(k).getText() for k in ("webdav_endpoint", "webdav_username", "webdav_remote_root")}
        event("first_confirm_form_readback", before=values, after_cancel=actual)
        (OUT / "first-confirm-form-diagnostic.json").write_text(json.dumps({"before":values,"after_cancel":actual},indent=2),encoding="utf-8")
        self.assertEqual(actual["webdav_endpoint"], values["webdav_endpoint"], "Opening/canceling first confirm reset unsaved endpoint")
        self.assertEqual(actual["webdav_username"], values["webdav_username"], "First confirm reset username")
        self.assertEqual(self.get("webdav_password").getText(), password_before, "First confirm reset password")
        self.assertEqual(self.get("webdav_sync_password").getText(), sync_before, "First confirm reset sync password")
        toggle = self.get("webdav_auto_sync_enabled")
        self.assertFalse(toggle.isChecked())
        self.driver.click(toggle)
        self.assertTrue(self.get("webdav_auto_sync_enabled").isChecked())
        self.click_id("settings_back")
        self.click_id("settings_section_sync")
        self.assertTrue(self.get("webdav_auto_sync_enabled").isChecked(), "Auto-sync true setting failed section reentry")
        self.assertEqual(self.get("webdav_endpoint").getText(), values["webdav_endpoint"], "Switch/reentry lost unsaved form")
        self.driver.click(self.get("webdav_auto_sync_enabled"))
        self.assertFalse(self.get("webdav_auto_sync_enabled").isChecked())
        self.mark("first-confirm-preserves-unsaved-public-and-password-fields", ["A02", "A16", "A27"])

    def test_02_saved_A_draft_B_cancel_and_close(self):
        self.fill("A")
        self.click_id("webdav_save_settings")
        time.sleep(0.4)
        self.fill("B")
        cursor = self.dav.configure("first-cancel")
        self.open_first()
        snapshot("first-cancel-waiting")
        self.dialog("取消")
        self.wait_first_closed()
        self.assertEqual(self.dav.rows[cursor:], [], "First cancel started a restore")
        self.open_first()
        self.driver.press_back()
        self.wait_first_closed()
        self.assertEqual(self.dav.rows[cursor:], [], "First close started a restore")
        self.driver.stop_app(BUNDLE)
        self.driver.start_app(BUNDLE, "EntryAbility", wait_time=1)
        self._last_values = {}
        self.click_id("home_settings_entry")
        self.click_id("settings_section_sync")
        self.assertTrue(self.get("webdav_endpoint").getText().endswith("/A"), "Cancel/close persisted unsaved B")
        self.assertFalse(self.get("webdav_auto_sync_enabled").isChecked(), "Disabled auto-sync failed restart persistence")
        self._last_values = {}
        self.mark("first-cancel-close-preserves-saved-A", ["A16", "A17", "A22", "A27", "A25"])
        self.fill("B")
        cursor = self.dav.configure("saved-A-draft-B", hold=True)
        self.start_restore()
        self.pending_samples("saved-A-draft-B", cursor)
        self.terminal("暂无备份")
        self.mark("saved-A-draft-B-current-values", ["A02", "A05", "A12", "A13", "A27"])

    def test_03_fast_and_repeated_clicks(self):
        self.fill()
        cursor = self.dav.configure("repeat", hold=True)
        component = self.stable_enabled("webdav_restore_from_cloud")
        bounds = component.getBounds()
        point = ((bounds.left + bounds.right) // 2, (bounds.top + bounds.bottom) // 2)
        for index in range(3):
            event("rapid_entry_tap_before", index=index, point=point)
            self.driver.click(point)
            observed = self.driver.find_all_components(BY.text("继续")) or []
            event("rapid_entry_tap_after", index=index, native_dialogs=len(observed))
            self.assertLessEqual(len(observed), 1, "Rapid entry stacked confirmation dialogs")
            self.assertEqual(self.dav.rows[cursor:], [])
        dialogs = self.driver.find_all_components(BY.text("继续")) or []
        snapshot("rapid-entry-native-result")
        self.assertLessEqual(len(dialogs), 1, "Rapid entry stacked competing confirmation dialogs")
        self.assertEqual(self.dav.rows[cursor:], [], "Rapid unconfirmed entry started unauthorized restoration")
        event("rapid_entry_observed", native_dialogs=len(dialogs), unauthorized_requests=0)
        if not dialogs:
            # Native autoCancel can consume subsequent taps as outside-dialog taps.
            # The approved contract permits stable 0/1 and still requires a new genuine flow.
            self.stable_enabled("webdav_restore_from_cloud")
            self.open_first()
        self.assertEqual(len(self.driver.find_all_components(BY.text("继续")) or []), 1)
        button_bounds = self.dialog("继续")
        action_point = ((button_bounds[0] + button_bounds[2]) // 2, (button_bounds[1] + button_bounds[3]) // 2)
        for _ in range(3):
            self.driver.click(action_point)
        self.wait_request(cursor)
        self.assertFalse(self.get("webdav_restore_from_cloud").isEnabled())
        for _ in range(3):
            self.driver.click(point)
        self.assertIsNone(self.driver.find_component(BY.text("继续")))
        self.pending_samples("repeat", cursor)
        self.terminal("暂无备份")
        heads = [r for r in self.dav.rows[cursor:] if r["method"] == "HEAD" and r["path"].endswith("/restore-fixture")]
        self.assertEqual(len(heads), 1, "Competing preflight chains started")
        self.mark("rapid-entry-continue-and-pending-repeat", ["A18", "A19", "A26"])

    def test_04_valid_backup_cancel_then_actual_import(self):
        self.fill()
        self.click_id("webdav_save_settings")
        self.dav.configure("business-before", "valid")
        before = self.actual_export()
        before_words = {w["word"] for w in before["words"]}
        self.assertNotIn(WORD_PREFIX + "0000", before_words, "This run's fixture already present; cancellation comparison invalid")
        cursor = self.dav.configure("second-cancel", "valid", hold=True)
        self.start_restore()
        self.pending_samples("second-cancel", cursor)
        self.wait_second()
        count = len(self.dav.rows)
        time.sleep(0.5)
        snapshot("second-wait-extended")
        self.assertEqual(len(self.dav.rows), count, "Human confirmation wait created new download")
        self.dialog("取消")
        self.terminal("取消")
        self.dav.configure("business-after-second-cancel", "valid")
        after_cancel = self.actual_export()
        self.assertEqual({w["word"] for w in after_cancel["words"]}, before_words)
        self.mark("second-cancel-business-unchanged", ["A22", "A28"])
        cursor = self.dav.configure("actual-import", "valid", hold=True)
        self.start_restore()
        self.pending_samples("actual-import", cursor)
        self.wait_second()
        event("second_continue_before")
        self.dialog("确认恢复")
        event("second_continue_after")
        import_items = snapshot("actual-import-working")
        import_loading = [n for n in import_items if n.get("id") == "webdav_restore_loading" and visible(n)]
        self.assertEqual(len(import_loading), 1, "Actual import progress not observed")
        self.assertEqual(import_loading[0]["type"], "LoadingProgress")
        self.assertTrue(any(n.get("id") == "webdav_restore_status" and visible(n)
                            and "正在恢复" in n.get("text", "") for n in import_items))
        self.terminal("恢复完成", timeout=100)
        self.dav.configure("business-after-import", "valid")
        exported = self.actual_export()
        restored = {w["word"] for w in exported["words"]}
        expected = {f"{WORD_PREFIX}{i:04d}" for i in range(1000)}
        self.assertTrue(expected.issubset(restored), f"Actual business data missing {len(expected - restored)} fixture words")
        self.mark("genuine-decrypt-preview-authorized-import-export-readback", ["A05", "A09", "A12", "A13", "A26", "A28"],
                  fixture_words=1000, exported_words=len(restored))

    def test_05_network_and_data_failures_retry(self):
        self.fill()
        cases = [("unauthorized", None), ("forbidden", None), ("server_error", None),
                 ("disconnect", None), ("bad_encrypted", "解密失败"), ("wrong_password", "解密失败"),
                 ("bad_preview", "预览失败"), ("empty_plain", None), ("missing", "暂无备份")]
        for mode, expected in cases:
            with self.subTest(mode=mode):
                cursor = self.dav.configure(mode, mode)
                self.start_restore()
                text = self.terminal(expected, timeout=65)
                self.assertNotIn("恢复完成", text)
                self.assertGreater(len(self.dav.rows[cursor:]), 0)
                self.mark(mode, ["A20", "A23", "A26"])
        self.dav.configure("legal-empty-business", "empty_business")
        self.start_restore()
        self.wait_second()
        self.dialog("确认恢复")
        self.terminal("恢复完成")
        self.mark("legal-empty-business-separate-from-empty-plaintext", ["A20", "A28"])

    def test_06_empty_and_whitespace_inputs(self):
        for value in ("", "   "):
            for key in ("webdav_endpoint", "webdav_username", "webdav_password", "webdav_sync_password"):
                with self.subTest(value=repr(value), key=key):
                    self.fill(overrides={key: value})
                    cursor = self.dav.configure(f"invalid-{key}-{len(value)}")
                    self.start_restore()
                    text = self.terminal()
                    self.assertEqual(self.dav.rows[cursor:], [], "Invalid current field used saved valid config")
                    self.assertNotIn("恢复完成", text)
                    self.mark(f"input-{key}-{len(value)}", ["A14" if not value else "A15", "A27"])
            with self.subTest(value=repr(value), key="all"):
                self.fill(overrides={k: value for k in ("webdav_endpoint", "webdav_username", "webdav_password", "webdav_sync_password")})
                cursor = self.dav.configure("all-invalid")
                self.start_restore()
                self.terminal()
                self.assertEqual(self.dav.rows[cursor:], [])
        for directory in ("", "   "):
            self.fill(overrides={"webdav_remote_root": directory})
            cursor = self.dav.configure("default-directory")
            self.start_restore()
            self.terminal("暂无备份")
            self.assertTrue(all("/weiyu_sync" in r["path"] for r in self.dav.rows[cursor:]))
        self.mark("empty-space-and-directory-defaults-real-password-spaces", ["A14", "A15"])

    def test_07_lifecycle_observation(self):
        self.fill()
        self.click_id("webdav_save_settings")
        self.dav.configure("lifecycle-terminal")
        self.start_restore()
        self.terminal("暂无备份")
        self.click_id("settings_back")
        snapshot("section-return")
        self.click_id("settings_section_sync")
        snapshot("section-reenter")
        self.click_id("settings_back")
        self.click_id("settings_back")
        snapshot("route-return")
        self.click_id("home_settings_entry")
        self.click_id("settings_section_sync")
        snapshot("route-reenter")
        hdc(["shell", "uitest", "uiInput", "keyEvent", "Home"], "background")
        self.driver.start_app(BUNDLE, "EntryAbility", wait_time=0.5)
        snapshot("foreground-reenter")
        self.driver.stop_app(BUNDLE)
        self.driver.start_app(BUNDLE, "EntryAbility", wait_time=1)
        self.click_id("home_settings_entry")
        self.click_id("settings_section_sync")
        snapshot("process-restart")
        self.mark("observed-return-reenter-background-and-process-restart", ["A24", "A25", "A31"],
                  scope="Exploratory observations only; no invented persistence or continuation contract")
