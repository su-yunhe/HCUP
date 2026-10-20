# cml-spec1：2-submit 独立核验 r1

机械一致性校验通过；正式提交材料仍为 blocked。R01—R25 为 **21 pass、1 fail、3 blocked**，不代表官方材料核验通过。R04 的历史范围失误保留为 fail，双 ID、人工声明和团队冻结仍有缺口。

本轮只验证提交材料，未构建、未操作设备、未改生产或 Spec，仅写本报告及同名 JSON。环境：Windows、Python 3.12.3、Git 2.45.2.windows.1；每个 PowerShell 进程加载 `D:/hongmengcup/Enter-HarmonyEnv.ps1`。本轮没有截图需求；既有设备截图随工程快照保留。

## 已独立完成的检查

- 完整快照 **11,951 文件**，快照、限定 `patch-apply-scoped` clone、非 runtime 的当前工程，全路径集合及逐文件 SHA-256 均零差异。聚合：`e1c8f2286ca9f93ca33bb094356bd415f53efa80a857baf8d2d22ce699ee870a`。
- 父 Agent 的限定分支 clone、基线 checkout、`git apply --check --binary`、实际 apply 原始命令均 exit 0；独立执行 `git -c core.autocrlf=false apply --reverse --check --binary` 也 exit 0。补丁 SHA-256：`da4db70fd3c29f6a4d05773479cb04acee153520c3769515612305482a5dcdc0`。
- **9,761** 个二进制清单条目与全文件 UTF-8/NUL 分类、路径、大小、SHA-256 一致；14 个生产二进制全部与基线同路径字节同源。
- **16 原生分段、15 唯一会话 ID**均可解析，逐条 JSON 与 Markdown 对象相同；工具调用索引的文件、行号、call ID、工具名与原文完全对应。未读取禁止的初始化总览或旧非限定 clone。
- **263** 份日志的源、复制件、清单路径集合、大小与 SHA-256 全部一致。
- 官方索引 **24 字段**全部保留并填写；10 个原始空输入逐项标待补充；JSON 三个路径均为 `/` 分隔的包内相对路径，目录/文件类型正确；构建说明无私有绝对路径。
- common 当前包含仓库 HEAD、四任务书源/本题副本/归档摘要一致，三官方模板归档摘要一致。`spec/history/` 当前不存在。
- 688 个生产文件零变化，聚合 `2cebe8ebb0c7fcc3d15058f9dedb0843580aacf5b1f41593f3dbe4200cf9d14c`；HAP 20,739,960 bytes、`d54386d3d42a6049d5af9fcece16c9d0cdbd271a2217cb008c196af177202615`。独立 `git diff --check` exit 0，tracked BuildProfile 与对应差异均空，仅保留既有 autocrlf 提示。

专用模拟器持续写入的 `traces/baseline-analysis/emulator-instances/CmlSpec1Baseline/Log/` 单列 **4 路径**的 live 差异。唯一交付版本是复制后实算的不可变快照；补丁和应用 clone 仍须与快照逐字节一致。例外不扩展到生产、测试、workflow、根 logs 或其余 traces。

## 逐需求结果

