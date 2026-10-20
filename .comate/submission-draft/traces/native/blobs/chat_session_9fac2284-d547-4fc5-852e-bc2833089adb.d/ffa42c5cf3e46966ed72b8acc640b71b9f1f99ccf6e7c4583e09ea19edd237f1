# 基线理解：商品搜索功能（cml-combo-search）

记录日期：2026-10-20。标注方式：

- 【代码】有 `文件:行号` 的代码实证（路径相对工程根目录）
- 【实测】在模拟器上实际操作/抓取到的结果
- 【Spec】`spec/requirement.md` 原文
- 【推断】我的推测，**未验证**

## 1. 基线快照标识

- HEAD：`261589401b664d4a9a5622f748071d14e04108e2`（`2615894 Harmony Cup sanitized baseline snapshot`），和 `spec/metadata.json` 的 `base_commit` 一致。
- 分支：`cml-combo-search`。
- 标签：新打了 `baseline-cml-combo-search` → 2615894；仓库原本已有 `base/cml-combo-search`，指向同一个提交。
- 分析阶段工作区状态：`git status` 只有未跟踪的 `spec/`、`logs/`；没有改任何已跟踪文件。`**/BuildProfile.ets` 已在 `.gitignore` 里，并且 `git ls-files` 中没有任何 BuildProfile.ets，所以 debug 构建不会产生已跟踪的噪声文件。

## 2. 构建基线状态

环境：macOS（arm64）+ DevEco Studio 自带工具链。命令行构建前必须设置 `JAVA_HOME`，否则 `PackageHap` 报 `00308018 Unable to locate a Java Runtime`（第一次构建就是这样失败的）：

