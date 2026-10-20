# cml-spec1 功能实现方案 r1

## 1. 版本、批准输入与范围

- 方案版本：`do-design-r1`，日期 2026-10-20；唯一产物为本文。只读本题当前源码、Spec 和记录、`../common/` 及通用官方技术资料；未修改生产代码、测试、依赖、全局 workflow 状态或设备，未访问其他题、题包、来源应用上游实现/历史/Issue/PR/副本、初始化总览会话。
- 已实算 `spec/requirement.md` SHA256=`491ea9b5efe284f449873234ba0c86345a0cc2eece2e097898de06a2c4f59d4b`、`spec/acceptance.md` SHA256=`7d7cedd00fb2c8cd5ce5be285da8428477a29ea1228cf63d0f8c9ec371b8497a`，均与批准值一致。基线为 metadata 的 `7014cebd60f2181fac2a36d399ca16b3d6a175ab`。
- 功能阶段需求复核：`workflow/requirements/do-review-r1.md`，SHA256=`14cb73d680630c50190a066fb0c1de4090f2e328e55ef1ed2b1404cc9d06b332`。A1–A39 沿用；主 Agent 已批准 A40 边界不循环、A41 非首页同标签无操作、A42 暖恢复保留、A43 所有图标有限播放且离开统一第一帧灰色静止、A44 跨标签返回保留首页滚动。这五项是本轮实现约定，不能倒写成 Spec 明文。
- 本子 Agent 环境实读 `CODEX_THREAD_ID=01a15798-722e-79d0-8668-f98754c9dda5`；这是本会话身份线索，需主 Agent 核对原生日志的 id、父会话、`agent_path=/root/design_do` 与 cwd 后登记。`CODEX_SESSION_ID` 是继承父值，不作为本子会话 UUID。
- 目标为既有 MainPage 内的四标签导航、真实 Lottie、首页滚动及生命周期边界。没有导航必需的网络、账号或持久化需求；采用本地可展示内容，不接入商品交易系统。

## 2. 本题证据与最小文件范围

入口链继续使用 `EntryAbility.onWindowStageCreate → view/EntryPage → NavigationHost → MainPage`。`EntryAbility.ets:52` 加载内容；`NavigationHost.ets:38` 已直接挂载 MainPage；不增加替代 @Entry 页面，不改初始路由、不 push 四个 tab 路由。

当前 `feature/main/src/main/ets/view/MainPage.ets` 正文为通知演示，四个子页都只有独立 AppNavDestination 包装与占位内容。Main/Home ViewModel 为空的 `@ObservedV2` 子类。`core/ui/.../AppNavDestination.ets:124–139` 负责导航、生命周期和安全区。直接在 Main 的分页内嵌套四个 NavDestination 不合适，应让现有子页支持普通内容嵌入；独立路由仍保持其包装。

