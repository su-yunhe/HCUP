"""Derive a complete warning index and readable node indexes from raw evidence."""
from collections import Counter
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
lines = (ROOT / "build.raw.log").read_text(encoding="utf-8-sig").splitlines()
starts = [i for i, text in enumerate(lines) if "WARN" in text]
entries = []
rows = ["# 本轮基线完整警告索引", "", "原始日志：build.raw.log；索引保留全部重复警告。", ""]
pattern = re.compile(r"ArkTS:WARN File: (.*):(\d+):(\d+)")
counts = Counter()
for index, start in enumerate(starts):
    end = starts[index + 1] if index + 1 < len(starts) else len(lines)
    block = []
    for line in lines[start + 1:end]:
        if line.startswith("> hvigor"):
            break
        if line.strip():
            block.append(line.strip())
    entry = {"index": index + 1, "raw_line": start + 1,
             "heading": lines[start], "message": "\n".join(block)}
    match = pattern.search(lines[start])
    if match:
        entry.update(file=match[1], line=int(match[2]), column=int(match[3]))
        counts[entry["message"]] += 1
    entries.append(entry)
    rows.extend([f"## W{index+1:03d} · build.raw.log:{start+1}", "", "```text",
                 lines[start], *block, "```", ""])
(ROOT / "warning-index.json").write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "warning-index.md").write_text("\n".join(rows), encoding="utf-8")
summary = {"raw_log_lines": len(lines), "warning_heading_count": len(starts),
           "located_compiler_warnings": sum("file" in item for item in entries),
           "other_warning_headings": sum("file" not in item for item in entries),
           "compiler_warning_messages": dict(counts)}
(ROOT / "warning-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")

node_root = ROOT / "nodes"
node_root.mkdir(exist_ok=True)
observations = []
for path in sorted(ROOT.glob("[0-9][0-9]-*.json")):
    raw = json.loads(path.read_text(encoding="utf-8-sig"))
    nodes = []
    def visit(node):
        if isinstance(node, dict):
            if "attributes" in node:
                nodes.append(node["attributes"])
            for child in node.get("children", []):
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)
    visit(raw)
    target = node_root / (path.stem + ".jsonl")
    with target.open("w", encoding="utf-8") as output:
        for index, attrs in enumerate(nodes):
            output.write(json.dumps({"raw_file": path.name, "raw_line": 1, "node": index, **attrs}, ensure_ascii=False) + "\n")
    observations.append({"snapshot": path.stem, "node_count": len(nodes),
                         "loading_progress_count": sum(n.get("type") == "LoadingProgress" for n in nodes),
                         "busy_texts": [{"line": index+1, "type": n.get("type"), "text": n.get("text"), "visible": n.get("visible"), "enabled": n.get("enabled")}
                                        for index, n in enumerate(nodes) if "正在" in n.get("text", "") or "处理中" in n.get("text", "")],
                         "inputs": [{"line": index+1, "text": n.get("text"), "hint": n.get("hint"), "id": n.get("id")}
                                    for index, n in enumerate(nodes) if n.get("type") == "TextInput"],
                         "toggles": [{"line": index+1, "checked": n.get("checked"), "bounds": n.get("bounds")}
                                     for index, n in enumerate(nodes) if n.get("type") == "Toggle"]})
(ROOT / "ui-observations.json").write_text(json.dumps(observations, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False))
print("indexed snapshots:", len(observations))