```bash
D=/Applications/DevEco-Studio.app/Contents
export JAVA_HOME=$D/jbr/Contents/Home
export DEVECO_SDK_HOME=$D/sdk
export PATH=$JAVA_HOME/bin:$D/tools/hvigor/bin:$D/tools/node/bin:$D/tools/ohpm/bin:$D/sdk/default/openharmony/toolchains:$PATH
hvigorw clean --no-daemon
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

- 结果【实测】：`BUILD SUCCESSFUL in 16 s 505 ms`（clean 之后全量构建）。产物 `entry/build/default/outputs/default/entry-default-unsigned.hap`（约 19.6 MB）。
- 日志：`logs/baseline-build.log`（全量）、`logs/baseline-clean.log`；告警归一化清单 `logs/baseline-warnings.txt`（去掉绝对路径、排序去重，共 440 条，实现阶段可以直接 diff）。
- 已有告警分类【实测】：
  - ArkTS 告警 240 条：`oh_modules` 内 166 条（ibest-ui-v2 等三方库）；工程源码 74 条，全在和本题无关的文件里——`core/util/.../NotificationUtil.ets` 21、`core/designsystem/.../Row.ets` 18、`Column.ets` 16、`Scroll.ets` 6、`entry/.../WindowAdapter.ets` 4、`core/util/.../ImageUtil.ets` 3、`ContextUtil.ets` 2、`OrderGoodsCard.ets` 2、`PermissionUtils.ets` 1、`feature/main/.../MainViewModel.ets` 1。类型只有两种：`Function may throw exceptions`、`'@BuilderParam' attribute ... can only be initialized by '@Builder'`。
  - 资源重名告警 195 条（194 条去重后）：`'xxx' conflict, first declared`，例如 `confirm`、`cancel`、`ok`、`search`、`page_show` 等，见 §8.2。
  - 其它 6 条：`No signingConfig found for product default`；`sourceMapsPath not found` ×3（ibest-ui-v2、cashiersdk、blueshieldsdk）；`'delete' conflict`；一条 FAQ 提示。
  - `feature/goods` 当前没有任何 ArkTS 告警，实现后这个模块新增的告警一眼就能看出来。
- 安装【实测】：`hdc -t 127.0.0.1:5555 install -r entry/build/default/outputs/default/entry-default-unsigned.hap` → `install bundle successfully`（`logs/baseline-install.log`）。未签名的 HAP 可以直接装到模拟器上；bundleName `com.joker.coolmall`，安装后 `updateTime=1792467464300`。
- 支付 SDK 架构问题：技术答疑里提到的"x86_64 模拟器装不上"在本机**不存在**——本机 Mac 是 arm64，模拟器 `const.product.cpu.abilist = arm64-v8a`，原始包能直接安装。不需要做调试隔离，`abiFilters` 也不用改。

## 3. Spec 描述的入口当前在哪

### 3.1 首页顶部搜索框（场景一·步骤1 的起点）

- 组件【代码】：`feature/main/src/main/ets/component/HomeTopBar.ets`
  - `onSearchTap` 参数默认是空函数：`:13-15`
  - 搜索行：`titleBuilder()` `:49-72`，Row 里是 `ic_search` 图标 + Text `$r("app.string.search_goods")`（= `搜索商品`，`feature/main/src/main/resources/base/element/string.json:68-69`），`:71` `.onClick((): void => this.onSearchTap())`
- 调用点【代码】：`feature/main/src/main/ets/view/HomePage.ets:38` 写的是 `HomeTopBar();`，**没传 `onSearchTap`**，所以点击什么都不会发生。
- 【实测】冷启动 → 首页正常加载 → 点 `搜索商品`（bounds `[628,192][797,241]`，点击坐标 (654,216)）→ 页面不变，没有跳转。
- 首页是 Navigation 的根内容，不是路由页：`entry/src/main/ets/navigation/NavigationHost.ets:37-42`（`Navigation(this.navPathStack) { MainPage() }` + `.navDestination(this.PagesMap)`）。启动流程不会自动进入 Splash/Guide（`LaunchNavigator` 没有调用点），冷启动直接到首页。

### 3.2 商品搜索页（goods/search）

- 路由名【代码】：`GoodsRoutes.Search = "goods/search"`，`core/navigation/src/main/ets/goods/GoodsRoutes.ts:13`
- 跳转封装【代码】：`GoodsNavigator.toSearch()`，`core/navigation/src/main/ets/goods/GoodsNavigator.ets:35-37`。全工程**没有调用点**（grep `toSearch` 只命中定义）。
- 注册【代码】：`feature/goods/src/main/ets/navigation/GoodsGraph.ets:18` → `GoodsSearchNav.ets:8-11` → `GoodsSearchPage()`；`entry/src/main/ets/entryability/EntryAbility.ets:106` `new GoodsGraph().register()`。
- 页面【代码】：`feature/goods/src/main/ets/view/GoodsSearchPage.ets`，是**占位页**：`AppNavDestination({ title: "商品搜索", viewModel })`（`:21-24`），内容只有 `Text("商品搜索页面内容视图")`（`:35`）。
- ViewModel【代码】：`feature/goods/src/main/ets/viewmodel/GoodsSearchViewModel.ets:7-9`，空类，继承 `BaseViewModel`。
- 不需要登录：`core/navigation/src/main/ets/RouteInterceptor.ts:17-36` 的需登录列表里没有 goods 路由，`requiresLogin()` 在 `:54-56`。
- 【实测】基线 UI 里没有任何入口能进入这个页面，占位页**没有在设备上看到**，上面只是读代码得出的结论。

### 3.3 商品分类列表页（goods/category，场景一·步骤5 的目标）

- 路由名【代码】：`GoodsRoutes.Category = "goods/category"`，`GoodsRoutes.ts:17`
- 跳转封装【代码】：`GoodsNavigator.toCategory(params?: GoodsCategoryParam)`，`GoodsNavigator.ets:44-50`；**没有调用点**。
- 参数【代码】：`GoodsCategoryParam { typeId?, featured?, recommend?, keyword?, minPrice? }`，`core/navigation/src/main/ets/goods/GoodsParam.ets:9-30`，其中 `keyword?: string` 在 `:25`。由导出 `core/navigation/Index.ets:34` 可以拿到。
- 注册【代码】：`GoodsGraph.ets:20` → `GoodsCategoryNav.ets:8-11` → `GoodsCategoryPage()`。
- 页面【代码】：`feature/goods/src/main/ets/view/GoodsCategoryPage.ets`，同样是**占位页**：标题 `"商品分类"`（`:22`），内容 `Text("商品分类页面内容视图")`（`:35`）。ViewModel `GoodsCategoryViewModel.ets:7-9` 也是空的。
- 【推断】"商品分类列表页"指的就是这个页面，而不是底部 tab 的"分类"（`MainRoutes.Category`，`core/navigation/src/main/ets/main/MainNavigator.ets:30-32`）。依据：只有 `GoodsCategoryParam` 带 `keyword` 字段，MainNavigator.toCategory 不接收参数。
- README 也写明这两个页面没做：`README.md:137` `商品搜索 (search) 待开发`、`README.md:140` `商品分类页面 (category) 待开发`。

### 3.4 其它相关但不在范围内的入口

- 首页分类宫格也没接点击：`HomePage.ets:69` `HomeCategorySection({ categories })` 没传 `onCategoryClick`（组件里的回调在 `HomeCategorySection.ets:76`）。Spec 没要求，**不处理**。
- `feature/goods/src/main/resources/base/element/string.json` 里已经有 `comprehensive=综合`、`sales=销量`、`price=价格`、`price_range=价格区间`、`min_price`/`max_price`、`reset=重置`（`:80-114`）。【推断】上游完整版的分类页可能带排序/筛选，但 Spec 没要求，**不做**。

## 4. 相关现状

### 4.1 页面组件与状态模型

- 页面统一写法【代码】：`@ComponentV2 struct XxxPage { @Local private vm = new XxxViewModel() }`，外层包 `AppNavDestination({ title, viewModel, menus? })`（例：`GoodsCommentPage.ets:11-39`）。
- `AppNavDestination`【代码】`core/ui/src/main/ets/component/navdestination/AppNavDestination.ets`：把组件生命周期转发给 VM（`aboutToAppear` `:73-75`、`aboutToDisappear` `:81-83`），把 NavDestination 的 `onShown`/`onHidden` 也转发给 VM（`:131-136`）。**从结果页 pop 回来时只会触发 `onShown`，不会再走 `aboutToAppear`**——要刷新历史只能放在 `onShown`。
- VM 基类【代码】：
  - `core/base/src/main/ets/viewmodel/BaseViewModel.ets:5-65`：只有空的生命周期钩子（含 `onShown(reason)` `:55-56`）。
  - `core/base/src/main/ets/viewmodel/BaseNetWorkListViewModel.ets:13-189`：`@Trace uiState`（初值 LOADING）、`listData`、`isLoading`、`isEnableSlideUp`；`currentPage=1`、`pageSize=10`（`:38-42`）；子类只需要实现 `requestListData()`（`:52`）；`aboutToAppear → initLoad → loadListData`（`:58-83`）；刷新 / 加载更多 / 重试 / 是否还有下一页（`:130-188`）。
- 状态 → 视图【代码】：`core/ui/src/main/ets/component/network/BaseNetWorkListView.ets:77-119`，Stack 里四层（loading / error / empty / content）**全部常驻**，只靠 `.opacity()` 切换（见 §8.3）。
- 状态管理是 V2（`@ObservedV2`/`@Trace`/`@Local`/`@Param`），README 技术栈也是这么写的。

### 4.2 数据模型与网络服务

- 推荐关键词模型【代码】：`GoodsSearchKeyword { id, name, sortNum, createTime?, updateTime? }`，`core/model/src/main/ets/entity/GoodsSearchKeyword.ets:5-37`。
- 商品搜索请求【代码】：`GoodsSearchRequest { page=1, size=20, typeId?, minPrice?, maxPrice?, keyWord?, order?, sort?, recommend?, featured? }`，`core/model/src/main/ets/request/GoodsSearchRequest.ets:5-65`，关键词字段名是 **`keyWord`**（大写 W，`:29`）。
- 商品模型【代码】：`Goods { id, title, subTitle?, mainPic, price, sold, ... }`，`core/model/src/main/ets/entity/Goods.ets:11-39`。
- 网络数据源【代码】：`core/network/src/main/ets/datasource/goods/GoodsNetworkDataSourceImpl.ets`
  - `getSearchKeywordList()`：`POST goods/search/keyword/list`，无 body，`:48-52`
  - `getGoodsPage(params)`：`POST goods/info/page`，`:59-63`
  - 接口声明在 `GoodsNetworkDataSource.ets:38` 等处。
- 仓库【代码】：`core/data/src/main/ets/repository/GoodsRepository.ets`，`getSearchKeywordList()` `:55-57`、`getGoodsPage()` `:64-66`；已经从 `core/data/Index.ets:8` 导出。
- 请求封装【代码】：`RequestHelper.repository<T>(promise).toast(bool).execute()`（例：`HomeViewModel.ets:51-65`、`BaseNetWorkListViewModel.ets:75-82`），来自 `result` 模块。
- 服务地址【代码】：`core/network/src/main/ets/NetworkClient.ets:16` 写死 `https://mall.dusksnow.top/app/`，axios 超时 10 s（`:19-25`），拦截器在 `interceptors/AppInterceptors`。工程**没有**面向用户的服务地址配置页。按技术答疑的要求：沿用这个机制，不改地址、不新增配置。

