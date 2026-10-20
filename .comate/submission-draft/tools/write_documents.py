"""Render factual task material from previously collected local evidence."""
import json
from pathlib import Path

DRAFT = Path(__file__).resolve().parents[1]
ROOT = DRAFT.parents[1]
PENDING = '【待补充】'


def write(name, text):
    (DRAFT / name).write_text(text.strip() + '\n', encoding='utf-8')


manifest = json.loads((DRAFT / 'traces/native-manifest.json').read_text(encoding='utf-8'))
version = json.loads((DRAFT / 'traces/task-books/version.json').read_text(encoding='utf-8'))
records = manifest['records']
session_table = '\n'.join(
    f'| `{r["native_id"]}` | `{r["payload_session_id"]}` | {r["role"]} | '
    f'[{r["agent_path"]}](../../traces/vg-spec7/markdown/{r["native_id"]}.md) |' for r in records)
book_table = '\n'.join(f'| `{r["name"]}` | `{r["used_local_sha256"]}` | {r["same_bytes"]} |' for r in version['files'])

write('build.md', r'''
# vg-spec7 构建与运行

以下命令均从本题 `project/` 根目录执行。源码、资源、根及 entry 的包清单／锁文件随工程交付。无需本机私有目录；本说明是可移植复现步骤，历史原始命令仍保留在日志中。本次材料阶段没有重新构建或运行应用。

## 环境与依赖

实测 DevEco Studio 6.1.0.860、SDK 编译工具 6.1.0.105（API 23）、Node 18.20.1、JBR OpenJDK 21.0.8。工程 targetSdkVersion 和 compatibleSdkVersion 均保持 `6.0.2(22)`，没有修改为 API 23。实测 PowerShell 7.6.5。依据自己的安装位置配置 `DEVECO_SDK_HOME`、`JAVA_HOME` 和 PATH，确保 DevEco 随附 `node`、`java`、`ohpm`、`hvigorw`、`hdc` 可调用；工程本身不附 hvigorw wrapper。

根及 entry 运行 dependencies 为空；开发依赖锁定 `@ohos/hypium 1.0.24`、`@ohos/hamock 1.0.0`，lockfileVersion=3。工具 CLI 的历史精确版本（ohpm、Hvigor、hdc）【待补充】，不能把 modelVersion 当 CLI 版本。

```powershell
ohpm install
hvigorw clean assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

`ohpm install` 是依据清单的复现步骤；历史安装日志只有成功输出，没有完整 argv／起止时间。独立 clean 构建实际退出 0；`project/traces/do-verification-build-v1/invocation.json` 保存起止时间与命令，build.log 保存完整输出。764 条基线诊断与 763 条当前诊断相比新增 0、减少 1，不是零告警。

## 产物、安装与启动

- 产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。
- 历史最终验证产物：9,101,851 字节，SHA-256 `604fe92b34c70df74cf6907a363ac4571721fb4078ed7107d854baaab42b6e0d`。构建输出不随源码工程拷贝；新构建不承诺安装包字节恒定。
- bundleName：`io.qzz.weiyu`；entry 模块；入口 `EntryAbility`，源文件 `entry/src/main/ets/entryability/EntryAbility.ets`；版本 1.0.0（1000000）。
- `signingConfigs=[]`；上述 unsigned HAP 已在实际模拟器安装、启动。真机签名和真机安装未验证，相关配置【待补充】。

```powershell
hdc list targets
$deviceId = Read-Host '输入列表中的目标设备标识'
$hapPath = (Resolve-Path -LiteralPath './entry/build/default/outputs/default/entry-default-unsigned.hap').Path
hdc -t $deviceId install -r $hapPath
hdc -t $deviceId shell aa start -a EntryAbility -b io.qzz.weiyu
```

Windows 安装使用 Resolve-Path 返回的原生路径，并同时检查退出码和 `install bundle successfully` 输出。历史 core-v1 曾因正斜杠路径解析失败却退出 0，整轮无效记录保留。实际设备 `127.0.0.1:5555`，安装与 bundle 元数据见同级 `logs/do-regression-v3/`。

## 必要初始化与本题行为

首页 → 设置 → WebDAV 配置；输入可访问的地址、账号、密码、同步密码并显式保存。验证确认门禁时关闭自动同步并等待旧任务排空。点击「从云端恢复」先出现本地「继续／取消」；尚未点击「继续」不应产生本次恢复网络流量。有效当前弹窗点击「继续」后才进入既有发现／下载／解密／统计预览，原第二次「确认恢复」仍保留。使用自己的受控 WebDAV 端点；日志中的账号与口令是测试夹具值，不是应用默认配置。

首次全新安装的引导未独立覆盖；不能把保留数据安装等同于全新安装验证。完整实际导入与非空覆盖未测，继续前门禁的本地证据不代表这些分支通过。

## 可移植自测命令

工程保留 `test-harness/` 与 `hypium_tests/`；Python 侧 `hypium==6.1.0.210` 与 ohpm 的同名开发依赖是不同工具。以可访问应用沙箱的模拟器、竖屏及受控端点运行。以下是利用随包框架的复现命令；历史日志中的绝对路径运行脚本只作记录，无需执行。

```powershell
python -m venv .testenv
& ./.testenv/Scripts/python.exe -m pip install -r ./test-harness/requirements.txt
$projectRoot = (Get-Location).Path
$testPython = Join-Path $projectRoot '.testenv/Scripts/python.exe'
$env:PYTHONPATH = Join-Path $projectRoot 'test-harness'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:VG7_EVIDENCE_DIR = Join-Path $projectRoot 'traces/reproduction'
$env:VG7_CASES = ''
$env:VG7_DATABASE_DIR = Read-Host '输入本次设备上本应用实际可访问的数据库目录，用于 D0 只读对比'
New-Item -ItemType Directory -Path ./logs -Force | Out-Null
Push-Location ./logs
try {
  & $testPython -m harness.runner --project $projectRoot --device $deviceId --json ./reproduction-selftest.json
} finally {
  Pop-Location
}
```

按执行顺序同轮运行时 T02 生成 T06 的单次发现链参考。单跑 T06 须通过 `VG7_SINGLE_FLOW_REFERENCE` 指向对应单次链 JSON。未提供可访问数据库目录时，测试会记录 D0 阻断，不能把这当作 D0 已验证。测试会经既有「立即备份」生成夹具并隔离其流量，因此只在允许测试数据操作的环境运行。

历史接受结果是 core-v2 的 T01/T02/T03/T05/T07 加 regression-v3 的 T04/T06/T08/T09，共 9 项最终有效通过；core-v2 原始退出 1、regression-v3 退出 0。没有一次历史执行全部 9 项成功的记录。参见 `project/workflow/verification/do-result-v1.json`。本材料阶段未执行上述复现命令，未取得新的功能测试结论。
''')

