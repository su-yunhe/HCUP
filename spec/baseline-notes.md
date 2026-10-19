# cmu-spec114 基线记录

标注约定：【代码】= 读源码得出，附 `文件:行号`；【实测】= 构建/模拟器走查得出，附日志位置；【推断】= 未直接验证的推测；【未验证】= 明确没有验证。

## 1. 基线快照标识

- `spec/metadata.json` 的 `base_commit`：`ebe2fbceaf5270ef0f5302edc4f77fa5962b0a3f`（tag `base/cmu-spec114`）。
- 当前 HEAD：`bb23a626e392618c4f1ab916a3cb8a4b68b2f024`（分支 `dev`），已打 tag **`baseline-cmu-spec114`** 指向该提交。
- `ebe2fbc..bb23a62` 只改了 `oh-package-lock.json5`（+2/-1，ohpm install 重建锁文件），不涉及业务代码。【实测】`git diff --stat`
- 工作区存在一处**未提交**改动：`build-profile.json5` 在 `products[0]` 增加 `"targetSdkVersion": "6.1.0(23)"`。文件 mtime 为 2026-10-19 13:20:06，与 `oh-package-lock.json5` 被重写的时间（13:20:07）相同，【推断】是 DevEco Studio 打开工程同步时自动写入，并非本阶段分析操作所改。
  - 【实测】在临时 worktree 中用 tag 内容（不含该改动）构建：同样 BUILD SUCCESSFUL、同样 588 条 ArkTS 告警，HAP 中 `targetAPIVersion` 同为 `60100023`。即该改动对产物无影响。
  - 决策（2026-10-19 用户确认）：**保留**该改动，不还原；作为环境改动在提交材料中说明（来源为 DevEco 同步自动写入、对产物无影响、已用不含该改动的提交对照构建验证）。

## 2. 构建基线状态

构建命令（工程根目录执行）【实测】：

```bash
export DEVECO_SDK_HOME=/Applications/DevEco-Studio.app/Contents/sdk
export JAVA_HOME=/Applications/DevEco-Studio.app/Contents/jbr/Contents/Home
export PATH=$JAVA_HOME/bin:/Applications/DevEco-Studio.app/Contents/tools/node/bin:/Applications/DevEco-Studio.app/Contents/tools/hvigor/bin:$PATH
hvigorw clean --no-daemon
hvigorw assembleHap --mode module -p module=entry@default -p product=default -p buildMode=debug --no-daemon
```

- 结果：BUILD SUCCESSFUL（约 8.4s），产物 `entry/build/default/outputs/default/entry-default-unsigned.hap`，`versionName 0.9.2 / versionCode 102 / minAPIVersion 50000012 / targetAPIVersion 60100023 / compileSdkVersion 6.1.0.105`。完整日志：`logs/baseline-build-clean.log`（另有早先一次构建日志 `logs/baseline-build.log`）。
- 环境坑【实测】：不设 `JAVA_HOME` 时 `PackageHap` 报 `00308018 Unable to locate a Java Runtime`，必须用 DevEco 自带 JBR。
- 安装：`hdc -t 127.0.0.1:5555 install -r <hap>` → `install bundle successfully`（未签名 HAP 可装到模拟器）。`logs/baseline-install.log`
- SDK：DevEco 内置 HarmonyOS 6.1.0（API 23，`6.1.0.105`）。

已有告警清单（后续对比是否新增的基准）：

- 非 ArkTS 告警 2 条：`No signingConfig found for product default`；`Warning: 'page_show' conflict, first declared.`
- ArkTS 告警共 **588** 条：其中 552 条来自 `oh_modules/@pura/harmony-utils`（三方库，不计）；**`entry/src` 内 36 条**：

