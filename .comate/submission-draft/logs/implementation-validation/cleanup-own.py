"""Post-run lease cleanup; never removes pre-existing forwards or application data."""
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess

base = Path(__file__).resolve().parent
result = json.loads((base / "selftest-09.json").read_text(encoding="utf-8"))
assert all(case["outcome"] == "pass" for case in result["cases"]), "Final test run is not fully passing"
commands = []


def run(args, name):
    command = [shutil.which("hdc"), *args]
    started = datetime.now(timezone.utc).isoformat()
    proc = subprocess.run(command, capture_output=True, timeout=30)
    output = (proc.stdout + proc.stderr).decode("utf-8", errors="replace")
    (base / (name + ".raw.log")).write_text(output, encoding="utf-8")
    commands.append({"command": command, "started": started, "exit_code": proc.returncode,
                     "raw_log": name + ".raw.log"})
    assert proc.returncode == 0 and "[Fail]" not in output, output
    return output


def maps(text):
    return {tuple(m) for m in re.findall(r"127\.0\.0\.1:5555\s+(tcp:\d+)\s+(tcp:\d+)\s+\[(Forward|Reverse)\]", text)}


initial = maps((base / "ports-before.raw.log").read_text(encoding="utf-8-sig"))
before = maps(run(["fport", "ls"], "ports-before-final-cleanup"))
owned = {m for m in before - initial if (m[2] == "Forward" and m[1] == "tcp:8012")
         or (m[2] == "Reverse" and m[0] == m[1] == "tcp:18165")}
for local, remote, kind in sorted(owned):
    message = run(["-t", "127.0.0.1:5555", "fport", "rm", local, remote], "cleanup-" + local.replace(":", "-"))
    assert "success" in message.lower(), message
after = maps(run(["fport", "ls"], "ports-after-final-cleanup"))
net = subprocess.run(["netstat", "-ano", "-p", "tcp"], capture_output=True, text=True, timeout=30)
relevant = [line for line in net.stdout.splitlines() if "127.0.0.1:18165" in line]
(base / "loopback-service-final.raw.log").write_text("\n".join(relevant), encoding="utf-8")
server_stopped = not any("LISTENING" in line.upper() for line in relevant)
display = run(["-t", "127.0.0.1:5555", "shell", "hidumper", "-s", "DisplayManagerService", "-a", "-a"], "environment-display-final")
density = re.search(r"\nDensity:\s+([0-9.]+)", display)
mode = re.search(r"activeModes<id, W, H, RS>:\s+([^\r\n]+)", display)
report = {"time": datetime.now(timezone.utc).isoformat(), "initial_mappings": sorted(initial),
          "own_mappings_removed": sorted(owned), "remaining_mappings": sorted(after),
          "preexisting_preserved": initial.issubset(after), "own_mappings_absent": not (owned & after),
          "loopback_service_stopped": server_stopped, "netstat_exit_code": net.returncode,
          "display_density": density.group(1) if density else None,
          "display_mode": mode.group(1) if mode else None, "commands": commands}
(base / "cleanup-final.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))
assert report["preexisting_preserved"] and report["own_mappings_absent"] and server_stopped