write('trace-index.md', f'''
# 运行记录索引

本文按官方 `templates/trace-index.md` 逐字段整理。任务内路径以 `tasks/vg-spec7/` 为基准；`project/` 指本题工程。会话材料最终位于包根 `traces/vg-spec7/`，本草稿中实际保存在 `traces/`。材料派工与导出产生于 2-submit，不能替代此前研发原始证据。

- 题目 ID：`vg-spec7`。
- AI 在本题实际参与的研发环节、用途及对应原始会话／事件范围：0-analyze 的需求拆解、基线结构／构建／设备观察；1-do 的需求复审、方案、两份 ArkTS 源码实现、独立 clean 构建及 Hypium 测试与失败修复；2-submit 的材料整理与校验。下表列原始会话；`project/workflow/events.jsonl` 和各角色产物关联交接。
- 基线构建准备：脚本配置 profile=`harmony-cup-build-v1`、dry_run=false、changes=[]，见同级 `logs/prepare-baseline.log`。`project/workflow/setup-result.json` 的 prepared_at=`2026-10-17T02:23:18.655110+00:00` 是准备登记时间。指定官方 `reports/build-baselines/vg-spec7.log` 缺失；官方准备脚本内容版本及独立精确执行时间 {PENDING}。不能把本地保留输出说成缺失原件。
- Agent 名称及版本：Codex Desktop；原生 cli_version=`0.162.0-alpha.17.2`；四角色 `harmony_requirements`、`harmony_design`、`harmony_implementation`、`harmony_verification`，以配置 SHA 标识，无独立语义版本。当前材料环境客户端包版本见 `traces/client-environment.json`，不倒推历史客户端版本。
- 模型名称、版本及运行参数：各已导出会话 turn_context 均记录 `gpt-6.1-sol`、effort=`xhigh`。每会话模型、最后一次原生 token_count 的累计值见 `traces/native-manifest.json`；未相加为团队费用／总用量，缓存、继承及活跃快照口径保持原样。模型底层构建版本、Comate payload.model／payload.agent／agentInfo／appliedRuleNames 不存在，{PENDING}（运行器不同）。
- 本题实际使用的 Skill、系统提示、工具及编排配置版本和保存位置：`project/AGENTS.md`；`project/system-config/initial-20261017T022145Z/`、`analysis-20261017/`、`do-20261017/`。实际 Skill 为 harmony-task-flow、hmos-arkts-knowledge-retriever、hmos-arkts-syntax-checker（分析仅构建）；原生 session_meta.base_instructions 及 response_item 保存生效指令、提示、工具参数和返回；工具次数索引见 native-manifest。不是把可用工具列表全部视为已调用。
- 运行期间配置变更及原因：保留初始化、分析、开发三个快照及各自 manifest，快照时间代表保存时间，不自动代表配置改动时间；开发 manifest 的 10 项及分析 3 项重算一致。工程 app/module、依赖、构建配置未随本轮功能修改；阶段任务书由 0-analyze 切到 1-do、2-submit。是否存在未留存的人工／运行器配置调整 {PENDING}，不能填“无”。
- 主会话 ID：分析 `01a147ac-5335-7db2-9deb-49a293cb1024`；开发 `01a147d9-320a-7c82-9055-dfebef374231`；材料 `01a14823-79c4-78f3-b80d-737ef7fb7799`。
- 关联会话及子会话 ID：见下表。Comate 引擎 sessionUuid 与 IDE 侧边栏 ID {PENDING}（本机无 Comate store，不能虚构对应）。Codex 的 `payload.id` 是每个原生记录的独立 ID；子记录 `payload.session_id` 和 source.subagent.thread_spawn.parent_thread_id 指向所属主会话，不能把子记录 session_id 当独立子 ID。过滤后的 Codex sidebar 索引原行位于 `traces/session-index.filtered.jsonl`，主会话原生 ID 与其索引 ID 相同；不称其为 Comate ID。
- 解题过程中产生的全部相关原始日志、DB 或原生轨迹文件路径及读取方式：`traces/native/*.jsonl`（逐行 JSON）、`traces/native-manifest.json`（SHA、来源、截点）、`traces/markdown/*.md`（从 JSONL 机械生成的阅读副本）。`project/traces/` 保留设备 UI、HTTP/TCP 账本、截图、业务数据库只读拷贝和各阶段旧快照；`logs/` 原样复制本题全部 33 份日志。没有打包整个客户端数据库。
- 失败、重试、未采用的候选方案及选择过程的记录位置：`project/workflow/state.json` failures、events；`logs/do-core-v1/INVALID.json`、core-v2 两个失败与 regression-v3 重测；`project/workflow/requirements/do-test-review-v2.md`；ArkTS 索引缺失、文档抓取超时、安装路径及端口清理误报均留在原生及本题日志。材料收集首轮遇 token_count.info=null 的解析失败及修复保留于本材料主会话原生记录和 `validation/material-attempts.md`。
- 实际提示、工具调用及返回结果、检索与代码修改、构建和自测记录位置：上述原生 JSONL response_item、tool result；`project/workflow/{{requirements,design,implementation,verification,acceptance}}/`；`project/traces/do-verification-build-v1/`；`logs/`；`traces/code-snapshots/` 与 `changes/final.diff`。PromptAction 文档失败不算成功 API 证据。
- 导出时间、方法与读取方式：最新 UTC 截点见 `traces/native-manifest.json.exported_at_utc`；原生 session_meta 按工程绝对路径和任务 ID 侧边栏索引分别筛选，并与登记 UUID 交叉核对，仅复制本题。Markdown 是整理期生成，IDE“导出本地”原件目录为空（{PENDING}）。活跃材料主会话只到拷贝截点，不含之后校验／最终回复；后续阶段需再次导出，不把新记录冒充旧研发记录。
- 成果冻结时间（北京时间，与 solution.md 一致）：{PENDING}，team.yaml 留空；原始 1-do production_frozen 只是生产源码冻结状态，不推断为团队正式成果冻结时间。
- 官方工程基线标识（本次题包 metadata.base_commit 发布提交号）、最终提交版本标识：基线 `9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`。HEAD 仍为该基线，最终工作树有未提交变更；提交树及全文件摘要由 `changes/project-snapshot.json` 标识。不是新造 Git 提交或团队版本。
- 基线至提交版本的完整差异位置：`changes/final.diff`，`--binary --full-index`，包含全部工程投影新增、修改、删除；二进制大小／SHA／基线同源标识见 `changes/binary-files.{{json,md}}`。
- 与提交源码的对应关系：`changes/project-snapshot.json` 明确最终 project 文件集合，`validation/diff-validation.json` 保存本题基线 clone、checkout、apply --check --binary、实际 apply、全量逐文件 SHA 比对结果。包括 spec、inputs、hypium_tests、logs、traces、workflow、system-config 和稳定 .comate 材料；只排除构建缓存、本机配置、明确跨题初始化总览原文，以及无法自包含的补丁／校验衍生文件。下一阶段须据该集合复制 project，见 README.md。为了与原始 Windows 工作树逐字节一致，diff 也记录基线文本的既有 CRLF／LF 差异；这不是新增业务修改。
- 人工操作及相关记录位置：人工给出的任务与阶段提示在主会话 user 消息；人工身份、其他操作及修改声明由 submit-input.yaml／team.yaml 提供，当前留空 {PENDING}。
- 人工修改索引位置：{PENDING}，human_edits 留空，不能写“无人工直接修改代码”；如确认发生，后续补 human-changes.md 及当时真实证据，不能补造历史。
- 人工修改的操作人、目的、文件、代码差异、修改前后版本及对应原始记录位置：{PENDING}。
- 公开资料检索与代码复用记录位置，以及 sources.md 中的对应来源条目：本题 `sources.fragment.md`；原生工具序列；`project/workflow/design/do-design-v1.md` 第 9 节、implementation/do-v1.md；额外人工来源声明 extra_sources 为空，{PENDING}。不等于“无额外来源”。
- 本题工作目录，以及赛题来源保护措施在本题运行中的配置位置：本题工程根（实际路径在原生 cwd 和 workflow/state.json）；实际单题边界见 project/AGENTS.md、四角色派工、保存的 Skill。team.yaml.source_guard 为空 {PENDING}，材料只记已观察到的约束，不替团队做完整合规声明。
- 脱敏范围：初始化总览会话已知含跨题内容，原文不读取、不复制进 project 投影；原有该快照 manifest 保留并注明排除。材料主会话一次终端输出中的 5 条无关侧边栏索引行从导出副本替换为明确 REDACTED，原文件不改；原／导出 SHA 与次数见 native-manifest。其余本题原生不改字节，历史路径、账户元数据和虚拟夹具值仍保留；未声称完成全量凭据审计。未提交账号密钥／签名私钥文件，匹配的私钥后缀被排除。后续对外打包仍须按清单核对。
- 记录缺失及原因：Comate 数据库／双 ID／IDE Markdown 原件不适用或缺失；指定官方基线报告不存在；部分工具历史版本／安装 argv 缺失；初始化总览原文因跨题隔离排除；材料活跃主会话尾部晚于导出截点。已登记的本题分析／开发原生会话均找到，不能将这些限制写成“无缺失”。

## 原生记录映射

| Codex payload.id | payload.session_id（主／所属主 ID） | 角色 | 阅读副本 |
| --- | --- | --- | --- |
{session_table}

## 任务书版本

common 目录属于父仓库（不是独立仓库），只对获准 common 路径查询 Git 元数据：HEAD `{version['common_git_head']}`；common/spec-harness 状态干净。当前本题实际四份任务书与 common 副本逐字节相同，哈希如下；这验证当前文件，不虚构过去未保存的版本。原样副本与核验结果在 `traces/task-books/`。本题 `spec/history/` 不存在。

| 文件 | 本题实际副本 SHA-256 | 与当前 common 相同 |
| --- | --- | --- |
{book_table}
''')

