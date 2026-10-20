"""Explicitly selected existing continuation branches; final import runs last."""
import time

from hypium import BY

from hypium_tests.evidence import BUNDLE, utc, write_json
from hypium_tests.test_restore_confirmation import RestoreConfirmationTests, ACTIONS


class ContinuationRegressionTests(RestoreConfirmationTests):
    def continue_first_layer(self):
        self.scroll_find("webdav_restore_button")
        start, at = len(self.probe.requests), utc()
        self.driver.click(self.get("webdav_restore_button"))
        self.first_layer()
        self.assertEqual(len(self.probe.requests), start, "First layer must precede every continuation request")
        self.e.screen("first-layer")
        self.driver.click(self.get("webdav_restore_confirm_continue"))
        return start, at

    def wait_idle_result(self, phrase):
        deadline = time.monotonic() + 150  # Existing wrapper timeout120s plus facility margin.
        result = ""
        while time.monotonic() < deadline:
            component = self.present("webdav_backup_result")
            result = component.getText() if component is not None else ""
            if phrase in result and self.get("webdav_restore_button").isEnabled():
                break
            time.sleep(.4)
        self.assertIn(phrase, result)
        for action in ACTIONS:
            self.assertTrue(self.get(f"webdav_{action}_button").isEnabled(), f"{action} remained disabled")
        self.assertIsNone(self.present("webdav_restore_confirm_dialog"))
        self.e.screen("completed-result")
        write_json(self.e.folder / "observed-result.json", {"at": utc(), "text": result})
        return result

    def verify_can_reopen_without_request(self):
        start, at = len(self.probe.requests), utc()
        self.driver.click(self.get("webdav_restore_button"))
        self.first_layer()
        self.cancel("button")
        self.assertEqual(self.probe.window(start, self.case + "-reopen", at), [])

    def test_14_continue_configuration_error_releases_busy(self):
        self.configure(("", "", "", "", ""))
        d0 = self.e.db_snapshot("data-before")
        self.sentinel(d0)
        start, at = self.continue_first_layer()
        self.wait_idle_result("未配置 WebDAV 地址")
        self.assertIsNone(self.driver.find_component(BY.text("⚠️ 恢复确认")))
        self.assertEqual(self.probe.window(start, self.case, at), [])
        self.assertEqual(self.e.db_snapshot("data-after")["tables"], d0["tables"])
        self.verify_can_reopen_without_request()

    def test_15_continue_no_cloud_backup_releases_busy(self):
        self.probe.mode = "no-backup"
        d0 = self.e.db_snapshot("data-before")
        self.sentinel(d0)
        start, at = self.continue_first_layer()
        self.wait_idle_result("云端暂无备份")
        self.assertIsNone(self.driver.find_component(BY.text("⚠️ 恢复确认")))
        requests = self.probe.window(start, self.case, at)
        self.assertTrue(any(r["method"] == "HEAD" and r["status"] == 404 for r in requests))
        self.assertFalse(any(r["method"] == "GET" for r in requests))
        self.assertEqual(self.e.db_snapshot("data-after")["tables"], d0["tables"])
        self.verify_can_reopen_without_request()

    def test_16_continue_real_get_failure_releases_busy(self):
        self.probe.mode = "download-failure"
        d0 = self.e.db_snapshot("data-before")
        self.sentinel(d0)
        start, at = self.continue_first_layer()
        self.wait_idle_result("下载失败")
        self.assertIsNone(self.driver.find_component(BY.text("⚠️ 恢复确认")))
        requests = self.probe.window(start, self.case, at)
        gets = [r for r in requests if r["method"] == "GET"]
        self.assertEqual(len(gets), 1)
        self.assertEqual(gets[0]["status"], 503)
        self.assertTrue(any(r["method"] == "HEAD" and r["status"] == 200 for r in requests))
        self.assertEqual(self.e.db_snapshot("data-after")["tables"], d0["tables"])
        self.verify_can_reopen_without_request()

    def test_17_explicit_second_confirmation_imports_cloud_conflict(self):
        """Run last; retain original raw DB/WAL/prefs before changing synthetic data."""
        self.scroll_find("webdav_restore_button")
        d0 = self.e.db_snapshot("data-before-final-import-backup")
        self.sentinel(d0)
        before_words = {r["word"]: r for r in d0["tables"]["words"]}
        start, at = self.continue_first_layer()
        self.require_text("⚠️ 恢复确认", "Existing second confirmation missing", timeout=45)
        self.require_text("确认恢复", "Final explicit import action missing")
        self.e.screen("second-confirmation-before-final-choice")
        self.assertEqual(self.e.db_snapshot("data-before-final-choice")["tables"], d0["tables"])
        self.driver.click(BY.text("确认恢复"))
        result = self.wait_idle_result("恢复完成")
        self.assertTrue(result.startswith("✅"), result)
        after = self.e.db_snapshot("data-after-explicit-import")
        words = {r["word"]: r for r in after["tables"]["words"]}
        # This task's existing import merges words; it does not clear the database.
        self.assertEqual(words["vgspec1_localonly"], before_words["vgspec1_localonly"])
        self.assertEqual(words["vgspec1_conflict"]["status"], "KNOWN")
        self.assertIn("CLOUD_CONFLICT_VALUE", words["vgspec1_conflict"]["definition"])
        self.assertIn("CLOUD_CONFLICT_VALUE", words["vgspec1_conflict"]["tags"])
        self.assertNotEqual(words["vgspec1_conflict"], before_words["vgspec1_conflict"])
        requests = self.probe.window(start, self.case, at)
        gets = [r for r in requests if r["method"] == "GET"]
        self.assertEqual(len(gets), 1)
        self.assertEqual(gets[0]["status"], 200)
        self.driver.stop_app(BUNDLE)
        self.driver.start_app(BUNDLE, "EntryAbility")
        self.enter_webdav()
        self.assertEqual(self.e.db_snapshot("data-after-import-cold-restart")["tables"], after["tables"])
        write_json(self.e.folder / "explicit-import-verdict.json", {
            "at": utc(), "first_layer_only_did_not_import": True,
            "second_confirmation_explicitly_clicked": True, "conflict_status": "KNOWN",
            "conflict_definition_tags": "CLOUD_CONFLICT_VALUE", "local_only_preserved": True,
            "persisted_after_cold_restart": True,
            "pre_import_backup_directory": "data-before-final-import-backup"})
