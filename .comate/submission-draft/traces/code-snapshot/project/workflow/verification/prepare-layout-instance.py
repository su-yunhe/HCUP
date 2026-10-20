"""Approved task-local emulator config copy; no userdata or global config mutation."""
from pathlib import Path
import hashlib
import json
import uuid

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path("D:/HarmonyDev/emulator/instances/HarmonyCup_API23")
TARGET = ROOT / "logs/verification-emulator/instances/CmlSpec7_Layout"
TARGET.mkdir(parents=True, exist_ok=False)
changes = {
    "config.ini": {
        "name": "CmlSpec7_Layout", "instancePath": TARGET.as_posix(),
        "uuid": str(uuid.uuid4()), "isCustomize": "true", "hw.lcd.density": "320",
        "hw.lcd.single.width": "1600", "hw.lcd.single.height": "2400",
        "hw.lcd.single.diagonalSize": "10.1",
    },
    "hardware-qemu.ini": {"hvd.name": "CmlSpec7_Layout", "hvd.id": "CmlSpec7_Layout"},
    "huawei-settings.cfg": {"uniqueId": str(uuid.uuid4())},
}
manifest = {"source": str(SOURCE), "target": str(TARGET), "files": {}, "copied_userdata": False}
for name, replacements in changes.items():
    source = SOURCE / name
    original = source.read_bytes()
    seen = set()
    output = []
    diffs = []
    for line in original.decode("utf-8-sig").splitlines():
        key, sep, value = line.partition("=")
        if sep and key in replacements:
            seen.add(key)
            diffs.append({"key": key, "before": value, "after": replacements[key]})
            line = key + "=" + replacements[key]
        output.append(line)
    if seen != set(replacements):
        raise RuntimeError(f"Unknown config field; not guessing: {set(replacements) - seen}")
    new = ("\n".join(output) + "\n").encode("utf-8")
    (TARGET / name).write_bytes(new)
    if source.read_bytes() != original:
        raise RuntimeError("Original config changed concurrently")
    manifest["files"][name] = {
        "source_sha256": hashlib.sha256(original).hexdigest(),
        "target_sha256": hashlib.sha256(new).hexdigest(), "changes": diffs,
    }
destination = ROOT / "logs/verification-preparation-01/layout-config-copy.json"
destination.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(destination)
