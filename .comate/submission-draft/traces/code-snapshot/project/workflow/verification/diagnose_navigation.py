"""Fresh install + single UiDriver, no external dump between navigation actions."""
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from cml_evidence import ROOT, hdc_record, production_fingerprint, snapshot, write_json

out = ROOT / ("logs/" + (sys.argv[1] if len(sys.argv) > 1 else "verification-navigation-diagnosis-02"))
out.mkdir(exist_ok=False)
old = json.loads((ROOT / "logs/verification-phone-preview-02/install-manifest.json").read_text(encoding="utf-8"))
source = production_fingerprint()
assert source["sha256"] == old["source_sha256"]
assert hashlib.sha256(Path(old["hap_path"]).read_bytes()).hexdigest() == old["hap_sha256"]
write_json(out / "fingerprint-before.json", source)
install = hdc_record(out, "install", "install", "-r", old["hap_path"])
assert install["exit_code"] == 0 and "success" in install["stdout"].lower()
write_json(out / "install-manifest.json", {**old, "install_output": install["stdout"], "install_exit_code": install["exit_code"]})
os.chdir(out)
from hypium import UiDriver, BY
driver = UiDriver.connect(device_sn="127.0.0.1:5555")
driver.set_implicit_wait_time(0.2)
steps = []


def note(label, **kwargs):
    row = {"label": label, "time": time.time(), **kwargs}
    steps.append(row)
    write_json(out / "steps.json", steps)
    print(json.dumps(row, ensure_ascii=False), flush=True)


def find(key):
    return driver.find_component(BY.key(key))


driver.stop_app("com.joker.coolmall")
driver.start_app("com.joker.coolmall", page_name="EntryAbility", wait_time=2)
for _ in range(10):
    me = find("main_tab_me")
    if me:
        break
    if driver.find_component(BY.text("青商城")):
        for text in ("不允许", "禁止"):
            target = driver.find_component(BY.text(text))
            if target:
                driver.click(target)
                driver.wait(0.5)
                confirm = driver.find_component(BY.text("确定"))
                if confirm:
                    driver.click(confirm)
                note("permission", text=text)
                break
    driver.press_back()
    driver.wait(0.6)
else:
    raise AssertionError("Cannot return to this app from permission settings")
driver.click(me)
driver.wait(0.8)
entry = find("me_login_entry")
assert entry is not None
driver.click(entry)
driver.wait(1)
first = find("auth_login_page")
logo = find("auth_login_logo")
note("first_entry_after_1s", page=first is not None, logo=logo is not None)
driver.capture_screen(str(out / "first-entry-native.jpeg"))
driver.press_back()
driver.wait(1)
entry = find("me_login_entry")
note("returned_after_1s", entry=entry is not None)
assert entry is not None
driver.click(entry)
driver.wait(1.2)
second = find("auth_login_page")
logo = find("auth_login_logo")
note("reentry_after_1_2s", page=second is not None, logo=logo is not None)
driver.capture_screen(str(out / "reentry-native.jpeg"))
# All navigation observations are complete before the external CLI dump.
snapshot(out, "after-critical-actions")
after = production_fingerprint()
write_json(out / "fingerprint-after.json", after)
assert after["sha256"] == source["sha256"]
note("complete", source_unchanged=True)
