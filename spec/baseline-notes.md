# cml-spec24 基线现状映射 v2

状态：**0-analyze 基线报告合并完成，可由主 Agent 发布。pristine 原包构建成功但 ABI 安装阻断；同业务源码的隔离诊断 v3 包安装启动成功，真实搜索进入目标占位页、两类分类点击无跳转已实测。完整目标功能未实现；原包在兼容 arm64 设备运行仍未验证。**

本报告仅分析本题未修改基线；不是实现方案。设计角色只写 `workflow/design/*`，未修改业务代码、配置、测试或 workflow/state。设计角色原生会话 `CODEX_THREAD_ID=01a1522a-c023-7410-852c-8372c784dd58`。

证据等级：`CODE_FACT` 为本题源码/记录事实；`DEVICE_OBSERVED` 为本轮自测角色提供的设备证据；`SPEC_EXPLICIT` 为 Spec 明文；`INFERENCE` 为从事实推导且尚非运行结论；`UNVERIFIED` 为尚未验证。所有路径相对本题根目录 `D:/HCUP/cml-spec24`。

输入合并：`workflow/requirements/acceptance-v1.md`（已批准分析稿，52 明文 + 14 合理推导 + 10 未决语义）、`workflow/implementation/analysis-audit-v1.md`（独立静态复审）、`workflow/verification/baseline-v1.md`（本轮 pristine 原包证据）、`workflow/verification/baseline-abi-diagnostic-v3.md`（隔离诊断包实测）。v1 草稿保留原样，供审计快照追溯；本版不把审计的结构复审计为功能通过。

## 1. 基线快照

- `CODE_FACT`：本轮 `git rev-parse HEAD` 返回 `ab3dc7cd5d05a9a3fd7d4e9ddd0a49e1a05085d8`，与 `spec/metadata.json:2` 的 base_commit 相同。本报告采用记录 HEAD 的方式，未创建 tag。
- `CODE_FACT`：`workflow/analysis-start-code-fingerprint.json:2` 记录同一 HEAD；`:863` 的 `differences_from_setup` 为 `[]`；`:865` 声明 `analysis_only`。本轮静态定位时 `git status --porcelain` 未报告已跟踪业务文件变更，存在分析/输入/日志等未跟踪目录。
- `CODE_FACT`：输入 Spec 为 `spec/requirement.md`，派工记录的 SHA256 为 `db94fb5440c450010739e4b8e01754bb7f54e04d7da2c719a288c1f8ead42939`，本角色不修改 Spec。
- 初始化总览会话、其他题、题包目录、上游修复历史、PR/Issue/补丁或已实现版本均未作为证据读取。

## 2. 本轮构建、告警、安装和启动状态

### 2.1 pristine 原包：构建 pass，安装/启动 blocked

下述为自测角色的新测量，均引用 `workflow/verification/baseline-v1.md`，不复用初始化构建。原包与后续诊断包必须分开判断。

```powershell
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
Set-Location D:/HCUP/cml-spec24
hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon
```

| 事项 | 结果与精确记录 | 证据 |
| --- | --- | --- |
| 冻结校验（CODE_FACT） | 858 tracked 文件在构建前、后、安装尝试后 HEAD 一致，changed=[]、missing=[] | 报告 `:13`–`:18`；`logs/analysis-baseline/fingerprint-before-build.json`、`fingerprint-after-build.json`、`fingerprint-after-install-attempt.json` |
| 新构建（CODE_FACT） | UTC 03:19:05.7839346–03:19:28.4544226；BUILD SUCCESSFUL in 20 s 522 ms，退出 0 | 报告 `:25`–`:33`；`logs/analysis-baseline/build-full.log`、`build-result.json` |
| 原始新 HAP（CODE_FACT） | `entry/build/default/outputs/default/entry-default-unsigned.hap`；19,706,293 字节；SHA256 `aabe9311c58047618fc14f4c07e38c8fd769120751906d8d3bfffc7a13bb87cd` | 报告 `:34`–`:36`；保全副本 `logs/analysis-baseline/baseline-pristine-unsigned.hap` |
| 环境（CODE_FACT） | SDK API23；DevEco 6.1.0.860；工程 target/compatible 仍为 6.0.1(21)、空 signingConfigs | 报告 `:37`–`:38`；不是修改配置后取得的构建成功 |
| 隔离设备（DEVICE_OBSERVED） | `CmlSpec24Baseline`，目标 `127.0.0.1:11241`；API23/6.1.0.115、x86_64、1308×2880；只操作本题独立实例 | 报告 `:65`–`:70`；`logs/analysis-baseline/17-device-abi.stdout.log`、`21-device-machine.stdout.log` |
| 原包安装（DEVICE_OBSERVED） | 两次 `9568347 / install parse native so failed`，ABI 不匹配，blocked | 报告 `:74`–`:99`；`logs/analysis-baseline/10-install-native-path.*`、`25-install-repro.*`；HAP 清单 `hap-native-libs.json` 仅两个 arm64-v8a so |
| 原包启动（DEVICE_OBSERVED） | aa start 返回 `10104001 / The specified ability does not exist`，未安装不能启动 | 报告 `:78`、`:86`–`:90`；`logs/analysis-baseline/12-start-installed.*`、`19-bundle-status.*` |
| 原包应用 UI | 没有应用 UI；`13-layout-installed.json`/`15-screen-installed.png` 是桌面，不能证明目标页 | 报告 `:107`–`:111` |

