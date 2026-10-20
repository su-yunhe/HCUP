# vg-spec14 2-submit 交付说明

本题提交草稿已整理。业务源码、资源与工程配置未修改；301个1-do冻结输入逐文件SHA-256一致。本阶段未重跑构建或设备自测，沿用1-do已保存的干净构建与11个唯一方法分批通过证据。没有生成ZIP或对外提交，正式提交前仍有待补充字段。

## 本地材料一致性验证

- 基线：`88db8789e28333c7b7dcc8db078f394a262b73c3`。
- 工程投影版本：`sha256:0b99275142247ad243afda40ea9f5f62eac57f733f89c76be2baf00650ab535f`；文件清单与边界见 [project-manifest.json](project-manifest.json)。
- 完整binary patch：[changes/final.diff](changes/final.diff)，92,628,383字节，SHA-256 `eb0a0db9fc4dfc2c63050d27e60a32337e1bcf42e82c503d74d289abec4d27bd`。
- 实际执行本地基线clone、checkout、`git apply --check --binary`与实际apply，全部退出0。重建后的967个纳入文件与本工程逐字节一致，文件集合无多余/遗漏；真实命令与结果在 [validation.json](validation.json)。
- 改动清单：新增671、修改4、删除0，含测试/任务书/日志/配置/工作流/本题原生快照等过程文件。二进制文件109项单列在 [changes/binaries.json](changes/binaries.json)，其中8项与基线相同，其余为本题生成证据；实际文件仍在工程投影中。
- 15份本题原生会话、过滤索引与机械Markdown阅读副本、301份源文件/配置/测试输入实物快照在traces/；515份历史日志副本在logs/，原生与日志复制散列一致。失败、重试、未采用与中断均保留，非IDE原生Markdown导出不冒充原生导出。
- 原生payload.id与payload.session_id有真实区别：3个主会话各有侧边栏索引，12个子Agent通过其session_id关联主会话。Comate字段不适用于本题Codex运行器。详见 [trace-index.md](trace-index.md)。
- CRLF作为原工作树字节保留；实际apply有尾空白告警，未做whitespace修复，退出0且全量SHA-256一致。未用去空白或批量换行改动掩盖差异。

## 工程交付边界

按manifest复制工程；将本封套移至包内题目材料根及全局traces，避免把final.diff递归放入它自己描述的工程。两份混合初始化总览原件本地保留但不提交其其他题内容。此为明确披露的有限工程投影，不声称覆盖本地字面全部目录。具体纳入/排除与3-package交接步骤见 [packaging-contract.md](packaging-contract.md)。

## 两份必需清单

1. [仍需补充的字段](pending-fields.md)：10个用户空白叶字段及记录缺口；指定题包基线报告不存在，已有本题日志不冒充缺失原件。正式版本/冻结时间/联系人/人工修改/额外来源等未推测。
2. [已自动填入的事实及出处](auto-filled-facts.md)：团队非空信息、基线/应用/依赖/工具/源码HAP/构建与自测/会话/任务书版本/来源事实等。

独立审查结果：[audit/independent-validation.json](audit/independent-validation.json)：`draft_consistency_pass=true`，未修复材料缺陷0；26项中23项pass，人工声明与正式冻结相关3项blocked，`formal_submission_ready=false`。如有新变更须重新生成manifest、patch和全量验证，不沿用本轮结论。最终团队冻结与3-package须由后续明确指令开展。

本轮审查与修订的收尾原生快照另存 `traces/finalization-native/`，以 `traces/finalization-manifest.json` 记录其与已审查快照的前缀对应及准确截止点；独立审计针对其明确列出的15份主导出快照，未将后来产生的收尾记录伪装成已提前审查的内容。交付封套文件摘要见 `materials-manifest.json`，不包含校验临时clone。
