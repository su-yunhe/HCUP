# vg-spec13 提交材料独立核验

本报告仅核验 `2-submit` 单题提交材料，不产生新的功能、构建或设备验收结论。核验 Agent 的真实 `CODEX_THREAD_ID` 为 `01a143ff-22b5-72e3-862a-7d5c9f465547`，由本次 PowerShell 进程环境读取。仅写入本报告；没有修改生产代码、配置、资源、Spec、测试或原始日志，没有运行材料生成器、构建或设备命令。每个 PowerShell 工具进程均先加载 `D:/hongmengcup/Enter-HarmonyEnv.ps1`。

最终复核于 `2026-10-16 09:29:54 UTC` 完成：`2-submit` 材料整理与一致性核验通过，F-01 已修复，可以交付本阶段材料。正式冻结、人工输入及完整活动会话尾部仍为明示待补项，按任务要求保留 `【待补充】`，不阻止本阶段交付，也不等于正式提交包已完备。下文 `blocked` 仅标识正式提交的信息缺口。最终权威封存树为 `93dafec8eb504b56d1329df5e5ad59110c66d27e`（750 文件）。下文先保留首轮失败证据，最终逐项状态和版本指纹见末节。

## 当前结论与边界

这是封存前的第一轮结果，尚未验收最终补丁。本报告所指材料会被主 Agent 修订；旧结论不自动适用于后续版本。官方清单、记录索引模板和任务清单模板均已读取。访问仅涉及本题工程、只读公共目录及获准的官方模板/本题报告路径；没有读取其他赛题、来源修复历史或跨题初始化总览原文。

| 需求/检查 | 状态 | 观察及限制 |
| --- | --- | --- |
| SUB-01 仅整理材料、保持生产冻结 | pass | 对 `workflow/implementation/source-fingerprint-v2.json` 的 299 个文件独立重算 SHA，缺失 0、不一致 0；聚合仍为 `e463b2682fed306471dc9068eadf9666cc9928c02a297363a334bf70ff7b30d3`。 |
| SUB-02 单题材料与团队阶段分工 | pass | 正文明确完整团队清单、团队根文件、ZIP 与对外提交留给阶段 3；本轮无此类操作。 |
| SUB-03 空字段、人工修改与来源声明 | pass | team/task 输入中的空字段逐项披露，不将未知人工修改、额外来源或已知问题写成“无”。正式冻结时间仍待补。 |
| SUB-04 客观字段与版本 | pass | 应用标识、依赖、构建结果有工程/日志出处；未核实的精确工具/后端/桌面版本保留待补。该项仅核验材料写法与现有证据关联。 |
| SUB-05/06 全范围 binary 补丁与 apply 比对 | not_run | 首轮检查时尚无 snapshot manifest 和 patch-validation；等待主 Agent 的封存结果后复核。 |
| SUB-07 二进制与构建噪声 | not_run | 依赖最终 snapshot/binary 清单，不能用脚本存在证明已正确生成。 |
| SUB-08 可移植构建说明 | pass | `build.md` 覆盖环境、依赖、构建、安装、启动、标识、初始化及自测；使用安装目录变量和包内相对路径。未把旧私有路径 runner 当复现入口。四个 PowerShell 代码块均仅解析，错误 0；没有实际运行这些命令。 |
| SUB-09/10/11 真实主/子轨迹、过滤与映射 | fail | 第一轮存在三份主会话被子会话覆盖，见 F-01。清单/文件 SHA 一致不能证明身份对应正确。主 Agent 已接受并开始修复；尚待重导后的独立复核。 |
| SUB-12 任务书、配置与工具记录 | pass | 公共/本题四书 SHA 与历史不存在的说明已列，实际配置和工具指向原生轨迹；身份修复后还需复核主会话配置字段。 |
| SUB-13 日志、失败与重试 | pass | `logs/copy-manifest.json` 的 337 份日志均与材料副本及原工程逐字节 SHA 一致；run01–04 和原失败未被仅保留成功的摘要替换。 |
| SUB-14 人工原始记录 | blocked | 输入 `human_edits` 未提供，正文明确待补；不据此认定“无人工直接修改代码”。这是最终提交信息缺口，材料整理没有虚构填充。 |
| SUB-15 JSON 包内路径 | pass | 片段合法 JSON；三个路径为 `/` 分隔的包内相对路径；build/trace-index 是文件路径。最终包实际目标存在性依赖阶段 3。 |
| SUB-16 两份清单、脱敏与准确披露 | pass | NEEDS-INPUT 与 AUTO-FACTS 均存在且与输入/证据关联。第一轮 14 份导出记录的 metadata 账号字段均已替换，未见非替换值；该检查不证明未披露的秘密绝不存在。正文明确 17 pass 来自 run02/run04 合并、非官方/单轮成绩，保留 not_run 和能力边界。 |
| SUB-17 完整活动会话尾部及正式冻结 | blocked | 此时会话仍活动，正文明确捕获截止与阶段 3 再导出要求，不能冒充正式全程归档。 |

