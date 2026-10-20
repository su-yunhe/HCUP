# cml-spec7 基线现状与验证记录

本轮仅完成 `spec-harness/0-analyze.md` 分析阶段。已先构建、安装、启动未修改的基线，再经真实页面入口操作并形成本文。**业务代码未修改，当前登录页仍是占位页，不能标记功能验收完成。** 验收标准见 [acceptance.md](D:/HCUP/cml-spec7/spec/acceptance.md)。

证据区分：**实测**指本轮构建、Hypium/hdc 操作、UI 树与截图；**代码事实**指当前源码静态核对；**推断/未验证**明确标注。完整交接分别在 `workflow/implementation/baseline-code-audit-01.md`、`workflow/verification/baseline-evidence-01.md`、`workflow/design/analysis-review-01.md`。初始化总览会话未被读取或用作功能证据。

## 1. 基线快照与输入

| 项目 | 标识及证据 |
| --- | --- |
| 题号/工程根 | `cml-spec7` / `D:/HCUP/cml-spec7`；本目录就是工程，没有另建 project 子目录 |
| 基线与当前 HEAD | `75fd0066a7fc0c1e8cedb6218df081f86d307f45`；对应 `spec/metadata.json:2`。采用记录 HEAD 的方式标识基线，未新增 tag、提交或切换分支 |
| Spec SHA256 | `d4600d3b744f8d5cd11d2c5e09e2148798a439b5206c03ffbf3c8c70a411fed9`；`spec/requirement.md` 与原始 `inputs/Spec.md` 一致 |
| metadata SHA256 | `cf5f402ae5042331bf332c4173a3b26ddb3c2494cee9976bd2b39106ca0e5a88` |
| tracked 文件冻结 | 开始指纹 `workflow/analysis-start-fingerprint.json` 记录 772 个 tracked 文件；编码角色复核全部无变化。独立验证的 794 个生产输入首尾也全部无变化，见 `logs/analysis-baseline/fingerprint-before.json`、`fingerprint-final.json`，汇总为 `closeout.json:3-10` |
| 本轮写入范围 | 两份 spec 分析文档，以及本题 workflow、logs、traces、system-config 记录和验证脚本；构建产物由工具生成。没有业务源码修复 |

## 2. 构建状态、产物与已有告警

### 2.1 本轮完整构建：实测通过

每个构建或设备命令的新 PowerShell 进程均加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。可复现命令：

```powershell
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
Set-Location D:/HCUP/cml-spec7
hvigorw --mode project -p product=default clean --no-daemon
hvigorw --mode module -p product=default -p module=entry@default -p buildMode=debug clean assembleHap --no-daemon --no-incremental
```

两步退出码均为 0；完整编译输出 `BUILD SUCCESSFUL in 32 s 790 ms`，见 `logs/analysis-baseline/build-full-raw.txt:1498`。复现脚本为 `workflow/verification/baseline-build.ps1`；退出码、时间与 HAP 哈希另记在 `logs/analysis-baseline/build-full-transcript.txt`。本次禁用增量，以取得完整告警，未按告警修改源码或压制诊断。

| 项目 | 本轮结果 |
| --- | --- |
| DevEco | 本机配置为 6.1.0.860；工具路径见 `logs/toolchain-paths.json`，版本运行输出见 `logs/analysis-baseline/tool-versions.txt` |
| 工具版本 | Node 18.20.1、Python 3.12.3、hvigor 6.23.7、hdc 3.2.0c、Hypium 6.1.0.210；均有本轮命令输出 |
| 工程 SDK 声明 | `build-profile.json5:7-8` 的 target/compatible 均为 `6.0.1(21)`，本轮保留原声明；设备实际 API 为 23，不混为工程已改 SDK |
| HAP | `entry/build/default/outputs/default/entry-default-unsigned.hap` |
| 实际安装的最终 HAP SHA256 | `792dc2809f4376f4d4c94a796d9c959305d300298870a00b1ee673bafc20f109` |
| 原始完整构建日志 SHA256 | `26c29957df10e5a86943c3325654f44e7aaa4dfd50abe397cae733244e3b3697` |

