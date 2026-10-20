"""Assert only the recorded, controlled baseline path; never an official score."""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
results = []


def nodes(name):
    return [json.loads(line) for line in (ROOT / "nodes" / (name + ".jsonl")).read_text(encoding="utf-8").splitlines()]


def check(identifier, description, condition, evidence, actual, scope):
    row = {"id": identifier, "description": description, "status": "pass" if condition else "fail",
           "actual": actual, "evidence": evidence, "scope": scope}
    results.append(row)
    print(json.dumps(row, ensure_ascii=False))


config = nodes("19-configuration-filled")
inputs = [n for n in config if n.get("type") == "TextInput"]
check("A02-public-fields", "组件输入后公开配置值与虚构配置一致", [n["text"] for n in inputs][::] ==
      ["http://127.0.0.1:18085", "spec15-user", "***************", "***********", "/baseline-spec15"],
      ["19-configuration-filled.json:1", "hypium-fill-all.raw.log"], [n["text"] for n in inputs], "本轮填写路径；密码仍保持遮蔽")

cancel = nodes("25-after-stable-cancel")
checkpoints = [json.loads(line) for line in (ROOT / "request-checkpoints.jsonl").read_text(encoding="utf-8").splitlines()]
cancel_checkpoint = next(row for row in checkpoints if row["label"] == "after_stable_cancel")
check("A16-cancel", "第一次取消后弹窗关闭、无恢复忙碌、无服务请求", not any(n.get("type") == "AlertDialog" for n in cancel)
      and not any("正在下载" in n.get("text", "") or "处理中" in n.get("text", "") for n in cancel)
      and cancel_checkpoint["request_begin_count"] == 0,
      ["25-after-stable-cancel.json:1", "request-checkpoints.jsonl"], cancel_checkpoint,
      "有效保存配置、自动同步已关闭；不推断数据库逐字节相同")

events = [json.loads(line) for line in (ROOT / "server-requests.jsonl").read_text(encoding="utf-8").splitlines()]
requests = [row for row in events if row["kind"] == "request_begin"]
timeline = [json.loads(line) for line in (ROOT / "device-timeline.jsonl").read_text(encoding="utf-8").splitlines()]
click = next(row for row in timeline if row.get("output_file") == "confirm-restore-continue.log")
check("A12-A13-network", "第一次继续后受控端点捕获实际恢复链请求", bool(requests) and
      all(row["auth_matches"] and row["time"] >= click["started"] and
          row["phase"] == "confirmed_restore_delayed_404" for row in requests),
      ["server-requests.jsonl", "device-timeline.jsonl"], requests,
      "仅本轮实际恢复链；方法、子路径、条数不作为 Spec 固定合同")

for name in ("27-restore-pending-early", "28-restore-pending-second", "29-restore-pending-later"):
    observed = nodes(name)
    spinners = [row for row in observed if row.get("type") == "LoadingProgress" and row.get("visible") == "true"]
    busy = [row for row in observed if row.get("text") == "正在下载云端备份..." and row.get("visible") == "true"]
    check("A05-" + name[:2], "真实请求 pending 样本存在可见 ArkUI LoadingProgress", len(spinners) > 0,
          [name + ".json:1", name + ".png", "request-checkpoints.jsonl"], {"visible_loading_progress": len(spinners), "node_count": len(observed)},
          "本次延迟目录预检/备份HEAD路径；至少一个缺失样本足以构成 A05 反例")
    check("A08-A09-" + name[:2], "请求 pending 样本存在可见恢复进行中文字", bool(busy),
          [name + ".json:1", "request-checkpoints.jsonl"], {"status_text_count": len(busy)},
          "仅三个采样点及已运行无备份分支；不声称成功解密/解析/导入区间已测")

terminal = nodes("30-restore-404-terminal")
terminal_buttons = [row for row in terminal if row.get("type") == "Button"]
check("A20-A23-404-subcase", "无备份404路径展示真实结果并恢复按钮可交互", any(
      row.get("text", "").startswith("⚠️ 云端暂无备份：") for row in terminal)
      and len(terminal_buttons) == 5 and all(row["enabled"] == "true" for row in terminal_buttons)
      and not any("正在下载" in row.get("text", "") or "处理中" in row.get("text", "") for row in terminal),
      ["30-restore-404-terminal.json:1", "server-requests.jsonl:9"],
      {"button_count": len(terminal_buttons), "enabled": [row["enabled"] for row in terminal_buttons]},
      "仅不存在备份的404子场景；其他错误、成功恢复仍未测")

output = {"time": datetime.now(timezone.utc).isoformat(), "official_score": None,
          "scope": "recorded baseline path only", "results": results,
          "exit_code": 1 if any(row["status"] == "fail" for row in results) else 0}
(ROOT / "assertion-results.json").write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
sys.exit(output["exit_code"])
