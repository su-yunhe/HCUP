"""Explicitly selected positive control after a failed human network isolation.

This module is outside test_*.py discovery. A reachable server here proves the
restored route only; it cannot turn the earlier offline negative control green.
"""
from hypium_tests.evidence import utc, write_json
from hypium_tests.offline_confirmation import OfflineRestoreTests


class NetworkRestoreControlTests(OfflineRestoreTests):
    def test_18_manual_restore_actual_online_positive(self):
        """Same guest NAT, real encrypted GET, second cancel, full D0 and actions."""
        self.online_positive("online-after-manual-restore")
        write_json(self.e.folder / "restored-route-verdict.json", {
            "at": utc(),
            "device": self.device_sn,
            "endpoint": self.endpoint,
            "online_positive": "pass",
            "earlier_offline_negative_control": "unchanged failure; not overridden",
            "proof": "Actual HEAD and one encrypted GET 200; second confirmation canceled; all nine tables unchanged; all five actions enabled",
        })
