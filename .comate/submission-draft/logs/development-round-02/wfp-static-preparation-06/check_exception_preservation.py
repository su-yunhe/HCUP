"""Synthetic error-recording regression; no device, helper, or WFP operation."""
import ast
import json
from pathlib import Path
import sys
import traceback
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
source = ROOT / "hypium_tests/wfp_offline_confirmation.py"
tree = ast.parse(source.read_text(encoding="utf8"))
test_class = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "WfpOfflineRestoreTests")
method = next(node for node in test_class.body if isinstance(node, ast.FunctionDef) and node.name == "hdc_preflight")
method.decorator_list = []
module = ast.fix_missing_locations(ast.Module(body=[method], type_ignores=[]))


class PrimaryFailure(Exception):
    pass


class RecoveryFailure(Exception):
    pass


def check(name, primary_failure, recovery_failure, expected_error):
    records, calls = {}, []

    class FakeEvidence:
        def __init__(self, folder, device):
            self.folder = folder
            assert device == "127.0.0.1:11237"

        def command(self, arguments):
            calls.append(arguments)
            return {"stdout": "tconn key [-remove]", "stderr": "", "exit_code": 0}

        def hdc(self, *arguments, **keywords):
            return {"stdout": "uid=2000(shell)", "exit_code": 0}

        def screen(self, name):
            pass

    class FakeController:
        def block(self):
            if primary_failure:
                raise PrimaryFailure("original strict-scope sentinel")

        def require_blocked(self, evidence, label):
            calls.append(label)

        def unblock(self):
            if recovery_failure:
                raise RecoveryFailure("secondary release sentinel")
            return {"state": "IDLE_UNBLOCKED"}

    namespace = {
        "Evidence": FakeEvidence, "shutil": SimpleNamespace(which=lambda name: "hdc"),
        "sys": sys, "traceback": traceback,
        "time": SimpleNamespace(monotonic=lambda: 0, sleep=lambda _: None),
        "utc": lambda: "synthetic-only",
        "write_json": lambda path, value: records.setdefault(path.name, value),
    }
    exec(compile(module, str(source), "exec"), namespace)
    error = None
    try:
        namespace["hdc_preflight"](SimpleNamespace(out=Path("synthetic"), device_sn="127.0.0.1:11237", wfp=FakeController()))
    except BaseException as caught:
        error = caught
    assert (type(error) if error else None) is expected_error
    if primary_failure:
        assert records["preflight-primary-error.json"]["type"] == "PrimaryFailure"
        assert "original strict-scope sentinel" in records["preflight-primary-error.json"]["traceback"]
    if recovery_failure:
        assert records["preflight-recovery-error.json"]["primary_error_preserved"] is primary_failure
    assert ("preflight-verdict.json" in records) is (expected_error is None)
    if expected_error is None:
        assert "before-target-reconnect" in calls and "after-target-reconnect" in calls
        assert ["hdc", "tconn", "127.0.0.1:11237", "-remove"] in calls
        assert ["hdc", "tconn", "127.0.0.1:11237"] in calls
    return {"name": name, "result": "pass", "raised": type(error).__name__ if error else None,
            "records": list(records), "synthetic_no_native_or_device_calls": True}


result = {"classification": "facility_exception_recording_only", "cases": [
    check("primary_and_recovery_fail", True, True, PrimaryFailure),
    check("only_recovery_fails", False, True, RecoveryFailure),
    check("successful_gate_retained", False, False, None),
], "product_requirement_evidence": False}
(Path(__file__).parent / "exception-preservation-result.json").write_text(json.dumps(result, indent=2), encoding="utf8")
print(json.dumps(result))
