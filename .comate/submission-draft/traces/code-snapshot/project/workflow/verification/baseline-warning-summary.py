"""Classify retained compiler diagnostic occurrences without suppressing warnings."""
from pathlib import Path
import collections
import hashlib
import json
import re

root = Path(__file__).resolve().parents[2]
raw = root / "logs/analysis-baseline/build-full-raw.txt"
content = raw.read_text(encoding="utf-8-sig")
diagnostics = [{"location": location.strip(), "message": message.strip(),
                "source": "dependency" if "/oh_modules/" in location else "project"}
               for location, message in re.findall(r"ArkTS:WARN File: ([^\n]+)\n([^\n]+)", content)]
summary = {"raw_log": str(raw.relative_to(root)), "raw_sha256": hashlib.sha256(raw.read_bytes()).hexdigest(),
           "arkts_file_diagnostic_occurrences": len(diagnostics),
           "arkts_unique_location_message_pairs": len({(row["location"], row["message"]) for row in diagnostics}),
           "arkts_messages": dict(collections.Counter(row["message"] for row in diagnostics)),
           "arkts_sources": dict(collections.Counter(row["source"] for row in diagnostics)),
           "resource_conflict_occurrences": len(re.findall(r"Warning: .* conflict, first declared", content)),
           "resource_conflicting_names": dict(collections.Counter(re.findall(r"Warning: '([^']+)' conflict, first declared", content))),
           "duplicate_filename_warning_occurrences": content.count("Duplicate file names detected"),
           "missing_sourceMapsPath_warning_occurrences": content.count("Property 'sourceMapsPath' not found"),
           "missing_signing_config_warning_occurrences": content.count("No signingConfig found"),
           "diagnostics": diagnostics}
target = root / "logs/analysis-baseline/warning-summary.json"
target.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in summary.items() if k != "diagnostics"}, ensure_ascii=False, indent=2))