早期构建/采集过程中产生过不同 HAP 哈希，不能用其替代上述最终产物。最终完整构建之后重新安装、冷启动并重新取证，安装证据为 `logs/analysis-baseline/install-final.json:10-11`。

### 2.2 告警基线

完整清单保存在 `logs/analysis-baseline/warning-summary.json`：每条 ArkTS 诊断保留源码路径、行列和消息；资源冲突名及出现次数也全部列出。原始日志保留未过滤输出。下面是分类汇总，不是“无告警”：

| 类别 | 出现次数 |
| --- | ---: |
| `arkts-strict-typing-required`（就地注释关闭类型检查） | 140 |
| `arkts-no-typing-with-this` | 1 |
| `arkts-no-implicit-return-types` | 8 |
| `arkts-no-type-query` | 2 |
| `Function may throw exceptions. Special handling is required.` | 34 |
| `@BuilderParam content` 初始化限制 | 22 |
| **ArkTS 文件诊断合计** | **207（207 个唯一位置/消息组合；依赖 153，工程 54）** |
| 资源名冲突 | 170 |
| Duplicate file names | 1 |
| 缺少 sourceMapsPath | 1 |
| 未配置 signingConfig | 1 |

后三项原始位置分别为 `build-full-raw.txt:1484`、`:1487`、`:1494`。资源重名包括 `wechat`、`qq`、`alipay`、`confirm`、`page_show` 等，完整名称清单见 JSON，后续比较应按消息/位置而非只比较总数。

`build-profile.json5:3` 的 signingConfigs 为空。**实测当前模拟器直接安装 unsigned HAP 成功**，没有修改签名配置，也没有关闭设备校验；该结果只适用于本轮设备，不外推到真机。

## 3. 安装、启动与真实入口：实测

### 3.1 环境与命令

设备 `127.0.0.1:5555`，使用本机已配置的 `HarmonyCup_API23` 模拟器。初检无在线设备，随后启动配置好的模拟器；安装前前台为锁屏/桌面，没有占用别题的运行流程。环境证据见 `logs/analysis-baseline/emulator-start.txt`、`foreground-before-install.json`、`env-check-after-boot.txt`。

实际镜像版本为 `6.1.0.115(SP11DEVC00E115R4P11)`，API 查询为 23，分辨率 1308×2880。`logs/analysis-baseline/runtime-display.stdout.txt` 记录 VirtualPixelRatio/Density 为 3.5，虚拟尺寸约 373×822；物理 DPI 字段与逻辑缩放字段分别记录，不混用。仅实测此手机窗口，没有进行平板、大屏或动态 resize 验证。

```powershell
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
Set-Location D:/HCUP/cml-spec7
hdc -t 127.0.0.1:5555 install entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t 127.0.0.1:5555 shell aa start -a EntryAbility -b com.joker.coolmall
```

bundle/ability 来自 `AppScope/app.json5:3` 与 `entry/src/main/module.json5:6,17`。安装退出码 0，原文 `install bundle successfully`；启动输出见 `logs/analysis-baseline/start-final.json`。首次启动出现麦克风权限界面，本轮选择“不允许”，之后从应用系统权限详情返回；自动化处理及系统返回过程保存在 `home-after-permission-action.json`、`final-permission-back-action.json`。这些操作未修改业务代码，未输入账号或凭证。

### 3.2 实际操作结果

