# cml-spec1 提交证据组织复核 r1

版本：`submission-evidence-r1`；日期：2026-10-20；角色：`harmony_design`。本轮仅复核 2-submit 的材料组织，不重新解题、不构建、不操作设备、不更改生产、测试、配置或全局状态；唯一写入为本文。其他角色正并行整理材料，本文不替代其 diff 可应用性、材料包完整性检查。

## 1. 结论与可写入片段的事实

本题已完成本地功能验收，现有记录足以支持“本地 8/8 用例通过、A1–A44 均通过”。这不是官方隐藏测试、F-point 总数或官方评分结论。材料应保留历史失败与重试、公开来源访问和人工提示，不能写成“全程一次通过”“无外部来源”或“无人工参与”。

| 事实 | 已核对入口 | 必须保留的界限 |
| --- | --- | --- |
| 基线 `7014cebd60f2181fac2a36d399ca16b3d6a175ab` | `spec/metadata.json`、`workflow/state.json` | HEAD 仍为基线，功能修改保留在工作区；不能用 HEAD 冒称新提交版本。 |
| 最终 run-r4 实际发现并完成 8 例，pass 8 / fail 0 / error 0 / skip 0 | `logs/selftest-run-r4.json`、`workflow/verification/do-result-r4.md` | 不以构建成功替代业务验收。 |
| A1–A28 明文、A29–A39 派生、A40–A44 获准策略，44 项本地均 pass | `workflow/verification/do-matrix-r4.md`、`traces/verification-do-r1/run-r4/a-matrix.json` | 5 个策略不倒写成 Spec 明文；44 不是官方 F-point 数量。 |
| 688 生产输入聚合 `2cebe8ebb0c7fcc3d15058f9dedb0843580aacf5b1f41593f3dbe4200cf9d14c` | `traces/do-implementation/source-frozen-r2.json`、run-r4 `final-audit.json` | 该指纹排除测试、workflow、日志，不能代替完整交付目录或 final.diff 指纹。 |
| HAP 20,739,960 bytes，SHA256 `d54386d3d42a6049d5af9fcece16c9d0cdbd271a2217cb008c196af177202615` | `workflow/verification/do-result-r4.md`、run-r4 `final-audit.json` | 独立构建/安装绑定同一 HAP；修复后部分构建任务缓存命中，据实保留输出。 |
| 最终交付审查 13 项均 pass | `workflow/do-delivery-validation.json` | 这是 1-do 的来源/测试绑定检查，尚不能当 2-submit 的完整 diff 应用检查。 |
| 首次独立完整构建 182 条基线文件诊断，新增/删除均 0 | `traces/verification-do-r1/independent-warning-compare-r1.json` | 既有告警保留；不称“零告警”。 |
| 最终 50 组采帧，每组 48 个真实成功样本，共 2400 JPEG | run-r4 `final-audit.json`、`verification-summary.json`、各组 `capture-raw.log` | 两次 exit255 失败采集也保留；动态证据包含引擎状态和真实屏幕形态。 |
| 本地完成时间 `2026-10-20T05:52:56.617187+00:00` | `workflow/state.json.functional_result.completed_at` | 即北京时间 13:52:56；这是本地验收完成时间，团队成果冻结时间仍由提供者填写，不能自动替代。 |
| 未执行外部提交 | `workflow/state.json.functional_result.external_submission` | 本轮也不上传、不打包团队级成果。 |

保留限制：r3 在 13:19 存在一次真实 `LIFECYCLE_TIMEOUT`，主线程处于 Window/RenderService Binder 路径；仅支持中等强度的系统生命周期/夹具交互归因。旧 PID 退出等待夹具改进后，同 HAP 的 run-r4 八例通过且未新增同类 faultlogger 项，根因仍未完全排除。无文本输入/必需网络请求/可达覆盖子路由分支，相关项明确 N/A；不能写成网络失败注入已通过。官方隐藏测试不可用、未运行。

## 2. 原生轨迹入口和实际标识

以下仅用本题已有快照复核。定义 `N`=`traces/native/20261020T055256Z-31ecad3e/2026/10/20/`，`A`=`traces/native/20261020T035403Z-ae7cfed4/2026/10/20/`。下列 10 份文件 SHA256 均与所属 manifest 匹配；JSONL 行号从 1 开始。

