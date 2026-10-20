# cml-spec24 来源汇总片段

本片段依据本题已保存材料和本次材料工具调用整理，供成果包根 `sources.md` 汇总。`spec/submit-input.yaml:extra_sources` 留空，用户额外来源声明为 **【待补充】**，不能据此写“无额外来源”。下列已知来源和疑点仍须披露；说明来源不替代来源保护核验。

## 随包基线

| 字段 | 已核事实与出处 |
| --- | --- |
| 题目 | `cml-spec24` |
| 赛题包提交 | `4ea7779175fc185ed70e8dc515249ec77cd55563`，来自 `workflow/baseline-provenance.json` |
| 指定 base_commit | `ab3dc7cd5d05a9a3fd7d4e9ddd0a49e1a05085d8`，来自 `spec/metadata.json`、基线准备日志及 provenance |
| 随包 bundle 标识 | `repo_bundles/coolmallarkts-ab3dc7cd5d-base.bundle`；provenance 记录 5,709,350 字节，SHA-256 `8556d5fca8f4c1f2aae1c107f64b19ec8565aa186e0f6c04af1448195e472f61`。这是既有本题记录中的标识，本次材料阶段未读取题包 bundle 目录 |
| 准备配置 | `harmony-cup-build-v1`，`dry_run: false`，`changes: []`；原始记录 `logs/prepare-baseline.log`，SHA-256 `f7ea0aba784c157d844a0c92107b9110d93fc169f05177434b35ff2a96548dac` |
| 官方指定日志缺失 | 任务书指定的 `reports/build-baselines/cml-spec24.log` 未找到；主 Agent 核验后授权使用本题原始 `logs/prepare-baseline.log` 和 `workflow/baseline-provenance.json`。不能将不存在的官方路径写作已取得证据 |
| 输入一致性 | requirement SHA-256 `db94fb5440c450010739e4b8e01754bb7f54e04d7da2c719a288c1f8ead42939`；metadata SHA-256 `14dfca1519c21b5df2291df500cbd6eb7e074e6c6a0114525f0b7c94c86f200c`；见 provenance、development-result |
| 基线许可证与声明 | 工程根 `LICENSE` 为 MIT，Copyright (c) 2025 Joker.X；`README.md`、`README_EN.md` 保留项目名称及来源链接。本次材料角色未改动上述文件。整个开发差异对版权/声明的保留情况须结合最终差异核验，不能只凭本次只读检查断言全部文件未经变化 |

本题 README 中的 GitHub/Gitee/API/DeepWiki 地址是基线自带文字；本次材料阶段只读取本题 README 和 LICENSE，未打开这些地址，不将链接存在当成实际外部访问记录。

## 已识别的依赖、公共材料和工具资料

| 来源 | 实际版本/记录 | 用途与范围 |
| --- | --- | --- |
| 工程 OHPM 清单、锁文件及安装记录 | 根 `@ohos/hypium 1.0.24`、`@ohos/hamock 1.0.0`；模块含 `@ohos/axios 2.2.6`、`@ibestservices/ibest-ui-v2 1.1.1`、`@ibestservices/ibest-orm 2.0.2`、`@jjr/lottie_component_v2 1.0.1`、`@ohos/lottie 2.0.25`、`@cashier_alipay/cashiersdk 15.8.42`、`@ohos/crypto-js 2.0.5`；安装日志还记录 pako 2.1.0 | 当前工程构建依赖；OHPM resolved 指向 `ohpm.openharmony.cn`，保留清单、锁及 `logs/ohpm-install.log`。逐项许可证及与基线的依赖差异归属 **【待补充】**，不能把模块自身 Apache-2.0 声明当成全部第三方包许可证 |
| cashiersdk 随附原生库 | 锁文件含 blueshieldsdk 1.0.30、utdid_sdk 1.2.5；HAP 内 `libblueshield.so`、`libutdid_native.so` | default 保留两 arm64 库；emulator/ohosTest 按目标配置过滤不匹配库，不是获得 x86 支付实现。实际包审计 `logs/development/verification-build-v4/independent-hap-manifest.json` |
| 工作区 common 自测框架 | `../common/test-harness/README.md`、`requirements.txt`；Python `hypium==6.1.0.210` | 公共 HarnessTestCase、runner 和环境检查，本地自测；不视作官方隐藏评测器。本轮只读文件摘要为 `facts/common-test-harness.json`，3-package 汇总至 `system-config/test-harness/` |
| 本题实际工作流与角色配置快照 | `system-config/analysis-20261019T031827Z/manifest.json`、`system-config/development-20261019T041612Z/manifest.json`；harmony-task-flow 快照 SHA-256 `be2e19c305bdc68e904af8cf074186b7eaa582a76db3ca1e854ec8f1434fc3f7` | 需求、方案、编码、自测四角色调度和交接；analysis manifest 还保存 ArkTS 检索/语法检查 Skill。配置快照不单独证明其引用的全部知识库条目实际被访问，实际资料条目以原生工具轨迹为准 |
| 本机官方 Hvigor SDK schema | `development-preflight-v1.md` 引用 `ohos-module-build-profile-schema.json` 和 `hvigorfile-configuration/module-schema.json`；已有摘录 `logs/analysis-baseline/abi-filter-sdk-schema-excerpt.json` | `targets[].config.buildOption`、`externalNativeOptions`、`nativeLib.filter.excludes` 的配置位置与含义，用于本题 ABI 方案。该记录是官方通用工具配置参考，不是应用来源项目修复补丁；具体工具安装版本/文件摘要以原始工具轨迹补齐 **【待补充】** |
| 官方提交模板与本地任务书 | `templates/{submission-checklist.md,trace-index.md,submission.json,solution.md,sources.md,README.md}`；本题只读 `../common/spec-harness/2-submit.md`、`team.yaml` | 本次材料整理参考。任务书和模板实际摘要/成果包相对位置由主 Agent 记录索引补齐 **【待补充】** |