| 文件（`entry/src/main/ets/` 下） | 位置 → 告警 |
| --- | --- |
| `pages/Settings.ets` | 33:21 px2vp deprecated |
| `components/head/SettingsHead.ets` | 13:24 showToast deprecated |
| `components/main/SearchComponent.ets` | 26:20 pushUrl deprecated；30:33 showToast deprecated |
| `components/head/IndexHead.ets` | 37:18、42:18 pushUrl deprecated |
| `components/head/CommonHead.ets` | 15:21 px2vp deprecated |
| `components/buttons/BackButton.ets` | 13:16 back deprecated |
| `pages/Index.ets` | 41:21 px2vp deprecated |
| `pages/login/WebLogin.ets` | 42:24 vp2px deprecated；58:7 Function may throw exceptions；58:20 showToast deprecated |
| `pages/SongsListPage.ets` | 20:48 getParams deprecated；55:41、61:21 px2vp deprecated |
| `pages/PlayListPage.ets` | 20:46、21:46 getParams deprecated；92:45、110:21 px2vp deprecated |
| `pages/LoginPage.ets` | 23:20 replaceUrl deprecated；32:26 showDialog deprecated |
| `api/getLoginStatus.ets` | 22:20 showToast；25:14 back；29:5 may throw；29:18 showToast |
| `common/functions/LogOut.ets` | 13:3 may throw；13:16 showToast |
| `components/sheets/MeSheet.ets` | 19:20 pushUrl；34:31 px2vp |
| `components/sheets/SongSheet.ets` | 68:50 px2vp |
| `components/sheets/LoginHelpSheet.ets` | 21:22 px2vp |
| `components/main/PlayListCard.ets` | 31:14 pushUrl |
| `components/dialog/DownloadDialog.ets` | 62:30 showToast；108:3、109:3 may throw；109:16 showToast |

注意：本题沿用基线写法（`router.pushUrl`、`promptAction.showToast`、`px2vp`），新代码会产生同类 deprecated 告警。决策（2026-10-19 用户确认）：**接受同类 deprecated 告警增加**，新代码与基线写法保持一致，不为消除告警改用 `getUIContext()` 系列 API；但不得引入其它类别的新告警（如 `Function may throw exceptions`、类型/语法类告警），也不得出现任何 ERROR。

## 3. Spec 入口当前位置

【实测】模拟器走查（`logs/baseline-walk/walk.log`、`walk5.log`，截图同目录）与【代码】对照：

| Spec 描述 | 基线位置 | 实测 |
| --- | --- | --- |
| 应用启动页 | `EntryAbility.ets:25` `windowStage.loadContent('pages/Index')`；路由表 `resources/base/profile/main_pages.json:2-10` | 冷启动进入首页，顶栏标题“云音汇” |
| 首页右上角更多按钮 | `components/head/IndexHead.ets:22-23` `CommonCircleButton(...ic_public_more_filled).bindMenu(this.MoreMenu())` | 顶栏右侧 Button，bounds `[1151,137][1274,259]`，无文本无 id |
| 菜单“设置” | `IndexHead.ets:35-38` `MenuItem({content:"设置"}).onClick → router.pushUrl({ url:'pages/Settings' })` | 菜单两项“设置”“下载管理”，点击进入设置页 |
| 设置页 | `pages/Settings.ets:12-38`（`@Entry struct Settings`），标题 `components/head/SettingsHead.ets:10` | 标题“设置”；行“当前版本 / 0.9.2 - 测试版”“隐私政策 / 前往查看本软件的隐私政策”“问题反馈 / chenlvin@126.com\n或 GitHub issue”；底部“云音汇 @Chenlvin\nGitHub: CloudMusic-HarmonyOSNext” |
| 版本值 | `Settings.ets:45` `Constants.VERSION + Constants.VER_DESC`；`common/constants/Constants.ets:2-3`（`'0.9.2'`、`' - 测试版'`） | 显示“0.9.2 - 测试版” |
| 清单版本 | `AppScope/app.json5:5-6`（`versionCode 102`、`versionName "0.9.2"`） | `bm dump` 输出 `versionName "0.9.2"`、`versionCode 102` |
| 隐私政策入口 | `Settings.ets:6-10` 定义 `wantInfo`（`ohos.want.action.viewData`、`entity.system.browsable`、`https://docs.chenlvin.cc/cloudmusic/#/privacy`）；`Settings.ets:70-73` 点击 `AppUtil.getContext().startAbility(wantInfo)` | 点击后 `current_app = com.huawei.hmos.browser`，浏览器空白页；连续两次 `press_back` 仍停在浏览器 |
| 底部项目信息 | `Settings.ets:78-88`，点击复制 `Settings.ets:100-106` | 单个 Text，含换行 |
| 首页搜索框 | `components/main/SearchComponent.ets:12` `TextInput({ placeholder: '请输入搜索词' })`，未设 placeholderColor/fontColor | hint=“请输入搜索词” |
| 搜索按钮 | `SearchComponent.ets:18-31`；判断 `if(this.searchKeyword)` → `router.pushUrl('pages/SongsListPage')`，否则 `promptAction.showToast({ message: '请输入搜索词' })`（:30） | 空输入 Toast“请输入搜索词”、不跳转；纯空格进入结果页并一直转圈 |
| 搜索结果页 | `pages/SongsListPage.ets` | 空格关键词只显示 `LoadingProgress` |

