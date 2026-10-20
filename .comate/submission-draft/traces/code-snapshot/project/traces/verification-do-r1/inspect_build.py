"""Independent frozen-input and full warning comparison (no device commands)."""
import collections
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
baseline = ROOT / "logs/analysis-baseline-assembleHap.log"
current = ROOT / "logs/verification-do-build-run-r1-assembleHap.log"


def parse(path):
    text = re.sub(r"\x1b\[[0-9;]*m", "", path.read_text(encoding="utf-8-sig", errors="replace")).replace("\r\n", "\n")
    diagnostics = [(a.strip().replace("\\", "/"), b.strip()) for a, b in re.findall(r"ArkTS:WARN File: ([^\n]+)\n[ \t]*([^\n]+)", text)]
    others = [line.strip() for line in text.splitlines() if re.search(r"\bWARN\b", line) and "ArkTS:WARN File:" not in line]
    return diagnostics, others


def difference(before, after):
    a, b = collections.Counter(before), collections.Counter(after)
    return {"added": list((b - a).elements()), "removed": list((a - b).elements())}


old, old_other = parse(baseline)
new, new_other = parse(current)
result = {"baselineFileDiagnosticCount": len(old), "currentFileDiagnosticCount": len(new),
          "fileDiagnosticDifference": difference(old, new),
          "otherWarningLineDifference": difference(old_other, new_other),
          "rawInputs": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (baseline, current)}}
(OUT / "independent-warning-compare-r1.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
(OUT / "independent-file-diagnostics-r1.json").write_text(json.dumps(new, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
assert len(old) == 182, "Baseline parser must recover the recorded complete diagnostic set"
assert not result["fileDiagnosticDifference"]["added"], "New file diagnostics require parent review"
assert not result["otherWarningLineDifference"]["added"], "New non-file warnings require parent review"