| 文件 | 最小变更与责任 |
| --- | --- |
| `feature/main/src/main/ets/view/MainPage.ets` | 移除通知演示正文和对应 import；保留 MainPage / MainViewModel / 外层 AppNavDestination；隐藏无意义的“主页面”标题，正文为纵向 Column：上方横向 Swiper、下方固定四标签。持有分页控制器与唯一首页 Scroller；四页按首页/分类/购物车/我的固定构建。 |
| `feature/main/src/main/ets/viewmodel/MainViewModel.ets` | 补单一已提交索引和递增选择 epoch；集中去重提交。初始 index=0、epoch=1，只初始化一次，不从 onShown/onForeground 重置。 |
| `feature/main/src/main/ets/view/HomePage.ets` | 新增 `embedded` 参数和可传入 Scroller；普通 Column 内容根、顶部优惠券 `领取`、`限时精选`、`推荐商品` 与足够纵向内容。独立路由默认仍经 AppNavDestination。 |
| `feature/main/src/main/ets/viewmodel/HomeViewModel.ets` | 放有明确类型、稳定 id 的本地展示数据；如确需滚动位置备份，保存偏移。不要把 UI Scroller、Canvas 或网络塞进数据模型。 |
| `feature/main/src/main/ets/view/CategoryPage.ets`、`CartPage.ets`、`MePage.ets` | 各补 embedded 模式及页面根 ID；保留原 VM 和默认独立路由包装。分类可展示本地分类，购物车使用现有 EmptyCart，个人页可展示未登录状态；不得通过登录/请求成功门控标签。 |
| 新建 `feature/main/src/main/ets/component/TabLottieIcon.ets` | V2 图标组件，封装 Canvas、真实 AnimationItem、异步就绪与 epoch 消费、颜色/首帧/事件/释放。四实例固定存在，按 name 单独管理。 |
| 新建 `feature/main/src/main/resources/rawfile/lottie/tab_home.json`、`tab_category.json`、`tab_cart.json`、`tab_me.json` | 四个可辨识的本地标准 Lottie shape 动画，自行制作简单房屋/网格/购物车/人物路径。资源含明确首帧和可见关键帧变化，不引用网络图片或表达式。建议约 48 帧/30fps，作为实现取样信息，不作为 Spec 固定时长。 |
| `feature/main/oh-package.json5` 与实际被 ohpm 更新的锁文件 | 新增精确依赖 `"@ohos/lottie": "2.0.33"`；只提交安装实际需要的 lock 变化，不手改 node/oh_modules 内容。 |
| `entry/src/main/ets/entryability/EntryAbility.ets` | 最小移除 loadContent 回调中的无关麦克风请求及未使用 PermissionUtils import，保留 ORM、路由、ContextUtil、IBest 初始化。权限声明与通用 PermissionUtils 不必改。 |
| 自测角色：`hypium_tests/test_main_tabs.py`，必要的本题采帧辅助文件及日志 | 继承 HarnessTestCase，落实本文 ID、四场景与边界。本方案角色不写测试。 |

不需修改 core 路由、网络、数据库、全局安全区组件、其他 feature 的业务实现。若实现选择额外拆出很小的本地数据/动画辅助类型文件，仍限 main 模块并在交接列出，不由此扩展功能范围。

## 3. 固定依赖与资源加载

本地检查范围是本题 `oh_modules/.ohpm`、manifest/lock 和 main 资源：已有包为 dayjs、area-data、ibest-orm、ibest-ui-v2、axios、hamock、hypium、lunar，没有 Lottie。不能把普通图片/符号位移算作 Lottie。

2026-10-20 只读查询官方 registry `https://ohpm.openharmony.cn/ohpm/@ohos/lottie`，确认固定稳定版 `2.0.33` 存在，MIT、无传递依赖。又在内存读取该官方 HAR（207550 bytes），校验 SHA512 匹配 registry，并核对实际 `package/index.d.ts`；没有安装、落盘或查询应用上游。

- tarball：`https://ohpm.openharmony.cn/ohpm/@ohos/lottie/-/lottie-2.0.33.har`
- integrity：`sha512-6abOGWdGwxLlVc+WoEDlqL0TJGjMut8gZubi2Jvmml6v2noHnvor3rX5qVPuuW8QXmyOL30+CJVmx+ahFzdaCQ==`
- 已核实导出：`AnimationItem.currentFrame`(135)、`isPaused`(198)、`goToAndStop(value,isFrame?,name?)`(311)、`goToAndPlay(...)`(321)、`addEventListener`(404)、`removeEventListener`(413)、`changeColor(number[],...)`(421)、`loadAnimation`(665)、指定 name 的 `destroy`(674)。事件集合包含 DOMLoaded、enterFrame、drawnFrame、complete、error/data_failed。

实现用 `Canvas.onReady` 创建该图标实例，经当前 host 的 ResourceManager 读取 rawfile，再解码/解析为依赖声明允许的 `animationData`，调用 `lottie.loadAnimation({ container, renderer:'canvas', animationData, autoplay:false, loop:false, name, contentMode:'Contain' })`。不采用库的 `path` 跨 HAR 查找；官方库说明该 path 基于 entry/ets，跨包资源应读出后传 animationData。ArkTS 按实际类型声明适配 JSON 数据类型，不引入 any、@ts-ignore 或放宽编译规则。

初始化/播放控制必须等 DOMLoaded；Canvas.onReady 不等于资源已解析。固定布局尺寸保持正方形，首帧即为清楚可见的完整图标。选择时纯黑 `[0,0,0,1]`，离开/未选时统一灰 `[128,128,128,1]`；动态变色完成后需重新绘制当前帧。颜色是本方案具体实现选择，测试取抗锯齿图形内核像素，不要求每个边缘像素精确相同。

