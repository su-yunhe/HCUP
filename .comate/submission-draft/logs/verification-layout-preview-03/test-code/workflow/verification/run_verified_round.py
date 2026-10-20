"""Frozen-code build -> fresh install -> capture or suite, with raw auditable logs."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys

from cml_evidence import ROOT, hdc_record, production_fingerprint, run_record, snapshot, write_json


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", required=True)
    parser.add_argument("--expected-source-sha256", required=True)
    parser.add_argument("--device", required=True)
    parser.add_argument("--mode", choices=["capture", "suite"], required=True)
    parser.add_argument("--visual-review")
    parser.add_argument("--allow-rotation", action="store_true")
    parser.add_argument("--built-manifest", type=Path)
    parser.add_argument("--initial-rotation", type=int, choices=range(4))
    parser.add_argument("--suite-kind", choices=["full", "smoke", "layout", "documents"], default="full")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", args.round):
        raise ValueError("Round must be a simple task-local directory name")
    out = ROOT / "logs" / args.round
    out.mkdir(exist_ok=False)
    before = production_fingerprint()
    write_json(out / "fingerprint-before.json", before)
    test_names = ["hypium_tests/test_login_acceptance.py", "workflow/verification/cml_evidence.py",
                  "workflow/verification/run_verified_round.py", "workflow/verification/run_navigation_smoke.py",
                  "workflow/verification/run_selected_checks.py", "workflow/verification/run-verified-round.ps1",
                  "workflow/verification/approved-document-fragments.json", "workflow/verification/provider-error-expectations.json"]
    test_hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in test_names}
    write_json(out / "test-code-fingerprint-before.json", test_hashes)
    for name in test_names:
        target = out / "test-code" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    if before["sha256"] != args.expected_source_sha256:
        raise RuntimeError("Source differs from the coordinator's explicit freeze")
    write_json(out / "environment.json", {
        "python": sys.executable, "device": args.device,
        "thread": os.environ.get("CODEX_THREAD_ID"), "cwd": str(ROOT),
        "hvigorw": shutil.which("hvigorw"), "hdc": shutil.which("hdc"),
        "SDK": os.environ.get("DEVECO_SDK_HOME"),
    })
    hvigor = shutil.which("hvigorw")
    if not hvigor:
        raise RuntimeError("Harmony environment not loaded")
    build_commands = [
        ("clean", [hvigor, "--mode", "project", "-p", "product=default", "clean", "--no-daemon"]),
        ("build", [hvigor, "--mode", "module", "-p", "product=default", "-p", "module=entry@default", "-p", "buildMode=debug", "clean", "assembleHap", "--no-daemon", "--no-incremental"]),
    ]
    if args.built_manifest:
        previous = json.loads(args.built_manifest.read_text(encoding="utf-8"))
        prior_hap = Path(previous["hap_path"])
        if previous["source_sha256"] != before["sha256"] or hashlib.sha256(prior_hap.read_bytes()).hexdigest() != previous["hap_sha256"]:
            raise RuntimeError("Previously built HAP/source differs; do not reuse it")
        write_json(out / "build-reuse.json", {"manifest": str(args.built_manifest.resolve()), "artifact": previous})
        build_commands = []
    for label, command in build_commands:
        print("COMMAND:", command, flush=True)
        row = run_record(out, label, command, timeout=600, cwd=ROOT)
        print(label, "exit", row["exit_code"], flush=True)
        if row["exit_code"]:
            return row["exit_code"]
    after_build = production_fingerprint()
    write_json(out / "fingerprint-after-build.json", after_build)
    changed = [name for name in before["files"].keys() | after_build["files"].keys()
               if before["files"].get(name) != after_build["files"].get(name)]
    write_json(out / "build-generated-input-changes.json", changed)
    if changed:
        raise RuntimeError("Production inputs changed during build; coordinator must classify changes and refreeze")
    hap = ROOT / "entry/build/default/outputs/default/entry-default-unsigned.hap"
    artifact = {"hap_path": str(hap), "hap_sha256": hashlib.sha256(hap.read_bytes()).hexdigest(),
                "source_sha256": before["sha256"], "built_at": previous["built_at"] if args.built_manifest else datetime.now(timezone.utc).isoformat(),
                "device": args.device}
    # Explicit target avoids testing another concurrently running emulator.
    install = hdc_record(out, "install", "install", "-r", str(hap))
    artifact.update({"installed_at": datetime.now(timezone.utc).isoformat(),
                     "install_exit_code": install["exit_code"], "install_output": install["stdout"]})
    write_json(out / "install-manifest.json", artifact)
    if install["exit_code"] or "success" not in install["stdout"].lower():
        raise RuntimeError("Fresh HAP install failed; do not run feature tests")
    os.environ["CML_RUN_DIR"] = str(out)
    if args.visual_review:
        os.environ["CML_VISUAL_REVIEW"] = args.visual_review
    if args.allow_rotation:
        os.environ["CML_ALLOW_ROTATION"] = "1"
    if args.initial_rotation is not None:
        os.environ["CML_INITIAL_ROTATION"] = str(args.initial_rotation)
    if args.mode == "suite":
        if args.suite_kind == "smoke":
            command = [sys.executable, str(ROOT / "workflow/verification/run_navigation_smoke.py"), "--json", str(out / "selftest.json")]
        elif args.suite_kind in ("layout", "documents"):
            command = [sys.executable, str(ROOT / "workflow/verification/run_selected_checks.py"), "--selection", args.suite_kind, "--json", str(out / "selftest.json")]
        else:
            command = [sys.executable, "-m", "harness.runner", "--project", str(ROOT), "--device", args.device, "--json", str(out / "selftest.json")]
        row = run_record(out, "hypium-runner", command, timeout=1800, cwd=out)
        code = row["exit_code"]
    else:
        os.chdir(out)
        from hypium import UiDriver, BY
        driver = UiDriver.connect(device_sn=args.device)
        driver.set_implicit_wait_time(2)
        driver.stop_app("com.joker.coolmall")
        driver.start_app("com.joker.coolmall", page_name="EntryAbility", wait_time=2)
        snapshot(out, "first-launch")
        # Capture mode intentionally stops at the natural first-launch UI.
        # Further navigation/permission handling is performed from observed UI.
        code = 0
    after = production_fingerprint()
    write_json(out / "fingerprint-after.json", after)
    test_after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in test_names}
    write_json(out / "test-code-fingerprint-after.json", test_after)
    if test_after != test_hashes:
        raise RuntimeError("Test/helper inputs changed during this round; affected evidence must be rerun")
    if after["sha256"] != before["sha256"]:
        raise RuntimeError("Sources changed during validation; all affected evidence is invalid")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
