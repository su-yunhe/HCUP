# cml-spec1 基线静态映射 r1

- 角色：`harmony_design`；会话：`01a15750-6e04-72b1-8b4d-5c2ff6dfc61b`。
- 范围：仅分析当前题的 Spec 和当前工作树，不生成实现方案，不修改生产代码、测试、全局 workflow 状态或构建配置。
- 基线：`git rev-parse HEAD` = `7014cebd60f2181fac2a36d399ca16b3d6a175ab`。本次检查时 `git status --short` 无已跟踪源码变更，仅有本题资料/日志等未跟踪目录。
- 输入校验：`spec/requirement.md` SHA256 = `491ea9b5efe284f449873234ba0c86345a0cc2eece2e097898de06a2c4f59d4b`；`spec/metadata.json` SHA256 = `8b4f53895d59cc4a74780c9d6d24d80ae59d236965755a7091f92375eb695768`，与派工一致。
- 证据标签：**代码实证**仅说明源码；**Spec 明文**仅说明需求；**推断**不得冒充设备观察；**未验证**保留给构建、安装、UI、动画和网络实际结果。
- 构建证据状态：已只读核对 verification 产出的 `logs/analysis-baseline-build-results.json` 和 `logs/analysis-baseline-assembleHap.log`，clean 与 assembleHap 均退出 0，后者 `:1304` 明确 `BUILD SUCCESSFUL`。本角色未执行构建。
- 运行证据状态：**仍待 verification 独立安装/启动/UI 报告**。本文不声明启动成功、页面实际可见、底栏实际缺失、动画实际表现或滚动实际结果已经设备验证。
- 需求草稿复审状态：待 requirements 草稿送审；复审结果记录在本文最后。

## 1. 当前入口、路由和页面树

以下链路是代码实证，实际入口表现仍须与独立安装启动结果核对。

| 层级 | 当前行为 | 精确源码证据 |
| --- | --- | --- |
| 启动 Ability | 模块以 `EntryAbility` 为入口，绑定 `./ets/entryability/EntryAbility.ets` | `entry/src/main/module.json5:6`、`:17-18` |
| 页面声明 | `main_pages` 仅登记 `view/EntryPage` | `entry/src/main/resources/base/profile/main_pages.json:2-4` |
| 路由注册 | `onCreate` 调用 `registerRouter()`；其中注册 `MainGraph` | `entry/src/main/ets/entryability/EntryAbility.ets:33-37`、`:125-126` |
| 加载入口 | 初始化 ORM 后 `loadContent('view/EntryPage')` | `entry/src/main/ets/entryability/EntryAbility.ets:50-53` |
| 根页面 | `@Entry @ComponentV2`，构建时只挂 `NavigationHost()` | `entry/src/main/ets/view/EntryPage.ets:9-12`、`:39-42` |
| 导航宿主 | 创建并提供 `NavPathStack`，`aboutToAppear` 设置全局导航栈；`Navigation` 根内容直接调用 `MainPage()` | `entry/src/main/ets/navigation/NavigationHost.ets:13-17`、`:36-42` |
| 主模块出口 | 对外导出 `MainPage`、`MainGraph` | `feature/main/Index.ets:6-8` |
| 当前主页面 | `AppNavDestination` 标题“主页面”，内容调用 `MainContent()`；其中 `Text("主页面内容视图")` 加通知演示按钮 | `feature/main/src/main/ets/view/MainPage.ets:25-31`、`:39-48`、`:49-130` |

当前可静态追踪的根页面树为：

```text
EntryAbility.loadContent('view/EntryPage')
  EntryPage.Column
    NavigationHost.Navigation(navPathStack)
      MainPage.AppNavDestination(title: '主页面')
        Text('主页面内容视图')
        Column(通知权限、预设、发送文本/长文本/多行/图片/下载模板、清除通知/角标等按钮)
```

不能把“存在四个路由注册”写成“已经有四个底栏页”。现有路由是具名导航目标：

