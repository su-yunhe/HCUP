# cml-spec1 基线现状

本轮任务为 `spec-harness/0-analyze.md` 的分析阶段。以下区分 **Spec 明文**、**代码实证**、**构建实测**、**设备实测**和 **推断/未验证**。本阶段不修改业务代码，也不作功能实现或官方评分结论。

## 1. 快照与当前验证状态

| 项目 | 记录 |
| --- | --- |
| 工程/工作树根 | `D:/HCUP/cml-spec1`，没有另建 project 子目录 |
| 基线 HEAD | `7014cebd60f2181fac2a36d399ca16b3d6a175ab`，与 `spec/metadata.json:2` 一致；采用记录 HEAD 的方式，不额外打 tag |
| Spec SHA256 | `491ea9b5efe284f449873234ba0c86345a0cc2eece2e097898de06a2c4f59d4b` |
| metadata SHA256 | `8b4f53895d59cc4a74780c9d6d24d80ae59d236965755a7091f92375eb695768` |
| 源码完整性 | 677 个 tracked 文件与准备后指纹相同，暂存/未暂存 diff 为空，指定源码目录没有新增未跟踪构建输入；见 `workflow/analysis-code-fingerprint.json`、`traces/baseline-analysis/source-before.json`、`source-after-build.json`。ignored 的安装依赖及本地配置没有完整前后指纹，不将此结论扩为全部构建环境未变 |
| 构建 | 独立 clean 和 assembleHap 均退出 0；见第 2 节 |
| 安装/启动/实际操作 | **已完成未修改基线的安装、启动及入口探索**：独立 11245 安装/启动退出 0；保持麦克风拒绝，经最近任务恢复主窗口，完成横滑、纵滑和重启复核。实际为通知演示页，四底栏入口缺失；见第 3 节 |
| 功能验收 | 本轮基线 17 步为 2 fail、15 blocked、0 pass，未开展实现后验收。验收矩阵在 `spec/acceptance.md`，构建成功不能代替其中任一交互通过 |

独立角色证据：`workflow/requirements/acceptance-r1.md`、`workflow/design/baseline-static-r1.md`、`workflow/implementation/baseline-audit-r1.md`、`workflow/verification/baseline-r1.md`、`baseline-r2.md`。初始化总览会话没有作为功能开发或本轮运行证据使用。

## 2. 未修改基线的构建与原有告警

**构建实测**：工作目录为本题根，每个构建/设备 PowerShell 进程先加载本机覆盖环境。可重跑脚本为 `traces/baseline-analysis/build-baseline.ps1`。

```powershell
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
hvigorw clean --mode module -p product=default -p buildMode=debug --no-daemon
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

| 命令 | 时间（北京时间，2026-10-20） | 退出码 | 原始证据 |
| --- | --- | --- | --- |
| clean | 11:18:06–11:18:10 | 0 | `logs/analysis-baseline-clean.log` |
| assembleHap | 11:18:10–11:18:32 | 0 | `logs/analysis-baseline-assembleHap.log:1304` 为 `BUILD SUCCESSFUL` |

精确起止时间/命令见 `logs/analysis-baseline-build-results.json`。实际工具为 DevEco Studio 6.1.0.860 随附 hvigor，Node 18.20.1、Java JBR 21.0.8、SDK `D:/HarmonyDev/sdk/api23`，工具绝对位置和版本在 `logs/analysis-baseline-env.json`。工程配置目标版本为 `6.0.1(21)`（`build-profile.json5:7–9`），与本机可用 SDK/API 及实际设备版本分开记录。

本轮重建产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`，19,133,822 bytes，SHA256 `49a5284455f6b6f9c29873da1431d7542bfd233071b67b46e5f52851d68906a4`，见 `logs/analysis-baseline-hap.json`。`build-profile.json5:3` 的 signingConfigs 为空；未签名事实不等于已经实测安装被拒绝。

原有告警清单如下。完整逐条文件、行列及原文在 `traces/baseline-analysis/warnings-file-diagnostics.csv` / `.json`；全上下文以原始构建日志为准，不只保留分类计数。

