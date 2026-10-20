"""Observed-state baseline actions and raw device snapshots; no app source changes."""
from pathlib import Path
from datetime import datetime, timezone
import json
import shutil
import subprocess
import sys
import time

from hypium import UiDriver, BY

ROOT = Path(__file__).resolve().parents[2]
SN = "127.0.0.1:5555"
label, *action = sys.argv[1:]
record = {"timestamp_utc": datetime.now(timezone.utc).isoformat(), "device": SN, "action": action, "commands": []}
prefix = ROOT / "traces" / "analysis-baseline" / label

def run(*args):
    command = [shutil.which("hdc"), "-t", SN, *args]
    result = subprocess.run(command, capture_output=True, timeout=30)
    row = {"command": command, "exit_code": result.returncode,
           "stdout": result.stdout.decode("utf-8", errors="replace"),
           "stderr": result.stderr.decode("utf-8", errors="replace")}
    record["commands"].append(row)
    if result.returncode or "[Fail]" in row["stdout"] or "error:" in row["stdout"]:
        raise RuntimeError(row)

def nodes(node):
    yield node["attributes"]
    for child in node.get("children", []):
        yield from nodes(child)

try:
    if action:
        driver = UiDriver.connect(device_sn=SN)
        driver.set_implicit_wait_time(2)
        if action[0] == "click-text":
            target = driver.find_component(BY.text(action[1]))
            if target is None:
                raise AssertionError(f"Observed target absent: {action[1]!r}")
            record["target_bounds"] = str(target.getBounds())
            driver.click(target)
        elif action[0] == "back":
            driver.press_back()
        elif action[0] == "restart":
            driver.stop_app("com.joker.coolmall")
            driver.start_app("com.joker.coolmall", page_name="EntryAbility", wait_time=2)
        else:
            raise ValueError(action)
        time.sleep(1.5)
    remote = f"/data/local/tmp/cml-spec7-{label}"
    run("shell", "uitest", "dumpLayout", "-p", remote + ".json")
    run("file", "recv", remote + ".json", str(prefix.with_suffix(".ui.json")))
    run("shell", "snapshot_display", "-f", remote + ".jpeg")
    run("file", "recv", remote + ".jpeg", str(prefix.with_suffix(".jpeg")))
    tree = json.loads(prefix.with_suffix(".ui.json").read_text(encoding="utf-8"))
    flat = list(nodes(tree))
    record["texts"] = [a.get("text") for a in flat if a.get("text")]
    summary = [{k: a.get(k) for k in ["text", "type", "bounds", "id", "bundleName", "backgroundColor"]}
               for a in flat if a.get("text") or a.get("bundleName")]
    prefix.with_suffix(".summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    record["status"] = "completed"
except Exception as error:
    record["status"] = "error"
    record["error"] = repr(error)
    raise
finally:
    (ROOT / "logs" / "analysis-baseline" / (label + "-action.json")).write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
