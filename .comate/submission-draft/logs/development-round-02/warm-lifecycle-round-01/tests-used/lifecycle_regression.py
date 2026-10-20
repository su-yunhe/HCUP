"""Explicit warm-background regression; no administrator or WFP facility."""
import time

from hypium import BY
from hypium_tests.evidence import BUNDLE, read_preferences, utc, write_json
from hypium_tests.offline_confirmation import OfflineRestoreTests


class WarmLifecycleTests(OfflineRestoreTests):
    def app_pid(self, name):
        result = self.e.hdc("shell", "pidof", BUNDLE)
        pids = result["stdout"].strip().split()
        self.assertEqual(len(pids), 1, "Need one observable app process for warm return")
        self.assertTrue(pids[0].isdigit())
        write_json(self.e.folder / (name + "-pid.json"), {"at": utc(), "bundle": BUNDLE, "pid": pids[0], "command": result})
        return pids[0]

    def test_20_pending_confirmation_warm_home_and_return(self):
        self.online_positive("live-server-positive-before")
        ui0 = self.ui_state("before-warm-window")
        d0 = self.e.db_snapshot("data-before-warm-window")
        self.sentinel(d0)
        prefs0 = read_preferences(self.e.folder / "data-before-warm-window/webdav_state_store.xml")
        self.assertEqual(prefs0.get("webdav_autosync_enabled"), "0")
        start, at = len(self.probe.requests), utc()
        self.driver.click(self.get("webdav_restore_button"))
        self.first_layer()
        self.e.screen("pending-before-home")
        before_pid = self.app_pid("before-home")
        self.driver.press_home()
        time.sleep(1)
        self.e.screen("actual-home-background")
        self.assertIsNone(self.present("webdav_restore_confirm_title"), "App dialog still foreground after Home")
        self.assertIsNone(self.present("webdav_restore_button"), "App page still foreground after Home")
        background_pid = self.app_pid("while-home-background")
        self.assertEqual(background_pid, before_pid)
        self.driver.start_app(BUNDLE, "EntryAbility")
        time.sleep(1)
        after_pid = self.app_pid("after-warm-return")
        self.assertEqual(after_pid, before_pid, "Return was not warm: app PID changed")
        self.e.screen("warm-return-raw")
        dialogs = self.driver.find_all_components(BY.key("webdav_restore_confirm_dialog")) or []
        self.assertLessEqual(len(dialogs), 1, "Stacked old confirmation after warm return")
        if dialogs:
            self.first_layer()
            modal_outcome = "one_pending_first_layer_retained_then_explicitly_canceled"
            self.cancel("button")
        else:
            modal_outcome = "platform_first_layer_dismissed"
            if self.present("settings_entry_button") is not None:
                self.enter_webdav()
            elif self.present("settings_section_sync") is not None:
                self.driver.click(self.get("settings_section_sync"))
        time.sleep(1.2)
        self.assertIsNone(self.present("webdav_restore_confirm_dialog"))
        self.assertEqual(self.ui_state("after-warm-cancel"), ui0)
        d1 = self.e.db_snapshot("data-after-warm-cancel")
        self.assertEqual(d1["tables"], d0["tables"])
        self.assertEqual(read_preferences(self.e.folder / "data-after-warm-cancel/webdav_state_store.xml"), prefs0)
        self.assertFalse(self.scroll_find("webdav_auto_sync_toggle", "DOWN").isChecked())
        self.scroll_find("webdav_restore_button")
        self.assertEqual(self.probe.window(start, self.case + "-warm-home-return", at), [])
        self.driver.click(self.get("webdav_restore_button"))
        self.first_layer()
        self.cancel("button")
        time.sleep(1.2)
        self.assertIsNone(self.present("webdav_restore_confirm_dialog"))
        self.assertEqual(self.ui_state("after-fresh-reopen-cancel"), ui0)
        d2 = self.e.db_snapshot("data-after-fresh-reopen-cancel")
        self.assertEqual(d2["tables"], d0["tables"])
        self.assertEqual(read_preferences(self.e.folder / "data-after-fresh-reopen-cancel/webdav_state_store.xml"), prefs0)
        self.assertEqual(self.probe.window(start, self.case + "-fresh-reopen-no-late-request", at), [])
        write_json(self.e.folder / "warm-lifecycle-verdict.json", {
            "at": utc(), "before_pid": before_pid, "background_pid": background_pid,
            "return_pid": after_pid, "same_pid": True, "modal_outcome": modal_outcome,
            "old_continue_clicked": False, "force_stop_between_home_and_return": False,
            "page_hide_callback_observed": False, "callback_evidence_claim": "UI/process observations only; no production callback instrumentation",
            "nine_tables_and_preferences_equal": True, "UI0_equal": True,
            "actual_requests_in_warm_and_reopen_windows": 0})
        self.online_positive("live-server-positive-after")