| 阶段/角色 | session_meta.id / thread_id | 文件（相对 N，首行例外） | 原生行数 | 快照最后事件 UTC |
| --- | --- | --- | --- | --- |
| 分析主会话 | `01a1574d-f7fd-7032-96ff-7fec7f78a664` | A/`rollout-2026-10-20T11-14-50-01a1574d-f7fd-7032-96ff-7fec7f78a664.jsonl` | 263 | 03:25:57.267Z |
| 分析需求 Curie | `01a1574f-a76b-7b40-a501-a34a767746dc` | `rollout-2026-10-20T11-16-40-01a1574f-a76b-7b40-a501-a34a767746dc.jsonl` | 209 | 03:32:57.710Z |
| 分析自测 Hypatia | `01a1574f-c26c-7e20-9ea9-ad83cbe0762a` | `rollout-2026-10-20T11-16-47-01a1574f-c26c-7e20-9ea9-ad83cbe0762a.jsonl` | 595 | 03:53:34.852Z |
| 分析方案 Hubble | `01a15750-6e04-72b1-8b4d-5c2ff6dfc61b` | `rollout-2026-10-20T11-17-31-01a15750-6e04-72b1-8b4d-5c2ff6dfc61b.jsonl` | 365 | 03:52:48.576Z |
| 分析编码审计 Plato | `01a1575b-5b42-71e2-943b-1d61058056bc` | `rollout-2026-10-20T11-29-27-01a1575b-5b42-71e2-943b-1d61058056bc.jsonl` | 108 | 03:34:03.575Z |
| 实现主会话 | `01a15796-a9f1-7d30-8387-81c60bbd3b0f` | `rollout-2026-10-20T12-34-14-01a15796-a9f1-7d30-8387-81c60bbd3b0f.jsonl` | 1546 | 05:52:56.003Z |
| 实现需求 | `01a15797-d4c2-7802-8c32-1a2436301e28` | `rollout-2026-10-20T12-35-30-01a15797-d4c2-7802-8c32-1a2436301e28.jsonl` | 71 | 04:38:07.922Z |
| 实现自测 Einstein | `01a15798-0e52-7a10-bd8e-fd7c091bb41b` | `rollout-2026-10-20T12-35-45-01a15798-0e52-7a10-bd8e-fd7c091bb41b.jsonl` | 1315 | 05:52:00.611Z |
| 实现方案 Halley | `01a15798-722e-79d0-8668-f98754c9dda5` | `rollout-2026-10-20T12-36-11-01a15798-722e-79d0-8668-f98754c9dda5.jsonl` | 290 | 05:01:11.743Z |
| 实现编码 Huygens | `01a1579e-dd21-7b11-a80b-23fc553e29e4` | `rollout-2026-10-20T12-43-11-01a1579e-dd21-7b11-a80b-23fc553e29e4.jsonl` | 268 | 05:01:52.660Z |

所有上述文件 L1 为 `session_meta`，L10 为首个 `turn_context`，均显示实际模型 `gpt-6.1-sol`、`effort=xhigh`。L1 显示 `originator=Codex Desktop`、`cli_version=0.163.0-alpha.10.2`、cwd 为本题。主会话 source=`vscode`；子会话 source.subagent.thread_spawn 给出真实 parent_thread_id、agent_path、昵称和角色。客户端其他版本及精确模型构建版本不能由此推断。

必须区分 `session_meta.id` / `token_usage_record.thread_id` 和 `token_usage_record.session_id`：子会话后者实际继承父 ID。不能把继承值当本子会话 UUID，也不能据此伪造两个不同产品 ID。2-submit 中的 Comate `sessionUuid` / 侧边栏 ID 字段在本机 Codex 证据中没有同名结构：应解释产品与字段映射，引用实际 thread_id 和 L1，而 Comate 专有字段写“不适用（实际使用 Codex）；独立侧边栏映射未核实则【待补充】”。

最新 manifest 不含分析主会话，故不能仅提交最新快照。A 中该主会话虽然于 03:54 制作快照，其最后事件仅到 03:25:57；快照生成时间不是记录覆盖截止时间。主 Agent 已报告在本题原生存储发现原片和后缀分段，应逐 segment 导出、保留各自原始字节与事件时间，不拼接伪装原文件。本报告不把尚未逐段核对的后缀当已读证据，也不把较早快照截止误称原数据丢失。

