# vg-spec9 独立验证报告

**结论：本轮12项最终有效本地用例全部 pass，fail/error/skip 均为0。A1—A18通过；未执行的扩展探索和不适用项单列，不计通过。** 验证角色没有修改生产代码、Spec或调度状态，也没有创建子 Agent。原生会话为 `01a14492-d90e-7c23-aa1e-0deef1467f23`。

## 环境、构建与完整性

- 主 Agent 明确确认5份生产文件冻结并独占 `127.0.0.1:5555` 后才构建和操作。每个PowerShell进程加载指定两份环境入口。实际运行 Python `D:/HCUP/common/.venv/Scripts/python.exe` 3.12.3、Hypium 6.1.0.210；Windows 11，DevEco 6.1.0.860 / SDK API23。
- 设备实读为 `emulator 6.1.0.115(SP11DEVC00E115R4P11)`、API23、model=`emulator`；UI树/截图1308×2880。框架环境告警为空只说明其镜像/分辨率检查通过；未独立确认Pura虚拟机型或560 DPI。见 `round02-t1-retry/environment-and-static-command.log`、`preparation/python-runtime-command.log`。
- 独立命令 `hvigorw clean assembleHap --mode module -p product=default -p buildMode=debug --no-daemon` 退出0，编译器实际执行，16.448秒。`logs/build.log` 为该原始日志字节副本；命令/退出码见 `round02-t1/Build-command.log`、`build-exit.txt`。
- HAP：`entry/build/default/outputs/default/entry-default-unsigned.hap`，SHA256 `b367da84359ad19ba9fad5e808f864fe06c10280850332da1c11615a8efe70b6`。每次最终有效runner前均重新安装此HAP，install退出0，再从 `logs/` 运行 `harness.runner`，见 `logs/install.log`。
- 编译文件诊断756条，基线759条。按“源文件+消息”多重集净新增0，`SettingsSyncSection` 的既有showToast弃用净减2、异常处理提示净减1。严格“消息+源码表达式”匹配中SS:66订阅toast的表达式变化单独保留，未隐藏。另2条 `LoadingAnimations` 既有可选@Prop提示已包含在756中；无签名配置警告仍存在。机器索引/差分在 `round02-t1/build-warning-index.json`、`build-warning-comparison.json`。
- 工程源码与资源指纹覆盖 `entry/src/`、`AppScope/` 及工程根相关脚本/配置，共251份，本轮5份生产文件均在其中。全部有效轮次前后指纹完全相同，canonical摘要 `19bd55c11a219168929aa255afb3a0580826b59cf958b5d2782f24b2d4b411cd`；范围及逐文件哈希见各轮 `source-fingerprint-*.json`。四份批准输入SHA亦再次核对一致。
- 三个被修改/新增UI组件行数为489、106、188，控制器100；原非UI manager 1218。`git diff --check`退出0。此静态检查不代替下面设备证据。

本文短路径均相对 `traces/implementation-validation/`，除非明确以 `logs/`、`workflow/`、`entry/` 开头。

## 最终有效执行与证据入口

| 轮次 | 实际选择 | 结果/runner退出 | 说明 |
| --- | --- | --- | --- |
| round02-t1-retry | 01 | 1 pass，0 | 正常入口、可写服务成功全链路，82.430秒 |
| round02-regression | 02—10 | 9 pass，0 | 1200.061秒；旧T10首闸风险另由补测排除 |
| round02-supplement | 10、11、12 | 3 pass，0 | 295.471秒；最终T10采用此轮，另补密码空格及系统返回 |

`logs/selftest.json` 按用例名取最新有效结果，共12项，同时引用全部分轮原报告。`logs/selftest.log`、`install.log`、`build.log` 及 `verification-log-manifest.json` 为可审计入口；历史失败仍保留。`round02-validation-summary.json` 联合请求接收/响应完成、UI采样和指纹重新校验，生成命令退出0，见 `finalization-command.log`。

服务仅绑定宿主loopback，使用本轮合成凭据，每场景独立目录。每条请求保留认证匹配布尔值、方法/路径、接收/响应时间、内容长度/哈希与真实PUT字节；没有硬编码产品UI结果或替换生产网络流程。自动同步在各测试入口实测为关闭。

关键证据：