### 4.3 本地存储（搜索历史）

基线已经有一整套搜索历史存储，只是没有页面使用：

- ORM 初始化【代码】：`entry/src/main/ets/entryability/EntryAbility.ets:51`、`:93-95`，`IBestORMInit(this.context, { name: "app.db" })`，在 `loadContent` 之前 await。
- 实体【代码】：`core/database/src/main/ets/entity/SearchHistoryEntity.ets:7-19`，表 `search_history`，主键 `keyword`（`@PrimaryKey({ autoIncrement: false })`），另有 `searchTime` INTEGER。
- 数据源【代码】：`core/database/src/main/ets/datasource/searchhistory/SearchHistoryLocalDataSourceImpl.ets`
  - 首次构造时 migrate（`:24-37`）
  - `addSearchHistory` → `this.orm.save(entity)`（`:44-46`），语义见 §8.4
  - `clearAllSearchHistory` → `orm.query(SearchHistoryEntity).delete()`（`:61-63`）
  - `getAllSearchHistory` 全表读出后按 searchTime 倒序（`:69-74`）；`getRecentSearchHistory(limit)` 取前 limit 条（`:89-92`）
  - `toEntity` 会再 trim 一次（`:110-115`）
- 仓库【代码】：`core/data/src/main/ets/repository/SearchHistoryRepository.ets`
  - `addSearchHistory(keyword)`：trim，空就直接 return，`searchTime = Date.now()`（`:30-39`）
  - `clearAllSearchHistory()`（`:54-56`）、`getRecentSearchHistory(limit)`（`:79-81`）、`getSearchHistoryByKeyword`（`:88-90`）
  - **没有在 `core/data/Index.ets` 导出**（`:6-36` 中没有它），feature 模块现在 `import { SearchHistoryRepository } from "data"` 会拿不到。实现时要补一行导出。