| 类别 | 数量/状态 | 定位 |
| --- | --- | --- |
| ArkTS 带文件诊断合计 | 182：项目 31、依赖 151 | `traces/baseline-analysis/warnings-summary.json` |
| `Function may throw exceptions. Special handling is required.` | 31 | 项目 ContextUtil、PermissionUtils、ImageUtil、NotificationUtil、WindowAdapter 等；逐条见上述 CSV |
| `arkts-strict-typing-required` | 140 | 依赖声明，逐条见 CSV |
| `arkts-no-implicit-return-types` | 8 | 依赖声明，逐条见 CSV |
| `arkts-no-type-query` | 2 | 依赖声明，逐条见 CSV |
| `arkts-no-typing-with-this` | 1 | 依赖声明，逐条见 CSV |
| 资源冲突 | 日志出现 135 次，非唯一资源数 | placeholder / placeholder_float 的 base/en 资源；`logs/analysis-baseline-assembleHap.log` |
| 重名文件 | 有 | dayjs.min.js 与 dayjs.min.js?commonjs-entry；同日志 `:1290` |
| sourceMapsPath 缺失 | 有 | @ibestservices/ibest-ui-v2；同日志 `:1293` |
| 未配置签名 | 有 | product default；同日志 `:1300` |

与本题准备阶段保存的构建日志相比，182 条带文件诊断的有序多重集差异为空，见 `traces/baseline-analysis/warnings-compare-preparation.json`。该比较仅用于确认既有告警，没有读取总览会话、上游修复历史或其他题工程。本阶段未修复、抑制这些告警。

## 3. 安装与实操记录

### 环境失败及恢复

**历史设备实测**：r1/r2 的 `hdc list targets` 及 `aa dump -l` 预检发现 11237、11239、11241、11243 均有其他任务运行，起初未占用。创建本题专用 `CmlSpec1Baseline`（11245，2GB，实例数据在本题 traces）退出 0，但首次启动失败：本题实例 `Log/Emulator.log` 提示剩余内存小于 3GB，`Log/qemu.log` 报 `CreateFiber failed`。r2 可用物理内存约 1.09GiB，未进行无新条件的重复启动。内存/资源不足是中等证据假设，未写成已排除一切其他原因。失败过程保留在 `workflow/verification/baseline-r1.md`、`baseline-r2.md`。

用户明确选择“释放一台后使用本题独立实例”后，使用官方 `Emulator.exe -stop CmlSpec17Baseline` 正常停止 11243 对应的一台实例，退出 0；没有删除实例、清应用数据或修改他题工程。随后本题 11245 成功上线。原始授权及工具调用在本题原生会话；停止记录见 `logs/analysis-baseline-r3-stop-candidate.json`、`analysis-baseline-r3-stop-result.json`。本题实际设备是 Pura 90 Pro Max、1308×2880/560dpi、HarmonyOS 6.1.0.115/API23；版本查询日志为 `logs/analysis-baseline-r3-api-version.json`、`analysis-baseline-r3-software-version.json`。

### 本轮产物安装与启动

```powershell
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
hdc -t 127.0.0.1:11245 install entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t 127.0.0.1:11245 shell aa start -a EntryAbility -b com.joker.coolmall
```

两个命令均退出 0，分别明确返回 `install bundle successfully` 和 `start ability successfully`。安装时间为 2026-10-20 11:33:10，启动为 11:33:27（北京时间）；原始输出见 `logs/analysis-baseline-r3-install-unsigned.json`、`analysis-baseline-r3-launch-first.json`。安装的是第 2 节哈希绑定的本轮重建 unsigned HAP；该模拟器接受此包，**未进行额外签名，也未改生产签名配置**。

### 权限路径与真实主入口

首次启动显示麦克风权限弹窗及其后的系统权限设置流程。本轮选择拒绝；`permission-denied.png` 仅表示“不允许”被勾选、仍待“确定”，不表示弹窗已经关闭。确认拒绝或关闭权限页会进入系统 Settings.AppDetail，直接 Back 可回 launcher，重新启动则再次出现权限页。此基线行为与 `PermissionUtils.ets:50–59` 的二次请求及 `:101–108`、`:155–159` 的打开设置逻辑吻合；本阶段只记录不修复。