write('sources.fragment.md', '''
# vg-spec7 来源片段

本题随包基线：metadata.base_commit=`9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`，baseline_bundle=`repo_bundles/vignette-9cbcf7292c-base.bundle`。名称来自本题 spec/metadata.json；本阶段没有访问题包 repo_bundles 或上游。基线准备记录为 project/workflow/baseline-provenance.json 和 logs/prepare-baseline.log；官方指定 build-baselines 报告缺失，不能替代为已取得原件。基线自带图标、图片、其他素材按实际 blob 同源记录在 changes/binary-files.json，未作为本轮新增外部素材申报。

生产实现依据本题 requirement.md、批准需求和本题基线源码。除一处修改、一份新增的 settings ArkTS 文件外，保持既有服务、路由、资源和配置；不把基线项目描述为完全自研。原有许可、声明与开发文档随完整工程保留。

可核实的通用参考／工具来源（整理自当时原生轨迹及角色登记，本阶段没有重新查询上游资料）：

- 官方 ohpm 锁定开发依赖：@ohos/hypium 1.0.24、@ohos/hamock 1.0.0，解析地址与 integrity 在 project/oh-package-lock.json5；本题没有新增运行依赖。
- 本地 hmos-arkts-knowledge-retriever 携带的 ArkTS classes、Concurrency/async-concurrency-overview 和 linter 摘要；search_docs.py 因缺 references/doc_index.json 失败后直接读取文档，失败保留在 logs/do-implementation/retrieval-index-failure.log、project/traces/do-verification-build-v1/arkts-reference-search.log。已保存 Skill 与部分文档在 project/system-config；完整当时读出内容可在原生工具输出定位，不能声称所有参考文档已独立归档。
- 本地 SDK 声明 @ohos.arkui.UIContext.d.ts、@ohos.promptAction.d.ts，用于实例 PromptAction 与按钮索引类型；依据 project/workflow/design/do-design-v1.md 第 9 节及 implementation/do-v1.md 的当时读取登记。
- 华为通用文档：[全局接口多实例适配](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides-V13/arkts-global-interface-V13) 检索结果；[PromptAction API](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/arkts-apis-uicontext-promptaction) 正文抓取超时；[promptAction 模块](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/js-apis-promptaction) 未取得可读正文。后两条是失败访问记录，不能用作已读技术结论。
- 公共 test-harness 与 Python Hypium 6.1.0.210；本题工程已有框架副本与 requirements，历史运行通过 common 环境调用；来源版本见随工程文件及原始调用。不把测试框架说成本题新写业务代码。
- 实际使用的 harmony-task-flow 与四角色、ArkTS 检索／语法检查 Skill 见 project/system-config/ 三个阶段快照。任务书实际副本、SHA 和 common 父仓库版本见 trace-index.md 与 traces/task-books/version.json。

用户 extra_sources 留空：【待补充】。上列是已核实记录，不是团队“无其他来源”的声明；人工额外使用情况、基线素材许可补充及团队来源保护声明由用户确认。没有为填材料访问来源项目相关修复提交、PR、Issue、补丁或其副本。材料期过滤无关侧边栏索引及跨题初始化总览的范围详见 trace-index.md，不作有利推定。
''')

