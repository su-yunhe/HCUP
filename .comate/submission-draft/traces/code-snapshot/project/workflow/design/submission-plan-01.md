# cml-spec7 单题材料方案 01

方案版本：`submission-plan-01`。角色：`harmony_design`。真实 `CODEX_THREAD_ID=01a1590f-cd99-7df0-9608-5c9d6cece03f`。本角色已读取 `D:/HarmonyDev/codex/agents/harmony_design.toml`，仅新增本方案，不修改业务、资源、配置、测试、公共目录、工作流状态或草案文件，不创建子 Agent。

## 1. 批准范围与交付结论

依据 `spec-harness/2-submit.md` 和 `workflow/requirements/submission-review-01.md` 的 S01–S22，继续制作如实披露的单题材料草案。当前真实本地验收为 **38 pass、3 blocked（B9/B10/B11）**；构建、安装、冷启动及已实现范围回归通过，真实微信、QQ、支付宝授权仍未完成。该条数不是官方 F-point 数量或官方成绩。材料整理不使 `1-do` 的全完成前置成立，不调整原需求或测试，也不把本题写成已正式提交。

所有材料实现产出位于 `.comate/submission-draft/`；本方案自身属于本题过程文件。团队根级 `solution.md`、`sources.md`、`README.md`、`system-config/` 汇总、最终题目选择、正式冻结、ZIP、上传及邮件由 `3-package` 处理。本阶段不变更它们。

工程根就是 `D:/HCUP/cml-spec7`，不新建工作用 `project/`。下文的 `project/` 专指未来成果包的 `tasks/cml-spec7/project/`。

## 2. 已读证据与现状

| 证据 | 已核实内容 |
| --- | --- |
| `spec/metadata.json`、本题 `git status` | 基线和当前 HEAD 均为 `75fd0066a7fc0c1e8cedb6218df081f86d307f45`；有生产修改及大量未跟踪过程目录，普通 `git diff BASE` 会漏新增文件 |
| `workflow/delivery-01.md`、`workflow/verification/final-verification-03.md`、草案 `facts.json` | 38/3、三项外部授权阻断、有效/无效测试轮次、源码/HAP 指纹与原始缺口 |
| `AppScope/app.json5`、`entry/src/main/module.json5` | `bundleName=com.joker.coolmall`，入口 `EntryAbility`，模块 `entry` |
| 根依赖/锁文件、`build-profile.json5`、`logs/verification-navigation-smoke-03/build.json` | HarmonyOS 6.0.1(21) 目标、实际 clean assembleHap 命令与退出码 0；不需要材料阶段重新构建 |
| 草案 `facts.json` | HAP 为 `entry/build/default/outputs/default/entry-default-unsigned.hap`，17,068,002 bytes，SHA-256 `8aaa5de48b5664b92210fad7ffcddf9abbcebbb92e52faf7f5359bbeb3611863`；它是构建产物，不因有摘要而自动纳入源码范围 |
| 草案 `logs-copy-manifest.json` | 读取时复制 3,526 文件、52,587,929 bytes；显式排除 6 个生成磁盘、913,638,912 bytes；这些是当时读取值，不是未来最终统计 |
| 草案 `traces/session-metadata.json`、`traces/discovery.json` | 初次读取有 12 个原生会话，逐会话解析无错误；材料阶段会话仍活动，须按实际截止点再导出 |
| 草案 `taskbook-versions.json` | common 实际 Git 根为 `D:/HCUP`；父仓库 HEAD 不单独证明四任务书内容，已有四份内容 SHA-256；本题 `spec/history/` 无文件 |
| 指定官方准备日志路径 | `D:/SWE-OpenHarmony/reports/build-baselines/cml-spec7.log` 缺失；本地准备日志/登记只能作为不同证据，不能冒充该原件 |
| `spec/submit-input.yaml`、`../common/spec-harness/team.yaml` | 已提供 task/team/stage；人工声明、版本、联系、冻结时间、成员等多项为空，必须保留 `【待补充】` |
| `workflow/provider-research-01.md`、`workflow/implementation/third-party-setup.md` | 已有官方通用 SDK/文档检索与失败记录；下载 HAR 不等于集成，不能把它们写成已完成三方接入 |