安装命令是 `hdc -t 127.0.0.1:11241 install -r .\entry\build\default\outputs\default\entry-default-unsigned.hap`，启动命令是 `hdc -t 127.0.0.1:11241 shell aa start -a EntryAbility -b com.joker.coolmall`。这些 hdc 进程退出码 0，但标准输出明确失败，不能按进程退出码判安装通过（报告 `:90`）。ABI 原因由安装报错、原包 ZIP 清单、设备 ABI 三者相互支持；这不证明 arm64 真机上的功能正确。

### 2.2 本轮已有告警清单

`CODE_FACT`：报告 `:42` 统计 246 行含 WARN 的诊断/汇总输出，其中 240 个带源码定位的唯一诊断（依赖 166、tracked 源码 74），另有 6 条构建/包级输出。不能将 246 当作业务缺陷数，或将构建成功写成零告警。

| 已有类别/原文 | 次数 |
| --- | ---: |
| arkts-strict-typing-required | 151 |
| arkts-no-typing-with-this | 1 |
| arkts-no-implicit-return-types | 10 |
| arkts-no-type-query | 2 |
| Function may throw exceptions. Special handling is required. | 34 |
| BuilderParam 初始化：content / selectSlot / actionSlot | 40 / 1 / 1 |
| sourceMapsPath 缺失：ibest-ui-v2 / cashiersdk / blueshieldsdk | 各 1 |
| 'delete' conflict, first declared | 1 |
| No signingConfig found for product default | 1 |
| ArkTS FAQ 汇总提示（非额外源码诊断） | 1 |

来源：报告 `:44`–`:57`；逐条位置与原始日志行号在 `logs/analysis-baseline/warning-inventory.csv`，汇总在 `warning-summary.json`。后续告警比较应使用该清单，不把诊断包的不同增量编译输出当原包警告消失。

### 2.3 隔离诊断适配：安装、启动与真实入口证据

证据来自 `workflow/verification/baseline-abi-diagnostic-v3.md`。本角色另只读查看 `logs/analysis-baseline/d58-goods-category.png`、`d59-goods-category-settled.png` 和 `d33-app-ready.png`，确认报告所述的目标占位与主页数据画面；没有操作设备或重跑构建。

`CODE_FACT`：诊断仅在 `logs/analysis-baseline/abi-diagnostic-v3` 的本题副本中改 `entry/build-profile.json5`，加入 `externalNativeOptions.abiFilters=["x86_64"]` 以及官方 `nativeLib.filter.excludes=["**/arm64-v8a/**"]`；新包不包含原始两个 arm64 so。不是原 pristine 包，也没有手工重打包。原工程 858 tracked 文件仍无差异；副本 858 文件只该配置不同；1,013 个物理依赖文件 SHA256 与原始一致（诊断报告 `:13`–`:32`）。仅业务源码相同，不将支付原生能力视作已验证。

```powershell
. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1
Set-Location D:/HCUP/cml-spec24/logs/analysis-baseline/abi-diagnostic-v3
hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon
```

`CODE_FACT`：UTC 03:31:07–03:31:35，构建退出 0（25s922ms）；诊断产物 `logs/analysis-baseline/abi-diagnostic-v3/entry/build/default/outputs/default/entry-default-unsigned.hap` 为 14,857,709 字节，SHA256 `59f4af7478bfaf6ae9d3c7bd5ccc7212f858a2f93ccdcaeab88d416d8cdc7ed7`，native libs=[]。v1 构建失败、v2 构建成功但仍含不匹配 so 的尝试均保留，未替换原包事实（诊断报告 `:17`–`:19`、`:34`–`:44`）。官方 schema/过滤实现依据与摘录已登记 `logs/analysis-baseline/abi-filter-sdk-schema-excerpt.json`（诊断报告 `:23`）。

| DEVICE_OBSERVED（仅诊断 v3） | 实际结果与范围 | 证据（均在 `logs/analysis-baseline/`） |
| --- | --- | --- |
| 安装与启动 | 精确 v3 包 `install bundle successfully`；EntryAbility `start ability successfully`；同一独立 x86_64 目标 11241 | `d30-install-v3.command.json` 及 stdout，`d31-start-v3.*`；诊断报告 `:48`–`:50` |
| 首页分类点击 | 主页有“手机”及真实商品卡；点击“手机”后仍主页；重复点击动作无独立截图，不另计样本 | `d33-app-ready.{png,json}` → `d35-home-phone.*` → `d36-after-home-phone.{png,json}`、`d37-home-phone-repeat.*`；报告 `:52` |
| 分类 tab 点击 | 分类 tab 有真实分组/子分类；点击“Xiaomi 数字旗舰”后仍分类页，前后 PNG SHA256 相同 | `d39-category-tab.{png,json}` → `d40-category-leaf.*` → `d41-after-category-leaf.{png,json}`；报告 `:53` |
| 搜索入口/输入 | 首页“搜索商品”到现有搜索页；完成首次系统输入法初始化后，TextInput 输入 phone | `d43-search-entry.*`、`d54-ime-next-step.{png,json}`、`d55-search-input.*`、`d56-search-entered.{png,json}`；报告 `:54`–`:55` |
| 搜索提交/目标页 | 点击“搜索”进入“商品分类”页，只显示“商品分类页面内容视图”，约40秒后仍相同；无目标搜索框、筛选/排序/布局控件或商品列表 | `d57-search-submit.*` → `d58-goods-category.{png,json}` → `d59-goods-category-settled.{png,json}`；报告 `:55`、`:92` |
| 部分远端数据可用 | 无需登录的样本中首页/分类/推荐词有数据；推荐词端点请求响应 status=200；不能将目标占位归因于服务器整体不可用 | `d47-app-log-all.stdout.log` PID11926 实际 NetLog，约1726–1731行；报告 `:88` |