## 4. 状态、事件与接口契约

### 4.1 V2 所有权

MainPage 继续 `@ComponentV2`、`@Local vm: MainViewModel`，VM 继续 `@ObservedV2`，可视驱动字段用 `@Trace selectedIndex: number=0`、`@Trace selectionEpoch: number=1`。不要混入 @State/@Prop/@Link V1 传递。

四个固定 TabLottieIcon 用只读 `@Param` 接收 `tabKey`、`selected`、`selectionEpoch`、资源名/ID；组件内用 @Local 保存可观察引擎快照，Canvas 上下文、AnimationItem、ready/generation/lastConsumedEpoch 用恰当的实例字段。`@Monitor('selected','selectionEpoch')` 只调同一个 reconcile，不能在 build 中播放。状态批处理后 reconcile 多次也由 epoch 去重。

HomePage 新参数 `@Param embedded:boolean=false`、`@Param scroller:Scroller=...`，MainPage 明确传持久的同一个 Scroller。`embedded=true` 构建普通内容，false 仍包原 AppNavDestination；其他三页同理。子页不写父级 @Param。

### 4.2 唯一提交入口

统一索引 `0=首页、1=分类、2=购物车、3=我的`。Swiper 使用 fixed children、`.loop(false)`、`.indicator(false)`、`.autoPlay(false)`、`.cachedCount(3)` 和横向方向；不使用按当前索引销毁重建子页的 if/else，不用 LazyForEach。底栏在 Swiper 外，纵向滚动只发生在首页内部。

`MainViewModel.commitSelection(index): boolean` 是唯一修改已提交索引/epoch 的位置：越界或 index 等于已提交值直接 false；确实不同则原子更新 selectedIndex 和 selectionEpoch，返回 true。该方法只由 `Swiper.onChange(index)` 调用；onAnimationStart/End、图标回调、点击与 onShown 均不得再独立提交或发一次播放。

点击标签由 MainPage 的 `requestTab(index)` 处理：

1. 若 pager 正在横向手势/页间动画中，保存最新待处理点击目标；多次输入合并为最后一次，不在半途修改 VM 或播放。用 onAnimationStart/onAnimationEnd 管理 busy；onChange 提交后、动画结束后均可尝试 drain。采用 controller.changeIndex(target,false) 的点击跳页，不额外启动跨多页动画。
2. 空闲且 target=已提交索引：首页只调用 `homeScroller.scrollTo({xOffset:0,yOffset:0,...})`；其他三页直接返回。此分支绝不调用 changeIndex、commitSelection 或图标 play。
3. 空闲且 target 不同：请求 `SwiperController.changeIndex(target,false)`，等实际 onChange 再提交；点击函数不先改 selectedIndex。短暂持有 requestInFlight 以免回调尚未到达时重复发同一请求；onChange 落定后释放并 drain。
4. gesture 取消、端点反向滑动不产生不同 onChange，不提交、不增长 epoch。onAnimationEnd 用来清 busy/drain，不重复提交。若目标与当前已相同则清请求，不永久锁住导航。
5. queued 目标在实际落定后按当时 committed index 判定；若切换期间没有真正接受某次过快输入，记录实际落定的转换，不伪造一次返回播放。需要时调用 finishAnimation 后再 drain，以所用 SDK 的事件顺序实测为准；仍保持 onChange 唯一提交和最后输入收敛原则。

初始化是构造出的 index=0、epoch=1；初始 onChange(0) 是 no-op。点击请求、Swiper 通知与渲染不各增一遍播放。实现可局部适配原生控制器事件时序，不能改成双来源写状态；快速点击/手势混用必须实测。

### 4.3 图标 reconcile 与真实引擎事件

每图标持有 `ready`、`instanceGeneration`、`lastConsumedEpoch`。创建/异步读取回调都核对本实例 generation，销毁后的旧回调直接忽略。一个图标只处理自己的唯一 name，禁止无参 `lottie.destroy()` 停掉其他图标。

