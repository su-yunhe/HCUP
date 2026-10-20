# 已自动填入的事实及出处

| 已核实事实 | 出处 |
| --- | --- |
| 团队HC2026-111 / Ghost_London、online；本题cml-spec1 | ../common/spec-harness/team.yaml；spec/submit-input.yaml（原始空字段未补猜） |
| 基线 `7014cebd60f2181fac2a36d399ca16b3d6a175ab`、对应bundle标识 | spec/metadata.json；workflow/baseline-provenance.json |
| 本地准备profile=harmony-cup-build-v1，changes=[]；指定题包reports缺失 | logs/prepare-baseline.log；workflow/setup-result.json；本轮真实文件存在性查询 |
| bundleName com.joker.coolmall，entry/EntryAbility，版本1.0.0/1000000；配置API21 | AppScope/app.json5；entry/src/main/module.json5；build-profile.json5 |
| 新增Lottie2.0.33、HAR地址与integrity；新增JSON/SVG而无业务二进制修改 | feature/main/oh-package.json5及两锁文件；workflow/implementation/submission-project-audit-r1.md |
| 生产688文件聚合2cebe8...，本阶段零变化；HAP20739960bytes、d54386d3... | traces/do-implementation/source-frozen-r2.json；production-preservation.json（本次重算） |
| 原最终构建exit0、安装exit0，8/8本地自测，44项本地矩阵 | logs/verification-do-build-run-r2-commands.json；logs/verification-do-run-run-r4-commands.json；logs/selftest-run-r4.json；workflow/verification/do-result-r4.md |
| 历史超时尚有局限、所有失败与重试保留 | workflow/state.json.failures；workflow/verification/do-result-r4.md；traces/verification-do-r1各轮原文 |
| 16原生分段，模型gpt-6.1-sol/xhigh、cli_version0.163.0-alpha.10.2，每分段实际token字段与工具 | traces/native-manifest.json；traces/tool-call-index.jsonl；原生session_meta/turn_context/token_count |
| 当前应用包26.1013.4894.0；当前Hypium/NumPy/OpenCV版本 | traces/runtime-versions.json；本轮只读Get-AppxPackage及importlib.metadata查询；不推定历史客户端版本 |
| common所在仓库HEAD与四任务书真实SHA-256、本题副本一致；无spec/history | traces/taskbooks/version.json及common任务书副本 |
| 完整工程11951 文件，完整项目聚合 SHA-256 `e1c8f2286ca9f93ca33bb094356bd415f53efa80a857baf8d2d22ce699ee870a`；补丁逐文件重建验证 | traces/code-snapshot/manifest.json；validation/patch-validation.json；validation/patch-commands.json |
| 二进制逐文件大小、摘要、原路径基线同源性 | changes/binary-files.csv；完整工程实际文件 |
| 已发生的第三方依赖与技术文档成功/失败查询 | sources.fragment.md；设计_do原生工具调用及返回 |

本表中的工程路径均相对本题工程；草稿路径均相对本目录。证据能证明的实际事实与提供者留空的人工/来源/已知问题声明分别记载，不作排他性推断。
