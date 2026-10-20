"""Capture commands against only this task's isolated emulator."""
import json
import pathlib
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

log_dir = pathlib.Path(__file__).resolve().parent
label, *args = sys.argv[1:]
args = [str(pathlib.Path(a)) if re.match(r"^[A-Za-z]:/", a) else a for a in args]
cmd = [shutil.which("hdc"), "-t", "127.0.0.1:11241", *args]
start = datetime.now(timezone.utc).isoformat()
try:
    r = subprocess.run(cmd, capture_output=True, timeout=90)
    stdout = r.stdout.decode("utf-8", "replace")
    stderr = r.stderr.decode("utf-8", "replace")
    code = r.returncode
except subprocess.TimeoutExpired as e:
    stdout = (e.stdout or b"").decode("utf-8", "replace")
    stderr = (e.stderr or b"").decode("utf-8", "replace") + "\nTIMEOUT 90s"
    code = 124
(log_dir / (label + ".stdout.log")).write_text(stdout, encoding="utf-8")
(log_dir / (label + ".stderr.log")).write_text(stderr, encoding="utf-8")
record = {"start_utc": start, "end_utc": datetime.now(timezone.utc).isoformat(), "command": cmd,
          "exit_code": code, "stdout": label + ".stdout.log", "stderr": label + ".stderr.log"}
(log_dir / (label + ".command.json")).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(record, ensure_ascii=False))
print(stdout[:18000])
print(stderr[:3000])
sys.exit(code)
