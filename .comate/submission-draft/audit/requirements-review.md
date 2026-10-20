# vg-spec1 材料需求独立复审

审查结论：**已准备材料通过，仍待用户字段和最终会话截点刷新**。不是正式可提交/已提交认定，也不证明全部硬约束或全程合规。审查时间：2026-10-17 12:33:18 UTC。原生会话：`01a149cb-a1d7-7711-af7b-8144cd1945fd`。

只修改本报告及同名 JSON；未改生产、测试、原工作流或其他材料。完整检查、限制和审查输入 SHA-256 见 requirements-review.json。

## 已核对

- 官方 trace-index 的 24 个字段标签全部出现，逐项状态见下表；缺证和用户空项均明示，没有用“无”替代空白。
- 13 个独立原生会话确为 8 个分析/开发及 5 个材料会话；混合初始化总览被排除。3 个主会话 Codex 侧边栏映射有真实索引行，子会话及 Comate 双 ID 不伪造。13 份 native 和 13 份 Markdown 的 SHA-256 均与 sessions.json 相符。
- 完成情况保留 28 本地需求/19 计划用例与官方 F-point 的区别；旧 HAP/设备复用、WFP 真实传输隔离与 guest LinkUp、服务零到达、历史失败/诊断缺失和未承诺注入项的限制均保留。
- 四任务书的工程/common 当前 SHA、三官方模板 SHA、团队/题目输入 SHA 均独立核对相符；无 spec/history。当前阶段 Skill/references/四角色共 8 项快照 SHA 相符，父工作区提交没有冒充本题功能提交或完整历史版本。
- 4175 个 manifest 路径唯一；84 排除项为 64 个模拟器运行文件、6 个 pyc、14 份混合初始化原文。与 manifest 无交集，无 entry/AppScope 业务文件排除，draft 自身未递归纳入 project。说明明确这是一份交付投影，与未经筛选的本机全目录不同；我未重跑补丁或 4175 文件逐字节比对，只核对其审计记录与材料表述。
- JSON 片段可解析，五个任务字段及三个包内相对路径符合模板。status=submitted 仅作为拟汇入任务清单的片段，结合草稿状态不能解释为已上传、已冻结或可正式提交。
- Windows OpenAI.Codex 26.1013.4894.0 的当前采集记录与 CLI 版本分开；不倒推历史版本或冒充 Mac/Comate 扩展。有限密钥模式扫描的两个命中已记录为 encrypted_content 随机子串误报，不能升级为完整秘密或来源合规审计。

## 逐字段映射

| 序号 | 官方字段 | 草稿状态 | 草稿位置 |
| --- | --- | --- | --- |
| 1 | 题目 ID | present | trace-index.md:3 |
| 2 | AI实际参与环节与会话范围 | present | trace-index.md:4 |
| 3 | 基线构建准备版本/时间/输出 | present_with_disclosed_gap | trace-index.md:5 |
| 4 | Agent名称及版本 | present_with_disclosed_gap | trace-index.md:6 |
| 5 | 模型版本及参数 | present_with_disclosed_gap | trace-index.md:7 |
| 6 | Skill/提示/工具/编排配置版本及位置 | present | trace-index.md:8 |
| 7 | 运行期间配置变更及原因 | present_with_disclosed_gap | trace-index.md:9 |
| 8 | 主会话ID | present_with_disclosed_gap | trace-index.md:10 |
| 9 | 关联及子会话ID | present_with_disclosed_gap | trace-index.md:11 |
| 10 | 全部相关原生记录及读取方式 | present_with_snapshot_boundary | trace-index.md:12 |
| 11 | 失败/重试/未采用方案 | present | trace-index.md:13 |
| 12 | 提示/工具/检索/编辑/构建/自测位置 | present | trace-index.md:14 |
| 13 | 导出时间/方法/读取方式 | present_with_disclosed_gap | trace-index.md:15 |
| 14 | 北京时间成果冻结时间 | pending_user_field | trace-index.md:16 |
| 15 | 官方基线及最终版本标识 | present_with_pending_team_version | trace-index.md:17 |
| 16 | 完整差异及二进制清单位置 | present_with_projection_boundary | trace-index.md:18 |
| 17 | 与提交源码对应关系 | present_with_projection_boundary | trace-index.md:19 |
| 18 | 人工操作及记录 | present_with_pending_user_declaration | trace-index.md:20 |
| 19 | 人工修改索引 | present_with_pending_user_declaration | trace-index.md:21 |
| 20 | 人工修改人/目的/文件/前后版本/原始证据 | pending_user_field | trace-index.md:22 |
| 21 | 公开检索/复用及来源条目 | present_with_pending_user_declaration | trace-index.md:23 |
| 22 | 工作目录及来源保护配置 | present_with_pending_user_declaration | trace-index.md:24 |
| 23 | 脱敏范围 | present_with_disclosed_limitations | trace-index.md:25 |
| 24 | 记录缺失及原因 | present_with_disclosed_gap | trace-index.md:26 |

## 已修复的问题

1. solution.fragment.md:19 已把排除清单引用修复为根 solution.md 汇总后可定位的 `tasks/vg-spec1/audit/excluded-files.json`。
2. trace-index.md:8 已明确指向 `audit/current-config/manifest.json`，可定位本次实际配置的保存位置和 SHA。

本范围内无剩余材料文字/字段修复项。

## 仍待完成的输入和边界

团队 version、contact、freeze_time、members[].name/work、source_guard；本题 human_edits、known_issues、extra_sources、md_export_dir 均仍待用户提供。Comate 双 ID、不可得历史版本/参数、官方基线原报告及脚本精确身份/时刻、旧 helper05/06 缺失诊断等继续如实披露，不以新日志补造。3-package 的三项团队输入不在本轮决定。

主 Agent 结束本次审核后刷新同一 13 会话截点并校验新摘要；本报告 JSON 中的 sessions.json SHA 仅标识审查时快照。正式冻结、团队汇总、全量敏感信息终核和 ZIP 属于后续获授权阶段。3-package 必须按同一 manifest 复制工程；若范围变化，应重新生成并验证 diff。此次通过不消除用户待补字段，也不等于全目录打包、官方成绩或正式可提交。