最终通过系统最近任务选择“青商城”卡片，正常恢复尚存的 EntryAbility 主窗口，**没有授予麦克风权限**。未遮挡的 `existing-app-window.png` / `existing-app-window-after.png` 以及同期 `existing-app-window.json` 确认：实际页面标题“主页面”，正文“主页面内容视图”，下有申请通知权限、预设默认配置、发送消息、清楚通知/角标等通知演示按钮。四个底栏文字“首页”“分类”“购物车”“我的”在应用窗口内均为 0，未发现相应底栏。

所有截图/树在 `traces/baseline-analysis/r3/`。原始 `first.json` 捕获了启动过渡中的 launcher，不能与稍后的 first.png 混为同一时刻权威 UI；文件名 `settled-home` 也只是采集标签，实际是系统 launcher。正式结论使用恢复后的应用窗口截图与同期树；应用窗口统计在 `observed-app-summary.json`，排除了系统窗口。

### 横滑、纵滑及重启复核

| 实际动作 | 设备结果 | 权威证据（均位于 `traces/baseline-analysis/r3/`） |
| --- | --- | --- |
| 通知主页面内容区左滑：`uitest uiInput swipe 1100 2100 200 2100 1200` | 命令退出 0，仍是相同通知演示页，没有切换到分类；不是在不存在的首页上完成 Spec 滑动 | `content-left.png`、`content-left-after.png`、`content-left.json` |
| 同内容区上滑以向下浏览：`uitest uiInput swipe 1050 2200 1050 800 1200` | 退出 0，通知页文字及位置不变，不能建立首页“领取”滚出视口的前置 | `content-up.png`、`content-up-after.png`、`content-up.json` |
| `aa force-stop com.joker.coolmall` 后重新 `aa start`，处理同样权限路径，再经最近任务恢复 | stop/start 均退出 0，仍回相同通知页；没有出现四底栏或默认首页。force-stop 是测试动作，不是应用崩溃 | `restart-permission.json`、`restarted-app-window.png`、`restarted-app-window-after.png`、`restarted-app-window.json` |

完整命令、采集时间、退出码在 `logs/analysis-baseline-r3-probe-commands.jsonl`；设备操作与报告索引为 `workflow/verification/baseline-r3.md`。四个权威应用窗口的文字/边界一致，Tabs、TabContent、Swiper、Scroll、List 的树节点统计均为 0；这是当前页面观察，不是要求必须使用某组件。

本轮未观察到应用崩溃；日志仍有 QoS 等系统/框架错误，不将其笼统写成“无错误”。源码和 HAP 在实操结束后再次核对：677 tracked 文件无变化，HAP 哈希与第 2 节一致，见 `traces/baseline-analysis/r3/source-final-comparison.json`。

**基线结论**：安装/启动及真实主入口探索已完成；四底栏入口缺失为实际观察。r3 按 17 个 Spec 步骤记录 **2 fail、15 blocked、0 pass**；这不是官方 F-point 数或分值。依赖首页/分类/购物车/我的内容、Lottie 图标或“领取”的后续点击、动画和回顶检查因前置不存在而 blocked/not_run，不能声称已全部执行或通过。逐步骤状态详见 r3 报告。

## 4. Spec 入口、路由与调用点

以下均为 **代码实证**，运行状态以第 3 节为准。

| 层级 | 当前源码行为 | 文件:行号 |
| --- | --- | --- |
| 模块入口 | `mainElement` 为 EntryAbility，srcEntry 指向 Ability | `entry/src/main/module.json5:6`、`:17–18` |
| 页面清单 | 仅注册 `view/EntryPage` | `entry/src/main/resources/base/profile/main_pages.json:2–4` |
| Ability | `onCreate` 注册路由；ORM 初始化后 loadContent | `entry/src/main/ets/entryability/EntryAbility.ets:33–37`、`:50–53`、`:125–126` |
| 根页 | `EntryPage` 构建 `NavigationHost()` | `entry/src/main/ets/view/EntryPage.ets:39–42` |
| 导航宿主 | 提供 NavPathStack，Navigation 根直接挂载 MainPage | `entry/src/main/ets/navigation/NavigationHost.ets:13–17`、`:36–42` |
| 主页面 | AppNavDestination 标题“主页面”；正文“主页面内容视图”和通知演示按钮 | `feature/main/src/main/ets/view/MainPage.ets:25–31`、`:39–130` |