| 输入/事件 | 必须执行的动作 |
| --- | --- |
| Canvas/资源未就绪，当前选中 | 仅保留最新 selected+epoch 意图；不能提前把“已播放”记为成功。 |
| DOMLoaded | ready=true，然后根据**此刻最新** selected+epoch reconcile。仍选中且 epoch 未消费才从 0 帧播放；已离开则灰色并 goToAndStop(0,true)，不补播已过期请求。 |
| selected=true，ready，epoch 未消费 | changeColor(黑)；标记本次请求 epoch；goToAndPlay(0,true)，loop=false；只消费一次。 |
| selected=true，同一 epoch 的重复通知 | 无新增 play；原播放可自然继续。 |
| selected=false，ready | 灰色并 goToAndStop(0,true)，停止且第一帧；取消尚未开始的过期播放意图。 |
| enterFrame/drawnFrame | 从实际 AnimationItem/事件取 currentFrame、isPaused；本次 play 后实际出现前进/渲染才更新 observedPlaySeq，不能仅因点击或 goToAndPlay 调用就伪报已播放。 |
| complete | 记录引擎完成与当前帧；选中图标停在完成帧，不循环。 |
| 真正组件销毁 | 移除所加监听、按唯一 name destroy，generation 失效。暖恢复原实例不能借此制造一次新初始化播放。 |
| error/data_failed | 真实记录错误及不可播放状态，导航仍可操作；静态图标兜底不得记为 Lottie 通过，作为实现/资源失败修复。 |

从首页切走无论由点击还是左滑、播放是否结束，reconcile 都复位到首页第一帧静止。真正从其他页回首页时 epoch 变更，播放一次。已选首页点一次/多次/顶部点，epoch 不变，图标不新增播放。若旧播放尚未结束，不强制暂停它来伪造“无新增播放”。

### 4.4 滚动、内容、生命周期和网络

首页顶端构建一个始终真实存在的优惠券卡及唯一逐字 `领取` 锚点；下方是有实质的本地 `限时精选`、`推荐商品` 展示，采用明确类型/稳定 id 的商品或生活用品条目、描述与本地已有合法图片/图形。不得用“测试内容”、空白高度、隐藏文字或不合理重复行充滚动证据；不宣称真实下单、领券成功。Spec 不要求触发领取动作，不新增领取交易/库存接口。

内容自然高度须超过当前屏幕内容视口，能够多次纵滑让顶部入口完全移出视口，底栏仍固定。实现可选择适量本地卡片并在目标设备测量，不将数量/价格/排序当成需求。使用真实 Scroll，不通过隐藏/删除入口伪造滚走。

相同 Scroller+固定缓存子页保留首页位置；返回首页仅切标签与播放，不调用回顶。若目标 SDK 实测仍会回收/重新布局，最小补偿为 HomeViewModel 保存真实 currentOffset().yOffset，在重建布局完成后无动画恢复一次；不要每次 onShown 无条件恢复旧位置覆盖正在回顶。优先让缓存避免该额外流程，A44 必须设备验证。

同首页重击使用 Scroller 回到 y=0，可用短纵向回顶动画；连续点击重复设置相同目标可合并，最终顶部可操作，不触发横向 changeIndex 或重新构建首页。默认无永久“回顶中”锁。

VM 与四个图标属于 MainPage 实例，不把 selectedIndex/epoch 存入 Preferences/AppStorage/PersistenceV2。后台/前台及现有覆盖路由返回保留实例、选择与滚动，不在 onShown 重播。完整终止后新 MainPage 构造回首页并初始化播放。不得为测 A42 另造子路由；若无覆盖路由入口，测试正常后台/前台，说明其他路径不适用。

网络八维结论：四标签/播放/回顶均为本地操作；无请求、无网络 loading、无导航索引持久化。现有启动数据库初始化保留。A37 的请求 pending/失败注入在没有新增请求的方案中为不适用；可测断网下仍可导航，但不能声称请求失败分支已发生或网络测试全部通过。

首次麦克风弹窗来自 EntryAbility 的无关测试请求，且基线拒绝后会进入系统设置；它与本题没有业务关系。最小处理是移除启动请求调用，保留通用权限能力，既不向用户索取麦克风授权，也不改变主入口来绕开弹窗。首次安装和拒绝授权残留状态下均应能直接到本题导航页。

