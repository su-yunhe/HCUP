"""Bounded OS-airplane toggle experiment; restore initial state and report facts."""
from __future__ import annotations
import os
import time
from hypium import BY, UiDriver
from hypium_tests.evidence import *


def main():
    e = Evidence(ROOT / "logs/development-round-01/network-ui-probe")
    os.chdir(e.folder)
    driver = UiDriver.connect(device_sn=DEVICE)
    driver.set_implicit_wait_time(.3)
    key = "transition_toggleair_plane"
    control = driver.find_component(BY.key(key))
    if control is None:
        raise RuntimeError("Expected observed airplane tile in open control center")
    e.screen("airplane-before")
    e.hdc("shell", "ifconfig")
    before = e.hdc("shell", "hidumper", "-s", "NetConnManager")
    e.hdc("shell", "netstat", "-rn")
    changed = False
    try:
        driver.click(control)
        changed = True
        time.sleep(2)
        e.screen("airplane-on")
        e.hdc("shell", "ifconfig")
        on = e.hdc("shell", "hidumper", "-s", "NetConnManager")
        e.hdc("shell", "hidumper", "-s", "EthernetManager")
        e.hdc("shell", "netstat", "-rn")
        write_json(e.folder / "result.json", {"at": utc(), "before":before["stdout"],
            "airplane_on":on["stdout"], "offline_proven": "IsAvailable: 1" not in on["stdout"] and "IsAvailable: 0" in on["stdout"],
            "note":"Airplane UI alone is not proof; use actual connection/interface/route state"})
    finally:
        if changed:
            driver.click(BY.key(key))
            time.sleep(2)
            e.screen("airplane-restored")
            e.hdc("shell", "ifconfig")
            e.hdc("shell", "hidumper", "-s", "NetConnManager")
            e.hdc("shell", "netstat", "-rn")
        driver.press_back()
    print("OS airplane probe recorded and original setting restored")


if __name__ == "__main__":
    main()
