"""Rebuild only the derived command index from immutable, offset-aware raw records."""
from __future__ import annotations

import csv
import datetime
import hashlib
import json
import pathlib
import shutil

OUT = pathlib.Path(__file__).resolve().parent
ROOT = OUT.parents[2]
LOGS = ROOT / "logs"
INDEX = OUT / "command-index.csv"
LEGACY = OUT / "command-index-v1-mixed-timezones.csv"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


if not LEGACY.exists():
    shutil.copy2(INDEX, LEGACY)

raw_paths = sorted(LOGS.glob("analysis-baseline-r3-*.json"))
jsonl = LOGS / "analysis-baseline-r3-probe-commands.jsonl"
raw_paths.append(jsonl)
before_hashes = {p.name: sha256(p) for p in raw_paths}
rows = []


def append(record: dict, source: str, line: int | None = None) -> None:
    raw_utc = record["utc"]
    parsed = datetime.datetime.fromisoformat(raw_utc.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"Offset absent in {source}:{line}: {raw_utc!r}")
    utc = parsed.astimezone(datetime.timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")
    output = record.get("output", "")
    if isinstance(output, list):
        output = "\n".join(str(value) for value in output)
    command = record.get("command") or " ".join(record["args"])
    rows.append({"utc": utc, "label": record.get("label", ""), "command": command,
                 "exit_code": record.get("exit_code"),
                 "output_has_failure": bool(record.get("output_has_failure", "[Fail]" in output)),
                 "raw_record": source, "raw_line": line, "raw_utc": raw_utc})


for path in raw_paths[:-1]:
    record = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(record, dict) and record.get("command"):
        append(record, path.name)
for line_number, line in enumerate(jsonl.read_text(encoding="utf-8-sig").splitlines(), 1):
    if line.strip():
        append(json.loads(line), jsonl.name, line_number)
rows.sort(key=lambda r: (r["utc"], r["raw_record"], r["raw_line"] or 0))
with INDEX.open("w", encoding="utf-8-sig", newline="") as handle:
    writer = csv.DictWriter(handle, fieldnames=["utc", "label", "command", "exit_code",
                                               "output_has_failure", "raw_record", "raw_line", "raw_utc"])
    writer.writeheader()
    writer.writerows(rows)

after_hashes = {p.name: sha256(p) for p in raw_paths}
if before_hashes != after_hashes:
    raise RuntimeError("Raw records changed during index rebuild")
legacy_rows = list(csv.DictReader(LEGACY.open(encoding="utf-8-sig", newline="")))
if len(legacy_rows) != len(rows):
    raise AssertionError(f"Row count changed: {len(legacy_rows)} -> {len(rows)}")

audit = {"rebuilt_utc": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
         "time_rule": "Parse offset-aware raw utc with datetime.fromisoformat, convert to UTC, emit ISO8601 Z; raw_utc preserves original precision and offset",
         "raw_record_count": len(raw_paths), "raw_records_unchanged": before_hashes == after_hashes,
         "raw_sha256": after_hashes, "rows_before": len(legacy_rows), "rows_after": len(rows),
         "legacy_file": LEGACY.name, "legacy_sha256": sha256(LEGACY),
         "index_file": INDEX.name, "index_sha256": sha256(INDEX),
         "example_existing_app_click": next(r for r in rows if r["label"] == "existing-app-window-click")}
audit_path = OUT / "command-index-rebuild-audit.json"
audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")

manifest_path = OUT / "artifact-manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
entries = {entry["file"]: entry for entry in manifest}
for path in [INDEX, LEGACY, pathlib.Path(__file__).resolve(), audit_path]:
    entries[path.name] = {"file": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
for entry in entries.values():
    path = OUT / entry["file"]
    if path.is_file():
        entry.update(bytes=path.stat().st_size, sha256=sha256(path))
manifest_path.write_text(json.dumps(sorted(entries.values(), key=lambda entry: entry["file"]), ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({key: audit[key] for key in ["rows_before", "rows_after", "raw_record_count", "raw_records_unchanged", "legacy_sha256", "index_sha256", "example_existing_app_click"]}, ensure_ascii=False))