严禁读取/复制初始化总览 UUID `01a13fc4-2611-7761-a580-1283e0c70541`。本轮仅看见其排除声明及路径清单，未打开其原生内容；`traces/native/20261020T031347Z-6162c371/` 不应整目录进入本题解题材料。

Token 入口为每段的 `token_usage_record`（usage、turn_token_usage、thread_token_usage）和 `event_msg.type=token_count`；按 segment 列原始口径，不跨快照相加，不冒称账单。原片中实现自测 L1313 的 thread_token_usage.total_tokens=`31233337`，L1314 token_count 的 total_tokens=`30901477`，两种原生累计值已不完全相同，应同时保留字段及来源而不自行“纠正”。

## 3. 实际 Skill、工具和配置索引

| 实际使用项 | 真实调用入口 | 归档入口/版本证据 |
| --- | --- | --- |
| harmony-task-flow | 分析主会话 L19；实现主会话 L19；实现方案 L18 | `system-config/analysis-20261020T034136Z/manifest.json`；`system-config/implementation-20261020T043624Z/skills/harmony-task-flow/`；SKILL SHA256 `be2e19c305bdc68e904af8cf074186b7eaa582a76db3ca1e854ec8f1434fc3f7`。 |
| arkts-syntax-assistant | 分析方案 L18；分析编码 L30；实现方案/编码 L18 | implementation 快照 `supplemental-skills/arkts-syntax-assistant/SKILL.md`；SHA256 `3819b8534ada65c06d9b30935514232785b2599d5ac06190360938752265f3e2`。 |
| hmos-arkts-knowledge-retriever | 上述方案/编码；实现主会话 L241 | implementation 快照 `supplemental-skills/hmos-arkts-knowledge-retriever/SKILL.md`；SHA256 `f46bde5b21ba1b1849c171917885ce4790c32da35790df617bb31e0094190304`。检索脚本缺索引失败也须保留。 |
| hmos-arkts-syntax-checker | 分析自测 L21；实现自测 L18/L293；实现编码 L18 | implementation 快照 `supplemental-skills/hmos-arkts-syntax-checker/SKILL.md`；SHA256 `9746eadf1bdbd14cb418a3aa9f7958d356e896eb14cce2d8569dac484ff3f830`。实际用 hvigor 诊断，不宣称调用不存在的 linter/MCP。 |
| 四角色定义及流程脚本 | session_meta 角色/parent；主会话派工调用 | `system-config/implementation-20261020T043624Z/agents/`、`skills/harmony-task-flow/scripts/`、`references/`；分析快照 manifest 有角色定义摘要。 |
| functions.exec 及嵌套工具 | JSONL `custom_tool_call.name=exec` 与 input；配对 call_id 的 `custom_tool_call_output` | 实际出现 `exec_command`、`apply_patch`、`write_stdin`、`view_image`；代码和返回结果以原生记录为准。 |
| 协作工具 | JSONL `function_call` | 实际出现 `spawn_agent`、`send_message`、`wait_agent`、`followup_task`、`list_agents`；分析主会话另有 `request_user_input_async`；实现方案有 `sleep`，自测有 `wait`。可用工具提示不等于已使用工具。 |
| 公开检索 | 实现方案 L52/L60/L82 的 exec 内 `tools.web__run` | 第4节列实际请求/结果；registry/HAR 还通过 PowerShell/Python 请求。 |
| 构建、运行与观察工具 | `logs/*commands*.json`、原生 exec input/output、独立报告 | Git、PowerShell、Python、ohpm、hvigor、hdc、Hypium、harness.runner；精确 argv/版本按对应日志，不把目录中存在的软件都列为实际使用。 |

本次读取四份 common 任务书和本题副本逐字一致；只读 `git -C D:/HCUP/common rev-parse HEAD` 得 `e9befa727bcd94f2eea263bd3c92c56d9f8ec6ac`。当前文件 SHA256：0-analyze=`a0518cb663406e9a25c2a8096799ddbb79253e1f874819b6099a38c2819c944a`，1-do=`2f02be9274ea7e68e7863a319382fc250a9ea845fa5fa0c124effc5524ee337d`，2-submit=`43455fc9ef3c6d0ddbcf0dc101201796ebec865e214929f3137b1bb4036895f9`，3-package=`3a97a8072042c29adde571af04da1658d0b1547e9c41cdd649e02fba04ae6b9c`。记录“当前核对版本”，不推测更早时刻版本；本题 `spec/history/` 当前不存在。

