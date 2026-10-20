# cml-spec1 编码角色只读基线审计 r1

审计时间：2026-10-20 11:26–11:33 +08:00。角色：`harmony_implementation`。派工：`workflow/implementation/dispatch-analysis-r1.txt`；本轮仅审计，未设计或实现功能。

结论：**677 个 tracked 文件的路径集和逐文件 SHA256 均与批准指纹一致；HEAD、Spec、metadata 一致；受 Git 跟踪的业务代码、资源、测试和构建输入没有变化。静态报告的核心源码事实成立。安装、启动及四场景运行表现仍未验证，不能据此作功能通过结论。**

本进程观察到 `CODEX_THREAD_ID=01a1575b-5b42-71e2-943b-1d61058056bc`。未将共享的 `CODEX_SESSION_ID=01a1574d-f7fd-7032-96ff-7fec7f78a664` 作为自身 UUID；本报告仅能证明工具进程暴露的 thread 值，原生会话归属由主 Agent 的会话登记交叉核对。

## 1. 批准输入与独立复核

| 对象 | 本轮实测值 | 结果 |
| --- | --- | --- |
| `git rev-parse HEAD` | `7014cebd60f2181fac2a36d399ca16b3d6a175ab` | 符合批准 HEAD |
| `spec/requirement.md` SHA256 | `491ea9b5efe284f449873234ba0c86345a0cc2eece2e097898de06a2c4f59d4b` | 符合批准 Spec |
| `spec/metadata.json` SHA256 | `8b4f53895d59cc4a74780c9d6d24d80ae59d236965755a7091f92375eb695768` | 符合批准 metadata；其中 base_commit 同 HEAD |
| `workflow/analysis-code-fingerprint.json` SHA256 | `c0185cc1032cfc2c76ec7c8fab1149dac323f93b7e19ba1690ce134dc4098e9d` | 本轮审阅版本 |
| `workflow/design/baseline-static-r1.md` SHA256 | `c461df99e58f46e8a6a5136e5800bba53c04a471a0a0febbf27a2d0e9c0949f6` | 本轮审阅版本 |
| `workflow/verification/baseline-r1.md` SHA256 | `80d2ac0aaba1f744b5cd7f15d57aa448132bb8e4bc3079fbc4745cb19d8fdfef` | 本轮审阅版本 |

审计命令和观察：

- 将 `analysis-code-fingerprint.json.tracked_files_sha256` 的每一条与 `Get-FileHash -Algorithm SHA256` 的当前结果比较：677 条，缺失 0，哈希不一致 0。
- 将上述指纹路径集与 `git ls-files` 排序后用 `Compare-Object` 比较：两边均 677 条，集合差异 0；防止仅检查旧清单而漏掉新增 tracked 文件。
- `git diff --name-only`、`git diff --cached --name-only`、`git diff --numstat`、`git diff --cached --numstat`、`git diff --name-only 7014cebd60f2181fac2a36d399ca16b3d6a175ab --` 均无输出。
- 当前 `git status --short` 仅显示本题未跟踪记录目录：`inputs/`、`logs/`、`spec-harness/`、`spec/`、`system-config/`、`test-harness/`、`traces/`、`workflow/`；没有 tracked 变化。
- 独立读取 verification 的 `traces/baseline-analysis/source-before.json` 和 `source-after-build.json`：各 677 条记录，逐项与批准分析指纹比较，差异均为 0。没有借用准备阶段总览会话作为功能证据。
- 按项目构建清单、锁文件、模块声明、构建配置、hvigor 文件等常见 tracked 构建输入路径筛选共 120 个；它们已包含在上述 677 个逐项比较中。资源和其他 tracked 文件同样全量比较，并非仅检查 `.ets`。

**证据范围限制**：`.gitignore:1-6` 排除了 `node_modules`、`oh_modules`、`local.properties`、`.idea`、`**/build` 和 `.hvigor`；`:14` 排除了生成的 `BuildProfile.ets`。本轮 `git status --ignored --short -- local.properties oh_modules node_modules` 观察到 `!! oh_modules/`。批准指纹只含 tracked 文件，故不能从空 diff 推导 ignored 依赖安装内容、本地设置、SDK 或构建缓存前后完全相同。本角色没有改动这些目录，也没有执行依赖安装；对这些内容的全量历史一致性保持未验证。

