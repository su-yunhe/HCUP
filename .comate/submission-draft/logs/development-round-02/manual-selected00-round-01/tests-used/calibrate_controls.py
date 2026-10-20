"""Explicit physical gesture/OS controls calibration on the assigned emulator."""
from __future__ import annotations
import argparse
import os
import time
from hypium import BY, UiDriver
from hypium_tests.evidence import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--inspect-network", action="store_true")
    args = parser.parse_args()
    e = Evidence(ROOT / "logs/development-round-01" / args.run_name)
    source = source_fingerprint()
    write_json(e.folder / "source-before.json", source)
    os.chdir(e.folder)
    hap = ROOT / "entry/build/default/outputs/default/entry-default-unsigned.hap"
    e.hdc("install", "-r", str(hap), timeout=60)
    write_json(e.folder / "hap-install.json", {"at": utc(), "hap_sha256": digest(hap.read_bytes())})
    driver = UiDriver.connect(device_sn=DEVICE)
    driver.set_implicit_wait_time(.2)
    driver.stop_app(BUNDLE)
    driver.start_app(BUNDLE, "EntryAbility")
    driver.click(BY.key("settings_entry_button"))
    driver.click(BY.key("settings_section_sync"))
    width, height = driver.get_display_size()
    for _ in range(7):
        restore = driver.find_component(BY.key("webdav_restore_button"))
        if restore is not None and restore.getBounds().bottom < height * .94:
            break
        driver.swipe("UP", distance=40)
    driver.click(restore)
    time.sleep(.6)
    e.screen("physical-before")
    width, height = driver.get_display_size()
    e.hdc("shell", "uitest", "uiInput", "swipe", "2", str(height // 2), str(int(width * .4)), str(height // 2), "1000")
    time.sleep(.6)
    e.screen("physical-after")
    write_json(e.folder / "physical-gesture-result.json", {"at": utc(), "start": [2, height // 2],
        "end": [int(width * .4), height // 2],
        "dialog_present": driver.find_component(BY.key("webdav_restore_confirm_dialog")) is not None})
    if args.inspect_network:
        driver.swipe("DOWN", distance=60, start_point=(int(width * .88), 2), swipe_time=.4)
        time.sleep(.7)
        tree = e.screen("control-center")
        print([{k: a.get(k) for k in ("text", "id", "type", "checked", "bounds", "description")}
               for a in flatten(tree) if a.get("text") or a.get("checked") == "true"])
    after = source_fingerprint()
    write_json(e.folder / "source-after.json", after)
    assert after == source


if __name__ == "__main__":
    main()
