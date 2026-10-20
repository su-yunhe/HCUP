# cml-spec7 独立验证方案 01

状态：准备中，功能用例全部尚未执行。自测角色 `/root/verification_do`，`CODEX_THREAD_ID=01a158d3-1977-7490-b337-d28df9f59e73`。仅完成主 Agent 派工，不调度角色、不修改生产代码/Spec/全局 state。

输入：`spec/requirement.md`、`spec/metadata.json`、`spec/acceptance.md` 的 41 项、`spec/baseline-notes.md`、`workflow/requirements/implementation-review-01.md`、批准方案 `workflow/design/implementation-plan-01.md` v1.0。使用公共 `D:/HCUP/common/test-harness`（只读）和 `common/.venv`。此前基线证据仅帮助定位，不替代本轮构建安装实测。

## 测试及证据契约

- `hypium_tests/test_login_acceptance.py` 继承公共 `harness.driver.HarnessTestCase`。动态生成 A1–A15、B1–B19、C1–C7 共 41 个具名用例；恢复/冷启动/连点另列，不能冒充 41 项原文或官方得分。
- 每轮由主调度先明确源码冻结；记录完整生产输入 SHA256（包含新增非 tracked 源码）。构建前/构建后/测试前/测试后检查。生产输入变化时停止并废弃受影响证据。构建自动生成变更另登记，不能偷偷改基准。
- 完整构建包括 project clean 和 entry clean assembleHap，完整 stdout/stderr、命令、退出码和 HAP SHA256 留在本题 `logs/<round>/`。每轮 UI/功能测试前重新安装这轮刚构建 HAP，记录设备和安装结果；不直接测试当前不明来源已安装应用。
- 执行环境仅当前进程设置 `PYTHONPATH=D:/HCUP/common/test-harness`、`HDC_DEVICE` 和本题日志目录，使用 `D:/HCUP/common/.venv/Scripts/python.exe -m harness.runner --project D:/HCUP/cml-spec7 --device <target> --json <round>/selftest.json`，工作目录必须在 `logs` 下，保留 Hypium reports。
- 每次新 PowerShell 加载 `D:/hongmengcup/Enter-HarmonyEnv.ps1` 及 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。不修改全局用户环境。
- 原始 UI dump、截图、DMS 密度与 WMS 窗口数据由 `workflow/verification/cml_evidence.py` 保存。命令 exit0 仍检查 stdout 是否 `[Fail]`/命令不存在，不按退出码粉饰环境可用性。
- `CML_RUN_DIR`、冻结指纹和成功的 `install-manifest.json` 是测试入口前置；没有这轮安装证据时整类 skip。视觉审查以同源码/HAP的截图为依据，review 必须写像素文件路径和理由；没有 review 的视觉项显式 skip。

## 41 项映射

| 验收项 | 自动实测 | 额外证据/判定 |
| --- | --- | --- |
| A1 | “我的”真实登录入口进入 auth_login_page；返回后再次点击 | 进入前后树/截图，未登录前置 |
| A2–A5 | Logo存在、按钮前、真实边界及密度换算120×120vp、中心 | A2图案/A3顶部归属需截图审查；中心固定对 auth_login_content |
| A6–A13 | 两按钮精确文字、Logo下方、可点击 | A8/A9实体填充/圆角、A10次级层次、A12/A13空心/圆角需截图；不擅定半径/间距 |
| A14–A15 | 真实点击分别进入不同目标id，并排除另一目标 | 不要求发验证码/认证，不要求实现下游表单 |
| B1–B8 | 提示精确文字/位置，三图标边界、相邻边缘间距≤1px舍入误差，标签对应/下方 | B3品牌语义由截图审查，id存在不证明图标正确 |
| B9–B11 | 缺合法平台配置时原子项显式 skip，最终矩阵记 blocked | 可另测真实缺配置错误及恢复；提示响应不算授权/快速登录启动；不造凭据/普通网页/deep link替代 |
| B12–B13 | 两个主题色链接精确文字及独立点击节点 | 底部位置、遮挡结合截图 |
| B14–B15 | 分别导航实际正文，按批准正文片段检查；滚动到末尾、返回重进 | U4已被用户授权本应用原创本地正文，不保持外部来源skip；正文需需求角色事实审查，不能只按长度/标题通过 |
| B16–B19 | 按真实可见节点顺序拼合逐字符合同意文案，页脚在主内容之后 | B17最底部归属、B18/B19当前主题主色需像素审查；短窗口允许真实滚动至页脚 |
| C1 | 手机真实窗口<600vp，region/content=100% | 保留window、page、content、region四套原始值 |
| C2–C3 | 平板真实窗口600≤w<840vp，region/content=70%，水平居中 | 1px仅布局舍入，不放宽比例 |
| C4–C5 | 大屏真实窗口≥840vp，region/content=60%，水平居中 | 没有真实大屏不能以注入断点标通过 |
| C6–C7 | 三种真实窗口分别图标均匀及包含于同一region | 聚合必须三类窗口齐备；单轮手机pass不能代替三类覆盖 |