## 2. 静态报告源码事实审计

| 审计对象 | 独立核对的精确证据 | 审计判断 |
| --- | --- | --- |
| 启动入口 | `entry/src/main/module.json5:6`、`:17-18`；`entry/src/main/resources/base/profile/main_pages.json:3`；`entry/src/main/ets/entryability/EntryAbility.ets:50-57` | 先初始化 ORM，再加载 `view/EntryPage`，回调初始化 UI 并申请音频权限；与报告一致。没有实际启动证据 |
| 根页面与宿主 | `entry/src/main/ets/view/EntryPage.ets:39-42`；`entry/src/main/ets/navigation/NavigationHost.ets:13-17`、`:36-42` | `NavigationHost` 使用 `NavPathStack`，根内容直接构建 `MainPage()`；不是首页路由自动入栈 |
| 当前主界面 | `feature/main/src/main/ets/view/MainPage.ets:25-31`、`:39-48`、`:49-130` | 标题“主页面”、正文“主页面内容视图”和通知演示按钮；未挂载四个目标页、底部标签或分页组件。源码事实成立，屏幕实际布局仍未观察 |
| 四页及注册 | `feature/main/src/main/ets/navigation/MainGraph.ets:17-21`；`HomeNav.ets:10`、`CategoryNav.ets:10`、`CartNav.ets:10`、`MeNav.ets:10`（均在同 navigation 目录） | MainGraph 共注册 5 个具名目标：主页面加四子页；注册本身不等于底栏组合或导航触发 |
| 四页内容 | `feature/main/src/main/ets/view/HomePage.ets:20-26`、`:34-35`；`CategoryPage.ets:20-26`、`:34-35`；`CartPage.ets:20-26`、`:34-35`；`MePage.ets:20-26`、`:34-35`（后 3 文件均在同 view 目录） | 各自只有标题和占位 Text；不含优惠券、商品列表或标签栏。报告没有把它们写成已集成业务页，判断正确 |
| 主模块状态 | `feature/main/src/main/ets/viewmodel/MainViewModel.ets:7-9`、`HomeViewModel.ets:7-9`、`CategoryViewModel.ets:7-9`、`CartViewModel.ets:7-9`、`MeViewModel.ets:7-9` | 五个 VM 为空的 `BaseViewModel` 子类，无选中索引、动画实例或重选处理 |
| Lottie、分页和回顶 | 下述全量定向搜索；`feature/main/oh-package.json5:8-18`；`core/ui/src/main/ets/component/refresh/RefreshLayout.ets:22-23`、`:42-51` | 搜索仅命中通用 RefreshLayout 的 scroller；未发现业务 Lottie、横向分页、底栏选中或首页回顶链。该负向结论限应用源码/清单，不扩大成第三方依赖内部绝无此能力 |
| 首页数据能力 | `core/model/src/main/ets/entity/Home.ets:14-38`、`:44-50`；`core/data/src/main/ets/repository/PageRepository.ets:18-19`、`:26-27`；`core/network/src/main/ets/datasource/page/PageNetworkDataSourceImpl.ets:15-18` | 首页模型和 `GET page/home` 仓库链存在，但主模块占位页和空 VM 没有调用；不能推导启动发起首页请求或已有优惠券 UI |
| 网络与拦截器 | `core/network/src/main/ets/NetworkClient.ets:16`、`:19-27`；`core/network/src/main/ets/interceptors/AppInterceptors.ets:10-25` | 基础地址、10 秒超时、JSON 头、直通拦截器描述正确；没有由此推出服务器可达或 token 注入 |
| 登录与持久化 | `core/navigation/src/main/ets/RouteInterceptor.ts:16-37`；`core/state/src/main/ets/UserState.ets:158-159`、`:169-175`；`core/datastore/src/main/ets/datasource/account/AccountStoreDataSourceImpl.ets:18-26`、`:32-33`、`:41-42`、`:59-60`；`core/util/src/main/ets/storage/PreferencesUtil.ets:45-49` | 主模块四路由不在当前保护列表；用户/账户持久化已存在，未发现底栏索引持久化调用。不存在静态的必须先登录前置证据 |
| 购物车能力 | `core/data/src/main/ets/repository/CartRepository.ets:18-19`、`:82-83`；`core/database/src/main/ets/datasource/cart/CartLocalDataSourceImpl.ets:24-35`、`:128-130` | 已有本地购物车数据源和读取能力，但 CartPage/CartViewModel 没有接入；报告描述正确 |
| 可观测性和原有测试 | 下述 `.id(` 搜索；`entry/src/ohosTest/ets/test/Ability.test.ets:25-32`；`entry/src/test/LocalUnit.test.ets:24-30` | 未发现应用业务组件稳定 id；现有两类断言为字符串模板，不能作为本题功能测试覆盖证据 |

