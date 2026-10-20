"""Compare current diagnostics to this task's approved baseline, including moves."""
import csv
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parents[2]
folder = Path(__file__).resolve().parent
raw = (folder / "build.log").read_text(encoding="utf-8-sig")
pattern = re.compile(r"ArkTS:WARN File: (.+?):(\d+):(\d+)\s*\n\s*([^\r\n]+)")
current = []
for path, line, column, message in pattern.findall(raw):
    relative = Path(path).relative_to(root).as_posix()
    category = "P1-deprecated-api" if "deprecated" in message else (
        "P2-exception-handling" if "throw exceptions" in message else "P2-ArkTS-restriction")
    current.append({"file": relative, "line": int(line), "column": int(column),
                    "category": category, "message": message.strip()})
with (folder / "warnings.csv").open("w", encoding="utf-8-sig", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=["file", "line", "column", "category", "message"])
    writer.writeheader()
    writer.writerows(current)
with (root / "logs/analysis-baseline/warnings.csv").open(encoding="utf-8-sig", newline="") as stream:
    baseline = list(csv.DictReader(stream))
for warning in baseline:
    warning["line"] = int(warning["line"])
    warning["column"] = int(warning["column"])

old_texts = {}
new_texts = {}
for warning in baseline:
    name = warning["file"]
    if name not in old_texts:
        old_texts[name] = subprocess.check_output(
            ["git", "show", "88db8789e28333c7b7dcc8db078f394a262b73c3:" + name], cwd=root).decode().splitlines()
for warning in current:
    name = warning["file"]
    if name not in new_texts:
        new_texts[name] = (root / name).read_text(encoding="utf-8-sig").splitlines()

def statement(warning, sources):
    lines = sources[warning["file"]]
    position = warning["line"] - 1
    return re.sub(r"\s+", "", lines[position]) if 0 <= position < len(lines) else ""

unmatched = set(range(len(baseline)))
same, relocated, added = [], [], []
for warning in current:
    exact = [i for i in unmatched if all(baseline[i][k] == warning[k] for k in ("file", "line", "column", "message"))]
    if exact:
        unmatched.remove(exact[0])
        same.append(warning)
        continue
    line = statement(warning, new_texts)
    candidates = [i for i in unmatched if baseline[i]["message"] == warning["message"] and
                  statement(baseline[i], old_texts) == line]
    if candidates:
        candidates.sort(key=lambda i: (baseline[i]["file"] != warning["file"],
                                       abs(baseline[i]["line"] - warning["line"])))
        index = candidates[0]
        unmatched.remove(index)
        relocated.append({"before": baseline[index], "after": warning,
                          "normalized_statement": line, "match": "same message and corresponding source statement"})
    elif (warning["file"] == "entry/src/main/ets/sync/WebDavManualSyncController.ets" and
          warning["message"] == "'showToast' has been deprecated." and
          line == "promptAction.showToast({message,duration:1200});"):
        # Human-audited extraction: old manual handler's res.message toast now
        # calls this.showToast(response.message), whose helper performs this call.
        candidates = [i for i in unmatched if baseline[i]["file"] ==
                      "entry/src/main/ets/pages/settings/SettingsSyncSection.ets" and
                      baseline[i]["line"] == 310 and baseline[i]["message"] == warning["message"]]
        if not candidates:
            added.append({**warning, "normalized_statement": line})
            continue
        index = candidates[0]
        unmatched.remove(index)
        relocated.append({"before": baseline[index], "after": warning,
                          "normalized_statement": line,
                          "match": "manually reviewed extraction of the same manual-sync promptAction.showToast API into helper",
                          "call_ownership": "old manual res.message -> controller response.message -> showToast(message)"})
    else:
        added.append({**warning, "normalized_statement": line})

result = {"baseline_source_warnings": len(baseline), "current_source_warnings": len(current),
          "same": len(same), "relocated": relocated, "new_candidates": added,
          "removed": [baseline[i] for i in sorted(unmatched)],
          "message_counts_equal": Counter(w["message"] for w in baseline) == Counter(w["message"] for w in current),
          "signing_warning_count": raw.count("No signingConfig found for product default"),
          "status": "pass" if not added else "needs_review"}
(folder / "warning-comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in result.items()}, ensure_ascii=False))
