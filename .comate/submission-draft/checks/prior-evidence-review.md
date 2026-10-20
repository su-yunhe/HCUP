# vg-spec9 既有验收证据独立复核（2-submit）

- 复核角色：`/root/submission_verification`；原生会话 ID（只读环境变量 `CODEX_THREAD_ID`）：`01a144bd-8665-7712-93a5-de24724c416c`。
- 复核时间：2026-10-16 20:49（北京时间，静态材料复核）。
- 写入范围：仅本报告；未修改生产源码、资源、配置、Spec、测试脚本或 workflow 状态，未执行构建、安装、设备命令或测试 runner。
- 下文“pass”表示既有本地实测记录得到本轮静态复核支持，**不表示本轮重新运行通过，也不表示官方成绩**。

## 结论

既有记录支持 **12 个唯一用例最终 pass，0 fail/error/skip**。三个有效轮次实际共执行 13 次用例，其中 T10 重复执行，最终采用补测结果；不能描述为某次完整运行一次通过 12 项。首次 T1 的脚本参数错误、主机夹具自检失败和旧 T10 的首闸风险均有保留，未计入最终通过数。

当前 HAP、251 项运行期源码/资源清单和五份冻结生产文件均与验收对应。未发现要求退回生产编码的证据。正式提交材料仍需要团队与人工声明等用户事实，不能据记录缺失推断为“无”。

## 用例、日志和重试核对

| 轮次（`traces/implementation-validation/` 下） | 原始结果 | runner 退出码 | 最终采用范围 |
| --- | --- | --- | --- |
| `round02-t1` | T1 error；`invalid direction up, expect [RIGHT, LEFT, UP, DOWN]` | 1 | 历史失败，不计通过 |
| `round02-t1-retry` | 1 pass；82.430 秒 | 0 | T1 |
| `round02-regression` | 9 pass；1200.061 秒 | 0 | T2—T9；旧 T10 另保留 |
| `round02-supplement` | 3 pass；295.471 秒 | 0 | T10、T11、T12 |

出处：各轮 `selftest.json`、`selftest-exit.txt`、`selftest-raw.log`、`Run-command.log`。本轮逐项比对 `logs/selftest.json`：12 个名称全部唯一，每项在其 `raw_report` 中恰有一个相同名称且 outcome 相同的结果，引用问题数为 0；与 `workflow/acceptance/final-audit.json` 一致。汇总日志的三段 `Ran 1/9/3 tests`、`OK` 与原始报告相符。`logs/selftest.json` 的 counts 只显式列出 `pass:12`；其他计数为零来自逐项检查，不是 JSON 存在这些字段。

`logs/build.log` 与 `round02-t1/build-raw.log` SHA256 完全相同。原构建命令是 `hvigorw clean assembleHap --mode module -p product=default -p buildMode=debug --no-daemon`，`build-exit.txt=0`，原日志末尾为 `BUILD SUCCESSFUL in 16 s 448 ms`。这是既有构建记录，本轮未运行该命令。

`logs/install.log` 是三轮安装退出码的汇总；完整原命令与安装前 HAP 摘要在各轮 `Run-command.log`。三个有效轮均为 `hdc -t 127.0.0.1:5555 install -r .../entry-default-unsigned.hap`、`INSTALL_EXIT=0`，随后 runner，`ACTION_EXIT=0`。

| 汇总日志 | 本轮重新计算 SHA256，与 `logs/verification-log-manifest.json` 一致 |
| --- | --- |
| `logs/build.log` | `52cc69fd05e50a9a8619f5587ecbecf86004b10786eecf8200381e5481f828de` |
| `logs/install.log` | `8de425d665b940d503b82f2fd4de1dd731ecfc6f74f9e6be1a68e249b6e7b29a` |
| `logs/selftest.log` | `f9d281c39f06513af2c9cd5cea9078a1ac5eda6679031bae2b440aed642451f2` |
| `logs/selftest.json` | `1949bf41d9f30732121cb1fb707b86be87464883a7502081526fde185f113b73` |

