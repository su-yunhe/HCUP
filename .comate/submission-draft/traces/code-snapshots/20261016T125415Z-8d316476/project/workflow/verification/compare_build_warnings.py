"""Compare this task's clean build against its approved baseline diagnostics."""
import collections
import json
from pathlib import Path
import re
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
out = root / "traces/implementation-validation" / sys.argv[1]
lines = (out / "build-raw.log").read_text(encoding="utf-8-sig").splitlines()
warnings = []
for i, line in enumerate(lines):
    match = re.search(r"WARN: ArkTS:WARN File: (.+):(\d+):(\d+)$", line)
    if match:
        message = lines[i + 1].strip()
        warnings.append({"rawLogLine": i + 1, "file": match[1].replace("D:/HCUP/vg-spec9/", ""),
                         "line": int(match[2]), "column": int(match[3]), "message": message,
                         "category": "deprecated API" if "has been deprecated" in message else message})
baseline = json.loads((root / "traces/baseline-analysis/build-warning-index.json").read_text(encoding="utf-8"))
base_sources = {}
for file in {row["file"] for row in baseline}:
    result = subprocess.run(["git", "show", f"a22f32b07bf81c6dde4367e2543ebac29186cbc1:{file}"],
                            cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode:
        raise RuntimeError(f"Cannot read approved local baseline {file}: exit={result.returncode}")
    base_sources[file] = result.stdout.splitlines()
baseline_by_source = collections.Counter((row["message"], base_sources[row["file"]][row["line"] - 1].strip()) for row in baseline)
unmatched = []
for row in warnings:
    source_line = (root / row["file"]).read_text(encoding="utf-8").splitlines()[row["line"] - 1].strip()
    signature = row["message"], source_line
    row["sourceLine"] = source_line
    if baseline_by_source[signature]:
        baseline_by_source[signature] -= 1
        row["baselineMatch"] = "same diagnostic and source expression; relocation/line shifts permitted"
    else:
        row["baselineMatch"] = "requires review"
        unmatched.append(row)
summary = {"baseline_count": len(baseline), "current_count": len(warnings),
           "current_categories": dict(collections.Counter(row["category"] for row in warnings)),
           "unmatched_by_message_and_source_expression": unmatched,
           "remaining_baseline_count": sum(baseline_by_source.values()),
           "signing_warning": any("No signingConfig found" in line for line in lines)}
old_by_file_message = collections.Counter((row["file"], row["message"]) for row in baseline)
new_by_file_message = collections.Counter((row["file"], row["message"]) for row in warnings)
summary["net_added_by_file_and_message"] = [{"file": key[0], "message": key[1], "count": count}
                                                   for key, count in (new_by_file_message - old_by_file_message).items()]
summary["net_removed_by_file_and_message"] = [{"file": key[0], "message": key[1], "count": count}
                                                     for key, count in (old_by_file_message - new_by_file_message).items()]
(out / "build-warning-index.json").write_text(json.dumps(warnings, ensure_ascii=False, indent=2), encoding="utf-8")
(out / "build-warning-comparison.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
