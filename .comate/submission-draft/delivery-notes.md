# 2-submit 交付说明

本题材料整理完成范围见本目录文件；版本/联系人/冻结时间/人工和来源等空声明仍为【待补充】，详见missing-fields.md。自动事实及出处见auto-filled-facts.md。submission.json.fragment是供3-package使用的本题submitted候选对象，最终是否提交须使用team.yaml.submitted_tasks，不表示已对外提交。

独立材料验收结果为21 pass、1 fail、3 blocked，机械一致性检查通过，正式提交材料尚未就绪。R04历史范围控制失误无法由后续修正撤销，继续如实列fail；双ID/人工声明/团队冻结等阻断见validation/independent-review-r1.md。不能把完整补丁重建成功写成材料全部合规。

完整工程范围：11951 文件，完整项目聚合 SHA-256 `e1c8f2286ca9f93ca33bb094356bd415f53efa80a857baf8d2d22ce699ee870a`。请将traces/code-snapshot/project/原样复制到包根tasks/cml-spec1/project/，将本目录build.md、trace-index.md、human-changes.md、changes/、logs/放到tasks/cml-spec1/，traces/放到包根traces/cml-spec1/。validation/、两份清单与本交付说明应作为本题辅助材料保留，solution.fragment.md及sources.fragment.md由3-package汇总；不在此阶段写团队根文件或生成ZIP。

原“生产冻结”688文件的实际集合为677个tracked基线/修改文件加11个新增feature/main文件；其中包含115个基线tracked测试文件，排除的是新增hypium_tests及过程材料。该输入冻结与本次完整11951文件快照分开标识，不能用688文件清单代替完整提交差异。

完整补丁校验状态：True。实际命令、stdout/stderr与退出码在validation/patch-commands.json；基线独立clone/checkout，git apply --check --binary和真实apply均exit0后，逐一对比完整文件集合/摘要；差异条目见validation/patch-validation.json。最终补丁SHA-256 `da4db70fd3c29f6a4d05773479cb04acee153520c3769515612305482a5dcdc0`。比对范围含新增/修改/删除、过程文件和二进制，并非仅生产目录。独立复核见validation/independent-review-r1.md/.json（若尚未生成，不能据此声称独立通过）。

本阶段只核对已有构建和自测日志，未重新构建或操作设备；原263份日志均有sha清单。指定官方reports原文不存在，已用真实本地准备输出披露；不能补跑一条新命令冒充缺失的历史日志。缺少的提供者声明和Comate特有字段仍待补充/确认，不将结构校验或本地功能通过等同于官方材料核验或官方评分。

本轮历史采集/临时clone的范围失误及修正如实记在traces/README.md、validation/material-retry-history.json和原生会话；旧clone未作为任何上游历史参考，不进入包。本轮材料校验的最终事实只引用scoped clone重做的检查。

补丁为精确字节重建而在临时clone设置core.autocrlf=false；现有工程的CRLF与Git基线LF差异也如实保留。git apply输出的trailing-whitespace警告原文保留，退出码为0，没有用whitespace修复选项改写工程字节。它不代表新增编译诊断；业务语义改动清单与原git状态见工程审计报告。

本题专用模拟器仍持续写traces/baseline-analysis/emulator-instances/CmlSpec1Baseline/Log/。这些运行日志以复制后的不可变文件摘要为交付版本，manifest记录逐文件捕获时段、复制前后和实际副本摘要；patch必须与副本逐字节一致。live随后新增/轮转/写入的差异逐项记录在patch-validation.json，不泛化到其他traces、logs/、workflow、测试或生产。当前仍在写的压缩流可能仅含截至采集边界的字节，不能冒称它是已关闭的完整日志流；历史失败原始记录仍保留。所有非该精确runtime路径的工程文件、688生产冻结及HAP均要求无漂移。

staging自包含冲突按公开工程快照边界处理：.comate/submission-draft整体属于项目旁的材料区，不再递归进入project；其余.comate过程文件仍保留。3-package若重新从live工作区复制、重导出后修改工程内历史轨迹或改变任何工程文件，必须重新生成diff并重新做逐文件比对，不能继续使用本次差异。

精确搬运清单见packaging-map.json；.validation/绝不可打包，包含被自动审批拒绝删除的旧临时clone。工具脚本属于材料复现辅助，后续打包如需保留应作为辅助工具单独映射，不递归复制临时目录。