| 操作 | 实际结果 | 本轮证据 |
| --- | --- | --- |
| 启动，处理首次权限界面 | 到首页，可见底部“我的” | `logs/analysis-baseline/final-home-visible-action.json`；`traces/analysis-baseline/final-home-visible.ui.json` / `.jpeg` |
| 点击“我的” | 显示未登录资料区域与“点击登录账号” | `logs/analysis-baseline/final-me-action.json`；`traces/analysis-baseline/final-me.ui.json` / `.jpeg` |
| 点击“点击登录账号” | 到标题“登录”的页面，正文仅“登录页面内容视图” | `logs/analysis-baseline/final-login-action.json:68-78`；`traces/analysis-baseline/final-login.ui.json` / `.jpeg` |
| 系统返回后再次进入 | 再次到同一占位登录页 | 对应返回/重进动作与截图索引见 `workflow/verification/baseline-evidence-01.md` |
| force-stop / start 后从首页重走入口 | 再次到同一占位登录页 | `logs/analysis-baseline/cold-stop.json`、`cold-start.json`，后续 cold-* 动作/UI/截图见验证报告 |

主 Agent 另直接查看了 `traces/analysis-baseline/final-login.jpeg`，与 UI 树和代码占位内容一致。关键截图可打开：[登录主页截图](D:/HCUP/cml-spec7/traces/analysis-baseline/final-login.jpeg)。

9 项独立实时文字断言结果为 **1 pass / 8 fail，退出码 1**，见 `logs/analysis-baseline/login-assertions.json:5-59`、`login-assertions-exit.txt:1`。A1 通过还有前后页面操作证据支持，不是只凭“登录”标题判断；失败项为 A6/A10/B1/B6/B7/B8/B12/B13，对应两按钮、其他登录提示、三方文字及协议/隐私入口文字缺失。这是当前基线的实际缺口，不是本阶段文档任务失败，也不是完整 41 项自动验收结果。

独立验证将截图、UI 树、实时断言及未执行项映射到全部 41 个明文项，结果为 **pass 1 / fail 11 / blocked 25 / not_run 4**，逐项证据与限制见 `workflow/verification/baseline-evidence-01.md` 的“逐需求基线状态”。其中 blocked 是缺控件等前置而无法执行点击/量测，不计通过；这组基线分类与 9 项实时文字断言的统计口径不同。

### 3.3 已验证与未验证边界

- **已验证**：构建、最终产物安装、启动、正常入口、占位页显示、返回重进、重启后经正常入口重进。
- **代码和截图均确认缺失**：Logo、两按钮、其他方式、三方图标/标签、底部文案/链接与响应式按钮区域；源码证据详见第 5–6 节。
- **未执行/缺前置**：手机号与账号密码按钮点击、微信/QQ/支付宝授权及认证、协议详情链接点击、上述控件的快速连点与取消/失败恢复。控件不存在，不能称已实际点击或发出过对应请求。
- **未验证**：平板/大屏比例、120 Logo 的设备测量、样式像素/主题色、接口可用性、真实账号登录与持久化成功路径。手机页面缺失按钮区，C1 比例也不能凭“空页面全宽”判通过。

## 4. 入口、路由与跳转调用点：代码事实

| 环节 | 路径、路由及调用点 |
| --- | --- |
| 导航图注册 | `entry/src/main/ets/entryability/EntryAbility.ets:33-37,125-135` 注册 MainGraph/AuthGraph/CommonGraph 等；`entry/src/main/ets/navigation/NavigationHost.ets:13-17,36-42` 挂全局 NavPathStack/Navigation |
| “我的”页 | `feature/main/src/main/ets/view/MainPage.ets:71-73` 的第 4 个 TabContent 是 MePage；`viewmodel/MainViewModel.ets:25` 配标题资源 |
| 点击区域 | `feature/main/src/main/ets/view/MePage.ets:102-115` 的资料 Row/Avatar；`:166-169` 的未登录提示。`feature/main/src/main/ets/viewmodel/MeViewModel.ets:269-270` 调 onHeadClick→toProfilePage，`:329-330` 调 navigateTo(UserRoutes.Profile) |
| 受保护路由 | `core/navigation/src/main/ets/routers/UserRoutes.ts:9`：`user/profile`；`RouteInterceptor.ts:16-21` 列为保护路由 |
| 未登录改写 | `core/navigation/src/main/ets/NavigationService.ets:56-73` 在未登录时替换为 getLoginRoute()；`RouteInterceptor.ts:62-63` 返回 AuthRoutes.Login。结果是 `auth/login`，不是头像直接写了登录路由 |
| 登录路由注册 | `core/navigation/src/main/ets/routers/AuthRoutes.ts:9,13,17`：`auth/login`、`auth/account-login`、`auth/sms-login`；`feature/auth/src/main/ets/navigation/AuthGraph.ets:17-19` 注册，三个 *Nav.ets:9-10 构造对应页面 |
| 其他拦截入口 | `NavigationService.ets:138-162` 的 navigateToWithResult 同样会改写；`:177-180` 的 navigateToForResult 间接走该分支。当前受保护入口包括订单/地址/足迹等，完整 MeViewModel 调用点清单见代码审计第 1.2 节 |
| 协议与隐私路由 | `core/navigation/src/main/ets/routers/CommonRoutes.ts:21,25` 定义 `common/user-agreement`、`common/privacy-policy`；`feature/common/src/main/ets/navigation/CommonGraph.ets:21-22` 已注册 |

