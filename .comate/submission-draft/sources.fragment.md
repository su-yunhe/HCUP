# vg-spec8 来源片段

随包基线：本题 `spec/metadata.json` 指定 `9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`，bundle标识 `repo_bundles/vignette-9cbcf7292c-base.bundle`。原有代码、资源、依赖与文档来自该基线，不声明为本次原创；在已核验的AI原生记录范围内，未见从来源应用上游当前实现或相关修复历史获取本功能代码的证据；这不代表对未知人工操作或团队额外来源的保证，相关声明仍【待补充】。基线来源与文件摘要见project中的 `workflow/baseline-provenance.json`。

用户的 `extra_sources` 声明为空：**【待补充】**。以下是本题记录已直接证实的额外技术资料，不代填用户声明：

| 来源 | 实际用途与记录 |
| --- | --- |
| OpenHarmony docs master原始CustomDialog文档：https://raw.githubusercontent.com/openharmony/docs/master/zh-cn/application-dev/reference/apis-arkui/arkui-ts/ts-methods-custom-dialog-box.md | 方案会话原生JSONL第84行open、第87行返回；实际打开过，予以披露 |
| OpenHarmony 6.0 Release文档：https://raw.githubusercontent.com/openharmony/docs/OpenHarmony-6.0-Release/zh-cn/application-dev/reference/apis-arkui/arkui-ts/ts-methods-custom-dialog-box.md | 同会话100/104行open与返回，108/112行查成员；官方通用API资料 |
| 6.0文档GitHub页面：https://github.com/openharmony/docs/blob/OpenHarmony-6.0-Release/zh-cn/application-dev/reference/apis-arkui/arkui-ts/ts-methods-custom-dialog-box.md | 设计报告引用同一文档页面，未取应用来源实现 |
| 本地SDK CustomDialog声明、ArkTS enum/初始化/迁移指南、linter CLI声明、公共Harness | 见project/workflow/design/implementation-plan-01.md第10节、原生调用；用于语法/API/测试框架 |
| harmony-task-flow 与四角色、ArkTS相关Skills | project/system-config既有快照；本阶段未改团队配置 |

以上方案会话为 `01a14503-4b1d-7e70-943e-a0d57c675547`，原生文件位于本材料traces/native同名JSONL。搜索回包中还包含通用文档Issue等命中；命中回包完整保留，不把未点击的全部命中当实际引用。检索工具缺索引失败、后续直接读取文档的过程均保留。依赖版本和registry URL见project/oh-package-lock.json5。

新二进制材料是本题测试截图、只读数据库哨兵快照和生成HAP；未新增App二进制素材。`changes/binary-manifest.json`逐项列路径、大小、SHA及基线同源判断。混合初始化总览与非本题安装前UI不交付，范围见trace-index和排除清单。
