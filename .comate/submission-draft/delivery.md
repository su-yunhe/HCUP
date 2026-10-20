# vg-spec15 材料交付与校验

本阶段只整理 .comate/submission-draft/；未改变业务代码、资源和配置，未提交赛事成果，未生成团队级根文件或ZIP。workflow 中仅追加本阶段会话与调度记录。

完整差异自官方基线 `88db8789e28333c7b7dcc8db078f394a262b73c3` 起生成，含过程文件。最终未提交工作树快照 SHA-256 为 `b8b0eaf672f295d50c8570d0d5d1df2b7c073aa06b6a162ac867233db47ecdea`，HEAD 仍为基线。采用本题 Git 仓库本地克隆后 checkout 到基线，未读取禁止的题包 bundle/修复来源。`git apply --check --binary` 和实际应用均 exit 0，随后 2059 文件 SHA-256 逐字节比对全部一致；额外、缺失、哈希不符均为0。具体命令及CRLF/LF处理见 changes/validation.json，临时克隆已清理。二进制逐项列在 changes/binaries.json；没有新增生产二进制素材。

## 3-package 搬运约定

- build.md、trace-index.md、changes/、logs/ 放入 tasks/vg-spec15/；sources.fragment.md、solution.fragment.md、submission.json.fragment 供团队汇总。
- traces/ 放入包根 traces/vg-spec15/，保留原生记录、过滤索引、Markdown及代码快照；taskbook-version.json、runtime-evidence.json、pending-fields.md、facts-and-sources.md、logs-manifest.json、final-checks.json、record-sensitivity-check.json、本交付说明、audits/ 和 tools/ 一并放入 tasks/vg-spec15/ 供索引审计。tools/ 是本轮原工作区材料生成过程的证据，不是正式构建依赖，也不声明可以在搬运后按原路径直接执行。
- project 必须严格按 changes/project-manifest.json 的文件清单复制本工程；总计 2059 文件，原始字节聚合 b8b0eaf672f295d50c8570d0d5d1df2b7c073aa06b6a162ac867233db47ecdea。保留 spec/、hypium_tests/、workflow/、logs/、traces/、system-config/、spec-harness/、test-harness/ 及清单内其他过程文件。
- 排除 build/、oh_modules/、node_modules/、.hvigor/、__pycache__/、.git、环境缓存和 local.properties；排除生成的 .comate/submission-draft/，因为它的内容已被搬到上述材料位置。其他 .comate/ 文件若在manifest内则必须保留。把 final.diff 再复制进其所描述的 project 会导致自包含递归，不能这样打包。
- 若工程内容在本快照后改变，必须重新生成 final.diff 和清单并重做基线应用及全文件比对；不要继续引用本次摘要。团队正式freeze_time、版本和提交选题仍由用户补充，本次没有虚构冻结。
- 正式打包前停止相关工作，重新导出本轮材料会话末尾；本轮快照不包含导出后的事件。保留所有研发失败、重试、run06重建标识和既有配置版本。
- 自测公共工具及cryptography额外依赖由3-package汇总；现有机器路径脚本只是历史证据，便携复用命令见build.md。

## 材料状态

完整工程差异、二进制清单、原生研发轨迹、过滤索引、Markdown阅读副本、代码快照、1617份日志和三类汇总片段已产出。缺失用户字段及运行器差异详见 pending-fields.md；不能将这些材料视为已补齐所有人工声明或已正式提交。

日志齐全，不需要补跑构建/自测。指定官方基线报告缺失，但本地原始准备与构建日志存在；新运行不能替代缺失的历史官方报告。