## F-01：主会话被子会话覆盖（高强度文件证据）

最小复现：读取 `.comate/submission-draft/traces/native/<主 UUID>.jsonl` 中 `session_meta.payload`，比较 `id`、`session_id` 与文件名/清单 `codex_thread_id`。第一轮实测：

| 文件名声称的主会话 | 实际 metadata.id | metadata.session_id |
| --- | --- | --- |
| `01a1438a-e703-72b1-8078-9425872e0989` | `01a1438f-c587-7983-a558-f76c8a73af3e` | `01a1438a-e703-72b1-8078-9425872e0989` |
| `01a143b8-b8fa-7491-a22c-c0e5faed0de0` | `01a143bf-40f7-7d62-b34c-af46d1698de6` | `01a143b8-b8fa-7491-a22c-c0e5faed0de0` |
| `01a143f4-3a36-78a0-a6e2-8b599d476dc4` | `01a143f6-f41b-70d0-8ea0-6b6239218c8d` | `01a143f4-3a36-78a0-a6e2-8b599d476dc4` |

期望：每个导出文件与其自身 `metadata.id` 相同，真实父/子记录分别保留，继承的 engine/session 字段另行解释。实际：三个主文件均含对应子会话 metadata，清单的主角色与其原始记录不对应。

归因：`prepare_materials.py collect` 初版优先 `meta.get('session_id', meta.get('id'))`，但本次原生子会话的 `session_id` 继承父级，`id` 才是自身 thread UUID；字典键碰撞覆盖真实主记录。主 Agent 已收到原始字段证据并接受修复。建议退回材料导出实现，改用自身 `id` 并独立记录继承字段，重导、逐文件身份断言和重写文档后，再封存；不修改原始记录来伪造映射。

初轮检查命令的关键原文（仅逐行 JSON 读取，不导入或运行生成脚本）：

```python
rows = [json.loads(x) for x in p.read_bytes().splitlines()]
meta = next(r['payload'] for r in rows if r.get('type') == 'session_meta')
print({k: v for k, v in meta.items()
       if k in ('id', 'session_id', 'cwd', 'timestamp', 'source')})
```

该进程退出 0。三份 `source.subagent.thread_spawn.parent_thread_id` 也各自等于对应父 UUID，与错误归因相互印证。F-01 为本次独立核验新发现，不应从记录中删除，后续修复结果在本报告追加。

## 首轮命令、原始输出与环境

执行位置均为 `D:/HCUP/vg-spec13`，PowerShell；环境加载输出为 Harmony development environment loaded，Python 入口来自环境脚本。无设备租用、无设备操作。