## 4. 相关现状

- 页面组件【代码】：全部为 `@Entry` 页面 + `router`（`@kit.ArkUI`）跳转，`main_pages.json` 注册 7 个页面；未使用 Navigation/NavDestination（全工程 grep 无匹配）。页面统一写法：根 `Stack` + `.padding({ top: px2vp(this.topRectHeight) })` + `.backgroundColor($r('app.color.main'))`（如 `Settings.ets:19-36`、`Index.ets:23-44`）。
- 标题栏【代码】：设置页用专用 `SettingsHead`（返回按钮 + “设置” + 分享按钮，`SettingsHead.ets:8-15`）；其它子页用通用 `CommonHead({ title })`（返回按钮 + 标题，自身带顶部避让 padding、高 90，`CommonHead.ets:10-18`）。返回按钮 `BackButton.ets:11-14` 调 `router.back()`。
- 状态模型【代码】：组件内 `@State`（如 `SearchComponent.searchKeyword`，`SearchComponent.ets:5`，由 `onChange` 回写 :13-15）；全局用 `AppStorage` + `@StorageProp`（`topRectHeight`、`bottomRectHeight` 在 `EntryAbility.ets:46,51` 写入；`isValidCookie`、`cookie` 用于登录态）。
- 数据模型【代码】：`common/entities/*.ets`（PlayList、SongsResult 等），本题不涉及。
- 网络服务【代码】：`common/utils/HttpRequestUtil.ets` 封装 `http.createHttp()` GET；`api/*.ets` 拼 `Constants.ROOT_URL`（`Constants.ets:7` 写死 `http://111.229.38.178:3000`）。首页 `Index.ets:12-20` 每次 onPageShow 发两个测试请求，仅打印日志。本题三个场景都不需要新增或修改 HTTP 调用。
- Web 组件【代码】：唯一用例 `pages/login/WebLogin.ets:2,13,20-30`（`webview.WebviewController` + `Web({ src: '', controller })`，`onControllerAttached` 中 `loadUrl`）。
- 本地存储【代码】：`common/utils/PreferencesUtils.ets`（`preferences` 封装，`EntryAbility.ets:16` 加载 `UserPreference`），本题不涉及持久化。
- Toast【代码】：两种写法并存——`promptAction.showToast({ message })`（`SearchComponent.ets:30`、`SettingsHead.ets:13`）与 `ToastUtil.showToast(...)`（`Settings.ets:60,105`）。
- 权限【代码】：`module.json5:37-42` 已有 `ohos.permission.INTERNET`，Web 加载网络页无需新增权限。

## 5. 可复用的既有实现

