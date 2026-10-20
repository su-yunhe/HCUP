"""Unprivileged, nonce-bound controller for the separately user-started helper.

No serve/process launch/UAC/WFP API calls occur here. File requests are only
used by an explicitly approved runner after the user starts the reviewed helper.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import threading
import time

from hypium_tests.evidence import ROOT, utc, write_json

LAYERS = {"c38d57d1-05a7-4c33-904f-7fbceee60e82", "4a72393b-319f-44bc-84c3-ba54dcb3b6b4"}
TARGET_PATH = Path("D:/HarmonyDev/vg-spec1-isolated-emulator61/Emulator.exe")


def instant(value):
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def normalized_path(value):
    return str(Path(value).resolve()).replace("\\", "/").casefold()


class WfpLeaseController:
    """Three-second lease renewal and continuous sticky isolation audit."""

    def __init__(self, runtime, nonce, manifest, out):
        if os.environ.get("VG_WFP_EXECUTION_APPROVED") != "1":
            raise RuntimeError("Coordinator execution approval required; helper is never auto-launched")
        self.runtime, self.out = Path(runtime).resolve(), Path(out).resolve()
        if not self.runtime.is_relative_to(self.out) or not self.out.is_relative_to(ROOT):
            raise RuntimeError("Runtime must be inside this task's fresh run directory")
        if len(nonce) != 32 or any(c not in "0123456789abcdef" for c in nonce):
            raise RuntimeError("Expected exact 32-lowercase-hex run nonce")
        self.nonce, self.expected = nonce, manifest
        self.target = manifest["target"]
        if normalized_path(self.target["path"]) != normalized_path(TARGET_PATH):
            raise RuntimeError("Only dedicated emulator copy is supported")
        if self.target["instance"] != "VgSpec1ManualOffline" or int(self.target["hdcPort"]) != 11237:
            raise RuntimeError("Wrong dedicated instance/port")
        if not Path(self.target["instanceRoot"]).resolve().is_relative_to(ROOT / "logs"):
            raise RuntimeError("Instance root must remain within this task logs")
        self.helper_exe = Path(manifest["helperExe"]).resolve()
        if not self.helper_exe.is_relative_to(ROOT):
            raise RuntimeError("Helper executable must be task-local")
        if hashlib.sha256(self.helper_exe.read_bytes()).hexdigest() != manifest["helperSha256"].lower():
            raise RuntimeError("Reviewed helper executable fingerprint mismatch")
        for source in manifest["sourceFiles"]:
            if hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() != source["sha256"]:
                raise RuntimeError("Reviewed helper support/source fingerprint mismatch: " + source["path"])
        self.lock = threading.RLock()
        self.stopped = threading.Event()
        self.operation, self.sequence = "unblock", 0
        self.failure, self.last_status = None, None
        self.helper_pid, self.block_ids, self.block_session = None, None, None
        self.block_confirmed = False
        self.last_accepted = 0
        self.last_status_bytes = None
        self.requests = {}
        self.started = False
        self.heartbeat_paused = threading.Event()
        self.expected_expiry = False
        self.expiry_confirmed = False
        self.expiry_sequence = None
        self.expiry_not_before = None
        self.block_sublayer = None

    def append(self, name, value):
        with self.lock:
            with (self.out / name).open("a", encoding="utf8") as stream:
                stream.write(json.dumps(value, ensure_ascii=False) + "\n")

    def issue(self, operation=None):
        with self.lock:
            if self.helper_pid is None:
                raise RuntimeError("No fresh user-started helper has been observed; no live request is allowed")
            if operation is not None:
                if operation not in ("block", "unblock", "exit"):
                    raise ValueError(operation)
                self.operation = operation
            self.sequence += 1
            now = datetime.now(timezone.utc)
            request = {"nonce": self.nonce, "sequence": self.sequence,
                       "operation": self.operation,
                       "createdUtc": now.isoformat().replace("+00:00", "Z"),
                       "expiresUtc": (now + timedelta(seconds=10)).isoformat().replace("+00:00", "Z")}
            encoded = json.dumps(request).encode("utf8")
            if len(encoded) > 4096:
                raise RuntimeError("Request exceeded helper contract")
            temporary = self.runtime / ("request-" + self.nonce + ".tmp")
            temporary.write_bytes(encoded)
            os.replace(temporary, self.runtime / "request.json")
            self.requests[self.sequence] = request
            self.append("wfp-controller-requests.jsonl", {"written_at": utc(), **request})
            return self.sequence

    def fail_sticky(self, error):
        with self.lock:
            if self.failure is None:
                self.failure = repr(error)
                self.append("wfp-controller-errors.jsonl", {"at": utc(), "error": self.failure})
            # Cleanup can never erase the original failure.
            if self.operation == "block":
                self.issue("unblock")

    def assert_healthy(self):
        if self.failure:
            raise AssertionError("WFP isolation evidence invalid: " + self.failure)

    def validate_status(self, state):
        now = datetime.now(timezone.utc)
        if state.get("nonce") != self.nonce:
            raise AssertionError("Wrong helper nonce")
        age = (now - instant(state["timestampUtc"])).total_seconds()
        if not -2 <= age <= 3:
            raise AssertionError("Stale/future helper status: " + str(age))
        pid = int(state["helperPid"])
        if self.helper_pid is None:
            self.helper_pid = pid
        if self.helper_pid != pid:
            raise AssertionError("Helper process changed mid-run")
        target = state["target"]
        for key in ("path", "instanceRoot"):
            if normalized_path(target[key]) != normalized_path(self.target[key]):
                raise AssertionError("Target path/root changed: " + key)
        for key in ("pid", "hdcPort"):
            if int(target[key]) != int(self.target[key]):
                raise AssertionError("Target identity changed: " + key)
        if target["instance"] != self.target["instance"] or target["sha256"].lower() != self.target["sha256"].lower():
            raise AssertionError("Target instance/hash changed")
        if instant(target["startTimeUtc"]) != instant(self.target["startTimeUtc"]):
            raise AssertionError("Target start time changed")
        if target.get("guardOk") is not True:
            raise AssertionError("Helper target guard is false")
        guard_age = (now - instant(target["lastGuardUtc"])).total_seconds()
        if not -2 <= guard_age <= 3:
            raise AssertionError("Target guard was not refreshed")
        accepted = int(state["lastAcceptedSequence"])
        if accepted < self.last_accepted or accepted > self.sequence:
            raise AssertionError("Accepted sequence regressed or has unknown origin")
        if accepted and accepted not in self.requests:
            raise AssertionError("Accepted request was not emitted by this runner")
        self.last_accepted = accepted
        planned_expiry_window = self.expected_expiry and now >= self.expiry_not_before
        if accepted and instant(state["requestExpiresUtc"]) <= now and not planned_expiry_window:
            raise AssertionError("Accepted request lease expired")
        if instant(state["totalDeadlineUtc"]) <= now:
            raise AssertionError("Helper absolute lifetime expired")
        expected_exit = self.operation == "exit" and state["state"] == "EXITED_UNBLOCKED" and state.get("terminationReason") == "exit_request"
        expected_lease_end = bool(planned_expiry_window and state["state"] == "ERROR_UNBLOCKED" and state.get("terminationReason") == "controller_lease_expired" and accepted == self.expiry_sequence)
        if state.get("cleanupUnconfirmed") is not False:
            raise AssertionError("Helper cleanup is absent or unconfirmed")
        if (str(state["state"]).startswith("ERROR") and not expected_lease_end) or (state.get("terminationReason") and not (expected_exit or expected_lease_end)):
            raise AssertionError("Helper terminated/failed: " + str(state))
        if (expected_exit or expected_lease_end) and (state.get("active") is not False or state.get("nativeEngineOpen") is not False or state.get("filters")):
            raise AssertionError("Exit did not release dynamic objects")
        if self.operation == "block" and self.block_confirmed and not expected_lease_end:
            self.validate_block(state)

    def validate_block(self, state):
        if state.get("state") != "BLOCKED" or state.get("active") is not True or state.get("nativeEngineOpen") is not True:
            raise AssertionError("Isolation was not continuously active")
        if instant(state["blockDeadlineUtc"]) <= datetime.now(timezone.utc):
            raise AssertionError("Absolute block deadline expired")
        filters = state["filters"]
        if len(filters) != 2 or {str(f["layerGuid"]).lower().strip("{}") for f in filters} != LAYERS:
            raise AssertionError("Expected exact V4/V6 AUTH_CONNECT filters")
        if not all(f.get("verified") is True and int(f["id"]) > 0 for f in filters):
            raise AssertionError("Native filter fields were not verified")
        identities = sorted((int(f["id"]), str(f["key"]).lower()) for f in filters)
        if self.block_ids is None:
            self.block_ids, self.block_session = identities, state["sessionGuid"]
            self.block_sublayer = state["subLayerGuid"]
        if identities != self.block_ids or state["sessionGuid"] != self.block_session:
            raise AssertionError("Filters/session changed during blocked interval")
        if state["subLayerGuid"] != self.block_sublayer:
            raise AssertionError("Owned sublayer changed during blocked interval")

    def read_status(self):
        with self.lock:
            # Serialize read and validation with the foreground phase guards:
            # an older concurrent read must not look like a sequence rollback.
            encoded = (self.runtime / "status.json").read_bytes()
            if len(encoded) > 65536:
                raise AssertionError("Unexpected helper status size")
            state = json.loads(encoded.decode("utf-8-sig"))
            self.validate_status(state)
            if encoded != self.last_status_bytes:
                self.append("wfp-controller-status.jsonl", {"observed_at": utc(), "expected_operation": self.operation, "status": state})
                self.last_status_bytes = encoded
            self.last_status = state
            return state

    def start(self):
        self.runtime.mkdir(parents=True, exist_ok=True)
        if (self.runtime / "request.json").exists() or (self.runtime / "status.json").exists():
            raise RuntimeError("Fresh runtime required; stale request/status cannot be reused")
        self.started = True
        write_json(self.out / "wfp-controller-ready.json", {
            "at": utc(), "runtime": self.runtime.relative_to(ROOT).as_posix(), "nonce": self.nonce,
            "helper_auto_started": False, "operation": "watch_only_no_request", "controller_pid": os.getpid(),
            "heartbeat_seconds": 3, "lease_seconds": 10, "monitor_seconds": .2})

        def heartbeat():
            while not self.stopped.wait(3):
                try:
                    with self.lock:
                        if self.heartbeat_paused.is_set():
                            return
                        self.issue()
                except BaseException as error:
                    self.fail_sticky(error)

        def monitor():
            seen = False
            while not self.stopped.wait(.2):
                if self.expiry_confirmed:
                    return
                try:
                    self.read_status()
                    seen = True
                except FileNotFoundError as error:
                    if seen:
                        self.fail_sticky(error)
                except BaseException as error:
                    self.fail_sticky(error)

        self.heartbeat_target = heartbeat
        self.threads = [threading.Thread(target=monitor, daemon=True)]
        for thread in self.threads:
            thread.start()

    def await_state(self, blocked, minimum_sequence, timeout):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.assert_healthy()
            state = self.last_status
            if state and int(state["lastAcceptedSequence"]) >= minimum_sequence:
                if blocked and state["state"] == "BLOCKED" and state["active"] is True:
                    with self.lock:
                        self.validate_block(state)
                        self.block_confirmed = True
                    return state
                if not blocked and state["state"] == "IDLE_UNBLOCKED" and state["active"] is False and state["nativeEngineOpen"] is False and not state["filters"]:
                    return state
            time.sleep(.1)
        raise AssertionError("Timed out waiting for actual helper state; no pass is inferred")

    def wait_user_helper(self, timeout=1800):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.assert_healthy()
            state = self.last_status
            if state and state["state"] == "IDLE_UNBLOCKED" and state["active"] is False and state["nativeEngineOpen"] is False and not state["filters"] and int(state["lastAcceptedSequence"]) == 0:
                sequence = self.issue("unblock")
                thread = threading.Thread(target=self.heartbeat_target, daemon=True)
                self.threads.append(thread)
                thread.start()
                write_json(self.out / "wfp-user-helper-observed.json", {"at": utc(), "status": state, "first_sequence": sequence, "first_request_follows_fresh_user_started_status": True})
                return self.await_state(False, sequence, 15)
            time.sleep(.1)
        raise AssertionError("User-started helper status absent; no live request was emitted")

    def block(self):
        self.assert_healthy()
        return self.await_state(True, self.issue("block"), 15)

    def require_blocked(self, evidence, name):
        self.assert_healthy()
        state = self.read_status()
        self.validate_block(state)
        write_json(evidence.folder / (name + "-wfp-guard.json"), {"at": utc(), "status": state})
        return state

    def unblock(self):
        if self.expiry_confirmed:
            return self.last_status
        # Recovery requests must still be written after a sticky audit failure.
        old_ids, old_sublayer = self.block_ids, self.block_sublayer
        sequence = self.issue("unblock")
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            state = self.last_status
            if state and int(state["lastAcceptedSequence"]) >= sequence and state.get("active") is False and state.get("nativeEngineOpen") is False and not state.get("filters"):
                if old_ids:
                    self.verify_cleanup(old_ids, old_sublayer, "unblock-" + str(sequence))
                self.block_confirmed = False
                self.block_ids, self.block_session = None, None
                self.block_sublayer = None
                return state
            time.sleep(.1)
        raise AssertionError("Helper did not confirm released dynamic session; inspect independent recovery evidence")

    def verify_cleanup(self, identities, sublayer, label):
        """Read native observer results; Close success alone never suffices."""
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            lines = (self.runtime / "helper.jsonl").read_text(encoding="utf-8-sig").splitlines()
            events = []
            for index, line in enumerate(lines):
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    if index == len(lines) - 1:
                        break  # A final append can still be in progress.
                    raise
                if event.get("nonce") != self.nonce:
                    raise AssertionError("Mixed helper nonce in cleanup log")
                events.append(event)
            for index in range(len(events) - 1, -1, -1):
                event = events[index]
                if event.get("event") != "cleanup_verification":
                    continue
                got = sorted((int(f["id"]), str(f["key"]).lower()) for f in event["filters"])
                if got != identities or event["subLayerGuid"] != sublayer:
                    continue
                if not (event["success"] is True and event["observerClosed"] is True and event["readOnlyTransaction"] is True):
                    raise AssertionError("Fresh native observer did not confirm cleanup")
                start = next((j for j in range(index - 1, -1, -1) if events[j].get("event") == "session_closed"), None)
                if start is None:
                    raise AssertionError("Observer query lacks preceding dynamic session Close")
                segment = events[start:index + 1]
                if segment[0].get("returnCode") != 0 or segment[0].get("verificationPending") is not True:
                    raise AssertionError("Dynamic Close did not precede observer verification")
                queries = [r for r in segment if r.get("event") == "cleanup_filter_query"]
                if sorted((int(r["filter"]["id"]), str(r["filter"]["key"]).lower()) for r in queries) != identities:
                    raise AssertionError("Observer did not query both exact historical filter IDs/keys")
                if not all(r["returnCode"] == 2150760451 and r["expectedReturnCode"] == 2150760451 and r["removed"] is True for r in queries):
                    raise AssertionError("Filter query did not return true FILTER_NOT_FOUND")
                subqueries = [r for r in segment if r.get("event") == "cleanup_sublayer_query"]
                if len(subqueries) != 1 or subqueries[0]["subLayerGuid"] != sublayer or subqueries[0]["returnCode"] != 2150760455 or subqueries[0]["removed"] is not True:
                    raise AssertionError("Owned sublayer query did not return true SUBLAYER_NOT_FOUND")
                calls = [r for r in segment if r.get("event") == "cleanup_observer_call"]
                expected = {"FwpmEngineOpen0", "FwpmTransactionBegin0", "FwpmTransactionAbort0", "FwpmEngineClose0"}
                if len(calls) != 4 or {r["function"] for r in calls} != expected or not all(r["returnCode"] == 0 for r in calls):
                    raise AssertionError("Independent read-only observer lifecycle failed")
                if next(r for r in calls if r["function"] == "FwpmTransactionBegin0").get("flags") != 1:
                    raise AssertionError("Observer transaction was not READ_ONLY")
                write_json(self.out / ("wfp-cleanup-proof-" + label + ".json"), {"at": utc(), "historical_filter_identities": identities, "subLayerGuid": sublayer, "native_event_segment": segment, "actual_not_found_queries": True})
                return event
            time.sleep(.1)
        raise AssertionError("No matching native observer cleanup evidence")

    def expire_lease_after_product_windows(self, evidence):
        """Bounded failure injection, only after every product assertion passed."""
        self.require_blocked(evidence, "before-intentional-lease-expiry")
        with self.lock:
            self.heartbeat_paused.set()
            self.expected_expiry = True
            self.expiry_sequence = self.sequence
            self.expiry_not_before = instant(self.requests[self.sequence]["expiresUtc"])
            if instant(self.last_status["blockDeadlineUtc"]) <= self.expiry_not_before + timedelta(seconds=5):
                raise AssertionError("Insufficient absolute block time for bounded lease-expiry cleanup test")
            identities, sublayer = self.block_ids, self.block_sublayer
            write_json(evidence.folder / "intentional-lease-expiry.json", {"at": utc(), "last_emitted_sequence": self.sequence, "last_request": self.requests[self.sequence], "product_windows_already_complete": True, "expected_reason": "controller_lease_expired", "not_an_unexpected_product_window_unblock": True})
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            self.assert_healthy()
            state = self.last_status
            if state and state["state"] == "ERROR_UNBLOCKED" and state["terminationReason"] == "controller_lease_expired" and int(state["lastAcceptedSequence"]) == self.expiry_sequence:
                self.verify_cleanup(identities, sublayer, "intentional-lease-expiry")
                self.expiry_confirmed = True
                write_json(evidence.folder / "lease-expiry-cleanup-confirmed.json", {"at": utc(), "status": state, "actual_observer_queries_verified": True})
                return state
            time.sleep(.1)
        raise AssertionError("Expected lease-expiry cleanup was not confirmed")

    def close(self):
        if not self.started:
            return
        exited = self.helper_pid is None or self.expiry_confirmed
        try:
            sequence = self.issue("exit") if self.helper_pid is not None and not self.expiry_confirmed else 0
            deadline = time.monotonic() + 15
            while not exited and time.monotonic() < deadline:
                state = self.last_status
                exited = bool(state and int(state["lastAcceptedSequence"]) >= sequence and state["state"] == "EXITED_UNBLOCKED" and state["active"] is False and state["nativeEngineOpen"] is False and not state["filters"])
                if not exited:
                    time.sleep(.1)
        finally:
            self.stopped.set()
            for thread in getattr(self, "threads", []):
                thread.join(timeout=4)
            write_json(self.out / "wfp-controller-final.json", {"at": utc(), "sticky_failure": self.failure, "last_status": self.last_status, "last_emitted_sequence": self.sequence, "exit_and_dynamic_release_confirmed": exited, "intentional_lease_expiry_observer_confirmed": self.expiry_confirmed})
        if not exited:
            raise AssertionError("Helper exit/dynamic cleanup was not confirmed")