- **成功全链路**：T1接收5条真实请求：HEAD200、词条GET404、上传前HEAD200、词条PUT201、事件GET404，最后真实成功。首/中/末可见LoadingProgress截图和类型树保存于 `round02-t1-retry/test_01_success_real_request_and_loading-*.png/.json`；终态恢复按钮、加载隐藏。业务载荷549字节原文保留于 `put-4.bin`。
- **无数据**：独立验证上述载荷MAC、AES-CTR解密后，仅汇总结构/数量：words=0、definitions=0、userBooks=0；无业务增量仍有真实请求与加载。见 `business-upload-summary.json`、`payload-summary-command.log`，退出0。没有仅凭远端404断言本地为空。
- **旧120秒边界**：T6沿既有递归父目录HEAD/.keep PUT预检，每条响应约8秒，整轮264.469秒后成功；点击约122.469秒后的 `round02-regression/test_06_long_chain_exceeds_old_wrapper_timeout-after-120s.json/.png` 中实际 `LoadingProgress` 可见，并与同轮未完成请求重叠。没有把第一条响应或包装计时到期当同步结束。
- **密码空格**：T11真实Basic认证精确匹配，实际上传MAC使用含首尾/内部空格的原密码验证成功，trim后的密码验证失败；见补测 `ui-events.jsonl` 的 `password_spaces_verified` 和request_id9上传原文。
- **重入**：T7标题返回分区后重进、T12系统返回首页后沿正常入口重进，均在真实请求仍进行时核对同轮类型/可见加载，最终正常结束；截图含 `after-reentry`、`after-system-reentry`。

## A1—A18逐项判定

| 项 | 状态 | 有效测试及观察 |
| --- | --- | --- |
| A1 | pass | T1/T4/T7/T12，正常首页→设置→WebDAV及重进 |
| A2 | pass | T1正确认证、可写受控端点，实际PUT201并成功终态 |
| A3 | pass | T1既有立即同步按钮点击及时间记录 |
| A4 | pass | T1请求保持期busy外观及禁用按钮，截图/树可查 |
| A5 | pass | T1按ID、实际LoadingProgress类型、visible及屏幕范围联合核验 |
| A6 | pass | 同一正常手动按钮触发，独立目录关联本轮 |
| A7 | pass | T1真实请求未完成时加载可见 |
| A8 | pass | T1原四阶段流程到达实际下载/加密上传/事件下载 |
| A9 | pass | 受控正确端点接收真实认证请求与本轮目录匹配 |
| A10 | pass | 同一按钮点击记录，不复用历史或测试连接请求 |
| A11 | pass | T1/T6同步期间实际LoadingProgress可见 |
| A12 | pass | 同轮真实服务端接收记录，与UI时间关联 |
| A13 | pass | 测试无本轮请求即失败；UI/网络联合断言，未加生产假模式 |
| A14 | pass | 首/中/末及>120秒活动请求与实际加载重叠，真实终态后隐藏 |
| A15 | pass | 成功终态恢复，T3完成后再点产生新轮请求 |
| A16 | pass | T2 HTTP403结束恢复→更正成功；T9连接拒绝→有效重试 |
| A17 | pass | 真实加密载荷空业务集合、空远端及T3重复同步仍有请求/加载 |
| A18 | pass | T3首轮3次快点、busy内3次点及终态后重试不提前清状态 |

前三场景共享完整证据；A15—A18仍为合理推导，不改标Spec明文。

## B1—B15与范围边界

| 项 | 状态 | 已观察覆盖与限制 |
| --- | --- | --- |
| B1 | pass | T5四必填字段逐个为空；T8空目录沿既有默认值；均能结束恢复 |
| B2 | pass | 纯空格、地址/账号trim、空格目录默认，T11密码首尾/内部空格真实认证与MAC |
| B3 | pass；取消按钮N/A | T4编辑/收键盘/未触发返回不产生本轮同步；原文无同步取消按钮 |
| B4 | pass；确认框N/A | T4未触发即离页、T7运行中标题返回；原文无同步启动确认框 |
| B5 | pass | T3 busy期间重复点击保持当前加载，完成后可新开轮 |
| B6 | pass | T3连续快速点击与busy后连点，未破坏正在运行流程 |
| B7 | pass | T1实际空业务载荷、远端GET404；T3再次同步仍真实请求 |
| B8 | N/A | 原文无分页/末页/加载更多 |
| B9 | pass（适用子项） | T4只编辑/保存/返回无本轮手动请求；T1/T6多阶段持续加载。单独点测试连接的归因演练not_run，未冒充同步证据 |
| B10 | pass（已测分支） | HTTP403、连接拒绝及更正重试。物理断网/DNS等其他错误类型not_run，不声称穷尽 |
| B11 | pass | 空闲返回、在途标题返回和系统返回首页后正常重入 |
| B12 | pass（空闲冷启动） | T4已结束临时busy不残留。运行中force-stop为扩展探索not_run |
| B13 | pass | T6真实264.469秒，多请求各8秒，>120秒仍可见且最终成功 |
| B14 | pass（快速响应分支） | 普通夹具后续响应约0.1秒，自然收束；未新增最短驻留要求，未专设一帧内整链结束 |
| B15 | pass（已选固定轮策略） | 最终T10运行中编辑下一轮地址/目录，五个提交入口禁用，本轮已观测后续请求保持A且成功。自动任务竞争、终态后直接采用B另轮、返回后再编辑交错为扩展not_run |

