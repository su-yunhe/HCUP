"""Actual local-file IPC experiment, with no helper/WFP/network/device calls."""
import ctypes
from ctypes import wintypes as wt
import json
from pathlib import Path
import sys
import threading
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from hypium_tests.wfp_controller import WfpLeaseController

OUT = Path(__file__).parent
FIXTURE = OUT / "local-native-fixture"
FIXTURE.mkdir(exist_ok=True)
kernel = ctypes.WinDLL("kernel32", use_last_error=True)
kernel.CreateFileW.argtypes = [wt.LPCWSTR, wt.DWORD, wt.DWORD, wt.LPVOID, wt.DWORD, wt.DWORD, wt.HANDLE]
kernel.CreateFileW.restype = wt.HANDLE
kernel.ReadFile.argtypes = [wt.HANDLE, wt.LPVOID, wt.DWORD, ctypes.POINTER(wt.DWORD), wt.LPVOID]
kernel.ReadFile.restype = wt.BOOL
kernel.CloseHandle.argtypes = [wt.HANDLE]
kernel.CloseHandle.restype = wt.BOOL
kernel.ReplaceFileW.argtypes = [wt.LPCWSTR, wt.LPCWSTR, wt.LPCWSTR, wt.DWORD, wt.LPVOID, wt.LPVOID]
kernel.ReplaceFileW.restype = wt.BOOL
controller = WfpLeaseController.__new__(WfpLeaseController)
controller.runtime, controller.lock = FIXTURE, threading.RLock()
controller.operation = "unblock"
controller.append = lambda name, record: None
results = []

for index in range(5):
    old, new = ("old-snapshot-" + str(index)).encode(), ("new-snapshot-" + str(index)).encode()
    (FIXTURE / "status.json").write_bytes(old)
    replacement = FIXTURE / ("replacement-" + str(index) + ".json")
    replacement.write_bytes(new)
    opened, release = threading.Event(), threading.Event()
    calls, outcome = [], {}

    def create(*args):
        calls.append({"operation": "CreateFileW", "desiredAccess": args[1], "shareMode": args[2], "creationDisposition": args[4]})
        return kernel.CreateFileW(*args)

    def held_read(*args):
        opened.set()
        if not release.wait(2):
            raise TimeoutError("Synthetic release absent")
        return kernel.ReadFile(*args)

    def close(*args):
        result = kernel.CloseHandle(*args)
        calls.append({"operation": "CloseHandle", "result": bool(result)})
        return result

    proxy = SimpleNamespace(CreateFileW=create, ReadFile=held_read, CloseHandle=close)

    def reader():
        try:
            outcome["data"] = controller.read_status_once()
        except BaseException as error:
            outcome["error"] = repr(error)

    with patch("hypium_tests.wfp_controller.ctypes.WinDLL", return_value=proxy):
        thread = threading.Thread(target=reader)
        thread.start()
        assert opened.wait(2)
        replaced = bool(kernel.ReplaceFileW(str(FIXTURE / "status.json"), str(replacement), None, 0, None, None))
        native_error = ctypes.get_last_error() if not replaced else 0
        release.set()
        thread.join(2)
    assert not thread.is_alive() and "error" not in outcome, outcome
    assert replaced and outcome["data"] == old and (FIXTURE / "status.json").read_bytes() == new
    assert calls == [{"operation": "CreateFileW", "desiredAccess": 0x80000000, "shareMode": 7, "creationDisposition": 3}, {"operation": "CloseHandle", "result": True}]
    results.append({"name": "held_reader_replace_" + str(index), "result": "pass", "ReplaceFileW": replaced, "winerror": native_error,
                    "held_handle_complete_old_snapshot": True, "new_path_complete_new_snapshot": True, "calls": calls})

(FIXTURE / "status.json").write_bytes(b"X" * 70000)
assert len(controller.read_status_once()) == 65537
try:
    controller.read_status()
except AssertionError as error:
    assert str(error) == "Unexpected helper status size"
else:
    raise AssertionError("Oversized status accepted")
results.append({"name": "bounded_65537_and_overlong_rejected", "result": "pass"})

empty = FIXTURE / "missing-status-folder"
empty.mkdir(exist_ok=True)
controller.runtime = empty
try:
    controller.read_status_once()
except FileNotFoundError as error:
    assert error.winerror == 2 and error.filename == str(empty / "status.json")
    results.append({"name": "invalid_handle_error_preserved", "result": "pass", "winerror": error.winerror, "filename": error.filename})
else:
    raise AssertionError("Missing file accepted")
controller.runtime = FIXTURE

for read_failure, close_failure in ((True, False), (False, True), (True, True)):
    closes = []

    def denied_read(*args):
        if read_failure:
            ctypes.set_last_error(32)
            return 0
        return kernel.ReadFile(*args)

    def checked_close(*args):
        result = kernel.CloseHandle(*args)
        closes.append(bool(result))
        if close_failure:
            ctypes.set_last_error(6)
            return 0
        return result

    proxy = SimpleNamespace(CreateFileW=kernel.CreateFileW, ReadFile=denied_read, CloseHandle=checked_close)
    with patch("hypium_tests.wfp_controller.ctypes.WinDLL", return_value=proxy):
        try:
            controller.read_status_once()
        except OSError as error:
            assert error.winerror == (32 if read_failure else 6)
            assert error.filename == str(FIXTURE / "status.json") and closes == [True]
            if read_failure and close_failure:
                assert "CloseHandle also failed" in " ".join(error.__notes__)
            results.append({"name": "resource_errors_read_" + str(read_failure) + "_close_" + str(close_failure), "result": "pass",
                            "winerror": error.winerror, "filename": error.filename, "actual_handle_closed": True, "notes": getattr(error, "__notes__", [])})
        else:
            raise AssertionError("Native error accepted")

for read_failure in (False, True):
    closes = []

    def maybe_denied_read(*args):
        if read_failure:
            ctypes.set_last_error(32)
            return 0
        return kernel.ReadFile(*args)

    def permission_denied_close(*args):
        closes.append(bool(kernel.CloseHandle(*args)))
        ctypes.set_last_error(5)
        return 0

    proxy = SimpleNamespace(CreateFileW=kernel.CreateFileW, ReadFile=maybe_denied_read, CloseHandle=permission_denied_close)
    with patch("hypium_tests.wfp_controller.ctypes.WinDLL", return_value=proxy):
        try:
            controller.read_status_bytes()
        except PermissionError as error:
            assert error.winerror == (32 if read_failure else 5)
            assert error.status_handle_cleanup_failed is True and closes == [True]
            if read_failure:
                assert "CloseHandle also failed" in " ".join(error.__notes__)
            results.append({"name": "close_failure_nonretryable_through_wrapper_read_" + str(read_failure),
                            "result": "pass", "winerror": error.winerror, "actual_handle_closed": True,
                            "single_attempt": True, "cleanup_error_not_swallowed": True})
        else:
            raise AssertionError("Cleanup failure was swallowed by read retries")

summary = {"classification": "actual_local_file_and_injected_native_error_checks", "nativeWfpCalls": 0, "deviceCalls": 0,
           "pass": len(results), "fail": 0, "cases": results}
(OUT / "native-status-read-result.json").write_text(json.dumps(summary, indent=2), encoding="utf8")
print(json.dumps(summary))
