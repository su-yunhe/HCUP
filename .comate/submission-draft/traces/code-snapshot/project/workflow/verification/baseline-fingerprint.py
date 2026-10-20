"""Record only this task's production inputs and Git state for baseline evidence."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[2]
tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
tracked = [p for p in tracked if p]
paths = set(tracked)
for folder in ["AppScope", "entry", "core", "feature", "hvigor"]:
    for directory, subdirs, files in os.walk(root / folder):
        subdirs[:] = [part for part in subdirs if part not in {"build", "oh_modules", ".hvigor", ".preview"}]
        for filename in files:
            paths.add((Path(directory) / filename).relative_to(root).as_posix())
for path in root.iterdir():
    if path.is_file() and path.suffix in {".json", ".json5", ".ts", ".properties", ".bat"}:
        paths.add(path.name)
rows = []
for relative in sorted(paths):
    path = root / relative
    rows.append({"path": relative, "tracked": relative in tracked,
                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None})
result = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "root": str(root),
          "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root).decode().strip(),
          "status": subprocess.check_output(["git", "status", "--short"], cwd=root).decode(),
          "inputs": rows}
target = root / "logs" / "analysis-baseline" / sys.argv[1]
target.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Saved {len(rows)} input fingerprints to {target}")
