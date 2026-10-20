"""Small hdc/uitest UI evidence utility; requires a previously captured real UI tree for text clicks."""
import json
import pathlib
import re
import subprocess
import sys

log = pathlib.Path(__file__).resolve().parent
def capture(label, *args):
    subprocess.run([sys.executable, str(log / "device_capture.py"), label, *args], check=True)
    text = (log / (label + ".stdout.log")).read_text(encoding="utf-8")
    if "[Fail]" in text or "error:" in text.lower():
        raise RuntimeError("Device operation failed; see " + label)
    return text
def nodes(tree):
    yield tree.get("attributes", {})
    for child in tree.get("children", []):
        yield from nodes(child)

mode, label, *args = sys.argv[1:]
if mode == "snapshot":
    remote = "/data/local/tmp/cmlspec24-" + label
    capture(label + "-layout", "shell", "uitest", "dumpLayout", "-p", remote + ".json")
    capture(label + "-layout-pull", "file", "recv", remote + ".json", str(log / (label + ".json")))
    capture(label + "-screen", "shell", "uitest", "screenCap", "-p", remote + ".png")
    capture(label + "-screen-pull", "file", "recv", remote + ".png", str(log / (label + ".png")))
    tree = json.loads((log / (label + ".json")).read_text(encoding="utf-8"))
    useful = [{k: a.get(k, "") for k in ("text", "type", "id", "bounds", "clickable", "enabled", "selected", "hint")} for a in nodes(tree) if a.get("text") or a.get("clickable") == "true" or a.get("type") in ("TextInput", "Search")]
    (log / (label + "-summary.json")).write_text(json.dumps(useful, ensure_ascii=False, indent=2), encoding="utf-8")
    print("UI SUMMARY:", json.dumps(useful, ensure_ascii=False))
elif mode == "click-text":
    source_label, text = args
    tree = json.loads((log / (source_label + ".json")).read_text(encoding="utf-8"))
    matches = [a for a in nodes(tree) if a.get("text") == text and a.get("visible", "true") == "true"]
    if len(matches) != 1:
        raise RuntimeError("Expected one exact text match, got " + str(len(matches)) + ": " + text)
    a = matches[0]
    left, top, right, bottom = map(int, re.findall(r"-?\d+", a["bounds"]))
    capture(label, "shell", "uitest", "uiInput", "click", str((left+right)//2), str((top+bottom)//2))
else:
    raise ValueError(mode)