- 领域模型【代码】：`SearchHistory { keyword, searchTime }`，`core/model/src/main/ets/entity/SearchHistory.ets:5-22`，已从 `core/model/Index.ets:82` 导出。
- 其它 KV 存储（preferences）【代码】：`core/datastore/src/main/ets/datasource/account/AccountStoreDataSourceImpl.ets` 等，本题用不到。

## 5. 可复用的既有实现

| 需要的能力 | 基线里最接近的实现 | 复用方式 |
| --- | --- | --- |
| 带路由参数的分页列表 VM | `GoodsCommentViewModel.ets:13-38`：`extends BaseNetWorkListViewModel<Comment>`，`getRouteParams<GoodsIdParam>(GoodsRoutes.Comment)` 取参数，`requestListData()` 里组装请求 | `GoodsCategoryViewModel` 照这个写，参数换成 `GoodsCategoryParam`，请求换成 `GoodsSearchRequest{keyWord}` |
| 分页列表页面 | `GoodsCommentPage.ets:28-73`：`BaseNetWorkListView` + `RefreshLayout` + `List/ForEach` | `GoodsCategoryPage` 照抄结构 |
| 商品卡片 | `core/ui/.../goods/GoodsGridItem.ets:22`、`GoodsListItem.ets:19`；首页"全部商品"的双列网格 `HomePage.ets:105-124`（`Grid` + `bp({sm:"1fr 1fr",...})`） | 结果页直接用 `GoodsGridItem`，点击 `GoodsNavigator.toDetail(id)` |
| 本地列表 + "清空" + 确认框 | 足迹页：`FootprintPage.ets:25-49`（`IBestDialog({ visible, title, message, showCancelButton, confirmButtonText, cancelButtonText, onConfirm, onCancel, onClose })`），`FootprintViewModel.ets:39-40`（`@Trace showClearDialog`）、`:96-121`（show / hide / confirmClearAll：清完再关框，失败也关框） | 搜索页的清空历史照这个写；注意按钮文本不能用 `$r("app.string.confirm")`（§8.2） |
| "删了再插"来实现置顶 upsert | `FootprintLocalDataSourceImpl.ets:44-47`：`deleteById` + `insert` | 如果 §8.4 验证出 `save` 不可靠，就改成这种写法 |
| 路由跳转与取参 | `navigateTo(name, params)` `core/navigation/src/main/ets/NavigationService.ets:51-78`；`getRouteParams<T>(name)` `:192-203`；`GoodsNavigator.toCategory(params)` 已经封装好 | 搜索页调 `GoodsNavigator.toCategory({ keyword })`；首页调 `GoodsNavigator.toSearch()` |
| 删除 / 搜索图标 | `core/ui/src/main/resources/base/media/ic_delete.svg`（足迹页"清空"菜单用的就是它，`FootprintPage.ets:31`）、`ic_search.svg` | 直接 `$r("app.media.ic_delete")` |
| 文案资源 | `feature/goods/.../string.json:92-97`：`search_history=搜索历史`、`recommended_search=推荐搜索`；`core/ui/.../string.json:112-117`：`search=搜索`、`search_hint=输入内容进行搜索`；`cancel=取消`（`core/ui/.../string.json:92-93`） | 这几个编译后的值都和 Spec 一致，可以直接用（§8.2 已核对） |
| 组件库 | `@ibestservices/ibest-ui-v2@1.1.1`（经 `core/ibestui/Index.ets:6` 整体 re-export）：`IBestSearch`（`autoFocus`、`showRightButton`、`rightButtonText`、`enterKeyType`、`onSearch`、`onRightButtonClick`、`$value`）、`IBestTag`（`text`、`round`、`onTagClick`）、`IBestDialog` | 可选。代价是三方组件内部节点设不了 `.id()`；用原生 `TextInput`/`Search` + `.id()` 可观测性更好。实现时二选一，见 §8.6 |

