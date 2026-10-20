# traces/ 说明（cml-combo-search）

本目录是本题 AI 原始记录的随包副本，只含 `trace-index.md` 会话表所列的两个会话。成果包内位置为 `traces/cml-combo-search/`。

| 路径 | 内容 |
| --- | --- |
| `native/chat_session_<uuid>.json` | 引擎会话明细的逐字节副本（原文件名无扩展名，为 JSON）。`messages[].elements[]` 是按序的 REASON / TOOL / TEXT |
| `native/blobs/chat_session_<uuid>.d/` | 明细中 `{"$blob":"sha256:…"}` 引用的外置内容（编辑内容、读文件结果、截图等），文件名即 SHA-256；`.trash/`、`.detail-prev-*` 为引擎保留的旧版本 |
| `native/terminals/*.output` | 明细引用到的终端长输出（4 个） |
| `native/project-memory/` | 会话读写过的 Comate 项目记忆文件 |
| `index/comate_chat_sessions.*.jsonl` | 引擎会话索引中仅这两个 sessionUuid 的行（索引已被引擎压缩，说明见 `trace-index.md`） |
| `markdown/chat_session_<uuid>.md` | 由 `tools/render_md.py` 从原生文件生成的可读副本（不是侧边栏导出；超长参数/结果在 4000 字符处截断，截图 base64 以占位符替换） |
| `code-snapshot/` | 基线/HEAD/工作树 tree 对象、变更文件清单与 SHA-256、任务书 SHA-256 |
| `tools/render_md.py` | Markdown 副本的生成脚本，用法见脚本头部：`python3 render_md.py <chat_session_*.json> <blobs/chat_session_*.d> <out.md> [max_chars]` |

读取示例：

```bash
python3 - <<'EOF'
import json
d = json.load(open("native/chat_session_b362b3f8-b428-4220-b57b-989aab79ddb5.json", encoding="utf-8"))
for m in d["messages"]:
    print(m["role"], m["id"], m.get("status"))
EOF
```

两个会话的对应关系：`9fac2284-…` 为分析（`0-analyze.md`），`b362b3f8-…` 为实现与自测（`1-do.md`）。IDE 侧边栏会话 ID 未能核实，见 `trace-index.md`。
