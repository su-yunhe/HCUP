"""Render factual, task-local submission documentation from collected evidence."""
from prepare_materials import ROOT, OUT, PENDING, read, write, dump, yaml_values, sha


def generate():
    team = yaml_values(ROOT.parent / 'common/spec-harness/team.yaml')
    local = yaml_values(ROOT / 'spec/submit-input.yaml')
    state = read(ROOT / 'workflow/state.json')
    inventory = read(OUT / 'traces/session-inventory.json')
    taskbooks = read(OUT / 'traces/taskbook-version.json')
    base = read(ROOT / 'spec/metadata.json')['base_commit']
    acceptance = read(ROOT / 'workflow/local-acceptance.json')
    frozen = read(OUT / 'traces/code-snapshot/manifest.json') if (OUT / 'traces/code-snapshot/manifest.json').exists() else None
    tree = frozen['git_tree'] if frozen else '见封存后 traces/code-snapshot/manifest.json 的 git_tree（该值将由工具实测填写）'
    table = '\n'.join(f'| `{x["codex_thread_id"]}` | {", ".join(x["roles"]) or "本题专用会话，角色见原始记录"} | {", ".join(x["models"]) or PENDING} | {", ".join(x["efforts"]) or PENDING} | {x["cli_version"] or PENDING} |' for x in inventory)
    taskbook_table = '\n'.join(f'| `{name}` | `{v["common_sha256"]}` | `{v["project_sha256"]}` |' for name, v in taskbooks['files'].items())
    write('submission.json.fragment', __import__('json').dumps({
        'task_id': 'vg-spec13', 'status': 'submitted',
        'project_path': 'tasks/vg-spec13/project',
        'build_instructions': 'tasks/vg-spec13/build.md',
        'trace_index': 'tasks/vg-spec13/trace-index.md',
    }, ensure_ascii=False, indent=2) + '\n')
    write('build.md', '''# vg-spec13 构建与运行

本文件按成果包内 `tasks/vg-spec13/` 编写，完整工程为同级 `project/`；命令中的位置由当前包路径计算，不依赖参赛电脑上的目录。历史原始命令和输出另见 `logs/`。

## 环境与声明

本地实测 DevEco Studio 6.1.0.860、SDK 6.1.0.105/API 23，HarmonyOS 模拟器 6.1.0.115(SP11DEVC00E115R4P11)、API 23、1308×2880、VirtualPixelRatio 3.5。机型没有独立确认，不能据此宣称满足全部官方屏幕/机型规格。Python 环境为 3.12.3，Hypium 6.1.0.210，uitest 6.0.2.3（见原运行证据及 `audits/build-evidence.md`）。

工程本身声明 `targetSdkVersion` / `compatibleSdkVersion` 为 `6.0.2(22)`，`modelVersion` 为 `6.0.2`，没有为本次材料改写。`signingConfigs=[]`。工具链版本与工程兼容声明是不同字段。Node、Java、OHPM、Hvigor 的独立精确版本未从现有日志核实，标记【待补充】，使用该 DevEco 配套工具。

在 Windows PowerShell 中由复现者把环境变量 `DEVECO_STUDIO_HOME` 设为已安装 Studio 的目录，把 `DEVECO_SDK_HOME` 设为 API 23 SDK 根目录，然后执行：

```powershell
$ErrorActionPreference = 'Stop'
if (-not $env:DEVECO_STUDIO_HOME -or -not $env:DEVECO_SDK_HOME) { throw 'Set Studio and API 23 SDK environment variables first.' }
$taskDir = (Get-Location).Path # 当前为 tasks/vg-spec13
$projectDir = Join-Path $taskDir 'project'
$env:JAVA_HOME = Join-Path $env:DEVECO_STUDIO_HOME 'jbr'
$env:NODE_HOME = Join-Path $env:DEVECO_STUDIO_HOME 'tools/node'
$toolPaths = @(
  (Join-Path $env:JAVA_HOME 'bin'), $env:NODE_HOME,
  (Join-Path $env:DEVECO_STUDIO_HOME 'tools/ohpm/bin'),
  (Join-Path $env:DEVECO_STUDIO_HOME 'tools/hvigor/bin'),
  (Join-Path $env:DEVECO_SDK_HOME 'default/openharmony/toolchains'),
  (Join-Path $env:DEVECO_SDK_HOME 'default/hms/toolchains')
)
$env:Path = ($toolPaths -join ';') + ';' + $env:Path
Set-Location -LiteralPath $projectDir
```

工程没有自带 hvigor wrapper；`hvigorw.bat` 来自 Studio 配套工具。不要执行工程旧 `workflow/verification` runner 来替代以上初始化，它们属于历史证据，含原运行机路径。

## 依赖、构建与产物

根 `oh-package.json5` 的开发依赖为 `@ohos/hypium=1.0.24`、`@ohos/hamock=1.0.0`，entry 模块无额外包依赖；提交完整 `oh-package-lock.json5`，不得只交安装包。

```powershell
ohpm install --all --registry https://ohpm.openharmony.cn/ohpm/ --strict_ssl true
if ($LASTEXITCODE -ne 0) { throw 'ohpm install failed' }
hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon
if ($LASTEXITCODE -ne 0) { throw 'assembleHap failed' }
$hap = Join-Path $projectDir 'entry/build/default/outputs/default/entry-default-unsigned.hap'
Get-FileHash -LiteralPath $hap -Algorithm SHA256
```

依赖安装与实现构建均退出 0（`logs/implementation-build/20261016-162656-result.json`）；独立 run02、run03 的 clean 构建退出 0。历史最终安装产物 SHA-256：`40971677431e7da2238dcff28e814dbe0ed81b889c093ee249be638fb34fd341`，大小见 `changes/verified-hap.json`。重新构建的容器时间/工具环境可能导致包字节不同，此摘要标识历史实际测试产物。

## 安装与启动

```powershell
hdc list targets
$device = '127.0.0.1:5555' # 本地实测设备；复现时替换为 discovery 返回的目标
hdc -t $device install -r $hap
if ($LASTEXITCODE -ne 0) { throw 'install failed' }
hdc -t $device shell aa start -a EntryAbility -b io.qzz.weiyu
```

应用 `bundleName=io.qzz.weiyu`，入口 `EntryAbility`，模块 `entry`，版本 `1.0.0` / `1000000`。来源：工程 `AppScope/app.json5` 与 `entry/src/main/module.json5`。上述 unsigned HAP 曾在所记录模拟器安装成功；对要求签名的物理设备，需要复现者按该设备配置自己的合法签名，本阶段不提供或复制私钥。

首次进入按界面完成必要引导。首页⚙→设置→WebDAV 同步，输入合法地址、账号、密码、至少四位同步密码及远程目录，点击“立即备份”。填入的当前配置用于本轮备份；自动同步应关闭以隔离手动测试。真实服务必须具备所需网络/目录权限。原运行的临时端点与凭据只用于本地 fixture，不是可连接的线上服务。无额外数据库初始化，历史本地数据为空库，不声明非空大库覆盖。

## 可移植自测入口

`repro-support/test-harness/` 是只读公共 Harness 的随材料副本，`requirements.txt` 固定 Hypium 版本。打包时连同 `repro-support/run-selftest.ps1` 复制到本题材料目录。建立本题独立虚拟环境不会改工程或公共框架：

```powershell
Set-Location -LiteralPath $taskDir
python -m venv .repro-venv
& ./.repro-venv/Scripts/python.exe -m pip install -r ./repro-support/test-harness/requirements.txt --index-url https://repo.huaweicloud.com/repository/pypi/simple
& ./repro-support/run-selftest.ps1 -Device $device -Python ./.repro-venv/Scripts/python.exe
```

先安装本轮刚构建的 HAP，再独占设备运行；脚本拒绝主机18173/18174/18175或设备18173/18174已有映射。测试创建本机18173/18174的合成WebDAV服务并经hdc反向映射；脚本只移除本轮创建的映射。自测会操作应用设置并保存合成配置，适用于独立测试模拟器。它使用提交工程原有 `hypium_tests`，从新日志目录运行，不覆盖历史失败记录。此入口是本次材料整理写出的可移植等价脚本，本阶段没有重新运行设备测试。

历史结果：同一 v2 源码 `run02` test00–13 与 `run04` test14–16 合并 17 pass；run02 原始15例为14 pass/1 fail，run04定向3例通过。run01/run03 中断保留。不是单次全套17/17，也不是官方评测。D03、B09、B16、B18、B19为 not_run；非预期本地异常、真实服务商/TLS、解密恢复、非空大库等限制见 `solution.fragment.md` 与工程 `workflow/verification/final-report.md`。原始日志齐备，不需要为补日志重跑业务。
''')
    write('human-changes.md', f'''# vg-spec13 人工操作与修改索引

`spec/submit-input.yaml:human_edits` 留空：{PENDING}。不能据 AI 会话或 Git 差异推断“无人工直接修改代码”。请补充人工操作人、目的、文件、前后版本和当时原始证据；若确认没有直接改代码，由用户填写该声明。

已知人工提示可按主/子会话原生轨迹中的 user 消息读取；AI 改动与失败重试可按 `trace-index.md` 和 `changes/final.diff` 读取。这些记录不自动证明其他人工操作不存在。整体 final.diff 不作为人工贡献归属证明。
''')
    write('sources.fragment.md', f'''# vg-spec13 来源片段

随包官方基线：`spec/metadata.json` 的 `{base}`，基线 bundle 标识 `repo_bundles/vignette-88db8789e2-base.bundle`。本题没有访问该来源项目的修复提交、PR、Issue或其副本；这是本次材料整理的访问事实，不替用户声明历史人工访问情况。

基线准备来源由工程 `workflow/baseline-provenance.json` 记录，bundle SHA-256 为 `50225027e85b86be317d42b8625c9f5ca7760e0b251b9915a4b1bd0eaaa5b9c5`；本阶段只读本题已保存的元数据和记录，未重新访问题包 bundle/specs/metadata。基线原有二进制资源的逐文件路径、大小、SHA-256及同源判断见 `changes/binary-files.json`；新增截图属于本题本地自测证据。

本题已记录的额外通用技术资料：[OpenHarmony 官方 @Builder 文档](https://raw.githubusercontent.com/openharmony/docs/master/zh-cn/application-dev/ui/state-management/arkts-builder.md)。实际检索和修订依据见工程 `workflow/design/final-source-review-v1.md` 与设计主/子会话；原始Gitee读取405失败与随后GitHub原文读取均保留。这里只转录既有来源证据，不声称本次重新访问网页。自动提取的工具输入URL另见 `traces/tool-input-urls.json`，它是候选索引，不能把每个URL都当成实际采用来源。

公共测试工具来自只读 `common/test-harness` 的实际副本 `repro-support/test-harness/`，锁定 Hypium 6.1.0.210；应用开发依赖来源见 `build.md`、工程 `oh-package.json5` / `oh-package-lock.json5`。实际 Skill、角色和工作流配置保存于工程 `system-config/` 既有快照及原生会话指令，不在本阶段重建团队级配置。

用户 `extra_sources` 留空：{PENDING}。需要用户披露全部额外来源/代码复用/人工检索及是否访问过受保护内容，不能自动写“无”。团队来源保护正式声明 `source_guard`：{PENDING}；可核实的本题限制写在工程 `AGENTS.md`、本题任务书与原生会话指令中。
''')
    write('solution.fragment.md', f'''# vg-spec13 完成情况与协作片段

已实现“立即备份”期间可见的原生 LoadingProgress 和“正在备份到云端...”文案，以独立手动任务控制器管理状态、快照本轮输入，并沿真实预检/导出/加密/上传链完成请求。业务改动六文件见工程 `workflow/local-acceptance.json`，本阶段未修改业务代码、资源或配置。

AI 实际参与需求与边界分析、方案设计及Builder方案修订、编码、独立构建/自测、测试oracle复审、失败诊断与重试和本阶段材料整理。需求/方案/实现/验证为真实子会话，关联UUID及工具调用见 `traces/session-inventory.json` 和 `trace-index.md`。人工分工：{PENDING}；人工直接代码修改：{local.get('human_edits', PENDING)}。

本地必需 A01–A16、R01–R10有通过证据。17 pass为同一源码run02前14例+run04后3例合并，不是单次17/17，也不等于官方F-point/隐藏测试成绩。run02 test14原失败经需求复审认定旧测试对其它任务占用提示的词匹配过度；只修正相应oracle，原失败与复审保留。其它失败/中断、未采用方案见工程 workflow 和原始会话。

客观限制：D03/B18/B19未做本地非预期异常注入；B09/B16不适用并保留not_run；真实TLS/服务商语义、解密恢复、非空大库性能及全部官方机型规格未验证。旧ESObject/废弃API等警告仍存在；独立clean编译警告759→756，新增0。用户 `known_issues` 留空：{local.get('known_issues', PENDING)}，不能替填“无已知问题”。官方隐藏测试未运行。

成果包冻结北京时间：{team.get('freeze_time', PENDING)}，由团队统一提供；与材料脚本UTC捕获时间、历史业务冻结时间是不同概念。官方基线 `{base}`；提交工程树 `{tree}`；完整范围和校验见 `DELIVERY.md`、`changes/patch-validation.json`。阶段3须使用封存 `traces/code-snapshot/project/`，并把本材料作为工程外的任务材料复制。

来源保护：本次只访问本工程、只读公共资料、官方templates与指定本题日志路径；原初始化总览会话的六份跨题原文副本排除；未读取它们作为开发参考。团队正式来源保护描述：{team.get('source_guard', PENDING)}。账号标识脱敏、缺失和导出边界见 `trace-index.md`。没有上传、打包赛事ZIP或对外提交。
''')
    trace = f'''# 运行记录索引

- 题目 ID：vg-spec13。
- AI 在本题实际参与的研发环节、用途及对应原始会话／事件范围：需求分析、方案审查/修订、编码、独立构建与自测、oracle复审、失败重试和材料整理；阶段与UUID见下表、工程 `workflow/events.jsonl`、`traces/session-inventory.json`。原始消息而非摘要证明参与。
- 基线构建准备：本题 `logs/prepare-baseline.log` 实际记录 profile=`harmony-cup-build-v1`、dry_run=false、changes=[]；准备记录 `workflow/setup-result.json` 的 prepared_at=`2026-10-16T07:08:01.277080+00:00`（这是记录生成时间，不冒充脚本准确执行时刻）。指定题包 `reports/build-baselines/vg-spec13.log` 不存在；该官方报告中的脚本配置版本/执行时间为{PENDING}。本地安装/构建日志可读取但不冒充缺失官方日志。
- Agent 名称及版本：原生记录 originator=Codex Desktop；逐会话 `cli_version` 见表。Comate 客户端/扩展未使用且指定文件不存在，其版本为{PENDING}（不适用，不能填入Codex CLI版本）；独立桌面GUI版本未取得。Agent角色/实例见工程state及逐会话记录。
- 模型名称、版本及运行参数：逐会话实际 `turn_context.model` / `effort` 见表；精确模型后端权重版本未输出，{PENDING}。token用量保留原生 `token_count.info.total_token_usage` 的最近观测值与时间，不推算计费量或重复汇总继承计数。
- 本题实际使用的 Skill、系统提示、工具及编排配置版本和保存位置：工程 `system-config/initial-20261016T070659Z/` 保存既有Skill/角色/环境快照；实际提示在原生 session_meta/turn_context/user 消息；工具清单 `traces/tools-used.json`，完整参数/结果在各JSONL。任务书版本见后表与 `traces/taskbook-version.json`；本题 `spec/history/` 不存在，没有历史任务书可列。
- 运行期间配置变更及原因（无则填“无”）：正式解题中需求/方案及oracle修订有 workflow/events 和对应版本文件。本阶段新增材料导出和等价复现入口，不改团队配置。无法从现有记录证明整个期间从未配置变更，不自动写“无”；团队补充项为{PENDING}。
- 主会话 ID：分析 `01a1438a-e703-72b1-8078-9425872e0989`；实现 `01a143b8-b8fa-7491-a22c-c0e5faed0de0`；本阶段 `01a143f4-3a36-78a0-a6e2-8b599d476dc4`。初始化总览 `01a13fc4-2611-7761-a580-1283e0c70541` 含跨题内容，未提交其原文或用作研发证据。
- 关联会话及子会话 ID：见下表与 `traces/session-inventory.json`，按工程绝对路径与题号两维查找，并按已登记UUID补查。Comate engine `sessionUuid`={PENDING}（无Comate库/字段，不能伪造）；IDE侧边栏为Codex chat UUID，同原生 session_meta.id/session_id 及实际 CODEX_THREAD_ID。仅能说明真实Codex映射，不能制造两个不同产品的ID。
- 解题过程中产生的全部相关原始日志、DB 或原生轨迹文件路径及读取方式：`traces/native/<UUID>.jsonl` 是按本题筛选的原生结构记录（仅账号标识脱敏），逐行JSON读取；`traces/session-index.filtered.jsonl`为对应metadata索引；`traces/markdown/<UUID>.md`为工具生成的逐记录Markdown副本。旧工程 `traces/native` 保留本题相关既有快照，但其历史manifest中的初始化总览原文引用已明确不随包，最终封存manifest为权威文件清单。
- 失败、重试、未采用的候选方案及选择过程的记录位置：工程 `workflow/state.json:failures`、`workflow/design/final-source-review-v1.md`、`workflow/requirements/test14-oracle-review-v1.md`、全部run01–04日志及原生工具调用。基线缺spinner、Builder方案风险、run01/run03中断、run02原失败及修复复测均保留；没有只选成功记录。
- 实际提示、工具调用及返回结果、检索与代码修改、构建和自测记录位置：`traces/native/`完整记录、工程workflow各角色版本、`changes/final.diff`与`logs/`；完整日志SHA清单 `logs/copy-manifest.json`。
- 导出时间、方法与读取方式：`traces/discovery.json`及每会话inventory记录真实UTC捕获时间，`tools/prepare_materials.py collect`按本题选择导出；原文件SHA与脱敏导出SHA分开保存。活跃会话只涵盖捕获前已写完的记录，之后的审核、导出与最终消息不可能包含在更早快照；不声称覆盖未来记录。用户 `md_export_dir`={local.get('md_export_dir', PENDING)}，未伪称IDE原生Markdown导出。
- 成果冻结时间（北京时间，与 `solution.md` 一致）：{team.get('freeze_time', PENDING)}。工程业务冻结记录 `2026-10-16T08:28:05.023355+00:00`；不是由团队提供的正式成果冻结时间。
- 官方工程基线标识（本次题包 metadata.base_commit 发布提交号）、最终提交版本标识：`{base}`；最终内容Git树 `{tree}`，全文件SHA和聚合见 `traces/code-snapshot/manifest.json`。当前HEAD仍是基线，不能用HEAD单独标识未提交改动。
- 基线至提交版本的完整差异位置（建议 changes/final.diff，含新增、修改、删除；二进制变更另列文件及摘要）：`changes/final.diff`（--binary、--full-index）；`changes/binary-files.json`。范围覆盖封存工程全部Git可见源码/过程文件，包括spec/hypium_tests/配置/日志/相关轨迹及任意工程内非staging的.comate文件。
- 与提交源码的对应关系：未来 `tasks/vg-spec13/project/`必须直接来自 `traces/code-snapshot/project/`，不要从活跃目录递归复制材料暂存目录；否则diff自引用且不对应版本。补丁在两份临时本题clone、官方base下先check再apply，逐文件SHA与文件集合全比对，结果 `changes/patch-validation.json`。本阶段前后业务指纹299项核对见独立审计。
- 人工操作及相关记录位置：用户提示见原始会话；其它人工操作 `spec/submit-input.yaml:human_edits`={local.get('human_edits', PENDING)}；不猜测操作者与分工。
- 人工修改索引位置（可使用 human-changes.md；无则注明“无人工直接修改代码”）：`human-changes.md`；用户未确认“无”，因此保留{PENDING}。
- 人工修改的操作人、目的、文件、代码差异、修改前后版本及对应原始记录位置：{PENDING}，由用户据实填写，整体final.diff不能替代人工原始证据。
- 公开资料检索与代码复用记录位置，以及 sources.md 中的对应来源条目：`sources.fragment.md`供阶段3汇入根sources.md；已核实Builder官方资料与其原生检索记录，额外人工来源 `extra_sources`={local.get('extra_sources', PENDING)}。
- 本题工作目录，以及赛题来源保护措施在本题运行中的配置位置（见 solution.md）：原工作区为工程AGENTS记录的本题专用目录，成果包路径 `tasks/vg-spec13/project/`；限制配置为工程 `AGENTS.md`、本题任务书与原生指令；团队 `source_guard`={team.get('source_guard', PENDING)}。本阶段不读其他题/来源修复；初始化总览原文不提交。
- 脱敏范围（无则填“无”）：仅原生会话creator_user_id/creator_account_id及这些账号字面值在内嵌工具输出中的重复出现；不改会话UUID、代码来源、模型/时间、失败、工具调用和返回。混题初始化原文排除而非伪称脱敏后的完整会话，详见 `traces/redaction-policy.json`及snapshot排除清单。旧manifest里的SHA标识原件，最终提交文件SHA以snapshot清单为准。日志未编辑，原本机路径保留作证据，不作为build.md的运行依赖。
- 记录缺失及原因（无则填“无”）：指定官方基线报告缺失；Comate库/字段/版本不适用于本次Codex实际研发，故无法提供Comate专属字段；独立桌面GUI版本及精确后端版本未取得；IDE导出Markdown目录未提供，改附明确标记的派生副本；活跃会话捕获后记录属于时间边界；人工空字段仍待补。已登记本题专用历史会话未发现缺失，不能因此宣称所有人工或客户端外操作记录齐备。

## 会话、角色与配置证据

| Codex 原生/IDE chat UUID | 已登记角色 | 原生model | effort | 原生CLI版本 |
| --- | --- | --- | --- | --- |
{table}

token字段、每会话工具调用数、来源路径与双SHA见 `traces/session-inventory.json`。原生模型与effort按记录逐会话填写，不把当前模型套到历史会话。

## 本题任务书版本

公共spec-harness没有独立`.git`，本次记录以下四书的实际SHA；工程副本与公共当前版本是否相同由表中值判断，不假定历史版本。`spec/history/`不存在。

| 文件 | 公共当前SHA-256 | 本题使用副本SHA-256 |
| --- | --- | --- |
{taskbook_table}
'''
    template = __import__('pathlib').Path('D:/SWE-OpenHarmony/templates/trace-index.md').read_text(encoding='utf-8-sig')
    labels = [line[2:].split('：')[0] for line in template.splitlines() if line.startswith('- ')]
    lines = trace.splitlines()
    indexes = [i for i, line in enumerate(lines) if line.startswith('- ')]
    assert len(labels) == len(indexes) == 24
    for i, label in zip(indexes, labels):
        lines[i] = '- ' + label + '：' + lines[i].split('：', 1)[1]
    trace = '\n'.join(lines) + '\n'
    trace = trace.replace('同原生 session_meta.id/session_id 及实际 CODEX_THREAD_ID', '同原生 session_meta.id 及实际 CODEX_THREAD_ID；session_meta.session_id 是独立保留的引擎关联字段，子会话可继承根会话值')
    trace = trace.replace('公共spec-harness没有独立`.git`，本次记录以下四书的实际SHA', '公共spec-harness没有独立`.git`，父仓库HEAD另存于taskbook-version.json，本次同时记录以下四书的实际SHA')
    write('trace-index.md', trace)
    write('NEEDS-INPUT.md', '''# 仍需用户补充

以下来自输入文件的空字段，未推测，所有正文统一标记【待补充】：

| 来源 | 字段 | 需要的事实 |
| --- | --- | --- |
| common/spec-harness/team.yaml | version | 成果包版本 |
| 同上 | contact | 联系人及联系方式 |
| 同上 | freeze_time | 正式成果冻结北京时间，阶段3统一 |
| 同上 | members[].name / work | 成员姓名及实际分工 |
| 同上 | source_guard | 实际来源保护措施 |
| spec/submit-input.yaml | human_edits | 无人工直接改代码的确认，或操作人/目的/文件/前后版本/原始证据 |
| 同上 | known_issues | 用户确认的未完成项和已知问题；已观测测试限制已另行如实列出 |
| 同上 | extra_sources | 额外来源、复用及人工来源访问情况，不能留空推断“无” |
| 同上 | md_export_dir | 若有IDE导出的Markdown，提供目录；当前附明确标记的派生副本 |

需要补齐或确认的原始记录缺口：指定题包基线准备报告不存在；如持有原报告可补入。Comate专属sessionUuid/客户端/扩展版本没有真实来源，本次用Codex原生证据，不得编造。独立桌面GUI版本、精确后端模型版本和未核实工具独立版本保留待补充，若运行器本来不输出应说明不可获得。

`submitted_tasks`、`attempted_not_submitted`、`zip_out`是阶段3专用字段，本阶段不代填。官方最终成果冻结和完整活跃会话尾部导出也由阶段3在停止相关任务后处理，不得用新记录替代原解题证据。
''')
    write('AUTO-FACTS.md', f'''# 已自动填入的事实及出处

| 事实 | 真实来源 |
| --- | --- |
| 团队 HC2026-111 / Ghost_London / online | common/spec-harness/team.yaml 的非空字段 |
| 题号 vg-spec13；base `{base}` | spec/submit-input.yaml、spec/metadata.json |
| 官方基线bundle名与摘要 | workflow/baseline-provenance.json；本阶段未重读题包bundle |
| io.qzz.weiyu / EntryAbility / entry / 1.0.0 | AppScope/app.json5、entry/src/main/module.json5 |
| SDK声明6.0.2(22)、空签名、模块default | build-profile.json5 |
| @ohos/hypium 1.0.24、hamock 1.0.0及锁文件 | 根与entry的oh-package.json5、oh-package-lock.json5 |
| 依赖、构建、安装、启动命令及成功记录 | logs/implementation-build/*result.json、run02/run03/run04/commands.log及install.log |
| 17 pass为run02/run04合并、未执行项和警告变化 | logs/selftest.json、workflow/local-acceptance.json、workflow/verification/final-report.md |
| 最终HAP大小及SHA | 当前HAP实物与历史hap-sha256.json；changes/verified-hap.json |
| 299项生产/配置指纹未变 | workflow/implementation/source-fingerprint-v2.json、audits/implementation-freeze.md |
| 主/子会话、模型ID、effort、CLI与token原始字段 | 按本题双维检索的Codex JSONL、traces/session-inventory.json |
| 工具清单和实际参数/返回 | traces/tools-used.json及原生轨迹 |
| 任务书版本和历史是否存在 | 四份公共/本题任务书SHA、spec/history实际存在性，traces/taskbook-version.json |
| 原始日志337个的完整复制 | logs/copy-manifest.json；保留全部失败/重试 |
| 二进制路径、大小、SHA和官方基线同源 | changes/binary-files.json、官方base对象与封存文件的逐字节摘要比对 |
| 完整封存版本、补丁可应用和逐文件一致 | traces/code-snapshot/manifest.json、changes/patch-validation.json |
| 指定官方准备报告/Comate库缺失 | 预期路径存在性检查、traces/discovery.json及审计报告 |

团队输入的空字段没有被这些客观事实替代；完整待补清单见 `NEEDS-INPUT.md`。
''')
    write('DELIVERY.md', f'''# vg-spec13 单题材料交付

本目录为2-submit单题材料暂存产物。业务代码、资源、工程配置未改。根团队solution/sources/README/system-config、成果ZIP及任何外部提交均未在本阶段生成。

## 阶段3复制约定与完整差异

必须把 `traces/code-snapshot/project/` 复制为成果包 `tasks/vg-spec13/project/`；其文件集合、每文件SHA和内容Git树以 `traces/code-snapshot/manifest.json` 为准，最终树 `{tree}`。把本目录的build/trace-index/fragments/changes/logs/repro-support等复制为project的同级任务材料。`traces/code-snapshot/project/`是完整封存工程，不是仅业务文件。

不要从仍活跃的工作区递归复制`.comate/submission-draft/`进入project：补丁和快照无法包含它们自己。此目录仅是工程外材料的staging，所有其它实际Git可见工程文件均纳入，含spec、inputs、hypium_tests、workflow、logs、相关traces、既有system-config及任意非staging的.comate文件。忽略的build/oh_modules/.hvigor/cache不属于源码交付。没有改源Git索引、HEAD或历史。

已存在的六份初始化跨题总览会话原文被排除，没有读取它们作为本题开发证据；既有manifest引用保留作原始历史文件说明，不假称原件都随包。所有选择/脱敏与原件/封存SHA见snapshot清单。账号标识脱敏不遮蔽代码与来源；本题已登记专用会话保留完整记录格式、失败重试及派生Markdown。

`changes/final.diff`为官方base到该封存工程树的完整--binary差异。校验使用本题仓库的两份临时单分支clone，各checkout到官方base；先 `git apply --check --binary`，再实际apply，与完整封存工程比较文件集合及每文件SHA。结果、补丁大小/SHA、比较数见 `changes/patch-validation.json`，不是只检查六个业务文件。临时clone完成后清理，不提交.git目录。二进制清单另列官方同源与新增本地截图证据。

## 剩余事项

输入空字段统一【待补充】，见 `NEEDS-INPUT.md`；自动填充事实及来源见 `AUTO-FACTS.md`。本阶段17项本地通过的准确范围及限制见solution片段，不能声称官方通过。历史构建、自测、安装与失败日志均已复制，不为材料补录而重新测试。官方基线准备报告缺失不通过重跑替换历史原件；本题已有本地准备日志保留。活动会话尾部只能在阶段3真正停止后再导出，当前有限快照的截止时间明示，不冒充全时段最终归档。

打包器还应将 `submission.json.fragment` 合并到官方全题清单；本片段的submitted是本题拟纳入评分工程的候选条目，团队最终submitted_tasks仍由阶段3确认，所有相对路径均为包内路径。本阶段未生成完整团队清单。
''')
    dump('input-values.json', {'team_nonempty': {k: team.get(k, PENDING) for k in ('team_id', 'team_name', 'stage')}, 'task_id': local.get('task_id'),
         'missing_user_fields': ['team.version', 'team.contact', 'team.freeze_time', 'team.members[].name', 'team.members[].work', 'team.source_guard', 'task.human_edits', 'task.known_issues', 'task.extra_sources', 'task.md_export_dir']})
    print('Documents written from local evidence.')


if __name__ == '__main__':
    generate()