| 需求 | 状态 | 证据及界限 |
| --- | --- | --- |
| R01 | pass | 既有最终构建 exit0、run-r4 8/8 原始证据及源码/HAP绑定保留；本轮未重跑设备。 |
| R02 | pass | 688生产文件/HAP不变；核验角色仅写两份指定报告。 |
| R03 | pass | 只交单题片段，团队文件、ZIP、外部提交留3-package。 |
| R04 | fail | 历史全库正文检索、前缀扫描和默认local clone范围失误已发生并披露；当前范围修正。 |
| R05 | pass | 十个原始空字段均待补充，自动事实另列。 |
| R06 | pass | 全11951文件精确重建，含过程文件及二进制。 |
| R07 | pass | 原始check/apply exit0；独立全文件hash及反向check通过。 |
| R08 | pass | diff --check及BuildProfile噪声检查通过。 |
| R09 | pass | staging排除与工程冻结投影明确，其他过程文件保留。 |
| R10 | pass | 全9761二进制摘要及14基线同源项复核一致。 |
| R11 | pass | 构建/安装/启动/自测说明及应用标识具备，可携带路径明确。 |
| R12 | blocked | 24字段完整；Comate引擎UUID不存在于实际Codex格式，部分侧边栏独立映射未核实。 |
| R13 | pass | 16段原生、过滤索引、完整派生Markdown和工程快照具备。 |
| R14 | pass | 当前双维发现、任务限定及时间点边界已记录；历史越界仍列R04 fail。 |
| R15 | pass | common当前版本/四摘要和历史目录缺失已核对。 |
| R16 | pass | 263日志源/副本/清单一致，原失败及重试保留。 |
| R17 | pass | 基线、依赖、公开来源与访问事实披露，提供者额外来源声明仍待补充。 |
| R18 | pass | 本地完成、AI参与、历史生命周期超时及官方测试不可用均如实说明。 |
| R19 | pass | 本题单JSON对象和三个相对路径均可映射到实际目录/文件。 |
| R20 | blocked | 人工提示/设备操作有索引；直接改码及人员声明空白，不能代填无人工改码。 |
| R21 | pass | 实用Skill/配置/工具位置保留；补充的当前定义没有冒充历史快照。 |
| R22 | pass | 实际未内容脱敏和记录缺失说明保留，禁止总览/整库不进入交付映射。 |
| R23 | pass | 待补字段和自动事实出处两清单齐备。 |
| R24 | blocked | 工程快照已固定；团队freeze_time为空，活跃材料会话还需最终时间点导出。 |
| R25 | pass | 未将结构/本地验证写成官方材料通过或官方得分。 |

## 失败、最小复现和归因

1. **历史范围控制失败（R04）**：初版 collector 全库 `rg` 读取正文但仅输出命中文件名；编码审计在排除混合目录前读取8000字节前缀。期望先排除禁止/非本题内容，实际历史访问不能撤销。证据强：初版脚本与审计原文。已限定后续选择并披露；交由主 Agent 保留失败和判断后续处理，不需要功能修复。
2. **初次临时 clone 范围异常（R04）**：默认local优化复制共享对象库，操作中断；自动审批以 `blocked by policy` 拒绝递归删除，旧目录仍在被排除的隐藏 `.validation/`。证据中等：命令及重试/清理报告；本核验角色未读取旧目录内容，不推断受保护历史被解析或使用。
3. **首次字节重建失败（R06/R07，已重测通过）**：例如 `feature/main/src/main/ets/component/TabLottieIcon.ets`，期望原始LF字节，实际首次clone应用继承全局autocrlf并改为CRLF；共159重建差异，另4个runtime live变更。固定临时clone及apply的 `core.autocrlf=false`，按公开runtime边界重做，最终完整快照及clone零差异。原失败记录保留，未改生产或削减断言。归因证据强。

## 未完成与证据范围

- 十个提供者字段、官方指定基线reports原文、Comate专有字段/部分侧边栏映射仍缺失；本地准备输出没有冒充缺失原文。
- 活跃会话为截至导出时的原生快照，最终新增材料事件需再采集；团队正式冻结时间仍待提供。
- 官方隐藏测试 **not_run**，本轮构建/设备复跑 **not_run**；没有官方成绩结论。
- 主 Agent 最终采集后只需核对新增原生/文档及固定快照、补丁标识；工程没有变化时，不重复已通过的全量hash。

原始命令、退出码、stdout/stderr、执行代码、环境、逐文件实际摘要和全部差异集合见[同名JSON](independent-review-r1.json)。定位时猜错过报告路径，已按真实目录定位；临时Markdown管道编码问题以直接UTF-8写入修正，未改动任何验证结论。
