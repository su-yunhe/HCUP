# cml-spec24 2-submit 独立材料核验 v1

状态：单题草稿技术核验通过（23项检查pass；历史F01/F02保留并重验）。这仅证明本次有限工程、差异与材料披露一致；10处用户输入、官方基线日志/Comate专有字段/原生Markdown及当前会话尾部等真实缺口仍在，正式成果冻结、3-package与赛事提交就绪为blocked，不能宣称最终成果包合格或官方通过。

- 核验角色实际 `CODEX_THREAD_ID`：`01a152f5-80c5-7470-91fb-a120d3a51b0c`，由本角色 PowerShell 环境变量读取，非推导值。
- 范围：仅本题 2-submit 材料。只写本文及明确获准的本题临时独立核验目录；未修改生产代码、资源、配置、测试、Spec、原工程Git索引或全局状态；未重建、未安装或操作设备、未生成子Agent。临时clone与apply只发生在本题`.comate/submission-check/independent-22cdf5270e79/`。
- 输入：本题 `spec-harness/2-submit.md`、`workflow/state.json`、`workflow/development-result.json`、需求审查、材料方案、提交工具和已生成草稿，指定官方三模板。本角色未读取混题初始化会话正文、其他题工程、来源项目修复历史。
- 环境：Windows / PowerShell；每个工具进程首先加载 `D:/hongmengcup/Enter-HarmonyEnv.ps1`。只读检查用该环境 Python，`python -B -` 防止写入字节码。无设备参与本轮。
- 原始命令和输出：本角色原生会话工具调用；下文保留关键命令、退出码和原始结果摘要。未将静态阅读或既有开发结果当作本轮功能验证。

## 预审结果

| 需求 | 状态 | 已核验证据及边界 |
| --- | --- | --- |
| R01 既有开发完成前置 | pass | `development-result.json` 为 `local_validation_complete`，本轮仅验证材料引用和限制，未重跑功能测试 |
| R02 本题草稿边界、生产冻结 | pass | 仅本指定报告写入；独立重算最终源码指纹 896 文件，`changed_source=[]` |
| R03 客观事实真实、空字段待补 | pass | 现有主文档/片段已区分用户10项空白、自动事实和限制；未把用户声明自动写“无”；最终材料摘要仍待收束 |
| R04 完整工程与 binary diff 对应 | pass | 最终16970文件完整边界独立枚举与清单相等；全新基线应用完整binary diff后逐文件等于清单和原工程，含spec/hypium_tests/workflow/.comate等过程 |
| R05 隔离 baseline clone 应用与全量比对 | pass | 独立no-local/depth1单分支clone，无alternates/临时attributes；精确base，check/apply --binary --index均exit0，全树路径/大小/SHA/mode一致 |
| R06 排除生成噪声与保留过程 | pass | 当前脚本排除两个输出子树、构建依赖缓存、BuildProfile、六个模拟器运行盘、明确混题原生副本；本次核对 baseline tracked 排除项为 0。最终 diff 仍需核对 |
| R07 二进制大小/摘要/同源 | pass | 1050真实binary差异、1067资源清单与project各项大小/SHA一致，标准binary差异无漏/多；68项同源声明独立重算baseline blob匹配 |
| R08 可移植 build.md | pass | 静态核对包含依赖、三个构建目标、安装/启动、标识、初始化、自测与公共环境变量；无本机私有绝对路径。明确未跨机重放、不要求本轮重建 |
| R09 官方 trace-index 逐字段 | pass | 已按官方模板24个原始字段逐项匹配，缺失0；正文保留待补、平台差异和限制 |
| R10 来源片段 | pass | 区分官方随包基线、依赖/工具、服务数据与实际过宽搜索；extra_sources 空白保持待补，未作“无额外来源”推断 |
| R11 方案片段及限制 | pass | 保留本地 76 项与官方成绩边界、x86_64 运行、arm64仅构建、受控两轮、原生响应截断、失败重试与清缓存自动审核拒绝 |
| R12 JSON 三相对路径 | pass | 已生成 JSON 为本题对象；`tasks/cml-spec24/project`、`tasks/cml-spec24/build.md`、`tasks/cml-spec24/trace-index.md`，使用 `/`，后两项为文件；实际包内存在性留给3-package |
| R13 本题双维检索与相关失败保留 | pass | 最终导出15会话，登记会话缺失0、明确混题排除；双维查询后使用本题cwd或登记UUID纳入策略，保留失败/重试；未读被排除会话研发正文 |
| R14 双ID及实际平台 | pass | 现有清单分别记录 Codex session_meta 的 session_id、thread id、parent id 和实际IDE thread；Comate sessionUuid 明确待补、不伪造。子会话引擎字段可能指向主会话，不能将二者误称独立Comate双ID |
| R15 原生、过滤索引、Markdown与快照 | pass | 15原生11,471行快照均可解析、哈希/记录数一致、机械Markdown逐行完整；code-snapshot以完整清单和可应用patch关联，分别说明草稿/包内路径。后续导出尾部仍按cutoff披露 |
| R16 日志与失败重试 | pass | v2精确宿主Log边界修订后15,815文件/1,097,999,280字节全部source/copy/manifest一致，额外/缺失副本均0；F01原失败保留、未覆盖 |
| R17 任务书版本/历史 | pass | facts/harness-version.json 已记录四份任务书与本题副本摘要、父仓库HEAD说明；history为空需在最终索引如实说明 |
| R18 人工修改 | pass | 片段保持 human_edits、人员/目的/文件/前后标识待补，未推断“无人直接改码” |
| R19 保护措施、脱敏、缺失 | pass | redactions.json登记一条非本题metadata工具返回脱敏及原行SHA；最新15原生/Markdown和主文档所列秘密特征无命中。来源疑点、原生平台/MD/官方日志缺口明示；非来源合规裁决 |
| R20 同一冻结映射 | pass | v2边界及F02编码修复后，最终manifest/diff核验期间未变，原工程与独立应用树16970文件全量一致、896源码不变、原HEAD/index不变；这是技术快照映射，团队正式freeze_time仍待补 |
| R21 两份交付清单 | pass | pending-fields.md完整列10项输入空白与平台缺口；automatically-filled-facts.md列自动事实及出处，均未代填3-package字段 |
| R22 实质材料核验边界 | pass | 不把文件存在、静态脚本阅读或本地结构检查当作官方合格结论 |
| R23 有限project导出边界 | pass | 完整边界独立枚举16970项与manifest精确相等，无误纳排除项；清单/完整diff全量一致；packaging-contract明确3-package必须清单物化，不能递归带回输出/缓存 |