1. `ast.parse(path.read_text(encoding='utf-8-sig'), filename=str(path))` 对当时两份 tools Python 文件解析；PowerShell `Language.Parser.ParseFile` 对复现 runner、`ParseInput` 对 build.md 的四段代码解析。原始结果：`python_ast_parsed=[prepare_materials.py,write_documents.py]`；`PowerShell runner parse errors: 0`；四次 `Build block parse errors: 0`。退出 0。之后新增/修改的脚本需重新解析。
2. JSONL 逐行解析、导出 SHA/大小/行数/尾时间、Markdown 逐行包含性核对。原始结果：`inventory_sessions=14`，无 SHA、大小、行数、尾时间、Markdown 缺行错误；仅上述三条 metadata 身份不符；`unredacted_metadata_fields=[]`；各清单 `incomplete_lines_omitted=0`。退出 0。检查程序报告不符不以 shell 退出 0 冒充通过。
3. 对 copy-manifest 的每条路径同时计算原工程与 draft 副本 SHA。原始结果：`log_manifest_count=337, log_errors=[]`。退出 0。
4. 对 299 项生产/配置清单 SHA 与聚合重算。原始结果：`source_count=299, missing=[], hash_mismatch=[], aggregate=e463b2682fed306471dc9068eadf9666cc9928c02a297363a334bf70ff7b30d3`。同一探索进程随后因另一处 `Path.read_text()` 未显式 UTF-8 而发生 `UnicodeDecodeError: 'gbk' codec can't decode byte 0x8c in position 26`，最终退出 1；此失败保留，后续只读复查改为 `encoding='utf-8-sig'` 后退出 0。
5. 官方 trace-index 24 项与正文 24 项逐语义阅读，均有对应条目。严格标题匹配会对四个略写标题误报，已反馈主 Agent 保持模板原字段名；`validate_materials.py` 初版的 Windows 路径正则还会把 `https://` 的 `s:/` 误识别为私有路径，已反馈加边界。这两项为验证器实现问题，不能修改事实或正文来源以迎合错误断言。

本报告尚未宣布最终材料通过；待主 Agent 通知后追加封存工程、补丁、过滤/脱敏、真实 ID 和最终脚本指纹复核结果。

## 最终封存与修复复核

本节覆盖前述首轮状态，保留首轮失败作为历史。主 Agent 在独立复核期间曾把已成功的 753 文件版本改为排除三个 Python 字节码缓存的 750 文件版本；本核验立即作废受影响的旧封存结论并对新版本重新核对，未沿用旧成功摘要。旧树 `4ac2b7bc067d7437c9bf9db430c1ecf7e6d38148` 的成功记录保存在 `audits/patch-validation-before-cache-filter.json`，不作为最终版本。

