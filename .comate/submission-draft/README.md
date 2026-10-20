# vg-spec7 单题材料交接

本目录是 2-submit 的本地草稿，未打 ZIP、未上传或发送。submission.json.fragment 是供 3-package 选入时的候选 submitted 条目，不代表团队已决定正式提交；三个路径均为成果包内相对路径，后两项指文件。团队 submitted_tasks 尚空，不能在本阶段擅自决定全阶段题目清单。

build.md、trace-index.md、两份 fragment、changes/final.diff、logs/ 和 traces/ 已按本题事实整理。完整检查结果看 validation/diff-validation.json 与 validation/independent-review.md；人工字段与记录缺口在下面两份清单。

## 3-package 复制接口

1. 将 build.md、trace-index.md、changes/、logs/ 放到 `tasks/vg-spec7/`；把本目录 traces/ 放到包根 `traces/vg-spec7/`，fragment 供团队文件汇总。validation 交付说明可放到任务材料 validation/；它不属于被补丁重建的 project。
2. `changes/project-snapshot.json.files` 是 project 的完整文件集合。按清单逐文件保留相对路径复制并核对 SHA-256，包含源码、资源、依赖锁文件、spec、inputs、hypium_tests、test-harness、workflow、原始日志和轨迹，以及 `.comate/submission-draft/` 的稳定材料。禁止简单递归复制工程根或一律排除 `.comate/`。
3. 精确排除 `.comate/submission-draft/changes/final.diff`、同目录 project-snapshot.json、binary-files.json/md、`.comate/submission-draft/validation/` 和 `.comate/submission-draft/.scratch/`。这些是补丁和它的证明／衍生输出，任务材料外层仍保留；把它们再放进 project 会产生自引用并破坏一一对应。其他 .comate 稳定文件均在补丁覆盖内。
4. 按脚本排除构建／依赖／缓存、local.properties、私钥后缀和明确跨题的初始化总览原文；原有快照 manifest 留在工程内，其缺少对应原文的理由在索引披露。不要删除原工作区历史文件来伪造完整性。`.scratch/` 是本题基线校验 clone 和独立 Git index，留本地，不进成果包。
5. 最后在干净本题 clone 的 `.git/info/attributes` 写入 `* -text -filter -working-tree-encoding`（仅该临时 clone），随后以 `git -c core.autocrlf=false -c core.eol=lf checkout --detach <base_commit>` 检出，再用相同 `-c` 参数执行 `apply --check --binary final.diff` 和实际 apply，按清单逐文件 SHA 比较。可直接从原工程根运行本目录 `tools/prepare_materials.py verify` 复现。校验 clone 只来自本题本地 Git，未访问上游仓库／题包受限目录。全局 core.autocrlf=true、基线 `* text=auto`，仅关闭 autocrlf 仍可能发生属性触发的换行转换；首轮失败原件保存在 validation/diff-validation-attempt1.json。本补丁为保留工作树原始字节也覆盖既有 CRLF 差异，不得通过 Git clean filter 静默改写 project。
6. 若用户补字段、变动 project 文件或刷新材料原生快照，必须重新生成补丁与清单并验证；不能沿用旧 SHA。本阶段不承担第 3 阶段的跨题汇总、正式冻结或上传。

## 仍需用户补充的字段

| 来源 | 留空字段／待确认内容 |
| --- | --- |
| common/spec-harness/team.yaml | version、contact、freeze_time（北京时间到分）、members.name/work、source_guard |
| spec/submit-input.yaml | human_edits、known_issues、extra_sources、md_export_dir（如有 IDE 原始 Markdown 导出；当前仅有 JSONL 阅读副本） |
| 如确有人工改码 | 操作人、目的、文件、前后版本及当时真实证据；目前不生成空的 human-changes.md |
| 第 3 阶段另填 | submitted_tasks、attempted_not_submitted、zip_out；本阶段不推测 |

Comate sessionUuid／侧边栏 ID、模型内部构建版、Comate agentInfo/appliedRuleNames、官方基线报告原件与官方脚本内容版本／独立执行时间、历史 ohpm 完整 argv／时间以及部分工具 CLI 版本均无法从已有证据核实，标【待补充】或说明运行器不适用。这里不会要求为填空重新造历史。正式提交前应决定记录缺口如何说明，而不是默认记录完整。

## 已自动填入的事实及出处

| 事实 | 出处 |
| --- | --- |
| 题号 vg-spec7、官方基线 9cbcf7292c8cc46955dc3b522ddbda41c66a61d9、随包 bundle 名称 | spec/metadata.json、workflow/baseline-provenance.json |
| 团队 HC2026-111、Ghost_London、online | 只读 common/spec-harness/team.yaml；本次输入副本及SHA保存在 traces/input-records/ |
| io.qzz.weiyu、entry/EntryAbility、1.0.0、SDK 声明22、无签名配置 | AppScope/app.json5、entry/src/main/module.json5、build-profile.json5 |
| Hypium 1.0.24、Hamock 1.0.0、锁版本3、无运行依赖 | 根／entry oh-package.json5、oh-package-lock.json5 |
| 实际 clean 命令、退出0、环境、9,101,851字节最终HAP及SHA | project/traces/do-verification-build-v1/、logs/do-regression-v3/install.json |
| 9项两轮汇总、29个有效门禁窗口、失败／未测范围 | workflow/verification/do-result-v1.json、workflow/acceptance/do-acceptance-v1.md、core-v1/v2及regression-v3日志 |
| 原生ID映射、模型gpt-6.1-sol、xhigh、CLI版本、逐会话原生token值、工具列表 | traces/native/*.jsonl、native-manifest.json、过滤后的session-index原行 |
| 当前客户端包版本与当前Python版本（不能倒推历史） | traces/client-environment.json |
| 任务书四份SHA及与common相同、common父仓库HEAD、无spec/history | traces/task-books/version.json；原样任务书副本 |
| 改动范围、基线同源二进制、工作树快照、补丁可应用性和全文件一致性 | changes/ 下清单、tools/prepare_materials.py、validation/diff-validation.json |
| 实际配置快照、来源及公开资料失败 | project/system-config/、workflow/design/do-design-v1.md、implementation/do-v1.md；sources.fragment.md |

记录披露：已登记的本题分析与开发原生均可定位；初始化总览因含跨题内容排除，材料主会话导出只到明示截点，Comate 格式／官方基线报告等缺口保留。材料主会话副本仅脱敏 5 条无关侧边栏索引行，原始文件未修改；原始和导出 SHA 分别登记。没有通过整理期文档替代原始研发证据。
