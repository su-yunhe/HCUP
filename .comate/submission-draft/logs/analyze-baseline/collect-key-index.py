import json
from pathlib import Path

root = Path(__file__).resolve().parent
names = ["03-settings", "05-settings", "06-webdav-initial", "13-ime-mode-choice", "17-auto-sync-off",
         "19-configuration-filled", "21-configuration-saved", "25-after-stable-cancel",
         "26-confirmation-stable-for-continue", "27-restore-pending-early", "30-restore-404-terminal"]
wanted = ["设置", "WebDAV 配置", "同意并进入", "同意全量模式", "✅ WebDAV 设置已保存", "取消", "继续",
          "正在下载云端备份...", "从云端恢复"]
out = []
for name in names:
    path = root / "nodes" / (name + ".jsonl")
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        node = json.loads(line)
        if node.get("text") in wanted or node.get("text", "").startswith("⚠️ 云端暂无备份") or node.get("type") == "Toggle":
            out.append(f"nodes/{name}.jsonl:{index} type={node.get('type')} text={node.get('text')} checked={node.get('checked')} enabled={node.get('enabled')} id={node.get('id')}")
keys = ["approved-consent.log", "approved-ime-full-mode.log", "disable-auto-sync.log", "save-fictional-webdav-config.log",
        "cancel-first-restore-stable.log", "confirm-restore-continue.log"]
for index, line in enumerate((root / "device-timeline.jsonl").read_text(encoding="utf-8").splitlines(), 1):
    row = json.loads(line)
    if row.get("output_file") in keys:
        out.append(f"device-timeline.jsonl:{index} {row['output_file']} {row['time']}")
for index, line in enumerate((root / "request-checkpoints.jsonl").read_text(encoding="utf-8").splitlines(), 1):
    row = json.loads(line)
    out.append(f"request-checkpoints.jsonl:{index} {row['label']} requests={row['request_begin_count']} responses={row['response_count']}")
(root / "key-evidence-index.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