| 需求/检查 | 最终状态 | 独立复核证据 |
| --- | --- | --- |
| SUB-01 生产冻结 | pass | 活跃工程与封存工程分别对同一 299 项 v2 指纹复核，均无缺失/不符。全部封存文件的原工程字节仍等于 manifest 的 `workspace_sha256`；没有发现封存后源文件变化。 |
| SUB-02 阶段范围 | pass | 本阶段只整理单题材料；正式团队文件、ZIP、外部提交未执行。 |
| SUB-03 空字段披露 | pass | 输入空字段仍为待补，未编造冻结时间、人工分工/修改或额外来源。 |
| SUB-04 事实与版本 | pass | 正文三处最终 tree 均为新 750 文件 tree，旧的“该值将由工具实测填写”占位已消失；base 与本题 metadata 一致。 |
| SUB-05 全范围 binary 差异 | pass | 独立 `git ls-files -c -o --exclude-standard -z` 得到除 staging 外 759 文件；除清单明确排除的 6 份跨题原文和 3 份缓存，全部 750 文件纳入封存，无遗漏、额外项或混入排除项。 |
| SUB-06 apply 与逐文件一致 | pass | 主 Agent 最终记录：两份本题 clone，官方 base，`git apply --check --binary` 和实际 apply 退出均 0，比较 750 文件，missing/extra/hash_mismatches 均空。本核验独立重算封存全部文件 SHA、文件集合、聚合、diff SHA/大小及 tree 关联，全部一致；本角色没有再次执行 apply，不将记录审查描述为自己重跑 apply。 |
| SUB-07 二进制与生成噪声 | pass | 独立按内容 NUL/二进制扩展筛得 75 项，与 binary inventory 一一对应，大小/SHA 全符；8 项用本题官方 base 的 `git cat-file blob` 独立比对相同，67 项为日志目录内本地截图证据。未知来源 0。封存中无 `.pyc`、`__pycache__`、`.git` 或递归 staging。 |
| SUB-08 可移植构建说明 | pass | 修正后的路径检查无私有绝对路径；PowerShell runner 及 build 四段代码最终解析均 0 错误。仅解析，没有运行新的构建/设备/自测命令。 |
| SUB-09/10/11 真实会话身份与范围 | pass | F-01 修复后 15 个导出文件各自 `session_meta.id` 均等于文件 UUID/清单 `codex_thread_id`；继承的 `session_id` 单列为 `codex_engine_session_id`，不再冒充自身。三个主会话均恢复其真实 ID。SHA、大小、行数、尾时间、源文件名、Markdown 逐记录包含性和全量工具计数均一致，已登记专用会话 missing 为空。 |
| SUB-12 配置、任务书与工具 | pass | 四份公共/本题任务书 SHA 独立重算均符，`spec/history` 确认不存在。四份材料工具及八份 Harness Python 共 12 文件 AST 全通过。新增 Skill 读取索引 19 项、5 路径，其每条 native 行号/call_id/tool/timestamp 指针均匹配；未运行索引生成脚本或访问这些外部 Skill。 |
| SUB-13 来源/协作片段、日志与失败 | pass | sources/solution/submission 三份片段均存在并如实区分自动事实、待补人工字段与本地测试范围。337 份日志在原工程、材料 logs、封存 project 三处 SHA 均符；原失败未覆盖。首次 patch CRLF 失败及随后缓存过滤导致的封存修订均保留独立记录。 |
| SUB-14 人工原始记录 | blocked | 用户 `human_edits` 等空字段仍待提供/确认；整理者不能自行解除此真实信息缺口。 |
| SUB-15 包内路径与模板字段 | pass | 官方 24 个字段名已逐字匹配，无缺漏。JSON 三个路径仍为包内相对路径，两个说明目标为文件；最终成果包汇总仍属阶段 3。 |
| SUB-16 两份清单、脱敏与准确披露 | pass | NEEDS-INPUT/AUTO-FACTS 两份清单均已提供，未用自动事实覆盖用户空字段。从本工程已存在的相关原始轨迹 metadata 提取 2 个账号标识，仅用于不回显的本地比对。材料目录全部文件中这些字面值命中 0；封存 30 份旧 native 文件账号字段均替换。逐字节复算证明 750 文件与原工程只相差 manifest 声明的账号替换，没有额外删改。该定向扫描不承诺未知账号/秘密绝不存在。 |
| SUB-17 正式冻结和完整活动尾部 | blocked | 仍需阶段 3 正式停止相关任务、统一冻结时间并导出捕获后的真实尾部。当前有限快照边界已披露；本报告产生在此前捕获之后，不能假称已存在于更早导出中。 |

### 首次 patch 失败及修复证据

`audits/patch-roundtrip-failed-v1.json` 保留了首次失败补丁 SHA `4413254fb7f1b920d4d2fa66dcbbf432fedf7620b0352a2e16a74109f3109120` 及 76 项 SHA/大小/CRLF 明细。其 missing/extra 为空，但 76 项字节不一致；每项大小增量均恰等于新增 CRLF 数量。最小例子：`ManualWebDavBackupController.ets` 期望 4223 字节、CRLF=0，实际 4333 字节、CRLF=110，两个 SHA 不同。这是失败，不能以 apply 命令本身成功代替内容一致性。

最终 `changes/patch-validation.json` 的实际命令全部显式带 `git -c core.autocrlf=false -c core.eol=lf`；记录了官方 base checkout、`--binary --full-index` diff、apply check、实际 apply 及最终全文件一致。该证据支持 Git 换行配置造成首次偏差并已修复的归因；没有改生产文件或放宽比较断言。之后发现 3 份 `test-harness/harness/__pycache__/*.pyc` 为生成缓存，仅从封存选择中排除，源文件仍在原位；新清单 `excluded_generated_files` 单列三项。完整补丁对应新封存工程，旧 753 文件证据不混入当前结论。

### 最终独立检查原始结果

以下只读核验进程均退出 0；完整工具调用中的脚本与输出属于本核验原生会话。使用 `ast.parse` 而非 import，PowerShell `Parser` 而非执行；没有运行材料生成器。