本次设计依据的内容指纹：

| 文件 | SHA-256 |
| --- | --- |
| `spec-harness/2-submit.md` | `43455fc9ef3c6d0ddbcf0dc101201796ebec865e214929f3137b1bb4036895f9` |
| `workflow/requirements/submission-review-01.md` | `e074a39dec29e83adab0884a03f3e74c6e553ce62241904a2fa5761c33c07a78` |
| 草案 `tools/export_evidence.py`（本次审查版本） | `670fd5218711b1d629e2173d825de577c80404495aba28d13e44e82a1d2d55af` |
| 草案 `facts.json`（读取版本） | `a308fdbb615dbc8ce3bbff4645f934bc8428e281a4cb9b27561d9c56e3bc5714` |
| 草案 `taskbook-versions.json`（读取版本） | `4bdb17019eaee470b4d2a639c7f45bce69ac599dfe8ad55f76ccfac9ea3be61c` |

## 3. 文件范围、数据流与版本边界

以一个不可变文件集合 **P** 定义本阶段的拟交付工程版本。先定范围、复制源码快照，再从快照生成 diff，验证程序也只使用同一 P。数据流为：本题基线/当前真实文件 → P 清单与字节快照 → 完整二进制补丁 → 独立基线 clone 应用 → 文件集合及摘要双向比对。不能从会持续变化的工作区分别生成各份材料，再假定它们相同。

### 3.1 纳入规则

P 至少取以下并集，再减去 3.2 的明确排除项：

1. 官方基线全部跟踪文件在当前工作树的真实存在状态；基线存在、当前已删除的路径单列删除，不能因简单枚举当前磁盘而漏删。
2. 本题当前全部真实新增文件，包括 `spec/`、`inputs/`、`spec-harness/`、`hypium_tests/`、`test-harness/`、`workflow/`、`logs/`、`traces/`、既有 `system-config/` 和其余真实 `.comate/` 过程文件。不能仅纳入 14 个生产变更文件。
3. 被 Git 忽略但确属交付配置/过程证据的文件须显式审定，例如本题根 `AGENTS.md` 可以作为访问约束纳入；`.gitignore` 仅是发现候选的工具，不能替代成果范围规则。反之，不能因为 `logs/` 未被忽略，就纳入模拟器磁盘。

可用 `git ls-tree -r -z BASE`、`git ls-files -z`、`git ls-files --others --exclude-standard -z` 建立初始候选，再补显式纳入项。路径统一为根相对 `/` 格式，拒绝绝对路径、`..`、大小写碰撞或越出根的链接；如存在符号链接/特殊模式，显式保存类型、目标和 Git mode，不能默默跟随到允许范围之外。

### 3.2 排除规则

| 范围 | 理由与处理 |
| --- | --- |
| `.git` 文件/目录 | 版本库内部状态不作为工程文件；基线身份由元数据与导出证据保留 |
| **整个 `.comate/submission-draft/`** | 这些材料稍后映射到 `tasks/cml-spec7/` 的同级材料位置；不再嵌套复制进 `project/`，从而消除 final.diff 包含自身及草案副本的递归 |
| `.hvigor/`、`**/build/`、`oh_modules/`、`node_modules/`、生成的 `BuildProfile.ets` | 可再生依赖/构建输出；原始构建日志、依赖及锁文件保留；若某路径本属基线跟踪文件，先核实而非直接按名称删去基线内容 |
| `__pycache__/`、`.pyc`、`.pyo`、已识别的临时锁、空的临时输出目录、旧 ZIP | 可再生或无交付用途的临时项；按实际路径列清单，不能延伸为排除任意日志或截图 |
| 已登记的 6 个 `logs/verification-emulator/instances/CmlSpec7_Layout/*img*` 磁盘 | 仅从复制范围排除；不删除原件，不绕过已有清理审批拒绝；保留实例小配置、命令、失败及拒绝 JSON |
| 本机私钥、账号凭据、无关私人会话 | 不复制；如实际有脱敏，逐项记载字段、理由、原始/导出摘要及影响，不笼统声称“无脱敏” |