## 6. 缺失项（Spec 要求但基线没有）

1. 首页搜索框点击跳转：`HomePage.ets:38` 要传 `onSearchTap: () => GoodsNavigator.toSearch()`。
2. 搜索页整页 UI 与逻辑：输入框（自动聚焦 + 弹键盘）、"搜索"按钮、键盘搜索键、历史区域（标题 + 垃圾桶 + 最多 10 个圆角标签，条件渲染）、推荐区域（R1 请求 + 标签）、清空确认框、空输入校验、防连点、`onShown` 刷新历史。
3. 结果页整页 UI 与逻辑：读 `keyword` 参数、分页请求 `goods/info/page`、商品网格、空 / 错误 / 加载更多。
4. `SearchHistoryRepository` 没有从 `core/data/Index.ets` 导出。
5. 文本为 `确认` 的资源（现有的 `confirm`/`ok` 编译后都不是"确认"，§8.2），以及 `确认清空所有搜索历史吗？` 的资源。
6. 所有稳定选择器（`.id()`）：feature 代码里一个都没有（§8.1）。
7. 搜索历史 upsert 的正确性：§8.4 没验证之前，不能假设 `save` 一定能"新增或置顶"。

## 7. 前置环境需求

- 登录：**不需要**（§3.2，goods 路由不在拦截列表里）。
- 服务端【实测，2026-10-20，从开发机 curl】：
  - `POST https://mall.dusksnow.top/app/goods/search/keyword/list` → `code=1000`，20 条：`Xiaomi 17`、`Xiaomi 17 Pro`、`Xiaomi 17 Ultra`、`Xiaomi 17T Pro`、`REDMI K90 Pro`、`REDMI Note 17 Pro`、`REDMI Turbo 5`、`Xiaomi Pad 8 Pro`、`REDMI Pad 2 Pro`、`REDMI Watch 6`、`小米手环 10`、`小爱音箱`、`路由器 BE7000`、`米家洗衣机`、`米家扫拖机器人`、`智能摄像机`、`充电宝`、`蓝牙耳机`、`电视 S Mini LED`、`旅行热水杯`（按 sortNum 1..20 升序返回）。
  - `POST goods/info/page {"page":1,"size":3,"keyWord":"Xiaomi 17"}` → total 8（`Xiaomi 17T Pro`、`Xiaomi 17T`、`Xiaomi 17 Max`……）；`keyWord:"小米"` → total 16；`keyWord:"手机"` → total 0（可以拿来测空结果）。
  - 只发了上面这些不带任何凭据的公开查询请求。
