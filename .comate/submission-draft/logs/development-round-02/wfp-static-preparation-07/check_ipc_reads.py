"""Injected controller IPC checks; no helper/device/network/WFP is used."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import errno
import hashlib
import json
from pathlib import Path
import sys
import threading
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from hypium_tests.wfp_controller import WfpLeaseController

OUT = Path(__file__).parent
recorded = json.loads((ROOT / "logs/development-round-02/wfp-offline-round-02/wfp-user-helper-observed.json").read_text(encoding="utf8"))["status"]
recorded_blocked = json.loads((ROOT / "logs/development-round-02/wfp-offline-round-02/wfp-hdc-preflight/before-target-reconnect-wfp-guard.json").read_text(encoding="utf8"))["status"]
results = []


def permission_error(code):
    error = PermissionError(errno.EACCES, "synthetic read denial", "synthetic/status.json")
    if code is not None:
        error.winerror = code
    return error


def check(name, denial_count, code=32, mutate=None, expected_error=None, invalid_json=False, read_sleep=0, blocked=False, preexisting_failure=False):
    state = deepcopy(recorded_blocked if blocked else recorded)
    now = datetime.now(timezone.utc)
    state.update(timestampUtc=now.isoformat(), requestExpiresUtc=(now + timedelta(seconds=10)).isoformat(),
                 totalDeadlineUtc=(now + timedelta(seconds=30)).isoformat())
    state["target"]["lastGuardUtc"] = now.isoformat()
    if blocked:
        state["blockDeadlineUtc"] = (now + timedelta(seconds=20)).isoformat()
    controller = WfpLeaseController.__new__(WfpLeaseController)
    controller.runtime, controller.out = OUT / "synthetic-runtime-not-created", OUT
    controller.lock = threading.RLock()
    controller.operation, controller.sequence = ("block" if blocked else "unblock"), int(state["lastAcceptedSequence"])
    controller.failure, controller.last_status, controller.last_status_bytes = ("preexisting sticky failure" if preexisting_failure else None), None, None
    controller.helper_pid, controller.last_accepted = None, 0
    controller.target, controller.nonce = deepcopy(state["target"]), state["nonce"]
    controller.requests, controller.expected_expiry = ({controller.sequence: {}} if controller.sequence else {}), False
    controller.expiry_not_before, controller.block_confirmed = None, blocked
    controller.block_ids = sorted((int(f["id"]), str(f["key"]).lower()) for f in state["filters"])
    controller.block_session, controller.block_sublayer = state["sessionGuid"], state["subLayerGuid"]
    diagnostics = []
    controller.append = lambda path, record: diagnostics.append({"file": path, **record})
    controller.issue = lambda *args: None  # Synthetic cleanup cannot write live files.
    if mutate:
        mutate(state)
    encoded = b"{" if invalid_json else json.dumps(state).encode("utf8")
    calls = 0

    def injected_read():
        nonlocal calls
        calls += 1
        if denial_count is None or calls <= denial_count:
            raise permission_error(code)
        if read_sleep:
            time.sleep(read_sleep)
        return encoded

    started, error = time.monotonic(), None
    with patch.object(Path, "read_bytes", side_effect=injected_read):
        try:
            controller.read_status()
        except BaseException as caught:
            error = caught
            controller.fail_sticky(caught, "injected.monitor.read_status")
    elapsed = time.monotonic() - started
    assert (type(error) if error else None) is expected_error, (name, repr(error))
    if expected_error is None:
        assert controller.failure == ("preexisting sticky failure" if preexisting_failure else None) and controller.last_status == state
        if preexisting_failure:
            try:
                controller.assert_healthy()
            except AssertionError:
                pass
            else:
                raise AssertionError("Successful read cleared a prior sticky failure")
    else:
        assert controller.failure is not None
        try:
            controller.assert_healthy()
        except AssertionError:
            pass
        else:
            raise AssertionError("Sticky failure was cleared")
    if denial_count is None:
        assert calls > 1 and .40 <= elapsed <= .5, elapsed
    if code not in (5, 32, 33) or invalid_json:
        assert calls == 1, calls
    for diagnostic in diagnostics:
        if "error" in diagnostic:
            assert {"operation", "context", "exception_type", "message", "error", "errno", "winerror", "filename", "filename2", "traceback"}.issubset(diagnostic)
            assert diagnostic["operation"] in ("unblock", "block") and diagnostic["traceback"]
    (OUT / (name + "-diagnostics.json")).write_text(json.dumps(diagnostics, indent=2), encoding="utf8")
    results.append({"name": name, "result": "pass", "read_attempts": calls,
                    "elapsed_seconds": elapsed, "error": type(error).__name__ if error else None,
                    "diagnostics": name + "-diagnostics.json"})


check("one_winerror32_then_fresh", 1)
check("one_winerror5_then_fresh", 1, code=5)
check("one_winerror33_then_fresh", 1, code=33)
check("continuous_winerror32", None, expected_error=PermissionError)
check("stale_after_retry", 1, mutate=lambda s: s.update(timestampUtc=(datetime.now(timezone.utc) - timedelta(seconds=4)).isoformat()), expected_error=AssertionError)
check("identity_after_retry", 1, mutate=lambda s: s["target"].update(pid=1), expected_error=AssertionError)
check("wrong_nonce_after_retry", 1, mutate=lambda s: s.update(nonce="0" * 32), expected_error=AssertionError)
check("unknown_winerror_no_retry", 1, code=1314, expected_error=PermissionError)
check("no_winerror_no_retry", 1, code=None, expected_error=PermissionError)
check("json_error_no_retry", 0, expected_error=json.JSONDecodeError, invalid_json=True)
check("overbudget_successful_read_rejected", 0, expected_error=TimeoutError, read_sleep=.51)
check("retry_then_overbudget_read_rejected", 1, expected_error=TimeoutError, read_sleep=.51)
check("fresh_blocked_after_retry", 1, blocked=True)
check("lease_expired_after_retry", 1, blocked=True, mutate=lambda s: s.update(requestExpiresUtc=(datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat()), expected_error=AssertionError)
check("blocked_state_changed_after_retry", 1, blocked=True, mutate=lambda s: s.update(state="IDLE_UNBLOCKED", active=False, nativeEngineOpen=False, filters=[]), expected_error=AssertionError)
check("filter_id_changed_after_retry", 1, blocked=True, mutate=lambda s: s["filters"][0].update(id=str(int(s["filters"][0]["id"]) + 1)), expected_error=AssertionError)
check("session_changed_after_retry", 1, blocked=True, mutate=lambda s: s.update(sessionGuid="0" * 32), expected_error=AssertionError)
check("sublayer_changed_after_retry", 1, blocked=True, mutate=lambda s: s.update(subLayerGuid="0" * 32), expected_error=AssertionError)
check("successful_read_does_not_clear_sticky", 1, preexisting_failure=True)

writer = WfpLeaseController.__new__(WfpLeaseController)
writer.lock, writer.helper_pid, writer.operation, writer.sequence = threading.RLock(), 1, "unblock", 0
writer.nonce, writer.runtime, writer.requests = "0" * 32, OUT / "synthetic-runtime-not-created", {}
write_attempts = 0


def denied_write(*args, **kwargs):
    global write_attempts
    write_attempts += 1
    raise permission_error(32)


with patch.object(Path, "write_bytes", side_effect=denied_write), patch.object(Path, "read_bytes", side_effect=AssertionError("Writer must not use read retry")):
    try:
        writer.issue("unblock")
    except PermissionError:
        assert write_attempts == 1
    else:
        raise AssertionError("Denied writer was accepted")
results.append({"name": "request_writer_no_retry", "result": "pass", "write_attempts": write_attempts, "live_request_written": False})
summary = {"classification": "injected_local_ipc_checks_only", "product_requirement_evidence": False,
           "native_or_device_calls": 0, "sourceSha256": hashlib.sha256((ROOT / "hypium_tests/wfp_controller.py").read_bytes()).hexdigest(),
           "cases": results, "pass": len(results), "fail": 0}
(OUT / "ipc-check-result.json").write_text(json.dumps(summary, indent=2), encoding="utf8")
print(json.dumps(summary))