路由与独立目标页如下。**已注册目标路由不能证明已有底栏入口。** MainPage 全文没有组合四页，也没有向下列四个子路由跳转。

| 路由 | 注册点 | builder 调用点 | 页面当前源码 |
| --- | --- | --- | --- |
| `main/main` | `feature/main/src/main/ets/navigation/MainGraph.ets:17` | `feature/main/src/main/ets/navigation/MainNav.ets:9–10` | MainPage 通知演示 |
| `main/home` | 同文件 `:18` | `feature/main/src/main/ets/navigation/HomeNav.ets:9–10` | `feature/main/src/main/ets/view/HomePage.ets:20–35`，标题“首页”与“首页内容视图” |
| `main/category` | 同文件 `:19` | `feature/main/src/main/ets/navigation/CategoryNav.ets:9–10` | 同目录 `CategoryPage.ets:20–35`，标题“分类”与“分类页面内容视图” |
| `main/cart` | 同文件 `:20` | `feature/main/src/main/ets/navigation/CartNav.ets:9–10` | 同目录 `CartPage.ets:20–35`，标题“购物车”与“购物车页面内容视图” |
| `main/me` | 同文件 `:21` | `feature/main/src/main/ets/navigation/MeNav.ets:9–10` | 同目录 `MePage.ets:20–35`，标题“我的”与“我的页面内容视图” |

路由值定义在 `core/navigation/src/main/ets/routers/MainRoutes.ts:5–25`。注册容器使用 `Map<string, WrappedBuilder<[]>>`（`core/navigation/src/main/ets/RouteBuild.ets:6`、`:13–14`、`:22–23`），导航宿主查找 builder 的调用位于 `entry/src/main/ets/navigation/NavigationHost.ets:26–28`。

## 5. 组件、状态、数据、网络和本地存储

| 范围 | 代码事实 | 对本题的限制 |
| --- | --- | --- |
| 主页面状态 | MainPage `:18–19` 持有 `@Local MainViewModel`；`feature/main/src/main/ets/viewmodel/MainViewModel.ets:7–9` 为空 BaseViewModel 子类 | 没有底栏索引、点击/滑动共用状态或动画控制器 |
| 四目标页状态 | 各页 `:13–14` 持有 @Local VM；同目录 viewmodel 下 Home/Category/Cart/MeViewModel 均 `:7–9` 为空类 | 没有首页数据加载、回顶、购物车加载或个人信息刷新接入 |
| 首页滚动 | `feature/main/src/main/ets/view/HomePage.ets:34–35` 只有占位 Text | 没有 Scroll/List/Grid、Scroller 或顶部“领取”入口 |
| 通用滚动/刷新 | `core/ui/src/main/ets/component/refresh/RefreshLayout.ets:22–23`、`:42–51` 声明 scroller 并传给 IBestPullRefresh | 应用业务源码没有 RefreshLayout 调用，不能当作首页已具备回顶；回顶也不等于刷新 |
| 首页实体 | `core/model/src/main/ets/entity/Home.ets:14–38`、`:44–50` 定义 banner/category/categoryAll/flashSale/recommend/coupon/goods 并映射 | 只有数据结构，当前 HomePage 未接入；不能当作“限时精选”“推荐商品”“领取”UI 已存在 |
| 首页仓库 | `core/data/src/main/ets/repository/PageRepository.ets:18–19`、`:26–27` 委托 getHomeData | 当前主页面与四目标页没有调用者 |
| 网络请求 | `core/network/src/main/ets/datasource/page/PageNetworkDataSourceImpl.ets:15–18` 为 GET page/home；`NetworkClient.ets:16`、`:19–24` 配基础地址和 10 秒超时 | 定义请求不等于启动会请求；服务可达性、真实响应和优惠券数据均未验证 |
| 拦截器 | `core/network/src/main/ets/interceptors/AppInterceptors.ets:10–15`、`:20–25` 原样返回或拒绝错误 | 未绑定导航、动画、底栏 loading，未注入 token |
| 网络状态模式 | `core/base/src/main/ets/state/BaseNetWorkUiState.ets:5–17` 定义 LOADING/SUCCESS/ERROR；`BaseNetWorkViewModel.ets:47–53`、`:95–112` 处理请求状态 | 可复用模式；五个主模块 VM 当前均没有接入，不是本题既有状态机 |
| 购物车本地能力 | `core/data/src/main/ets/repository/CartRepository.ets:18–19`、`:82–83`；`core/database/src/main/ets/datasource/cart/CartLocalDataSourceImpl.ets:24–35`、`:128–130` | 有本地数据库和仓库，CartPage/VM 未调用；本 Spec 未要求商品操作 |
| 数据库初始化 | `entry/src/main/ets/entryability/EntryAbility.ets:118–119` 初始化 app.db | 不证明保存或恢复标签索引 |
| 用户持久化 | `core/state/src/main/ets/UserState.ets:158–159`、`:169–175` 使用 PersistenceV2 | 当前主模块没有标签持久化调用 |
| 账户存储 | `core/datastore/src/main/ets/datasource/account/AccountStoreDataSourceImpl.ets:18–26`、`:32–33`、`:41–42` 使用 Preferences；`core/util/src/main/ets/storage/PreferencesUtil.ets:45–49` 写入并 flush | 账户存储存在不等于底栏必须登录或需新增存储 |

