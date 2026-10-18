# traces — cmu-spec34

只包含 `trace-index.md` 会话表所列的两个会话，未按工程路径、题目 ID 或时间检索其他会话，未打包 `~/.comate-engine/store/` 的其余内容。

| 会话 | sessionUuid | 用途 | 原生明细 SHA-256 |
| --- | --- | --- | --- |
| A | `39649b73-d6f6-439f-b7f1-7bc77cc45e16` | 分析（0-analyze） | `d15ca68485fb62a3ed41bbce158dce3447d8cc23cfe050b1764a244427bc458b` |
| B | `16786162-2757-4ccd-a27f-3b71c2342c4b` | 开发与自测（1-do） | `9f9a482b37ec45f93f184865440bcd230e4359db5818f79045dce10f758e22a1` |

IDE 侧边栏会话 ID：两个会话均 `【待补充】`（见 `trace-index.md`）。

## 目录

- `native/chat_session_<sessionUuid>`：Comate 引擎原生会话明细（一个 JSON 对象）。
  - `messages[]` 按时间排列；`role=user` 的 `payload.model` / `payload.agent` 是模型与 Agent，`role=assistant` 的 `tokenUsage`、`performanceMetrics`、`appliedRuleNames`、`status`、`discard`、`elements[].children[]`（`type` 为 `REASON`/`TEXT`/`TOOL`/`EXCEPTION`）是回复、工具调用及结果。
  - 用 Python 读取：`json.load(open(path))`。
- `native/chat_session_<sessionUuid>.d/`：blob 目录。明细中的 `{"$blob":"sha256:<hex>"}` 对应其中文件名为 `<hex>` 的文件（UTF-8 文本，长工具输出）；`.trash/` 为目录自带的已回收 blob，原样保留；`manifest.json` 为引擎自带清单。
- `comate_chat_sessions.filtered.jsonl`：`comate_chat_sessions.jsonl` 中仅这两个 sessionUuid 的 2 行（SHA-256 `6980a4f5a9f5fadbbd80b355fea91c9fa40fff5ae9e33d865bfec4b4cfd27acb`）。
- `markdown/<sessionUuid>.md`：从原生明细**自动生成**的可读副本，不是 IDE“导出本地”产物；推理与工具文本超过 3000／1500 字符处截断并标注，以原生明细为准。
- `code-snapshot/git-state.txt`：基线、HEAD、`baseline-cmu-spec34` 标签、工作树快照 tree 摘要、`git status`、`base..HEAD` 日志、numstat。
- `code-snapshot/files.sha256`：`changes/final.diff` 覆盖的 31 个文件在提交版本下的 SHA-256。

## 保留的失败与重试

会话 A `[4-5]`、会话 B `[2-3]` 因模型服务网络错误（`getaddrinfo ENOTFOUND comate.baidu-int.com`）失败，会话 B `[4-5]` 状态 `cancelled`（含 9 次被中止、1 次失败的 `edit_file`）。均未删减，位置与下标见 `trace-index.md`。

## 脱敏

无。两个会话的原生明细文件与 blob 目录均经 `cmp`／`diff -rq` 与 `~/.comate-engine/store/` 中的原件逐字节比对一致（SHA-256 见上表）。
