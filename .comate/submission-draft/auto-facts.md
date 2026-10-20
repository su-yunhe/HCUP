# 已自动填入的事实及出处

| 事实 | 已填写内容 | 出处 |
| --- | --- | --- |
| 团队/阶段/题号 | HC2026-111 / Ghost_London / online / vg-spec8 | `common/spec-harness/team.yaml；spec/submit-input.yaml` |
| 官方基线 | 9cbcf7292c8cc46955dc3b522ddbda41c66a61d9 | `spec/metadata.json；本地base/vg-spec8解析` |
| 应用与入口 | io.qzz.weiyu / entry / EntryAbility | `AppScope/app.json5；entry/src/main/module.json5` |
| 依赖锁/SDK | Hypium1.0.24、hamock1.0.0；锁3；target/compatible22 | `oh-package*.json5；build-profile.json5` |
| 构建及告警 | exit0；764条旧告警，新增0 | `logs/implementation-validation/round-01/build-result.json、warning-comparison.json` |
| 自测 | A1—A19本地pass；6方法分轮真实pass；138点零请求 | `logs/selftest.json；workflow/final-evidence-check.json；两轮原始报告` |
| 生成HAP | SHA256 c30a83a3523e83ee77db7ba8a827ca781aad5cd0d4f2669de293fef19b4bf229 | `实际产物重新hash；changes/build-artifact.json` |
| 实际准备记录 | harmony-cup-build-v1；dry_run=false；changes=[]；官方规定路径不存在 | `logs/prepare-baseline.log；workflow/setup-result.json；本轮文件存在性检查` |
| 客户端/CLI/模型 | Codex Desktop26.1007.2314.0 / CLI0.162.0-alpha.17.2 / gpt-6.1-sol xhigh | `Get-AppxPackage输出；原生session_meta与turn_context` |
| 会话映射/用量 | 逐会话id、session_id、parent、tokenUsage记录 | `traces/session-index.json；原生JSONL逐字段` |
| 公共任务书版本 | 四文件SHA256；本题副本同异另列；无spec/history | `provenance/taskbook-version.json` |
| 来源/人工客观边界 | AI写入证据与实际API文档访问；不代填人工声明 | `sources.fragment.md；human-changes.md；原生工具调用` |
| 完整差异/二进制/对应 | 全冻结project文件；仅派生容器/缓存/跨题内容排除 | `changes/project-manifest.json、binary-manifest.json、patch-manifest.json；validation/apply-check.json` |

正式团队冻结时间、版本和人工声明仍未提供；没有用本地技术快照时间代填。
