"""Stop only the explicitly authorized task emulator and retain closeout evidence."""
import hashlib
import json
import re
import shutil
import time
from pathlib import Path

from cml_evidence import ROOT, production_fingerprint, run_record, write_json

out = ROOT / "logs/verification-closeout-03"
out.mkdir(parents=True, exist_ok=True)
expected = "26307326248e8e874d1e2d8c3a4abf10e14008d5fd386b91682357a928f6f78e"
before = production_fingerprint()
if not (out / "fingerprint-before.json").exists():
    write_json(out / "fingerprint-before.json", before)
assert before["sha256"] == expected
hdc = shutil.which("hdc")
assert hdc
ps_prefix = ". 'D:/hongmengcup/Enter-HarmonyEnv.ps1'\n. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'\n"
process_query = "Get-CimInstance Win32_Process -Filter \"Name='Emulator.exe'\" | Where-Object { $_.ProcessId -in @(35092,30856) } | Select-Object ProcessId,ParentProcessId,ExecutablePath,CommandLine | ConvertTo-Json -Depth 3"

def processes(label):
    return run_record(out, label, ["powershell.exe", "-NoProfile", "-Command", ps_prefix + process_query])

stop_path = out / "stop-own-layout.json"
if stop_path.exists():
    # Resume read-only verification after the initial helper incorrectly treated
    # a retained HDC Offline row as a still-connected device. Do not stop twice.
    stop = json.loads(stop_path.read_text(encoding="utf-8"))
else:
    pre = processes("processes-before")
    assert pre["exit_code"] == 0
    assert 'CmlSpec7_Layout -instancePath D:/HCUP/cml-spec7/logs/verification-emulator/instances' in pre["stdout"]
    assert 'HarmonyCup_API23' in pre["stdout"]
    run_record(out, "targets-before", [hdc, "list", "targets", "-v"])
    for device, label in [("127.0.0.1:5555", "phone"), ("127.0.0.1:5557", "layout")]:
        run_record(out, label + "-display-before-stop", [hdc, "-t", device, "shell", "hidumper", "-s", "DisplayManagerService", "-a", "-a"])
        run_record(out, label + "-window-before-stop", [hdc, "-t", device, "shell", "hidumper", "-s", "WindowManagerService", "-a", "-a"])
    stop = run_record(out, "stop-own-layout", [
        "D:/HarmonyDev/DevEcoStudio-6.1.0/tools/emulator/Emulator.exe",
        "-stop", "CmlSpec7_Layout", "-instancePath",
        "D:/HCUP/cml-spec7/logs/verification-emulator/instances"], timeout=30)
assert stop["exit_code"] == 0 and not stop["timed_out"]
targets = None
for index in range(10):
    targets = run_record(out, "targets-final-" + str(index), [hdc, "list", "targets", "-v"])
    if not re.search(r"^127\.0\.0\.1:5557\s+TCP\s+Connected\b", targets["stdout"], re.M):
        break
    time.sleep(1)
post = processes("processes-final")
assert not re.search(r"^127\.0\.0\.1:5557\s+TCP\s+Connected\b", targets["stdout"], re.M), "Task emulator is still connected; do not claim stopped"
assert re.search(r"^127\.0\.0\.1:5555\s+TCP\s+Connected\b", targets["stdout"], re.M), "Shared main device must remain available"
assert re.search(r'"ProcessId":\s*30856\b', post["stdout"])
assert not re.search(r'"ProcessId":\s*35092\b', post["stdout"])
assert 'CmlSpec7_Layout' not in post["stdout"]

config_pre = json.loads((ROOT / "logs/verification-preparation-01/layout-config-copy.json").read_text(encoding="utf-8"))
config_now = {name: hashlib.sha256((Path(config_pre["source"]) / name).read_bytes()).hexdigest() for name in config_pre["files"]}
config_unchanged = all(config_now[name] == row["source_sha256"] for name, row in config_pre["files"].items())
after = production_fingerprint()
write_json(out / "fingerprint-after.json", after)
assert after["sha256"] == before["sha256"]
write_json(out / "closeout.json", {
    "source_sha256": after["sha256"], "source_unchanged": True,
    "own_layout_stopped": True, "own_initial_pid": 35092,
    "shared_main_alive": True, "shared_main_pid": 30856,
    "shared_instance_config_sha256": config_now, "shared_instance_config_unchanged": config_unchanged,
    "orientation_evidence": [
        "logs/verification-large-geometry-03/final-orientation-restored-action.json",
        "logs/verification-phone-rotation-03/test_D5_runtime_rotation_layout-rotation-restored-display.json",
        "logs/verification-closeout-03/phone-display-before-stop.json",
        "logs/verification-closeout-03/layout-display-before-stop.json"],
    "retained_instance_path": "logs/verification-emulator/instances/CmlSpec7_Layout",
    "instance_data_deleted": False,
    "hdc_offline_entry_retained": "127.0.0.1:5557" in targets["stdout"],
    "helper_correction": "First closeout assertion confused an HDC Offline row with Connected; original logs retained. Verified process 35092 absent, target not Connected, main 30856 and 5555 Connected. Stop was issued once."
})
assert config_unchanged, "Shared instance tiny configuration changed; report exact evidence"
print("Closeout verified: task emulator stopped, shared main alive, source and shared config unchanged")
