"""Continue a freshly installed round through observed real UI, collecting raw evidence."""
import argparse
import json
import os
from pathlib import Path
import time

from cml_evidence import ROOT, production_fingerprint, snapshot, write_json

parser = argparse.ArgumentParser()
parser.add_argument("--out", type=Path, required=True)
parser.add_argument("--device", required=True)
parser.add_argument("--label", required=True)
parser.add_argument("action", choices=["click-id", "click-text", "back", "snapshot", "rotate", "login-path"])
parser.add_argument("target", nargs="?")
args = parser.parse_args()
out = args.out.resolve()
out.relative_to(ROOT / "logs")
manifest = json.loads((out / "install-manifest.json").read_text(encoding="utf-8"))
before = production_fingerprint()
if manifest["source_sha256"] != before["sha256"] or manifest["device"] != args.device:
    raise RuntimeError("No matching frozen-source fresh installation for this action")
os.chdir(out)
from hypium import UiDriver, BY
driver = UiDriver.connect(device_sn=args.device)
driver.set_implicit_wait_time(3)
record = {"action": args.action, "target": args.target, "device": args.device}
try:
    if args.action in ("click-id", "click-text"):
        selector = BY.key(args.target) if args.action == "click-id" else BY.text(args.target)
        component = driver.find_component(selector)
        if component is None:
            raise AssertionError(f"Real observed target absent: {args.target}")
        record["target_bounds"] = str(component.getBounds())
        driver.click(component)
    elif args.action == "back":
        driver.press_back()
    elif args.action == "rotate":
        from hypium.model.basic_data_type import DisplayRotation
        record["previous_rotation"] = str(driver.get_display_rotation())
        driver.set_display_rotation(DisplayRotation(int(args.target)))
    elif args.action == "login-path":
        record["steps"] = []
        # Only the observed permission sheet for this named application is
        # handled; recording is not a precondition for login/local reading.
        app_label = driver.find_component(BY.text("青商城"))
        if app_label:
            for text in ("不允许", "禁止"):
                component = driver.find_component(BY.text(text))
                if component:
                    driver.click(component)
                    record["steps"].append({"permission": text})
                    time.sleep(0.3)
                    confirm = driver.find_component(BY.text("确定"))
                    if confirm:
                        driver.click(confirm)
                        record["steps"].append({"permission": "确定"})
                    time.sleep(0.8)
                    break
        for key in ("main_tab_me", "me_login_entry"):
            component = driver.find_component(BY.key(key))
            if key == "main_tab_me":
                for _ in range(4):
                    if component is not None:
                        break
                    snapshot(out, args.label + "-permission-return-" + str(_))
                    driver.press_back()
                    record["steps"].append({"permission_return": "system_back"})
                    time.sleep(0.5)
                    component = driver.find_component(BY.key(key))
            if component is None:
                snapshot(out, args.label + "-entry-failure")
                raise AssertionError(f"Normal login path absent: {key}")
            record["steps"].append({"key": key, "bounds": str(component.getBounds())})
            driver.click(component)
            time.sleep(0.6)
        if driver.find_component(BY.key("auth_login_page")) is None:
            raise AssertionError("Login main absent after actual My-page entry")
    time.sleep(0.8)
    snapshot(out, args.label)
    record["status"] = "completed"
finally:
    after = production_fingerprint()
    write_json(out / (args.label + "-source-after.json"), after)
    record["source_unchanged"] = after["sha256"] == before["sha256"]
    write_json(out / (args.label + "-action.json"), record)
    if not record["source_unchanged"]:
        raise RuntimeError("Production sources changed; invalidate this evidence")