历史问题归属与证据强度：

1. 首次 T1 在同步点击前调用小写 swipe 方向而报错。原 JSON、异常栈和退出 1 保留；修正测试方向后重新安装相同 HAP 重试。明确的测试参数错误，证据强；不据此判断生产功能失败。
2. 嵌套目录夹具自检 `fixture-tree-selfcheck.log` 退出 1；`fixture-tree-selfcheck-corrected.log` 退出 0。既有报告归因为父目录 `.keep` 路径归属缺失；属于主机夹具准备阶段，未充当设备成功证据。
3. 旧 T10 使用首闸加延迟，回归轮最大请求时间 24.008025 秒，存在越过客户端读取超时的风险。修正后补测最大请求时间 18.012239 秒，T10 最终采用补测成功记录。不得删除旧轮或把旧轮当作最终 T10 唯一依据。

## 冻结源码、测试源和 HAP 对应

- 批准 Spec 当前 SHA256：`c6236994e253c6de9f6decd99d7c0637620027ac16ce3699154796cba7a5edbf`；metadata：`496950d171e032fe6f10cf76fd485341f4f293b6f162857d60a46bd98756f660`。均与主 Agent 指定值及状态一致。
- 当前 `entry/build/default/outputs/default/entry-default-unsigned.hap` SHA256 为 `b367da84359ad19ba9fad5e808f864fe06c10280850332da1c11615a8efe70b6`，与最终审计、状态记录及三个有效轮安装前摘要一致。
- `workflow/implementation/frozen-source-01.json` 中五份生产文件逐一与当前文件重新计算比较：5/5 一致，差异 0。
- 四轮各自 before/after、command-before/command-after 清单均为同一 SHA256：`e7389484845bf9abf6ea6571434e7cc1995def6e363d87c359adafc64bebd575`。当前逐文件校验 251 项，缺失/内容变更 0；按相同枚举规则另查新增/删除路径，路径差异 0。
- 该清单范围见 `hypium_tests/evidence.py:source_fingerprint()`：`entry/src/`、`AppScope/`，以及工程根 `.json5/.ts/.ets` 文件。它不是整个仓库所有文件的摘要；例如目录内其他构建配置、依赖目录和验证脚本不应据此宣称全部冻结。提交工程及包级完整性需另做 manifest。

| 测试材料 | SHA256 | 对应关系 |
| --- | --- | --- |
| 旧测试源 | `60e899d481b3f90cb0a9a4a0f0e491cbf5f5ce74ba9b16459e6b1c62ebbaff97` | retry、regression 的 `test-source-used.py` |
| 当前测试源 | `78c9aaa7fa8e368b5a59869d064bd26db665127d2d240427397e9f0d0a76c726` | 当前 `hypium_tests/test_webdav_loading.py` 与 supplement 的 `test-source-used.py` 相同 |
| 旧夹具源 | `9a56252949c15b9b952fc34031afbaf24872af9287e40d5a6af94952162f5f8b` | retry、regression 的 `fixture-source-used.py`；**事后按单行首闸修改复原的历史文本** |
| 当前夹具源 | `95fe3371fba612a99a3881de08831adec737eae7ea09ca3fa38b9549dd6739d8` | 当前 `hypium_tests/webdav_fixture.py`；见 `round02-test-versions.json` |

旧夹具的复原性质已在 `round02-test-versions.json` 和原验证报告明确，不能包装为当时即时采集的源码快照。各轮实际结果必须保留其版本对应关系，不能写成“12 项全部由当前测试源一次执行”。

## 可观察需求的证据复核

本轮对三个有效轮的原始 `webdav-requests.jsonl` 和 `ui-events.jsonl` 重新关联：分别有 5/78/15 条 request、同数 response；6/43/14 次 `ui_loading_sample` 全部落在至少一条已接收但尚未响应完成的真实请求窗口，非重叠采样数均为 0。该结论来自历史时间记录，不是本轮网络实测。