- **PrivacyPage 骨架**：照 `WebLogin.ets` —— `CommonHead({ title: ... })` 作自有标题栏 + `Web` + `WebviewController`；去掉登录相关的 Help 和按钮即可。官方测试沿现有流程（设置页点击 → 新页）进入，沿用同款结构最稳。
- **路由**：`router.pushUrl({ url: 'pages/PrivacyPage' }, router.RouterMode.Single)` + 在 `main_pages.json` 追加 `"pages/PrivacyPage"`，与 `IndexHead.ets:37` 写法一致（`RouterMode.Single` 按 acceptance U6 决策只加在隐私页入口）；返回用既有 `BackButton`（`router.back()`）与系统返回。
- **版本号**：改 `Constants.VERSION`（`Constants.ets:2`）为 `'0.9.3'`，`AppScope/app.json5:5-6` 改为 `versionCode 103`、`versionName "0.9.3"`（acceptance U1/U2 决策）；`Settings.ets:45` 的拼接逻辑不动。
- **搜索文案**：`SearchComponent.ets:12,30` 两处；可在组件内或 `Constants` 中定义一个常量供 placeholder 与 Toast 共用（工程无 i18n 字符串资源用法，界面文字均为硬编码中文）。
- **样式扩展**：工程习惯用 `@Extend(Text)`（`Settings.ets:91-106`）；颜色资源 `resources/base/element/color.json`（`main`、`reverse`、`start_window_background`），暗色在 `resources/dark/element/color.json`。

## 6. 缺失项（Spec 要求、基线完全没有）

1. `PrivacyPage` 页面文件与路由注册（`main_pages.json` 无此页）。
2. 应用内打开隐私政策的跳转逻辑（基线只有外部 Want）。
3. 0.9.3 版本号（清单与常量均为 0.9.2）。
4. “请输入搜索内容”文案（placeholder 与 Toast）。
5. 搜索框 `placeholderColor` / `fontColor`（`SearchComponent.ets:12` 均未设置）。
6. 全工程没有任何 `.id()`（grep `\.id\(` 无匹配），自测选择器只能靠文本/类型/坐标。

## 7. 前置环境需求

- 登录账号：不需要。【实测】未登录状态（首页显示“登录账号\n以显示你的歌单”）下三个场景全部可走通。
- 服务端：不需要。设置页、隐私页、空搜索都不依赖 `ROOT_URL` 服务；只有非空搜索（回归项 C10）需要服务，本地不可用时结果页一直转圈（基线缺陷）。官方答疑提到的"API 设置页"在本基线不存在，地址写死在 `Constants.ets:7`。
- 互联网：隐私页正文需访问 `docs.chenlvin.cc`；Spec 明确内容未加载也要通过，官方答疑称不比对 URL 与正文。【实测】本机模拟器打开该地址时浏览器为空白页（是否可达未验证）。
- WebDAV / 测试数据：不需要。
- 模拟器【实测】：`harness.env_check` → `emulator 6.1.0.115`、`1308×2880`，"环境与官方评测规格一致"。
- Hypium 运行【实测】：必须把 `.../sdk/default/openharmony/toolchains`（含 `hdc`）加入 `PATH`，否则 `UiDriver.connect` 报 `Connection refused`；Hypium 在 cwd 生成 `reports/`、`tmp_hypium/`，应在 `logs/` 下运行（本次已把误生成在工程根目录的报告移到 `logs/baseline-walk/hypium-reports/`）。

## 8. 测试可观测性风险

