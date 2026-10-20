# 已自动填入的事实及出处

| 事实 | 真实来源 |
| --- | --- |
| 团队 HC2026-111 / Ghost_London / online | common/spec-harness/team.yaml 的非空字段 |
| 题号 vg-spec13；base `88db8789e28333c7b7dcc8db078f394a262b73c3` | spec/submit-input.yaml、spec/metadata.json |
| 官方基线bundle名与摘要 | workflow/baseline-provenance.json；本阶段未重读题包bundle |
| io.qzz.weiyu / EntryAbility / entry / 1.0.0 | AppScope/app.json5、entry/src/main/module.json5 |
| SDK声明6.0.2(22)、空签名、模块default | build-profile.json5 |
| @ohos/hypium 1.0.24、hamock 1.0.0及锁文件 | 根与entry的oh-package.json5、oh-package-lock.json5 |
| 依赖、构建、安装、启动命令及成功记录 | logs/implementation-build/*result.json、run02/run03/run04/commands.log及install.log |
| 17 pass为run02/run04合并、未执行项和警告变化 | logs/selftest.json、workflow/local-acceptance.json、workflow/verification/final-report.md |
| 最终HAP大小及SHA | 当前HAP实物与历史hap-sha256.json；changes/verified-hap.json |
| 299项生产/配置指纹未变 | workflow/implementation/source-fingerprint-v2.json、audits/implementation-freeze.md |
| 主/子会话、模型ID、effort、CLI与token原始字段 | 按本题双维检索的Codex JSONL、traces/session-inventory.json |
| 工具清单和实际参数/返回 | traces/tools-used.json及原生轨迹 |
| 任务书版本和历史是否存在 | 四份公共/本题任务书SHA、spec/history实际存在性，traces/taskbook-version.json |
| 原始日志337个的完整复制 | logs/copy-manifest.json；保留全部失败/重试 |
| 二进制路径、大小、SHA和官方基线同源 | changes/binary-files.json、官方base对象与封存文件的逐字节摘要比对 |
| 完整封存版本、补丁可应用和逐文件一致 | traces/code-snapshot/manifest.json、changes/patch-validation.json |
| 指定官方准备报告/Comate库缺失 | 预期路径存在性检查、traces/discovery.json及审计报告 |

团队输入的空字段没有被这些客观事实替代；完整待补清单见 `NEEDS-INPUT.md`。