| 路由值 | 注册位置 | builder 调用点 | 目标页当前内容 |
| --- | --- | --- | --- |
| `main/main` | `feature/main/src/main/ets/navigation/MainGraph.ets:17` | `feature/main/src/main/ets/navigation/MainNav.ets:9-10` | `MainPage` 通知演示 |
| `main/home` | 同文件 `:18` | `feature/main/src/main/ets/navigation/HomeNav.ets:9-10` | `HomePage` 标题“首页”，正文 `Text("首页内容视图")`：`feature/main/src/main/ets/view/HomePage.ets:20-26`、`:34-35` |
| `main/category` | 同文件 `:19` | `feature/main/src/main/ets/navigation/CategoryNav.ets:9-10` | `CategoryPage` 标题“分类”，正文 `Text("分类页面内容视图")`：`feature/main/src/main/ets/view/CategoryPage.ets:20-26`、`:34-35` |
| `main/cart` | 同文件 `:20` | `feature/main/src/main/ets/navigation/CartNav.ets:9-10` | `CartPage` 标题“购物车”，正文 `Text("购物车页面内容视图")`：`feature/main/src/main/ets/view/CartPage.ets:20-26`、`:34-35` |
| `main/me` | 同文件 `:21` | `feature/main/src/main/ets/navigation/MeNav.ets:9-10` | `MePage` 标题“我的”，正文 `Text("我的页面内容视图")`：`feature/main/src/main/ets/view/MePage.ets:20-26`、`:34-35` |

路由字符串定义于 `core/navigation/src/main/ets/routers/MainRoutes.ts:5-25`。`RouteBuild` 用 `Map<string, WrappedBuilder<[]>>` 保存注册项（`core/navigation/src/main/ets/RouteBuild.ets:6`、`:13-14`、`:22-23`），宿主按路由取 builder（`entry/src/main/ets/navigation/NavigationHost.ets:26-28`）。当前 MainPage 的全部内容中没有调用这四个子页或导航到这四个路由；定向搜索这些 `MainRoutes.*` 在主模块的使用，只命中注册位置。

## 2. 状态、Lottie、Swiper 和首页重选事件链

| 关注点 | 代码实证 | 能支持的结论及限制 |
| --- | --- | --- |
| 主页面状态 | `feature/main/src/main/ets/view/MainPage.ets:18-19` 持有 `@Local MainViewModel`；`feature/main/src/main/ets/viewmodel/MainViewModel.ets:7-9` 是空 `BaseViewModel` 子类 | 没有主模块选中索引、底栏数据、动画实例或切页控制状态 |
| 四子页状态 | 各页 `:13-14` 持有自己的 `@Local` VM；`HomeViewModel.ets`、`CategoryViewModel.ets`、`CartViewModel.ets`、`MeViewModel.ets` 均在 `:7-9` 为空类 | 不能从占位页推导首页数据加载、购物车加载、登录刷新或滚动状态已经实现 |
| 生命周期 | `core/ui/src/main/ets/component/navdestination/AppNavDestination.ets:68-69`、`:76-77`、`:92-93`、`:126-130` 转发生命周期至 VM；`core/base/src/main/ets/viewmodel/BaseViewModel.ets:11-12`、`:25-26`、`:55-56`、`:63-64` 都是空钩子 | 可复用的是现有容器和生命周期转发模式；目前空 VM 不会因这些钩子自动产生业务事件 |
| Lottie | 当前应用源码检索无 `lottie`；所有非依赖/构建目录的 `oh-package*.json5` 也无 `lottie`；主模块依赖表见 `feature/main/oh-package.json5:8-18` | 未发现应用显式引入或调用 Lottie，也没有播放/暂停/首帧复位/次数控制证据。不能断言第三方依赖内部绝无相关实现，但当前业务页没有接入 |
| Swiper / Tabs | 当前应用源码无 `Swiper`、`Tabs(`、`TabContent`、`tabbar`、`selectedIndex`、`currentIndex` 命中 | 没有横向分页控件或“滑动 → 索引 → 底栏高亮 → 动画”的现有调用链。Spec 要求用户行为，并未强制某一具体分页控件 |
| 首页重选入口 | MainPage 没有“首页”按钮、`index===0` 重选分支、回顶回调或事件发送；HomePage 仅占位文字 | “已经选中首页 → 再次点击 → 只回顶、保持选中、不重播”的链路在当前主模块没有实现证据 |
| 首页滚动容器 | HomePage `:34-35` 没有 `Scroll`/`List`/`Grid` 或 `Scroller`；HomeViewModel `:7-9` 无控制器 | 当前没有把首页滚至优惠券入口不可见的源码前置条件，也没有首页回顶接收点 |
| 唯一通用 Scroller 命中 | `core/ui/src/main/ets/component/refresh/RefreshLayout.ets:22-23` 声明 `@Param scroller`，`:42-51` 传给 `IBestPullRefresh` 并转发刷新回调 | 它是通用刷新容器；当前所有业务源码没有 `RefreshLayout(` 调用命中，不能写成“首页已经使用该控制器”或“回顶等于触发刷新” |
| 事件链检索 | 应用源码无 `emitter`、`scrollTo(`、`scrollEdge`、`scrollToTop` 命中 | 不存在可定位的“主页面发送回顶事件 → 首页监听 → Scroller 回顶”源码链。事件名、控制器方式、回调签名均未定义；本阶段不另行设计 |

