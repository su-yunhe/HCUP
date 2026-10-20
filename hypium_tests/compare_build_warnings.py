"""Compare full clean-build diagnostics, retaining source locations and moves."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "traces/do-verification-build-v1"
baseline = json.loads((ROOT / "traces/analysis-baseline-build/warnings-full.json").read_text(encoding="utf-8-sig"))
log = (OUT / "build.log").read_text(encoding="utf-8-sig")
log = re.sub(r"\x1b\[[0-9;]*m", "", log)
pattern = re.compile(r"(?:WARN|INFO|ERROR): ArkTS:(?:WARN|INFO|ERROR) File: (.+?):(\d+):(\d+)\s*\n([^\n]+)")
current = [{"file": match[1].replace("\\", "/"), "line": int(match[2]),
            "column": int(match[3]), "message": match[4].strip(),
            "build_log_line": log.count("\n", 0, match.start()) + 1}
           for match in pattern.finditer(log)]
cache = {}


def source_line(item, old):
    rel = item["file"].removeprefix(ROOT.as_posix() + "/")
    key = (old, rel)
    if key not in cache:
        if old:
            result = subprocess.run(["git", "show", "HEAD:" + rel], cwd=ROOT,
                                    capture_output=True, text=True, encoding="utf-8")
            if result.returncode:
                raise RuntimeError("Cannot read this question baseline source: " + rel)
            cache[key] = result.stdout.splitlines()
        else:
            cache[key] = (ROOT / rel).read_text(encoding="utf-8").splitlines()
    lines = cache[key]
    return re.sub(r"\s+", " ", lines[item["line"] - 1].strip())


def key(item, old):
    file = item["file"]
    # The approved extraction moves existing card declarations to this file.
    file = file.replace("/SettingsSyncCards.ets", "/SettingsSyncSection.ets")
    return file, item["message"], source_line(item, old)


pool = {}
for item in baseline:
    pool.setdefault(key(item, True), []).append(item)
matches, added = [], []
for item in current:
    possibilities = pool.get(key(item, False), [])
    if possibilities:
        previous = possibilities.pop(0)
        matches.append({"baseline": previous, "current": item,
                        "mapping": "same diagnostic message and exact normalized source statement"})
    else:
        added.append({**item, "source_statement": source_line(item, False)})
removed = [item for remaining in pool.values() for item in remaining]
result = {"baseline_count": len(baseline), "current_count": len(current),
          "matched_count": len(matches), "added": added, "removed": removed,
          "status": "pass" if len(baseline) == 764 and current and not added else "fail",
          "comparison": "file/message/normalized statement, consumes duplicates; approved cards extraction maps to original file"}
for filename, data in (("warnings-current.json", current), ("warnings-matched.json", matches),
                       ("warning-comparison.json", result)):
    (OUT / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
raise SystemExit(0 if result["status"] == "pass" else 1)
