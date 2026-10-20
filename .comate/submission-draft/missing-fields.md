# 仍需补充的字段与真实证据缺口

以下原始人工字段为空，全部保持 **【待补充】**，没有自动改为“无”：

| 字段 | 原始输入 | 待补内容 |
| --- | --- | --- |
| human_edits | `spec/submit-input.yaml` | 【待补充】：声明是否人工直接改码；有则提供人/目的/文件/前后版本/当时证据 |
| known_issues | 同上 | 【待补充】：人工已知问题声明；本题已观察限制另据事实列示，不能代填“无” |
| extra_sources | 同上 | 【待补充】：人工额外来源声明；已有公开研究记录不能替代人工完整声明 |
| md_export_dir | 同上 | 【待补充】：IDE手工Markdown导出目录；已有机械JSONL可读副本不是该导出 |
| version / contact / freeze_time | `../common/spec-harness/team.yaml` | 【待补充】：正式成果包版本、联系人、北京时间冻结时刻 |
| members[0].name / work | 同上 | 【待补充】：真实成员姓名与人工分工；不从本机用户名或AI角色推断 |
| source_guard | 同上 | 【待补充】：人工填写实际来源保护措施；已有规则配置不代填该声明 |

`team_id=HC2026-111`、`team_name=Ghost_London`、`stage=online`、`task_id=cml-spec7`已有明确输入；`submitted_tasks=[]`、`attempted_not_submitted=[]`、`zip_out=""`由3-package处理，不阻断本题材料整理。本题JSON当前保守not_completed，拟定路径与完成范围已解释。

## 记录缺口和非人工字段

- Comate `sessionUuid`、客户端和扩展版本：**【待补充】 / 不适用**。实际使用Codex，检查未发现Comate索引，不能编造Comate值；证据见 `traces/discovery.json`、`facts.json`。
- 无侧边栏索引的子Agent独立IDE ID：**【待补充】**。本体线程ID可从原生 `session_meta.payload.id` 证明，父子关系可读；不能复制父ID当子ID或宣称独立IDE对应已证明。逐项见 `trace-index.md`。
- 官方 `reports/build-baselines/cml-spec7.log`：**缺失**，见 `taskbook-versions.json.official_baseline_report`。本题 `logs/prepare-baseline.log` 是不同的既有证据；它不带独立执行起止时刻，`workflow/setup-result.json.prepared_at` 是准备完成登记时间，不能冒充脚本精确起止时间。现在补跑不能变成历史原件。
- 初始化独立hdc stdout捕获不完整：见 `facts.json.original_record_gaps`、转录JSON、原生工具返回与后续完整输出；不宣称原缺口已补回。
- 没有提供IDE“导出本地”Markdown路径；当前 `traces/markdown/` 由原生JSONL逐对象机械生成，明确标记，不冒称IDE导出。
- 原生记录为各自导出截止切片，活动会话后续事件和3-package行为尚未发生/尚需后续导出。导出时间与hash以 `traces/session-metadata.json` 为准，不能覆盖未来。
- B9–B11真实授权需要合法平台账号、应用身份/签名回调及服务端契约；本阶段不能用材料消除阻断，也不为补日志重跑业务。

团队打包前需补齐人工字段、正式提交选择及冻结时间，依据最终元数据刷新索引并重新校验完整工程与补丁；上述缺失均据实保留，不能由排版或示例值填满。