**推断且需保持测试前置**：已有非空 token 时资料点击继续去 user/profile。`core/state/src/main/ets/UserState.ets:134-135` 的 isLoggedIn 只查 token 非空，`:142-143` 的过期判断是另一方法。本轮实际走的是未登录分支，未实测已有/过期 token 分支。头像与外层均绑回调是否导致快速操作重复入栈，未验证。

## 5. 页面、状态、服务、存储现状：代码事实

| 范围 | 当前事实与证据 |
| --- | --- |
| 登录主页 | `feature/auth/src/main/ets/view/LoginPage.ets:20-26` 使用 AppNavDestination、标题“登录”；`:34-35` 仅一个占位 Text。`feature/auth/src/main/ets/viewmodel/LoginViewModel.ets:7-9` 是空类，无状态、点击处理或请求 |
| 短信、密码目标页 | `SmsLoginPage.ets:20-35`、`AccountLoginPage.ets:20-35` 分别只有标题和占位 Text；完整路径同登录主页的 view 目录。对应 `viewmodel/SmsLoginViewModel.ets:7-9`、`AccountLoginViewModel.ets:7-9` 为空。路由存在不等于表单或登录实现 |
| 第三方客户端流程 | 登录页/VM 没有三方入口与处理；`feature/auth/oh-package.json5:8-16` 未声明授权 SDK；`entry/src/main/module.json5:23-35` 只有 home entity/action。认证相关受限检索未找到提供商拉起/授权回调，不能用资源文字当实现证据 |
| 认证仓库 | `core/data/src/main/ets/repository/AuthRepository.ets:27-28,36-37` 转发微信/QQ；`:54-55,72-73,81-82` 转发短信发送/手机号认证/密码认证。未被三个登录 VM 调用 |
| 网络接口 | `core/network/src/main/ets/datasource/auth/AuthNetworkDataSourceImpl.ets:16-19` POST `user/login/wxApp`；`:27-30` POST `user/login/qq`；`:49-52` POST `user/login/smsCode`；`:71-74` POST `user/login/phone`；`:82-85` POST `user/login/password`；`:92-95` GET captcha。没有支付宝登录方法；QQ 模型在 `core/model/src/main/ets/request/QQLoginRequest.ets:9-20` |
| 服务基础地址 | `core/network/src/main/ets/NetworkClient.ets:16-24` 为 `https://mall.dusksnow.top/app/`、超时 10000ms。本轮没有主动调用认证服务，可用性未验证；`core/network/src/main/ets/interceptors/AppInterceptors.ets:15-35` 未实现用户 token 注入 |
| 认证/用户模型 | `core/model/src/main/ets/entity/Auth.ets:10-27,56-79` 有 token、refreshToken 和过期判断；`core/state/src/main/ets/UserState.ets:23-31,41-68` 保存、更新 Auth/User |
| 登录状态持久化 | `UserState.ets:158-159,169-175` 用 PersistenceV2 和 `user_state`；`:77-80` 清除。`MeViewModel.ets:115-136` onShown 读取用户状态；当前缺少登录 UI 写入链路 |
| 账号密码存储 | `core/data/src/main/ets/repository/AccountStoreRepository.ets:19-20,28-54` 提供保存/读取；`core/datastore/src/main/ets/datasource/account/AccountStoreDataSourceImpl.ets:18-33,41-68` 使用 PreferencesUtil，文件 account_store，键 account/password，直接存取字符串。登录 VM 未接入；Spec 没有要求本题新增密码保存 |
| 协议详情 | `feature/common/src/main/ets/view/UserAgreementPage.ets:20-35`、`PrivacyPolicyPage.ets:20-35` 仅标题和占位正文；对应 viewmodel 文件 `:7-9` 为空。主页链接、真实正文和加载逻辑都未实现 |

