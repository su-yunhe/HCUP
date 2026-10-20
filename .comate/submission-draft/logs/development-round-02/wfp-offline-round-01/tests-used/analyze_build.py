"""Compare independent clean-build diagnostics to this task's own baseline."""
from __future__ import annotations
import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

from hypium_tests.evidence import ROOT, digest, source_fingerprint, write_json, utc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir")
    args = parser.parse_args()
    run = (ROOT / args.run_dir).resolve()
    assert run.is_relative_to(ROOT)
    text = re.sub(r"\x1b\[[0-9;]*m", "", (run / "build.log").read_text(encoding="utf-8-sig"))
    pattern = re.compile(r"WARN: ArkTS:WARN File: (.+?):(\d+):(\d+)\s*\n([^\n]+)")
    rows = [{"path": p, "line": int(l), "column": int(c), "message": m.strip()}
            for p, l, c, m in pattern.findall(text)]
    baseline = list(csv.DictReader((ROOT / "traces/baseline-round-01/build-warnings.csv").open(encoding="utf-8-sig")))

    def key(row):
        return (row["path"].replace("SettingsWebDavActions.ets", "SettingsSyncSection.ets"), row["message"])

    old, new = Counter(map(key, baseline)), Counter(map(key, rows))
    def entries(counter):
        return [{"path": p, "message": m, "count": n} for (p, m), n in counter.items()]
    write_json(run / "build-diagnostics.json", rows)
    with (run / "build-diagnostics.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "line", "column", "message"])
        writer.writeheader()
        writer.writerows(rows)
    result = {"at": utc(), "baseline_arkts": len(baseline), "clean_arkts": len(rows),
              "signing_warning": "No signingConfig found for product default" in text,
              "new_diagnostics": entries(new - old), "not_reported_diagnostics": entries(old - new),
              "rule": "Compare path+message+occurrence count, ignoring shifted line/column; map moved Actions back to SyncSection",
              "build_success": "BUILD SUCCESSFUL" in text}
    write_json(run / "warning-comparison.json", result)
    implementation = json.loads((ROOT / "logs/implementation-round-01/source-fingerprint.json").read_text(encoding="utf-8"))
    current = source_fingerprint()
    manifest = implementation["production_tree_sources"]
    unequal = [entry["path"] for entry in manifest if current.get(entry["path"]) != entry["sha256"]]
    ordered_hash = digest("".join(entry["path"] + "\t" + current[entry["path"]] + "\n" for entry in manifest).encode())
    write_json(run / "freeze-comparison.json", {"at": utc(), "files": len(manifest), "different_paths": unequal,
        "using_implementation_manifest_order_sha256": ordered_hash,
        "expected_sha256": implementation["production_tree_manifest_sha256"],
        "equal": not unequal and ordered_hash == implementation["production_tree_manifest_sha256"],
        "note": "Initial Python ordinal re-sort produced e54e... while PowerShell manifest order produces the expected digest; file hashes unchanged"})
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