| 风险 | 证据 | 影响与对策 |
| --- | --- | --- |
| 全工程无 `.id()` | 【代码】grep 无匹配 | 自测可补 id；官方测试不会依赖我们的 id，所以既有组件的类型、文本、顺序都不能改 |
| 图标按钮无文本 | 【实测】首页 3 个 Button（菜单、更多、搜索）、设置页返回/分享按钮 text 均为空 | 只能按 `BY.type("Button")` + bounds 排序定位；新增页面不要在标题栏前插入额外 Button，以免改变顺序 |
| placeholder 不是 text | 【实测】`BY.text("请输入搜索词")` → False；`BY.hint("请输入搜索词")` → True；`getHint()` 返回该串、`getText()` 为空 | 场景三断言必须用 `BY.hint` / `getHint()` |
| 底部信息是单个带 `\n` 的 Text | 【实测】`BY.text("云音汇 @Chenlvin")` EQUALS → False，CONTAINS → True；`CloudMusic-HarmonyOSNext` CONTAINS → True | 见 acceptance U3（已定：保持单个 Text 不拆，自测用 CONTAINS） |
| “隐私政策”同名文本 | 【实测】设置页 EQUALS 计数 1（左侧标签）；PrivacyPage 标题将同名 | router 压栈后下层页面节点不在 UI 树（【实测】进入下载管理页时首页“云音汇”、TextInput 均查不到），故 router 方案下隐私页上只会命中标题；若改用 Navigation/半模态则可能同屏两处 |
| “设置”同名文本 | 【实测】菜单项与设置页标题同为“设置”，设置页内计数 1 | 菜单关闭后不冲突；断言设置页时可加 `BY.text("当前版本")` 辅助 |
| “云音汇”文本 | 【实测】首页 EQUALS 计数 1（顶栏标题）；设置页 CONTAINS 计数 1（底部信息） | 场景三"首页标识"用 EQUALS，避免与设置页底部混淆 |
| Web 内部节点 | 【未验证】网页加载成功后其内部文字是否进入 Hypium UI 树 | 若进入且网页含“隐私政策”字样，按文本计数的断言可能 >1；实现后需在联网状态下实测 |
| 颜色不可观测 | 【实测】TextInput `getAllProperties()` 只有 `backgroundColor`（`#FFDBD9D9`），无字体色/占位色 | C3 只能代码审查 + 截图 |
| Toast 可观测 | 【实测】`start_listen_toast` + `get_latest_toast(timeout=3)` 能取到文本；Toast 同时以 `Toast` 类型节点出现在 UI 树（点击后约 1s 抓树仍在，持续时长未测） | C5 两种方式均可断言 |
| 前台应用判定 | 【实测】`driver.current_app()` 返回 `(bundle, ability)`，基线点击隐私入口后为 `('com.huawei.hmos.browser','MainAbility')` | B2 直接用它断言 |
| 返回路径 | 【实测】设置页 `press_back` 与左上返回按钮都能回首页；回首页后 hint 仍在 | 新隐私页需保证同样两种返回都可用 |

## 9. 基线缺陷（只记录，本阶段不修）

1. 隐私政策走外部 Want，返回后无法回到应用（`Settings.ets:6-10,72`）——本题需求本身要改。
2. 搜索关键词不 `trim()`，纯空格会进入结果页（`SearchComponent.ets:25`）。
3. `SongsListPage.loadSongs` 失败时 `catch` 不重置 `isLoading`，请求失败后永久转圈（`SongsListPage.ets:35-37`）。【实测】空格关键词截图 `logs/baseline-walk/21_space_search_page.jpeg`。
4. 首页每次显示都发两个测试请求（`Index.ets:12-20`），与本题无关。

## 10. 走查记录索引

- `logs/baseline-walk/walk.log`：第 1–4 轮（首页、空/空格搜索、设置页、隐私入口、返回、WebLogin 的 Web 选择器、router 压栈节点可见性）。对应脚本 `cmu114_walk.py`～`cmu114_walk4.py`。
- `logs/baseline-walk/walk5.log`：第 5 轮（`BY.hint`、TextInput 属性、文本唯一性计数、快速连点空搜索、两种返回、重启后重进）。脚本 `cmu114_walk5.py`。
- 截图：`01_home`、`02_after_empty_search`、`05_settings`、`06_after_privacy_click`（外部浏览器空白页）、`21_space_search_page`、`23_weblogin`。
- Hypium 原始报告：`logs/baseline-walk/hypium-reports/`。
