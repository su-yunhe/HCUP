"""Baseline preparation only; never emits R01-R28 pass labels."""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import time
from pathlib import Path

from hypium import BY, UiDriver

from hypium_tests.evidence import (BUNDLE, DEVICE, ROOT, Evidence, flatten,
                                   read_preferences, source_fingerprint, utc, write_json)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--isolate", action="store_true")
    parser.add_argument("--inspect-import", action="store_true")
    parser.add_argument("--seed-ui", action="store_true")
    parser.add_argument("--complete-import", action="store_true")
    parser.add_argument("--finish-fixture", action="store_true")
    parser.add_argument("--confirm-fixture", action="store_true")
    args = parser.parse_args()
    out = ROOT / "logs/development-round-01/prepare"
    e = Evidence(out)
    write_json(out / "preparation-source-start.json", source_fingerprint())
    os.chdir(out)
    driver = UiDriver.connect(device_sn=DEVICE)
    driver.set_implicit_wait_time(.5)
    if args.isolate:
        # Explicitly install the known, previously built baseline before experiments.
        hap = ROOT / "entry/build/default/outputs/default/entry-default-unsigned.hap"
        e.hdc("install", str(hap), timeout=60)
        driver.start_app(BUNDLE, "EntryAbility")
        time.sleep(1)
        gear = driver.find_component(BY.text("⚙"))
        if gear is not None:
            driver.click(gear)
            time.sleep(.4)
            driver.click(BY.text("WebDAV 配置"))
            time.sleep(.4)
        for attempt in range(8):
            label = driver.find_component(BY.text("启用自动同步"))
            if label is not None:
                break
            driver.swipe("DOWN", distance=55)
            time.sleep(.3)
        label = driver.find_component(BY.text("启用自动同步"))
        if label is None:
            raise AssertionError("Cannot find actual auto-sync row")
        label_bounds = label.getBounds()
        toggles = driver.find_all_components(BY.type("Toggle")) or []
        toggle = min(toggles, key=lambda c: abs(c.getBounds().top - label_bounds.top))
        if toggle.isChecked():
            driver.click(toggle)
            time.sleep(.8)
        if toggle.isChecked():
            raise AssertionError("Auto sync remained checked")
        e.screen("auto-sync-isolated")
        # Verify actual persisted value, not selected=false or screenshot color.
        from hypium_tests.evidence import PREFS
        e.receive(PREFS, out / "autosync-off.xml")
        prefs = read_preferences(out / "autosync-off.xml")
        matches = {k: v for k, v in prefs.items() if "auto" in k.lower()}
        write_json(out / "auto-sync-verified.json", {"at": utc(), "ui_checked": toggle.isChecked(), "prefs": matches})
        if not any(v in ("0", "false") for k, v in matches.items() if "enabled" in k):
            raise AssertionError("Auto-sync false not found in actual Preferences")
    if args.inspect_import:
        driver.click(BY.text("←"))
        driver.click(BY.text("备份与恢复"))
        e.screen("backup-ui")
        driver.click(BY.text("导入"))
        time.sleep(1)
        tree = e.screen("import-picker")
        print(json.dumps([a for a in flatten(tree) if a.get("text")], ensure_ascii=False))
    if args.seed_ui:
        from hypium_tests.evidence import local_fixture
        fixture = out / "vg-spec1-local-fixture.json"
        write_json(fixture, local_fixture())
        e.hdc("file", "send", str(fixture), "/storage/media/100/local/files/Docs/Download/vg-spec1-local-fixture.json")
        driver.click(BY.text("浏览"))
        time.sleep(.5)
        tree = e.screen("picker-browse")
        print(json.dumps([{k: a.get(k) for k in ("text", "id", "type", "bounds")} for a in flatten(tree) if a.get("text")], ensure_ascii=False))
    if args.complete_import:
        driver.click(BY.text("我的手机"))
        time.sleep(.4)
        tree = e.screen("picker-phone")
        print(json.dumps([{k: a.get(k) for k in ("text", "type", "bounds")} for a in flatten(tree) if a.get("text")], ensure_ascii=False))
    if args.finish_fixture:
        driver.click(BY.text("Download"))
        time.sleep(.5)
        e.screen("picker-download")
        driver.click(BY.text("vg-spec1-local-fixture.json"))
        time.sleep(.4)
        done = driver.find_component(BY.text("完成"))
        if done is not None:
            driver.click(done)
        time.sleep(1)
    if args.finish_fixture or args.confirm_fixture:
        e.screen("local-import-preview")
        driver.click(BY.text("继续导入"))
        time.sleep(2)
        e.screen("local-import-result")
        snapshot = e.db_snapshot("local-import-data")
        words = snapshot["tables"]["words"]
        assert {r["word"] for r in words} == {"vgspec1_localonly", "vgspec1_conflict"}, words
        assert all("LOCAL_" in r["definition"] for r in words), words
        assert snapshot["tables"]["user_word_books"], "Local-only user book missing"
    write_json(out / "preparation-source-end.json", source_fingerprint())
    print("Baseline preparation completed; no development acceptance executed.")


if __name__ == "__main__":
    main()