配置变更不能仅依据 state 就填“无”，也不能仅因存在多份快照就断言内容改变：state 记录 initial / analysis / implementation 三阶段快照，应解释初始准备与正式功能阶段并核对实际差异；确无内容差异的配置可据实注明。initial 配置文件不是初始化总览对话本身，但不能因此把总览会话改当本题功能证据。团队 source_guard 空字段仍待提供者补充，日志中已有本题边界与来源限制可独立列为已观察配置。

## 4. 公开来源访问和代码复用建议条目

以下行号均指“实现方案 Halley”上述 N 文件；本轮没有重新联网。

| URL | 实际用途与结果 | 原生入口 |
| --- | --- | --- |
| `https://gitee.com/openharmony-tpc/lottieArkTS/blob/master/README_zh.md` | 通用动画库维护方 README，成功取得正文；Canvas、DOMLoaded、首帧/播放、颜色、按 name 销毁等 API 参考。README 中自带图片/示例 JSON、Issue/PR 链接的出现，不等于实际点击/下载；不能把它们列为已复用素材。 | L60 请求；L64 返回；`workflow/design/do-design-r1.md` §9。 |
| `https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Flottie` | 实际打开，只有仓库门户一行，不能据此称读全包 API。 | L60/L64。 |
| `https://ohpm.openharmony.cn/ohpm/@ohos/lottie` | L82 查询 metadata，成功返回 latest 2.0.33 和候选 2.0.16 元数据；L94 再实际读取 2.0.33 元数据。 | L82/L87；L94/L97。 |
| `https://ohpm.openharmony.cn/ohpm/@ohos/lottie/-/lottie-2.0.33.har` | L94 在内存下载并读 package/index.d.ts，成功 207550 bytes，sha512_ok=True；MIT、dependencies={}；实际最终安装版本 2.0.33。 | L94/L97；`logs/do-ohpm-install-r1.log:3`；锁文件。 |
| `https://developer.huawei.com/consumer/en/doc/harmonyos-references-V13/ts-container-swiper-V13` | L52 搜索返回可读摘要；L82 直接 open 返回 Internal Error，不能宣称直接打开全文成功。 | L52/L56；L82/L87。 |
| `https://developer.huawei.com/consumer/en/doc/harmonyos-references-V13/ts-container-scroll-V13` | 实际 open，返回 Total lines:0，没有可核实正文。 | L60/L64。 |
| `https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-new-param` | open 返回 Internal Error。 | L60/L64。 |
| `https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-new-monitor` | open 返回 Internal Error。 | L60/L64。 |
| `https://developer.huawei.com/consumer/en/doc/harmonyos-guides-V14/arkts-v2-decorators-V14` | 搜索返回的官方索引；不是本记录中的直接 open 请求。 | L82/L87；设计 §9。 |

L52 的三个实际搜索串为 `site.ohpm.openharmony.cn @ohos/lottie loadAnimation animationData playSegments goToAndStop`、`site.gitee.com/openharmony-sig/lottie lottie 2.0.24 loadAnimation RenderingContext`、`site.developer.huawei.com SwiperController changeIndex onChange cachedCount Scroller scrollTo ArkUI`。L82 两个搜索串为 `site.developer.huawei.com "@Monitor" "@Param" ComponentV2` 和 `site.developer.huawei.com "scrollTo" "animation" "currentOffset" "Scroller"`。搜索串中的 2.0.24 不是实际安装版本；候选 2.0.16 元数据查询也不等于采用它。

搜索返回不全是官方页面。L87 可见以下额外结果 URL，只能标“搜索结果/摘要被工具返回，未见对应直接 open、未据此登记代码复用”，不得隐去后笼统称“全部来自官方”：

