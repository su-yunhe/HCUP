"""No-device syntax/discovery and capture-analysis calibration; never A-item evidence."""
import ast
import hashlib
import json
import re
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.runner import discover
from harness.driver import HarnessTestCase
from hypium_tests.evidence import shape_variants, still_metrics

files = sorted((ROOT / "hypium_tests").glob("*.py"))
for path in files:
    compile(path.read_text(encoding="utf-8"), str(path), "exec")
suite = discover(ROOT)


def cases(group):
    for item in group:
        if hasattr(item, "_tests"):
            yield from cases(item)
        else:
            yield item


tests = list(cases(suite))
assert tests and all(isinstance(t, HarnessTestCase) for t in tests)
source = (ROOT / "hypium_tests/test_main_tabs.py").read_text(encoding="utf-8")
tokens = {n.value for n in ast.walk(ast.parse(source)) if isinstance(n, ast.Constant) and isinstance(n.value, str)}
ids = sorted(int(x[1:]) for x in tokens if re.fullmatch(r"A\d+", x))
assert ids == list(range(1, 45)), ids
gray = np.full((80, 80, 3), 255, dtype=np.uint8)
gray[20:60, 20:60] = 128
black = np.full((80, 80, 3), 255, dtype=np.uint8)
black[20:60, 20:60] = 0
color_only = [({}, x) for x in (gray, black, gray, black)]
assert shape_variants(color_only)[0] == 1, "Gray/black selection alone must never satisfy animation geometry"
moving = []
for offset in (10, 20, 30):
    image = np.full((80, 80, 3), 255, dtype=np.uint8)
    image[20:40, offset:offset + 20] = 0
    moving.append(({}, image))
assert shape_variants(moving)[0] == 3
assert all(v["meanDelta"] == 0 for v in still_metrics([({}, black)] * 3))
assert any(v["meanDelta"] > .5 for v in still_metrics(moving))
result = {"scope": "offline helper calibration only; no device use; no A item passed",
          "syntaxFiles": [str(p.relative_to(ROOT)) for p in files], "discovered": [t.id() for t in tests],
          "scriptSHA256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
          "AReferences": ids, "colorOnlyShapeVariants": 1, "movingShapeVariants": 3,
          "staticAndMotionDiscrimination": "pass", "deviceExecuted": False}
(ROOT / "logs/verification-do-offline-r1.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