T1 的五条请求为 HEAD200、GET404、HEAD200、PUT201、GET404，认证匹配均 true，PUT 内容 549 字节。`business-upload-summary.json` 记录 MAC 有效，解密业务集合 words/definitions/userBooks 均为 0；本轮未重新执行解密。T11 既有 `password_spaces_verified` 事件记录精确 Basic Auth 与原密码 MAC 成功、trim 密码 MAC 失败。

本轮已打开既有 T1 `first-inflight.png` 和 T6 `after-120s.png` 作目视复核，均见忙碌页面及蓝色加载圈。对应 `.json` 均包含唯一 `id=webdav_sync_loading`、`type=LoadingProgress`、`visible=true`、`bounds=[154,1737][238,1821]`；组件身份由树证据支持，不能仅凭图片认定。截图原文件为 1308×2880，本轮查看工具缩放为 930×2048，未改写原图。

| 需求 | 静态复核判定 | 既有实测出处/行为 |
| --- | --- | --- |
| A1 | pass | T1/T4/T7/T12 正常入口及重进 |
| A2 | pass | T1 有效认证端点、实际 PUT201 与成功终态 |
| A3 | pass | T1 同步按钮点击事件及本轮独立目录 |
| A4 | pass | T1 busy 按钮与页面外观、截图/树 |
| A5 | pass | T1 实际 LoadingProgress 类型、可见性、范围 |
| A6 | pass | T1 同一手动同步按钮触发 |
| A7 | pass | T1 加载采样与活动请求重叠 |
| A8 | pass | T1 真实多阶段请求及上传载荷 |
| A9 | pass | T1 独立目录、目标端点及认证匹配 |
| A10 | pass | T1 本轮点击事件，不以保存/测试连接替代 |
| A11 | pass | T1/T6 实际可见 LoadingProgress |
| A12 | pass | T1 服务端原始接收记录 |
| A13 | pass | 测试源有“点击无新请求即失败”断言；历史实际请求存在 |
| A14 | pass | 同轮 UI/网络窗口；T6 超过旧 120 秒边界仍加载 |
| A15 | pass | T1 成功恢复、T3 终态后再触发新请求 |
| A16 | pass | T2 HTTP403 后更正、T9 连接失败后有效重试 |
| A17 | pass | T1 空业务载荷及空远端；T3 重复仍真实请求 |
| A18 | pass | T3 连续快速点击和 busy 期重复点击 |

A1—A14 为批准矩阵中的明文项，A15—A18 为合理推导；编号不等同官方评分点。详细 B1—B15 判定沿用 `workflow/verification/round-02-final-report.md` 的限定：B1/B2/B5/B6/B7/B11/B13 已测分支 pass；B3/B4/B9/B10/B12/B14/B15 只对报告列明适用或已测子项 pass，不能扩张成穷尽覆盖；B8 无分页需求，本轮 `not_run（不适用）`。取消按钮、启动确认框不存在，不虚构测试。

下列项目 `not_run`：运行中 force-stop、自动任务竞争、物理断网/DNS 等其他错误分支、首次清数据安装引导、物理设备、其他 WebDAV 产品、无关 ohosTest；以及原报告列明的终态后配置 B 新轮、返回后编辑交错、单独测试连接归因等扩展。官方隐藏评测 `not_run/不可见`，不能算 pass。

## 真实工具环境与已知限制

本题实施快照中验证会话：

`traces/native/implementation-20261016T124115Z-622cf51a/2026/10/16/rollout-2026-10-16T19-57-17-01a14492-d90e-7c23-aa1e-0deef1467f23.jsonl`

该文件当前 SHA256 与快照 manifest 一致：`f34394deac181129f37471347df26e6c5284973375c1ed5796f182f9f173bdde`。本轮只读取上述本题验证会话，没有读取禁止的两份总览会话。

