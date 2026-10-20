"""Local observation helper. Does not modify application source or import external data."""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import subprocess
import sys
import time
from datetime import datetime

ROOT = pathlib.Path(__file__).resolve().parents[2]
LOG = pathlib.Path(__file__).resolve().parent
os.chdir(LOG)
sys.path.insert(0, str(ROOT / "test-harness"))
from harness.device import find_hdc, select_device
from hypium import BY, UiDriver


def record(action: str, **data):
    item = {"time": datetime.now().astimezone().isoformat(), "action": action, **data}
    with (LOG / "device-actions.jsonl").open("a", encoding="utf-8") as output:
        output.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(json.dumps(item, ensure_ascii=False), flush=True)


def hdc(*args):
    cmd = [find_hdc(), "-t", "127.0.0.1:5555", *args]
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
    record("command", command=cmd, exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
    if result.returncode:
        raise RuntimeError(f"hdc failed: {result.returncode}")
    return result.stdout


def snapshot(name):
    for suffix, command in [("json", "dumpLayout"), ("png", "screenCap")]:
        remote = f"/data/local/tmp/vg-spec8-{name}.{suffix}"
        hdc("shell", "uitest", command, "-p", remote)
        hdc("file", "recv", remote, str(LOG / f"{name}.{suffix}"))


def walk(node):
    yield node.get("attributes", {})
    for child in node.get("children", []):
        yield from walk(child)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["snapshot", "click", "swipe", "back", "summary", "replace-field", "field-status", "toggle-status", "click-coordinate", "configure-sentinel", "restore-observe"])
    parser.add_argument("--name", default="observation")
    parser.add_argument("--text")
    parser.add_argument("--index", type=int, default=0)
    parser.add_argument("--direction", default="up")
    parser.add_argument("--value", default="")
    parser.add_argument("--x", type=int)
    parser.add_argument("--y", type=int)
    parser.add_argument("--wait", type=float, default=.5)
    args = parser.parse_args()
    if args.action == "summary":
        data = json.loads((LOG / f"{args.name}.json").read_text(encoding="utf-8-sig"))
        for attributes in walk(data):
            if attributes.get("text") or attributes.get("clickable") == "true":
                print({key: attributes.get(key) for key in ["text", "type", "id", "bounds", "enabled", "clickable", "checked"]})
        return
    select_device("127.0.0.1:5555")
    if args.action == "snapshot":
        snapshot(args.name)
        return
    driver = UiDriver.connect(device_sn="127.0.0.1:5555")
    driver.set_implicit_wait_time(1)
    if args.action == "click":
        component = driver.find_component(BY.text(args.text))
        if component is None:
            record("find_missing", text=args.text)
            raise AssertionError(f"Missing text: {args.text}")
        record("click_text", text=args.text, enabled=component.isEnabled(), bounds=str(component.getBounds()))
        driver.click(component)
    elif args.action == "click-coordinate":
        record("click_coordinate", x=args.x, y=args.y)
        driver.click((args.x, args.y))
    elif args.action == "swipe":
        record("swipe", direction=args.direction)
        driver.swipe(args.direction.upper())
    elif args.action == "back":
        record("press_back")
        driver.press_back()
    elif args.action == "replace-field":
        fields = driver.find_all_components(BY.type("TextInput")) or []
        component = fields[args.index]
        # Never print existing text; only sentinel values passed by this task.
        record("replace_field", index=args.index, existing_nonempty=bool(component.getText()), new_value=args.value)
        component.clearText()
        driver.input_text(component, args.value)
    elif args.action == "configure-sentinel":
        sentinel_values = ["http://127.0.0.1:18988/dav/", "vg_spec8_observer", "sentinel-not-a-secret", "sentinel-sync-password", "/vg_spec8_observation"]
        for index, value in enumerate(sentinel_values):
            fields = driver.find_all_components(BY.type("TextInput")) or []
            if len(fields) != 5:
                raise AssertionError(f"Expected 5 config fields, got {len(fields)}")
            component = fields[index]
            component.clearText()
            driver.input_text(component, value)
            driver.press_back()
            record("configure_sentinel_field", index=index, value=value)
        record("configuration_replaced", existing_configuration="present; credentials not recorded; not reused", persisted=False)
    elif args.action == "restore-observe":
        requests = LOG / "mock-requests.jsonl"
        def request_count():
            return len(requests.read_text(encoding="utf-8").splitlines()) if requests.exists() else 0
        component = driver.find_component(BY.text("从云端恢复"))
        if component is None:
            raise AssertionError("Restore entry missing")
        bounds = component.getBounds()
        before = request_count()
        record("restore_observation_begin", request_count=before, continue_ever_clicked=False)
        driver.click(component)
        time.sleep(.4)
        snapshot("06-first-restore-inflight")
        data = json.loads((LOG / "06-first-restore-inflight.json").read_text(encoding="utf-8-sig"))
        attributes = list(walk(data))
        texts = [item.get("text") for item in attributes if item.get("text")]
        busy_buttons = [{key: item.get(key) for key in ["text", "enabled", "bounds", "id"]} for item in attributes if item.get("type") == "Button"]
        immediate_count = request_count()
        record("first_restore_inflight", request_count=immediate_count, dialog_cancel_visible="取消" in texts, dialog_continue_visible="继续" in texts, buttons=busy_buttons)
        # Repeat click on the same observed restore entry coordinates while busy.
        driver.click(((bounds.left + bounds.right) // 2, (bounds.top + bounds.bottom) // 2))
        record("repeat_restore_coordinate_while_busy", request_count=request_count())
        time.sleep(.4)
        snapshot("07-repeat-click-inflight")
        deadline = time.monotonic() + 40
        while time.monotonic() < deadline:
            component = driver.find_component(BY.text("从云端恢复"))
            if component is not None:
                break
            time.sleep(.5)
        snapshot("08-restore-result")
        result = {"initial_request_count": before, "request_count_at_first_ui_capture": immediate_count, "final_request_count": request_count(), "continue_ever_clicked": False, "cancel_visible_after_first_click": "取消" in texts, "continue_visible_after_first_click": "继续" in texts, "busy_buttons": busy_buttons, "first_confirmation_status": "pass" if "取消" in texts and "继续" in texts else "fail", "no_request_before_continue_status": "pass" if request_count() == before else "fail", "scope": "First restore activation; cancellation steps not executed because first confirmation absent"}
        (LOG / "restore-observation-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        record("restore_observation_result", **result)
        sys.exit(0 if result["first_confirmation_status"] == "pass" and result["no_request_before_continue_status"] == "pass" else 1)
    elif args.action == "field-status":
        fields = driver.find_all_components(BY.type("TextInput")) or []
        record("field_status", count=len(fields), fields=[{"index": index, "nonempty": bool(component.getText()), "bounds": str(component.getBounds())} for index, component in enumerate(fields)])
        return
    elif args.action == "toggle-status":
        fields = driver.find_all_components(BY.type("Toggle")) or []
        record("toggle_status", count=len(fields), fields=[{"index": index, "bounds": str(component.getBounds()), "text": component.getText()} for index, component in enumerate(fields)])
        return
    driver.wait(args.wait)
    if args.name != "none":
        snapshot(args.name)


if __name__ == "__main__":
    main()
