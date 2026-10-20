"""Parse raw current warnings and compare message counts to local baseline."""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[2]
evidence = Path(sys.argv[1]).resolve()
raw = evidence / "build-raw.log"
lines = raw.read_text(encoding="utf-8-sig", errors="replace").splitlines()
diagnostics = []
other = []
for index, original in enumerate(lines):
    line = re.sub(r"\x1b\[[0-9;]*m", "", original)
    match = re.search(r"WARN File: (.+):(\d+):(\d+)\s*$", line)
    if match:
        source = Path(match[1])
        try:
            filename = source.relative_to(root).as_posix()
        except ValueError:
            filename = str(source)
        message = lines[index + 1].strip() if index + 1 < len(lines) else ""
        diagnostics.append(dict(raw_log_line=index+1, path=filename, line=int(match[2]),
                                column=int(match[3]), message=message))
    elif "WARN" in line and "warning" not in line.lower():
        other.append(dict(raw_log_line=index+1, message=line))
baseline = json.loads((root / "logs/baseline-20261016/warnings-full.json").read_text(encoding="utf-8-sig"))
before = Counter(item["message"] for item in baseline["source_diagnostics"])
after = Counter(item["message"] for item in diagnostics)
before_files = Counter((item["path"], item["message"]) for item in baseline["source_diagnostics"])
after_files = Counter((item["path"], item["message"]) for item in diagnostics)
summary = dict(source_diagnostics=len(diagnostics), baseline_source_diagnostics=sum(before.values()),
               message_counts=dict(after), increased_message_counts=dict(after-before),
               decreased_message_counts=dict(before-after),
               added_file_message_counts=[dict(path=key[0],message=key[1],count=count) for key,count in (after_files-before_files).items()],
               removed_file_message_counts=[dict(path=key[0],message=key[1],count=count) for key,count in (before_files-after_files).items()],
               raw_log_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
               comparison_note="Counts do not establish absence of newly introduced individual warnings; inspect changed-file diagnostics and source mapping too.")
(evidence / "warnings-full.json").write_text(json.dumps(dict(source_diagnostics=diagnostics,other_warning_lines=other), ensure_ascii=False,indent=2),encoding="utf-8")
(evidence / "warnings-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False,indent=2))