负向检索范围与可复核命令（本题工作树）：

```powershell
rg -n -i 'lottie|swiper|tabcontent|tabs\(|tabbar|selectedindex|currentindex|scrolltotop|scrollto\(|scrollEdge|scroller|emitter|\.id\(' entry/src/main feature core -g '*.ets' -g '*.ts' -g '*.json5' -g '*.json' -g '!**/oh_modules/**' -g '!**/build/**'
rg -n -i 'lottie' -g 'oh-package*.json5' -g '!**/oh_modules/**' -g '!**/build/**' .
rg -n 'RefreshLayout\(|getHomeData\(|PageRepository' entry/src/main/ets feature core -g '*.ets' -g '*.ts' -g '!**/oh_modules/**' -g '!**/build/**'
```

第一条仅命中上述 `RefreshLayout` 的 scroller；第二条无命中；第三条仅命中 PageRepository 定义/导出和数据源接口/实现，没有业务调用者。主模块资源枚举也仅见通知测试图片、string/float 配置，未见主模块的底栏动画资源。本条是文件清单观察，不是运行资源加载观察。

## 3. 数据模型、网络和持久化

### 3.1 已存在但未接入主页面的数据能力

| 能力 | 现有定义/流向 | 与本题入口的关系 |
| --- | --- | --- |
| 首页聚合模型 | `core/model/src/main/ets/entity/Home.ets:14-38` 有 `banner`、`category`、`categoryAll`、`flashSale`、`recommend`、`coupon`、`goods`，默认均可空；`:44-50` 将初始化值映射为实体 | 已有“限时精选商品”“推荐商品”“优惠券”数据字段，不等于已有对应 UI；HomePage 没有导入 Home 或仓库 |
| 首页接口 | `core/data/src/main/ets/repository/PageRepository.ets:18-19` 注入/创建网络数据源；`:26-27` 委托 `getHomeData()` | 主模块/入口无该调用；不能写成“启动必然请求首页” |
| HTTP 请求 | `core/network/src/main/ets/datasource/page/PageNetworkDataSourceImpl.ets:15-18` 为 `GET page/home`；`core/network/src/main/ets/NetworkClient.ets:16` 配置基础地址，`:19-24` 配置 10 秒超时和 JSON 头 | 只有被显式调用后才形成该请求链；服务端可达性、响应内容、数据是否含优惠券均未验证，本文没有请求该服务 |
| 拦截器 | `core/network/src/main/ets/interceptors/AppInterceptors.ets:10-15` 返回原请求或拒绝错误，`:20-25` 返回原响应或拒绝错误 | 当前拦截器没有注入 token 或绑定导航、动画、loading 的逻辑 |
| 通用请求状态模式 | `core/base/src/main/ets/state/BaseNetWorkUiState.ets:5-17` 有 LOADING/SUCCESS/ERROR；`core/base/src/main/ets/viewmodel/BaseNetWorkViewModel.ets:47-53` 经 RequestHelper 串接开始、成功、失败；`:95-112` 提供状态设置 | 这是现有可复用架构事实；主模块五个 VM 均继承空 BaseViewModel，没有接入这套网络状态流程，不能为四场景虚构网络状态机 |
| 购物车本地能力 | `core/data/src/main/ets/repository/CartRepository.ets:18-19` 创建本地数据源，`:82-83` 可读全部购物车；`core/database/src/main/ets/datasource/cart/CartLocalDataSourceImpl.ets:24-35` 迁移 CartEntity、`:128-130` 查询并映射 | CartPage/CartViewModel 没有接入该仓库；Spec 仅要求切到购物车页，没有定义商品数据操作 |

