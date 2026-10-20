"""Render task materials from inspected local evidence; blank declarations stay blank."""
from pathlib import Path
from datetime import datetime, timezone
import json
from collect_evidence import ROOT, OUT

def save(name,text):
    (OUT/name).write_text(text.rstrip()+'\n',encoding='utf-8')

def main():
    native=json.loads((OUT/'traces/native-manifest.json').read_text('utf-8'))
    snap=json.loads((OUT/'traces/code-snapshot/manifest.json').read_text('utf-8')) if (OUT/'traces/code-snapshot/manifest.json').exists() else {}
    patch=json.loads((OUT/'validation/patch-validation.json').read_text('utf-8')) if (OUT/'validation/patch-validation.json').exists() else {}
    app=json.loads((OUT/'traces/runtime-versions.json').read_text('utf-8'))
    base=json.loads((ROOT/'spec/metadata.json').read_text('utf-8'))['base_commit']
    state=json.loads((ROOT/'workflow/state.json').read_text('utf-8'))
    package=lambda p:'traces/cml-spec1/'+p
    summary=f"{snap.get('file_count','【待补充】')} 文件，完整项目聚合 SHA-256 `{snap.get('snapshot_aggregate_sha256','【待补充】')}`"
    save('build.md',r'''# cml-spec1 构建与运行

下列命令从包内 `tasks/cml-spec1/project/` 执行。工程、锁文件及自测工具均随包提供。命令使用复现方的本地工具环境，本说明不依赖参赛电脑的私有目录或环境脚本。

## 环境与依赖

原实测环境：DevEco Studio 6.1.0.860、SDK API23、Node 18.20.1、JBR 21.0.8、hdc 3.2.0c。工程 `build-profile.json5` 保留 target/compatible `6.0.1(21)`，product `default`；工程 API21 配置与使用 API23 SDK 的事实分别记录。

安装上述工具，将 DevEco 的 Node、JBR、ohpm、hvigor 和 SDK hdc 工具加入当前终端 PATH，并使 JAVA_HOME、DEVECO_SDK_HOME 指向复现方安装目录。仓库不含独立 hvigorw 包装器，命令由 DevEco 提供。保留所有模块的 `oh-package.json5` 与 `oh-package-lock.json5`；模块间 `file:` 依赖均为工程内相对路径。新增运行依赖为 `@ohos/lottie=2.0.33`，锁文件同时保留 registry 地址及 integrity。根开发依赖有 `@ohos/hypium=1.0.24`、`@ohos/hamock=1.0.0`。

```powershell
ohpm install --all
hvigorw clean --mode module -p product=default -p buildMode=debug --no-daemon
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

最终产物相对路径：`entry/build/default/outputs/default/entry-default-unsigned.hap`。原实测大小 20,739,960 bytes，SHA-256 `d54386d3d42a6049d5af9fcece16c9d0cdbd271a2217cb008c196af177202615`。重建产物可能因工具时间戳不同而摘要不同，源码绑定以随包快照清单为准。

## 安装、启动与初始化

应用 bundleName `com.joker.coolmall`，模块 `entry`，入口 `EntryAbility`；应用版本 `1.0.0` / `1000000`。原验证模拟器为 Pura 90 Pro Max，系统镜像 6.1.0.115 / API23，分辨率 1308×2880、560dpi。

```powershell
hdc list targets
$taskDevice = Read-Host '输入 hdc 实际列出的目标序列号'
hdc -t $taskDevice install -r ./entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t $taskDevice shell bm dump -n com.joker.coolmall
hdc -t $taskDevice shell aa start -a EntryAbility -b com.joker.coolmall
```

`signingConfigs` 为空，当前 HAP 未签名。上述 unsigned HAP 在原模拟器安装成功有日志；其他设备若要求签名，应由复现方使用自己的合法签名配置，不随包提供参赛者签名私钥。原首启包含麦克风权限请求，拒绝权限后的系统设置窗口与返回路径在基线日志保留；此权限不是四标签本地导航的授权前提。保留启动路由和数据库自动初始化，无需预置账号、人工改库或启动私有服务。购物车为空、我的页未登录属于已测状态。

## 本题自测

以下复现环境安装方式使用随包 `test-harness/`。原执行使用其公共只读副本，实际 argv 与退出码见日志；本次材料整理没有重新执行构建或设备测试。

```powershell
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r ./test-harness/requirements.txt numpy==2.5.4 opencv-python==5.0.0.93
$env:PYTHONPATH = (Resolve-Path ./test-harness).Path
./.venv/Scripts/python.exe -m harness.runner --project (Get-Location).Path --device $taskDevice --json ./logs/selftest-reproduction.json
```

Python 原实测为 3.12.3，Hypium 为6.1.0.210；NumPy/OpenCV 版本是材料整理时从同一公共虚拟环境只读查询得到，不冒称保存了历史运行时的独立依赖锁。不要启用 skip-env-check。测试会写新的日志和轨迹，复跑结果应另存，不替换原 run-r4。

## 原始验证与限制

原最终独立构建 `assembleHap` exit0（增量任务含 UP-TO-DATE），其日志 `logs/verification-do-build-run-r2-commands.json` 与同前缀 assembleHap.log；首次 clean 全量构建为修复前 r1，不能混写。基线182条文件诊断无新增，比较见 `project/traces/verification-do-r1/independent-warning-compare-r1.json`（相对本说明所在目录）。run-r4 安装与 runner 均exit0，8/8 pass，A1–A44本地验收通过，记录在 `logs/selftest-run-r4.json`、`logs/verification-do-run-run-r4-commands.json`，详细矩阵见 `project/workflow/verification/do-matrix-r4.md`。

历史一次 LIFECYCLE_TIMEOUT 的根因尚未完全排除，最终 run-r4 未复现；截图工具的有界重试原文保留。未运行官方隐藏测试，不声明官方得分。文本输入、空白输入、强制网络请求失败分支不属于本题可达验收内容。现有构建和自测日志完整复制到本题 `logs/`，本阶段无需补跑替代历史证据。
''')
    fields=[
      'cml-spec1',
      '基线需求拆解、方案、ArkTS/Lottie 实现、构建诊断、8项设备自测及修复回归；本阶段另做材料整理。分析主会话 01a1574d-f7fd-7032-96ff-7fec7f78a664（含两个分段），功能主会话 01a15796-a9f1-7d30-8387-81c60bbd3b0f；逐会话文件、行号、工具调用见 traces/cml-spec1/native-manifest.json 与 tool-call-index.jsonl。',
      '本地 logs/prepare-baseline.log：profile=harmony-cup-build-v1、dry_run=false、changes=[]；project/workflow/setup-result.json 记准备结束 2026-10-20T03:13:47.519931+00:00。该时间是本地报告 prepared_at，不冒称脚本自身输出时间。指定题包 reports/build-baselines/cml-spec1.log 缺失；脚本源码提交版本【待补充】。',
      'Codex Desktop；原生 cli_version=0.163.0-alpha.10.2；当前已安装应用包 OpenAI.Codex=26.1013.4894.0（只读查询，不证明历史已安装版本）；四角色名称、agent_path、配置见 project/system-config 与 native-manifest.json。Comate 客户端/扩展版本【待补充】（未找到所列路径，本次为Codex运行器）。',
      '已核验各原生 turn_context：gpt-6.1-sol，effort=xhigh。模型服务精确构建版本【待补充】（原生未提供）。按分段保存实际 token_count.total_token_usage，见 native-manifest.json；含input/cached/output/reasoning/total，不跨分段求和冒称实际账单。未记录的温度等参数【待补充】。',
      'harmony-task-flow 与四角色配置；实施阶段另实际使用 arkts-syntax-assistant、hmos-arkts-knowledge-retriever、hmos-arkts-syntax-checker。前三者归档在 project/system-config/{initial-20261020T031059Z,analysis-20261020T034136Z,implementation-20261020T043624Z}/；syntax-checker当时读取的内容与工具返回以原生记录为证，当前定义补充归档在traces/cml-spec1/config-supplement/，不冒称它是历史冻结副本。实际读取/调用以原生工具序列为准，工具名称及嵌套tools调用见 native-manifest.json/tool-call-index.jsonl。生效规则来源 AGENTS.md、对应Skill与角色TOML；Comate appliedRuleNames 字段不存在，不能编造。',
      '初始化、分析、功能实施三个配置快照版本均保留；原因与阶段交接见 project/workflow/events.jsonl 与 state.json.config_snapshot_history。实施补充语法/知识检索Skill；本阶段仅更新材料采集/验证脚本，见 traces/cml-spec1 与本题验证报告，未改业务配置。',
      '分析 01a1574d-f7fd-7032-96ff-7fec7f78a664；功能 01a15796-a9f1-7d30-8387-81c60bbd3b0f；材料 01a157ed-349c-7131-b46e-eaaf0b4f6055。这是实际Codex session_meta.id/session_id及侧边栏线程标识。Comate 引擎sessionUuid【待补充】；不能把继承的token_usage_record.session_id伪装成另一引擎UUID。',
      '全部本题原生分段/子会话ID与agent_path逐项见 traces/cml-spec1/native-manifest.json；轻量侧边栏索引筛选行见 traces/cml-spec1/session_index.filtered.jsonl。映射依据 session_meta.id 及可用 token_usage_record.thread_id；每个副本有SHA-256，未整盘复制客户端数据库。',
      'traces/cml-spec1/native/*.jsonl 为实际原生逐行JSON；traces/cml-spec1/markdown/*.md 为全记录逐行JSON格式Markdown转换副本，不是人工补写对话或IDE导出；project/traces/ 保存本题历史快照、命令、失败和设备证据。初始化跨题会话单独排除，详细边界见code-snapshot/manifest.json。',
      'project/workflow/state.json.failures、project/workflow/verification/do-failure-r1.md、do-result-r4.md，以及project/traces/verification-do-r1/run-r1至run-r4和script-versions/；依赖ETIMEDOUT后成功记录在logs/ohpm-install.log。未采用/修订方案见project/workflow/design/。初始镜像启动内存故障保留日志，磁盘缓存不随包。',
      '原始提示、真实工具调用/返回与代码写入见native JSONL及tool-call-index.jsonl（原生行号）；代码冻结r1/r2及差异在project/traces/do-implementation/；构建、自测日志在tasks/cml-spec1/logs/，源实现与当前完整快照同版性分别有两类摘要。',
      '本次导出UTC时间见traces/cml-spec1/native-manifest.json的export_started_utc/export_finished_utc，读取方法见traces/cml-spec1/README.md。JSONL按行解析，Markdown只是方便阅读的派生物。活跃整理会话是截至导出时的快照，不含之后事件；3-package最终冻结应再次导出。',
      '【待补充】（team.yaml.freeze_time为空；本地生产冻结、工程快照采集时间均不代替团队成果冻结时间）。',
      f'官方 base_commit={base}；当前HEAD仍为同一基线，业务变化未Git提交。最终完整工程版本以 {summary} 标识；688文件生产冻结聚合另为2cebe8ebb0c7fcc3d15058f9dedb0843580aacf5b1f41593f3dbe4200cf9d14c。',
      'tasks/cml-spec1/changes/final.diff（--binary/--full-index）；tasks/cml-spec1/changes/binary-files.csv 单列路径、大小、SHA-256与基线同源说明；全部实际文件位于完整项目快照/最终project。新增生产资源为4 JSON+6 SVG文本，无生产二进制修改。',
      f'唯一工程输入为traces/cml-spec1/code-snapshot/project/，打包时原样复制为tasks/cml-spec1/project/。清单包括spec/hypium_tests/system-config/workflow/本题traces/ignored AGENTS.md及staging之外的.comate文件；排除目录逐项列于manifest。补丁不包含它自身所在submission-draft，避免自包含递归；不得从live目录再把staging复制进project。验证：基线独立clone、checkout、git apply --check --binary、真实apply、{patch.get("files_compared","【待补充】")}文件逐SHA-256及新增/删除集合比较，详见验证报告。',
      '现有原生记录包含用户对专用模拟器内存释放的选择和权限拒绝/返回操作；定位 project/workflow/verification/baseline-r1.md至r3.md和分析主会话原生记录。操作者姓名/职责仍【待补充】，不从提示推定实名。',
      'human_edits=【待补充】（spec/submit-input.yaml为空）；本题提供human-changes.md作为事实/待确认索引，不能自动声明“无人工直接修改代码”。',
      '【待补充】（操作人、是否直接改码、目的、文件、前后版本及原始证据待提供者确认；AI工具改码已有原生证据不等于排除人工改码）。',
      '见最终包根sources.md的cml-spec1基线、Lottie2.0.33、官方ArkUI文档检索及公共自测工具条目（草稿为sources.fragment.md）；实际成功/失败检索保留在设计_do原生记录。extra_sources=【待补充】，不以已查日志替用户作排他性声明。',
      '原工作目录 D:/HCUP/cml-spec1，仅作证据定位，不是构建依赖。实际隔离规则见project/AGENTS.md及project/system-config/；team.yaml.source_guard=【待补充】。审计范围失误如实见traces/cml-spec1/README.md：初次全库题号rg只输出文件名；编码审计前缀扫描曾触及混合快照，均未作实现参考，未复制其原始会话。',
      '原生副本未作字段或内容脱敏；保留路径、账号内部ID与原始工具结果，不含整个客户端数据库。排除初始化混合会话属于题目范围过滤，排除缓存属于打包边界。后续3-package需核查敏感信息，不应无记录改写这些原生副本。',
      '官方指定reports日志缺失；Comate引擎UUID/版本字段与IDE Markdown导出未提供；原生不暴露的模型精确版本/参数不能补造。当前整理会话只是时间点快照；历史任务书spec/history不存在。原生当前可读文件均保留其全部分段，过去是否存在已删未留档会话不能据此保证。'
    ]
    template=(OUT/'traces/official-templates/trace-index.md').read_text('utf-8')
    lines=[];i=0
    for line in template.splitlines():
        if line.startswith('- '):lines.append(line+' '+fields[i]);i+=1
        else:lines.append(line)
    assert i==24,(i,len(fields))
    save('trace-index.md','\n'.join(lines)+'\n\n路径口径：project/、logs/、changes/、human-changes.md相对本索引所在tasks/cml-spec1/；traces/cml-spec1/及tasks/前缀相对成果包根。裸native-manifest.json、tool-call-index.jsonl等轨迹文件名均指包根traces/cml-spec1/下同名文件。sources.fragment.md/solution.fragment.md由3-package汇总到包根sources.md/solution.md。在本草稿内，traces/cml-spec1/对应traces/，tasks/cml-spec1/对应本目录。\n\n任务书版本：common为HCUP仓库受版本控制的子目录；当前包含仓库HEAD=e9befa727bcd94f2eea263bd3c92c56d9f8ec6ac，四份任务书SHA-256与本题副本一致，见traces/cml-spec1/taskbooks/version.json。当前版本核验不替代历史原生提示；spec/history/当前不存在。')
    save('solution.fragment.md',f'''# cml-spec1 汇总片段

团队：HC2026-111 / Ghost_London，阶段online；版本、联系人、成员实名分工、团队冻结时间及来源保护声明均【待补充】。这是单题材料草稿，没有上传、邮件或正式赛事提交。

完成内容：四底部标签点击与双向滑动联动、选中状态、有限Lottie动画、离选复位、首页内容/滚动及重复选中回顶、空购物车/未登录状态和冷暖启动。独立run-r4在原模拟器8/8通过，44项本地验收通过（28明文、11派生、5批准策略）。原始报告及命令见project/workflow/verification/do-result-r4.md和logs/selftest-run-r4.json；未运行官方隐藏用例，无官方评分结论。

AI实际参与：主Agent调度需求、方案、编码、自测四角色，基线探索、失败归因、Swiper索引修复、设备动态采帧、回归与材料审计均有原生记录。gpt-6.1-sol/xhigh和每个分段实际token字段见traces/cml-spec1/native-manifest.json。分析与功能会话分开，本次材料四角色报告不能替代之前解题证据。

未完成项与已知问题（提供者）：【待补充】。已有证据的局限须保留：历史一次LIFECYCLE_TIMEOUT根因未完全排除，改进停止夹具后最终8组未复现；截图工具局部有界重试不重放业务动作；官方隐藏测试不可见；原有182条文件诊断无新增。不存在文本输入/必需联网分支，因此不声称相关注入测试通过。

人工直接改码声明：【待补充】；现有日志中的用户设备选择和权限操作见human-changes.md，不推定操作人姓名。额外来源完整声明：【待补充】；已证实的依赖和公开文档查询见sources.fragment.md。实际来源边界规则见project/AGENTS.md、system-config快照；团队source_guard空白仍待确认。本轮范围扫描失误与排除边界公开记于trace-index及traces README，不能声明从未触及混合初始化文件的任何字节。

生产冻结：688文件聚合2cebe8ebb0c7fcc3d15058f9dedb0843580aacf5b1f41593f3dbe4200cf9d14c，HAP d54386d3d42a6049d5af9fcece16c9d0cdbd271a2217cb008c196af177202615；本阶段生产文件零变化。完整工程提交快照：{summary}，包括本题过程文件。差异从基线生成，校验记录见validation/patch-validation.json；这不是团队成果冻结时间。

成果冻结时间（北京时间）：【待补充】。3-package负责团队级文件、系统配置汇总和ZIP；应使用本文指定的工程快照及最终导出的本题原生记录，先补齐人工声明，再冻结打包。
''')
    save('sources.fragment.md',f'''# cml-spec1 来源汇总片段

1. 随包官方基线：metadata声明base_commit `{base}`，bundle标识`repo_bundles/coolmallarkts-7014cebd60-base.bundle`；输入摘要与准备来源登记在project/workflow/baseline-provenance.json。基线已有源码、依赖与资源原样随完整工程保留，不把它们当作新增外部创作。二进制原路径同源性见changes/binary-files.csv。官方题包reports日志当前缺失，本地logs/prepare-baseline.log不能冒称该文件。
2. 新增第三方运行库：[@ohos/lottie 2.0.33](https://ohpm.openharmony.cn/#/cn/detail/@ohos%2Flottie)，实际锁定HAR地址和integrity见project/feature/main/oh-package-lock.json5及entry锁文件；获取/安装原文在logs/do-ohpm-install-r1.log。查阅[公开Lottie README](https://gitee.com/openharmony-tpc/lottieArkTS/blob/master/README_zh.md)与OHPM元数据用于有限播放、暂停/销毁等API设计，实际请求序列见设计_do会话原生L52/60/82/94及其返回，不是本次重新访问来源项目修复历史。
3. 已发生公开技术检索：[ArkUI Monitor](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-new-monitor)、[Param](https://developer.huawei.com/consumer/cn/doc/harmonyos-guides/arkts-new-param)、[Scroll](https://developer.huawei.com/consumer/en/doc/harmonyos-references-V13/ts-container-scroll-V13)、[Swiper](https://developer.huawei.com/consumer/en/doc/harmonyos-references-V13/ts-container-swiper-V13)。部分打开返回Internal Error，保留原结果，不将失败访问写成已成功阅读。证据：traces/cml-spec1/native/中01a15798-722e-79d0-8668-f98754c9dda5会话及project/workflow/design/do-design-r1.md。
4. 新增4份Lottie JSON与6份商品SVG为AI在本题生成的文本资源，实施交接及原始写入记录见project/workflow/implementation/do-handoff-r1.md与01a1579e-dd21-7b11-a80b-23fc553e29e4会话。经本地摘要比对，不与基线677个文件任何blob逐字节相同；这项比较不能独立证明创作来源。22个生产变更均为文本，没有新增/修改生产二进制素材。原始新增文本资源路径/大小/摘要见project/workflow/implementation/submission-project-audit-r1.md。
5. 自测工具：随包project/test-harness/为公共自研harness的本题副本；Hypium6.1.0.210、NumPy、OpenCV用于真实设备控制、截图和动态帧断言。依赖清单、原运行环境与只读查询记录见build.md及traces/cml-spec1/runtime-versions.json。原有工程全部第三方依赖仍以各模块清单、锁文件为准。

extra_sources（提供者完整声明）：【待补充】。本表记录已核实来源，不据此断言没有其他使用、人工复制或历史缺失；不推定许可范围，第三方授权与许可随依赖自身文件核对。未查询来源项目相关修复提交、PR、Issue或补丁；本次审计的初始化混合记录扫描范围失误已在trace-index中披露。
''')
    save('human-changes.md','''# 人工操作与修改索引

提供者 human_edits 为空，声明为【待补充】。不能自动填写“无人工直接修改代码”。操作人、是否人工编辑、目的、文件、前后版本、原始证据均待确认；若确有人工改码，应补已有真实编辑历史/差异索引，不能事后补造过程。

现有本题原始记录能证实：用户在分析阶段选择释放一个模拟器以缓解内存；权限拒绝和系统最近任务返回的设备操作被记录。索引为project/workflow/verification/baseline-r1.md、baseline-r2.md、baseline-r3.md及分析主会话原生两个分段。AI实施工具调用与差异可证明AI参与，不能证明人从未改码。上述事实不填入空白的提供者声明，也不猜测实名。
''')
    task={'task_id':'cml-spec1','status':'submitted','project_path':'tasks/cml-spec1/project','build_instructions':'tasks/cml-spec1/build.md','trace_index':'tasks/cml-spec1/trace-index.md'}
    save('submission.json.fragment',json.dumps(task,ensure_ascii=False,indent=2))
    missing=[('team.version','成果包版本'),('team.contact','联系人姓名及邮箱/电话'),('team.freeze_time','北京时间成果冻结时间'),('team.members[].name','成员实名'),('team.members[].work','成员实际分工'),('team.source_guard','提供者的实际来源保护措施声明'),('task.human_edits','是否人工直接改码及已有证据'),('task.known_issues','提供者确认的未完成项与已知问题'),('task.extra_sources','提供者确认的完整额外来源使用声明'),('task.md_export_dir','IDE侧边栏Markdown导出目录；当前提供原生转换副本')]
    save('missing-fields.md','# 仍需提供者补充的字段\n\n'+ '\n'.join(f'- `{k}`：**【待补充】**，{v}。' for k,v in missing)+'''

以上来自../common/spec-harness/team.yaml及spec/submit-input.yaml的空字段；members的name/work为两个原字段。team_id、team_name、stage、task_id已有值。submitted_tasks、attempted_not_submitted、zip_out只属3-package，本阶段不擅填。

客观证据缺口：官方指定reports/build-baselines/cml-spec1.log缺失（本地准备输出已保留）；Comate引擎sessionUuid/客户端扩展字段不存在于当前Codex运行器；模型精确服务构建版本与未暴露参数无法核实。没有用示例UUID或版本替代。当前Codex应用版本仅是现状查询。活跃材料会话最终导出由3-package冻结时补齐，不能称本次时间点副本包含之后事件。
''')
    save('auto-filled-facts.md',f'''# 已自动填入的事实及出处

| 已核实事实 | 出处 |
| --- | --- |
| 团队HC2026-111 / Ghost_London、online；本题cml-spec1 | ../common/spec-harness/team.yaml；spec/submit-input.yaml（原始空字段未补猜） |
| 基线 `{base}`、对应bundle标识 | spec/metadata.json；workflow/baseline-provenance.json |
| 本地准备profile=harmony-cup-build-v1，changes=[]；指定题包reports缺失 | logs/prepare-baseline.log；workflow/setup-result.json；本轮真实文件存在性查询 |
| bundleName com.joker.coolmall，entry/EntryAbility，版本1.0.0/1000000；配置API21 | AppScope/app.json5；entry/src/main/module.json5；build-profile.json5 |
| 新增Lottie2.0.33、HAR地址与integrity；新增JSON/SVG而无业务二进制修改 | feature/main/oh-package.json5及两锁文件；workflow/implementation/submission-project-audit-r1.md |
| 生产688文件聚合2cebe8...，本阶段零变化；HAP20739960bytes、d54386d3... | traces/do-implementation/source-frozen-r2.json；production-preservation.json（本次重算） |
| 原最终构建exit0、安装exit0，8/8本地自测，44项本地矩阵 | logs/verification-do-build-run-r2-commands.json；logs/verification-do-run-run-r4-commands.json；logs/selftest-run-r4.json；workflow/verification/do-result-r4.md |
| 历史超时尚有局限、所有失败与重试保留 | workflow/state.json.failures；workflow/verification/do-result-r4.md；traces/verification-do-r1各轮原文 |
| {len(native['files'])}原生分段，模型gpt-6.1-sol/xhigh、cli_version0.163.0-alpha.10.2，每分段实际token字段与工具 | traces/native-manifest.json；traces/tool-call-index.jsonl；原生session_meta/turn_context/token_count |
| 当前应用包26.1013.4894.0；当前Hypium/NumPy/OpenCV版本 | traces/runtime-versions.json；本轮只读Get-AppxPackage及importlib.metadata查询；不推定历史客户端版本 |
| common所在仓库HEAD与四任务书真实SHA-256、本题副本一致；无spec/history | traces/taskbooks/version.json及common任务书副本 |
| 完整工程{summary}；补丁逐文件重建验证 | traces/code-snapshot/manifest.json；validation/patch-validation.json；validation/patch-commands.json |
| 二进制逐文件大小、摘要、原路径基线同源性 | changes/binary-files.csv；完整工程实际文件 |
| 已发生的第三方依赖与技术文档成功/失败查询 | sources.fragment.md；设计_do原生工具调用及返回 |

本表中的工程路径均相对本题工程；草稿路径均相对本目录。证据能证明的实际事实与提供者留空的人工/来源/已知问题声明分别记载，不作排他性推断。
''')
    (OUT/'traces/README.md').write_text(f'''# 本题轨迹读取与范围说明

native/保存本次只摘本题的{len(native['files'])}个原生文件分段，全部有独立SHA-256；同一主会话的后缀分段同样保留。用Python逐行json.loads读取，tool-call-index.jsonl提供原生文件行号。markdown/是每个JSONL逐行的完整格式化JSON转换副本，保留提示、工具调用、结果、失败及原生事件，不是IDE“导出本地”。未提供md_export_dir的事实仍保留【待补充】。

session_index.filtered.jsonl仅含选中本题ID的真实索引行，能证明三条主会话的侧边栏映射；其余子会话没有侧边栏索引行，保留原生线程ID并将独立侧边栏映射标【待补充】。子记录token_usage_record.session_id有继承父ID的情况，不当作独立引擎UUID。Comate数据库未找到，原生格式没有sessionUuid、payload.agent、appliedRuleNames等Comate字段；按实际格式取证，不伪造同名字段。

模型/effort来自turn_context，token值是各分段最后一个原生token_count.total_token_usage。它是原始运行统计，不跨分段求和作为账单，不把缺少字段视为0。导出时间与最后事件时间逐文件记录；活跃材料会话只含截至导出时的事件，最终3-package冻结还须再次导出。

发现方法：先按原生首行cwd匹配工程路径，再按轻量侧边栏索引题号和获准本题原生文件正文题号核对。非本题工作区候选不复制。必须排除的初始化总览UUID=01a13fc4-2611-7761-a580-1283e0c70541，旧混合快照目录同样不进完整工程。

范围失误如实披露：本阶段最初的题号rg曾扫描整个原生store正文，仅输出命中文件名；后来改成先metadata/轻量索引筛选，再在本题文件正文查询。编码审计曾读取git可见文件前8000字节做二进制判断，未先排除初始化混合快照。均未解析/输出该混合原文作为实现参考、未复制其原生会话到草稿；当前正确采集器已修正。首次Git本地clone默认优化曾复制共享对象库存储，已中断该轮，改用--no-local限定本题分支；未查询这些额外对象作为实现或上游历史参考，旧临时clone不进入交付，清理及重试记录见validation/material-retry-history.json。本阶段审计记录不能替代原解题证据。

code-snapshot/project/是后续3-package的唯一工程复制源；manifest.json列全部文件、摘要和排除项。业务与本题过程文件均保留，排除.git/构建依赖缓存/模拟器磁盘缓存/混合初始化记录/submission-draft自身。排除submission-draft避免补丁自包含递归；staging之外的.comate不排除。失败、截图、重试、失败候选与历史原生快照保留。此解释已公开，不宣称官方逐字豁免staging。

原生副本未脱敏；路径、内部账号ID与工具结果保留。未复制整个客户端DB、凭证文件或签名私钥。打包前核查不能遮蔽来源与修改依据；如需脱敏，说明具体字段和方法，并相应重新校验快照/补丁，不能悄悄改动已核对副本。
''',encoding='utf-8')
    save('delivery-notes.md',f'''# 2-submit 交付说明

本题材料整理完成范围见本目录文件；版本/联系人/冻结时间/人工和来源等空声明仍为【待补充】，详见missing-fields.md。自动事实及出处见auto-filled-facts.md。submission.json.fragment是供3-package使用的本题submitted候选对象，最终是否提交须使用team.yaml.submitted_tasks，不表示已对外提交。

独立材料验收结果为21 pass、1 fail、3 blocked，机械一致性检查通过，正式提交材料尚未就绪。R04历史范围控制失误无法由后续修正撤销，继续如实列fail；双ID/人工声明/团队冻结等阻断见validation/independent-review-r1.md。不能把完整补丁重建成功写成材料全部合规。

完整工程范围：{summary}。请将traces/code-snapshot/project/原样复制到包根tasks/cml-spec1/project/，将本目录build.md、trace-index.md、human-changes.md、changes/、logs/放到tasks/cml-spec1/，traces/放到包根traces/cml-spec1/。validation/、两份清单与本交付说明应作为本题辅助材料保留，solution.fragment.md及sources.fragment.md由3-package汇总；不在此阶段写团队根文件或生成ZIP。

原“生产冻结”688文件的实际集合为677个tracked基线/修改文件加11个新增feature/main文件；其中包含115个基线tracked测试文件，排除的是新增hypium_tests及过程材料。该输入冻结与本次完整11951文件快照分开标识，不能用688文件清单代替完整提交差异。

完整补丁校验状态：{patch.get('pass','【待补充】')}。实际命令、stdout/stderr与退出码在validation/patch-commands.json；基线独立clone/checkout，git apply --check --binary和真实apply均exit0后，逐一对比完整文件集合/摘要；差异条目见validation/patch-validation.json。最终补丁SHA-256 `{patch.get('patch_sha256','【待补充】')}`。比对范围含新增/修改/删除、过程文件和二进制，并非仅生产目录。独立复核见validation/independent-review-r1.md/.json（若尚未生成，不能据此声称独立通过）。

本阶段只核对已有构建和自测日志，未重新构建或操作设备；原263份日志均有sha清单。指定官方reports原文不存在，已用真实本地准备输出披露；不能补跑一条新命令冒充缺失的历史日志。缺少的提供者声明和Comate特有字段仍待补充/确认，不将结构校验或本地功能通过等同于官方材料核验或官方评分。

本轮历史采集/临时clone的范围失误及修正如实记在traces/README.md、validation/material-retry-history.json和原生会话；旧clone未作为任何上游历史参考，不进入包。本轮材料校验的最终事实只引用scoped clone重做的检查。

补丁为精确字节重建而在临时clone设置core.autocrlf=false；现有工程的CRLF与Git基线LF差异也如实保留。git apply输出的trailing-whitespace警告原文保留，退出码为0，没有用whitespace修复选项改写工程字节。它不代表新增编译诊断；业务语义改动清单与原git状态见工程审计报告。

本题专用模拟器仍持续写traces/baseline-analysis/emulator-instances/CmlSpec1Baseline/Log/。这些运行日志以复制后的不可变文件摘要为交付版本，manifest记录逐文件捕获时段、复制前后和实际副本摘要；patch必须与副本逐字节一致。live随后新增/轮转/写入的差异逐项记录在patch-validation.json，不泛化到其他traces、logs/、workflow、测试或生产。当前仍在写的压缩流可能仅含截至采集边界的字节，不能冒称它是已关闭的完整日志流；历史失败原始记录仍保留。所有非该精确runtime路径的工程文件、688生产冻结及HAP均要求无漂移。

staging自包含冲突按公开工程快照边界处理：.comate/submission-draft整体属于项目旁的材料区，不再递归进入project；其余.comate过程文件仍保留。3-package若重新从live工作区复制、重导出后修改工程内历史轨迹或改变任何工程文件，必须重新生成diff并重新做逐文件比对，不能继续使用本次差异。

精确搬运清单见packaging-map.json；.validation/绝不可打包，包含被自动审批拒绝删除的旧临时clone。工具脚本属于材料复现辅助，后续打包如需保留应作为辅助工具单独映射，不递归复制临时目录。
''')
    # These two fragments are destined for package-root prose, so qualify task-local paths.
    for name in ('sources.fragment.md','solution.fragment.md'):
        p=OUT/name;text=p.read_text('utf-8')
        for prefix in ('project/','logs/','changes/','validation/'):
            text=text.replace(prefix,'tasks/cml-spec1/'+prefix)
        text=text.replace('见human-changes.md','见tasks/cml-spec1/human-changes.md')
        text=text.replace('见build.md','见tasks/cml-spec1/build.md')
        text=text.replace('见sources.fragment.md','见根sources.md的cml-spec1来源条目')
        text=text.replace('system-config快照','tasks/cml-spec1/project/system-config/快照')
        text=text.replace('trace-index及traces README','tasks/cml-spec1/trace-index.md及traces/cml-spec1/README.md')
        p.write_text(text,encoding='utf-8')
    print('Rendered task material files and traces README; official trace-index fields:',i)

if __name__=='__main__':main()
