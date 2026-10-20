"""Preserve the exact pre-visibility-fix script by matching its recorded SHA."""
import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "script-versions"
source = (ROOT / "hypium_tests/test_main_tabs.py").read_text(encoding="utf-8")
old = source.replace("import hashlib\n", "")
old = old.replace('        self.receive_anchor = None\n        self.offscreen_observation = 0\n', '')
old = old.replace('                                                   "testSourceSHA256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()\n                                                                        for p in (Path(__file__), Path(__file__).with_name("evidence.py"))},\n', '')
start = old.index("    def receive_visible(self, nodes):\n")
end = old.index("    def y(self):\n", start)
original_receive = '''    def receive_visible(self, nodes):
        attrs = self.node(nodes, "home_coupon_receive")["attributes"]
        self.assertEqual(attrs.get("text"), "领取", "Top coupon anchor must keep exact Spec text")
        box = rectangle(attrs.get("origBounds", attrs["bounds"]))
        scroll = rectangle(self.node(nodes, "home_scroll")["attributes"]["bounds"])
        pager = rectangle(self.node(nodes, "main_content_pager")["attributes"]["bounds"])
        viewport = [max(scroll[0], pager[0]), max(scroll[1], pager[1]), min(scroll[2], pager[2]), min(scroll[3], pager[3])]
        return attrs.get("visible", "true") != "false" and intersection(box, viewport) / max(1, area(box)) > .8

'''
old = old[:start] + original_receive + old[end:]
old = old.replace('        if self.receive_anchor is None:\n            origin = self.e.tree(f"scroll_origin_{self.e.seq}")\n            self.e.screenshot(f"scroll_origin_{self.e.seq}")\n            self.assertTrue(self.receive_visible(origin), "Verify the original top coupon before creating an offscreen precondition")\n', '')
expected = "59813c012c97bafb9aabda87f3367ec666b74d237d5cac2439a2b94924d7187a"
actual = hashlib.sha256(old.encode()).hexdigest()
assert actual == expected, f"Pre-fix reconstruction is not byte-identical to recorded run-r2: {actual}"
for name, text in (("run-r2", old), ("run-r3", source)):
    directory = OUT / name
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "test_main_tabs.py").write_text(text, encoding="utf-8", newline="")
    (directory / "evidence.py").write_bytes((ROOT / "hypium_tests/evidence.py").read_bytes())
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.glob("*.py")}
    (directory / "sha256.json").write_text(json.dumps(hashes, indent=2), encoding="utf-8")
(OUT / "run-r2-to-run-r3.diff").write_text(''.join(difflib.unified_diff(old.splitlines(True), source.splitlines(True),
    fromfile="run-r2/test_main_tabs.py", tofile="run-r3/test_main_tabs.py")), encoding="utf-8")
context_file = Path(__file__).resolve().parent / "run-r2/run-context.json"
context = json.loads(context_file.read_text(encoding="utf-8"))
context["testSourceSHA256"] = json.loads((OUT / "run-r2/sha256.json").read_text())
context["testVersionProvenance"] = "Backfilled from exact reconstruction matching SHA recorded before runner in logs/verification-do-offline-r2.log; no device verdict changed"
context_file.write_text(json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"run-r2-exactSHA": actual, "versions": str(OUT)}, ensure_ascii=False))
