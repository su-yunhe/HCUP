# cml-spec7 独立工程入口

当前工程根目录就是本题的 Git worktree；分支为 `cml-spec7`，跟踪 `origin/cml-spec7`。
官方基线提交为 `75fd0066a7fc0c1e8cedb6218df081f86d307f45`。

- [原始题目说明](requirement.md)
- [官方基线元数据](metadata.json)
- [基线准备与构建记录](baseline-notes.md)
- [待填写的题目提交信息](submit-input.yaml)
- [工程准备结果](../workflow/setup-result.json)
- [流程状态](../workflow/state.json)
- [本题工作约定](../AGENTS.md)

在本题工程根目录打开 PowerShell，运行：

```powershell
. ..\.hcup-local\Enter-HarmonyEnv.ps1
ohpm install --all
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

也可以使用工作区的 `../.hcup-local/Open-cml-spec7-Terminal.cmd` 打开已配置环境的本题终端。

本次完成工程准备与基线构建验证。正式解题请从本题目录开启专属会话，先读取 `AGENTS.md` 和 `workflow/state.json`，登记新会话后开始需求阶段。初始化总览会话仅作为准备记录，不作为本题功能开发证据。

公共任务书和测试框架通过 `../common/spec-harness/`、`../common/test-harness/` 只读引用；赛题包位置为 `../../SWE-OpenHarmony/`。不要读取其他赛题工程，也不要将公共资源复制提交到本题分支。