U1分类分母为真实窗口宽（由WMS、DMS密度得到）；U3比例/Logo居中固定分母为 `auth_login_content`（扣安全区、业务padding前）。`auth_login_page`和原始WMS窗口始终保存，不能按结果换分母。

## 边界与恢复

E01空输入/E02纯空格：主页没有TextInput，输入校验不适用；不输入任何凭据点击两按钮仍须跳转。E08最后一页：没有分页，N/A；协议滚动末尾是阅读测试，不虚构分页。

执行 E03/E04/E09 部分操作/取消/离页：短信、账号、协议、隐私页进入后未提交即系统返回，再次进入；缺配置三方提示后可返回/重试/改用普通入口，不假称测试了真实授权取消。E05/E06：同入口三次快速点击、两登录按钮交错点击、“我的”入口连点，保留栈/截图，确认可恢复且一次返回能回原页。精确首击/末击优先未规定，不增加隐藏判据。E07：首次启动/无账号/无历史数据的静态UI完整。E11/E12：返回重进、stop/start冷启动经正常入口重进。

网络和持久化不变量不能只凭UI证明。需在冻结代码上取得真实登录相关调用/日志或可观察网络证据；首页后台请求另计。当前真实缺配置分支不应生成认证/支付请求或Token。若无可可靠采集的方法，明确记该辅助不变量not_run，不将静态阅读写作实测pass。

## 设备与三尺寸策略

只读初检：`127.0.0.1:5555`，API23，`emulator 6.1.0.115(SP11DEVC00E115R4P11)`，1308×2880，Density3.5、373×822vp，前台coolmall0。只读CLI帮助和原始输出在 `logs/verification-preparation-01/`。Hypium有 `get_display_rotation`/`set_display_rotation`；后续旋转放finally恢复，不能假称已实测。当前主实例保持运行、禁止停止或改其配置。

主 Agent 已批准在本题 `logs/verification-emulator/instances` 创建 `CmlSpec7_Layout`，复用只读官方 phone_all_x86/API23 镜像，自定义 `1600 2400 320 10.1`。预期 portrait800vp、landscape1200vp（均须启动后重读DMS/WMS确认）。命令参数、退出码、stdout/stderr保存在 create-layout-instance*；当前两次CLI返回0但目标配置未生成，因此创建尚未成功，未启动也未宣称有三尺寸覆盖。不得无限调研或以空stdout当成功。

若临时实例可用，先记录实际新hdc target，所有动作显式指定目标；新实例每轮先装新HAP。旋转/resize需记录before/after/恢复的真实几何；未达阈值或不支持则blocked。测试结束只停止本角色启动的临时实例，保留配置和证据，大文件清理由主调度决定。

## 状态与回退

当前41项均 `not_run`；B9–B11的外部接入前置另记 `blocked`。没有任何本轮功能pass/fail结论。失败报告包含最小复现、关联需求、期望/实际、原始日志/截图、源指纹、归因假设及证据强度，交主调度决定回需求/方案/编码或修环境。生产代码、Spec和原验收断言保持由其所有者管理。