N/A项不计通过；表中的限定与not_run子项不被折算为整类边界穷尽通过。首次全新清数据安装引导、物理设备、其他外部WebDAV产品、旧无关ohosTest均not_run。保留原应用数据，未为测试清空业务数据库。

## 历史失败与夹具修正

1. 嵌套目录主机自检首次父目录 `.keep` 路径归属缺失：期望PUT201，实际断言失败，日志 `preparation/fixture-tree-selfcheck.log`。归因强度高：夹具未登记父目录文件路径。仅修夹具后主机自检退出0；发生在设备主路径前，不作为生产失败。
2. 首次T1在点击同步前，Hypium `swipe('up')` 被API拒绝，期望UP/DOWN，实际 `HypiumParamDirectionError`，runner退出1且未发同步请求。原 `round02-t1/selftest.json`/日志保留；仅把测试参数转大写，重新安装相同HAP，T1重测退出0。归因强度高：明确的测试API参数错误。
3. 旧T10首闸16秒叠8秒延迟，首响应实测24.008秒，可能越过客户端20秒读取超时；原9组虽均成功，该项以补测为最终依据。新夹具使用 `min(16,18-delay)`，补测最长请求18.012秒，T10正常成功。旧T1提前释放、T6无首闸等证据未受影响，无需重复全套。

测试版本见 `round02-test-versions.json`：旧测试 `60e899d481b3f90cb0a9a4a0f0e491cbf5f5ce74ba9b16459e6b1c62ebbaff97`；当前测试 `78c9aaa7fa8e368b5a59869d064bd26db665127d2d240427397e9f0d0a76c726`；当前夹具 `95fe3371fba612a99a3881de08831adec737eae7ea09ca3fa38b9549dd6739d8`。旧夹具9a5625…的文本由已记录的单行首闸变更复原，元数据明确注明，不伪称运行时采集。未删除失败断言，没有生产失败需要回退编码/方案。

## 复现、结束状态与限制

完整命令和环境变量在 `workflow/verification/REPRODUCE.md`。必须先冻结生产源码并取得设备独占，设置 `VGSPEC9_SOURCE_FROZEN=1`；`VGSPEC9_TESTS=''`或不设筛选会发现全部12项。脚本自动设置 `VGSPEC9_EVIDENCE`、HDC_DEVICE和PYTHONPATH，先安装再从logs运行。`preparation/unfiltered-discovery-12.log` 已验证无筛选发现12项，退出0。

服务已正常close，补测末行记录 `fixture_stopped`；`host-service-closed.log` 实读18769端口LISTENER_COUNT=0。Windows connect_ex返回10035仅表示该次未建立连接，停服结论以监听表和正常close记录为准。设备仍停在成功WebDAV分区，保存本轮合成端点/凭据，自动同步关闭，未恢复不可读取的旧真实密码。从交接消息起停止设备操作并释放租用。

未重试此前被自动审批拒绝的端口清理。最终残留18769 Reverse，以及9908/9923/9942/9949/9981/9982/9989至8012的Forward，完整列表在 `finalization-command.log`；不宣称映射全清。主Agent清理本题生成缓存时，递归删除亦被自动审批拒绝（blocked by policy）；随后采用不删除方案，将3个已核实的 `__pycache__` 原样移至本题现有忽略目录 `.hvigor/vg-spec9-selftest-cache-20261016-1238/`，gitstatus已不含缓存噪声。处理记录为 `workflow/acceptance/cleanup.log`；本角色随后仅编辑报告，不再import测试模块生成新缓存。HAP、原始报告、日志、上传字节和截图均保留。构建产生 `entry/build`、缓存及Hypium `logs/reports` 属工具产物，与生产编辑分别登记。主Agent最终审计见 `workflow/acceptance/final-audit.json`。

HAP为unsigned，仅证明本机模拟器安装/本地验收；官方隐藏评测不可见，不捏造官方分数或通过率。本报告不把静态阅读、构建成功、服务收到单条错误请求或官方示例当整题完成证据。
