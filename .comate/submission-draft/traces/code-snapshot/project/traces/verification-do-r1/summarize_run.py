"""Summarize actual per-A assertions and immutable evidence; never fabricate skips/pass."""
import argparse
import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--run", required=True)
args = parser.parse_args()
base = Path(__file__).resolve().parent / args.run
runner_file = ROOT / "logs" / f"selftest-{args.run}.json"
runner = json.loads(runner_file.read_text(encoding="utf-8-sig")) if runner_file.exists() else None
observations = collections.defaultdict(list)
case_completion = {}
for path in sorted(base.glob("test_*/case-result.json")):
    result = json.loads(path.read_text(encoding="utf-8"))
    case_completion[result["test"]] = result["completed"]
    for item in result["observations"]:
        for a in item["items"]:
            observations[a].append({"case": result["test"], "assertion": item,
                                    "record": str(path.relative_to(ROOT))})

status = []
for number in range(1, 45):
    ident = f"A{number}"
    records = observations[ident]
    outcomes = [r["assertion"]["status"] for r in records]
    value = "fail" if "fail" in outcomes else "blocked" if "blocked" in outcomes else "pass" if records else "not_run"
    status.append({"id": ident, "status": value, "evidence": records,
                   "kind": "approved implementation policy" if number >= 40 else "explicit" if number <= 28 else "derived"})

source_changes = []
for path in sorted(base.glob("test_*/source-difference.json")):
    changes = json.loads(path.read_text(encoding="utf-8"))
    if changes:
        source_changes.append({"file": str(path), "changes": changes})
frames = []
for path in sorted(base.rglob("frame-times.json")):
    timing = json.loads(path.read_text(encoding="utf-8"))
    starts = [x for x in timing if x["event"] == "START"]
    ends = [x for x in timing if x["event"] == "END"]
    frames.append({"file": str(path.relative_to(ROOT)), "startedFrames": len(starts), "finishedFrames": len(ends),
                   "durationHostSeconds": starts[-1]["hostMonotonic"] - starts[0]["hostMonotonic"] if len(starts) > 1 else None,
                   "nativeFailures": [x for x in ends if x["exit"] != 0]})
scripts = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted((ROOT / "hypium_tests").glob("*.py"))}
result = {"run": args.run, "runner": runner, "caseCompletion": case_completion,
          "AStatusCounts": dict(collections.Counter(x["status"] for x in status)), "items": status,
          "sourceChanges": source_changes, "testSHA256AtSummary": scripts, "frameCollections": frames,
          "N_A": {"emptyInput": "No text input/submission in Spec", "whitespaceInput": "No text input/submission in Spec",
                   "requestFailureInjection": "No navigation/content API in approved local implementation",
                   "emptyRemoteCategory": "Fixed local category data, no remote response/empty source",
                   "overlayRouteReturn": "No approved reachable overlay route; normal warm background/foreground is tested"},
          "complete": runner is not None and bool(runner.get("cases"))
             and all(x["outcome"] == "pass" for x in runner["cases"])
             and len(case_completion) == 8 and all(case_completion.values())
             and not source_changes and all(x["status"] == "pass" for x in status)}
output = base / "verification-summary.json"
output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"run": args.run, "complete": result["complete"], "caseCompletion": case_completion,
                  "AStatusCounts": result["AStatusCounts"], "sourceChanges": source_changes,
                  "frameCollectionCount": len(frames)}, ensure_ascii=False))
