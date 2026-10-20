"""Evidence helpers: source fingerprints and normalized baseline build warnings."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("VG15_AUDIT_DIR", str(ROOT / "logs" / "implementation-validation")))


def fingerprint():
    paths = [p for base in (ROOT / "entry/src", ROOT / "AppScope", ROOT / "hvigor")
             for p in base.rglob("*") if p.is_file()]
    paths += [p for p in ROOT.iterdir() if p.is_file() and p.suffix in (".json5", ".ts", ".properties")]
    records = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    return {"head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "files": records, "sha256": hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()}


def test_archive(label):
    target = OUT / ("archive-" + label)
    target.mkdir(parents=True, exist_ok=True)
    records = {}
    for path in sorted((ROOT / "hypium_tests").iterdir()):
        if path.is_file() and path.suffix in (".py", ".mjs", ".ps1"):
            raw = path.read_bytes()
            (target / path.name).write_bytes(raw)
            records[path.name] = hashlib.sha256(raw).hexdigest()
    return {"archive": str(target), "files": records,
            "sha256": hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest()}


def warnings():
    raw = (OUT / "build.raw.log").read_text(encoding="utf-8-sig", errors="replace")
    lines = raw.splitlines()
    records = []
    for i, line in enumerate(lines):
        match = re.search(r"ArkTS:WARN File: (.+?):(\d+):(\d+)", line)
        if match:
            message = lines[i + 1].strip() if i + 1 < len(lines) else ""
            records.append({"file": match.group(1).replace("\\", "/").replace(str(ROOT).replace("\\", "/") + "/", ""),
                            "line": int(match.group(2)), "column": int(match.group(3)), "message": message})
    baseline = json.loads((ROOT / "logs/analyze-baseline/warning-index.json").read_text(encoding="utf-8-sig"))
    norm = lambda r: (r["file"].replace("\\", "/").replace(str(ROOT).replace("\\", "/") + "/", ""), r["message"])
    before = Counter(norm(r) for r in baseline if "file" in r and r.get("message"))
    after = Counter(norm(r) for r in records)
    result = {"baseline_diagnostics": sum(before.values()), "current_diagnostics": len(records),
              "added": [{"file": k[0], "message": k[1], "count": n} for k, n in (after - before).items()],
              "removed": [{"file": k[0], "message": k[1], "count": n} for k, n in (before - after).items()],
              "current": records, "normalization": "file + message count; ignores relocated line/column"}
    (OUT / "warning-comparison.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "current"}, ensure_ascii=False))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    if sys.argv[1] == "warnings":
        warnings()
    else:
        path = OUT / (sys.argv[1] + ".json")
        value = test_archive(sys.argv[1]) if sys.argv[1].startswith("tests-") else fingerprint()
        path.write_text(json.dumps(value, indent=2), encoding="utf-8")
        print(json.dumps({"path": str(path), "sha256": value["sha256"], "files": len(value["files"])}))
