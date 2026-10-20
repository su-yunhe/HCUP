# 3-package 逐题交接合同

本阶段仅完成本题提交草稿。正式团队冻结时间/版本/人工声明待补充；status=submitted为本题待汇总条目，不表示已上传。没有生成团队根文件、ZIP、邮件或执行外部提交。

1. 按 project-manifest.json 的 files 精确复制工作树到 tasks/vg-spec14/project/，先逐文件核对SHA256。不能递归复制整个本机目录。manifest覆盖基线tracked（即使匹配ignore也保留）和非忽略本题新增文件，实际删除由diff表达。
2. 排除 .comate/submission-draft/** 交付封套，因为以下材料将各放到包内真实位置；该封套含final.diff自身和校验临时clone，递归放进project无法得到有限完整补丁。这是明确披露的工程投影解释，不声称覆盖工作区字面所有路径。其他.comate过程文件仍在投影中（如有）。
3. 混合初始化总览两份原生JSONL本地保留，按manifest的精确路径/哈希从project和diff同时排除。它们含其他题内容，只用于初始化而非本题功能证据；本题独立会话与setup文件均保留。Python缓存、构建输出、oh_modules、.hvigor等不提交。
4. 把 build.md、trace-index.md、human-changes.md、changes/、logs/ 及project-manifest.json、validation.json、provenance.json、client-runtime.json、logs-manifest.json、pending-fields.md、auto-filled-facts.md、packaging-contract.md、delivery.md、workflow-result.json、materials-manifest.json、audit/复制到 tasks/vg-spec14/。不要复制 _validation/ 临时clone、探针或整库Git元数据。
5. 把本封套 traces/ 放包根 traces/vg-spec14/；保留native/、机械Markdown、过滤索引、manifest、实际代码快照。原始轨迹中私有路径只作为历史证据，不作构建依赖；脱敏若有变化需重新记录摘要/范围，不能隐去来源和失败。
6. sources.fragment.md、solution.fragment.md由3-package汇总。三个路径字段直接使用submission.json.fragment；人工字段/历史缺失不能被结构校验自动消除。
7. 补丁按现有Windows基线core.autocrlf=true checkout；再只在临时校验仓库 .git/info/attributes 写入 `* -text -filter -ident -working-tree-encoding`，用core.autocrlf=false应用binary patch。这两个步骤是还原原工作树字节的前置，不改变提交工程.gitattributes。完全命令及结果以validation.json为准。
8. 本轮活跃原生会话仅保存导出截止点前的快照。最终包冻结时3-package应再取本题已登记会话尾部，准确记录新的导出/冻结时点；若修改投影内文件必须重新生成manifest、final.diff并完整验证，不能沿用旧通过结果。

9. 本轮封套在冻结后补齐复制清单、导出路径语义和工具计数，未改投影或原生字节。冻结工程中的采集器初版只计function_call；重新采集后还需运行随封套保存的 `audit/reconcile-native-metadata.py`，分别核对function_call/custom_tool_call及其合计，不能用初版计数覆盖本轮独立复核结果。exec内嵌套调用仍按原始文本读取，不递归推算调用次数。

只读验证副本保留在本机 _validation/，便于核验。保留范围必须由manifest与diff共同约束；若3-package决定采用不同工程范围，必须同步重生差异，不能直接套用本轮patch。