- `https://developer.huawei.com/consumer/cn/blog/topic/03184612822676181`
- `https://developer.huawei.com/consumer/cn/doc/best-practices/bpta-smart-reach`
- `https://developer.huawei.com/consumer/cn/doc/harmonyos-references-V13/ts-container-scroll-V13`
- `https://developer.huawei.com/consumer/cn/doc/harmonyos-references/ts-container-scroll-0000001821000913#ZH-CN_TOPIC_0000001821000913__scroller`
- `https://developer.huawei.com/consumer/cn/forum/topic/0204227187849954105`
- `https://developer.huaweicloud.com/tags/202904/blog_15`
- `https://bbs.huaweicloud.com/blogs/479395`
- `https://ai6s.net/6902d4b482fbe0098ca67206.html`
- `https://ai6s.net/6974a55ca16c6648a984c15c.html`
- `https://bbs.itying.com/topic/676dca825b798701ddf82551`
- `https://download.copadata.com/fileadmin/user_upload/Downloads/Dokumentation/820SP0/ENGLISH/Manual/Screens.pdf`
- `https://gitee.com/harmonyos-cases/cases/blob/master/CommonAppDevelopment/feature/listslidetohistory/README.md`
- `https://harmonyosdev.csdn.net/688c5e4c080e555a88d430e4.html`
- `https://harmonyosdev.csdn.net/6a1d569010ee7a33f276e7f0.html`
- `https://jishuzhan.net/article/2062823998492323841`

来源片段建议使用以下实质内容（再按最终包内相对路径改链接）：

> cml-spec1 以随题基线 `7014cebd60f2181fac2a36d399ca16b3d6a175ab` 开展；基线资源及既有依赖随工程保留。本题新增固定依赖 `@ohos/lottie@2.0.33`，来源为 OHPM 官方 registry/HAR，许可证 MIT，实际 lock 和安装日志可核对。参考通用库维护方 README、华为 API/装饰器检索结果、本地官方 SDK 声明及 ArkTS 技能包资料。部分官方页面打开失败及工具返回的额外搜索摘要已保留在原生记录。本题四个 Lottie JSON 和六个商品 SVG 由 AI 在本题实现过程中编写，见实现原生修改和交接记录；基线自带图像不能误列为新外部素材。提供者 extra_sources 仍为空，补充声明为【待补充】；不据此宣称无额外来源。

既有依赖与基线素材的许可证/来源以工程随包清单为准，本报告未逐项重审全部 677 个基线文件，不能新增“全部来源已审计”的断言。不得读取来源应用的修复历史来补证。

## 5. 必须保留的真实失败与重试链

| 阶段/指纹 | 原始失败入口 | 最小处理及后续结果 |
| --- | --- | --- |
| 基线模拟器 CreateFiber / 内存不足 | `workflow/verification/baseline-r1.md`、相关 analysis-baseline-r1 日志 | 用户选择释放一台后使用本题独立实例；r3 建立 11245。不能删去 r1/r2。 |
| 拒绝麦克风后系统设置前台 | `workflow/verification/baseline-r3.md` §2、r3 permission/recent-tasks 原始树图和 commands | 保持拒绝，经正常最近任务恢复 app 主窗口；不当作崩溃/许可绕过，也不当作四标签返回。 |
| 基线四标签缺失 | baseline-r3 与 `spec/baseline-notes.md` | 真实 2 fail / 15 blocked；随后 1-do 才实现，不能改写基线状态。 |
| 截图/树 recv 私有绝对路径被误解，hdc exit0 但 stdout [Fail] | `logs/analysis-baseline-r3-first-*-recv*.json`、baseline-r3 §2 | 改相对路径后成功；原失败和前后状态时差保留。 |
| 文档验证误认为假设表六列 | `workflow/analysis-validation-initial-parser-failure.json` | 修为 A40–A44 七列；保留原断言及失败，非改需求规避。 |
| 命令索引混时区 | `traces/baseline-analysis/r3/command-index-v1-mixed-timezones.csv`、`command-index-rebuild-audit.json` | 28 原始记录哈希不变，119 行统一 UTCZ；旧 CSV 不删除，也不用来判断时间。 |
| 本地知识检索脚本缺 doc_index | 实现方案 L44 调用及紧随结果；实现交接 r1 技能节 | 未改技能包，改 rg 直读语言/API文档及官方资料。 |
| 官方页面 open 空/错误 | 实现方案 L60/L64、L82/L87 | 区分可读搜索摘要、维护方 README、真实 SDK 类型和编译证据；不冒称打开成功。 |
| snapshot_display 拒绝 PNG 后缀，hdc exit0 | `logs/verification-do-probe-run-r1-first-screen.log` | 改匹配 JPEG 并检查实际输出失败；保留试探失败。 |
| /proc/uptime 权限不足中断采帧 | `logs/selftest-run-r1-interrupted.json` | 改真实 date+JPEG 48帧采集；保留原始中断，未削弱动画断言。 |
| 单次分类点击 H→C→H | `workflow/verification/do-failure-r1.md`、`traces/verification-do-r1/repro-tab-reset-r1/` | 仅 MainPage `.index(0)`→`.index(this.vm.selectedIndex)`；`workflow/implementation/do-handoff-r2.md`；r2 独立构建后的原生 click/left-swipe 回归通过。 |
| r2 离屏领取节点被 UI dump 省略 | `traces/verification-do-r1/run-r2/test_04_scene_four_scroll_and_reselect/failure.json` | 解析器先验证原锚点、真实偏移/截图/同实例，再接受离屏省略；回顶仍检同 ID、文本、原生节点及可视交集；run-r4 场景四通过。 |
| r3 短 stop/start 间隔下 LIFECYCLE_TIMEOUT | `logs/verification-do-run-r3-sysfreeze.log`、run-r3 场景四 failure.* | 夹具等待旧 PID 连续不存在并停稳，只发送一次 start；run-r4 无新增同类 fault，但根因未完全排除。 |
| r3 一次、r4 两次截图 exit255 | run-r3 场景五 failure.*；run-r4 场景三 `03_me_return_home/capture-raw.log` | 仅采集位置按上限重试；保留失败/时间，无用户动作或启动重放；最终每组48真实帧。 |

