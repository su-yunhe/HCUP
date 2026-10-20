"""Offline audit of already captured evidence; does not operate the device."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "logs/implementation-validation"


def visit(tree):
    if isinstance(tree, dict):
        if tree.get("attributes"):
            yield tree["attributes"]
        for child in tree.get("children", []):
            yield from visit(child)
    elif isinstance(tree, list):
        for child in tree:
            yield from visit(child)


def main(run):
    out = BASE / ("run-" + run)
    rows = [json.loads(line) for line in (out / "timeline.jsonl").read_text(encoding="utf-8").splitlines()]
    samples = [r for r in rows if r["kind"] == "pending_ui_asserted"]
    begins = {r["request_id"]: r for r in rows if r["kind"] == "request_begin"}
    ends = {r["request_id"]: r for r in rows if r["kind"] == "response_end"}
    aligned = []
    for sample in samples:
        matched = [rid for rid in sample["request_ids"] if rid in ends
                   and begins[rid]["time"] < sample["time"] < ends[rid]["time"]]
        assert matched, "A sampled loading UI was not inside a genuine request begin/end interval"
        aligned.append({"scenario": sample["name"], "sample": sample["sample"], "time": sample["time"], "request_ids": matched})
    waits = []
    for path in out.glob("second-confirmation-*.json"):
        attrs = list(visit(json.loads(path.read_text(encoding="utf-8"))))
        loading = [a for a in attrs if a.get("id") == "webdav_restore_loading" and a.get("visible") == "true"]
        restore = [a for a in attrs if a.get("id") == "webdav_restore_from_cloud"]
        waits.append({"file": path.name, "visible_spinner": bool(loading),
                      "restore_exposed": bool(restore), "exposed_restore_disabled": all(a["enabled"] == "false" for a in restore) if restore else None})
        assert not loading, "Spinner active during human confirmation wait"
        if restore:
            assert all(a["enabled"] == "false" for a in restore)
    export_paths = sorted(out.glob("export-*.json"))
    exports = [json.loads(p.read_text(encoding="utf-8")) for p in export_paths]
    business = {"export_files": [p.name for p in export_paths]}
    if len(exports) >= 3:
        before, canceled, restored = ({w["word"] for w in e["words"]} for e in exports[:3])
        prefix = "spec15proof" + run + "x"
        expected = {prefix + f"{i:04d}" for i in range(1000)}
        assert not (before & expected)
        assert before == canceled
        assert expected.issubset(restored)
        business.update({"before_words": len(before), "after_cancel_words": len(canceled),
                         "after_import_words": len(restored), "verified_new_fixture_words": len(expected),
                         "cancel_preserved_business": True, "actual_import_readback": True})
    before = json.loads((BASE / f"source-before-run-{run}.json").read_text(encoding="utf-8"))
    after = json.loads((BASE / f"source-after-run-{run}.json").read_text(encoding="utf-8"))
    assert before["files"] == after["files"], "Production source changed while tests ran"
    selftest = json.loads((BASE / f"selftest-{run}.json").read_text(encoding="utf-8"))
    outcomes = Counter(c["outcome"] for c in selftest["cases"])
    report = {"run": run, "source_sha256": before["sha256"], "source_unchanged": True,
              "harness_outcomes": dict(outcomes), "pending_sample_count": len(samples),
              "samples_inside_live_request_intervals": aligned, "second_waits": waits,
              "business_readback": business,
              "request_statuses": dict(Counter(str(r["status"]) for r in ends.values())),
              "completed_scenarios": [r["name"] for r in rows if r["kind"] == "verified_scenario"],
              "retained_evidence_files": len(list(out.iterdir()))}
    target = out / "offline-audit.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k not in ("samples_inside_live_request_intervals", "second_waits")}, ensure_ascii=False,indent=2))
    return 0 if outcomes.get("fail", 0) + outcomes.get("error", 0) + outcomes.get("skip", 0) == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