write('solution.fragment.md', '''
# vg-spec7 完成情况与 AI 协作片段

团队已提供：HC2026-111 / Ghost_London，阶段 online。团队版本、联系人、成员及分工、正式成果冻结时间、source_guard 均【待补充】。本片段用于 3-package 汇总；本阶段没有创建团队级 solution.md、sources.md、README.md、system-config 或 ZIP。

实现：WebDAV 配置页「从云端恢复」先出现纯本地继续／取消确认，有效当前弹窗的精确继续才授权既有恢复链；pending、busy 和轮次保护抑制重入／失效回调。保留下载、解密、统计预览及第二次「确认恢复」。生产范围为修改 SettingsSyncSection.ets 与新增 SettingsSyncCards.ets；当前 SHA 与 1-do 验收一致。源码及 config 没有在 2-submit 改动。

本地验证：独立 clean 构建退出 0；基线 764 条诊断、当前 763 条，新增 0。最终有效 9 项由 core-v2 接受的 5 项与 regression-v3 重新运行／新增的 4 项组成，0 最终失败、0 最终跳过；不是一次全跑通过。29 个最终有效继续前窗口为 0 新 TCP／0 任意 HTTP；下载、解密、预览和取消使用真实应用生成密文，D0 业务表计数／逻辑哈希一致，样本词数为 0。它们不等于官方 F-point 结果或得分。

未完成／未验证：R7.actual_import 完整导入及非空数据覆盖、独立自动同步并发 U07、真实 HTTPS／真机、全新安装引导、未保存 E2、401/403／断网／超时／错误密钥等额外错误分支、已授权在途返回／重启，以及超过既有观测时间的等待。既有 Promise.race 不会取消已授权底层请求。用户 known_issues 留空【待补充】，不能把上述客观范围替换为用户已确认的完整问题声明。

AI 参与：分析、需求复审、方案、ArkTS 实现、测试设计和设备实测、失败诊断、材料整理；各阶段主会话和四角色独立记录见 trace-index.md。失败与重试保留，包括无效安装轮、两项测试假设修正、端口清理误报、ArkTS 索引缺失和公开 API 抓取失败。需求复审后只修正测试假设，没有放宽门禁断言。token 用量保留原生逐会话口径，不估算人工／AI 贡献百分比。

人工修改与操作：human_edits 为空【待补充】，不能声明“无人工直接修改代码”。人工身份、目的、文件及当时证据待用户提供。md_export_dir 留空，现有 Markdown 是材料期从 JSONL 机械生成阅读副本，并非 IDE 原生导出。

最终交付版本由 changes/project-snapshot.json 的 Git tree、全文件 SHA 清单和 diff SHA 标识；工作树有未提交修改、HEAD 仍为官方基线。团队正式版本与冻结时间待用户填，不从文件时间推测。可应用性与全文件对比结果见 validation/diff-validation.json，二进制资源同源性见 changes/binary-files.json。按 README.md 所述工程投影复制，保留稳定 .comate 过程材料，精确排除无法自包含的衍生输出及跨题初始化原文。

材料已准备为单题草稿，仍有明确待补字段与记录缺口；不等于可立即正式提交。官方隐藏测试不可见，本地通过不能声明官方评分通过。
''')