复核搜索在本题根目录执行，依赖和构建输出排除；负向搜索返回 1 表示无匹配，不是构建失败：

```powershell
rg -n -i 'lottie|swiper|tabcontent|tabs\(|tabbar|selectedindex|currentindex|scrolltotop|scrollto\(|scrollEdge|scroller|emitter|\.id\(' entry/src/main feature core -g '*.ets' -g '*.ts' -g '*.json5' -g '*.json' -g '!**/oh_modules/**' -g '!**/build/**'
rg -n -i 'lottie' -g 'oh-package*.json5' -g '!**/oh_modules/**' -g '!**/build/**' .
rg -n 'RefreshLayout\(|getHomeData\(|PageRepository' entry/src/main/ets feature core -g '*.ets' -g '*.ts' -g '!**/oh_modules/**' -g '!**/build/**'
rg -n 'HomePage\(|CategoryPage\(|CartPage\(|MePage\(|MainRoutes\.' entry/src/main/ets feature/main -g '*.ets' -g '*.ts'
```

结果：第一条仅有 `RefreshLayout.ets:20`、`:23`、`:44` 的 scroller 注释/声明/传递；第二条无匹配；第三条仅仓库导出/定义、数据源接口/实现，无业务调用者；第四条仅四个 nav builder 和 MainGraph 注册。主模块资源枚举为 3 张通知测试图片、base/en string 及 float 配置，没有底栏动画资源。当前源码缺少四场景实现的结论不依赖单一关键词搜索，而由根页面、全部主模块页面/VM 和调用点读取共同支持。

## 3. 纠正与表述边界

1. **核心事实无实质纠错**：静态报告对主入口、四占位页、空 VM、无 Lottie/分页/回顶及已有模型/数据链的描述均可定位到当前源码。未发现需要更改需求或重大调整方向的反证。
2. **构建输入不变的表述须限定**：完整实证为“tracked 源码、资源、测试、构建配置和锁文件与批准基线相同”。ignored 的安装依赖及本地配置没有批准前后指纹，不能称全部构建环境/输入已经全量证明未变。此限制也适用于把 verification 的 677 文件指纹扩张成全环境指纹的说法。
3. **运行报告状态需更新**：`workflow/design/baseline-static-r1.md:9`、`:128` 仍写等待 verification 运行报告。现已存在本轮 `workflow/verification/baseline-r1.md`：构建成功，设备占用且独立新实例启动失败，安装/启动/交互为 blocked。可以将“报告待交付”更新成“报告已交付，运行证据仍缺”，但本角色未修改其他角色报告。
4. **稳定 id 属于可观测性建议**：静态报告 `:110` 的“未来实现时需补 `.id()`”应标注为本地验收建议。`test-harness/README.md:74` 原文是建议；Spec 没有指定 id、BY.key 或其他选择器名称。不能把此建议升级成独立的 Spec 验收失败项，亦不能将这些名称假设为官方评测约定。

## 4. 基线缺口及现有可复用结构

以下是源码与 Spec 的差距，不是运行失败的虚构结果，也不是本轮实现方案：

- 场景一：`MainPage.ets:39-130` 无四个底部标签、选中态或四页组合；默认首页和点击切页均缺少当前源码入口。
- 场景二：全部主模块页面/VM 未提供横向分页或滑动联动；暂无“内容滑动与底栏选中、动画同步”调用链。
- 场景三：`MainViewModel.ets:7-9` 无动画状态；没有初始化播放、离选首帧静止、重返播放一次的调用证据。
- 场景四：`HomePage.ets:34-35` 仅占位 Text，无法在现有业务 UI 建立顶部“领取”滚出视区前置；MainPage 无已选首页重点击分支、回顶接收点及保持动画不重播的控制。