## 命令及原始结果摘要

1. 会话ID：`. D:/hongmengcup/Enter-HarmonyEnv.ps1; $env:CODEX_THREAD_ID`。退出码0，原始输出 `01a152f5-80c5-7470-91fb-a120d3a51b0c`。
2. 只读指纹和清单：通过 `python -B -` 读取工具源码，以 `__name__='independent_readonly_review'` 加载定义、只调用 `inventory()`，并用独立 `hashlib.sha256` 重算 `workflow/final-code-fingerprint-v2.json` 全部文件；以只读 `git ls-tree -r --name-only <base>` 核对排除规则。退出码0。原始结果：`files=17024`、`bytes=1357064275`、`baseline_files_excluded=[]`、`source_reference_files=896`、`changed_source=[]`。这次文件数是动态预审值，不能当作最终冻结计数。
3. 大文件与签名扫描：只读遍历同一有限边界，统计文件路径/大小，扫描小于30MiB的指定文本扩展名；签名为PEM私钥、OpenAI key、GitHub token，只输出候选路径/类别。退出码0。`SECRET_SIGNATURE_CANDIDATES=[]`。这只证明所列签名在已扫描文本范围未命中，不等于所有敏感类型均不存在；最终导出的副本仍须独立检查。
4. 大文件分类：最大为19,923,862字节的本题default HAP；模拟器目录保留62文件/65,890,398字节，为日志等证据，不含被排除的运行盘。主要保留体积来自正常/受控设备原始日志和多次本题原生快照，未按体积删失败记录。
5. 初始工具源码SHA-256：`651ab8b2d5988dcebc464504120b8cdaebdb4e0c15c7f4dee368648417cf241d`。主Agent随后修改材料脚本修复预审意见，最终脚本需重新计算；本值仅标识初次静态阅读对象。
6. 本题原Git状态只读基准：`git rev-parse HEAD`及`git ls-files --stage -z`，均退出码0。HEAD为`ab3dc7cd5d05a9a3fd7d4e9ddd0a49e1a05085d8`，858项index记录的stdout SHA-256为`b19accb4d8ced9dd4ba85acf9fd0ff9409e2eb4f02463ac8c0a8f9e96584d470`，用于终验比较。
7. 预审原生导出：独立逐行JSON解析、重算文件SHA、比较manifest记录数及Markdown存在性，退出码0；`native_files=15`、`native_records=10719`、`manifest_errors=[]`。原生过滤session index仅3条主会话行，12个子会话不在该平台index中，但已在本题manifest和IDE筛选表。已反馈主Agent须说明原生index覆盖边界；不得生成伪原生行补齐。
8. 日志全量核验：通过`python -B -`读取`checks/log-copy-manifest.json`，独立对每一项同时核对草稿副本和原logs的存在、大小、SHA-256，不复用生成脚本的哈希结果。命令退出码0，校验结果fail：`copied_files=15873`、`copied_bytes=1163662672`、`source_and_copy_hash_mismatches`共7条（2条副本、5条原文件），清单SHA-256为`ffc1e06c0c64abbe1fcdab97b78a97bd5fd37d2b9b57cb5c11f5ce5b35a129d9`。详细见F01；非零校验不因Python本身exit0而记通过。
9. v2日志重验：同一独立算法对修订后的全清单重算source/copy/manifest并比较副本完整路径集合；退出码0、`pass=true`。原始结果：`utc=2026-10-19T07:13:56.253792+00:00`、`copied_files=15815`、`copied_bytes=1097999280`、`source_and_copy_hash_mismatches=[]`、`extra_copies=[]`、`missing_copies=[]`、manifest SHA-256=`f6d7335b3233288923f374b4c19f11e45ceee67f36fb0f1a4fe74080055070e4`。F01只作为历史失败保留，新通过仅适用于v2保留边界。
10. 最新文档/原生核验：独立解析官方模板和JSON片段，逐条解析JSONL、验证原生SHA/行数及每一条原生记录在Markdown副本中保留。退出码0。原始结果：`trace_template_fields=24`、`missing_template_field_numbers=[]`、`build_private_absolute_path_candidates=[]`、`json_paths_correct=true`、`missing_registered=[]`、`native_files=15`、`native_records=11471`、`native_errors=[]`、`sensitive_signature_candidates=[]`。最新导出manifest SHA-256=`fc1ff2673893222643707b0c8094424aa2743a04f4561492f998d145d34926f9`，redactions SHA-256=`7ec9fdad53cebcd8d310efcb082fb27d07949a7d22496340c8e2ac6bfc84f57b`；`build.md` SHA-256=`55a3c001d90899a3c9c6e5e7bb4d61dd57be2294262b9c27ae2fdc015a59a79f`。导出若继续更新，以上只标识该快照，需终态摘要再核。
11. 官方事实摘要重算：重新读取获准官方三模板、common四任务书与本题副本，逐项核对facts中SHA-256，退出码0，两份facts的`mismatches=[]`。
12. 最终有限边界：只按脚本排除策略独立枚举路径，未调用复制/patch动作。退出码0，`manifest_files=16970`、`source_boundary_files=16970`、`missing_source=[]`、`source_not_in_manifest=[]`、`excluded_paths_in_manifest=[]`、`snapshot_digest_equal=true`。最终工具脚本SHA-256=`a3f6f7f2f96ea9e36c9ca119af326f1113655b7a63dddb2ad6319bb39b26c4e7`。
13. 二进制清单：独立核对标准changed-files中`added_lines='-'`路径集合、两份binary表与工程清单，以及所有声明同源项的Git blob（`sha1('blob '+bytes+'\0'+content)`）对baseline ls-tree映射。退出码0；1050 binary-diff项、1067 resource项、68同源项，`binary_errors=[]`、`standard_binary_diff_missing=[]`、`standard_binary_diff_extra=[]`。