- 第 341 行 `custom_tool_call_output` 含设备查询原始输出：`emulator 6.1.0.115(SP11DEVC00E115R4P11)`、API23、model=`emulator`；退出 0。不是 Pura 机型或 560 DPI 的确认。
- 第 697 行 `custom_tool_call_output` 含 Python 实读：`D:/HCUP/common/.venv/Scripts/python.exe`、Python 3.12.3、Hypium 6.1.0.210、`Windows-11-10.0.26200-SP0`。runner 原始日志亦记录 Hypium 6.1.0.210、uitest 6.0.2.3、agent 1.1.9；PowerShell transcript 为 7.6.5。
- `environment-and-static-command.log`、`preparation/python-runtime-command.log` 留有命令与退出码，但 transcript 本身未收录上述 native stdout 的值。材料应同时索引这两条原生工具返回，不能仅引用 transcript 声称它包含数值。
- 配置入口标明 DevEco 6.1.0.860/API23。环境加载消息默认 Python 位于 `D:/hongmengcup/...`，而真实验收显式使用 `D:/HCUP/common/.venv/...`；提交说明应采用实际运行路径/版本并改写为可迁移步骤，不能混为一套解释器。
- `env_warnings=[]` 是 runner 的检查字段；原始日志仍有 `tracker dependency is not ok`，构建有 756 条 `ArkTS:WARN File:` 及 unsigned/no signingConfig 警告，不能写“无告警”。`build-warning-comparison.json` 记载基线759、当前756、按文件+消息净新增0；本轮仅重数当前756。允许的 `D:/SWE-OpenHarmony/reports/build-baselines/vg-spec9.log` 不存在，本轮基线原始警告重核 `blocked（文件不可读）`，未读取其他位置替代。
- HAP unsigned，仅有本地 API23 模拟器安装与验收；官方成绩不可得。服务关闭的既有记录为 `host-service-closed.log` 的 `LISTENER_COUNT=0` 和补测末尾 `fixture_stopped`，本轮没有重新查端口。
- 旧 hdc 映射未清理；自动审批拒绝的清理命令不等于成功清理。缓存搬移记录见 `workflow/acceptance/cleanup.log`。测试保留应用数据、使用合成端点/凭据，自动同步关闭；不能声称恢复原真实密码或覆盖全新用户流程。

## 对照官方模板仍须补齐/确认的内容

只读依据：`D:/SWE-OpenHarmony/templates/README.md`、`submission-checklist.md`、`submission.json`、`solution.md`、`sources.md`、`human-changes.md`、`trace-index.md`。本轮未把草稿存在等同正式可提交。

| 项目 | 当前可据本题记录整理 | 仍缺的事实或动作 |
| --- | --- | --- |
| 清单 | 本题 ID、基线、工程/构建/索引路径 | team_id、team_name、contact、version、正式阶段确认；其他题实际状态不可推测，线上完整清单须由团队统一填写 |
| 团队/成员贡献 | AI 四角色流程及原生会话索引 | 真实成员姓名、各自实际贡献、联系与报名信息 |
| 人工记录 `human_edits` | 已有 AI 编辑/工具轨迹可引用 | 用户未提供是否人工直接改代码及具体批次；不得据此填“无人工直接修改代码” |
| 问题 `known_issues` | 本报告和既有验证报告的已知本地限制 | 用户未提供额外已知问题；不得将缺省值解释成“无已知问题” |
| 额外来源 `extra_sources` | 本题基线标识、工程既有依赖和已记录工具配置 | 未提供完整外部资料/代码/人工引入声明；不得填“无额外来源”作为事实 |
| 工程及差异 | 当前源码与 HAP 对应；冻结五文件指纹 | 完整可搬迁工程、完整基线差异（含新增/删除/二进制）、依赖及锁文件、包内资源摘要；本轮未审核最终打包工程 |
| 构建运行说明 | 原命令、应用 ID `io.qzz.weiyu`、EntryAbility、工具版本、复现说明 | 将私有绝对路径改为包内/安装步骤；需要的公共 harness 不得只指向未提交的本机路径 |
| 冻结/索引/轨迹 | 实施会话与失败重试、本轮静态复核会话 | 统一成果冻结时间和最终版本、当前提交整理会话导出、包内有效相对路径、逐条缺失/脱敏说明 |
| 成果包 | 可按官方模板生成候选材料 | 正式 ZIP 大小/SHA256/解包核验、上传权限与正式邮件信息；本轮均未执行 |

