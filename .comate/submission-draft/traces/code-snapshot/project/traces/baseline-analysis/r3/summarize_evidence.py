"""Summarize captured baseline evidence; no device or source operations."""
import collections
import hashlib
import json
import pathlib
import struct

out = pathlib.Path(__file__).resolve().parent
labels = ["existing-app-window", "content-left", "content-up", "restarted-app-window"]
summaries = []
baseline_rows = None
for label in labels:
    tree = json.loads((out / f"{label}.json").read_text(encoding="utf-8-sig"))
    windows = []

    def locate(node):
        if node.get("attributes", {}).get("bundleName") == "com.joker.coolmall":
            windows.append(node)
            return
        for child in node.get("children", []):
            locate(child)

    locate(tree)
    attrs = []

    def walk(node):
        attrs.append(node.get("attributes", {}))
        for child in node.get("children", []):
            walk(child)

    for window in windows:
        walk(window)
    rows = sorted((a.get("text", ""), a.get("type", ""), a.get("bounds", ""))
                  for a in attrs if a.get("text"))
    if baseline_rows is None:
        baseline_rows = rows
    summaries.append({"label": label, "app_window_count": len(windows),
                      "text_bounds_equal_first_app_capture": rows == baseline_rows,
                      "four_tab_text_occurrences": {t: sum(a.get("text") == t for a in attrs)
                                                    for t in ["首页", "分类", "购物车", "我的"]},
                      "navigation_scroll_component_counts": {t: sum(a.get("type") == t for a in attrs)
                                                             for t in ["Tabs", "TabContent", "Swiper", "Scroll", "List"]},
                      "text_and_bounds": rows})
(out / "observed-app-summary.json").write_text(json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8")

files = []
for path in sorted(out.glob("*")):
    if not path.is_file() or path.name == "artifact-manifest.json" or path.suffix not in (".png", ".json", ".py"):
        continue
    data = path.read_bytes()
    entry = {"file": path.name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
    if path.suffix == ".png":
        entry["dimensions"] = struct.unpack(">II", data[16:24])
    files.append(entry)
(out / "artifact-manifest.json").write_text(json.dumps(files, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps([{k: v for k, v in s.items() if k != "text_and_bounds"} for s in summaries], ensure_ascii=False))
