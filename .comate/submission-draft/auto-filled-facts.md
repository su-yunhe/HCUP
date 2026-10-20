# 已自动填入的事实及出处

只取本题真实输入、现有记录和官方逐字段模板；未猜测人工字段。事实采集时刻以 `facts.json.collected_at_utc` 为准，会话导出时刻以 `traces/session-metadata.json.exported_at_utc` 为准。

| 事实 | 自动填入内容 | 具体证据 |
| --- | --- | --- |
| 团队、题目与阶段 | HC2026-111 / Ghost_London / online / cml-spec7 | `../common/spec-harness/team.yaml`、`spec/submit-input.yaml` |
| 基线与当前Git HEAD | 75fd0066a7fc0c1e8cedb6218df081f86d307f45（完整提交版本另看project清单） | `facts.json`、`spec/metadata.json`、`workflow/baseline-provenance.json` |
| 准备执行情况 | pass，profile=harmony-cup-build-v1；dry_run=false | `logs/prepare-baseline.log`、`workflow/setup-result.json`；官方报告缺失不能混称 |
| 应用与入口 | com.joker.coolmall / EntryAbility | `AppScope/app.json5`、`entry/src/main/module.json5` |
| 构建目标/依赖 | default / entry / debug，锁定版本见build表 | `build-profile.json5`、根和模块OHPM锁文件、`hvigor/hvigor-config.json5` |
| 历史HAP | 17068002 bytes / SHA256 8aaa5de48b5664b92210fad7ffcddf9abbcebbb92e52faf7f5359bbeb3611863 | `facts.json.hap`、`logs/verification-navigation-smoke-03/install-manifest.json` |
| 当前本地验收 | 38pass / 3blocked，非官方成绩 | `facts.json.validation`、`logs/verification-final-03.json`、`workflow/verification/final-verification-03.md` |
| 完整生产输入摘要 | 26307326248e8e874d1e2d8c3a4abf10e14008d5fd386b91682357a928f6f78e | `workflow/verification/root-delivery-check-03.json`、最终验证指纹；不等于14变更文件聚合 |
| 实际AI工具/版本 | Codex Desktop App 26.1013.4894.0；各原生cli_version单列 | `facts.json.app_package`、`traces/session-metadata.json` |
| 模型/effort/token/双ID | 逐线程从原生记录读取，不重复累加累计token | `traces/session-metadata.json`、`trace-index.md`及每个原生首行/turn_context/token记录 |
| 任务书版本 | 四任务书SHA256、公共包含仓库HEAD及历史列表 | `taskbook-versions.json`；公共git顶层并非独立spec-harness仓库 |
| 日志副本与缓存排除 | 逐项路径/bytes/SHA256，以清单为准 | `logs-copy-manifest.json`；原文件未删除，生成磁盘清理拒绝记录仍保留 |
| 完整工程/资源/差异 | 最终路径与摘要以机器清单为准 | `project-manifest.json`、`project-exclusions.json`、`changes/`、`patch-validation.json` |

公开来源与读取/失败范围另见 `sources.fragment.md`，人工空字段另见 `missing-fields.md`。历史命令、产物与失败证据未冒称本材料阶段新执行。