本题状态 `local_validation_complete` 只描述既有本地验证。它不能替代团队声明、正式提交审批或服务器评测结果。原始记录必须保留失败和重试，旧夹具复原、原生 stdout 补证位置、未测分支与环境限制均应进入索引。

## 本轮命令与退出码留存

所有 PowerShell 工具进程首行加载 `. 'D:/hongmengcup/Enter-HarmonyEnv.ps1'`，只执行 `Get-Content`、`rg`、`Get-FileHash`、JSON 解析和文件清单比较等静态读取。本轮完整命令和原始返回保留在原生会话 `01a144bd-8665-7712-93a5-de24724c416c`，应由主 Agent 随材料整理记录导出。

- 指纹/用例引用/日志 manifest 比较命令均退出 0：251 项无内容差异、251 路径无增删、5 冻结文件一致、12 唯一名称且原报告引用差异 0、4 日志摘要一致。
- 读取原始网络与 UI 日志并重新计算重叠的命令完成全部重叠检查；随后查询不存在的允许基线日志，该工具进程退出 1，错误为路径不存在。本轮没有将这一环境/证据读取阻断记为通过。
- 当前警告数、精确 double 请求时长和原生快照摘要的后续静态查询退出 0，修正了初次整数累加造成的时长截断显示。最终时长使用 6.006942/24.008025/18.012239 秒，不采用初次显示的 6/24/18。
- 一次辅助读取尝试了不存在的 `preparation/fixture-tree-selfcheck-retry.log`，产生非终止读取错误；随后通过限定文件列表定位真实 `fixture-tree-selfcheck-corrected.log`。未创建替代日志、未重跑夹具；不存在的路径不作证据。
- 两次图片读取只打开既有截图；没有新增设备截图或图像编辑。构建/设备/runner 在本轮均为 `not_run（派工范围禁止）`。

材料整理风险已告知主 Agent；待最终候选工程、差异、索引与声明形成后，可继续做材料终审。

## 追加：候选材料终审（2026-10-16 21:03，北京时间）

本段为第二次派工的静态终审，仍仅写本报告；未构建、安装、启动设备、运行测试或实际应用补丁。复核对象是候选工程路径 `traces/code-snapshots/20261016T125520Z-21b1f50b/project`，其清单声明 ID 为 `e68d9772f8f7a89f502e8f21574b3259d9a5af87f0fa2eb0244e5e8e08182a63`。**下述发现的 ID 算法问题尚不能以本段作为修复后通过；主 Agent 将在本报告停止后更新 workflow 元数据并重新冻结，最终版本应以新的完整性报告为准。**

### 字段、路径、会话与空输入