基线之外实际使用的其他资料 URL、访问时间、精确条目、许可证、引入/适配步骤及完整检索工具事件索引：**【待补充】**。本片段不能仅靠上述清单作“除此之外未使用”声明。人工选择、引入或适配来源的操作人和记录同样为 **【待补充】**。

## 真实服务数据来源

既有服务基址为 `https://mall.dusksnow.top/app/`，本题只读取证使用 `goods/type/list`、`goods/info/page`。`workflow/verification/development-preflight-v1.md` 记录 2026-10-19 UTC 04:15:44.889795 至 04:18:33.970422 的 32 次只读 POST 和 26 项契约断言，原始请求/响应字节、HTTP 头、时间与 SHA-256 保存在 `logs/development/service-contract-v1/`。

最终正常设备测试使用 58 组实际 App 请求/响应及 58 份单独的只读 oracle；其中 App 原响应 13 组完整、45 组截断，不把 oracle 填入 App 原日志。以上是运行验证数据和契约依据，不是移植实现；商品快照、销量和默认顺序不作为永久固定答案。原服务与内容授权细项：**【待补充】**。

## 过宽搜索、来源疑点与脱敏

1. **开发自测预检的过宽递归检索。** `workflow/verification/development-preflight-v1.md` 明确记录：一次本题根递归 `rg` 意外命中 `traces/native` 的会话归档片段，发现后停止使用该结果，后续限定明确源码目录和证据文件；`development-verification-v5.md` 也保留该事项。本片段据实保留这一行为，不将“已停止使用”当成未发生访问，也不凭备注断言命中内容完全不涉及受保护材料。已自动定位实际调用：自测会话 `01a1525d-74e1-7c63-9036-70f1490169f9` 原生 JSONL 第48行，UTC `2026-10-19T04:14:45.727Z`，邻接返回及后续记录为第49–55行；逐行摘要见 `traces/source-review-events.json`。来源核验结论仍为【待补充】，不能由材料整理作有利推断。
2. **本次材料阶段的会话归属索引清点。** 主 Agent 按工程路径和题号两维反查原生记录，报告命中 52 个候选；其归属筛选只检查命中文件 `session_meta`，多数为其他工作区模板提及题号，排除后未作为本题研发参考。一次 metadata 清点的工具返回意外含非本题会话 ID / cwd；主 Agent 将在当前材料导出副本中明确脱敏该返回并登记行号及原始 SHA-256，本机原文件保留。这里披露的是索引 metadata 清点，不能改写成读取其他题工程源码，也不能据此宣称全部来源疑点已消除。准确脱敏副本及原始行 SHA-256 已自动记入 `traces/redactions.json`；本轮主会话原生文件位于 `traces/native/`。该返回保留记录标识、调用及脱敏说明。
3. **本次材料子 Agent 的文件枚举。** 首次在本题根用 `rg --files` 枚举配置/命令文件时，输出包含本题 `logs/analysis-baseline/abi-diagnostic*` 中的配置文件名；未读取这些诊断副本的工程源码，随后限定当前工程实际配置与明确命令记录。该次调用保留在本材料子会话 `01a152ef-e16d-77d3-8237-b522d7e8dcfd`；不把文件枚举描述为新功能依据。

初始总览会话涉及公共环境、官方示例和其他题工程准备，不应作为本题功能开发依据。本片段未读取该总览内容；对历史记录的实际访问范围仍依赖保留的完整轨迹核验。

团队 `source_guard` 字段为空，按输入规则为 **【待补充】**。当前题目录指令要求隔离本题、common 只读及禁止来源项目相关修复历史；指令存在、人员报告和实际工具调用须分别记录，不能互相替代。来源保护是否满足及存在疑点的最终结论留待原始记录审查，本片段不作推测性有利解释。

## 本轮材料校验的失败与调整

初次日志复制全量复核发现宿主模拟器 Log/ 下5个源文件与2个副本摘要不符；首次补丁生成也在 crash_server.log 检出复制时变化，未得到有效补丁。失败证据在 checks/log-freeze-failure-01.json 与独立报告F01。随后把精确宿主运行缓存目录排除，保留主动捕获的设备测试日志、截图、HAP及所有历史失败，再重新校验；这不代表生产代码回归。

首次普通本地 clone 面对共享 worktree，其行政对象复制范围可能包含共享对象；未把这些对象作为实现资料读取。本轮改用 --no-local --depth 1 --single-branch --no-tags 请求本题基线可达对象。首次尝试与终止/失败事实保留在 checks/clone-attempt-01.json 和原生工具调用，临时目录排除，不据此代作来源保护合规判断。