- 正式评测：技术答疑原文——"正式评测使用官方受控的服务、数据或测试适配条件，并通过基线已有的数据访问机制接入"，"不要将自建服务地址硬编码为数据源"。所以必须走 `GoodsRepository` → `GoodsNetworkDataSourceImpl`，方法签名和请求 / 响应模型保持不变。【推断】官方推荐词的内容可能和公网的不一样，自测不能写死具体的推荐词文本，应该"读第 0 个推荐标签的文本再用"。
- 模拟器【实测】：`127.0.0.1:5555`，`emulator 6.1.0.115`、API 23、1308×2880、`arm64-v8a`、语言 `zh-Hans`；`harness.env_check` 输出"✓ 环境与官方评测规格一致"。
- 模拟器网络【实测】：DNS 用的是 `114.114.114.114`/`8.8.8.8`（`/etc/resolv.conf`），在当前网络下解析时好时坏——第一次冷启动首页显示了 `网络连接失败`，`ping mall.dusksnow.top` 先报 `Try again`，过一会儿再试就能解析（RTT 异常大）。自测前要先确认首页能加载出来，失败的用例要区分"网络问题"和"功能问题"。
- WebDAV、测试账号、本地 mock 服务：都不需要。
- Hypium 环境：`../common/.venv`（hypium 6.1.0.210），`../common/test-harness`；`hdc` 在 `$D/sdk/default/openharmony/toolchains`，默认不在 PATH 里。

## 8. 测试可观测性风险

### 8.1 没有稳定 id

- 【代码】`feature/` 和 `core/` 源码里 `.id(` / `.key(` 的使用次数都是 **0**。
- 【实测】首页 dump 里唯一带 id 的业务节点是三方组件自动生成的 `ibest_pull_down_161`（下拉刷新），这个 id 不稳定，不能用。
- 影响：新增的输入框、按钮、垃圾桶图标、标签都必须补 `.id()`（清单见 `acceptance.md` §0）。垃圾桶是纯图标，没有 id 就只能靠类型+顺序去找。

### 8.2 资源重名导致的文案偏差

工程有多个 HAR 模块，相同 key 的字符串在编译时只保留**第一个声明**的值（构建日志 `'confirm' conflict, first declared ... core/ui/.../string.json`）。用 `restool dump` 打开基线 HAP 核对编译后的实际值【实测】：

| key | 声明位置与值 | HAP 中的实际值 | 对本题的影响 |
| --- | --- | --- | --- |
| `confirm` | core/ui「确定」、feature/goods「确定」、feature/user「确认」、feature/order「确认」 | **确定** | Spec 要的是 `确认`，**不能用这个 key** |
| `ok` | feature/user「确认」等 | 默认「确认」，另外有 `zh_CN` 限定的「确定」 | 设备语言是 `zh-Hans`，会不会命中 `zh_CN` 未验证，**不能用** |
| `cancel` | core/ui / user / order 都是「取消」 | 取消 | 可以用 |
| `search` | core/ui、feature/main 都是「搜索」 | 搜索 | 可以用 |
| `search_history` / `recommended_search` | 只在 feature/goods | 搜索历史 / 推荐搜索 | 可以用 |

顺带：足迹页 `FootprintPage.ets:43` 用的 `$r("app.string.confirm")`，按上表实际显示的是"确定"（【推断】，因为要登录才能进足迹页，没有在设备上看到）。这是基线问题，按要求只记录，不修。

新建资源 key 时要用本模块唯一的名字（例如 `search_history_clear_confirm`），否则会被别的模块先声明的同名 key 覆盖，而且会多出一条重名告警。设备语言是简体中文【实测 `persist.global.locale=zh-Hans`】，`$r` 取到的是 base 下的中文；en 目录下的值不影响评测。

### 8.3 被隐藏的状态层仍然留在组件树里