| 核对项 | 判定 | 本轮独立读取/计算结果 |
| --- | --- | --- |
| 官方 trace-index 字段标题覆盖 | pass | 官方模板 24 条，候选 24 条，逐条标题比较无差异；仅证明字段覆盖，不表示所有事实已补齐 |
| 文档相对链接 | pass | README、delivery-notes、trace-index、build、solution/source片段、pending/facts、session-map、token-usage 共检查23个本地 Markdown 链接，缺失0 |
| submission 片段 | pass（候选结构） | vg-spec9；3个路径均用 `/`，后2项是文件；project来源目录、build.md、trace-index.md实际存在。`tasks/vg-spec9/*` 是阶段3映射后的包根路径，当前片段不是团队完整清单或已提交事实 |
| 原生会话文件身份和摘要 | pass | 10份原生JSONL的header.payload.id、字节数/SHA256与导出manifest一致；各行JSON可解析、records匹配，parse error=0 |
| 父子/侧边栏映射 | pass | 3主线程header.id等于sidebar索引id；7子线程header.id为自身UUID，header.session_id对应父sidebar；过滤索引恰有3个父行，每个映射命中1行，不要求存在独立子sidebar行 |
| token表 | pass | 对10份JSONL重新取最后event_msg/token_count，原始行号、total_token_usage与manifest及Markdown表全匹配；没有另加缓存或reasoning，没有父子求和 |
| 真实团队已提供值 | pass | 本轮实际读取 `D:/HCUP/common/spec-harness/team.yaml`，确认 `HC2026-111` / `Ghost_London` / `online`，与片段一致。此事实更新前文初审时“团队待提供”的范围 |
| 未提供字段的处理 | pass（诚实占位） | 同一YAML的version/contact/freeze_time/members/source_guard及 `spec/submit-input.yaml` 的human_edits/known_issues/extra_sources/md_export_dir为空；pending、人工作业、solution/source片段均保留待补充，没有填造“无” |
| 正式材料事实完整性 | blocked（待用户事实） | 正式版本、联系人、冻结时间、成员分工、人工修改声明、已知问题/额外来源及实际保护措施仍未提供；完整团队清单、ZIP与外发未执行 |
| 可移植构建说明 | pass（静态整理） | 环境变量与工程相对路径代替私有运行路径；工程含test-harness和requirements；明确首启/签名/物理设备未验收及未重跑。命令在新环境的实际执行为not_run |

本轮按候选 `traces/manifest.json` 逐一读入相应native路径，核验ID映射，不把子线程的父会话ID错报为子线程自身ID。材料线程为截点记录，不能宣称本段报告及后续workflow事件已全部包含在先前导出内。

主 Agent 随后对材料主线程一次过宽侧边栏索引返回做局部隐私替换，提供 `checks/trace-redactions.json`：原生第45/47行各9条无关索引元数据行，原件未改。`trace-index.md` 与delivery-notes已披露该范围；解题8线程未改写。导出哈希应与脱敏后的manifest核对，不能继续要求脱敏导出等于原件哈希。本轮10线程摘要/解析/token复核针对当时实际导出字节；之后重导出仍需最终自动校验。未为对照脱敏而读取其他赛题会话。

### 完整工程、补丁、二进制与排除边界

| 核对项 | 判定 | 独立结果 |
| --- | --- | --- |
| 工程快照文件 | pass | manifest 776项；逐文件大小/SHA256及实际递归路径全匹配，78,993,873字节，未列路径0 |
| 当前纳入范围 | pass（该截点） | 本仓库tracked+nonignored，排除材料容器和明确2份总览后恰为776；与快照路径差异0，纳入项与当时工作区字节差异0 |
| 既有实际应用后的clone | pass（静态复核既有应用结果） | 只读检查 `checks/diff-validation.json` 指定已还原clone，776份哈希/路径与快照差异0；未在本轮重新应用补丁 |
| 补丁路径与摘要 | pass | 只读 `git apply --numstat --binary <final.diff>` 退出0，760路径与changed-files.json恰好一致；补丁84,427,139字节，SHA256 `60755bdd58b3da476db903e18302586cb47d8355eb9fa851227f11e8af9729e2` |
| 二进制清单 | pass | 125项实际字节/大小/摘要与清单一致；以本仓库批准基线blob比较，同路径同字节/changed标志判断差异0；未访问来源修复历史 |
| HAP证据 | pass（摘要） | build_artifact所列8,983,170字节和 `b367da…70b6` 与原HAP一致；明确它为ignored构建产物、不在project，不充当源码交付 |
| 排除边界 | pass | manifest无材料容器递归、2份总览raw、.git、build、.hvigor、oh_modules/node_modules或local.properties泄漏；仅保留排除路径/历史manifest说明，不把总览补回工程 |
| 基线换行保留表 | pass | 277项逐份取批准基线blob，与快照比较；原字节不同，CRLF→LF规范化后全部相同，问题0。该表准确区分checkout字节保留与功能编辑 |
| 内容快照ID算法 | **fail（M1）** | 下节最小复现说明；文件级内容和补丁覆盖未失败 |

