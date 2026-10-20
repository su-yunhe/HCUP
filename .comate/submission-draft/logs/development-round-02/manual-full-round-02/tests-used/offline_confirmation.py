"""R27 supplement with a human controlling only the assigned emulator network.

The coordinator observes transition-request.json, waits for the user's action,
then records the actual method and matching nonce acknowledgement JSON.
Acknowledgement is metadata, never accepted as proof of network isolation:
actual online/offline/restored application requests provide that proof.
This module is outside test_*.py discovery because it requires that controller.
"""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import time
import uuid
import http.client

from harness.driver import HarnessTestCase
from hypium import BY

from hypium_tests.evidence import (BUNDLE, PORT, PREFS, ROOT, Evidence, WebDavProbe,
                                   digest, read_preferences, source_fingerprint,
                                   utc, write_json)
from hypium_tests.test_restore_confirmation import RestoreConfirmationTests, ACTIONS


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
        """Pause for the user's real method; ACK is not an isolation verdict."""
        ack = self.out / f"transition-{name}-ack.json"
        if ack.exists():
            raise RuntimeError("Stale transition acknowledgement; use a fresh evidence directory")
        nonce = uuid.uuid4().hex
        request = {
            "requested_at": utc(), "transition": name, "device": self.device_sn,
            "nonce": nonce,
            "ack_file": ack.relative_to(ROOT).as_posix(),
            "manual_action_evidence": (self.out / f"manual-user-action-{name}.json").relative_to(ROOT).as_posix(),
            "action": "Wait for the human user to change only this emulator network; keep the host online",
            "ack_schema": ["nonce", "transition", "device", "manual_action_evidence", "actual_method"],
            "ack_is_not_network_proof": True}
        write_json(self.out / f"transition-{name}-request.json", request)
        write_json(self.out / "transition-request.json", request)
        deadline = time.monotonic() + int(os.environ.get("VG_HOST_WAIT_SECONDS", "1800"))
        while time.monotonic() < deadline:
            if ack.exists():
                data = json.loads(ack.read_text(encoding="utf-8-sig"))
                self.assertEqual(data.get("nonce"), nonce)
                self.assertEqual(data.get("transition"), name)
                self.assertEqual(data.get("device"), self.device_sn)
                self.assertTrue(str(data.get("actual_method", "")).strip(), "Missing actual human network method")
                evidence = ROOT / data.get("manual_action_evidence", "")
                self.assertTrue(evidence.resolve().is_relative_to(ROOT) and evidence.is_file(), "Missing task-local manual action evidence JSON")
                write_json(self.e.folder / f"transition-{name}-observed.json", data)
                return
            time.sleep(.5)
        self.fail(f"Human network {name} acknowledgement absent; state is NOT a pass")

    def host_service_health(self, name):
        """Prove the controlled server remains alive on the still-online host."""
        start, at = len(self.probe.requests), utc()
        nonce = uuid.uuid4().hex
        path = "/__hcup_host_health__/" + nonce
        for method in ("HEAD", "GET"):
            connection = http.client.HTTPConnection("127.0.0.1", PORT, timeout=5)
            try:
                connection.request(method, path, headers={"X-VgSpec1-Test-Observer": "host-health"})
                response = connection.getresponse()
                self.assertEqual(response.status, 200)
                payload = response.read()
                if method == "GET":
                    self.assertIn(nonce.encode(), payload)
            finally:
                connection.close()
        requests = self.probe.window(start, self.case + "-" + name, at)
        self.assertEqual([r["method"] for r in requests], ["HEAD", "GET"])
        self.assertTrue(all(r["observer"] == "host-health" and r["path"] == path for r in requests))
        write_json(self.e.folder / f"{name}-host-health.json", {
            "at": utc(), "nonce": nonce, "path": path, "methods": ["HEAD", "GET"],
            "status": [r["status"] for r in requests], "excluded_from_guest_windows": True})

    def online_positive(self, name):
        with self.evidence_scope(name):
            ui0 = self.ui_state("before-positive")
            self.assertEqual(ui0["inputs"]["endpoint"], self.endpoint)
            if not hasattr(self, "initial_inputs"):
                self.initial_inputs = ui0["inputs"]
            self.assertEqual(ui0["inputs"], self.initial_inputs, "Actual network controls must keep all saved credentials/root unchanged")
            self.scroll_find("webdav_restore_button")
            d0 = self.e.db_snapshot("data-before")
            self.sentinel(d0)
            if not hasattr(self, "initial_tables"):
                self.initial_tables = d0["tables"]
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
            for action in ACTIONS:
                self.assertTrue(self.get(f"webdav_{action}_button").isEnabled())
            self.network_state("network-online")
            self.host_service_health("host-health")

    def resume_webdav_after_human(self):
        """The user may leave the system Settings app foreground after toggling."""
        self.driver.start_app(BUNDLE, "EntryAbility")
        if self.present("settings_entry_button") is not None:
            self.enter_webdav()
        elif self.present("settings_section_sync") is not None:
            self.driver.click(self.get("settings_section_sync"))
        elif not any(self.present(key) is not None for key in (
                "webdav_restore_button", "webdav_endpoint_input", "webdav_auto_sync_toggle")):
            self.e.screen("return-from-manual-action-unrecognized")
            self.fail("Could not safely return from user's Settings app to existing WebDAV context")

    def offline_connection_control(self):
        with self.evidence_scope("offline-connection-negative-control"):
            self.scroll_find("webdav_restore_button")
            d0 = self.e.db_snapshot("data-before")
            start, at = len(self.probe.requests), utc()
            previous_result = self.present("webdav_backup_result")
            result_before = previous_result.getText() if previous_result is not None else None
            self.driver.click(self.get("webdav_restore_button"))
            self.first_layer()
            self.assertEqual(len(self.probe.requests), start)
            self.driver.click(self.get("webdav_restore_confirm_continue"))
            deadline = time.monotonic() + 150  # Existing production outer timeout is120s.
            while time.monotonic() < deadline:
                if self.driver.find_component(BY.text("⚠️ 恢复确认")) is not None:
                    self.e.screen("negative-control-unexpected-online-preview")
                    self.probe.window(start, self.case, at)
                    self.fail("User's method did not isolate the configured NAT path: actual encrypted preview was reached")
                result_component = self.present("webdav_backup_result")
                observed_result = result_component.getText() if result_component is not None else ""
                if observed_result and observed_result != result_before and "正在处理" not in observed_result and self.get("webdav_restore_button").isEnabled():
                    break
                time.sleep(.4)
            self.assertTrue(self.get("webdav_restore_button").isEnabled(), "Offline continuation never returned to idle")
            self.assertIsNone(self.present("webdav_restore_confirm_dialog"))
            self.assertIsNone(self.driver.find_component(BY.text("⚠️ 恢复确认")))
            result_after = self.get("webdav_backup_result").getText()
            self.assertTrue(result_after and "正在处理" not in result_after)
            self.assertNotEqual(result_before, result_after, "No observable failed continuation result")
            self.assertTrue(result_after.startswith("⚠️"), "Expected explicit failure result")
            self.assertTrue(any(marker in result_after for marker in (
                "HEAD 0", "GET 0", "PUT 0", "网络", "Network", "network",
                "connect", "Connect", "unreachable", "timed out", "操作超时")),
                f"Result does not identify a transport/network failure: {result_after}")
            for action in ACTIONS:
                self.assertTrue(self.get(f"webdav_{action}_button").isEnabled(), f"Offline failure left {action} disabled")
            self.e.screen("offline-connection-failure")
            write_json(self.e.folder / "observed-failure-result.json", {"before": result_before, "after": result_after})
            self.assertEqual(self.probe.window(start, self.case, at), [], "User disconnect did not block actual NAT path")
            self.assertEqual(self.e.db_snapshot("data-after")["tables"], d0["tables"])
            self.network_state("network-offline-at-connection-failure")
            return d0

    def test_13_actual_offline_three_cancels_and_restore(self):
        """R27 human per-instance disconnection, actual controls before/after."""
        self.online_positive("online-before-disconnect")
        try:
            self.transition("disconnect")
            self.network_state("user-disconnected")
            self.host_service_health("host-alive-while-guest-disconnected")
            self.driver.stop_app(BUNDLE)
            self.driver.start_app(BUNDLE, "EntryAbility")
            self.enter_webdav()
            self.assertFalse(self.scroll_find("webdav_auto_sync_toggle", "DOWN").isChecked())
            ui0 = self.ui_state("after-manual-disconnect-cold-start")
            self.assertEqual(ui0["inputs"], self.initial_inputs)
            self.assertEqual(self.e.db_snapshot("data-after-manual-disconnect-cold-start")["tables"], self.initial_tables)
            baseline = self.offline_connection_control()
            self.host_service_health("host-alive-after-negative-control")
            # Terminate any underlying network Promise before product windows.
            self.driver.stop_app(BUNDLE)
            self.driver.start_app(BUNDLE, "EntryAbility")
            self.enter_webdav()
            self.assertFalse(self.scroll_find("webdav_auto_sync_toggle", "DOWN").isChecked())
            ui0 = self.ui_state("after-negative-control-restart")
            self.assertEqual(ui0["inputs"], self.initial_inputs)
            self.assertTrue(all(action["enabled"] for action in ui0["actions"].values()))
            self.assertEqual(self.e.db_snapshot("data-after-negative-control-restart")["tables"], baseline["tables"])
            for mode in ("button", "gesture", "outside"):
                with self.evidence_scope("offline-" + mode):
                    self.network_state("offline-before-action")
                    self.safe_cancel_scenario(mode, wait=True)
                    self.network_state("offline-after-action")
            self.host_service_health("host-alive-after-product-windows")
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
            "online_after": "HEAD/GET200", "network_restore": "observed", "device": self.device_sn,
            "system_state_interpretation": "Preserve raw interface/NetConn facts; coordinator reviews actual user method, no icon/ACK-only system offline claim"})