## 最终独立应用证据

运行时间UTC `2026-10-19T07:26:41.684868+00:00`；总Python检查退出码0，`pass=true`、`errors=[]`。独立工作区为本题`.comate/submission-check/independent-22cdf5270e79/`；该目录不进入工程/成果包。主Agent按明确派工将其中`commands.json`、`result.json`、`command-*.stdout.raw`、`command-*.stderr.raw`复制为可交付`checks/independent-apply-v1/`证据；未复制临时clone本身。报告完成后的材料总manifest由主Agent生成，再作只读摘要核对，避免本文自修改使清单失效。

全部Git命令均带单次`-c core.autocrlf=false -c core.safecrlf=false -c core.filemode=false -c core.quotepath=false`，没有改原/全局配置。保留的完整argv/cwd/退出码在commands.json，原始stdout/stderr逐命令保存；依次为：

1. 原工程`git ls-files --stage -z`、`git rev-parse HEAD`。
2. `git clone --no-local --depth 1 --single-branch --no-tags --no-checkout --branch cml-spec24 <本题根> <独立check/applied-project>`。
3. clone内`git rev-parse HEAD`等于精确base；`git rev-parse --is-shallow-repository`为true，无objects/info/alternates；`git checkout --detach <base>`。未设`.git/info/attributes`。
4. clone内`git apply --check --binary --index --whitespace=nowarn <final.diff>`，退出0。
5. clone内`git apply --binary --index --whitespace=nowarn <final.diff>`，退出0。
6. 对全部清单项分别检查原source和clone文件的存在、bytes和独立流式SHA-256；比较clone实际全路径集合及`git ls-files --stage -z`的git_mode；`git write-tree`。
7. 再次核对原index、manifest/diff摘要、最终源码指纹896文件；全部未变。

