"""Portable output-only wrapper for this task's unchanged six formal tests.

Requires the project's test-harness requirements and configured HarmonyOS tools.
The original suite reserves device127.0.0.1:11239; other devices are rejected.
No credentials are supplied. Exit2 means the harness completed with skipped cases.
This material helper has not itself been used for a new device run.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import importlib
import json
import os
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
import unittest

TEST_SHA = "7893587e2eeb59a7d91b366621d6791cf46f95aa474e450581a494cb8955ef7f"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class Tee:
    def __init__(self, original, log):
        self.original, self.log = original, log

    def write(self, value):
        self.original.write(value)
        self.original.flush()
        self.log.write(value)
        self.log.flush()

    def flush(self):
        self.original.flush()
        self.log.flush()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    parser.add_argument("--device", required=True)
    parser.add_argument("--hap", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="New output directory inside project; never overwritten")
    parser.add_argument("--hdc", help="Optional configured hdc executable")
    parser.add_argument("--allow-own-address-writes", action="store_true",
                        help="Enable original test05's own-created-address lifecycle; authentication still required")
    args = parser.parse_args()
    project, hap, out = args.project.resolve(), args.hap.resolve(), args.out.resolve()
    assert out.is_relative_to(project), "Original snapshot routine requires output inside project"
    test = project / "hypium_tests/test_address_workflow.py"
    manifest = project / "workflow/implementation/development-frozen-fingerprint-10.json"
    assert test.is_file() and sha(test) == TEST_SHA, "Original test version differs"
    assert hap.is_file() and not out.exists(), "Require existing HAP and a new output directory"
    frozen = json.loads(manifest.read_text(encoding="utf-8-sig"))

    def verify_sources():
        assert len(frozen["files"]) == 827
        for row in frozen["files"]:
            assert sha(project / row["path"]) == row["sha256"], row["path"]
        assert sha(test) == TEST_SHA

    verify_sources()
    sys.path[:0] = [str(project), str(project / "test-harness")]
    from harness.device import find_hdc
    module = importlib.import_module("hypium_tests.test_address_workflow")
    assert Path(module.__file__).resolve() == test
    assert unittest.defaultTestLoader.loadTestsFromTestCase(module.AddressWorkflowTests).countTestCases() == 6
    assert module.BUNDLE == "com.joker.coolmall"
    assert args.device == module.DEVICE, "Original test suite reserves device127.0.0.1:11239; no device operation performed"
    original_evidence = module.EVIDENCE.resolve()
    assert not out.is_relative_to(original_evidence) and not original_evidence.is_relative_to(out)

    def old_fingerprints():
        return [{"path": str(p.relative_to(project)), "sha256": sha(p)}
                for p in sorted(original_evidence.rglob("*")) if p.is_file()]

    old_before = old_fingerprints()
    module_identity = id(module)
    out.mkdir(parents=True)
    module.EVIDENCE = out / "ui"
    module.EVIDENCE.mkdir()
    shutil.copy2(test, out / "original-test_address_workflow.py")
    shutil.copy2(Path(__file__), out / "executed-material-wrapper.py")
    commands = []

    def command(label, argv):
        result = subprocess.run(argv, cwd=project, capture_output=True, timeout=180)
        (out / (label + ".log")).write_bytes(result.stdout + result.stderr)
        commands.append({"label": label, "argv": [str(x) for x in argv], "exit_code": result.returncode})
        save(out / "commands.json", commands)
        assert result.returncode == 0 and b"[Fail]" not in result.stdout, label
        return result.stdout

    hdc = args.hdc or str(find_hdc())
    installed = command("install", [hdc, "-t", args.device, "install", "-r", str(hap)])
    assert b"install bundle successfully" in installed
    bm = command("bundle-after-install", [hdc, "-t", args.device, "shell", "bm", "dump", "-n", module.BUNDLE])
    assert b"updateTime" in bm and module.BUNDLE.encode() in bm
    original_env = os.environ.get("CML28_ALLOW_ADDRESS_WRITES")
    os.environ["CML28_ALLOW_ADDRESS_WRITES"] = "1" if args.allow_own_address_writes else "0"
    runner_argv = ["harness.runner", "--project", str(project), "--device", args.device,
                   "--json", str(out / "selftest.json")]
    save(out / "invocation.json", {"captured_utc": datetime.now(timezone.utc).isoformat(),
         "wrapper_argv": sys.argv, "runner_argv": runner_argv,
         "CML28_ALLOW_ADDRESS_WRITES": os.environ["CML28_ALLOW_ADDRESS_WRITES"],
         "original_reserved_device": module.DEVICE,
         "source_aggregate": frozen["aggregate"], "test_sha256": TEST_SHA,
         "hap_sha256": sha(hap), "hap_bytes": hap.stat().st_size,
         "scope": "Real-service tests; no injected authentication. Evidence path only is configured."})
    previous_cwd, previous_argv = Path.cwd(), sys.argv[:]
    old_stdout, old_stderr = sys.stdout, sys.stderr
    try:
        with (out / "selftest.log").open("w", encoding="utf-8") as log:
            sys.stdout, sys.stderr = Tee(old_stdout, log), Tee(old_stderr, log)
            os.chdir(out)
            sys.argv = runner_argv
            try:
                runpy.run_module("harness.runner", run_name="__main__")
                code = 0
            except SystemExit as error:
                code = int(error.code or 0)
    finally:
        os.chdir(previous_cwd)
        sys.argv = previous_argv
        sys.stdout, sys.stderr = old_stdout, old_stderr
        if original_env is None:
            os.environ.pop("CML28_ALLOW_ADDRESS_WRITES", None)
        else:
            os.environ["CML28_ALLOW_ADDRESS_WRITES"] = original_env
    verify_sources()
    assert id(sys.modules["hypium_tests.test_address_workflow"]) == module_identity
    assert module.EVIDENCE == out / "ui"
    old_after = old_fingerprints()
    assert old_before == old_after, "Historical evidence changed"
    save(out / "old-evidence-fingerprints.json", old_after)
    result = json.loads((out / "selftest.json").read_text(encoding="utf-8"))
    assert len(result["cases"]) == 6
    counts = dict(Counter(row["outcome"] for row in result["cases"]))
    wrapper_code = code or (2 if counts.get("skip", 0) else 0)
    save(out / "completion.json", {"runner_exit_code": code, "wrapper_exit_code": wrapper_code,
         "counts": counts, "all_six_passed": all(row["outcome"] == "pass" for row in result["cases"]),
         "old_evidence_unchanged": True, "original_test_unchanged": True,
         "build_binding_limit": "Record the preceding clean-build command and log separately; this helper does not rebuild."})
    print(json.dumps({"counts": counts, "wrapper_exit_code": wrapper_code}))
    return wrapper_code


if __name__ == "__main__":
    raise SystemExit(main())