## 5. 稳定 ID 与动态观察契约

沿用 acceptance 的 prospective 名称，实施后成为实际契约：

| 对象 | ID |
| --- | --- |
| 主页面/底栏/横向分页 | `main_root` / `main_tab_bar` / `main_content_pager` |
| 四标签可点击父区域 | `main_tab_home` / `main_tab_category` / `main_tab_cart` / `main_tab_me` |
| 四标签文字 | `main_tab_home_text` / `main_tab_category_text` / `main_tab_cart_text` / `main_tab_me_text` |
| 四图标 Canvas 或唯一固定观察父区域 | `main_tab_home_icon` / `main_tab_category_icon` / `main_tab_cart_icon` / `main_tab_me_icon` |
| 四页普通内容根 | `home_page` / `category_page` / `cart_page` / `me_page` |
| 首页滚动/顶部领取 | `home_scroll` / `home_coupon_receive` |
| 两展示区（辅助精确纵滑） | `home_flash_sale` / `home_recommend` |

根和分页的非可见 accessibilityDescription 可输出当前真实已提交页；标签输出语义 selected；图标输出来自引擎事件的 `ready, frame, paused, consumedEpoch, observedPlaySeq, completeSeq`。标签可被辅助技术正确读作“首页，已选中”；诊断不得加可见调试文字、伪造事件或作为商品内容。若 XML dump 不暴露对应描述，以实际可读取属性/结构化 hilog 为辅证，不能修改测试预期降低要求。

自测同时使用：稳定 ID 操作；当前页根与 PAGER/屏幕交集判断可见（预构建节点存在不算显示）；`领取` 与 Scroll 视口交集判断离开/恢复；图标 bounds 的真实屏幕 ROI 多帧；引擎事件/状态仅作为辅证。

动态证据应带动作开始/结束时间、采帧时间、目标 ROI 坐标、相关 epoch 与截图原件：

- 播放：动作后实际 ROI 至少出现三个不同时间采样，出现可见图形变化并落定；真实引擎帧前进/完成对齐。不要用整个屏幕变化（文字或翻页）证明图标播放。
- 第一帧静止：同一图标刚初始化未选中/离开复位时记录其灰色第一帧参照，再连续采样证实稳定；与真实 frame≈0、paused 对齐。不要仅拿黑色最终帧当第一帧。
- 返回一次：隔开初始播放与离开/返回，返回后只有一个新的 epoch 和一个真实播放序列，有限播放结束；引擎监听不得自行补增返回计数。
- 无新增播放：等待旧播放结束后下滚再重击，图标 ROI 稳定、observedPlaySeq 不增加、epoch 不变；另覆盖旧播放仍进行时重击，允许旧序列继续但无新序列。回顶的内容变化从图标 ROI 排除。
- 黑/灰：等待布局/颜色落定后按四图标 ROI 的非背景图形像素比较选中黑色及其他灰色，不把字体黑色当图标变黑。

可从资源帧数/帧率选择约 1.6 秒播放、50–100ms 采样及足够等待窗口。具体采样率是验证实现参数；官方需求未规定固定毫秒/哈希。

## 6. 八维覆盖与测试映射

本表继承 `spec/acceptance.md` 每一 A 项的原文和八维；以下逐组给出实现落点与可执行检查，不合并掉独立断言。网络列 N=无 Spec 强制请求且方案没有新增该请求；每一行都需在测试结果中明确此事实，不能填“网络已通过”。前置数据无需账号、服务端商品或购物车条目；场景四仍需上节真实本地内容。

测试编号：T01 启动/四标签；T02 点击分类/购物车；T03 滑动与混合切换；T04 初始化/离开/返回 Lottie；T05 首页滚动重击；T06 重复/快速/取消/端点；T07 空状态/离线；T08 暖恢复/冷启动。均在 `hypium_tests/test_main_tabs.py` 中保留独立断言及 A 索引。