可选 PIL 未安装导致的离线像素比较未运行，见 baseline-r3 §5；不据此称像素/动画通过。业务动画通过依据后续真实 ROI/引擎/帧断言。未采用方案还包括通知演示基线、静态图标冒充 Lottie、将点击和 onChange 各自提交造成重复播放等；仅把原生讨论明确出现的选择登记为候选，不能事后编造探索。

## 6. 人工、提供者信息、缺失与脱敏

`../common/spec-harness/team.yaml` 已提供 team_id=`HC2026-111`、team_name=`Ghost_London`、stage=`online`；version、contact、freeze_time、members.name/work、source_guard 均空。`spec/submit-input.yaml` 的 human_edits、known_issues、extra_sources、md_export_dir 均空，按任务书逐项标【待补充】，即使存在相关日志也不代填提供者声明。

已观察到的人工提示/选择：分析主会话 L15 为启动 0-analyze 的用户请求，L258 为选择释放一台模拟器后使用独立实例的问答响应；实现主会话 L15 为开始 1-do 的用户请求。主 Agent 转达和实际正常停止命令记录见 baseline-r3 §1 及 `logs/analysis-baseline-r3-stop-result.json`。这些是人工授权/提示与 AI 工具操作的证据，不能改写成操作人已实名、人工亲自执行停止或人工直接修改代码。

人工直接改代码：提供者未填，写【待补充】；原生中有 AI apply_patch 也不能排除记录外人工编辑。已知问题：将第1节客观历史限制列出，同时保留提供者 known_issues【待补充】。额外来源：第4节的实际访问可自动填写，同时保留提供者 extra_sources【待补充】。

Markdown：md_export_dir 为空。可从原生 JSONL 生成明确标记的“派生 Markdown 副本”，注明脚本版本、导出时刻、源 SHA 和行号；不能称其是 IDE 侧边栏导出。Comate store / macOS product.json 不适用于当前产品环境，不应制造记录或访问整库替代。独立侧边栏 ID/对应关系仍需真实证据或明确记录缺失。

基线准备日志：本轮只检查允许的 `D:/SWE-OpenHarmony/reports/build-baselines/cml-spec1.log`，路径不存在，无法提供该脚本版本/时间/输出。可引用本题独立 clean/build 日志证明实际基线构建，但不能将它改名冒充题包准备脚本日志。

脱敏范围：应由最终导出动作给出实际规则与清单；本轮未对原生文件作任何脱敏修改，不能提前写“无”。禁止把初始化总览和无关私人会话放包；路径/用户名脱敏不应遮蔽来源与代码依据。最终各 segment 截止、未导出字段、未取得的产品 ID 都应列为限制；state 中 record_gaps=[] 只是该次工作流记录，不能覆盖本次发现的材料缺口。

## 7. trace-index 字段映射与 solution 片段建议

