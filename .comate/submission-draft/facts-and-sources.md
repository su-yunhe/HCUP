# 已自动填入的事实与出处

| 事实 | 值/结论 | 出处 |
| --- | --- | --- |
| 团队 | HC2026-111 / Ghost_London / online | common/spec-harness/team.yaml |
| 题目与基线 | vg-spec15 / 88db8789e28333c7b7dcc8db078f394a262b73c3 | spec/submit-input.yaml、spec/metadata.json |
| 基线准备 | harmony-cup-build-v1，dry_run=false，changes=[] | logs/prepare-baseline.log、workflow/setup-result.json |
| 应用 | io.qzz.weiyu / entry / EntryAbility | AppScope/app.json5、entry/src/main/module.json5 |
| 正式构建 | clean assembleHap 命令，exit 0，759诊断与基线相同 | logs/implementation-validation/build-round-02/、warning-comparison.json |
| 本地自测 | run09 9通过、0失败、0跳过，exit 0 | logs/implementation-validation/selftest-09.json、selftest-09-command.json |
| 已测 HAP | 8978553字节；481c6f4609aee0370e12331e5200f1a1021886f9b8f9dd4e45289944ee6b56fa | build-round-02/artifacts.json |
| 生产指纹 | 511264d4077a8b570329124dd41c36dae2bceea3e9b10ee5a871f2398bb78b6a | workflow/implementation/source-round-02.json；本轮逐文件复核 |
| 完整工程快照 | 2059文件；b8b0eaf672f295d50c8570d0d5d1df2b7c073aa06b6a162ac867233db47ecdea | changes/project-manifest.json |
| 完整差异 | 190895672字节；49c6fd78bb6c83e415d52da0cc387019268c88d2dad868aba2426f12adbde10a | changes/final.diff、changes/validation.json |
| 可应用性 | check/apply exit 0，全部文件原始字节一致，无额外/缺失 | 本轮临时基线 clone，changes/validation.json |
| 日志复制 | 1617份，逐文件SHA256 | logs-manifest.json；原工程 logs/ |
| 二进制 | 208份，含同源基线及新增过程材料 | changes/binaries.json |
| 会话/模型/effort/token/工具 | 14会话，gpt-6.1-sol / xhigh；逐会话原生累计值 | traces/session-inventory.json，原生JSONL |
| 客户端 | 本轮Windows包26.1007.2314.0；原生CLI 0.162.0-alpha.17.2 | runtime-evidence.json、session_meta |
| 任务书 | 当前common父仓库HEAD及四份文件双端SHA256，历史目录不存在 | taskbook-version.json；spec-harness/、common/spec-harness/ |
| 已知来源 | 随包基线、本地SDK声明、ArkTS指南、锁文件依赖 | sources.fragment.md与所列原生调用 |

事实与用户声明分别记录；没有用自动核查推定人工修改、额外来源、已知问题或团队成员分工。没有把本地通过换算成官方成绩。
