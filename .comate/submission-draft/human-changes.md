# vg-spec1 人工操作与改码索引

人工直接修改代码情况、操作人姓名、修改前后标识及证据：**【待补充】**。题目输入human_edits为空，不能解释成“无人工直接修改代码”。本文件记录已知操作事实，不补造编辑历史。

| 事实 | 原始/当时披露记录（相对本任务目录） |
| --- | --- |
| Agent误点IME首次声明“同意”，随后停止并披露 | `project/workflow/verification/facility-incident-02.md`、`.json`；`logs/development-round-02/ime-preparation-01/root-stop-state/action-disclosure.json` |
| 用户报告输入法设置完成后继续 | `project/workflow/manual-ime-user-completion.json`；相关本题原生主会话 |
| 用户手动关闭/恢复Wi-Fi；NAT仍在线，不能作离线通过 | `logs/development-round-02/manual-offline-round-01/manual-user-action-disconnect*.json`、`manual-user-action-restore.json` |
| 用户启动审查后的管理员helper；05/06失败及最终07均保留 | `project/workflow/network-isolation-user-launch-07.md`；`project/workflow/verification/wfp-attempt-05.json`、`wfp-attempt-06.json`、`offline-round-03.json` |

实际提示、工具操作与返回见最终包根 `traces/vg-spec1/native/`。操作人的身份及其他人工修改完整性由用户补充，不按聊天中“用户”自动推断姓名/成员分工。
