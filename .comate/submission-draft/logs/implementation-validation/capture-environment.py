from datetime import datetime, timezone
import importlib.metadata
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys

root = Path(__file__).resolve().parent
commands = []
for label, args in [
    ("hdc-version", ["-v"]),
    ("software", ["-t", "127.0.0.1:5555", "shell", "param", "get", "const.product.software.version"]),
    ("model", ["-t", "127.0.0.1:5555", "shell", "param", "get", "const.product.model"]),
    ("api", ["-t", "127.0.0.1:5555", "shell", "param", "get", "const.ohos.apiversion"]),
    ("dpi", ["-t", "127.0.0.1:5555", "shell", "param", "get", "persist.sys.dpi"]),
    ("window-environment", ["-t", "127.0.0.1:5555", "shell", "hidumper", "-s", "WindowManagerService", "-a", "-a"]),
]:
    command = [shutil.which("hdc"), *args]
    started = datetime.now(timezone.utc).isoformat()
    result = subprocess.run(command, capture_output=True, timeout=30)
    raw = result.stdout + result.stderr
    target = root / ("environment-" + label + ".raw.log")
    target.write_bytes(raw)
    commands.append({"command": command, "started": started, "exit_code": result.returncode,
                     "raw_log": target.name, "output": raw.decode("utf-8", errors="replace").strip() if label != "window-environment" else "See raw log"})
report = {"time": datetime.now(timezone.utc).isoformat(), "host": platform.platform(),
          "python": sys.version, "python_path": sys.executable,
          "hypium": importlib.metadata.version("hypium"), "cryptography": importlib.metadata.version("cryptography"),
          "device": "127.0.0.1:5555", "commands": commands}
(root / "environment.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