可复用事实仅限现有结构：

- `feature/main/Index.ets:6-8`、`MainGraph.ets:17-21` 及四个 nav builder 已具备模块出口和具名路由注册框架。
- `core/ui/src/main/ets/component/navdestination/AppNavDestination.ets:68-69`、`:76-77`、`:92-93`、`:126-130` 已向 VM 转发生命周期；`:123-138` 已集中标题、背景和安全区 padding。
- `entry/src/main/ets/viewmodel/EntryViewModel.ets:14-17`、`:25-26` 已连接 WindowAdapter、安全区与断点状态；这不等于已验证底栏在目标设备上的位置或尺寸。
- `core/base/src/main/ets/state/BaseNetWorkUiState.ets:5-17` 和 `core/base/src/main/ets/viewmodel/BaseNetWorkViewModel.ets:47-53`、`:95-112` 已有网络状态基类；首页聚合模型、仓库、网络数据源和本地购物车亦已存在。当前主模块 VM 没有采用网络状态基类。
- `RefreshLayout.ets:22-23`、`:42-51` 已有可传入 Scroller 的通用刷新封装，但业务调用者为空；其存在不能证明首页已支持回顶，更不能把回顶等同刷新。

## 5. 构建证据交叉核对和未验证项

本角色没有新建构建/设备进程，没有修改或重跑构建，没有启动模拟器。只读核对已有日志与实际产物：

- `logs/analysis-baseline-build-results.json:3-7` 记录 clean 退出 0，`:10-14` 记录 assembleHap 退出 0；`logs/analysis-baseline-assembleHap.log:1304` 为 `BUILD SUCCESSFUL`。
- 实际读取 `entry/build/default/outputs/default/entry-default-unsigned.hap`：19,133,822 bytes，SHA256 `49a5284455f6b6f9c29873da1431d7542bfd233071b67b46e5f52851d68906a4`，与 `logs/analysis-baseline-hap.json:2-5` 一致。该哈希绑定当前待装产物，不能证明已经安装运行。
- `build-profile.json5:3` 为 `signingConfigs: []`，`:7-9` 为 HarmonyOS `6.0.1(21)`；构建日志 `:1300` 提示未找到签名配置。设备目标由本地框架记录为 API 23（`test-harness/README.md:6-8`）；兼容表现和安装签名是否被接受均未实测。
- 启动回调确实申请麦克风（`EntryAbility.ets:52-57`、`core/util/src/main/ets/permission/PermissionUtils.ets:195-196`），且模块声明权限（`entry/src/main/module.json5:61-69`）。权限弹窗是否出现、是否遮挡目标 UI 仍未验证。
- verification 报告的环境阻塞不能由静态阅读补齐。尚缺当前 HAP 的安装/启动结果、实际首页截图/UI 树、四标签点击和滑动、动画帧序列/一次播放/首帧复位/颜色、已选首页重点击回顶，以及“不切页、不额外重播”的动态负向证据。
- 首页服务器可达性、实际优惠券数据、空/失败态和真实滚动前置均未验证。Spec 没有要求执行领取交易；“领取”仅是本题回顶可见性观察锚点。
- 当前原有字符串测试模板无本题覆盖；本角色没有修改、删除或放宽断言，也没有编写新测试。

## 6. 写入范围和交接

本轮唯一写入：`workflow/implementation/baseline-audit-r1.md`。未修改生产代码、配置、依赖、测试、Spec、需求/设计/自测报告或调度状态；未访问其他题、上游工程/历史/Issue/PR/补丁/副本、原题包或初始化总览会话，未查询网络。

读取了已安装 `arkts-syntax-assistant` 与 `hmos-arkts-knowledge-retriever` 技能说明以约束审阅；本报告只根据本题源码给出静态事实，没有引入外部 API 语义或新实现设计。因为没有生成 ArkTS 或运行构建，本轮不触发代码生成后的编译流程。

交回主 Agent：核心静态事实可采用；请保留 tracked 指纹范围限制、将设备状态标为运行阻塞，并将选择器建议与 Spec 明文区分。未解决项是设备/运行证据、ignored 构建输入的全量历史一致性及会话 UUID 原生归属交叉核对。最终基线和功能结论由主 Agent 结合独立自测确定。