界限：系统输入法初始化和 d44 的桌面过渡不是应用崩溃证据；不能把 `d60-netlog-v3.stdout.log` 的空采样当作目标页零请求/请求成功证明；商品筛选、排序、分页协议、库存和价格边界未做服务端验证。`d33` 树含隐藏的预建错误/加载节点，截图为正常数据，单凭树中“网络连接失败”字串不能判屏幕错误（诊断报告 `:54`、`:90`）。

最小复现：安装该 v3 包 → 启动 → 首页“搜索商品” → 输入 phone → 点击“搜索” → 观察 d58/d59 占位画面。归因有同业务源码的静态空实现、实际动作链、截图与树支持；不外推原 arm64 包在兼容设备上的运行结论。诊断报告 V01–V20 的 1 pass/4 fail/15 blocked 只是其本地聚合拆分，原包 V01–V20 仍因 ABI blocked；不代表本报告 76 个验收项均执行，也不代表官方 F-point。

设备释放按诊断报告 `:98` 已停止本题独立实例，保留实例/HAP/日志供恢复；未停止其他任务设备。

## 3. Spec 入口、路由和调用点

### 3.1 已有搜索入口链（静态事实）

1. `entry/src/main/ets/entryability/EntryAbility.ets:36` 注册路由，`:51` 先 await ORM 初始化，`:52` 才加载 `view/EntryPage`；`:100` 的注册函数在 `:106` 注册 GoodsGraph。ORM 初始化失败可能阻断整个页面加载，初始化成功是运行前置。
2. `entry/src/main/ets/view/EntryPage.ets:41` 挂载 NavigationHost；`entry/src/main/ets/navigation/NavigationHost.ets:14` 创建 NavPathStack，`:17` 保存到导航服务，`:37` 以 MainPage 为根，`:42` 按 RouteBuild 构造目标页。
3. `feature/main/src/main/ets/view/MainPage.ets:59` 首页 Tab 构建 HomePage；`:63` 分类 Tab 构建主分类页 CategoryPage。`feature/main/src/main/ets/viewmodel/MainViewModel.ets:23` 是“分类”Tab 配置。
4. `feature/main/src/main/ets/component/HomeTopBar.ets:58` 显示搜索入口文本，`:71` 转发点击；`feature/main/src/main/ets/view/HomePage.ets:39` 注入 `GoodsNavigator.toSearch()`。
5. `core/navigation/src/main/ets/goods/GoodsNavigator.ets:35` 跳转搜索路由；`core/navigation/src/main/ets/goods/GoodsRoutes.ts:13` 路由名 `goods/search`；`feature/goods/src/main/ets/navigation/GoodsGraph.ets:18` 注册搜索页。
6. `feature/goods/src/main/ets/view/GoodsSearchPage.ets:40` 使用 SearchTopAppBar；`:43` 接输入变化、`:44` 接搜索提交。历史词点击 `:109`、推荐词点击 `:132` 最终也执行 onSearch。
7. `feature/goods/src/main/ets/viewmodel/GoodsSearchViewModel.ets:76` 的 onSearch 将输入 trim，空值在 `:78` 返回；`:82` await 写本地历史、`:83` await 重新加载后，`:85` 构造 `{ featured:false, recommend:false, keyword:trimmed }`，`:90` 才调用 `GoodsNavigator.toCategory(params)`。该方法无 catch，历史读写异常可能阻断导航。既有流程从提交/推荐词/历史词直接跳目标页，没有需再次点击的商品“搜索结果列表”中间页（对应 A02）。
8. `core/navigation/src/main/ets/goods/GoodsNavigator.ets:44` 允许有/无参数跳转；`core/navigation/src/main/ets/goods/GoodsRoutes.ts:17` 的路由名是 **`goods/category`**。`feature/goods/src/main/ets/navigation/GoodsGraph.ets:20` 注册，`feature/goods/src/main/ets/navigation/GoodsCategoryNav.ets:10` 构造 GoodsCategoryPage。

以上链路为 `CODE_FACT`；第 2.3 节的 `DEVICE_OBSERVED` 已证明诊断 v3 的“首页搜索→提交 phone→目标占位页”到达链路，不将其升级为原包已走通，也不将“到达”当作带词商品展示完整通过。

### 3.2 分类入口未绑定的位置

- `CODE_FACT`：主分类页 `feature/main/src/main/ets/view/CategoryPage.ets:170` 的 buildCategoryItem 只构建图片、文字及样式，函数结束于 `:193`；`:181` 是分类名，`:192` 结束样式链，**无 onClick/导航调用**。侧栏 `:75` 仅绑定 onSideBarChange，`:200` 只滚动右侧列表，不跳转商品分类页。
- `CODE_FACT`：首页分类组件 `feature/main/src/main/ets/component/HomeCategorySection.ets:21` 的 onCategoryClick 默认空函数；`:76` 虽转发分类 id，但 `feature/main/src/main/ets/view/HomePage.ets:71` 仅传 categories，**未传 onCategoryClick**。
- `CODE_FACT`：在本题 `feature`、`core`、`entry` 的 `.ets` 跳转调用检索中，目标页的业务调用点只有 GoodsSearchViewModel 的 `:90`。导航封装、路由注册不等于分类项已有入口。
- `DEVICE_OBSERVED`（诊断 v3）：首页“手机”点击与主分类页“Xiaomi 数字旗舰”点击都未跳转，前后证据见第 2.3 节。只对这两个实际样本记录失败，不声称已穷举每个分类层级或每个数据项。
- `SPEC_EXPLICIT`：`spec/requirement.md:11` 要求通过分类或搜索结果进入商品分类页。`INFERENCE`：后续实现必须补齐既有分类流的目标页跳转；当前具体哪些分类层级可点仍需需求复审。