应用源码和非依赖 manifest 的定向检索未发现 Lottie 引入/调用、Swiper/Tabs/TabContent、底栏选中索引或回顶事件链。检索范围与命令保存在 `workflow/design/baseline-static-r1.md` 第 2 节，排除 oh_modules/build；这是源码范围内的缺失证据，不是设备动态验证。

## 6. 可复用能力与缺失项

**可复用的代码事实**：

- 既有入口 MainPage、四个独立页面及 MainGraph 路由注册，见第 4 节；后续应沿当前入口接入需求，不能假定隐藏测试会走新建的独立入口。
- 现有 @ComponentV2/@Local ViewModel 结构和 AppNavDestination 生命周期转发（`core/ui/src/main/ets/component/navdestination/AppNavDestination.ets:68–69`、`:76–77`、`:92–93`、`:126–130`；`core/base/src/main/ets/viewmodel/BaseViewModel.ets:11–12`、`:25–26`、`:55–56`、`:63–64`）。空生命周期钩子本身没有实现业务。
- NavPathStack 和 RouteBuild 的具名路由模式、Home 实体/仓库以及网络状态模式、通用 RefreshLayout 和购物车本地仓库，均有第 4、5 节证据。复用与否留待功能阶段方案，不在本轮选型或改造。

**Spec 明文到源码缺失的映射**：

| Spec 场景 | 验收项 | 当前源码缺口 |
| --- | --- | --- |
| 场景一，`spec/requirement.md:7–15` | A1–A9 | 底部四标签、默认首页组合、点击切页、目标 Lottie 动画和黑/灰复位均未接入 MainPage |
| 场景二，`:21–28` | A10–A15 | 内容区横滑切页、底栏选中与图标动画联动，以及滑动后点击“我的”的统一状态链未实现 |
| 场景三，`:34–41` | A16–A22 | 初始化自动播放、离开首页回第一帧静止、返回首页重新播放一次、首页文字黑色未实现 |
| 场景四，`:47–54` | A23–A28 | 可纵向浏览首页、顶部“领取”入口、已选首页重击回顶及“不切页、不额外重播”分支未实现 |

以上为源码缺口映射；第 3 节已用设备确认主入口仍是通知演示页、无底栏。直接观察到的入口缺失与依赖缺失入口而 blocked/not_run 的后续操作分别记录在 r3，不把所有动作都写成已执行 fail。本阶段只记录，不修复。

## 7. 前置环境需求及网络边界