write('submission.json.fragment', json.dumps({
    'task_id':'vg-spec7','status':'submitted',
    'project_path':'tasks/vg-spec7/project',
    'build_instructions':'tasks/vg-spec7/build.md',
    'trace_index':'tasks/vg-spec7/trace-index.md'}, ensure_ascii=False, indent=2))

write('README.md', '''
# vg-spec7 单题材料交接

本目录是 2-submit 的本地草稿，未打 ZIP、未上传或发送。submission.json.fragment 是供 3-package 选入时的候选 submitted 条目，不代表团队已决定正式提交；三个路径均为成果包内相对路径，后两项指文件。团队 submitted_tasks 尚空，不能在本阶段擅自决定全阶段题目清单。

build.md、trace-index.md、两份 fragment、changes/final.diff、logs/ 和 traces/ 已按本题事实整理。完整检查结果看 validation/diff-validation.json 与 validation/independent-review.md；人工字段与记录缺口在下面两份清单。

## 3-package 复制接口

1. 将 build.md、trace-index.md、changes/、logs/ 放到 `tasks/vg-spec7/`；把本目录 traces/ 放到包根 `traces/vg-spec7/`，fragment 供团队文件汇总。validation 交付说明可放到任务材料 validation/；它不属于被补丁重建的 project。
2. `changes/project-snapshot.json.files` 是 project 的完整文件集合。按清单逐文件保留相对路径复制并核对 SHA-256，包含源码、资源、依赖锁文件、spec、inputs、hypium_tests、test-harness、workflow、原始日志和轨迹，以及 `.comate/submission-draft/` 的稳定材料。禁止简单递归复制工程根或一律排除 `.comate/`。
3. 精确排除 `.comate/submission-draft/changes/final.diff`、同目录 project-snapshot.json、binary-files.json/md、`.comate/submission-draft/validation/` 和 `.comate/submission-draft/.scratch/`。这些是补丁和它的证明／衍生输出，任务材料外层仍保留；把它们再放进 project 会产生自引用并破坏一一对应。其他 .comate 稳定文件均在补丁覆盖内。
4. 按脚本排除构建／依赖／缓存、local.properties、私钥后缀和明确跨题的初始化总览原文；原有快照 manifest 留在工程内，其缺少对应原文的理由在索引披露。不要删除原工作区历史文件来伪造完整性。`.scratch/` 是本题基线校验 clone 和独立 Git index，留本地，不进成果包。
5. 最后在干净本题 clone 的 `.git/info/attributes` 写入 `* -text -filter -working-tree-encoding`（仅该临时 clone），随后以 `git -c core.autocrlf=false -c core.eol=lf checkout --detach <base_commit>` 检出，再用相同 `-c` 参数执行 `apply --check --binary final.diff` 和实际 apply，按清单逐文件 SHA 比较。可直接从原工程根运行本目录 `tools/prepare_materials.py verify` 复现。校验 clone 只来自本题本地 Git，未访问上游仓库／题包受限目录。全局 core.autocrlf=true、基线 `* text=auto`，仅关闭 autocrlf 仍可能发生属性触发的换行转换；首轮失败原件保存在 validation/diff-validation-attempt1.json。本补丁为保留工作树原始字节也覆盖既有 CRLF 差异，不得通过 Git clean filter 静默改写 project。
6. 若用户补字段、变动 project 文件或刷新材料原生快照，必须重新生成补丁与清单并验证；不能沿用旧 SHA。本阶段不承担第 3 阶段的跨题汇总、正式冻结或上传。

## 仍需用户补充的字段

| 来源 | 留空字段／待确认内容 |
| --- | --- |
| common/spec-harness/team.yaml | version、contact、freeze_time（北京时间到分）、members.name/work、source_guard |
| spec/submit-input.yaml | human_edits、known_issues、extra_sources、md_export_dir（如有 IDE 原始 Markdown 导出；当前仅有 JSONL 阅读副本） |
| 如确有人工改码 | 操作人、目的、文件、前后版本及当时真实证据；目前不生成空的 human-changes.md |
| 第 3 阶段另填 | submitted_tasks、attempted_not_submitted、zip_out；本阶段不推测 |

Comate sessionUuid／侧边栏 ID、模型内部构建版、Comate agentInfo/appliedRuleNames、官方基线报告原件与官方脚本内容版本／独立执行时间、历史 ohpm 完整 argv／时间以及部分工具 CLI 版本均无法从已有证据核实，标【待补充】或说明运行器不适用。这里不会要求为填空重新造历史。正式提交前应决定记录缺口如何说明，而不是默认记录完整。

## 已自动填入的事实及出处

| 事实 | 出处 |
| --- | --- |
| 题号 vg-spec7、官方基线 9cbcf7292c8cc46955dc3b522ddbda41c66a61d9、随包 bundle 名称 | spec/metadata.json、workflow/baseline-provenance.json |
| 团队 HC2026-111、Ghost_London、online | 只读 common/spec-harness/team.yaml；本次输入副本及SHA保存在 traces/input-records/ |
| io.qzz.weiyu、entry/EntryAbility、1.0.0、SDK 声明22、无签名配置 | AppScope/app.json5、entry/src/main/module.json5、build-profile.json5 |
| Hypium 1.0.24、Hamock 1.0.0、锁版本3、无运行依赖 | 根／entry oh-package.json5、oh-package-lock.json5 |
| 实际 clean 命令、退出0、环境、9,101,851字节最终HAP及SHA | project/traces/do-verification-build-v1/、logs/do-regression-v3/install.json |
| 9项两轮汇总、29个有效门禁窗口、失败／未测范围 | workflow/verification/do-result-v1.json、workflow/acceptance/do-acceptance-v1.md、core-v1/v2及regression-v3日志 |
| 原生ID映射、模型gpt-6.1-sol、xhigh、CLI版本、逐会话原生token值、工具列表 | traces/native/*.jsonl、native-manifest.json、过滤后的session-index原行 |
| 当前客户端包版本与当前Python版本（不能倒推历史） | traces/client-environment.json |
| 任务书四份SHA及与common相同、common父仓库HEAD、无spec/history | traces/task-books/version.json；原样任务书副本 |
| 改动范围、基线同源二进制、工作树快照、补丁可应用性和全文件一致性 | changes/ 下清单、tools/prepare_materials.py、validation/diff-validation.json |
| 实际配置快照、来源及公开资料失败 | project/system-config/、workflow/design/do-design-v1.md、implementation/do-v1.md；sources.fragment.md |

记录披露：已登记的本题分析与开发原生均可定位；初始化总览因含跨题内容排除，材料主会话导出只到明示截点，Comate 格式／官方基线报告等缺口保留。材料主会话副本仅脱敏 5 条无关侧边栏索引行，原始文件未修改；原始和导出 SHA 分别登记。没有通过整理期文档替代原始研发证据。
''')

print('Wrote 7 task documents; no production/configuration writes.')
