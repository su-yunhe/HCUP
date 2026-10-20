# vg-spec14 来源片段

本文件供 `3-package.md` 汇总到成果包根 `sources.md`。证据路径以单题交付目录为基准，`project/` 表示本题工程；汇总到根文件时应再加 `tasks/vg-spec14/` 前缀。范围仅限 vg-spec14，不能代表整队或其他题目的来源声明。工程交付为manifest定义的有限投影，排除交付封套自身、两个混合总览原件和Python缓存，不能称为本地全部目录。

## 随包基线

| 字段 | 本题事实 / 状态 |
| --- | --- |
| 题目 | `vg-spec14` |
| 赛题包版本 / 提交 | `4ea7779175fc185ed70e8dc515249ec77cd55563`，记录于 `project/workflow/baseline-provenance.json`；本阶段没有重新访问题包其他目录。 |
| metadata.base_commit | `88db8789e28333c7b7dcc8db078f394a262b73c3`，`project/spec/metadata.json`。这是题包指定基线标识。 |
| 基线包记录 | `repo_bundles/vignette-88db8789e2-base.bundle`，记录大小2,792,680字节、SHA-256 `50225027e85b86be317d42b8625c9f5ca7760e0b251b9915a4b1bd0eaaa5b9c5`；出处为本题已有 `project/workflow/baseline-provenance.json`，本阶段未访问该包。 |
| 准备执行 | 本题 `project/logs/prepare-baseline.log`：profile `harmony-cup-build-v1`、`dry_run=false`、`changes=[]`；`project/workflow/setup-result.json` 登记pass。题包约定的 `reports/build-baselines/vg-spec14.log` 缺失。准备脚本独立版本及精确执行时间【待补充】。 |
| 许可证与原有声明 | 工程 `project/LICENSE` 为 GNU AGPL v3，含 Copyright (C) 2026 CLMC2025；工程 `project/README.md` 保留基线的项目、许可及致谢内容。该两文件及原有依赖清单在本次整理时相对基线无差异。本角色未访问 README 中链接指向的来源仓库。 |

## 已有记录可定位的资料、工具与依赖

以下是已核实的使用事实，不替代参赛者尚未填写的完整额外来源声明。已有研发访问记录日期为2026-10-16；外部仓库链接仅来自公共登记和事实调查，本材料角色没有重新访问链接。对应人工操作、具体引入/适配批次和原始人工证据均为【待补充】，不能用AI角色说明代填。