- 【代码】`BaseNetWorkListView.ets:78-118` 只用 opacity 隐藏非当前状态。
- 【实测】首页加载成功后 dump 出来，`网络连接失败`、`重新加载`、`暂无数据`、`加载中...` 这些节点都还在，属性是 `visible=true`、`opacity=1.000000`（隐藏它们的 opacity 设在父容器上，节点本身拿不到）。
- 影响：
  - 结果页已经定为复用这个组件（acceptance U16），所以"`暂无数据` 存在 / 不存在"这种断言分不清当前状态。自测要结合 `goods_category_item_0` 是否存在来判断。
  - 搜索页的历史区域必须用 `if` 渲染，否则清空之后 `搜索历史` 仍然"存在"（acceptance A5/A32）。
  - 内容层叠在最上面，opacity 为 0 时有没有拦截点击，未验证。

### 8.4 搜索历史 upsert 的语义没有验证

- 【代码】`SearchHistoryLocalDataSourceImpl.ets:45` 用的是 `orm.save(entity)`；ibest-orm 2.0.2 的声明里注释是"保存实体（有主键更新，无主键插入）"（`oh_modules/.ohpm/@ibestservices+ibest-orm@2.0.2/.../ets-next/core/ORM.d.ts:49-52`）。
- 【推断】`keyword` 是手动设置的非自增主键，新词一进来"有主键"就成立。如果 `save` 只根据"主键字段有没有值"来决定走 UPDATE，那新词会去 UPDATE 一个不存在的行，结果一条都写不进去。这个风险也可能不存在（如果它内部先查一次是否存在）。
- 同一工程里，Cart 新增用的是 `insert`、更新才用 `save`（`CartLocalDataSourceImpl.ets:45` vs `:54`），足迹用的是 `deleteById + insert`（`FootprintLocalDataSourceImpl.ets:45-46`）；只有搜索历史是直接 `save`，而且这条链路在基线里从来没有被调用过。
- 结论：**未验证**。实现阶段第一步就在设备上验证"新词能插入、旧词能更新 searchTime"；不行就改成 `deleteById + insert`。

### 8.5 同名文本与选择器歧义

- 搜索页里 `搜索`（按钮）、`搜索历史`、`推荐搜索`、`商品搜索`（标题）都含"搜索"二字：精确匹配没有冲突，`CONTAINS` 匹配会冲突。要保证精确文本 `搜索` 在页面上只出现一次。
- 首页是 `搜索商品`，搜索页标题是 `商品搜索`，两个字符串不一样，不会冲突。
- 同一个词可能同时出现在历史和推荐两个区域（点了推荐词再返回之后一定会这样），按文本查找会命中两个节点；历史在上方，按树顺序先命中历史。
- 推荐词之间存在前缀关系（`Xiaomi 17` / `Xiaomi 17 Pro` / `Xiaomi 17 Ultra` / `Xiaomi 17T Pro`）：精确匹配没问题，模糊匹配会命中多个。
- 结果页的商品标题可能包含关键词（`Xiaomi 17` → `Xiaomi 17T Pro`），而结果页又会显示关键词（acceptance U5），所以要用精确匹配或 `goods_category_keyword` 来区分。
- 对话框里的 `确认` 和提示文案 `确认清空所有搜索历史吗？` 在 `CONTAINS` 匹配下会冲突，精确匹配下不会。

### 8.6 其它

- 三方组件（`IBestDialog`、`IBestSearch`、`IBestTag`）的内部节点不能设 id；`IBestDialog` 的按钮只能按文本定位。用 `IBestSearch` 的话，输入框本体也拿不到我们的 id，只能用外层容器的 id 再按类型 `TextInput` 往下找。【推断】用原生 `TextInput`（或 `Search`）+ `.id()` 更稳，实现时定。
- dump 出来的节点属性里有独立的 `hint` 字段【实测，首页 Text 节点】。【推断】输入框的 placeholder 会出现在 `hint` 里而不是 `text` 里；基线里没有能进入的输入框页面，**未验证**。"搜索框为空"的断言应该检查 `text == ""`。
- 软键盘是否弹出，Hypium 没有直接的 API，只能靠窗口列表或截图（未验证具体做法）。
- 模拟器网络不稳（§7），涉及 R1/R2 的用例需要预检 + 重试，不然会把网络抖动误判成功能失败。
