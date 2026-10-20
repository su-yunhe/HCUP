# 已自动填入的事实及出处

| 事实 | 直接出处 |
| --- | --- |
| HC2026-111 / Ghost_London / online | common/spec-harness/team.yaml（输入SHA见audit/taskbook-versions.json） |
| base_commit `9cbcf7292c8cc46955dc3b522ddbda41c66a61d9` | project/spec/metadata.json；本题HEAD实读；project/workflow/baseline-provenance.json保存准备时来源摘要 |
| 本地准备profile=harmony-cup-build-v1、dry_run=false、changes=[]；准备完成时间 | logs/prepare-baseline.log、project/workflow/setup-result.json；非官方缺失报告替代品 |
| bundleName io.qzz.weiyu、entry/EntryAbility、版本1.0.0 | project/AppScope/app.json5、project/entry/src/main/module.json5 |
| 声明SDK6.0.2(22)、HarmonyOS；Hypium1.0.24/Hamock1.0.0 | project/build-profile.json5、oh-package.json5和锁文件 |
| 构建/安装/启动命令与现有结果 | build.md逐条引用的logs及project脚本 |
| 当前HAP 9121443字节、SHA a3574072f81f37e14c0f0c1b335673d44e7aa1691c83488a065d4b7c91278a36 | 原HAP现存字节；project/workflow/final-validation-fingerprint.json及最终审计/安装manifest |
| 当前222输入一致；28条需求、13+4+1+1用例通过；764既有警告 | project/workflow最终指纹/报告；各run build/exit/hypium/selftest；本阶段只读复核 |
| 旧HAP/分辨率复用边界、真实隔离范围及人工操作 | project/workflow/development-handoff.md、各run原始日志/数据库/报告 |
| 13个本题原生会话；模型gpt-6.1-sol、effort=xhigh、CLI0.163.0-alpha.10.2 | traces/vg-spec1/sessions.json，session_meta/turn_context/token_count/thread_spawn与筛选sidebar原始行 |
| 当前Windows OpenAI.Codex安装包版本26.1013.4894.0 | audit/client-version.json；Get-AppxPackage材料阶段实读，不能倒推全部历史时刻 |
| 工程快照版本 `sha256:2968c3ebfe338969634f8d28fece3c28fce3f71e87a2901d52538a3412787bba`、4175文件、diff应用与全字节比对通过 | changes/project-manifest.json、audit/diff-validation.json |
| 二进制路径、字节、SHA及基线同源判定 | changes/binary-files.json/.md；按基线Git blob实际字节SHA比对 |
| common父工作区commit `e9befa727bcd94f2eea263bd3c92c56d9f8ec6ac`，当前四任务书和模板SHA；无spec/history | audit/taskbook-versions.json（目录继承父Git，额外保留逐文件SHA） |

本表未将用户留空字段转为“无”，未推断官方分数或全程无风险。片段及索引采用成果包相对路径；draft在本地是搬运前暂存位置。