| 来源 | 版本 / 日期与使用方式 | 记录及随包位置 | 尚缺信息 |
| --- | --- | --- | --- |
| 赛题本地 Spec、任务书与官方材料模板 | 本题 `project/spec/requirement.md`、`project/spec/metadata.json`、`project/spec-harness/0-analyze.md` / `project/spec-harness/1-do.md` / `project/spec-harness/2-submit.md`；材料模板包括 submission-checklist、trace-index、submission.json、sources、solution、human-changes。本材料阶段读取官方模板。 | 本题原始副本在 `project/inputs/`、`project/spec/`；实际任务书与模板版本摘要由 `trace-index.md` 关联。 | 如模板文件需随包，按主Agent记录清单汇总。 |
| 基线既有 ohpm 依赖 | `@ohos/hypium` `1.0.24`、`@ohos/hamock` `1.0.0`；用于工程测试开发依赖，本题未新增业务依赖。锁文件列出 registry URL 和 integrity。 | `project/oh-package.json5`、`project/oh-package-lock.json5`，`project/logs/ohpm-install.log`。 | 各依赖许可证以分发物原有声明为准；本片段未核对其全部许可证文件【待补充】。 |
| 公共本地自测框架 | `harness.runner`、设备/环境/报告封装；Python `hypium==6.1.0.210`，实际在公共环境运行。工程内 `project/test-harness/` 的10个文档/依赖/Python文件与公共框架逐文件SHA-256相同，可随工程用于复现。 | `project/test-harness/README.md`、`project/test-harness/requirements.txt`、`project/test-harness/harness/`；历史命令在 `project/logs/do-validation/runner-v*.command.txt`，报告在 `project/workflow/verification/do-validation-v1.md`。 | 框架授权依据及 Python Hypium 发行许可证声明【待补充】。 |
| ArkTS 参考文档 | 索引缺失的检索失败被保留，随后查阅技能包 `hmos-arkts-knowledge-retriever/docs/ArkTS-Language-Guide/Basic-Syntax/concurrency.md` 的Promise/async/await与 `collection-types.md` 的Map；访问日期2026-10-16，仅作语法参考。 | `project/workflow/implementation/do-implementation-v1.md`；实现原生线程 `01a142c9-4290-7550-aeb4-dcf1a2279cc9` 的工具事件，对应定位见 `project/workflow/design/submit-facts-v1.md` §5。 | 原文档版本/许可及是否另有完整文档副本【待补充】；不声称失败检索返回了资料。 |
| 官方 SDK 类型声明 | 编译SDK `6.1.0.105 / API23`；核对 `@ohos.arkui.UIContext.d.ts` 中 FrameCallback / onFrame / onIdle / postFrameCallback；另检索过 `@ohos.graphics.displaySync.d.ts`，最终使用UIContext帧门槛。记录日期2026-10-16，仅用于接口及语义参考。 | `project/workflow/implementation/do-implementation-v1.md`、`project/workflow/design/do-design-v1.md` 与方案/实现原生线程；精确事件定位见 `project/workflow/design/submit-facts-v1.md` §5。 | 完整SDK发行许可证本片段未另行核验【待补充】。 |
| Python Hypium 随包API文档与实现 | `hypium_api_6.1.0.210.md`、`hypium/uidriver`，参考定位、滑动、输入、生命周期与组件状态；影响本地测试，非生产实现。访问日期2026-10-16。 | 独立自测线程 `01a142c5-5844-70b0-92f9-f941525030f0` 的文档检索工具调用；`project/workflow/design/submit-facts-v1.md` §5。 | API文档许可、是否另附文档副本【待补充】。 |
| `arkts-syntax-assistant` Skill | 语法/状态管理参考；common来源登记为MIT。登记链接 `https://github.com/summerkaze/skill-arkts-syntax-assistant`；链接来自已有公共清单，本题未访问该仓库。 | `project/system-config/do-stage/arkts-syntax-assistant/SKILL.md`、`project/workflow/do-config-index.json` 的摘要标识实际副本；来源调查见 `project/workflow/design/submit-facts-v1.md`。 | 原Git提交【待补充】；不以转载链接代替实际版本。 |
| `hmos-arkts-knowledge-retriever` Skill | 本地检索；`search_docs.py` 缺少 `references/doc_index.json` 失败，随后改读上述文档/SDK。公共清单登记转载链接 `https://github.com/iskenkenya/skills`；本题未访问该仓库。 | `project/logs/do-implementation/retrieval-missing-index.log`、`project/system-config/do-stage/hmos-arkts-knowledge-retriever/SKILL.md`、配置摘要。 | 原版本【待补充】；技能许可证未声明，再分发授权不明确，不作已获授权声明。 |
| `hmos-arkts-syntax-checker` Skill | 构建诊断工作流参考；实际使用可用的Hvigor。公共清单登记转载链接 `https://github.com/weikangzeng07-ops/dsh-hmos-skills`；本题未访问该仓库。 | `project/workflow/implementation/do-implementation-v1.md`、`project/system-config/do-stage/hmos-arkts-syntax-checker/SKILL.md`、配置摘要。 | 原版本【待补充】；技能内容授权未声明，不能套用转载仓库插件代码的MIT。 |
| 本题人机协作 Skill / 角色配置 | `harmony-task-flow` 与需求、设计、编码、独立验证四角色；已有配置快照而非业务实现复用。 | `project/system-config/do-stage/`，摘要 `project/workflow/do-config-index.json`；实际调用见 `trace-index.md` 指向的原生记录。 | 团队统一说明及额外自定义项由后续阶段汇总。 |

本题新增控制器、组件拆分及本地测试夹具的产生过程见 AI 原始记录；没有依据上述框架或资料表推定其他未披露来源不存在。二进制素材的基线同源、大小及SHA-256由本题完整差异与二进制清单记录；本角色未新增/替换图片、字体或其他二进制资源。

## 已发生但未采用的网络检索

依据 `project/workflow/design/submit-facts-v1.md` 对本题已有原生记录的调查，方案阶段在2026-10-16查询过 `site.harmonyos.com postFrameCallback FrameCallback onIdle UIContext` 和 `site.gitee.com/openharmony/docs postFrameCallback onIdle`。结果摘要含Gitee索引、CSDN、DeepWiki、文档镜像和无关平台PR；没有进一步打开这些结果，也未将摘要/社区示例作为最终接口依据。随后尝试打开 `https://raw.githubusercontent.com/openharmony/docs/master/zh-cn/application-dev/reference/apis-arkui/js-apis-arkui-UIContext.md`，返回404，未成功读到页面。最终依据是本机官方SDK声明。不能因此写成「没有网络检索」或「已成功阅读该官方页面」。原生方案线程为 `01a142c5-bb5c-7d80-a071-2577785ebda5`，查询、返回与404事件定位见上述事实报告；最终全局导出从 `../../traces/vg-spec14/` 及本题 `trace-index.md` 读取。

## 参赛者输入与来源保护

- `project/spec/submit-input.yaml` 的 `extra_sources`：【待补充】。不能据空值声明「无额外来源」；参赛者须补全实际额外资料/实现及访问、引入、适配、人工操作证据。
- `../common/spec-harness/team.yaml` 的 `source_guard`：【待补充】。现有 `project/AGENTS.md` 与派工明确限制只用本题工程/输入、只读公共材料与授权模板，禁止其他赛题工程和本题来源项目相关修复提交、PR、Issue、补丁及副本。此处只说明可核实的文字限制，不替团队确认完整措施或实际全程合规结论。
- 本材料角色仅读本题工程、只读公共框架/团队输入与授权官方模板；未访问来源项目修复历史，未读取混合初始化总览会话。本阶段未引入业务依赖、代码或素材。
- 人工来源操作及改码信息仍见 `human-changes.md` 的【待补充】项；记录缺失和脱敏范围以 `trace-index.md` 的实际导出审计为准，不作「无缺失」「无脱敏」推断。