## 4. 相关组件、状态、数据、网络与本地存储

### 4.1 目标页现状

- `CODE_FACT`：`feature/goods/src/main/ets/view/GoodsCategoryPage.ets:13` 是 `@Local` ViewModel 实例；`:21` 使用 AppNavDestination，`:22` 固定标题“商品分类”；`:35` 唯一内容是 `Text("商品分类页面内容视图")`。
- `CODE_FACT`：`feature/goods/src/main/ets/viewmodel/GoodsCategoryViewModel.ets:8` 是空的 `@ObservedV2` BaseViewModel 子类，没有路由参数读取、可观察查询/布局/面板状态、仓库、请求、分页、搜索、筛选、排序或持久化。
- `CODE_FACT`：`core/ui/src/main/ets/component/navdestination/AppNavDestination.ets:73` 转发 aboutToAppear，`:81` 转发 aboutToDisappear，`:131` 转发 onShown；`core/base/src/main/ets/viewmodel/BaseViewModel.ets:11` 等默认生命周期均为空。因此本目标页出现本身不发商品请求。

### 4.2 已有数据契约

| 数据 | CODE_FACT 位置与现有写法 | 未确认内容 |
| --- | --- | --- |
| 目标路由参数 | `core/navigation/src/main/ets/goods/GoodsParam.ets:9`：typeId 为可选 string（`:13`），featured/recommend 为可选 boolean（`:17`/`:21`），keyword/minPrice 为可选 string（`:25`/`:29`） | 无 maxPrice、排序、布局参数；目标页尚未消费。typeId string 到请求 number[]、路由 **keyword** 到请求 **keyWord** 的显式映射均未实现 |
| 商品查询请求 | `core/model/src/main/ets/request/GoodsSearchRequest.ets:9` page=1，`:13` size=20；`:17` typeId:number[]，`:21`/`:25` min/maxPrice:string，`:29` keyWord，`:33` order，`:37` sort，`:41`/`:45` recommend/featured；`:54` 构造函数按字段赋值 | order/sort 允许字符串，未定义商品排序枚举；缺省与 false/null 的后端语义、价格单位/精度未验证 |
| 商品显示数据 | `core/model/src/main/ets/entity/Goods.ets:11` id，`:15` typeId，`:19` title，`:27` mainPic，`:35` price:number，`:39` sold:number | 真实数据分布、价格单位及排序协议需服务端/设备证据 |
| 分类数据 | `core/model/src/main/ets/entity/Category.ets:9` id，`:13` name，`:17` parentId，`:21` sortNum，`:33` children；`core/model/src/main/ets/entity/CategoryTree.ets:43` children 为 CategoryTree[] | Spec 的多个标签组如何映射分类层级、父子同时选择的语义未确认 |
| 分页响应 | `core/model/src/main/ets/network/NetworkPageData.ets:11` list，`:15` pagination；`:22`/`:23` 做 null 兜底；`core/model/src/main/ets/network/NetworkPageMeta.ets:9`/`:13`/`:17` 为 total/size/page | 非法/缺失分页元数据、服务端最后页行为需验证 |

`UNVERIFIED`（A76）：搜索入口显式传入 `featured:false`/`recommend:false`，但没有证据证明 false 与“不筛选”相同；也可能表示筛掉推荐/精选。不能因为输入类型为 boolean 就擅自赋予缺省语义。路由 keyword 与请求 keyWord 的拼写差异是代码事实，不需要由用户猜字段名；字段值、flags 和分类映射的服务语义仍需核对（独立审计 R3，`workflow/implementation/analysis-audit-v1.md:19`）。

### 4.3 网络链与已有参数传递

- `CODE_FACT`：`core/data/src/main/ets/repository/GoodsRepository.ets:30` 支持注入 GoodsNetworkDataSource，默认真实网络实现；`:38` 分类列表、`:55` 推荐搜索词、`:64` 商品分页直接转交数据源。
- `CODE_FACT`：`core/network/src/main/ets/datasource/goods/GoodsNetworkDataSourceImpl.ets:29` POST `goods/type/list`，`:50` POST `goods/search/keyword/list`，`:61` POST `goods/info/page` 且请求体原样为 GoodsSearchRequest。接口声明位于 `core/network/src/main/ets/datasource/goods/GoodsNetworkDataSource.ets:25`、`:38`、`:45`。
- `CODE_FACT`：`core/network/src/main/ets/NetworkClient.ets:16` 后端为 `https://mall.dusksnow.top/app/`，`:21` 超时 10000ms，`:23` JSON 内容类型。`core/network/src/main/ets/interceptors/AppInterceptors.ets:21` 读取 token，`:25` 仅在有值时设置 Authorization。
- `CODE_FACT`：`core/result/src/main/ets/RequestHelper.ets:41` 接已经创建的请求 Promise，`:103` 处理开始回调、loading、成功/失败；`:113` 根据 NetworkResponse.isSucceeded 取 data，`:119` 对业务失败抛 Error，`:126` finally 恢复其可选全局 loading。目标页当前未调用这些设施。
- `CODE_FACT`：现有商品分页调用示例在 `feature/main/src/main/ets/viewmodel/HomeViewModel.ets:31`：新建 GoodsSearchRequest 后 `:33`/`:34` 覆盖 page/size，`:35` 调仓库；没有商品 order/sort 的现有赋值实例可确认为排序协议。

### 4.4 当前分页基类的准确行为（并非目标页已接入）

