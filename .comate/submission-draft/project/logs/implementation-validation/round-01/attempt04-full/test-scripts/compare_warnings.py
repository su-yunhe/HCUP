"""Compare fresh ArkTS warnings with this problem's approved baseline, including moved code."""
from __future__ import annotations

import argparse
import collections
import csv
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "9cbcf7292c8cc46955dc3b522ddbda41c66a61d9"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    source_cache = {}

    def source(path, line, baseline):
        key = (path, baseline)
        if key not in source_cache:
            if baseline:
                result = subprocess.run(["git", "show", f"{BASE}:{path}"], cwd=ROOT, capture_output=True,
                                        encoding="utf-8", errors="replace", check=True)
                source_cache[key] = result.stdout.splitlines()
            else:
                source_cache[key] = (ROOT / path).read_text(encoding="utf-8-sig").splitlines()
        lines = source_cache[key]
        return re.sub(r"\s+", " ", lines[int(line) - 1].strip())

    with (ROOT / "logs/analysis-baseline/build-warnings.csv").open(encoding="utf-8-sig", newline="") as stream:
        baseline = list(csv.DictReader(stream))
    for item in baseline:
        item["source"] = source(item["path"], item["line"], True)
    text = re.sub(r"\x1b\[[0-9;]*m", "", arguments.log.read_text(encoding="utf-8-sig", errors="replace"))
    current = []
    pattern = re.compile(r"ArkTS:WARN File:\s*(.+):(\d+):(\d+)\s*\n([^\r\n]+)")
    for found in pattern.finditer(text):
        path, line, column, message = found.groups()
        path = Path(path).relative_to(ROOT).as_posix()
        current.append({"path": path, "line": int(line), "column": int(column), "message": message.strip(),
                        "source": source(path, line, False)})
    signature = lambda item: (item["message"], item["source"])
    old_count = collections.Counter(map(signature, baseline))
    new_count = collections.Counter(map(signature, current))
    new = new_count - old_count
    removed = old_count - new_count
    result = {"baselineCount": len(baseline), "currentCount": len(current), "comparison": "message + normalized source statement; path/line moves allowed",
              "newDiagnostics": [{"message": key[0], "source": key[1], "count": count} for key, count in new.items()],
              "removedDiagnostics": [{"message": key[0], "source": key[1], "count": count} for key, count in removed.items()],
              "current": current}
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "current"}, ensure_ascii=False, indent=2))
    return 0 if not new and len(baseline) == 764 else 1


if __name__ == "__main__":
    raise SystemExit(main())