上述服务只表示代码中存在可调用声明；本轮未取得外部授权凭据、有效验证码或服务可用性证据。Spec 要求的手机/密码入口是跳转，本阶段不擅自扩成实现两个目标页的完整登录业务。

## 6. 可复用的既有能力及缺口

| 基础能力 | 可复用位置与当前限制 |
| --- | --- |
| 页面容器与返回栈 | `core/ui/src/main/ets/component/navdestination/AppNavDestination.ets:13-67,122-150` 提供标题、安全区/padding和生命周期；`core/navigation/src/main/ets/NavigationService.ets:83-89` 提供 pop。应沿现有主入口，不另建测试入口 |
| Logo | `core/ui/src/main/ets/component/icon/LogoIcon.ets:13-28` 使用 app.media.ic_logo、可传 iconSize；底层 `CommonIcon.ets:32-53` 设置宽高。登录页未使用；120×120vp 是有代码依据的推导，Spec 只明写 120 |
| 居中与行布局 | `core/designsystem/src/main/ets/component/Column.ets:146-217` 的 ColumnCenter、`Row.ets:386,447` 的 RowSpaceBetweenCenter 已存在，登录页未接入 |
| 断点 | `core/state/src/main/ets/BreakpointState.ets:17-33,76-82`：XS<320、SM<600、MD<840、LG≥840vp；`:125-154` 取响应值，`:208-209` 导出 bp |
| 窗口变化 | `entry/src/main/ets/adapter/WindowAdapter.ets:156-166,192-202` 监听宽度并从 px 转 vp；`feature/main/src/main/ets/view/MainPage.ets:32-33,55-84,105-119` 已使用 bp 调整导航布局。登录页没有读取断点 |
| 百分比/主题 | `core/designsystem/src/main/ets/constants/LayoutPercent.ets:69,79,109` 有 P60/P70/P100；`core/designsystem/src/main/resources/base/element/color.json:4-6` 有 primary #465CFF。常量存在不证明当前页面达标 |
| 可见 loading 组件 | `core/ui/src/main/ets/component/loading/Loading.ets:14-16`、`PageLoading.ets:21-30`、`component/network/BaseNetWorkView.ets:62-90` 已有可见组件/状态分支，登录页未用 |
| 请求辅助边界 | `core/result/src/main/ets/RequestHelper.ets:68-70,103-129` 可配置 loading 并 finally 调关闭；但 `RequestUI.ets:11-12,18-19,26-27` 的 showLoading/hideLoading/toastError 均为空。不能据 helper 调用声称已显示或恢复 loading |

对应 Spec 的主要缺失：场景一的 Logo/双按钮/入口跳转；场景二的提示、三方图标/说明/可操作登录、页脚文案/主题色链接及真实详情；场景三的按钮区域比例、居中和区域内均匀排列。A1 的现有入口已实测可达，其余缺失与细化验收编号见 `spec/acceptance.md` 第 3–4 节，不能以“依赖存在”替代完成。

## 7. 前置环境、数据与真实歧义

