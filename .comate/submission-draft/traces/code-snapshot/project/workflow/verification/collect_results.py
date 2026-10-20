"""Merge explicit requirements with three real-window AND coverage; retain raw cases."""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import re
from cml_evidence import ROOT, write_json

parser = argparse.ArgumentParser()
parser.add_argument("--round", action="append", type=Path, required=True)
parser.add_argument("--out", type=Path, required=True)
parser.add_argument("--document-review", type=Path)
args = parser.parse_args()
requirements = [f"A{i}" for i in range(1, 16)] + [f"B{i}" for i in range(1, 20)] + [f"C{i}" for i in range(1, 8)]
observations = {req: [] for req in requirements}
rounds = []
source_sha = hap_sha = None
for folder in args.round:
    folder = folder.resolve()
    folder.relative_to(ROOT / "logs")
    report = json.loads((folder / "selftest.json").read_text(encoding="utf-8"))
    artifact = json.loads((folder / "install-manifest.json").read_text(encoding="utf-8"))
    before = json.loads((folder / "fingerprint-before.json").read_text(encoding="utf-8"))
    after = json.loads((folder / "fingerprint-after.json").read_text(encoding="utf-8"))
    assert before["sha256"] == after["sha256"] == artifact["source_sha256"], "Source changed: cannot merge this round"
    if source_sha is not None:
        assert source_sha == artifact["source_sha256"] and hap_sha == artifact["hap_sha256"], "Cannot merge different artifacts"
    source_sha, hap_sha = artifact["source_sha256"], artifact["hap_sha256"]
    test_before = json.loads((folder / "test-code-fingerprint-before.json").read_text(encoding="utf-8"))
    test_after = json.loads((folder / "test-code-fingerprint-after.json").read_text(encoding="utf-8"))
    assert test_before == test_after, "Test scripts changed within this round"
    selected_path = folder / "selection.json"
    selection = json.loads(selected_path.read_text(encoding="utf-8")) if selected_path.is_file() else {"kind": "full", "selected_count": len(report["cases"])}
    rounds.append({"round": folder.relative_to(ROOT).as_posix(), "device": report["device_sn"], "selection": selection,
                   "case_counts": dict(Counter(case["outcome"] for case in report["cases"])),
                   "raw_cases": report["cases"], "environment_warnings": report["env_warnings"],
                   "test_code_sha256": test_before})
    for case in report["cases"]:
        match = re.match(r"test_([ABC])(\d+)\b", case["name"])
        if not match:
            continue
        req = match.group(1) + str(int(match.group(2)))
        test_name = "test_" + match.group(1) + match.group(2)
        path = folder / (test_name + ".observations.json")
        detail = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
        observations[req].append({"round": folder.relative_to(ROOT).as_posix(), "outcome": case["outcome"],
                                  "message": case["message"], "actual_layout": detail.get("actual_layout"),
                                  "observation": path.relative_to(ROOT).as_posix() if path.is_file() else None})

doc_review = json.loads(args.document_review.read_text(encoding="utf-8")) if args.document_review else None
if doc_review:
    assert doc_review["source_sha256"] == source_sha and doc_review["hap_sha256"] == hap_sha
matrix = []
for req in requirements:
    rows = observations[req]
    failure = [row for row in rows if row["outcome"] in ("fail", "error")]
    passed = [row for row in rows if row["outcome"] == "pass"]
    status, reason = "not_run", "No valid executed pass evidence"
    if req in ("B9", "B10", "B11"):
        status, reason = "blocked", "No issued provider application configuration/account and genuine authorization environment; unavailable feedback is not a login flow"
    elif failure:
        status, reason = "fail", "Valid final-round failure; see original case logs"
    elif req in ("C6", "C7"):
        covered = {row["actual_layout"] for row in passed}
        if {"phone", "tablet", "large"} <= covered:
            status, reason = "pass", "Pass evidence in all 3 actual window classes"
        else:
            reason = "Missing actual-window coverage: " + ", ".join(sorted({"phone", "tablet", "large"} - covered))
    elif req.startswith("C"):
        group = {"C1": "phone", "C2": "tablet", "C3": "tablet", "C4": "large", "C5": "large"}[req]
        if any(row["actual_layout"] == group for row in passed):
            status, reason = "pass", "Measured pass at actual " + group + " window"
    elif passed:
        status, reason = "pass", "Observed UI/interaction evidence; manual pixels used only for visual attributes"
    if req in ("B14", "B15") and status == "pass":
        name = "user_agreement" if req == "B14" else "privacy_policy"
        reviewed = (doc_review and (doc_review.get("documents", {}).get(name, {}).get("status") == "pass" or
                                   doc_review.get("requirements", {}).get(req, {}).get("status") == "pass_visual_end"))
        if not reviewed:
            status, reason = "not_run", "Actual document end pixels still need independent review"
    matrix.append({"requirement": req, "status": status, "reason": reason, "evidence": rows})
result = {"source_sha256": source_sha, "hap_sha256": hap_sha,
          "requirement_counts": dict(Counter(row["status"] for row in matrix)),
          "requirements": matrix, "rounds": rounds, "document_review": doc_review,
          "limits": "Local acceptance evidence, not hidden tests or an official score. Original interrupted/obsolete-artifact rounds are retained separately and are not merged."}
write_json(args.out.resolve(), result)
print(json.dumps(result["requirement_counts"]))
