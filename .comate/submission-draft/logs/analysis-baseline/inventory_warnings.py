import collections
import csv
import json
import pathlib
import re

root = pathlib.Path(__file__).resolve().parent
data = (root / "build-full.log").read_bytes()
text = data.decode("utf-16") if data[:2] in (b"\xff\xfe", b"\xfe\xff") else data.decode("utf-8-sig")
lines = text.splitlines()
rows = []
for i, line in enumerate(lines):
    if "WARN" not in line:
        continue
    m = re.search(r"File: (.*):(\d+):(\d+)", line)
    msg = lines[i + 1].strip() if m and i + 1 < len(lines) else line.strip()
    rows.append({"log_line": i + 1, "file": m.group(1) if m else "", "source_line": m.group(2) if m else "", "column": m.group(3) if m else "", "message": msg})
with (root / "warning-inventory.csv").open("w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
counts = collections.Counter(r["message"] for r in rows)
summary = {"warning_records": len(rows), "file_diagnostics": sum(bool(r["file"]) for r in rows), "unique_file_diagnostics": len({(r["file"], r["source_line"], r["column"], r["message"]) for r in rows if r["file"]}), "messages": dict(counts), "scope": dict(collections.Counter("dependency" if "/oh_modules/" in r["file"] else "tracked-source" if r["file"] else "build-or-package" for r in rows))}
(root / "warning-summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(summary, indent=2, ensure_ascii=False))