| 前提/歧义 | 本地现状及后续处理 |
| --- | --- |
| 普通进入页面 | 无需账号，当前手机模拟器已满足；权限界面处理须纳入自动化步骤 |
| 服务端/测试账号 | 代码有基础 URL 和认证接口，但未验证在线状态；Spec 未提供有效账号、手机号、验证码或第三方凭据，不能声称能本地走完真实认证 |
| 第三方提供商环境（U2） | SDK/config、客户端应用、回调与账号条件未给出；微信真实启动与完整认证的完成范围需明确，QQ/支付宝概述要求保留，不能用“暂不支持”代替 |
| 协议正文（U4） | Spec 未提供正文或 URL，本题允许输入与已读代码尚未确定真实内容来源。本地资源/远端内容两种路径需保留；禁止自行编造正式协议正文 |
| 多尺寸（U1） | 现有窗口断点可作推荐映射，但 Spec 没有定义设备类型与数值阈值的对应关系；本轮未实测平板、大屏 |
| 宽度基准（U3） | Spec 手机写“屏幕全宽”，其他写“页面宽度”；窗口、内容、安全区/padding 的基准需明确，不能用内部 100% 掩盖外层留白 |
| WebDAV/分页/历史数据 | 本题 Spec 无此类要求，不适用；不为分析擅自引入服务或测试数据 |

U1–U4 的完整假设、推荐方式、证据等级与受影响条目在 `spec/acceptance.md` 第 5.2 节。本阶段列出而未自行作最终裁定；这些不影响交付分析文档，但会影响后续实现与最终网络/几何断言。

## 8. 测试可观测性风险与记录完整性

1. **缺少稳定 id（代码事实）**：定向检索 auth、MePage、MainPage、AppNavDestination、图标组件未发现 `.id()`。建议 id 及缺失状态逐项列在验收矩阵第 2 节；路由名不是 UI id。后续需要在真实组件补 id，并在设备上确认 Span 链接的独立可定位/可点击性。
2. **同名文本（实测与代码分别标注）**：`final-login-action.json:68-72` 的文本数组出现两次“登录”，因此单独按标题查找有歧义；基线协议资源也有重复名称，但资源重复本身不证明运行页面同时有重复节点。测试应限定目标页和节点。
3. **既有资源与 Spec 冲突（代码事实）**：`feature/auth/src/main/resources/base/element/string.json:76-81` 的短信入口资源为“验证码登录”，不是 Spec 的“手机号登录”；`:32-49` 的前缀为“登录即代表您已阅读并同意”，不是 Spec 的完整原句；`:200-205` 的“仅支持QQ”资源未被业务调用，也不能覆盖 Spec 微信要求。应以 Spec 逐字文案为准。
4. **样式/图案/比例不能只靠文字判定**：截图可见登录页当前没有这些元素；未来需用真实组件边界、密度和截图验证 Logo、圆角、填充/描边、主题色及区域比例。当前 9 项文字检查不是 41 项完整验收，更不是官方 F-point 统计。
5. **请求可观测性**：首页可能有其他后台请求；未来应隔离登录相关请求，记录真实授权与 HTTP 时序、loading 绑定和终态。当前没有点击处理器，不能伪称测试了成功/取消/失败网络分支；状态机候选与未决条件见验收矩阵第 8 节。
6. **采集过程限制**：早期仅用 Start-Transcript 未完整落盘原生命令 stdout，已改用 Tee-Object 或逐命令 JSON/stdout/stderr 采集并重新完整构建、安装、运行。原始失败和初检工具返回保留在本轮原生会话记录，旧不完整日志未删除；最终结论引用重采集后的证据。
7. **过程保存**：四角色真实派工、角色产物和主调度状态在 workflow；主/子会话 UUID 登记于 `workflow/state.json`，原生记录按其中的专用会话精确匹配到 traces/native。初始化总览会话按 AGENTS.md 排除，活跃会话快照不声称包含捕获后的事件。

本轮分析文档完成不代表业务功能完成；后续只可针对当前源码和已确认验收标准重新实施、构建、验证，再决定是否达到本地验收状态。