- **代码实证**：根 MainPage 直接挂载；`core/navigation/src/main/ets/NavigationService.ets:56–73` 实现登录拦截，但 `core/navigation/src/main/ets/RouteInterceptor.ts:16–37` 不包含 main 的五个路由。当前代码没有“必须登录后才显示底栏”的前置证据。
- **Spec 明文**：四场景均无登录、WebDAV、领券交易、API 请求次数、loading、重试按钮或服务器响应要求（`spec/requirement.md:1–54`）。“领取”是回顶可见性的锚点，不是要求点击领券；“限时精选”“推荐商品”是浏览区域举例，不能扩成商品交易、排序或分页任务。
- **未验证**：本机未实测账户、后台接口或真实首页数据供应。网络层存在的 GET page/home 没有被当前 HomePage 调用，不能将后台假设为已就绪或本题启动必要条件。
- **确定前置缺口**：场景四需要顶部“领取”入口和足够长的可滚动内容；当前源码没有它们。后续实现必须建立该可观察前置，不能用“没有后端数据”豁免场景。
- **首屏权限的代码与设备证据**：EntryAbility 在 loadContent 回调请求麦克风权限（`entry/src/main/ets/entryability/EntryAbility.ets:52–57`）；请求点为 `core/util/src/main/ets/permission/PermissionUtils.ets:195–196`，声明为 `entry/src/main/module.json5:61–69`。本轮实际出现弹窗；拒绝后跳转设置，最终经最近任务恢复主窗口且未授权，完整路径见第 3 节。
- **网络适用性**：本题未规定必须发送的请求，验收矩阵逐动作列明此点及 loading 的适用性，不虚构导航 API 或请求状态机。若后续保留业务加载，须与本地导航/动画/回顶状态区分，并记录真实完成、空数据及失败恢复；具体接口义务须另有需求依据。

## 8. 测试可观测性风险

1. **缺少稳定 ID**：应用源码范围 `.id(` 检索没有命中，五个主模块页面及导航容器未设置业务稳定 ID；具体范围见静态报告第 5 节。验收矩阵中的 ID 都是本地自动化可观测性建议，**需实现时补 `.id()`**，不冒充已有组件；Spec 没有指定 ID 名称，不将建议命名升级成独立业务验收项。
2. **同名文本歧义**：“首页”“分类”“购物车”“我的”目前是目标页面标题参数，未来底栏也会同名。必须定位底栏容器、点击标签、文字、图标和当前活动页；仅找到文本不能证明底部位置、当前选择或页面切换。
3. **存在不等于可见**：分页器可能预建非活动页；“领取”滚出屏幕后也可能仍在 UI 树。应断言活动内容和屏幕可视范围/几何位置，不能只断言节点存在。
4. **动画需要动态证据**：Lottie 播放、首页第一帧静止、返回只播一次及重击不新增播放都不能由一张截图或颜色变化证明。需要多帧/播放状态证据，动画播放计数也不能由 ID 推得；未能观察时保留未验证。
5. **边界不可混同**：从其他标签返回首页与点击已选首页的要求不同。纵向回顶可以有滚动动画，Spec 禁止的是同页重击触发切页/额外 Lottie；不得因此禁止纵向滚动过渡。
6. **现有测试覆盖缺口**：`entry/src/ohosTest/ets/test/Ability.test.ets:25–32` 与 `entry/src/test/LocalUnit.test.ets:24–30` 是字符串断言模板，没有覆盖导航、动画或回顶。`test-harness/README.md:74` 建议稳定 `.id()`/BY.key，`:6–8` 说明本地框架不是官方评测器。当前未执行 Hypium 需求测试。

## 9. 未解决项与恢复点

- 本轮分析范围已经完成：验收矩阵、未修改基线构建/安装/启动/实操、源码审计与缺口记录齐备。功能需求尚未实现或验收通过；不存在的底栏及后续能力留待后续明确的实现阶段，本轮不自动进入编码。
- Spec 未规定的端点循环、非首页重击、暖恢复、动画素材/时长/非首页终帧、跨标签返回的滚动位置，均在验收矩阵 A40–A44 单独列假设与推荐，不擅定为官方要求，也不据此阻断本轮分析。
- 文档与当前源码对应；若后续源码变化，需重新计算指纹并重跑受影响的检查。本轮只允许文档、日志和工作流记录变化。
- 未访问其他题源码、题包、上游提交/PR/Issue/补丁或副本；没有自动上传、发布或提交赛事成果。没有人工改代码；设备环境选择来自用户本轮回复。