`core/base/src/main/ets/viewmodel/BaseNetWorkListViewModel.ets:14` 是可复用 `@ObservedV2` 泛型基类。`:19` uiState 默认 LOADING；`:24` listData=[]；`:29` isLoading=false；`:34` 可上滑=true；`:38` currentPage=1；`:42` pageSize=10，和请求模型默认 size=20 不同。

| 动作/结果 | CODE_FACT 行为与行号 |
| --- | --- |
| 初次出现 | `:58` → initLoad `:66` → loadListData `:74`，调用抽象 requestListData `:52`。该链不把 isLoading 设 true，也没有重复请求 guard |
| 每次请求 | `:75` 包装 Promise，`:76` 默认禁用错误 toast，`:78`/`:79` 交成功/失败回调，`:80` finally 仅设 isLoading=false。这里不统一设置 uiState=LOADING，不保存请求快照/请求 id |
| 重试 | `:130` 设 uiState=LOADING、currentPage=1，再请求；不置 isLoading=true、不检查已加载、不清 listData 或重置 isEnableSlideUp |
| 下拉刷新 | `:140` 检查 isLoading，设 true、currentPage=1，再请求；不清已有列表，不修改 uiState 或先重置可上滑标记 |
| 上拉加载 | `:153` 对 isLoading、isEnableSlideUp、空列表做 guard；`:157` 设 true，`:158` 先将 currentPage 加 1，再请求 |
| 页 1 成功 | `:90` null 包装为空数据；`:95` 根据**响应到达时当前 currentPage**判断页 1，`:96` 替换全部列表，`:97` 空则 EMPTY 否则 SUCCESS，`:98` 更新可上滑 |
| 后续页成功 | `:102` 直接数组展开追加，无去重；`:106` 按响应分页更新可上滑；不修改 uiState |
| 页 1 失败 | `:114` 打日志；`:116` 当前页为 1 且旧列表为空才切 ERROR；已有列表时保留列表和此前 uiState |
| 后续页失败 | `:123` 当前页减 1；不清已有列表，不修改可上滑或 uiState；finally 停止 isLoading |
| 是否有更多 | `:181` 要求 pagination、total、size、page 均非 null，且 size*page<total；缺元数据返回 false。不使用本页 list.length 判定 |

`INFERENCE`：该基类已有替换、追加、失败回退和末页门禁骨架，但初载/重试的 loading guard 缺口、共享 currentPage 的到达时判断、无请求版本隔离，对快速搜索/筛选/排序重载存在旧请求覆盖新结果风险；这是静态风险，尚无并发运行复现。目标 VM 目前不继承它，不能直接声称目标页存在该并发 bug。

`INFERENCE`（A57/A63，条件性风险）：**已有非空 listData 时调用 retryRequest 后请求失败**，`:130`–`:133` 已先将 uiState 设 LOADING，`:116`–`:120` 不再更改 uiState，finally `:81` 仅清 isLoading，因此页面状态可能保持 LOADING。该调用路径是否从现有 UI 可达未验证，不能泛化成所有失败，也不能泛化成目标空 VM 已复现；见 `workflow/implementation/analysis-audit-v1.md:26`。

`CODE_FACT`/`INFERENCE`：RequestHelper.repository 接的是已创建的 Promise（`core/result/src/main/ets/RequestHelper.ets:41`），start 回调在 `:104` 执行；不能把 start 当作发起数据源调用前的互斥锁。分页元数据包装没有正数校验（`NetworkPageMeta.ets:24`–`:26`）；缺失 metadata 将禁止更多，异常 metadata 行为仍待测试（A61/A76）。

## 5. 可复用的既有架构与限制

- `CODE_FACT`：组件 `@ComponentV2 + @Local vm`、模型 `@ObservedV2 + @Trace`、AppNavDestination 生命周期转发是本题现有方式；目标页应沿原路由和容器继续承载（`GoodsCategoryPage.ets:8`、`GoodsCategoryViewModel.ets:7`、`AppNavDestination.ets:73`）。这里仅记录架构，不提出本阶段代码改动。
- `CODE_FACT`：`feature/goods/src/main/ets/viewmodel/GoodsCommentViewModel.ets:13` 继承分页基类，`:21` 用 getRouteParams 读取路由，`:31` 构造请求后 `:35`/`:36` 覆盖页码/大小。`core/navigation/src/main/ets/NavigationService.ets:192` 用 getParamByName(name)[0] 读取首个同名路由参数；缺失返回 undefined（`:195`/`:201`），重入相同路由及无参进入需边界验证。
- `CODE_FACT`：`feature/goods/src/main/ets/view/GoodsCommentPage.ets:33` 使用 BaseNetWorkListView，`:47` 使用 RefreshLayout 并绑定 loading、可上滑、同一 Scroller 与方向回调，`:53` 是 List。`core/ui/src/main/ets/component/refresh/RefreshLayout.ets:42` 透传到 IBestPullRefresh。是否仅到达底部就自动触发下一页尚待设备验证，不能仅由组件名认定满足 Spec。
- `CODE_FACT`：`core/ui/src/main/ets/component/network/BaseNetWorkListView.ets:77` 的 Stack 含 loading/error/empty/content 四层，分别用 opacity 控制（`:86`/`:96`/`:106`/`:114`），默认空/错误组件见 `EmptyData.ets:14`、`EmptyNetwork.ets:30`。
- `CODE_FACT`：`core/ui/src/main/ets/component/appbar/SearchTopAppBar.ets:100` 已封装可输入 IBestSearch，`:112` 输入、`:114` 键盘搜索、`:115` 清空、`:137` 右侧搜索按钮、`:148` 按当前 value 回调；可用于嵌入搜索栏。目标页尚未使用。
- `CODE_FACT`：`core/ui/src/main/ets/component/goods/GoodsGridItem.ets:46`/`:55`/`:72` 已渲染主图/名称/价格，`GoodsListItem.ets:41`/`:53`/`:70` 是横排图文价格卡。`feature/main/src/main/ets/view/HomePage.ets:114` 已使用网格卡，`:123` 用断点控制列数（2/3/4）；这不同于本题目标页明确要求的默认两列，不能直接认定满足。
- `CODE_FACT`：`core/ui/src/main/ets/component/modal/SpecSelectModal.ets:92` 已有 isGridMode=true，`:146` 使用 ic_menu_list/ic_menu，`:150` 切换状态，`:158` 条件构造两种布局；`:335`/`:383` 按选中状态变边框颜色，可参考其布局图标/选中风格。它是规格单选弹窗，不是本题分类多选筛选，不能将其行为当现成筛选实现。
- `CODE_FACT`：主分类页的 `feature/main/src/main/ets/viewmodel/CategoryViewModel.ets:199` 已支持从平铺 parentId 或嵌套 children 转树；`:204`–`:206` 优先返回嵌套树，`:209` 的 sortNum 排序**仅覆盖平铺输入分支**，嵌套分支 `:258`/`:270` 沿接口数组顺序转换，不应概括为所有分类组已排序。这提供已有分类数据组织证据（独立审计 R4，`workflow/implementation/analysis-audit-v1.md:20`）。

