

---

# 本题自动调度

题号：cml-spec17

本题根目录：D:/HCUP/cml-spec17

主 Agent 开始/继续作答时加载 `D:/HarmonyDev/codex/skills/harmony-task-flow/SKILL.md`，读取 workflow/state.json，调度四个角色并按失败证据回退。

子 Agent 仅完成收到的派工，不自行成为调度者或创建子 Agent。仅使用本题 inputs、project 和记录；禁止其他题工程及相关上游修复历史。

## HCUP 工作区布局与阶段

本题工程根就是当前目录；workflow/state.json 的 project 指向当前目录，不要再创建 project 子目录，也不要使用 Skill 示例中的另一套工程路径。

本题需求读取 spec/requirement.md，元数据读取 spec/metadata.json；inputs/ 保留原始输入副本。公共资源只读访问 ../common/，不得访问其他赛题目录。

开始构建或设备命令前加载 D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1。

本次仅完成独立工程准备；尚未分析需求、设计方案或实现功能。正式作答从本目录的新会话开始，登记新会话后再按四角色流程推进。

初始化总览会话也包含公共环境、官方示例与其他题的工程准备内容，不能将其视为本题功能开发证据；后续需求和编码角色不要读取该总览会话作为实现参考。
