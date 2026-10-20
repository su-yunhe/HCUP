"""Prepare a fresh dedicated synthetic emulator; never emits acceptance passes."""
import argparse
import os
from pathlib import Path
import time

from hypium import BY, UiDriver

from hypium_tests.evidence import BUNDLE, PREFS, ROOT, Evidence, digest, read_preferences, source_fingerprint, utc, write_json
from hypium_tests.test_restore_confirmation import RestoreConfirmationTests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--seed-fixture", action="store_true")
    parser.add_argument("--fresh", action="store_true", help="Explicitly wait for fresh privacy/onboarding instead of racing background home controls")
    args = parser.parse_args()
    out = Path(args.out).resolve()
    e = Evidence(out, args.device)
    before = source_fingerprint()
    hap = ROOT / "entry/build/default/outputs/default/entry-default-unsigned.hap"
    e.hdc("install", "-r", str(hap), timeout=60)
    os.chdir(out)
    driver = UiDriver.connect(device_sn=args.device)
    driver.set_implicit_wait_time(.3)
    helper = RestoreConfirmationTests("test_00_first_use_empty_local_and_cloud")
    helper.driver, helper.e = driver, e
    driver.start_app(BUNDLE, "EntryAbility")
    time.sleep(.8)
    consent = helper.require_text("同意并进入", "Fresh device privacy did not finish loading") if args.fresh else driver.find_component(BY.text("同意并进入"))
    if consent is not None:
        e.screen("fresh-privacy-screen")
        driver.click(consent)
    skip = helper.require_text("跳过", "Fresh device onboarding did not finish loading") if args.fresh else driver.find_component(BY.text("跳过"))
    if skip is not None:
        e.screen("fresh-onboarding-screen")
        driver.click(skip)
    helper.enter_webdav()
    toggle = helper.scroll_find("webdav_auto_sync_toggle", "DOWN")
    if toggle.isChecked():
        driver.click(toggle)
        time.sleep(.5)
    assert not helper.get("webdav_auto_sync_toggle").isChecked()
    e.receive(PREFS, out / "auto-sync-disabled.xml")
    assert read_preferences(out / "auto-sync-disabled.xml").get("webdav_autosync_enabled") == "0"
    e.screen("fresh-device-auto-sync-disabled")
    if args.seed_fixture:
        helper.import_local_fixture()
        e.screen("local-fixture-restored-through-existing-ui")
    assert before == source_fingerprint()
    write_json(out / "preparation.json", {"at": utc(), "device": args.device,
        "hap_sha256": digest(hap.read_bytes()), "source_unchanged": True,
        "ui_auto_sync_checked": False, "persisted_auto_sync": "0",
        "acceptance_status": "Preparation only; no R pass claims"})


if __name__ == "__main__":
    main()
