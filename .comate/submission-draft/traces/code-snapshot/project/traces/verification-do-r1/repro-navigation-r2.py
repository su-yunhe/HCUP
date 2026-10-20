"""Native fix regression plus actual frame-collector validation; no Hypium input."""
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from hypium_tests.evidence import Evidence, FrameCapture, flatten_tree, rectangle, save_json, shape_variants

e = Evidence(SimpleNamespace(_testMethodName="native_fix_regression"), "127.0.0.1:11245",
             ROOT / "traces/verification-do-r1/run-r2")


def tree(label):
    nodes = e.tree(label)
    e.screenshot(label)
    root = json.loads(nodes["main_root"][0]["attributes"]["description"])
    save_json(e.path / f"{label}-summary.json", root)
    print(label, json.dumps(root), flush=True)
    return nodes, root


def center(nodes, ident):
    b = rectangle(nodes[ident][0]["attributes"]["bounds"])
    return (b[0] + b[2]) // 2, (b[1] + b[3]) // 2


e.cmd("shell", "aa", "force-stop", "com.joker.coolmall")
e.cmd("shell", "aa", "start", "-a", "EntryAbility", "-b", "com.joker.coolmall")
time.sleep(2)
nodes, before = tree("before_click")
cap = FrameCapture(e, "native_category_click").start()
action_time = time.monotonic()
e.cmd("shell", "uitest", "uiInput", "click", *center(nodes, "main_tab_category"))
cap.finish()
nodes, after = tree("after_click")
assert after["selectedIndex"] == 1, f"Category click failed: {after}"
assert after["selectionEpoch"] == before["selectionEpoch"] + 1, "Selection was submitted more than once"
bounds = rectangle(nodes["main_tab_category_icon"][0]["attributes"]["bounds"])
samples = cap.roi(bounds, "category", after=action_time)
variants, distances = shape_variants(samples)
save_json(cap.path / "collector-validation.json", {"samples": len(samples), "shapeVariants": variants, "differences": distances})
print("category_click_actual_shape_variants", variants, flush=True)
assert variants >= 3, "Collection must preserve real temporal Lottie geometry"

e.cmd("shell", "uitest", "uiInput", "click", *center(nodes, "main_tab_home"))
time.sleep(2)
nodes, before = tree("before_left")
assert before["selectedIndex"] == 0
box = rectangle(nodes["main_content_pager"][0]["attributes"]["bounds"])
width = box[2] - box[0]
y = (box[1] + box[3]) // 2
cap = FrameCapture(e, "native_home_left").start()
action_time = time.monotonic()
e.cmd("shell", "uitest", "uiInput", "swipe", int(box[0] + width * .8), y,
      int(box[0] + width * .2), y, 1200)
cap.finish()
nodes, after = tree("after_left")
assert after["selectedIndex"] == 1, f"Native left swipe failed: {after}"
assert after["selectionEpoch"] == before["selectionEpoch"] + 1
bounds = rectangle(nodes["main_tab_category_icon"][0]["attributes"]["bounds"])
variants, distances = shape_variants(cap.roi(bounds, "category", after=action_time))
save_json(cap.path / "collector-validation.json", {"shapeVariants": variants, "differences": distances})
print("home_left_actual_shape_variants", variants, flush=True)
assert variants >= 3
e.unchanged()
save_json(e.path / "native-fix-result.json", {"categoryClick": "pass", "homeLeft": "pass", "actualDynamicCollection": "pass"})