不得按 `logs/**`、`traces/**`、所有二进制、全部 `.comate/` 或 `workflow/**` 整体排除。排除清单须给相对路径、原因；对实际排除文件可记录 bytes/SHA-256，原文件保留。HAP 默认作为构建输出不放 P，其路径、大小和摘要在材料中保留；若后续决定额外交付安装包，须放材料/产物位置并另记映射，不改变 P 的定义。

### 3.3 清单与快照接口

建议产物：`changes/project-manifest.json`、`changes/excluded-files.json`、`changes/binary-files.json`、`traces/code-snapshot/`。实施可沿用等价名称，但交接必须明确每个接口的实际位置。

`project-manifest.json` 至少含：task_id、base_commit、material_snapshot_at、相对范围根、纳入/排除规则版本、每项 `path/type/mode/bytes/sha256`、相对基线状态（added/modified/deleted/unchanged）、删除清单、文件数与总大小、稳定清单 SHA-256、源码快照位置。对 sorted path/bytes/SHA-256 的明确 UTF-8 序列计算 snapshot ID；记录精确算法，不把生产输入聚合值、14 文件聚合值或 HEAD 当作完整 P 的摘要。

清单、补丁、验证报告和快照容器都在 P 外。`workflow/state.json` 如被纳入 P，必须在切片时保存真实字节；随后主 Agent 写入材料完成登记属于切片之后的状态，不可再宣称实时工作树与该切片完全一致。不能把 P 自身摘要写进将被 P 覆盖的 state 后又重算同一摘要。未来正式打包如需更晚状态，按新切片重导，不把本阶段时间冒充人工正式冻结时间。

## 4. 草案产物及包内映射

以下是给 `3-package` 的拟定映射，当前不代表 ZIP 已存在。

| 草案源（相对 `.comate/submission-draft/`） | 未来包内位置 | 内容契约 |
| --- | --- | --- |
| `traces/code-snapshot/` 中 P 的内容 | `tasks/cml-spec7/project/` | 唯一工程复制源，逐字节与 P 一致；绝不从包含草案的实时根目录递归复制 |
| `changes/final.diff` | `tasks/cml-spec7/changes/final.diff` | 从官方基线精确重建 P，新增/修改/删除及二进制齐全 |
| `build.md` | `tasks/cml-spec7/build.md` | 可在交付工程根执行的依赖、构建、安装、启动及限制说明 |
| `trace-index.md` | `tasks/cml-spec7/trace-index.md` | 保留官方模板全部 24 个字段，链接原生记录、人工缺项、版本及验证 |
| `traces/`、`logs/`、清单及校验记录 | `tasks/cml-spec7/` 下同名相对位置 | 保留实际相对结构；若打包去重快照副本，须同步重写并校验全部引用 |
| `sources.fragment.md` | 由 `3-package` 汇总进根 `sources.md` | 官方基线声明、已有额外来源事实、人工 extra_sources 待补充，不代签“无来源” |
| `solution.fragment.md` | 由 `3-package` 汇总进根 `solution.md` | 38/3、未完成/已知限制、AI环节、缺失、有效轮次和材料切片边界 |
| `submission.json.fragment` | 由 `3-package` 合并到根 `submission.json` 的本题条目 | 仅本题，不复制其他题条目；草案默认 status=`not_completed` |
| 人工待补清单、自动事实清单、交付说明 | `tasks/cml-spec7/` 下相应文件 | 两份清单可在交付说明内分区，也可各自成文件；最终回复要能够直接定位 |

