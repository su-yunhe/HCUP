# 本机环境与单题初始化

每个构建/设备命令的新 PowerShell 进程先加载 `D:\hongmengcup\Enter-HarmonyEnv.ps1`，使用已验证的 DevEco 6.1.0.860、SDK 6.1.0.105 API 23 和随附工具。Python 为 `D:\hongmengcup\SWE-OpenHarmony\.venv\Scripts\python.exe`。模拟器 HarmonyCup_API23 常用连接 127.0.0.1:5555；运行前实际查询设备。

新下载、软件、缓存和产物放 D 盘。不要更改全局 Java 或系统 PATH。正式工程位于 `D:\hongmengcup\tasks\题号\project`，资料和日志放同题目录下，不在环境验证目录或题包根解题。

## 初始化顺序

仅在用户明确指定题号并要求开始/继续作答时执行。浏览 Spec 或配置流程时，不建立正式作答目录、不分析具体题目的方案。

1. 题包缓存为 `D:\hongmengcup\SWE-OpenHarmony`。仅取指定 `specs/题号.md`、`metadata/题号.json` 和 manifest 对应条目，不枚举其他基线。缺少 metadata 时对这一个路径执行 `git sparse-checkout add /metadata/题号.json`。
2. 用脚本创建本题目录，原样复制 Spec、metadata 并保存配置快照。下例题号替换成用户指定值：

   ```powershell
   . D:\hongmengcup\Enter-HarmonyEnv.ps1
   python D:\HarmonyDev\codex\skills\harmony-task-flow\scripts\workflow.py init --task jm-spec7 --root D:\hongmengcup\tasks\jm-spec7 --spec D:\hongmengcup\SWE-OpenHarmony\specs\jm-spec7.md --metadata D:\hongmengcup\SWE-OpenHarmony\metadata\jm-spec7.json
   ```

3. 从该 metadata 取得 `baseline_bundle` 和 `base_commit`；验证路径在题包 `repo_bundles/` 下，按 `release-manifest.json` 校验本题文件。只 sparse-checkout 本题 bundle。需要 LFS 时使用 `git lfs pull --include="本题bundle路径" --exclude=""`，不执行无过滤的全包下载。
4. `git clone --branch base 本题bundle路径 本题目录\project`，checkout --detach 到指定提交。已有工程不覆盖，先核实仓库根、基线、差异、准备记录。
5. 在改源码、提交或 HEAD 切换到别的提交之前，执行题包 `tools/prepare_baseline.py --task 题号 --project 本题目录\project`。保存完整输出、生成配置和锁文件，不修改工具绕过校验。
6. 准备完成后，在工程 `AGENTS.md` 追加本题入口并保留原有规则：题号、本题根路径、Skill 绝对路径，及“主 Agent 调度四个角色，子 Agent 只执行派工，不自行成为调度者”。本题主对话以本题目录为工作目录。
7. 登记主会话 ID，每次 spawn 后登记实际返回的子 Agent ID、角色和可获得的原生会话 ID。此时才派需求 Agent 分析。

## 每题目录

```text
题号/
  AGENTS.md
  inputs/Spec.md
  inputs/metadata.json
  project/                     官方基线及本题代码
  workflow/state.json          阶段、版本、角色实例、阻断原因、下一步
  workflow/events.jsonl        追加式调度事件
  workflow/requirements/      需求及复审版本
  workflow/design/            方案及修订版本
  workflow/implementation/    实现交接
  workflow/verification/      自测矩阵、失败诊断
  traces/                     原始会话、构建和测试输出
  system-config/              实际使用的 Skill 和四角色配置快照
```

`workflow.py init` 对已有匹配题目只报告恢复，不重置进度。输入或题号变更先明确迁移原因，不静默覆盖。不得把题目目录或 agent 实例复用于另一题。