| 官方字段 | 建议内容/入口 |
| --- | --- |
| 题号、AI环节/用途 | cml-spec1；需求拆解、方案/取舍、编码/单行修复、独立构建自测、失败归因和材料整理；分配到第2节各会话/segment及 workflow 产物。 |
| 基线准备 | 允许路径日志缺失，明确待补；另列本题真实基线 clean/build 的命令日志。 |
| Agent/模型/参数 | Codex Desktop 及四角色；第2节 L1/L10；不推断模型精确内部版本；各 segment 单列。 |
| Skill/提示/工具/编排 | 第3节实际调用与 system-config 快照，附 manifest/SHA；不按“可用工具”罗列。 |
| 配置变更 | initial→analysis→implementation 的真实快照与时间；工具 fallback、采集夹具变更按失败链列出，不称无。 |
| 主/关联会话 | 分析与实现两主会话+四角色，新增材料整理会话另纳入；明确 thread_id 与 inherited session_id。 |
| 原始日志/读取 | JSONL 每行独立 JSON；tool_call/output按call_id配对；segment/manifest有 bytes、SHA、事件范围；日志和树图保持原文。 |
| 失败/重试/未采用 | 第5节；失败日志、旧脚本版本、原始输出都保留。 |
| 提示/检索/代码/构建/自测 | 原生消息/工具input+output、来源登记、source-frozen、全部 build/run命令、run-r1至r4、最终矩阵。 |
| 导出时刻/方法 | 按本次实际导出写；原生复制与派生Markdown分开；snapshot_only/include_future_events限制保留。 |
| 冻结时间 | 团队 freeze_time【待补充】，另列本地1-do完成时间，不能混用。 |
| 基线/最终标识/diff | 基线 metadata；最终完整交付清单/摘要由材料角色生成；不能只填688生产聚合；最终 `changes/final.diff` 应应用校验。 |
| 对应提交源码 | 完整目录相对路径清单+摘要、diff应用及关键文件比对；排除构建噪声；另指生产/HAP/测试绑定。 |
| 人工操作/修改 | 第6节已观察提示/选择+human_edits【待补充】，若发生人工修改需当时差异/快照，不以总体diff替代。 |
| 来源/保护 | 第4节基线/依赖/文档/搜索结果；本题 AGENTS 与角色限制的实际配置；团队 source_guard【待补充】。 |
| 脱敏/记录缺失 | 最终实际导出清单；当前基线准备日志、产品ID映射、提供者字段等；后缀未逐段复核前不称完整。 |

solution.fragment 建议正文：

> cml-spec1 已在本地完成四标签导航、点击/横滑联动、真实本地 Lottie 选择播放与离开复位、首页同标签回顶和批准边界策略。独立 Hypium runner 最终 8/8 用例通过，明文28项、派生11项、批准策略5项共44项本地通过；详见最终矩阵与原始记录。生产冻结清单、独立构建 HAP 和测试来源在 final-audit/交付检查中相互绑定。AI 实际参与需求、方案、编码、失败修复和独立验证；人类提示与模拟器选择记录另有索引，团队人员分工和人工直接修改声明仍为【待补充】。历史一次系统生命周期超时的根因未完全排除，最终运行未复现；官方隐藏测试与评分未取得。公开库/文档使用、失败重试、记录导出限制如实披露；未外部提交。

## 8. 收口顺序、权衡及本角色验证

材料角色先按本题 allowlist 导出所有原片/后缀分段并建逐段索引，再生成来源、人工与完成情况片段；随后定稿完整项目文件清单，生成含新增过程文件和二进制的 final.diff，基线临时 checkout 做 apply --check 并比对关键文件，最后写入校验结果。若工程包含 `.comate/submission-draft/`，须明确哪些物理文件随 project 交付并保持 diff 一一对应，避免把生成中的 diff 自身递归纳入；不能静默漏掉其他真实过程文件。本角色仅提供这一组织建议，未执行该校验。

权衡：以原生 JSONL+分段manifest为事实，以 Markdown/索引为可读派生物；保留较早快照但去除无关总览，不把多个快照/累计token拼成单段事实。把“客观日志可自动填”与“提供者空声明待补”并列，材料可复核且不推测有利结论。

本轮已核对：官方三份模板、2-submit、state、run-r4报告/矩阵/机器检查、上述10份本题原生快照摘要和SHA、system-config可用入口、common版本和四文件摘要、来源原生请求/结果。未修改其他文件，未构建、安装、启动或重新测试。未解决项：提供者空字段、准备脚本日志缺失、独立侧边栏/产品字段映射、后缀逐段导出与完整交付diff校验，均由主 Agent 按现有授权继续处理或明确留缺。