| 最终事实 | 实测值 |
| --- | --- |
| base_commit及原HEAD | `ab3dc7cd5d05a9a3fd7d4e9ddd0a49e1a05085d8` |
| 完整工程 | 16,970文件；1,291,343,617字节 |
| snapshot_sha256 | `4c6693b5ae2c84b32e50a20eab4ada81b0a7e7247cf8137b1f435eeda2159d65` |
| project-manifest SHA-256 | `e502e40f60292f4f6dd0bf29c054a7acace5bb137554e64dd2db8ea50014e904` |
| 完整final.diff | 946,836,934字节 |
| final.diff SHA-256 | `21ecbc727bfe439bd529991289091f8d57ad439e226c5127598044a7d01b1a11` |
| 独立应用tree（与主校验相同） | `4f9c2cff69b4ca8c2af427055a11bb9007115ea7` |
| 原index项stdout摘要，前后相同 | `b19accb4d8ced9dd4ba85acf9fd0ff9409e2eb4f02463ac8c0a8f9e96584d470` |
| 896源码指纹 | 全部与`workflow/final-code-fingerprint-v2.json`相同 |

## 预审问题及处理

| 编号 | 关联需求 | 期望/实际与最小复现 | 处理/证据强度 |
| --- | --- | --- | --- |
| P01 | R13 | 初版traces()对路径/题号双检索后，一律排除cwd!=本题的候选，可能漏异目录本题测试设计会话；静态定位条件即可复现 | 已反馈主Agent；当前脚本已改为登记UUID可跨cwd纳入，明确混题UUID仍排除。主Agent报告所有本题已登记研发会话均在本题cwd。最终导出待重验。代码证据强、实际漏会话证据未建立 |
| P02 | R15/R23 | code-snapshot中引用需明确草稿与成果包语境。最终方案将traces移至包根traces/cml-spec24，则`../../../tasks/cml-spec24/changes/final.diff`成立；在草稿中应为`../../changes/final.diff` | 已向主Agent反馈，收到包根布局解释，保留两个语境标注的建议；不得把正确包内路径误判为最终缺陷。静态路径推导证据强 |

## F01：活动模拟器日志导致清单/副本不一致

关联R16、R20、R23；材料冻结时序失败，不是生产功能回归。期望：`log-copy-manifest.json`每项的bytes/SHA同时等于原logs和draft副本；实际：以下相对`logs/analysis-baseline/emulator-instances/CmlSpec24Baseline/Log/`的文件不一致。

