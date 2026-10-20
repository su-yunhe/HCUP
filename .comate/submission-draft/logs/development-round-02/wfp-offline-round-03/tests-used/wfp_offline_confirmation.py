"""Explicit supplementary test of actual per-copy outbound NAT isolation.

This is not discovered by test_*.py. The ordinary user must first launch the
reviewed helper as administrator; this module never launches or elevates it.
Guest NetConn may still report available. Actual same-path I/O decides isolation.
"""
import json
import os
from pathlib import Path
import sys
import shutil
import time
import traceback

from hypium_tests.evidence import BUNDLE, ROOT, Evidence, digest, source_fingerprint, utc, write_json
from hypium_tests.offline_confirmation import OfflineRestoreTests
from hypium_tests.wfp_controller import WfpLeaseController


class WfpOfflineRestoreTests(OfflineRestoreTests):
    @classmethod
    def setUpClass(cls):
        cls.wfp = None
        base_ready = False
        try:
            verification = json.loads(Path(os.environ["VG_VERIFICATION_MANIFEST"]).read_text(encoding="utf-8-sig"))
            if not verification.get("coordinator_frozen") or not verification.get("installed_at"):
                raise RuntimeError("Fresh frozen-HAP install required")
            if verification["device"] != cls.device_sn or cls.device_sn != "127.0.0.1:11237":
                raise RuntimeError("Dedicated device mismatch")
            if verification["source"] != source_fingerprint():
                raise RuntimeError("Production input fingerprint changed")
            if verification["hap_sha256"] != digest((ROOT / "entry/build/default/outputs/default/entry-default-unsigned.hap").read_bytes()):
                raise RuntimeError("Freshly installed HAP does not match build")
            cls.out = ROOT / verification["evidence_dir"]
            manifest = json.loads(Path(os.environ["VG_WFP_HELPER_MANIFEST"]).read_text(encoding="utf-8-sig"))
            cls.wfp = WfpLeaseController(os.environ["VG_WFP_RUNTIME"], os.environ["VG_WFP_NONCE"], manifest, cls.out)
            cls.wfp.start()
            cls.wfp.wait_user_helper(int(os.environ.get("VG_WFP_START_WAIT_SECONDS", "1800")))
            cls.hdc_preflight()
            # A fresh UiDriver is first created only after transport reconnect.
            OfflineRestoreTests.setUpClass.__func__(cls)
            base_ready = True
        except BaseException:
            original = sys.exc_info()
            if hasattr(cls, "out"):
                write_json(cls.out / "wfp-setup-error.json", {"at": utc(), "type": original[0].__name__, "message": str(original[1])})
            try:
                if cls.wfp is not None:
                    try:
                        if cls.wfp.started and cls.wfp.helper_pid is not None:
                            cls.wfp.unblock()
                    finally:
                        cls.wfp.close()
            except BaseException as cleanup_error:
                write_json(cls.out / "wfp-setup-recovery-error.json", {"at": utc(), "message": repr(cleanup_error)})
            finally:
                if base_ready:
                    OfflineRestoreTests.tearDownClass.__func__(cls)
                elif hasattr(cls, "probe"):
                    cls.probe.stop()
            raise original[1].with_traceback(original[2])

    @classmethod
    def hdc_preflight(cls):
        evidence = Evidence(cls.out / "wfp-hdc-preflight", cls.device_sn)
        hdc = shutil.which("hdc") or "hdc"
        help_result = evidence.command([hdc, "-h"])
        if "tconn key [-remove]" not in help_result["stdout"] + help_result["stderr"]:
            raise RuntimeError("Installed HDC did not document the target-only reconnect command")
        primary_error = None
        try:
            cls.wfp.block()
            cls.wfp.require_blocked(evidence, "before-target-reconnect")
            evidence.command([hdc, "tconn", cls.device_sn, "-remove"])
            evidence.command([hdc, "tconn", cls.device_sn])
            deadline = time.monotonic() + 20
            connected = False
            while time.monotonic() < deadline:
                result = evidence.hdc("shell", "id", check=False)
                if result["exit_code"] == 0 and "uid=2000" in result["stdout"]:
                    connected = True
                    break
                time.sleep(.5)
            if not connected:
                raise AssertionError("Dedicated HDC transport did not reconnect under active filters")
            evidence.screen("target-reconnected-under-active-wfp")
            cls.wfp.require_blocked(evidence, "after-target-reconnect")
        except BaseException:
            primary_error = sys.exc_info()
            write_json(evidence.folder / "preflight-primary-error.json", {
                "at": utc(), "type": primary_error[0].__name__,
                "message": str(primary_error[1]),
                "traceback": "".join(traceback.format_exception(*primary_error))})
            raise
        finally:
            try:
                state = cls.wfp.unblock()
                write_json(evidence.folder / "preflight-unblocked.json", {"at": utc(), "status": state})
            except BaseException:
                recovery_error = sys.exc_info()
                write_json(evidence.folder / "preflight-recovery-error.json", {
                    "at": utc(), "type": recovery_error[0].__name__,
                    "message": str(recovery_error[1]),
                    "traceback": "".join(traceback.format_exception(*recovery_error)),
                    "primary_error_preserved": primary_error is not None})
                if primary_error is None:
                    raise
        write_json(evidence.folder / "preflight-verdict.json", {"at": utc(), "hdc_reconnect": "pass", "device": cls.device_sn, "global_server_kill_used": False, "UiDriver_initialized_during_preflight": False})

    @classmethod
    def tearDownClass(cls):
        try:
            if cls.wfp is not None:
                cls.wfp.close()
        finally:
            OfflineRestoreTests.tearDownClass.__func__(cls)

    def transition(self, name):
        if name == "disconnect":
            state = self.wfp.block()
        elif name == "restore":
            state = self.wfp.unblock()
        else:
            raise ValueError(name)
        write_json(self.e.folder / ("wfp-transition-" + name + ".json"), {"at": utc(), "status": state})

    def cold_start_and_compare(self, name, expected_tables):
        self.driver.stop_app(BUNDLE)
        self.driver.start_app(BUNDLE, "EntryAbility")
        self.enter_webdav()
        self.assertFalse(self.scroll_find("webdav_auto_sync_toggle", "DOWN").isChecked())
        ui = self.ui_state(name)
        self.assertEqual(ui["inputs"], self.initial_inputs)
        self.assertTrue(all(action["enabled"] for action in ui["actions"].values()))
        self.assertEqual(self.e.db_snapshot(name + "-data")["tables"], expected_tables)

    def test_19_wfp_actual_outbound_isolation_three_cancels(self):
        """Same NAT positive/failed negative/three cancels/restored positive."""
        self.online_positive("online-before-wfp")
        primary_error, restoration_error = None, None
        block_attempted = False
        try:
            block_attempted = True
            self.transition("disconnect")
            self.wfp.require_blocked(self.e, "before-negative-control")
            self.network_state("wfp-blocked-guest-system-facts")
            self.host_service_health("host-alive-while-wfp-blocked")
            self.cold_start_and_compare("blocked-cold-start", self.initial_tables)
            baseline = self.offline_connection_control()
            self.wfp.require_blocked(self.e, "after-negative-control")
            self.host_service_health("host-alive-after-wfp-negative-control")
            self.cold_start_and_compare("after-negative-control-restart", baseline["tables"])
            for mode in ("button", "gesture", "outside"):
                with self.evidence_scope("wfp-offline-" + mode):
                    self.wfp.require_blocked(self.e, "before-product-window")
                    self.network_state("network-before-product-window")
                    self.safe_cancel_scenario(mode, wait=True)
                    self.network_state("network-after-product-window")
                    self.wfp.require_blocked(self.e, "after-product-window")
            self.host_service_health("host-alive-after-wfp-product-windows")
            self.wfp.require_blocked(self.e, "end-of-all-product-windows")
            self.wfp.expire_lease_after_product_windows(self.e)
        except BaseException:
            primary_error = sys.exc_info()
            write_json(self.e.folder / "primary-isolation-error.json", {"at": utc(), "type": primary_error[0].__name__, "message": str(primary_error[1])})
        finally:
            if block_attempted:
                # Each recovery stage is attempted independently. A failed
                # unblock acknowledgment must not skip actual G4 observation.
                try:
                    # Existing production timeout does not cancel its Promise;
                    # stop only this app before unblocking to prevent late I/O.
                    self.driver.stop_app(BUNDLE)
                except BaseException:
                    restoration_error = sys.exc_info()
                    write_json(self.e.folder / "recovery-stop-error.json", {"at": utc(), "message": str(restoration_error[1])})
                try:
                    self.transition("restore")
                except BaseException:
                    if restoration_error is None:
                        restoration_error = sys.exc_info()
                    write_json(self.e.folder / "recovery-unblock-error.json", {"at": utc(), "message": repr(sys.exc_info()[1])})
                try:
                    self.driver.start_app(BUNDLE, "EntryAbility")
                    self.enter_webdav()
                    # Keep recovery proof even when G2/G3 failed. It cannot
                    # erase the primary failure or turn it into a pass.
                    self.online_positive("online-after-wfp-restored")
                except BaseException:
                    restoration_error = sys.exc_info()
                    write_json(self.e.folder / "restoration-error.json", {"at": utc(), "type": restoration_error[0].__name__, "message": str(restoration_error[1])})
        if primary_error is not None:
            raise primary_error[1].with_traceback(primary_error[2])
        if restoration_error is not None:
            raise restoration_error[1].with_traceback(restoration_error[2])
        self.wfp.assert_healthy()
        process_evidence = self.e.folder / "helper-process-after-lease-cleanup.json"
        process_command = ". 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'\n" + \
            "$record = Get-CimInstance Win32_Process -Filter 'ProcessId=" + str(int(self.wfp.helper_pid)) + "'\n" + \
            "[ordered]@{capturedAtUtc=(Get-Date).ToUniversalTime().ToString('o');helperPid=" + str(int(self.wfp.helper_pid)) + \
            ";present=[bool]$record} | ConvertTo-Json | Set-Content -Encoding utf8 -LiteralPath '" + str(process_evidence).replace("'", "''") + "'"
        self.e.command(["powershell", "-NoProfile", "-Command", process_command])
        self.assertFalse(json.loads(process_evidence.read_text(encoding="utf-8-sig"))["present"], "Helper did not exit after intentional lease expiry")
        write_json(self.e.folder / "wfp-transport-isolation-verdict.json", {
            "at": utc(), "device": self.device_sn, "same_endpoint": self.endpoint,
            "actual_transport_isolation": "pass", "three_cancels": "pass",
            "before_and_restored_positive": "real HEAD/GET200 and second confirmation cancel",
            "negative_control": "explicit network failure, all five actions idle, zero arrivals at live server",
            "continuous_guard": "nonce/sequence/lease/target/session/filter identity checked throughout",
            "post_product_failure_injection": "intentional heartbeat stop; controller_lease_expired and true observer NOT_FOUND queries; helper process gone",
            "guest_system_offline_claim": False,
            "boundary": "Per-program-copy outbound WFP isolation; preserve actual guest NetConn/Ethernet values",
        })
