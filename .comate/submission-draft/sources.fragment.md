# vg-spec7 来源片段

本题随包基线：metadata.base_commit=`9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`，baseline_bundle=`repo_bundles/vignette-9cbcf7292c-base.bundle`。名称来自本题 spec/metadata.json；本阶段没有访问题包 repo_bundles 或上游。基线准备记录为 project/workflow/baseline-provenance.json 和 logs/prepare-baseline.log；官方指定 build-baselines 报告缺失，不能替代为已取得原件。基线自带图标、图片、其他素材按实际 blob 同源记录在 changes/binary-files.json，未作为本轮新增外部素材申报。

生产实现依据本题 requirement.md、批准需求和本题基线源码。除一处修改、一份新增的 settings ArkTS 文件外，保持既有服务、路由、资源和配置；不把基线项目描述为完全自研。原有许可、声明与开发文档随完整工程保留。

可核实的通用参考／工具来源（整理自当时原生轨迹及角色登记，本阶段没有重新查询上游资料）：

- 官方 ohpm 锁定开发依赖：@ohos/hypium 1.0.24、@ohos/hamock 1.0.0，解析地址与 integrity 在 project/oh-package-lock.json5；本题没有新增运行依赖。
- 本地 hmos-arkts-knowledge-retriever 携带的 ArkTS classes、Concurrency/async-concurrency-overview 和 linter 摘要；search_docs.py 因缺 references/doc_index.json 失败后直接读取文档，失败保留在 logs/do-implementation/retrieval-index-failure.log、project/traces/do-verification-build-v1/arkts-reference-search.log。已保存 Skill 与部分文档在 project/system-config；完整当时读出内容可在原生工具输出定位，不能声称所有参考文档已独立归档。
- 本地 SDK 声明 @ohos.arkui.UIContext.d.ts、@ohos.promptAction.d.ts，用于实例 PromptAction 与按钮索引类型；依据 project/workflow/design/do-design-v1.md 第 9 节及 implementation/do-v1.md 的当时读取登记。
- 华为通用文档：[全局接口多实例适配](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V13/arkts-global-interface-V13) 检索结果；[PromptAction API](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkts-apis-uicontext-promptaction) 正文抓取超时；[promptAction 模块](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-promptaction) 未取得可读正文。后两条是失败访问记录，不能用作已读技术结论。
- 公共 test-harness 与 Python Hypium 6.1.0.210；本题工程已有框架副本与 requirements，历史运行通过 common 环境调用；来源版本见随工程文件及原始调用。不把测试框架说成本题新写业务代码。
- 实际使用的 harmony-task-flow 与四角色、ArkTS 检索／语法检查 Skill 见 project/system-config/ 三个阶段快照。任务书实际副本、SHA 和 common 父仓库版本见 trace-index.md 与 traces/task-books/version.json。

用户 extra_sources 留空：【待补充】。上列是已核实记录，不是团队“无其他来源”的声明；人工额外使用情况、基线素材许可补充及团队来源保护声明由用户确认。没有为填材料访问来源项目相关修复提交、PR、Issue、补丁或其副本。材料期过滤无关侧边栏索引及跨题初始化总览的范围详见 trace-index.md，不作有利推定。