| A 项 | 入口 | 前置数据 | 用户动作 | UI 结果 / 实现落点 | 数据结果 | 网络 | 返回结果 | 边界 / 测试 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A1、A2、A3 | 正常启动入口链 | 新 MainPage | 启动 | 四逐字标签在下方；首页在上方；MainPage/VM | index=0，唯一选中 | N | 新实例默认首页 | 权限无关请求已移除；T01 |
| A4 | 已选首页 | 分类无需后端 | 点击分类 | 分类为当前活动页；Swiper onChange | index=1 | N | 非返回 | 内容几何可见；T02 |
| A5、A6、A7 | A4 切换 | Lottie 就绪或排队 | 点分类 | 分类真实播放且黑，其余三灰；TabLottieIcon | 单 epoch，真实播放序列 | N | 首页离开复位 | 分开动画/颜色断言；T02/T04 |
| A8、A9 | 分类页 | 空购物车允许 | 点购物车 | 购物车当前显示，购物车图标真实播放 | index=2，单 epoch | N | 非返回 | 不能只判页面略播放；T02 |
| A10、A11、A12 | 首页内容区 | PAGER可滑 | 有效左滑 | 分类可见、底栏联动及真实播放 | index=1，一次提交 | N | 非返回 | 无底栏点击；T03 |
| A13 | 分类内容区 | 已落定分类 | 继续左滑 | 购物车可见，底栏/图标对应 | index=2 | N | 非返回 | 顺序固定；T03 |
| A14、A15 | 购物车页 | 我的可用 | 点我的 | 我的当前显示、其图标真实播放 | index=3，单 epoch | N | 非返回 | 点击/滑动共用提交；T03 |
| A16 | 新主页面初始化 | Canvas/资源异步 | 等待就绪 | 首页自动真实播放；DOMLoaded reconcile | 初始 epoch=1，只消费一次 | N | 不适用 | 不以重复 onShown 补播；T01/T04 |
| A17、A18、A19 | 首页 | 首页可在播放中 | 点击我的 | 我的页面+播放；首页第一帧灰色静止 | index=3，H frame=0 paused | N | 已离开首页 | 动画中途也测试；T04 |
| A20、A21、A22 | 我的/其他页 | 此前真实离开首页 | 点首页 | 首页可见、文字黑、真实重播一次 | 新 epoch；单播放序列 | N | 首页滚动保留 | 区分同页点击；T04/T08 |
| A23 | 已选首页 | 顶部入口+足够真实内容 | 明确纵滑浏览 | 领取离开视口，底栏固定 | y>0，index仍0 | N | 尚未返回 | 不隐藏/删除入口；T05 |
| A24、A25 | 下滚且已选首页 | 同一领取锚点在视口外 | 点已选首页 | Scroller自动回顶，领取可视 | y→0 | N | 同一首页顶部 | 禁重建首页；T05 |
| A26、A27、A28 | A24 全程 | 记录当前 epoch/播放 | 重击首页 | 唯一首页始终选中；无页间过渡/新增播放 | index、epoch不变 | N | 未发生标签返回 | ROI排除内容回顶变化；T05 |
| A29 | 任一标签 | 四固定页 | 每次有效切换 | 内容、唯一选中、活动图标一致 | 一个 committed index | N | 回首页遵循A20 | 独立检查四项；T02/T03/T06 |
| A30 | 中间/末页 | 非越界方向 | 有效右滑或购物车左滑 | 按 H/C/K/M 邻接联动播放 | 相邻索引变化一次 | N | 分类右滑回首页真实重播 | 双向，不只左滑；T03 |
| A31、A32 | 首页顶部/下滚/回顶中 | 首页已选 | 一次/连续快速同击 | 最终顶部，无切页/新增播放 | index、epoch不变 | N | 始终同一首页 | 旧播放可继续；T05/T06 |
| A33 | 任一页/切换中 | busy/待处理目标 | 快速交替点击与滑动 | 最终页、标签、图标一致不锁死 | 实际提交去重，待处理收敛 | N | 实际回首页一次 | onChange与点击不双计；T06 |
| A34 | 首页 | Scroll有足够内容 | 明确纵向浏览 | 首页标签不变，底栏可点 | 仅y变化 | N | 不适用 | 内纵外横无全屏抢手势；T05 |
| A35 | 任一内容页 | 原页稳定 | 部分横拖后取消/回拖 | 原页/实际落定页与标签一致 | 未离开不增epoch | N | 无假回首页播放 | 不硬编码手势阈值；T06 |
| A36 | 空购物车/未登录我的 | 无服务器数据 | 四标签点击/滑动 | 空状态不阻断导航 | index仍可提交 | N | 回首页正常播放 | 首页场景四仍可建立；T07 |
| A37 | 本地页面 | 无本题请求 | 离线切标签/回顶 | 导航、播放、回顶正常可完成 | 无永久loading/请求状态 | N | 返回不等待请求 | 失败注入不适用，不能伪称通过；T07 |
| A38 | 非首页后完全终止 | 普通数据保留 | 终止再冷启动 | 新实例首页、初始播放 | index=0，初始epoch | N | 新主实例 | 区分暖恢复；T08 |
| A39 | 首页正在播放/已结束 | 首页选中 | 点击他页或左滑离开 | H第一帧灰色且静止 | H消费过期意图取消 | N | 再回首页单次播放 | 初始未ready即离开也覆盖；T04/T06 |
| A40（约定） | H或M端点 | 对应端点稳定 | H右滑/M左滑 | 停原页，无新播放 | index/epoch不变 | N | 未返回另一端 | loop(false)；T06 |
| A41（约定） | 已选C/K/M | 图标状态已记录 | 重击同标签 | 同页无新增播放 | epoch不变 | N | 未离开 | 不扩展首页专属回顶；T06 |
| A42（约定） | 非首页/下滚首页 | 实例仍存活 | 后台→前台；已有子路由返回如可达 | 保留选择/滚动，不新增初始化播放 | VM/epoch保留 | N | 暖恢复原状态 | 不造子路由，冷启动另测；T08 |
| A43（约定） | 任一选中图标 | 本地标准JSON/引擎 | 选中、等待结束、离开 | 有限真实播放，离开第一帧灰色静止 | loop=false，frame/paused真实 | N | 再选中从0播 | 所有图标相同策略；T04/T06 |
| A44（约定） | 下滚首页 | 记录y与可见卡片 | 切他页→真实返回H | 首页原浏览位置保留且播一次 | y保持，新选择epoch | N | 再同击才回顶 | 不在回首页时scrollTo(0)；T05/T08 |