`delivery-notes.md` 已要求阶段3从指定快照提取全部project，不能递归复制原工作区；外层材料、traces索引、日志和checks非work文件须保留。checks/work中的临时Git仓库不是交付物。旧manifest指向排除总览的路径属于已披露历史引用，不据此补回禁止内容。相对链接的最终映射及ZIP解包为阶段3责任，本轮not_run。

### 必须保留的重试与本轮失败

**已有补丁重试：** `checks/material-retries.md` 如实记录首次检查失败：Windows原生checkout在仅设core.autocrlf=false时仍取CRLF，不能匹配LF基线blob；原工作区未改。修复为隔离clone同时显式设core.eol=lf、core.autocrlf=false，再做新的apply-check/实际apply。当前 `checks/diff-validation.json` 记录二者退出0、全部文件字节还原；historical whitespace检查退出2另保留。此重试不能删掉或把首次失败记为通过；与277项实际checkout字节保留表相容。

**M1：快照ID算法声明与排序实现不一致（已先通知主 Agent）。**

- 关联要求：最终内容版本标识可由清单独立重算，且差异、工程、索引引用同一版本。
- 最小复现（只读）：按清单自述算法，将 `manifest.files` 按相对路径字符串排序，对每项连接 `path + NUL + sha256 + LF`，UTF-8编码后SHA256。
- 期望：重算值等于manifest.snapshot_id。
- 实际：重算 `db68058492eb13149c4e8a5781ae11fa69650c81c75ce257d01168de494b433f`，声明为 `e68d9772f8f7a89f502e8f21574b3259d9a5af87f0fa2eb0244e5e8e08182a63`。审计进程正常退出0，明确输出 `CANONICAL_SNAPSHOT_MATCH=False`；这是断言发现差异，不是成功匹配。
- 归因：freeze_project.py以WindowsPath对象排序，受Windows大小写排序规则影响；manifest文字却声明按path字符串排序。主 Agent 已确认该归因，证据强。776文件级哈希、补丁路径和既有还原结果均一致，证据不支持生产代码损坏。
- 建议回退：材料生成/验证，不退回功能需求或编码。主 Agent 负责显式按 `relative.as_posix()` 字符串排序、在verify_materials中加入独立重算检查，再为最终workflow元数据截点重生成工程清单/补丁及所有引用。修复后必须新报告证明ID、补丁应用和全文件字节均通过。
- 本轮终审不等待修复后快照，不宣称M1已重测通过；主 Agent 已授权在本报告停止后完成上述修复及最终自动报告。

### 终审证据留存与结束

完整静态命令/原始返回仍在本原生会话 `01a144bd-8665-7712-93a5-de24724c416c`。本轮大多数只读核对进程退出0；一次先尝试不存在的 `.comate/team.yaml` 读取退出1，随后按facts-and-sources指向读取真实只读common YAML完成核对，没有创建或猜填输入。Python只读核对使用 `PYTHONDONTWRITEBYTECODE=1`，未导入题内测试代码；仅取Git批准基线blob及JSON/文件字节，未生成测试缓存。只读补丁numstat不会应用或修改工程。

终审结论：候选材料的24字段覆盖、路径、会话对应、token、空输入处理、776文件覆盖、二进制/EOL清单及排除边界得到支持；**M1须由主 Agent 修复并在最终截点重新校验**。正式声明仍待用户补充。本角色完成追加派工并停止写入；后续workflow状态/事件变化及新版本引用不由本段替代最终校验。