JSON 本题候选路径固定为 `tasks/cml-spec7/project/`、`tasks/cml-spec7/build.md`、`tasks/cml-spec7/trace-index.md`，均为成果包内相对路径并用 `/`，后两项必须指向文件。`status=not_completed` 是未作正式提交选择的草案默认，不表示规则禁止提交部分完成工程。最终 `submitted` 由 `3-package` 依据真实选择统一填写。

## 5. 材料字段与证据要求

### 5.1 build.md

从现有配置与实际成功日志提取依赖安装方式、工具/SDK需求、构建命令、产物相对路径、应用标识、安装和启动命令及初始化条件。实际构建命令参数为：

```text
hvigorw --mode module -p product=default -p module=entry@default -p buildMode=debug clean assembleHap --no-daemon --no-incremental
```

说明使用本机安装工具的 PATH/环境配置方式，命令不依赖 `D:/HarmonyDev`、`C:/Users/22580` 或本机未交付脚本。原始日志可保留真实绝对路径；便携指南不能把 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1` 写成收件人必须拥有的唯一前置。当前若需执行任何新构建/设备命令，执行者仍必须先加载该本地环境脚本。本阶段通过已有证据即可完成材料，无须新安装/启动来填字段。

列明未配置发布签名和三方真实身份/回调/换票条件；不虚构 appId、签名密钥、后端契约或将支付当登录。涉及账号/手机号目标页的范围按本题原需求和已验证导航披露，不外推认证功能。缺少可核实的依赖安装或环境版本记录时列缺口与应补的真实命令，不能编造“已执行”。

### 5.2 trace-index.md 与原生轨迹

逐字段保留官方模板的 24 项。对主/子会话保存 session_meta 的原生线程 ID、真实父子关系、角色/昵称、CLI originator/version、逐 turn_context 模型/effort、原生 token 字段、源路径/哈希/bytes、导出时刻及最终完整事件的行号/ordinal/时间。不同 ID 字段不可互换：子会话 `payload.id` 是自身线程，`payload.session_id` 可能是父会话。

Comate 未发现时写“不适用：本题实际使用 Codex”，并保留要求的字段位置；不能造 Comate `sessionUuid` 或扩展版本。若 `session_index.jsonl` 按同 ID 有真实侧边栏行，可据该行说明与 native ID 的关联；没找到行时写 `【待补充：未核实独立 IDE ID】`，不能仅因 ID 同形宣称存在两个独立 ID。桌面 AppX 版本与 CLI 版本分开，未知模型内部版本不推断。

原生 JSONL、过滤后的索引行与 Markdown 均保留。Markdown 注明“机械转换的可读副本”，以原始行定位，不能称 IDE 手工导出；人工 `md_export_dir` 仍待补充。JSONL 失败/重试/返回值不删；若活动文件末尾是不完整行，记录原始 bytes/hash、解析边界和截断原因，可另生成完整事件切片，不静默修复原始记录。

token 只报告明确计量口径和截止事件：原生 `token_count.info.total_token_usage` 与 `token_usage_record` 保持各自语义，累计事件不逐行相加，不重复累加历史快照，不把缓存输入再算一次，不推算 Comate tokenUsage。工具调用统计区分 native function/custom call 和 `functions.exec` 脚本中观察到的嵌套工具名称；字符串出现不是调用成功或 Skill 实际生效的充分证据。Skill/规则应链接真实读取调用、结果和本题已保存的配置快照。

先按工程绝对路径与 task_id 两个维度独立搜索候选，再依据真实 cwd、父子链和本题事件选择。保留排除的初始化总览 ID `01a13fc4-2611-7761-a580-1283e0c70541` 及原因，不读取或导出其正文，也不打包整个客户端数据库。材料新主/子会话同样加入。测试设计会话 cwd 不同而确属本题时应审定关联范围；不能只凭标题或目录名批量导出。

### 5.3 失败、来源、人工与缺失

保留原始手机测试 error、滚动方向助手修正、旧布局与导航回归、02b 失效证据、大屏方向被重置的 800vp 原轮、真实 1200vp 补测、SDK查询失败、初次 hdc 捕获缺口及清理审批拒绝。明确哪些证据可证明最终版本，哪些是历史失败；旧轮名称不能代替真实尺寸/源码/HAP校验。

来源片段只复述已有本题来源记录和真实检索事实，包括官方通用文档/HAR的实际获取结果及失败。SVG资源是文本，也要纳入 diff；二进制清单不能替代实际字节。基线同路径同摘要的资源标“随包基线同源”；新增/修改资源依本题记录登记来源，无法确定的写待补，不按扩展名猜来源。

人工空字段保留：`human_edits`、`known_issues`、`extra_sources`、`md_export_dir`；团队 `version/contact/freeze_time/members[].name/members[].work/source_guard`。可以另写已观察到的限制、AI角色和实际访问约束，不能代填“无人工直接修改代码”“无额外来源”“未配置”或从本机用户名推断成员。`submitted_tasks/attempted_not_submitted/zip_out` 留给 `3-package`，无需阻止当前整理。

缺失明确列出：指定官方准备原日志、初始独立 hdc stdout 的当时捕获缺口、未核实的独立 IDE ID及不存在的 Comate体系、活动会话截止后的未来事件、正式冻结时间和三方外部条件。当地日志和后补实验只能分别说明，不能宣称补回历史原件。脱敏按实际检查填写，不因自动导出未报错就默认“无敏感信息/无脱敏”。

## 6. 完整补丁生成程序

1. 主 Agent 收齐本轮需求、方案、材料交接，先保存 P 内计划纳入的记录。做生产/资源/配置/测试前后指纹对比，确认本阶段未改；检查 tracked `BuildProfile.ets` 等噪声，不能顺带修业务。
2. 输出有限范围规则，复制 P 到草案 `traces/code-snapshot/`，从副本重新计算清单，与源端捕获的 path/bytes/SHA-256 比较；捕获期间变化则该轮失败并重采。以清单摘要表示本阶段完整源码版本，HEAD仍为基线不能充当最终版本号。
3. 仅在草案下唯一临时目录，从**本题本地仓库** clone 基线，checkout metadata 的 base_commit；不访问来源项目修复或题包禁止目录。保存 clone/checkout 命令及退出码。配置临时 clone 的 `core.autocrlf=false`，检查 `.gitattributes`/过滤器，避免补丁隐式改换行。所有配置和索引仅在临时 clone 生效，不改本题原 index/HEAD/全局配置。
4. 依据 P 删除临时 clone 中已不再交付的基线路径，再按相对路径覆盖全部 P；所有递归删除/移动先验证绝对目标落在本轮草案临时目录内，原工程不删除。保留本题原始日志及磁盘。
5. 在该临时 clone 用 `git add -f -A -- .` 收录新增、修改、删除；`-f` 仅用于已经审定的 P 副本，不能对真实根目录直接强制添加缓存。生成 `git diff --cached --binary --full-index --no-ext-diff --no-renames BASE -- .` 的原始 stdout bytes，存为 `changes/final.diff`。不经可能变更编码/换行的文本管道；检查命令返回码。
6. 从同一变更集得到新增/修改/删除路径及 binary numstat 识别，生成二进制文件清单。列实际资源 path/bytes/SHA-256、基线存在/同源性及来源证据；不能把 SVG 当 binary 的唯一依据，也不能省去基线自带的实际资源。
7. patch/check 报告和 clear-scope 声明都在 P 外，记录 snapshot ID、patch bytes/SHA-256、base_commit、生成工具版本与本轮临时路径映射。临时目录不由打包阶段复制进正式材料。

## 7. 独立验证程序与可判定标准

由验证角色维护独立入口（建议草案 `tools/verify_submission.py`）及报告；不要导入导出脚本的选择函数后自证同一逻辑。脚本只读本题/草案，允许在自己的草案临时 clone 写文件，不执行构建、设备操作或业务测试，不改源文件。

| 核验 | 独立操作与通过标准 |
| --- | --- |
| 阶段范围 | 与材料开始指纹比较生产/资源/配置/测试逐项 hash，不发生变化；`git diff --check` 通过；真实 tracked 构建噪声为0 |
| P 完整性 | 直接用本题基线树/当前候选重新审阅纳入与排除规则，核对所有未跟踪目录已处理；发现基线跟踪路径被通配排除必须解释；清单路径唯一、安全且 `/` 规范 |
| 快照 | 独立遍历 `traces/code-snapshot/`，集合、bytes、SHA-256及类型/mode与 P 完全相等；既不能缺文件也不能多文件；删除项不存在 |
| 补丁可应用 | 新建**第二个**本题本地基线 clone，checkout确切base；先 `git apply --check --binary final.diff` 返回0，再实际 `git apply --binary final.diff` 返回0；不能复用生成补丁的已覆盖目录 |
| 补丁内容 | 应用后除 `.git` 的全部文件集合与 P 完全相同，每项 bytes/SHA-256和支持的mode一致；删除项全不存在，二进制逐字节一致。不能只对14业务文件抽查或只验证patch语法 |
| 变更映射 | 独立比较基线与 P，得到 A/M/D；与补丁变更路径双向一致。diff 不含草案自身、临时目录、缓存；`project/` 的每个文件均由基线或patch重建 |
| 二进制 | 逐项核对清单与实际资源大小/hash/来源；核实基线同源声明；图片/HAR等原始证据不能因binary而遗漏 |
| 便携构建说明 | 覆盖依赖、构建、安装、启动、标识、初始化与限制；所有引用的工程/脚本路径会随包交付或明确为公开工具；指南无参赛机私有绝对路径 |
| 记录索引 | 与官方模板逐字段比较，不删字段；引用文件存在。native逐行可解析或明确记录截断，thread ID与header/父子链一致，Markdown标注派生性质，工具返回与失败保留 |
| 原始证据复制 | 对 logs-copy-manifest 的所有 included/excluded 项独立重算；复制项hash对应原文件，排除仅已审定cache；前后失败原件均仍存在；活动源变化按切片声明处理 |
| JSON 与映射 | 片段可解析、只有cml-spec7；status为草案默认并有说明；三个路径 `/` 且是包内相对路径，后两项文件；在模拟未来任务目录中验证映射，不要求现在创建ZIP |
| 真实性与缺项 | 38/3、非官方成绩、原始缺口、Comate不适用、人工待补、正式冻结未定均可见；两个交接清单逐字段一致；未经输入的“无”或示例值判失败 |

独立报告建议写 `validation/submission-check.json` 与可读摘要，记录实际命令、退出码、范围ID、patch hash、比较计数/差异、检查时间和未消除项。独立验证成功证明“当前材料切片与补丁一致”，不证明 B9–B11 完成、官方准备日志存在或材料已经正式合格提交。

## 8. 导出脚本审查与最小调整

审查对象是第2节哈希对应的草案 `tools/export_evidence.py`，不是已执行的独立验证。初版仅从 workflow 登记表选会话、只统计 function_call，并把无sidebar行推定为子Agent；主 Agent 的当前版本已补独立工程路径/题号 `rg` 查询、原生 custom_tool_call、真实父子字段、token_usage_record及较准确的ID缺失文字。这些调整只涉及材料派生逻辑。

剩余最小建议：

本方案落盘时，主 Agent 回报已修正下列1/2项的异cwd父子检查和sidebar union；此处保留审查依据，最终以独立验证结果为准，不将其继续列为已知未修复故障。主 Agent 已采用本方案核心并新增草案 `tools/freeze_patch.py`，报告保留原始CRLF字节、单列EOL-only差异且临时clone在checkout前配置`autocrlf=false`；本角色未代替验证角色运行该脚本。

1. 当前约68行允许父会话关系发现异目录候选，而约103行仍一律拒绝 `cwd!=ROOT`。两处规则应一致；本次已核验12会话均同根，尚无实际失败。若发现本题异目录测试会话，依据真实父子/任务范围批准导出；否则记录当前仅支持同根，不伪称覆盖所有异目录候选。多级父子发现若依赖遍历顺序，使用已证实父子闭包再选择。
2. sidebar关联约141行只从 `matched_task` 取值，可改为 `matched_task+matched_root` 按真实id去重；若侧边栏条目标题无题号但ID已选，不应仅因标题不匹配而漏掉其真实索引行。未知项继续留待补。
3. native工具计数与 exec脚本中 `tools.*` 出现分开：前者为实际可见调用类型，后者只能称嵌套工具观察。Skill关键词出现次数不能代替已执行读取/生效证据。
4. 为每个导出文件增加 `last_complete_line/ordinal/timestamp`（缺字段则明确空），并记录源在读取开始/结束的size/hash或复制切片边界。活动源允许后续增长，但已导出副本必须稳定且可解析；临末partial行如实登记，不静默丢失。
5. 重跑导出时核对旧输出残留：目标native/Markdown集合要等于本次所选集合；日志副本集合等于included清单，过期额外副本不能被无清单地带入包。对新增候选/无法解析行/缺原件显式失败或写gap，不能只输出成功计数。
6. 此脚本目前不负责 P/patch/二进制/clone验证，不能把“导出成功”当“完整diff可应用”。这些按第6/7节另做，且不需要重新修改业务。

## 9. 实施顺序、覆盖与回退

实施顺序为：确认需求复审 → 保存各角色过程文档及生产前指纹 → 完成事实/轨迹/日志导出与字段说明 → 固定P切片/范围 → 生成快照与完整patch → 材料正文和JSON映射引用该P → 独立clone/apply及全部材料校验 → 交付两份清单。保持快照之外的材料可以更新；P内文件如变更必须重新生成P、patch和相关校验，不能只修改清单摘要。

| 需求 | 本方案覆盖 |
| --- | --- |
| S01–S03 | 第1/2/5节：范围、38/3、真实来源和空字段 |
| S04–S07 | 第3/6/7节：完整P、A/M/D、binary、缓存及独立apply |
| S08–S09 | 第4/5/7节：便携build、完整官方索引与包内映射 |
| S10–S14 | 第5/7/8节：双维检索、原生/Markdown、失败、ID、模型/token/Skill/任务书 |
| S15–S20 | 第4/5/7节：来源、部分完成、JSON、日志、人工声明及缺失/脱敏 |
| S21–S22 | 第3/4/7/9节：两份清单、切片与正式冻结分离、对应同一P |

失败归因：若 P 包含草案自身或其摘要、选择规则遗漏真实过程文件、跨目录会话条件矛盾造成漏导，是方案/范围缺陷，先修范围约定再重导；若已有明确P却patch漏untracked、binary未加、错误复用生成目录做验证、hash对不上，是实施偏离，只修材料脚本/输出并重跑对应检查。资料空字段、原始日志缺失、三方授权条件不齐属于已披露缺口，不能靠改材料变为通过，也不要求回业务实现。

权衡：完整过程文件会使快照及binary patch大于仅业务diff，但这是可追溯性和一一对应所需；只排除确认可再生缓存可控制体积。保留原失败并标有效范围比删除旧轮更便于核验。以清单摘要表达未提交工作树避免虚构最终commit；材料切片不冒充正式freeze避免对未来会话做不可能的完整性声明。

未解决项：人工输入与最终提交选择/冻结时间；指定官方准备原日志与初始hdc原捕获缺口；未核实的独立IDE ID；B9–B11合法外部授权及服务端条件；本方案时点之后的材料会话/状态写入。它们均须在最终草案中可见，不阻止完成本阶段已经授权的整理和验证。
