"""Write only the assigned cml-spec7 submission documentation from local evidence.

Run after export_evidence.py, and rerun after its final refresh. This script does not
build, operate a device, modify evidence JSON, or change production/test sources.
"""
from pathlib import Path
import hashlib
import json
import os
import re

OUT = Path(__file__).resolve().parents[1]
ROOT = OUT.parents[1]
PENDING = "【待补充】"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(name, value):
    (OUT / name).write_text(value.strip() + "\n", encoding="utf-8")


def cell(value):
    return str(value if value is not None else PENDING).replace("|", "\\|").replace("\n", " ")


def table(headers, rows):
    return "\n".join(["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"] +
                     ["| " + " | ".join(cell(x) for x in row) + " |" for row in rows])


def main():
    facts = read_json(OUT / "facts.json")
    versions = read_json(OUT / "taskbook-versions.json")
    meta = read_json(OUT / "traces/session-metadata.json")
    logs = read_json(OUT / "logs-copy-manifest.json")
    setup = read_json(ROOT / "workflow/setup-result.json")
    hap = facts["hap"]
    validation = facts["validation"]
    base = facts["base_commit"]
    patch = read_json(OUT / "patch-validation.json") if (OUT / "patch-validation.json").is_file() else None
    patch_state = ("已通过；完整命令、退出码、逐文件比较与当前摘要见 `patch-validation.json`（`passed=true`）"
                   if patch and patch.get("passed") else "【待补充：主调度尚须完成独立基线应用与逐文件比较；未声明通过】")
    try:
        app_version = json.loads(facts["app_package"]["stdout"])["Version"]
    except (ValueError, KeyError):
        app_version = PENDING
    locks = [ROOT / "oh-package-lock.json5", ROOT / "entry/oh-package-lock.json5"]
    locks += sorted((ROOT / "core").glob("*/oh-package-lock.json5"))
    locks += sorted((ROOT / "feature").glob("*/oh-package-lock.json5"))
    deps = {}
    for lock in locks:
        for package in read_json(lock).get("packages", {}).values():
            if package.get("registryType") == "ohpm":
                deps.setdefault((package["name"], package["version"]), []).append(lock.relative_to(ROOT).as_posix())
    deps_table = table(["已锁定外部依赖", "版本", "锁文件（工程相对路径）"],
                       [(name, version, "、".join(f"`{p}`" for p in paths)) for (name, version), paths in sorted(deps.items())])

    write("build.md", r"""
# cml-spec7 构建与运行草案

本题当前为本地部分完成：41项明文验收中38项通过，B9/B10/B11真实微信、QQ、支付宝授权流程受外部条件阻断。不可用提示与恢复不计三项通过。构建、安装、冷启动及已实现范围适用回归已通过；本地计数不等于官方 F-point 或成绩。本阶段整理现有证据，未重跑构建或设备测试，未正式打包提交。

以下命令均从成果包 `tasks/cml-spec7/project/` 执行。工具链须由使用者安装并配置到 PATH，不能依赖参赛机环境脚本；工程内已有 `test-harness/`，无需另一个公共目录。构建目标、依赖和原始日志见工程内的配置及本文引用。

## 环境与依赖

- 工程 `build-profile.json5`：HarmonyOS，target/compatible SDK 均为 `6.0.1(21)`；产品 `default`，模块 `entry`，构建模式 `debug`。实际历史运行使用 API 23 SDK/模拟器，见原始 `logs/verification-navigation-smoke-03/environment.json` 和 `logs/analysis-baseline/env-check-final.json`。
- 历史工具实测：Node.js `18.20.1`、Python `3.12.3`、Hvigor `6.23.7`、hdc `3.2.0c`、Python Hypium `6.1.0.210`，依据 `logs/analysis-baseline/tool-versions.txt`。工程 modelVersion 为 `6.0.1`；modelVersion 不是 Hvigor 运行时版本。
- 本机需准备兼容的 DevEco Studio/HarmonyOS SDK、JDK、Node.js、OHPM，并保证 `hvigorw`、`ohpm`、`hdc` 可从 PATH 调用。签名配置为空，产物为 unsigned HAP；历史可调试模拟器安装成功不证明任意真实设备可接受未签名包。真实设备需使用合法本地签名配置，私钥不随成果包提交。
- 依赖版本以根及模块 `oh-package-lock.json5` 为准。本题没有新增三方登录 SDK 依赖；研究下载的 HAR 不代表已集成。Python 测试依赖由 `test-harness/requirements.txt` 锁定为 `hypium==6.1.0.210`。

__DEPS__

在工程根执行（PowerShell）：

```powershell
ohpm install
hvigorw --mode module -p product=default -p module=entry@default -p buildMode=debug clean assembleHap --no-daemon --no-incremental
```

保留锁文件；不要用升级依赖代替安装。原始准备安装结果见 `logs/ohpm-install.log`，最终独立全量构建及退出码见 `logs/verification-navigation-smoke-03/build.json`、`build.stdout.txt`、`build.stderr.txt`。这些是历史执行记录，上述便携命令未在本材料阶段重新执行。

## 安装、启动与人工入口

应用标识来自 `AppScope/app.json5`：`com.joker.coolmall`；entry 模块 `mainElement` 与 Ability 名均为 `EntryAbility`。产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。

```powershell
hdc list targets
$taskDevice = Read-Host '输入 hdc 列出的目标设备序列号'
hdc -t $taskDevice install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t $taskDevice shell aa start -b com.joker.coolmall -a EntryAbility
```

先确认安装输出成功，再启动。首次启动按实际系统提示处理权限；正常进入“我的”，点击未登录入口/头像进入登录页。手机号登录、账号密码登录分别进入既有目标页；两份本地协议可离线查看并滚动至末尾。目标页导航不代表短信发送、密码认证或第三方登录已验证成功。没有为本页新增初始化账号、数据库导入、网络服务或硬编码凭据。

最终历史 HAP 的 bytes/SHA-256 见同级 `facts.json` 的 `hap` 和 `project/workflow/verification/root-delivery-check-03.json`；源码指纹与HAP对应见原始 `install-manifest.json`。HAP 是构建产物，不替代完整源码；当前工程快照的缓存排除以同级 `project-exclusions.json` 为准，解包后需要重新构建。

## 使用随包框架复现本地检查

原 `workflow/verification/run-verified-round.ps1` 写死了参赛机驱动器、工程目录、公共虚拟环境及 PYTHONPATH，保留它是为了原始证据；换机器时使用下面的相对路径入口。`cml_evidence.py` 从自身位置推导工程根，`fingerprint` 的 `--out` 必须是工程内的**JSON文件路径**。`run_verified_round.py` 从同一工程根定位源码和HAP，调用 PATH 中的 Hvigor/hdc，归档源码/测试首尾哈希、重新安装HAP及命令原始输出；其 `--round` 必须是全新的简单目录名。

```powershell
python -m venv .submission-venv
& ./.submission-venv/Scripts/python.exe -m pip install -r test-harness/requirements.txt
$taskProject = (Get-Location).Path
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPATH = (Join-Path $taskProject 'test-harness') + [IO.Path]::PathSeparator + $taskProject
$env:HDC_DEVICE = $taskDevice
& ./.submission-venv/Scripts/python.exe workflow/verification/cml_evidence.py fingerprint --out logs/reproduce-source.json
$taskSource = Get-Content -LiteralPath logs/reproduce-source.json -Raw | ConvertFrom-Json
$taskRound = 'reproduce-smoke-' + (Get-Date -Format 'yyyyMMddHHmmss')
& ./.submission-venv/Scripts/python.exe workflow/verification/run_verified_round.py --round $taskRound --expected-source-sha256 $taskSource.sha256 --device $taskDevice --mode suite --suite-kind smoke
```

该入口默认真实重构建和安装，不使用含旧绝对路径的 `--built-manifest`。不要在该轮运行期间改源码或测试。若要跑手机完整用例，换一个新 `$taskRound` 并使用 `--suite-kind full`。视觉条目需要对**当前源码/HAP及当前设备截图**独立复核；未提供匹配的 `--visual-review` 会跳过相应条目，跳过不计通过，不应把旧轮视觉JSON当作新轮结果。大屏/平板、旋转和文档终点另有 `layout`、`large-geometry`、`rotation`、`documents` 分组；只有真实改变设备窗口后才有对应尺寸证据，目录名称不构成尺寸证据。

三方真实授权仍需合法平台应用身份、签名/回调登记和服务端凭据交换契约，详见 `workflow/implementation/third-party-setup.md`。当前缺少这些条件，B9–B11保持blocked。历史最终验收矩阵和限制见 `workflow/verification/final-verification-03.md`、`logs/verification-final-03.json`。本材料阶段未执行上述复现命令，不能把指南当新增通过证据。
""".replace("__DEPS__", deps_table))

    source_rows = [
        ("随包官方基线", f"`{base}`", "`spec/metadata.json`、`inputs/`、`workflow/baseline-provenance.json`；本题当前基线，不读取来源项目修复历史"),
        ("基线已有组件/资源", "Logo、主题、断点、路由、ViewModel、现有三方图标", "`workflow/implementation/implementation-handoff-01.md`、`workflow/design/implementation-plan-01.md`；三份专用 `ic_login_*.svg` 复制自本题 `core/ui` 基线资源，详见资源清单"),
        ("原创本地协议正文", "本地1.0 / 2026-10-20", "`feature/common/src/main/resources/base/element/string.json`；按用户授权由AI编写，需求角色复核，见 `workflow/implementation/implementation-handoff-01.md` 及原生会话；不是上游官方协议"),
        ("Harmony/ArkTS参考与工具", "实际读取版本和hash见配置快照", "`system-config/analysis-20261020T095248Z/manifest.json`、实际Skill副本和原生工具read记录；文件存在不单独证明使用"),
        ("公共本地测试框架", "Python hypium==6.1.0.210", "随包 `test-harness/`、`test-harness/requirements.txt`；本题 `hypium_tests/` 继承框架，非官方评测器"),
    ]
    write("sources.fragment.md", f"""
# cml-spec7 来源片段（供3-package汇总）

本片段仅报告本题已有可读证据，人工输入 `spec/submit-input.yaml.extra_sources` 仍为 **{PENDING}**；不代填“无额外来源”。团队来源保护声明 `source_guard` 仍为 **{PENDING}**。

{table(["来源类别", "事实", "证据与使用范围"], source_rows)}

## 三方通用SDK研究：读取成功、下载与失败分别记录

以下均为既有 `workflow/provider-research-01.md` 的研究事实；本材料阶段未重新联网核验，未把下载包写入生产依赖。

- QQ官方通用说明实际读取：[环境搭建](https://wiki.connect.qq.com/harmonyos_sdk%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA)、[接口说明](https://wiki.connect.qq.com/harmonyos_sdk%E6%8E%A5%E5%8F%A3%E8%AF%B4%E6%98%8E)、[应用注册说明](https://wiki.connect.qq.com/__trashed-2)。读取范围、authCode与旧后端契约差异见该研究记录。
- 官方OHPM元数据及发行包实际获取：[@tencent/wechat_open_sdk 1.0.23](https://ohpm.openharmony.cn/ohpm/@tencent/wechat_open_sdk/-/wechat_open_sdk-1.0.23.har)、[@tencent/qq-open-sdk 1.0.4](https://ohpm.openharmony.cn/ohpm/@tencent/qq-open-sdk/-/qq-open-sdk-1.0.4.har)。实际读取README/声明，下载物和命令输出在 `logs/provider-research-01/`，完整摘要见 `changes/binary-files.json`。
- 微信开发者接入页打开失败；支付宝开放文档超时，没有据此声称读到具体实现。`ohpm info`字段尝试失败、一次多字段失败、猜测名称`@alipay/apay`返回404均保留；404不表示平台不支持鸿蒙登录。准确失败URL及输出索引见研究记录和原生会话。

根/模块OHPM依赖的名称、精确版本、resolved URL与integrity，以各 `oh-package-lock.json5` 为准，摘要表见 `build.md`。本题没有添加真实三方授权SDK/凭据，B9–B11仍未完成。

## 来源、修改和素材追溯

总体差异为 `changes/final.diff`；二进制文件及每项bytes/SHA-256、基线同源判定在 `changes/binary-files.json`；资源另外列于 `changes/resource-files.json`，含新增的文本SVG。基线复制资源需结合原生工具调用确认原路径，不能因换名被当作外部素材。

当前适用访问边界由本题 `AGENTS.md`、角色提示和既有 `system-config/` 副本记录：本题inputs/工程/记录、只读公共资源与允许的官方模板/本题基线报告；禁止其他题工程和来源项目相关修复提交/PR/Issue/补丁及副本。初始化总览因混含其他题准备被排除，不作为本题功能研发证据。该配置和本片段不替代尚未提供的人工 `extra_sources` / `source_guard` 声明。
""")

    write("human-changes.md", f"""
# cml-spec7 人工操作与修改索引

`spec/submit-input.yaml.human_edits` 为空，人工直接改码声明为 **{PENDING}**。目前不能填写“无人工直接修改代码”，也不能由总体diff推算作者或代码占比。

用户已通过本题原生会话提供任务、约束及后续选择；这些人工提示保留在 `traces/native/*.jsonl` 的消息对象，机械可读副本为 `traces/markdown/*.md`，逐会话路径、哈希、事件截止与关联关系见 `traces/session-metadata.json`、`trace-index.md`。提示不自动等于人工直接编辑源码。

若存在人工直接改码，仍需补充每个实际操作批次：操作人、目的、文件、修改前后真实提交/快照/摘要、差异及当时留存的原始编辑历史或记录路径，均为 **{PENDING}**。不能在整理阶段制造当时不存在的过程证据。

AI修改、构建和修复的既有证据见 `workflow/implementation/`、`workflow/verification/` 及原生工具调用；`changes/final.diff` 仅证明总体交付差异，不单独证明人工操作。团队 `members[].name/work` 仍为 **{PENDING}**，不从设备用户名推断人员。
""")

    write("solution.fragment.md", f"""
# cml-spec7 完成情况与协作片段

本题为本地部分完成：41项明文原子验收中38项pass，B9/B10/B11真实微信、QQ、支付宝授权流程blocked。用户没有第三方开发者账号，缺少合法平台应用身份、签名/回调登记及确认的服务端换票条件；现有点击、缺配置反馈与恢复不计真实授权通过。构建、安装、冷启动和已实现范围适用回归通过；不是官方F-point/成绩，不宣称全部完成。

实现范围为正常“我的”入口到登录页、120vp基线Logo、两种登录目标页导航、三品牌图标和标签、两份独立协议链接及原创本地长正文、逐字页脚、100%/70%/60%自适应与入口去重。未新增SDK依赖或伪造认证结果。原始需求与blocked项继续有效。详见 `workflow/delivery-01.md`、`workflow/verification/final-verification-03.md` 和 `logs/verification-final-03.json`。

## AI实际参与及证据

AI参与需求拆解和复核、基线代码审计、方案与修订、14个生产文件实施和修复、独立构建/设备回归、失败诊断、材料整理与交付校验。主调度按需求/方案/编码/独立自测四角色派工；真实Agent角色、父子关系、模型/effort、工具调用及事件范围见 `trace-index.md` 和 `traces/session-metadata.json`。AI角色分工不等于人工成员分工；真实 `members[].name/work` 为 **{PENDING}**。

有效03轮保留完整原始结果：手机原轮39通过/8跳过/1测试错误，文档助手大小写修正后3/3通过；平板800vp补测、大屏真实1200vp四项和短横屏另有原始记录。曾标称large的旧轮实际800vp、旧导航/布局失败、02b并发改源失效、原始stdout缺口和清理拒绝均保留并标范围。合并验收仍为38pass/3blocked，不通过堆叠用例数扩大结论。

## 已观察问题与验证边界（自动取证）

除B9–B11外，未执行已登录个人资料分支、恰好600/840vp断点、拖拽调整和真实授权；没有抓包证明网络请求数量。短信/密码目标页仅验证导航，不宣称认证成功。初始化独立hdc stdout未被最初Transcript捕获；保留原生工具结果、明确标注转录和之后完整设备输出。临时模拟器磁盘清理被工具自动审批拒绝，未执行删除；原磁盘保留，生成缓存从提交清单排除。具体证据见 `workflow/delivery-01.md`、`logs/analysis-baseline/initial-device-observation-transcription.json`、`logs/verification-closeout-03/temporary-disk-cleanup-rejected.json`。

这些已知事实不代填人工 `known_issues`；该输入仍为 **{PENDING}**。人工修改、额外来源、IDE导出路径及团队人工声明亦待补，见 `missing-fields.md`、`human-changes.md`。

## 版本、来源保护与正式提交边界

官方基线为 `{base}`。完整生产输入聚合SHA-256为 `{validation['source_sha256']}`；它与14个变更文件的聚合范围不同。HAP SHA-256为 `{hap['sha256']}`，大小 `{hap['bytes']}` bytes，证据为 `facts.json` 及最终验证记录。完整交付文件树标识以 `project-manifest.json.final_version` 为准，不能用仍停留基线的Git HEAD代替。

当前材料草案拟映射到 `tasks/cml-spec7/`，工程必须精确取 `traces/code-snapshot/project/`，避免把包含自身补丁/快照的 `.comate/submission-draft/` 递归塞回project。其他真实过程文件按完整清单纳入；二进制、排除项及补丁校验见 `DELIVERY.md`。当前补丁状态：{patch_state}。

`submission.json.fragment` 仅一个本题对象；`team.yaml.submitted_tasks=[]` 尚未选择本题，因此保守为 `not_completed`。三个非空路径是拟供3-package采用的真实材料位置，非“全部功能通过”或“已正式提交”的声明；最终是否标submitted由3-package依据真实选择决定。

团队正式版本 `version`、联系人 `contact`、成果冻结北京时间 `freeze_time`、成员姓名/分工及 `source_guard` 均为 **{PENDING}**。材料导出/快照时间不能代替正式冻结时间。本阶段不生成团队根solution/sources/README、system-config或ZIP。实际保护配置见本题 `AGENTS.md` 与已有 `system-config/`，原生记录索引见 `trace-index.md`；人工来源保护声明仍待提供。
""")

    write("submission.json.fragment", json.dumps({"task_id": "cml-spec7", "status": "not_completed",
          "project_path": "tasks/cml-spec7/project", "build_instructions": "tasks/cml-spec7/build.md",
          "trace_index": "tasks/cml-spec7/trace-index.md"}, ensure_ascii=False, indent=2))

    missing_rows = [
        ("human_edits", "`spec/submit-input.yaml`", "声明是否人工直接改码；有则提供人/目的/文件/前后版本/当时证据"),
        ("known_issues", "同上", "人工已知问题声明；本题已观察限制另据事实列示，不能代填“无”"),
        ("extra_sources", "同上", "人工额外来源声明；已有公开研究记录不能替代人工完整声明"),
        ("md_export_dir", "同上", "IDE手工Markdown导出目录；已有机械JSONL可读副本不是该导出"),
        ("version / contact / freeze_time", "`../common/spec-harness/team.yaml`", "正式成果包版本、联系人、北京时间冻结时刻"),
        ("members[0].name / work", "同上", "真实成员姓名与人工分工；不从本机用户名或AI角色推断"),
        ("source_guard", "同上", "人工填写实际来源保护措施；已有规则配置不代填该声明"),
    ]
    write("missing-fields.md", f"""
# 仍需补充的字段与真实证据缺口

以下原始人工字段为空，全部保持 **{PENDING}**，没有自动改为“无”：

{table(["字段", "原始输入", "待补内容"], [(a, b, PENDING + "：" + c) for a, b, c in missing_rows])}

`team_id=HC2026-111`、`team_name=Ghost_London`、`stage=online`、`task_id=cml-spec7`已有明确输入；`submitted_tasks=[]`、`attempted_not_submitted=[]`、`zip_out=""`由3-package处理，不阻断本题材料整理。本题JSON当前保守not_completed，拟定路径与完成范围已解释。

## 记录缺口和非人工字段

- Comate `sessionUuid`、客户端和扩展版本：**{PENDING} / 不适用**。实际使用Codex，检查未发现Comate索引，不能编造Comate值；证据见 `traces/discovery.json`、`facts.json`。
- 无侧边栏索引的子Agent独立IDE ID：**{PENDING}**。本体线程ID可从原生 `session_meta.payload.id` 证明，父子关系可读；不能复制父ID当子ID或宣称独立IDE对应已证明。逐项见 `trace-index.md`。
- 官方 `reports/build-baselines/cml-spec7.log`：**缺失**，见 `taskbook-versions.json.official_baseline_report`。本题 `logs/prepare-baseline.log` 是不同的既有证据；它不带独立执行起止时刻，`workflow/setup-result.json.prepared_at` 是准备完成登记时间，不能冒充脚本精确起止时间。现在补跑不能变成历史原件。
- 初始化独立hdc stdout捕获不完整：见 `facts.json.original_record_gaps`、转录JSON、原生工具返回与后续完整输出；不宣称原缺口已补回。
- 没有提供IDE“导出本地”Markdown路径；当前 `traces/markdown/` 由原生JSONL逐对象机械生成，明确标记，不冒称IDE导出。
- 原生记录为各自导出截止切片，活动会话后续事件和3-package行为尚未发生/尚需后续导出。导出时间与hash以 `traces/session-metadata.json` 为准，不能覆盖未来。
- B9–B11真实授权需要合法平台账号、应用身份/签名回调及服务端契约；本阶段不能用材料消除阻断，也不为补日志重跑业务。

团队打包前需补齐人工字段、正式提交选择及冻结时间，依据最终元数据刷新索引并重新校验完整工程与补丁；上述缺失均据实保留，不能由排版或示例值填满。
""")

    auto_rows = [
        ("团队、题目与阶段", "HC2026-111 / Ghost_London / online / cml-spec7", "`../common/spec-harness/team.yaml`、`spec/submit-input.yaml`"),
        ("基线与当前Git HEAD", base + "（完整提交版本另看project清单）", "`facts.json`、`spec/metadata.json`、`workflow/baseline-provenance.json`"),
        ("准备执行情况", setup["baseline_prepare"]["result"] + "，profile=harmony-cup-build-v1；dry_run=false", "`logs/prepare-baseline.log`、`workflow/setup-result.json`；官方报告缺失不能混称"),
        ("应用与入口", "com.joker.coolmall / EntryAbility", "`AppScope/app.json5`、`entry/src/main/module.json5`"),
        ("构建目标/依赖", "default / entry / debug，锁定版本见build表", "`build-profile.json5`、根和模块OHPM锁文件、`hvigor/hvigor-config.json5`"),
        ("历史HAP", f"{hap['bytes']} bytes / SHA256 {hap['sha256']}", "`facts.json.hap`、`logs/verification-navigation-smoke-03/install-manifest.json`"),
        ("当前本地验收", "38pass / 3blocked，非官方成绩", "`facts.json.validation`、`logs/verification-final-03.json`、`workflow/verification/final-verification-03.md`"),
        ("完整生产输入摘要", validation["source_sha256"], "`workflow/verification/root-delivery-check-03.json`、最终验证指纹；不等于14变更文件聚合"),
        ("实际AI工具/版本", f"Codex Desktop App {app_version}；各原生cli_version单列", "`facts.json.app_package`、`traces/session-metadata.json`"),
        ("模型/effort/token/双ID", "逐线程从原生记录读取，不重复累加累计token", "`traces/session-metadata.json`、`trace-index.md`及每个原生首行/turn_context/token记录"),
        ("任务书版本", "四任务书SHA256、公共包含仓库HEAD及历史列表", "`taskbook-versions.json`；公共git顶层并非独立spec-harness仓库"),
        ("日志副本与缓存排除", "逐项路径/bytes/SHA256，以清单为准", "`logs-copy-manifest.json`；原文件未删除，生成磁盘清理拒绝记录仍保留"),
        ("完整工程/资源/差异", "最终路径与摘要以机器清单为准", "`project-manifest.json`、`project-exclusions.json`、`changes/`、`patch-validation.json`"),
    ]
    write("auto-filled-facts.md", f"""
# 已自动填入的事实及出处

只取本题真实输入、现有记录和官方逐字段模板；未猜测人工字段。事实采集时刻以 `facts.json.collected_at_utc` 为准，会话导出时刻以 `traces/session-metadata.json.exported_at_utc` 为准。

{table(["事实", "自动填入内容", "具体证据"], auto_rows)}

公开来源与读取/失败范围另见 `sources.fragment.md`，人工空字段另见 `missing-fields.md`。历史命令、产物与失败证据未冒称本材料阶段新执行。
""")

    session_rows, token_rows, range_rows = [], [], []
    for s in meta["sessions"]:
        native = OUT / s["native_path"]
        lines = native.read_text(encoding="utf-8").splitlines()
        header = json.loads(lines[0])["payload"]
        sid = header["id"]
        source = header.get("source")
        rel = source.get("subagent", {}).get("thread_spawn", {}) if isinstance(source, dict) else {}
        parent = rel.get("parent_thread_id", "主会话 / 无父线程字段")
        role = s.get("agent_role") or ",".join(x.get("role", "") for x in s.get("agent_registrations", [])) or "主调度"
        session_rows.append((sid, header.get("session_id", "字段未提供"), parent, s["IDE_sidebar_id"], role))
        range_rows.append((sid, f"`{s['native_path']}` / `{s['markdown_path']}`", f"1–{len(lines)}（ordinal 0–{len(lines)-1}）", s["sha256"]))
        token = (s.get("latest_token_info") or {}).get("total_token_usage") or {}
        params = "; ".join(f"{x.get('model', PENDING)} / effort={x.get('effort', PENDING)}" for x in s.get("turn_contexts", [])) or PENDING
        token_rows.append((sid, params, token.get("input_tokens", PENDING), token.get("cached_input_tokens", PENDING),
                           token.get("output_tokens", PENDING), token.get("total_tokens", PENDING)))
    session_table = table(["Codex线程：payload.id", "原生payload.session_id（不能当子线程ID）", "父线程", "IDE侧边栏ID", "实际角色"], session_rows)
    token_table = table(["线程", "模型/参数（去重turn_context）", "input", "cached input（input子项）", "output", "原生累计total"], token_rows)
    ranges_table = table(["线程", "原生/机械Markdown副本", "本次切片事件行范围", "原生副本SHA-256"], range_rows)
    books_table = table(["实际任务书", "公共SHA-256", "本题副本SHA-256"],
                        [(x["local_path"], x["sha256"], x["local_sha256"]) for x in versions["task_books"]])
    write("trace-index.md", f"""
# 运行记录索引

本索引保留官方模板全部字段，当前为本题材料草案；相对材料路径从 `tasks/cml-spec7/` 读取，工程文件路径从其 `project/` 读取。当前draft中工程副本为 `traces/code-snapshot/project/`。证据最终以各机器清单为准。

- 题目 ID：`cml-spec7`。
- AI 在本题实际参与的研发环节、用途及对应原始会话／事件范围（每道作答的赛题均须填写）：需求拆解/复核、基线审计、方案修订、生产实现/修复、独立构建自测和回归、材料取证。按下面真实角色与原生全文行范围追溯；`workflow/requirements/`、`workflow/design/`、`workflow/implementation/`、`workflow/verification/` 是阶段交接，不能代替原生工具记录。B9–B11仍blocked。
- 基线构建准备：脚本配置版本、执行时间及输出记录路径（见 tools/prepare_baseline.py）：`logs/prepare-baseline.log` 记录 `profile=harmony-cup-build-v1`、`dry_run=false`、本题与基线、`changes=[]`；准备完成登记 `{setup['prepared_at']}` 来自 `workflow/setup-result.json`，不是脚本精确起止时刻。官方 `reports/build-baselines/cml-spec7.log` 缺失，版本/路径检查见 `taskbook-versions.json`；不把本地log冒称该官方文件。精确脚本执行起止时间 **{PENDING}**。
- Agent 名称及版本：真实工具为 `Codex Desktop`；Windows App包版本 `{app_version}` 来自 `facts.json.app_package`。原生运行时 `cli_version` 见各会话元数据（当前读取为 `0.163.0-alpha.10.2`），它不是桌面App/Comate扩展版本。角色定义为 `system-config/*/agents/*.toml`，与原生角色字段关联。Comate客户端/扩展版本 **{PENDING} / 不适用：实际工具并非Comate，未发现其索引**。
- 模型名称、版本及运行参数：逐会话 `turn_context.model/effort`、approval/sandbox等见 `traces/session-metadata.json.turn_contexts` 及下表；只填写可见模型ID，不推断内部模型版本。token采用截止时每会话最后可见 `event_msg/token_count.info.total_token_usage`，不逐事件累加，不跨旧快照重复相加；cached input是input子项，reasoning字段按原生口径保留，不能重复加到total。最新 `token_usage_record` 另留源行号与原始口径，活动会话可能晚于token_count；不混合两套计量或宣称最终账单。完整值/截止以机器JSON为准。
- 本题实际使用的 Skill、系统提示、工具及编排配置版本和保存位置：本题 `AGENTS.md`、四角色提示及已有 `system-config/initial-20261020T094258Z/`、`system-config/analysis-20261020T095248Z/`、`system-config/implementation-20261020T101847Z/`；实际工作流Skill、ArkTS参考/构建Skill副本和hash见对应清单/文件。工具使用由原生调用/返回证明，包括functions.exec内的shell/read/apply_patch、协作派工、真实构建设备与Hypium、公开通用SDK检索；`traces/session-metadata.json.tools_observed`仅统计外层可见调用，不能覆盖嵌套工具细节。文件存在不自动算已使用；按原生read调用确认。没有新增团队system-config。
- 运行期间配置变更及原因（无则填“无”）：四角色流程和访问范围由任务指令/实际配置副本记录；API/工具链路径按本机环境加载，原.ps1的不可移植限制见 `build.md`。方案布局修订、导航去重、文档测试助手修正、真实大屏旋转顺序修正均有交接和原始轮次。实际提示/配置快照版本见已有system-config及 `workflow/events.jsonl`；未推断缺失的私人全局配置变更。人工全局变更补充 **{PENDING}**。
- 主会话 ID：分析 `01a158b5-95c1-7843-be11-cfb16aaa2e74`；实施/回归 `01a158d0-416c-75a3-8836-233f0c35fb6f`；本次材料 `01a1590b-c9f9-7f32-9607-2b3f4c8c38e7`。逐项由原生首行 `payload.id`、本题登记和侧边栏过滤索引证明。
- 关联会话及子会话 ID：见下方完整映射与 `traces/session-metadata.json`。Comate引擎 `sessionUuid` **{PENDING} / 不适用（未发现Comate记录）**；Codex线程与IDE侧边栏ID分别核实。子Agent `payload.session_id` 可能为父主会话，不能替代其自身 `payload.id`；无独立侧边栏行的字段保持待补。
- 解题过程中产生的全部相关原始日志、DB 或原生轨迹文件路径及读取方式：`traces/native/*.jsonl` 为逐行UTF-8原生事件副本；`traces/session-index.filtered.jsonl`仅本题侧边栏索引；`traces/discovery.json`及 `native-discovery-search.json` 保存按工程路径与题号两个维度选择结果；完整构建/设备/测试输出在 `logs/`，逐文件路径/bytes/hash见 `logs-copy-manifest.json`。只导出本题独立记录，不提交整个客户端数据库或无关私人会话。初始化总览 `01a13fc4-2611-7761-a580-1283e0c70541` 按AGENTS排除，未作为功能证据读取。
- 失败、重试、未采用的候选方案及选择过程的记录位置：保留 `workflow/verification/final-verification-03.md`、`workflow/delivery-01.md` 和对应 `logs/verification-*-01/02/03/`；手机原轮1 error及文档补测、旧800vp被误称large后实测1200vp、导航/布局修订、02b并发改源作废、SDK查询失败、磁盘清理自动审批拒绝均可追溯。不能拿失效/跳过证据当当前pass。清理拒绝JSON仍保留，原磁盘未删。
- 实际提示、工具调用及返回结果、检索与代码修改、构建和自测记录位置：原生JSONL保留消息、工具调用及原返回；机械Markdown逐对象标出原生行号。代码修改交接在 `workflow/implementation/`，方案修订在 `workflow/design/`，第三方研究在 `workflow/provider-research-01.md` / `logs/provider-research-01/`，最终矩阵在 `logs/verification-final-03.json`。`changes/final.diff` 反映完整交付差异，不能替代原生过程。
- 导出时间、方法与读取方式：精确时间以 `traces/session-metadata.json.exported_at_utc` 为准；`tools/export_evidence.py` 只取本题所选原生文件/过滤索引，逐项保存源位置、hash、bytes、字段和快照标记。`traces/markdown/*.md` 是该脚本机械生成的JSONL可读副本，**不是IDE导出**。`md_export_dir` **{PENDING}**。下表范围只覆盖当前切片，`snapshot_only=true`、`includes_future_events=false`；当前导出之后事件须由后续打包继续收录。读取JSONL可逐行 `json.loads`，Markdown可直接阅读；源hash和事件行号可互查。
- 成果冻结时间（北京时间，与 `solution.md` 一致）：**{PENDING}**（团队 `freeze_time` 为空；材料快照/导出时间不代填正式冻结）。
- 官方工程基线标识（本次题包 metadata.base_commit 发布提交号）、最终提交版本标识：官方基线 `{base}`；Git HEAD仍为基线，未提交改动不能丢失。完整草案交付版本取 `project-manifest.json.final_version` 与 `snapshot_git_tree`；正式团队版本 **{PENDING}**，本阶段没有正式提交。
- 基线至提交版本的完整差异位置（建议 changes/final.diff，含新增、修改、删除；二进制变更另列文件及摘要）：`changes/final.diff`；`changes/changed-files.json`、`binary-files.json`、`resource-files.json` 和完整工程 `project-manifest.json`。补丁校验状态：{patch_state}。
- 与提交源码的对应关系：最终拟交project精确复制 `traces/code-snapshot/project/`；按 `project-manifest.json` 每项路径/bytes/SHA-256比对，基线clone后 `git apply --check --binary` 再实际apply和全树比较证据在 `patch-validation.json`。`.comate/submission-draft/`为派生材料，不递归入project；其他真实过程文件按声明清单纳入。缓存/生成磁盘排除及原因见 `project-exclusions.json`。源码/HAP与有效03测试指纹见 `facts.json.validation` 和原始轮次。扩大清单或改源须重新冻结/生成patch，不能把将来的修改视作已覆盖。
- 人工操作及相关记录位置：人工提示在本题原生JSONL消息中；人工操作完整声明 **{PENDING}**，原输入 `human_edits` 为空，详见 `human-changes.md`。
- 人工修改索引位置（可使用 `human-changes.md`；无则注明“无人工直接修改代码”）：`human-changes.md`；是否无人工直接改码 **{PENDING}**，目前不代填该否定声明。
- 人工修改的操作人、目的、文件、代码差异、修改前后版本及对应原始记录位置：全部 **{PENDING}**，需实际批次与当时证据；总体diff不能代替人工修改归属证明。
- 公开资料检索与代码复用记录位置，以及 `sources.md` 中的对应来源条目：本题 `sources.fragment.md`，待3-package汇入根sources；通用官方SDK实际读取/失败、锁定依赖、基线资源复用与原创正文分别说明。人工 `extra_sources` **{PENDING}**。
- 本题工作目录，以及赛题来源保护措施在本题运行中的配置位置（见 `solution.md`）：实际工作目录 `D:/HCUP/cml-spec7`，交付后为包内 `tasks/cml-spec7/project/`；本题AGENTS/角色及已有system-config限制访问本题、只读公共资源与授权官方模板/本题基线报告，禁止其他题和来源相关修复历史。团队人工 `source_guard` **{PENDING}**；实际观察事实见 `solution.fragment.md`、`sources.fragment.md`。
- 脱敏范围（无则填“无”）：当前取证脚本原生副本未做内容脱敏；系统用户名/本地路径保留在原始证据，build指南使用便携相对路径。筛掉无关会话、整个数据库与生成缓存属于选择范围，不冒称内容脱敏；源与副本hash可复核。正式打包敏感信息检查/人工补充 **{PENDING}**，不得遮蔽代码来源或修改依据。
- 记录缺失及原因（无则填“无”）：官方指定基线报告不存在；本地准备日志缺独立起止时刻；初始化hdc stdout的Transcript缺口；没有IDE手工Markdown导出；Comate不适用/不存在；部分子Agent独立侧边栏ID未核实；活动会话导出截止后的事件不在切片内；人工声明为空。细项见 `missing-fields.md`、`facts.json.original_record_gaps`。这些缺口没有以新造历史或有利推断补齐。

## 真实ID映射

{session_table}

## 模型参数与累计token口径

{token_table}

不把上表相加为单一账单：分叉可能继承上下文，不同累计口径/截止事件需保留原生解释。最新 `token_usage_record` 的usage、thread/turn/session/root_turn/response标识和源行号保存在机器JSON及原生文件，不用它覆盖或重算另一口径。

## 原生文件与事件范围

{ranges_table}

每个原生文件从首个session_meta到本次导出截止均可读；文件SHA对应本次切片，不承诺活动会话最终结束。脱敏/选择与缺失见官方字段说明。

## 实际任务书版本

`taskbook-versions.json`记录公共目录所属仓库HEAD及真实git顶层：公共spec-harness不是独立仓库，不能把其包含仓库HEAD当成四文件内容版本。四文件逐一校验如下，本题副本与实际公共输入对应；官方模板hash另在该JSON。`spec/history/`当前历史清单为空，没有编造历史版本。

{books_table}
""")

    write("DELIVERY.md", f"""
# cml-spec7 材料草案交接

这是2-submit单题材料草案，不是正式成果包。功能本地验收为38pass/3blocked（B9–B11），未全完成；原始失败/重试和限制未删除，完整事实见 `solution.fragment.md`。team未选择submitted题目，当前JSON保守not_completed；三个非空路径仅为3-package拟定映射。

## 文件与后续映射

| 当前草案相对路径 | 3-package拟定包内路径/用途 |
| --- | --- |
| `traces/code-snapshot/project/` | `tasks/cml-spec7/project/`，精确复制这一文件树 |
| `build.md` / `trace-index.md` / `human-changes.md` | `tasks/cml-spec7/`下同名文件 |
| `changes/`、`traces/`、`logs/`及取证JSON | 本题材料目录内保留相对关联；原生文件只保留本题 |
| `sources.fragment.md` / `solution.fragment.md` | 3-package汇总到团队根sources/solution；当前不改团队根文件 |
| `submission.json.fragment` | 仅本题task对象，合并团队总任务清单，最终status由真实提交选择决定 |
| `missing-fields.md` / `auto-filled-facts.md` | 人工待补与自动事实两份清单 |

`.comate/submission-draft/`是材料派生输出，不能再整个塞回project。否则final.diff包含自身、代码快照再包含快照，无法有限冻结。除了该输出及逐项识别缓存，实际Spec、inputs、Hypium、workflow、系统配置副本、原始记录等仍按 `project-manifest.json` 清单交付。`project-exclusions.json`列明缓存/生成磁盘排除，不删除原文件；`logs-copy-manifest.json`逐项保存日志副本hash和排除原因。项目/补丁输出本身位于清单外，避免摘要包含自身。

## 版本与补丁核对

官方基线 `{base}`。完整交付版本/文件数量/哈希、snapshot git tree与本次快照时刻取 `project-manifest.json`；快照时刻明确不是团队正式freeze_time。源码完整生产输入SHA为 `{validation['source_sha256']}`；历史HAP为 `{hap['bytes']}` bytes、SHA256 `{hap['sha256']}`。Git HEAD仍停在基线，不能只用普通git diff漏掉未跟踪材料。

主调度负责生成 `changes/final.diff`（`--binary`、新增/修改/删除全量），并保留临时基线clone的原始命令、输出和校验记录；先 `git apply --check --binary` 后真实apply，每个交付文件SHA、额外文件与删除项、生产漂移和BuildProfile噪声均在 `patch-validation.json`。**当前读取的校验状态：{patch_state}。** 不以diff语法通过代替完整应用/全树一致性。临时 `.validation-work/`、`validation/independent-baseline/` 当前均在本地保留，按 `assembly-plan.json` 及最终 `artifact-manifest.json` 的排除规则不随包。主调度安全清理 `.validation-work/` 的操作被自动审批以 `blocked by policy` 拒绝，未执行，也未换机制删除；原始拒绝记录见 `temporary-clone-cleanup-rejected.json`。该拒绝不改变已完成的补丁应用和逐文件校验结果，不以临时clone目录代替原始校验记录。

当前快照树不含构建依赖缓存或HAP编译产物；`facts.json`保存历史验证HAP摘要，使用 `build.md`从完整工程重建。二进制与资源单列 `changes/binary-files.json`、`changes/resource-files.json`；每项路径、bytes、SHA及基线同源关系可查，文本SVG也在diff与资源清单内。最终以真实生成清单为准，不在正文硬编码会持续变化的数量。

## 原生记录、失败和缺口

会话选择由工程路径与题号两维核对，真实ID、父子关系、源路径、导出hash/bytes、模型与累计token口径见 `traces/session-metadata.json`；`traces/discovery.json` / `native-discovery-search.json`记录过滤过程。`traces/native/*.jsonl`为可独立读取的原生副本；`traces/markdown/*.md`是机械副本，不是IDE导出。导出截止后的事件和3-package活动须后续收录，不用当前材料快照冒充未来完整轨迹。混含其他题的初始化总览排除，不作为本题功能证据。

官方本题基线报告缺失，本地prepare log与setup登记如实分别引用；初始化hdc stdout捕获缺口、手机原轮测试error及定向补测、800vp旧轮/1200vp新轮、02b失效、清理拒绝均保留。详见 `trace-index.md`、`missing-fields.md`。本阶段没有补跑命令来冒充历史原始输出。

## 仍需人工补充与正式打包条件

见 `missing-fields.md`：human_edits、known_issues、extra_sources、md_export_dir，以及团队version/contact/freeze_time/members/source_guard均为 **{PENDING}**。已自动取事实与出处独列 `auto-filled-facts.md`。不能根据空字段写“无人工修改/无额外来源”，不能把材料时间代填正式冻结时间。

主调度还需将最终材料会话刷新进原生切片，重跑本文档生成器以同步机器元数据和补丁状态，并由独立验证角色核对官方逐字段、路径/文件存在、完整patch/快照与便携说明。正式3-package在真实冻结/选择后再生成团队根文件及ZIP。本角色仅撰写被授权文档，无业务、资源、配置或测试改动。
""")
    # Keep input/config copies and byte-exact line-ending scope explicit without
    # modifying machine evidence produced by the coordinating agent.
    for name in ["trace-index.md", "DELIVERY.md"]:
        text = (OUT / name).read_text(encoding="utf-8")
        text += "\n## 补充取证位置与字节范围\n\n"
        text += ("原始人工输入与官方逐字段模板的包内只读副本为 `evidence-inputs/team.yaml`、"
                 "`evidence-inputs/submit-input.yaml`、`evidence-inputs/templates/`。本材料阶段实际读取的"
                 "工作流Skill及四角色配置副本/hash在 `evidence-inputs/current-config/manifest.json`；"
                 "它是本题材料附件，不改团队根system-config。原始公共输入路径用于来源说明，"
                 "离线核对可直接读取这些随包副本。\n\n"
                 "`changes/line-ending-only.json`另列既有Windows CRLF与基线LF造成的纯行尾差异；"
                 "这些既有字节差异纳入exact-bytes补丁，但不计为本材料阶段业务改动。"
                 "主调度在临时基线clone中设置 `core.autocrlf=false`，以清单内真实字节生成和应用补丁，"
                 "不改原工程行尾。文件数、清单hash与比较结果以最终机器JSON为准。\n\n"
                 "本材料阶段沿用同一生产源码的历史构建/设备结论："
                 "`current-production-fingerprint.json`与最终03验收完整生产输入SHA一致，"
                 "没有通过重跑构建制造新证据；根调度的 `git diff --check` 退出0，"
                 "记录见本次原生会话及材料验证报告。\n")
        write(name, text)
    names = ["build.md", "trace-index.md", "sources.fragment.md", "solution.fragment.md", "submission.json.fragment",
             "human-changes.md", "missing-fields.md", "auto-filled-facts.md", "DELIVERY.md"]
    print(json.dumps({"writer_thread": os.environ.get("CODEX_THREAD_ID"), "written": names,
                      "document_sha256": {n: hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names},
                      "patch_state_at_generation": patch_state, "logs_manifest_entries": len(logs.get("copied", []))}, ensure_ascii=False))


if __name__ == "__main__":
    main()