## 6. Spec 要求而目标页缺失的能力

下表“缺失”均以目标页 `feature/goods/src/main/ets/view/GoodsCategoryPage.ets:20`–`:36` 与空目标 VM `feature/goods/src/main/ets/viewmodel/GoodsCategoryViewModel.ets:8` 为 `CODE_FACT`；现有基础设施不计作目标页功能已完成。验收编号来自 `workflow/requirements/acceptance-v1.md:87`–`:138`，共 52 项 `SPEC_EXPLICIT`，本节逐组覆盖全部编号。

| 验收编号 | Spec 来源（SPEC_EXPLICIT） | 基线能力/缺失与证据定位 |
| --- | --- | --- |
| A01 | `spec/requirement.md:11` | 分类项进入目标页缺绑定：`feature/main/src/main/ets/view/CategoryPage.ets:170`、`feature/main/src/main/ets/view/HomePage.ets:71`；Spec 没指定必须让每个候选分类 UI/每层全部可点，具体入口范围待复审 |
| A02 | `:11` | 搜索直接到目标页的静态调用已存在 `feature/goods/src/main/ets/viewmodel/GoodsSearchViewModel.ets:90`；目标页不消费关键词、不查询商品，不满足完整带词展示语义。数据库 await 是入口前置 |
| A03–A05 | `:11` | 目标页标题区域没有可编辑搜索框、修改词再次搜索和商品结果；`GoodsCategoryPage.ets:22`/`:35`，`GoodsCategoryViewModel.ets:8` |
| A06–A09 | `:12` | 搜索下方“筛选”/“排序”/右侧布局图标的工具栏、上下/左右关系及操作全部缺失；目标页同上 |
| A10–A13 | `:13` | 默认两列网格及每项主图/名称/价格缺失；既有 GoodsGridItem 只是可复用卡，不是目标页接入 |
| A14–A15 | `:14` | 切单列列表与切回网格缺失；既有规格弹窗的局部布局切换不计为目标页实现 |
| A16–A18 | `:15`、`:7` | 滚到底部自动下一页、末尾追加、下拉刷新缺失；目标页没有分页 VM、滚动/刷新容器 |
| A19–A21 | `:25` | 下拉筛选面板、价格区间与多个分类标签组缺失；目标页没有分类列表请求/状态 |
| A22–A24 | `:26` | 最低价/最高价输入与中间横线缺失 |
| A25–A27 | `:27` | 标签点击、高亮、选中边框变色及多选缺失 |
| A28–A32 | `:28`、`:21` | “重置”“确认”、先调整后统一应用的草稿语义、确认关闭与实际筛选重载缺失 |
| A33–A37 | `:29` | 重开面板、清空最低/最高/全部分类选择、重置确认后的“全量展示”缺失；全量范围 A72 未决 |
| A38–A43 | `:39` | 排序下拉及五项精确文案缺失：综合排序、价格由低到高、价格由高到低、销量由低到高、销量由高到低 |
| A44–A46 | `:40`、`:35` | 选择价格升序后关闭菜单、更新按钮名称，不同排序立即重载缺失 |
| A47–A50 | `:41`、`:42`、`:35` | 数值价格升/降序、销量升/降序的请求与商品结果展示缺失；协议 A76 未确认 |
| A51–A52 | `:43`、`:42` | 综合排序恢复服务默认、价格排序后切销量再次刷新缺失 |

以下 14 项只按 `REASONABLE_DERIVATION` 承接；来源为 `workflow/requirements/acceptance-v1.md:146`–`:159`。它们的合理性已通过独立文档复审（`workflow/implementation/analysis-audit-v1.md:30`–`:41`），不是基线功能通过证据。