### 3.2 持久化和登录边界

- **代码实证**：启动显式初始化 `app.db`（`entry/src/main/ets/entryability/EntryAbility.ets:118-119`）。这可作为现有数据库环境信息，不代表有底栏索引持久化。
- **代码实证**：用户状态在 `core/state/src/main/ets/UserState.ets:169-175` 通过 `PersistenceV2.globalConnect` 持久化，`:158-159` 保存；账号密码另经 `core/datastore/src/main/ets/datasource/account/AccountStoreDataSourceImpl.ets:18-26`、`:32-33`、`:41-42` 使用 Preferences，工具在 `core/util/src/main/ets/storage/PreferencesUtil.ets:45-49` 写入并 flush。当前主页面/四子页无相关读写调用或选中标签恢复逻辑。
- **代码实证**：`navigateTo` 可实施登录拦截并向 `NavPathStack.pushPath` 入栈（`core/navigation/src/main/ets/NavigationService.ets:56-73`）。受保护路由表位于 `core/navigation/src/main/ets/RouteInterceptor.ts:16-37`，不含 `main/main`、`main/home`、`main/category`、`main/cart`、`main/me`；根 MainPage 又是直接挂载。静态上没有“必须登录后才能显示四个标签页”的证据。
- **Spec 明文**：四场景围绕标签显示、切换、动画和回顶；没有网络请求次数、接口、loading、数据写入、领取优惠券或登录操作要求。“领取”是滚动可见性锚点（`spec/requirement.md:51-54`），不能扩张成领取交易测试。
- **推断边界**：验证四个标签和联动本身不应凭空要求真实账户或购物车商品；场景四确实需要可滚动首页和可见/可隐藏的顶部“领取”入口。若未来页面采用服务端数据，需另登记数据前置条件；当前基线既无该 UI 也无其请求调用，因此服务端能否满足仍是未验证事项。

## 4. 四个场景的静态覆盖和缺失证据

这里“缺失”指当前业务源码未实现，最终运行基线结论由 verification 的观察确认。

| Spec 范围 | 明文检查点 | 当前实证/缺口 |
| --- | --- | --- |
| 场景一 `spec/requirement.md:7-15` | 底部四标签；默认首页及上方内容；点击分类/购物车切内容；选中图标播放 Lottie、黑色，其余图标灰色 | MainPage 正文为通知演示，未组合四页；四目标页仅独立占位目标；没有底栏/选中状态/动画调用 |
| 场景二 `:21-28` | 内容区左右滑动切页；首页左滑到分类、继续左滑到购物车；底栏选中和图标动画联动；点击我的切换 | 没有 Swiper/Tabs/拖动分页或索引回调；也没有点击与滑动共用状态的现有证据 |
| 场景三 `:34-41` | 初始化首页动画；切到我的后首页首帧静止；回首页再播一次；首页文字黑色 | MainViewModel 无状态；没有动画实例、帧控制、初始化播放或重返播放逻辑 |
| 场景四 `:47-54` | 首页向下浏览，顶部“领取”滚出视口；重点击已选首页后回顶、入口重现；保持选中、不切页、不额外重播 Lottie | HomePage 无滚动 UI、“领取”入口或 scroller；MainPage 无首页重选按钮/分支；没有回顶事件链。需将“只回顶”和“从其他页切回首页”区分为不同前置状态，不能用一次返回首页操作代替 |

## 5. 选择器和可观测性

