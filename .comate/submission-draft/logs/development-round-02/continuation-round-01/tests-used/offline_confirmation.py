"""R27 supplement, explicitly selected after official emulator tooling is ready.

The host controller observes transition-request.json, performs the official
per-instance network action, then writes the requested acknowledgement JSON.
Acknowledgement is metadata, never accepted as proof of network isolation:
actual online/offline/restored application requests provide that proof.
This module is outside test_*.py discovery because it requires that controller.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import time

from harness.driver import HarnessTestCase
from hypium import BY

from hypium_tests.evidence import (BUNDLE, PORT, PREFS, ROOT, Evidence, WebDavProbe,
                                   digest, read_preferences, source_fingerprint,
                                   utc, write_json)
from hypium_tests.test_restore_confirmation import RestoreConfirmationTests


class OfflineRestoreTests(RestoreConfirmationTests):
    """Reuses existing strong UI/data assertions; select only test_13 explicitly."""

    @classmethod
    def setUpClass(cls):
        path = os.environ.get("VG_VERIFICATION_MANIFEST")
        if not path:
            raise RuntimeError("Fresh frozen-HAP install manifest required")
        manifest = json.loads(Path(path).read_text(encoding="utf8"))
        if not manifest.get("coordinator_frozen") or not manifest.get("installed_at"):
            raise RuntimeError("Missing source freeze/fresh install")
        cls.original_source = source_fingerprint()
        if manifest["source"] != cls.original_source:
            raise RuntimeError("Source changed; invalidate execution")
        hap = ROOT / "entry/build/default/outputs/default/entry-default-unsigned.hap"
        if digest(hap.read_bytes()) != manifest["hap_sha256"]:
            raise RuntimeError("HAP fingerprint mismatch")
        if not cls.device_sn:
            raise RuntimeError("Explicit dedicated device serial required")
        if manifest.get("device") != cls.device_sn:
            raise RuntimeError("Fresh-install manifest does not identify this device")
        cls.out = ROOT / manifest["evidence_dir"]
        cls.audit = Evidence(cls.out, cls.device_sn)
        cls.probe = WebDavProbe(cls.out / "webdav")
        cls.probe.start()
        # Deliberately no HDC reverse forwarding: guest NAT must be tested.
        HarnessTestCase.setUpClass.__func__(cls)
        cls.driver.set_implicit_wait_time(.2)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "probe"):
            cls.probe.stop()
        if hasattr(cls, "out"):
            after = source_fingerprint()
            write_json(cls.out / "source-after-tests.json", after)
            if after != cls.original_source:
                raise RuntimeError("Production source changed; invalidate execution")

    def setUp(self):
        self.case = self._testMethodName
        self.e = Evidence(self.out / self.case, self.device_sn)
        self.probe.mode = "success"
        self.driver.stop_app(BUNDLE)
        self.driver.start_app(BUNDLE, "EntryAbility")
        self.enter_webdav()
        self.assertFalse(self.scroll_find("webdav_auto_sync_toggle", "DOWN").isChecked())
        self.e.receive(PREFS, self.e.folder / "precondition-preferences.xml")
        self.assertEqual(read_preferences(self.e.folder / "precondition-preferences.xml").get("webdav_autosync_enabled"), "0")
        self.endpoint = f"http://10.0.2.2:{PORT}"
        self.configure((self.endpoint, "vg_user", "vg_password", "vg_spec1_sync_1234", "/weiyu_vignette"))

    @contextmanager
    def evidence_scope(self, name):
        previous_e, previous_case = self.e, self.case
        self.e = Evidence(previous_e.folder / name, self.device_sn)
        self.case = previous_case + "-" + name
        try:
            yield
        finally:
            self.e, self.case = previous_e, previous_case

    def network_state(self, name):
        state = {"captured_at": utc(), "device": self.device_sn, "target_endpoint": self.endpoint,
                 "transport": "guest NAT to host loopback, no HDC rport"}
        for key, args in (("id", ("id",)), ("interface", ("ifconfig", "eth0")),
                          ("routes", ("netstat", "-rn")),
                          ("netconn", ("hidumper", "-s", "NetConnManager")),
                          ("ethernet", ("hidumper", "-s", "EthernetManager"))):
            state[key] = self.e.hdc("shell", *args, check=False)
        self.e.screen(name)
        write_json(self.e.folder / f"{name}-network-state.json", state)
        return state

    def transition(self, name):
        """Coordinate one observed official UI action with the host operator."""
        ack = self.out / f"transition-{name}-ack.json"
        if ack.exists():
            raise RuntimeError("Stale transition acknowledgement; use a fresh evidence directory")
        write_json(self.out / "transition-request.json", {
            "requested_at": utc(), "transition": name, "device": self.device_sn,
            "ack_file": ack.relative_to(ROOT).as_posix(),
            "action": "Use official per-instance Network Disconnection Simulation control; preserve native UI evidence"})
        deadline = time.monotonic() + 900  # Controller coordination ceiling, not a product latency requirement.
        while time.monotonic() < deadline:
            if ack.exists():
                data = json.loads(ack.read_text(encoding="utf8"))
                self.assertEqual(data.get("transition"), name)
                self.assertTrue(data.get("official_action_evidence"), "Missing official UI action evidence reference")
                self.assertEqual(data.get("device"), self.device_sn)
                write_json(self.e.folder / f"transition-{name}-observed.json", data)
                return
            time.sleep(.5)
        self.fail(f"Host official network {name} acknowledgement absent; state is NOT a pass")

    def online_positive(self, name):
        with self.evidence_scope(name):
            self.scroll_find("webdav_restore_button")
            d0 = self.e.db_snapshot("data-before")
            self.sentinel(d0)
            start, at = len(self.probe.requests), utc()
            self.driver.click(self.get("webdav_restore_button"))
            self.first_layer()
            self.assertEqual(len(self.probe.requests), start)
            self.driver.click(self.get("webdav_restore_confirm_continue"))
            self.require_text("⚠️ 恢复确认", "Online NAT route did not reach existing encrypted-backup preview", timeout=45)
            self.require_text("确认恢复", "Existing second confirmation missing")
            self.e.screen("existing-second-confirmation")
            requests = self.probe.window(start, self.case, at)
            gets = [r for r in requests if r["method"] == "GET"]
            self.assertEqual(len(gets), 1)
            self.assertEqual(gets[0]["status"], 200)
            self.assertGreater(gets[0]["response_bytes"], 0)
            self.assertTrue(any(r["method"] == "HEAD" and r["status"] == 200 for r in requests))
            self.driver.click(BY.text("取消"))
            time.sleep(.7)
            self.assertEqual(self.e.db_snapshot("data-after-second-cancel")["tables"], d0["tables"])
            self.assertTrue(self.get("webdav_restore_button").isEnabled())
            self.network_state("network-online")

    def offline_connection_control(self):
        with self.evidence_scope("offline-connection-negative-control"):
            self.scroll_find("webdav_restore_button")
            d0 = self.e.db_snapshot("data-before")
            start, at = len(self.probe.requests), utc()
            result_before = self.get("webdav_backup_result").getText()
            self.driver.click(self.get("webdav_restore_button"))
            self.first_layer()
            self.assertEqual(len(self.probe.requests), start)
            self.driver.click(self.get("webdav_restore_confirm_continue"))
            deadline = time.monotonic() + 150  # Existing production outer timeout is120s.
            while time.monotonic() < deadline:
                if self.get("webdav_restore_button").isEnabled():
                    break
                time.sleep(.4)
            self.assertTrue(self.get("webdav_restore_button").isEnabled(), "Offline continuation never returned to idle")
            self.assertIsNone(self.present("webdav_restore_confirm_dialog"))
            self.assertIsNone(self.driver.find_component(BY.text("⚠️ 恢复确认")))
            result_after = self.get("webdav_backup_result").getText()
            self.assertTrue(result_after and "正在处理" not in result_after)
            self.assertNotEqual(result_before, result_after, "No observable failed continuation result")
            self.e.screen("offline-connection-failure")
            write_json(self.e.folder / "observed-failure-result.json", {"before": result_before, "after": result_after})
            self.assertEqual(self.probe.window(start, self.case, at), [], "Official disconnect did not block actual NAT path")
            self.assertEqual(self.e.db_snapshot("data-after")["tables"], d0["tables"])
            self.network_state("network-offline-at-connection-failure")

    def test_13_actual_offline_three_cancels_and_restore(self):
        """R27 real official per-instance disconnection, controls before/after."""
        self.online_positive("online-before-disconnect")
        try:
            self.transition("disconnect")
            self.network_state("official-disconnected")
            for mode in ("button", "gesture", "outside"):
                with self.evidence_scope("offline-" + mode):
                    self.network_state("offline-before-action")
                    self.safe_cancel_scenario(mode, wait=True)
                    self.network_state("offline-after-action")
            self.offline_connection_control()
        finally:
            # Also closes any still-pending network control before reconnect.
            try:
                self.driver.stop_app(BUNDLE)
            finally:
                self.transition("restore")
            self.driver.start_app(BUNDLE, "EntryAbility")
            self.enter_webdav()
        self.online_positive("online-after-restore")
        write_json(self.e.folder / "offline-verdict.json", {
            "at": utc(), "three_offline_cancels": "pass", "online_before": "HEAD/GET200",
            "offline_actual_same_path": "Failed continuation with zero server arrivals",
            "online_after": "HEAD/GET200", "network_restore": "observed", "device": self.device_sn})