```json
{
  "git_visible_file_count_except_staging": 759,
  "declared_excluded_files": 9,
  "git_visible_missing_from_snapshot": [],
  "unexpected_snapshot_files": [],
  "excluded_files_in_snapshot": [],
  "snapshot_files": 750,
  "file_set_and_hashes_match": true,
  "patch_files_compared": 750,
  "patch_apply_check_exit_recorded": 0,
  "patch_apply_exit_recorded": 0,
  "patch_missing_extra_hash_mismatches": [[], [], []],
  "binary_records": 75,
  "binary_errors": [],
  "binary_origins": {"official_baseline_unchanged": 8, "local_UI_test_evidence": 67},
  "production_reference_count": 299,
  "live_and_sealed_production_mismatches": [[], []],
  "logs_compared_in_three_locations": 337,
  "log_errors": [],
  "official_exact_trace_labels": 24,
  "absent_exact_labels": [],
  "build_private_paths": [],
  "exported_sessions": 15,
  "trace_errors": [],
  "known_identity_literal_hits_any_draft_file": [],
  "snapshot_bytes_differ_only_by_declared_account_redaction": true,
  "source_workspace_changed_since_seal": [],
  "python_AST_files": 12,
  "python_AST_errors": 0,
  "runner_and_four_build_blocks_PS_parse_errors": [0, 0, 0, 0, 0],
  "skill_read_entries": 19,
  "skill_unique_paths": 5,
  "skill_pointer_errors": [],
  "taskbook_hash_errors": [],
  "material_validator_recorded_checks": 16,
  "material_validator_recorded_failures": []
}
```

核验使用的完整范围命令为 `git -c core.quotepath=false ls-files -c -o --exclude-standard -z`（退出 0）；只对本题 base 中 8 个同路径二进制使用 `git cat-file blob <base>:<path>`（逐次检查返回码 0 及 SHA）。其它核验均使用 Python 标准库 `Path/json/hashlib/ast` 读取本题文件。原始 SHA/文件集合比较没有放宽成文本换行等价。

### 最终版本指纹

| 对象 | 结果/摘要 |
| --- | --- |
| 官方 base | `88db8789e28333c7b7dcc8db078f394a262b73c3` |
| 最终 Git tree | `93dafec8eb504b56d1329df5e5ad59110c66d27e` |
| manifest 聚合 | `a2a39f50228e6add93be0d3d5e264c38da8e09ab348c176961bc0dfd14d1df45` |
| final.diff 字节数 | `82722306` |
| final.diff SHA-256 | `8973cdc960ca5e6c02b33cd549258f4684c7d4ede1ceb9b444c5ef406b3ba837` |
| snapshot manifest SHA-256 | `fe7bfcb1e3903facb19454c6e4092a60ebcce86ebb4b0a02cefb463c4da447d0` |
| patch-validation SHA-256 | `e6cfd33dc18dd8d34f39bec27fa1380a8e4e4af9ec8fcaf891ba27a3ce05f617` |
| tools/prepare_materials.py SHA-256 | `a5de26bae1a35365416912130633536d17cd831adedc7b57f40072e3f9bebcf9` |
| tools/validate_materials.py SHA-256 | `504e52c051959fc4e78a9cde492033aadad44f0b71e54eb8c525538ce24318fd` |
| tools/write_documents.py SHA-256 | `26e172e29cc2a9dacc11fc8ca2f9df99f4fe00ab26f0ff9c6beb3daca196fb9b` |
| tools/index_skill_reads.py SHA-256 | `1423e52e69aabfa03a621def66f92f216c320a5eae566e166eb2aa991d023813` |
| repro-support/run-selftest.ps1 SHA-256 | `cf1c12491f91724cc9317181164b9e07fbf333a5523dcdd696201ff77871742a` |

最终两次检查中 manifest/patch-validation 摘要保持相同。后续仅刷新材料层原生记录时，需按实更新其 inventory/校验和；如果修改封存工程、补丁或正文，此报告中相关版本结论应重新核验。人工输入/官方基线报告等无法补取的真实缺口继续列于 NEEDS-INPUT，不把它们记为已经提供。