| 文件 | 实际错误 |
| --- | --- |
| `crash_server.log` | source_hash |
| `hilog_tmp_2026-10-19T123313/hilog.036.20261019-131903.gz` | source_hash |
| `hilog_tmp_2026-10-19T123313/hilog.085.20261019-145518.gz` | copy_hash、source_hash |
| `kernel.log` | copy_hash、source_hash |
| `memInfo.log` | source_hash |

最小复现：读取当前清单，分别计算`sha256(project_root / item.path)`和`sha256(draft / item.path)`与`item.sha256`比较，并核对大小。完整原始命令/结果在本角色原生工具调用，未输出日志正文或秘密值。

归因假设：本题模拟器仍写入/轮转运行日志，清单读取与复制/复核间字节变化。证据强度：文件摘要/大小不一致为强证据；持续写入归因与进程归属尚未独立查看，仅为位置和变化模式支持的假设。本角色未停止共享/本题模拟器。

已报主Agent。建议由主Agent协调本题实例冻结，或将活动运行日志作为带明确cutoff的历史快照独立保留，并修正有限project边界、日志复制、清单和patch；不能删除失败证据或把活动日志一致性失败写成通过。修复后需重验受影响证据。由主Agent决定退回材料方案/编码或环境协调。

处理结果：主Agent采纳方案v2，精确排除宿主`Log/`整根并披露包括该根历史轮转日志一并省略，保留主动捕获证据；不停止模拟器、不动原文件。首轮失败副本移至不入包check目录，`checks/log-freeze-failure-01.json`保留失败摘要与真实重试链。v2全量重验通过，见命令9；旧失败结论不适用于新边界，但不删除旧失败记录。工程总清单/patch冻结仍待最终独立应用验证。

## F02：完整文本补丁超过Git应用限制（主Agent实际运行）

主Agent报告：16,970文件/1,291,340,382字节已物化并stage，生成完整diff为1,294,184,961字节；`git apply --check --binary`退出128，原stderr为`error: patch too large`。这次失败发生于主Agent校验进程，本角色尚未独立运行该失败补丁。证据强度以保留的`checks/patch-size-failure-01.json`、失败补丁摘要和原生工具记录为准；不能称本轮已通过apply。

拟采取的仅编码调整：在独立materialized clone的`.git/info/attributes`设置`* -diff`，以Git原生binary压缩载荷表示完整工程，不改源工程字节/范围/模式或原Git配置；另附可读`source-review.diff`供业务审查，不能替代完整patch。真实二进制资源表应在强制属性前按真实格式/标准numstat采集，不能把所有文本伪称资源。最终独立apply必须在未设置该临时属性的全新浅clone执行并全量比对；不沿用本次失败结果。

处理结果：完整compressed-binary补丁946,836,934字节，独立未设属性的全新浅clone检查和实际应用均exit0，全文件SHA/模式一致，见最终证据。可读source-review.diff为127,157字节，明确仅供阅读，不是完整工程差异替代。F02原失败仍在`checks/patch-size-failure-01.json`。

## 真实待补与结论边界

10处用户空值必须继续保留：team.version、contact、freeze_time、members[].name、members[].work、source_guard，以及task.human_edits、known_issues、extra_sources、md_export_dir。存在自动事实和已知技术限制不能静默代填用户声明；不能据空值声称无人改码、无额外来源或无问题。

客观缺口：指定官方`reports/build-baselines/cml-spec24.log`未取得；本题真实准备/构建日志仍在。Comate专有存储/版本/sessionUuid及其侧栏映射未取得，提供的是实际Codex native.id/IDE threads.id与独立父引擎字段，不伪造Comate。用户未提供IDE原生Markdown目录；现有机械副本保留原生每条记录并明确生成方式。活跃2-submit原生导出只覆盖各次cutoff，导出后的当前核验/最终答复及未来3-package活动不在该次快照中；正式冻结需重新导出真实尾部，不能声称覆盖未来。

本轮未跨机执行build.md，未重建/重跑1-do或访问官方隐藏测试；本地76项结果不是官方F-point/分数。原生过宽检索、共享Git对象复制尝试和材料失败均按实际证据披露，本角色不作来源合规裁决。无额外隐含通过声明。3-package须严格按同一project-manifest物化并复核ZIP真实文件，不能带回两个输出目录、活动宿主Log、运行盘、缓存或混题初始化原生正文；若变更project任何文件，当前diff/全树核验证据即需重新生成。
