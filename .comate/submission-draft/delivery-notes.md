# vg-spec9 材料交付说明

本轮仅完成2-submit单题材料；本地材料可审阅，用户未提供项保持【待补充】。没有改业务代码、资源和配置，也没有运行设备/重建HAP。workflow/state与events仅登记本轮会话和材料阶段事件。正式团队文档和ZIP由3-package处理。

工程快照：`traces/code-snapshots/20261016T130254Z-d8384998/project`；snapshot_id=`1b5799251641879b65b9daed9c3a8073439773ab7f0692901ecd6103c81921e3`，776份文件。阶段3必须将这个目录的全部内容复制为 `tasks/vg-spec9/project/`，不能直接递归复制原工作区。完整补丁基于该同一版本。材料会话一次索引读取返回了无关侧边栏元数据行，导出副本只替换这些行，原件不改；checks/trace-redactions.json保留逐行脱敏说明及前后摘要。

补丁验证：仅通过本地传输clone本题分支、不拉取其他分支/标签，并detach到 `a22f32b07bf81c6dde4367e2543ebac29186cbc1`，git apply --check --binary 退出0；实际apply退出0；全文件路径、大小、SHA-256均与快照相同，快照与原工程所纳入文件逐字节相同。验证记录 `checks/diff-validation.json`，逐文件 `changes/project-manifest.json`。快照ID以相对路径字符串排序计算，最终完整性检查独立重算；材料阶段的换行与排序问题、修复和重试保留于 `checks/material-retries.md` 及材料原始会话。用临时仓库的 `core.autocrlf=false`、`core.eol=lf`，并通过临时info/attributes禁用写入时归一化，保留原始日志CRLF。部分基线文件的Windows checkout CRLF与Git基线blob LF不同，补丁为字节复原保留这部分差异；它们不属于功能修改，清单见 `changes/baseline-checkout-eol-preservation.json`。原始历史文本的空白诊断单独保留，不改写证据。

纳入边界：基线全部保留文件，以及本工程所有tracked和非ignored新增文件，包括spec、hypium_tests、流程资料、原生本题记录、日志、配置快照。没有把diff限定在业务目录。已有.gitignore排除构建产物/依赖缓存/本机local.properties；新增输出目录 `.comate/submission-draft/**` 是外层材料容器，不再放进project/，避免补丁、快照和自身递归。若日后该容器外出现其他.comate过程文件，必须纳入工程并重生成补丁。

隐私和跨题隔离仅排除以下本机原始初始化总览快照，原件留在原工作区，相关初始化摘要/版本/准备日志仍在本题工程；不读取或用其内容证明本题研发：

- `traces/native/20261016T113308Z-03d71bbf/2026/10/15/rollout-2026-10-15T21-33-01-01a13fc4-2611-7761-a580-1283e0c70541.jsonl`：Initialization overview contains other tasks; excluded from submitted project and native evidence. Original retained locally, not read as feature evidence.
- `traces/native/20261016T113324Z-9abab26e/2026/10/15/rollout-2026-10-15T21-33-01-01a13fc4-2611-7761-a580-1283e0c70541.jsonl`：Initialization overview contains other tasks; excluded from submitted project and native evidence. Original retained locally, not read as feature evidence.

历史manifest仍保留其原始路径/摘要，未伪造新哈希；其中指向被排除总览的条目须结合本说明读取。阶段3不能为了补齐这些路径而把总览原文放回工程。没有删除本题失败和重试。

二进制实际字节保存在上述工程快照；基线同源、截图、夹具上传字节全部单列在 changes/binary-files.*。HAP摘要在同文件，仅作构建证据，不以HAP代替完整工程。

路径汇总约定：以 `delivery-manifest.json` 的逐文件复制表为准，它同时指定完整project的来源和目的地，并排除checks/work临时仓库与旧的scratch快照。本材料目录的build.md、trace-index.md、taskbook-version.md、human-changes.md、sources.fragment.md、solution.fragment.md、delivery-notes.md、pending-fields.md、facts-and-sources.md、traces/、changes/、logs/、tools/及checks中的非work文件，按相同相对位置置于tasks/vg-spec9/；最终traces/code-snapshots中的完整project另外复制为任务project。复制表保留最终快照作为代码证据，确保索引路径有效。`checks/work/**`仅为本地补丁验证临时clone，含.git，不是交付材料；不要打包这些临时仓库。

`submission.json.fragment`是官方tasks数组内本题候选对象；三个路径字段均用/，后两项为文件。它不是根任务清单或正式提交指令。team.yaml的submitted_tasks为空，阶段3应按用户选择合并，不据此自动决定全部题目状态。

仍需补充项见 pending-fields.md；自动事实及出处见 facts-and-sources.md。本地输出和导出时间均不能代替用户未提供的正式冻结时间。