- 当前上述应用源码范围的 `.id(` 搜索无命中，五个主模块页面、`NavigationHost`、`AppNavDestination` 均未设置业务组件稳定 id。
- 目前可见文字中“首页”“分类”“购物车”“我的”只是各占位目标的标题参数（四页 `:22`），没有对应的底栏 Text。未来验收不能仅以存在同名文字证明它位于底部或已选中。
- 验收需要可区分的对象：底栏容器、四个可点击标签、各标签文字与图标、上方当前页根内容、首页滚动容器、顶部“领取”入口；这些在基线均没有可报告的现成业务 id。未来实现时需补 `.id()`；本阶段不指定接口或最终命名。
- Lottie 是否播放、是否只播一次、首帧静止以及选中颜色，不可仅用“能找到标签文字”替代。设备验证需要动画时间序列/截图或可审计的播放状态证据；静态代码也需核对播放器调用。任何观测手段均不能在本阶段虚报为已具备。
- “领取”入口在屏幕外可能仍存在于 UI 树；场景四应观察其可视区域/屏幕位置与截图，不能只判断节点存在。
- 现有 `entry/src/ohosTest/ets/test/Ability.test.ets:25-32` 和 `entry/src/test/LocalUnit.test.ets:24-30` 仅是字符串断言模板，不覆盖底栏和滚动。
- 本题自测框架明确建议稳定 `.id()` 和 `BY.key`（`test-harness/README.md:74`），并说明自测非官方评测器（`:6-8`）；本文不把选择器命名推断为官方隐藏约定。

## 6. 环境、运行验证依赖和发布前待补证据

1. **构建通过，签名/安装待验证**：verification 记录命令 `hvigorw clean --mode module -p product=default -p buildMode=debug --no-daemon` 与 `hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon` 均退出 0（`logs/analysis-baseline-build-results.json`），构建日志 `:1304` 为 `BUILD SUCCESSFUL`。已有告警可见同日志 `:142` placeholder 冲突、`:743-1193` 第三方声明相关 ArkTS 告警、`:1197-1287` util/WindowAdapter 告警、`:1290` 重名文件、`:1293` sourceMapsPath 缺失以及 `:1300` `No signingConfig found for product default`；完整清单由 verification 归档。当前 `build-profile.json5:3` 签名列表为空，`:7-9` 目标为 HarmonyOS `6.0.1(21)`，不能把“构建通过”当成“可安装启动”。本设计角色仅阅读现成日志，未执行构建、安装或设备命令。
2. **设备目标**：本地框架记录官方规格 Pura 90 Pro Max、HarmonyOS 6.1.0/API 23、1308×2880/560 dpi（`test-harness/README.md:6-8`）；实际设备匹配度待验证。App bundle 为 `com.joker.coolmall`（`AppScope/app.json5:3`），需确认安装的是本题当前基线 HAP，而非仅依赖设备上同名包（框架提示见 `test-harness/README.md:52-53`）。
3. **启动弹窗**：`loadContent` 回调请求麦克风权限（`entry/src/main/ets/entryability/EntryAbility.ets:52-57`）；工具在 `core/util/src/main/ets/permission/PermissionUtils.ets:195-196` 明确请求 `MICROPHONE`，模块也声明该权限（`entry/src/main/module.json5:61-69`）。可能影响首次 UI 操作，是否出现及处理后页面状况须记录设备证据。
4. **账户/服务端/数据**：当前可静态到达的主页面无登录或首页网络调用前置；首页数据接口、空/失败态、优惠券数据供应均未进行网络验证；场景四的滚动和优惠券 UI 在当前基线无代码入口。本题没有 WebDAV 需求或相关验证前置证据。
5. **运行报告至少补齐**：构建及原有告警清单、安装/启动命令与退出状态、实际首页截图与 UI 树、四标签是否能操作、启动权限弹窗、场景四滚动前置是否可建立、源码指纹复核。基线能力缺失时应明确“操作入口不存在，未能执行该场景”，不要记为已通过。

## 7. 审阅与未解决项

- 静态映射完成，覆盖四个场景及入口、路由、模型、网络、持久化、Lottie、Swiper、首页重选/Scroller 和选择器风险。
- 取舍：复用能力仅记录当前架构事实；没有提出新 API、动画依赖选择、页面结构重构、回顶事件机制或网络接入方案，符合本轮仅分析范围。
- 当前待解决：verification 运行证据、requirements 草稿复审。二者未齐时，协调者可采用本文静态证据，但不应发布“已安装实际操作并确认入口”的最终运行结论。
- 外部来源：未访问上游项目、其他赛题、题包、提交/PR/Issue/补丁或其副本；未查询公开网络技术文档。本次仅阅读本题资料、当前源码与已安装角色/技能说明。