| 验收编号 | 派生可观察语义 | 基线事实与限制 |
| --- | --- | --- |
| A53–A54 | 新查询/刷新从首屏替换，分页和刷新保留已应用完整查询 | 基类页 1 替换、后续追加已存在（`core/base/src/main/ets/viewmodel/BaseNetWorkListViewModel.ets:95`/`:102`），但目标未接入；keyword/typeId/价格/排序/flags 查询身份尚未实现 |
| A55–A56 | 布局切换保留有序商品，纯布局不重载商品 | 目标没有布局状态/列表；不能以规格弹窗切换或 ForEach key 推定已满足 |
| A57–A59 | loading 绑定当前请求、重复触底不重复追加、旧响应不覆盖新查询 | 基类刷新/追加有门禁（`:140`/`:153`），初载/重试无门禁，`:95` 用共享页码、无版本隔离；详见第 4.4 节静态风险 |
| A60–A62 | 空结果结束且清旧数据、已知末页停止、追加失败不前移/不破坏旧列表 | 基类页 1 空变 EMPTY（`:97`）、metadata 判更多（`:181`）、追加失败页码回退（`:123`）；目标未接入，异常/缺失 metadata 和复合操作未验证 |
| A63–A64 | 首屏/重载失败可结束等待、离页旧请求不污染下一次进入 | 基类失败处理不覆盖全部加载态恢复，已有非空列表 retry 失败可能停 LOADING；没有目标页请求生命周期隔离 |
| A65–A66 | 其他排序项也关闭菜单、标题与当前选项一致 | 目标没有排序菜单或选中排序状态 |

网络状态机沿 `workflow/requirements/acceptance-v1.md:211` 的 Q（已应用查询）/D（草稿）/V（生命周期与查询版本）/P（成功页）/L（有序列表）/H（更多）语义复审，图示与动作表位于 `:216`–`:269`。这是验收一致性模型，不要求新增特定类/库；基线没有该完整闭环。仅打开菜单、编辑草稿或未确认重置时不得应用草稿，但**严格零次商品请求仅为 P02 建议**（`:279`），不将合法同 Q 刷新/预取判成 Spec 明文失败。当前阶段不选择实现方式。

十项 `UNCONFIRMED_ASSUMPTION`（A67–A76）保持在第 8.2 节，不能按未决推荐策略断言基线或后续实现失败。52+14+10=76 是本地验收拆解统计，不是官方分值。

### 6.1 诊断运行证据对验收编号的映射

以下只映射已完成/被阻断的观察范围，不将验证报告 V02 的“到达 pass”扩大为 A02 完整数据/请求语义通过。原包的所有运行项仍是 ABI 安装前置 blocked。

| 验收编号/子行为 | 诊断 v3 的运行状态 | 依据与未完成部分 |
| --- | --- | --- |
| A01（两个分类样本） | fail | d33→d36、d39→d41 均未进入目标页；其他分类项没有逐项执行 |
| A02 的到达子行为 | pass；A02 完整带词结果语义未通过 | d56 输入 phone、d57 提交、d58 到达占位页；没有商品结果/目标查询管线，不能判完整 A02 pass |
| A03 | fail | d58/d59 标题是普通“商品分类”文本，没有目标输入框 |
| A04–A05 | blocked | 缺目标输入框，无法编辑并再次搜索，未做假输入 |
| A06–A09 | fail | d58/d59 无搜索下方控制栏、“筛选”“排序”与布局图标，结构可直接观察缺失 |
| A10–A13 | fail | 目标页无商品列表、默认两列或商品卡主图/名称/价格；首页商品不计入目标结果 |
| A14–A18 | blocked | 布局控件、商品列表与刷新容器缺失，往返、触底和下拉操作未执行 |
| A19–A52 | blocked | 筛选/排序入口缺失，不能进入面板或菜单完成后续操作；不存在可做的数据排序/筛选断言 |
| A53–A66 | blocked | 目标页真实请求/列表/布局/菜单闭环缺失，派生状态机、并发、空/错/末页与恢复未执行 |
| A67–A76 | 未决/未运行 | 语义尚未裁定，价格/排序/flags/分类等服务协议未核对，不将建议策略作为失败判据 |

## 7. 前置环境、登录、服务端和测试数据

- `CODE_FACT`：导航保护列表 `core/navigation/src/main/ets/RouteInterceptor.ts:16`–`:37` 不含 goods/search 与 goods/category；`core/navigation/src/main/ets/NavigationService.ets:52` 仅对受保护路由拦截。`DEVICE_OBSERVED`（诊断 v3）：未登录样本可显示首页、分类、推荐搜索数据并进入目标占位页（诊断报告 `:88`）；**不能据此认定尚不存在的目标商品查询、筛选和排序均获匿名服务授权**。
- `CODE_FACT`：`entry/src/main/module.json5:54` 声明 INTERNET 权限。商品分类、推荐搜索词、商品分页都依赖上述远程 POST 链；目标链路未提供本地商品 fallback。`DEVICE_OBSERVED`（诊断 v3）：部分远端链路和数据确实可用，见第 2.3 节。`UNVERIFIED`：目标筛选/排序/分页参数语义、可控数据、错误/乱序服务行为仍需专门验证；不再将服务器整体可达性笼统写成未测。
- `CODE_FACT`：搜索历史仓库 `core/data/src/main/ets/repository/SearchHistoryRepository.ets:30` trim 后存储；数据源 `core/database/src/main/ets/datasource/searchhistory/SearchHistoryLocalDataSourceImpl.ets:78` 使用 `search_history(keyword TEXT PRIMARY KEY, search_time INTEGER)`，`:93`/`:94` 先删后插，`:125` 时间倒序，`:143` 截取数量；搜索 VM `feature/goods/src/main/ets/viewmodel/GoodsSearchViewModel.ets:148` 取最近 10 条。`entry/src/main/ets/entryability/EntryAbility.ets:94` 初始化 app.db，`:51` await 完成才加载 UI；数据源构造 `:29` 立即检查/迁移表，搜索 `GoodsSearchViewModel.ets:82`/`:83` await 历史读写后才 `:90` 导航。数据库初始化与历史读写成功是 A02 搜索入口的真实前置，不能只验网络。目标页无独立本地查询状态存储。
- `CODE_FACT`：token 使用 Preferences（`core/datastore/src/main/ets/datasource/token/TokenStoreDataSourceImpl.ets:18` token_store、`:22` token 键），默认空值（`:47`）。不读取/记录用户 token 或账号机密。
- `SPEC_EXPLICIT`：价格示例 50~200 与标签示例“运动户外”见 `spec/requirement.md:26`/`:27`；`INFERENCE`：验证至少需要多个分类组、可区分的类别商品、跨 50/200 边界商品、价格/销量非等值且顺序不同的数据、超过一页的数据、空结果/最后页/失败场景。不能假定线上当前具备这些数据。
- `UNVERIFIED`：尚无本轮证据证明可控测试数据源/账号已经提供。WebDAV 未在 Spec 或所读目标链路中出现，不将其作为已确认前置需求。

