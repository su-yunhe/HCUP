# cml-spec7 提交材料文档交接 01

角色：本次材料文档实施。真实 `CODEX_THREAD_ID=01a15912-a712-7051-9226-6396f727ba11`。已加载 `D:/HarmonyDev/codex/agents/harmony_implementation.toml`，按本题 `spec-harness/2-submit.md`、`workflow/requirements/submission-review-01.md`、批准方案 `workflow/design/submission-plan-01.md` 和主调度派工实施。没有创建子Agent、操作设备、重新构建或修改业务/资源/配置/测试/团队根文件。

## 写入文件与责任范围

本角色仅新增以下授权文件：

- `.comate/submission-draft/build.md`
- `.comate/submission-draft/trace-index.md`
- `.comate/submission-draft/sources.fragment.md`
- `.comate/submission-draft/solution.fragment.md`
- `.comate/submission-draft/submission.json.fragment`
- `.comate/submission-draft/human-changes.md`
- `.comate/submission-draft/missing-fields.md`
- `.comate/submission-draft/auto-filled-facts.md`
- `.comate/submission-draft/DELIVERY.md`
- `.comate/submission-draft/tools/write_documents.py`
- 本交接文件。

根调度已有 `export_evidence.py`、`freeze_patch.py`、机器JSON/日志、需求/设计/验证文档及调度状态均未改写。文档生成器只读取本题真实facts、任务书版本、会话元数据/原生副本、日志清单、准备记录及根/模块锁文件，写入上述9份草案文档。它可在根调度最终刷新元数据及补丁结果后重新执行，以同步切片与验证状态。脚本SHA-256：`df681e790b2a04dd7ab374aafe4d1dca4dee1b3f449fcf4c9b3e89830ab8ab58`。

## 需求覆盖与事实边界

| 材料需求 | 实施结果 |
| --- | --- |
| S01/S16：真实完成范围 | 保留38pass/3blocked；B9–B11真实三方授权未完成，不当成官方F-point/成绩或全完成 |
| S08：便携构建说明 | 锁文件精确依赖、产品/模块/模式、安装启动/应用标识/必要初始化、历史结果出处齐全；只用工程相对路径和PATH工具；披露原.ps1硬编码，并提供随包test-harness+Python入口命令 |
| S09/S12/S14：官方索引与真实工具映射 | 官方24字段全部保留；Codex payload.id为本体线程、payload.session_id可能指父、父子关联/IDE侧边栏分别核实；Comate缺失不造ID；逐线程模型/effort及最新原生累计token，不逐事件求和 |
| S10/S11/S13/S18/S20：轨迹与失败/缺失 | 引用两维发现清单、原生/机械Markdown副本及切片范围；保留原失败、02b失效、800vp旧轮/1200vp补测、测试助手错误补测、清理拒绝；官方基线报告缺失与本地替代log区别、初始stdout和IDE导出缺口明确 |
| S15/S19：来源与人工操作 | 基线同源图标、原创协议、官方通用SDK读取/下载/失败分别说明；人工extra_sources、human_edits等空字段待补，不填“无” |
| S17/S21：任务片段与两份清单 | 只一个cml-spec7对象；status保守not_completed，三个拟定包内相对路径非空且后两是文件；自动事实与仍需人工补充分别列表 |
| S04–S07/S22：完整project/patch范围 | 本角色只写映射及验证位置，不越权声称patch通过；明确精确复制snapshot/project、防材料递归、缓存/生成磁盘排除、行尾差异不计本阶段业务改动；完整冻结/应用/逐文件比对由root及独立验证负责 |

使用证据：`facts.json`、`taskbook-versions.json`、`traces/session-metadata.json`、`logs-copy-manifest.json`、`workflow/delivery-01.md`、`workflow/provider-research-01.md`、本题原始输入、官方三个模板、构建配置/模块锁文件、`cml_evidence.py`及实际验证入口。只读公共team输入与授权官方模板；没有访问其他题或来源项目相关修复历史。官方准备脚本的本题既有执行证据为 `logs/prepare-baseline.log` 的 `dry_run=false` 及 `workflow/setup-result.json.baseline_prepare=pass`，不是缺失官方报告的同一文件。

## 本角色局部检查

文档生成命令 `python .comate/submission-draft/tools/write_documents.py` 已成功，退出0。未执行指南中的构建或设备命令，未把历史日志冒称本次执行。

独立于生成器的本地只读断言退出0：

- 脚本AST可解析，没有生成字节码；官方trace-index模板24项均有对应字段，无漏项。
- `build.md` 私有驱动器绝对路径、`/Users/`、`/home/`匹配数0。
- JSON片段解析为单一对象，字段集合和三项路径正确，status为not_completed。
- 当次机器元数据中的15个原生本题会话ID均出现在索引；无U+FFFD编码替代字符。
- `current-production-fingerprint.json.sha256` 与 `facts.json.validation.source_sha256` 相同，为 `26307326248e8e874d1e2d8c3a4abf10e14008d5fd386b91682357a928f6f78e`；是完整生产输入范围，不混同14变更文件范围。

历史HAP为17,068,002 bytes、SHA256 `8aaa5de48b5664b92210fad7ffcddf9abbcebbb92e52faf7f5359bbeb3611863`。主调度另已核实791生产输入与最终03验收一致、`git diff --check`退出0；本角色没有重跑这些构建/设备环节。局部文档断言不替代独立材料验收。

## 尚需根调度及后续阶段处理

1. 本交接和最终材料会话应在root声明的冻结范围/切片截止内收录；根调度完成project-manifest、binary/resource/line-ending清单与完整patch应用/全树比较，再重跑文档生成器刷新状态。不在本角色交接中预先记pass。
2. 独立验证角色复核文档、输入/模板副本、会话选择与敏感范围、工程/patch一致性及便携命令的真实脚本行为。最终结论由root结合独立验证作出。
3. 人工human_edits/known_issues/extra_sources/md_export_dir、团队version/contact/freeze_time/members/source_guard均仍待补；Comate字段不适用、部分独立IDE ID未核实、历史初始stdout与官方报告缺口不能杜撰补回。
4. B9–B11外部接入条件未消除；团队3-package仍需真实题目选择和正式冻结，不以本草案not_completed或拟定路径代替其决定。

本角色写入到此结束。现有9份文档已可供独立审查；后续只在收到主调度定向派工时修订获派文件。
