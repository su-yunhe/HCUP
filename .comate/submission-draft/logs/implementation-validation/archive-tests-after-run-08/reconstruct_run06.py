"""Reconstruct run06 imported test revision from recorded, exact later patches.

This is labelled reconstruction, not a contemporaneous pre-run archive/hash.
"""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
target = root / "logs/implementation-validation/run-06/reconstructed-imported-test-version"
target.mkdir(parents=True, exist_ok=True)
if (target / "manifest.json").exists():
    print("Existing labelled reconstruction preserved; no overwrite.")
    raise SystemExit(0)
text = (root / "hypium_tests/test_restore.py").read_bytes().decode()
start = text.index("    def click_id(self, key):")
end = text.index("    def disable_auto_sync(self):", start)
text = text[:start] + '''    def click_id(self, key):
        component = self.get(key)
        self.assertTrue(component.isEnabled(), f"{key} disabled unexpectedly")
        self.driver.click(component)

''' + text[end:]
line = '        self.assertIsNone(self.driver.find_component(BY.text("继续")), "First cancel did not dismiss dialog")\n'
assert text.count(line) == 1
text = text.replace(line, "")
start = text.index("    def test_03_fast_and_repeated_clicks(self):")
block = text[start:]
block = block.replace('component = self.stable_enabled("webdav_restore_from_cloud")', 'component = self.get("webdav_restore_from_cloud")', 1)
a = block.index('        dialogs = self.driver.find_all_components(BY.text("继续")) or []')
b = block.index('        button_bounds = self.dialog("继续")', a)
block = block[:a] + '''        self.require_text("继续", "Rapid entry did not open first dialog")
        self.assertEqual(len(self.driver.find_all_components(BY.text("继续")) or []), 1)
''' + block[b:]
text = text[:start] + block
(target / "test_restore.py").write_bytes(text.encode())
current_support = root / "hypium_tests/restore_support.py"
(target / current_support.name).write_bytes(current_support.read_bytes())
ps = (root / "hypium_tests/run.ps1").read_bytes().decode()
ps = "\n".join(line for line in ps.split("\n") if 'audit.py "tests-' not in line)
(target / "run.ps1").write_bytes(ps.encode())
records = {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in target.iterdir() if p.is_file() and p.name != "manifest.json"}
(target / "manifest.json").write_text(json.dumps({"label":"reconstruction from native tool patch operations, not contemporaneous capture",
    "restoration":"Reverse three post-import test edits: stable target helper, first-cancel disappearance assertion, approved rapid-entry contract; remove two later run.ps1 archive calls.",
    "support":"restore_support.py had no post-import edits during run06; copied current bytes, not claimed as an original pre-run hash.",
    "files_sha256":records},indent=2),encoding="utf-8")
print(json.dumps(records,indent=2))
