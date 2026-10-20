"""Run and retain one explicit HDC baseline command (including misleading exit=0 failures)."""
from datetime import datetime, timezone
from pathlib import Path
import json
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parents[2]
label, *args = sys.argv[1:]
command = [shutil.which("hdc"), *args]
result = subprocess.run(command, capture_output=True, timeout=90)
record = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "command": command,
          "exit_code": result.returncode,
          "stdout": result.stdout.decode("utf-8", errors="replace"),
          "stderr": result.stderr.decode("utf-8", errors="replace")}
prefix = root / "logs" / "analysis-baseline" / label
prefix.with_suffix(".json").write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
prefix.with_suffix(".stdout.txt").write_bytes(result.stdout)
prefix.with_suffix(".stderr.txt").write_bytes(result.stderr)
print(json.dumps({key: value for key, value in record.items() if key not in {"stdout", "stderr"}}, ensure_ascii=False))
print(record["stdout"][:14000])
print(record["stderr"][:2000])
sys.exit(result.returncode)