空输入/纯空格与文本提交不适用：本题没有输入框/搜索/表单；不新增输入框凑测试。无数据覆盖购物车/未登录状态。取消覆盖部分横滑；关闭覆盖应用完整终止、暖后台恢复。商品分页末页、请求取消和领券交易不适用，端点标签由 A40 单测。

## 7. 实现顺序与独立验证

1. 编码角色先确认基线 tag/HEAD 与批准矩阵；沿原入口替换通知正文，四子页 embedded 普通内容、底栏、固定 Swiper、唯一提交方法和稳定 ID。先设备验证点击/横滑能落定与初始首页。
2. 补真实本地首页内容、独立 Scroller、同首页重击分支，验证领取可滚出/回到可视与跨标签偏移。不要等业务网络数据才能进入场景四。
3. 安装精确 Lottie 2.0.33，保留真实 lock 与资源；实现四个图标 DOMLoaded/epoch/generation、黑灰、首帧、有限播放。先核对真实图形变化，再做颜色/尺寸视觉细节。
4. 移除启动无关麦克风请求；确认首次安装/冷启动入口不被其遮挡，暖恢复不重置；补快速、取消、端点与未ready离开分支。
5. verification 在本题 `hypium_tests/` 编写/运行 T01–T08 及 ROI 多帧证据。构建/设备命令前先 dot-source `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`；依赖安装由编码角色执行，设备由主 Agent 串行分配，不能抢占别题设备。
6. 使用 `hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon`，独立报告新旧告警差异。每次自测前安装本题**刚构建**的 HAP，记录 hash/install/updateTime/设备；不能只启动已有同名包。从 logs 下用 common `.venv` 和 `harness.runner --project ... --device ... --json ...` 运行，保存命令、退出码、UI树、截图/帧、引擎日志和 A 项结果。
7. 失败时保留原始证据再最小修复。构建和启动不代表功能通过；若某动态观察工具不可用，状态记未验证并补采，不以隐藏描述/源码计数单独判通过。交付前只还原真实生成噪声，不覆盖其他角色改动。

