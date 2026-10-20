"""Semantic compiler-warning comparison; line/column shifts are not new warnings."""
from collections import Counter
import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("--round", type=Path, required=True)
args = parser.parse_args()
out = args.round.resolve()
out.relative_to(ROOT / "logs")
baseline = json.loads((ROOT / "logs/analysis-baseline/warning-summary.json").read_text(encoding="utf-8"))
content = "\n".join((out / name).read_text(encoding="utf-8-sig") for name in ("build.stdout.txt", "build.stderr.txt"))
content = re.sub(r"\x1b\[[0-9;]*m", "", content)
rows = [{"location": location.strip(), "message": message.strip()} for location, message in re.findall(r"ArkTS:WARN File: ([^\n]+)\n([^\n]+)", content)]


def semantic(row):
    path = re.sub(r":\d+:\d+$", "", row["location"]).replace("\\", "/").lower()
    return path, row["message"]


old = Counter(semantic(row) for row in baseline["diagnostics"])
new = Counter(semantic(row) for row in rows)
result = {
    "comparison": "path + exact warning message + occurrence count; ignore source line/column shifts",
    "arkts_occurrences_before": sum(old.values()), "arkts_occurrences_after": sum(new.values()),
    "new_semantic_diagnostics": [{"path": key[0], "message": key[1], "count": count} for key, count in (new - old).items()],
    "missing_semantic_diagnostics": [{"path": key[0], "message": key[1], "count": count} for key, count in (old - new).items()],
    "resources_before": baseline["resource_conflicting_names"],
    "resources_after": dict(Counter(re.findall(r"Warning: '([^']+)' conflict, first declared", content))),
    "other_warnings": {
        "duplicate_file_names": content.count("Duplicate file names detected"),
        "sourceMapsPath": content.count("Property 'sourceMapsPath' not found"),
        "missing_signing": content.count("No signingConfig found"),
    },
    "diagnostics": rows,
    "raw_log_sha256": {name: hashlib.sha256((out / name).read_bytes()).hexdigest() for name in ("build.stdout.txt", "build.stderr.txt")},
}
(out / "warning-semantic-comparison.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps({key: value for key, value in result.items() if key not in {"diagnostics", "resources_before", "resources_after"}}, ensure_ascii=False))