## 8. 测试可观测性风险与未解决项

### 8.1 选择器

- `CODE_FACT`：目标页 `GoodsCategoryPage.ets:20`–`:36` 没有 `.id()`；当前占位文字只能用于确认占位状态。主分类项 `CategoryPage.ets:170`、首页分类项 `HomeCategorySection.ets:52`、搜索页标签 `GoodsSearchPage.ets:147`、SearchTopAppBar 搜索输入 `:100`/按钮 `:137`、两类商品卡片均缺稳定 `.id()`。
- `INFERENCE`：首页搜索文本与按钮“搜索”、推荐词和历史词、不同层级的同名分类、网格/列表的同一商品标题及反复出现的价格可能造成基于 text 的选择器歧义。实现时应为入口、目标根、搜索输入/提交、面板按钮/价格输入/标签、五种排序项、布局切换、列表/商品项/关键字段、加载/空/错/末页状态补稳定 id；本阶段不写 id。
- `INFERENCE`：BaseNetWorkListView 通过 opacity 保留四层节点，是否有隐藏节点仍被 Hypium 找到、是否阻挡命中需要实机 dump/点击验证，不能静态声称 selector 一定可用。
- `CODE_FACT`：`workflow/requirements/acceptance-v1.md:17` 与 `:76` 建议 `gc.*`；它们不是现存选择器或 Spec 固定命名。`feature/main/src/main/ets/component/HomeCategorySection.ets:36`、`feature/main/src/main/ets/view/HomePage.ets:121` 的 ForEach key 是渲染 key，不是测试 id。`INFERENCE`：若后续网格/列表都使用 `gc.goods.<id>`，应核对当前可见树是否唯一，配合几何位置和可见性断言，避免 opacity/虚拟化制造误判（独立审计 R8，`workflow/implementation/analysis-audit-v1.md:24`）。
- `DEVICE_OBSERVED`（诊断 v3）：d33 UI 树实际含隐藏错误/加载的预建节点，而截图为正常主页；这证实“节点存在不等于当前可见”的风险。目标控件还不存在，选中边框属性、网格/列表复用 id、虚拟化下商品有序断言的工具可观测性仍未验证。

### 8.2 未决事项与交接

| 项目 | 状态及负责证据 |
| --- | --- |
| pristine 构建、告警、安装/启动 | 已合并本轮报告；构建 pass，原包因 ABI 安装/启动 blocked，见第 2.1/2.2 节 |
| 隔离诊断包及真实页面可达性 | 已合并 `workflow/verification/baseline-abi-diagnostic-v3.md`；安装/启动及搜索到占位页有实际证据，两个分类样本点击不跳转；保持与 pristine 不同证据链 |
| 全部原子验收项/八维边界/稳定选择器编号 | A01–A76 已逐组映射；原始八维、B01–B12 × G1–G7、Q/D 状态机仍以 `workflow/requirements/acceptance-v1.md:87`–`:279` 为准，无运行通过声明 |
| A67：空词/纯空格提交 | 未决，不能把既有搜索页拒空词自动推广为目标页规则；需求稿 `:285` 保留不提交/去词全量分支 |
| A68–A70：单边/空格价格、非法/逆序/精度、闭开端点/相等价 | 未决，需求稿 `:286`–`:288` 推荐不等于主 Agent 已裁定；价格单位也待服务证据 |
| A71：分类组/标签层级、父子含义、同标签去选等 | 未决，需求稿 `:289`；分类树与 typeId 数组只证明结构，不能推导全部层级/布尔组合 |
| A72：重置全量范围 | 未决，需求稿 `:290`；入口 keyword/typeId/flags/minPrice 是否保留要明确，关联 A37/A54 与请求状态机 |
| A73–A74：关闭手段/草稿保留、重开回显 | 未决，需求稿 `:291`–`:292`；明确仍是 A30 未确认草稿不能应用，不强加新增取消按钮 |
| A75：返回/重启后的状态恢复 | 未决，需求稿 `:293`；历史表不等于目标查询状态持久化，不擅自新增跨进程存储要求 |
| A76：排序/金额/分类/flags/分页协议 | 未决，需求稿 `:294`；price/sold 与 asc/desc 是候选值，false 不等于无筛选尚无服务实证；缺 metadata 策略未冻结 |
| 初载/重试 guard、旧响应覆盖、同名路由取第一个参数、下拉组件自动触底行为 | 静态风险，后续实现方案与运行验证应覆盖，不在 0-analyze 修改 |

本轮合并已经完成：八个 0-analyze 基线主题、76 项验收对照、独立审计修正、pristine/诊断包证据边界齐全。未解决项保留为原包兼容设备运行、目标功能尚未实现的运行测试、A67–A76 语义/服务协议与可控数据，而非尚未补写的报告内容。

当前阶段没有对外接口变更、生产文件改动或实现顺序。后续方案应以已确认验收与独立只读审计为输入。