## 8. 风险、取舍与失败路由

| 风险/失败指纹 | 最小处理与归类 |
| --- | --- |
| 点击和 onChange 双播放、同首页重击epoch增长 | 实现偏离：回到唯一 onChange→commit；删点击/生命周期直接play，回归T04/T05/T06。 |
| DOMLoaded晚到后播了已离开的图标 | 实现偏离：核对generation与最新selected/epoch；只保留最新意图，离开首帧。 |
| Swiper原生回调顺序导致请求未释放/最终页错 | 先收集 onChange/animation start/end/request 序列；局部适配 busy/drain/finishAnimation。若无法维持单一提交才回方案修订，不能多源写索引掩盖。 |
| 子页NavDestination嵌套或安全区重复 | 实现偏离：embedded只构建普通内容；安全区由外层AppNavDestination管理一次，勿改全局组件。 |
| 离开首页后滚动归零 | 先查固定子页/cache/Scroller是否重建；必要时真实offset备份一次恢复，限Home/Main。A44不能被取消。 |
| Canvas静止、shape不支持或black/gray错误 | 资源/实现：简化为标准shape关键帧，读DOMLoaded/error与ROI；局部修资源/绘制。静态图标兜底不算通过。 |
| 引擎描述显示播放但ROI未变化 | 证据或动画失败：检查frame关键帧、Canvas尺寸/可视性/绘制事件，补真实采帧，不能仅调高计数。 |
| 引入第三方声明新增告警 | 记录2.0.33真实声明及新增诊断，先检查错误使用/本地适配；不改ignored库、屏蔽编译或降验收。确为依赖固有告警由主Agent决定固定版本局部替换，并重做来源登记/回归。 |
| 领取无法移出视口 | 本地内容不足/布局失败：用实质本地卡片自然扩展适量高度；不隐藏入口，不填空白凑通过。 |
| 需求解释改变 | 回主Agent请求requirements复审；普通API/布局可逆适配自行处理，不再逐项向用户批准。 |

本方案没有阻断性需求未决项。生产实现、构建、实际安装和动态运行都尚未由本方案角色执行，不能把本文当成功证据。

## 9. 来源登记与检索限制

1. 本题批准 Spec/acceptance、`workflow/requirements/do-review-r1.md`、本轮实读 Main/四子页/VM/入口/AppNavDestination，及本题 `workflow/design/baseline-static-r1.md` 的定位证据；均属本题资料。
2. 官方 OHPM registry：`https://ohpm.openharmony.cn/ohpm/@ohos/lottie` 及上述2.0.33 HAR，只读核对固定版本/声明/完整性，未读来源应用代码。
3. 通用库维护方 README：`https://gitee.com/openharmony-tpc/lottieArkTS/blob/master/README_zh.md`，核对 Canvas/DOMLoaded、首帧控制、颜色、按name销毁、animationData加载；它是独立动画库文档，与本题来源应用无关。未进入其Issue/PR/History/示例应用实现。
4. 华为官方 Swiper API：`https://developer.huawei.com/consumer/en/doc/harmonyos-references-V13/ts-container-swiper-V13`，检索结果可读取缓存/索引/控制器说明；changeIndex(index,useAnimation) API12+，本题SDK21满足。官方V2装饰器索引：`https://developer.huawei.com/consumer/en/doc/harmonyos-guides-V14/arkts-v2-decorators-V14`。部分官方页面 open 返回空/错误，不将未取得的正文冒充已核实；细节以本机SDK编译和实际事件验证为准。
5. 已应用本机 `arkts-syntax-assistant` 与 `hmos-arkts-knowledge-retriever`。后者首次检索脚本因缺 `references/doc_index.json` 失败；已检查本地 docs 邻近目录，但V2/ArkUI不在该纯语言库范围，故使用上列官方来源。语言静态类型限制另读 `C:/Users/22580/.codex/skills/arkts-syntax-assistant/references/en/typescript-to-arkts-migration-guide.md` 的 Static Typing Is Enforced；没有借此执行编译或修改技能包。
6. `D:/HCUP/common/test-harness/README.md` 只读用于 HarnessTestCase、BY.key 与安装后运行约定。未访问其他题工程或修改common。
