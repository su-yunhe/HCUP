# 已自动填入的事实及出处

| 事实 | 已填值 / 限定 | 真实出处 |
| --- | --- | --- |
| 团队 | HC2026-111 / Ghost_London / online | ../common/spec-harness/team.yaml 非空字段 |
| 题号、基线 | vg-spec14；88db8789e28333c7b7dcc8db078f394a262b73c3；vignette-88db8789e2-base.bundle | spec/metadata.json、inputs/metadata.json |
| 完成情况 | 6个生产文件；本地验收完成 | workflow/do-delivery.md、workflow/do-final-integrity.json |
| 自测 | 11个唯一方法分批通过、29适用项pass、2项有据不适用；非官方成绩 | workflow/do-final-validation-audit.json、workflow/verification/do-results-v1.json、logs/do-validation/ |
| 源码与HAP | 生产聚合8d882180894e3689b4dc0930b59034f3d46627fb454496b0e3ac32a141f2b285；HAP a8c2b0cd7f00f13cdded0bbbb51e17b183e7236c949f14ea97ca15fbd4634b17 | workflow/do-final-integrity.json、logs/do-validation/hap-sha256.json |
| 应用 | io.qzz.weiyu / entry / EntryAbility；1.0.0 | AppScope/app.json5、entry/src/main/module.json5 |
| 工具链 | DevEco6.1.0.860、编译SDK6.1.0.105/API23；工程target/compatible22 | logs/do-implementation/environment.log、logs/do-validation/bundle-installed-run-11.txt、build-profile.json5 |
| 依赖 | ArkTS hypium1.0.24 / hamock1.0.0；Python Hypium6.1.0.210；Python实测3.12.3 | oh-package*.json5、test-harness/requirements.txt、logs/do-validation/preparation-manifest.json |
| 客户端/模型 | Codex Appx26.1007.2314.0、CLI0.162.0-alpha.17.2；逐会话模型/effort/token | 本轮Get-AppxPackage原生记录；traces/manifest.json对应原生session_meta/turn_context/token_count |
| 构建 | clean assembleHap退出0；源码诊断756和签名告警1 | logs/do-validation/build-command.txt、build.log、build-exit-code.txt、warning-comparison.json |
| 基线准备 | 本地profile harmony-cup-build-v1，changes=[]；官方指定log缺失 | logs/prepare-baseline.log；本轮精确路径存在性检查 |
| 实际来源 | SDK声明、技能语言指南、Hypium资料、失败网络检索及404，非无额外来源声明 | workflow/design/submit-facts-v1.md、sources.fragment.md及对应原生工具返回 |
| 会话、任务书、完整投影 | 实际ID/映射/原生哈希、四任务书SHA256、工程文件/二进制摘要 | traces/manifest.json、provenance.json、trace-index.md、project-manifest.json、changes/binaries.json |
| 完整差异验证 | clone/checkout/check/apply和全部文件集合/字节比较的实际结果 | validation.json，独立审查 audit/independent-validation.json |

上述相对源路径以本题工程为准；成果包工程内增加project/前缀，单题材料日志放logs/，规范导出轨迹在包根traces/vg-spec14/。不以摘要替代原始证据。
