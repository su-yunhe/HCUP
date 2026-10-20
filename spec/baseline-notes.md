# cml-spec17 基线调查（0-analyze）

分析阶段及授权补充调查已完成。原始未修改包的全量构建、安装和启动已通过，两条下单入口因登录前置条件受阻。用户随后授权了独立本地测试构建，已在无账号条件下进入既有确认页，完成必要的非输入交互、备注输入及新增地址流程调查。原工程844个受版本控制文件未改；新增内容仅为隔离测试设施、一次性构建副本和采证。原始包证据与本地补充结果分别记录，真实后端下单未验证。

以下至“无账号本地调查补充”之前为原始普通包调查记录，保留当时的证据资格和运行限制。本报告仅支撑 `spec-harness/0-analyze.md` 的现状调查，不代表功能完成或正式评测结果。执行派工：`workflow/verification/dispatch-01.md`。日期：2026-10-19；宿主 Windows / PowerShell；Agent `/root/baseline_verification`。没有修改生产代码、Spec、业务配置或断言，没有使用其他题工程、题包、上游修复历史。没有绕过登录，也没有猜测账号。

## 输入、源码与环境

- HEAD：`d6a6ba7480fbd0a30075462e46bb4344a430ba61`。
- Spec SHA256：`81d6d215138d27533848c7eb94f0d6a451241bd431f76297720755d340d8cc9a`；完整记录在 `traces/baseline-01/spec-fingerprint.json`。
- `git diff --stat` 构建前后均空。全部 tracked 文件逐文件 SHA256 在 `tracked-sha256-before.txt` / `tracked-sha256-after.txt`；`tracked-hash-diff.txt` 为空。测试期间没有生产源码变化。后续任何代码变化均需重新判定、重跑相关证据。
- 原生进程环境：`CODEX_THREAD_ID=01a15321-b0ef-7cc1-b352-1be9214d9d08`、`CODEX_SESSION_ID=01a15320-35c3-7341-a387-a8c8cec04015`；未读取会话原始记录。由主 Agent 对比父环境，不能用这些值推断子会话隔离。
- 每个本次 PowerShell 构建、设备进程均先加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。DevEco Studio 6.1.0.860，SDK `D:/HarmonyDev/sdk/api23`；Node v18.20.1、hvigor 6.23.7、hdc 3.2.0c。
- 最初发现的 `11237`、`11239`、`11241` 经主 Agent 确认为其他题独立实例，本次只查询设备状态，未操作其 UI、安装或中断进程。
- 按主 Agent 明确协调，新建本题独立实例 `CmlSpec17Baseline`，目录 `traces/baseline-01/emulator-instances/CmlSpec17Baseline`，设备 `127.0.0.1:11243`。启动前确认端口空闲；所有 Start-Process 使用 Hidden；未执行接受协议命令。
- 实际设备 API 23 / `emulator 6.1.0.115(SP11DEVC00E115R4P11)` / 1308 × 2880；实例配置 dpi=560、x86_64、RAM=4096MB、存储6144MB。公共 `harness.env_check` exit 0，规格检查通过；它不验证所有硬件差异，也不是官方评测。

## 构建、安装与启动（pass）

所有相对证据路径以下均相对 `traces/baseline-01/`。

| 动作 | 实际命令 | 退出码 | 证据 |
| --- | --- | --- | --- |
| 首次增量构建 | `hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug assembleHap --no-daemon` | 0 | `build.log`；仅实际重现 unsigned 配置告警 |
| 清理构建输出 | `hvigorw.bat clean --no-daemon` | 0 | `clean.log`；仅构建工具生成目录 |
| 全量编译 | 同首次构建命令 | 0 | `full-build.log`，BUILD SUCCESSFUL，18 s 672 ms |
| 创建模拟器 | 见 `emulator-create-command.txt` | 0 | `emulator-create.log` / `emulator-create-error.log` |
| 启动模拟器 | 见 `emulator-start-command.txt`；`-hdcPort 11243 -bootmode coldboot` | launcher 已启动 | `emulator-start.log` / `emulator-start-error.log`；在线及系统命令成功证明实际启动 |
| 安装本次 HAP | `hdc -t 127.0.0.1:11243 install -r entry/build/default/outputs/default/entry-default-unsigned.hap` | 0 | `install.log`，`install bundle successfully` |
| 启动本次应用 | `hdc -t 127.0.0.1:11243 shell aa start -a EntryAbility -b com.joker.coolmall` | 0 | `start.log`，`start ability successfully`；后续真实应用截图、UI 树、PID日志 |
| 环境检查 | `python -m harness.env_check --device 127.0.0.1:11243`，PYTHONPATH 指公共 test-harness | 0 | `env-check.log` |

HAP：`D:/HCUP/cml-spec17/entry/build/default/outputs/default/entry-default-unsigned.hap`。

SHA256：`88a99de864e56beb0a8a0f3d553ccae658f467fa21bb05de7f8430f056614a34`（`hap.json`）。本题 signingConfigs 为空；独立模拟器直接接受本次 unsigned HAP，因此没有补签名、修改配置或私钥。签名工具帮助及公共 SDK 证书清单只用于调查可行路径，未用于修改全局环境或 HAP。

创建实例额外告警：找不到 DevEco Studio `bin/idea.properties`，无法写 Device Manager 配置；工具明确说不影响实例启动，后续设备实际在线。启动 stderr 报无视频输入设备。本次无需相机，不将其当作订单功能失败。

## 本次全量构建告警目录

这是本次 clean 后全量编译的真实日志，不采用准备期日志替代。`warnings.csv` 与 `warnings-full.md` 保存所有诊断文本、文件位置、重复出现项及 `full-build.log` 行号，未去重。`warnings-index.txt` 可直接检索原日志；索引脚本为 `workflow/verification/summarize-baseline.py`，运行 exit 0。

| 分类 | 原始诊断块数 | 内容与处理 |
| --- | ---: | --- |
| 资源名冲突 | 177 | `delete/edit/search/total/app_name/placeholder_float/address_edit/cancel/confirm/my_footprint/phone_number/invalid_phone_number/qq/wechat` 等资源在多个模块和语言目录重名；完整路径及全部资源名见清单 |
| ArkTS / 编译提示 | 236 | 234 条带 `File:` 源位置诊断（含依赖 strict typing / this type / 设计系统 BuilderParam 等），另 1 条 FAQ 提示、1 条 `sourceMapsPath` 缺失；逐项清单保留，不能把两条额外提示均称为 sourcemap 告警 |
| 无签名配置 | 1 | `No signingConfig found for product default` |
| 合计 | 414 | 这里的单位是日志诊断块，不是唯一源码位置、错误数、测试数或官方分值 |

本次没有修复任何告警。首次增量构建与全量编译的告警范围不同，不能把全量告警说成增量日志也重现了。

## 实际 UI 路径与证据

采证脚本 `workflow/verification/capture-baseline.ps1` 每次固定 `127.0.0.1:11243`，执行真实 `uitest uiInput`、`dumpLayout`、`screenCap`、`aa dump -l`。`device-commands.log` 保存操作时间、命令、原始返回及退出码。每个编号同时保存 `.png`、`.json` 和 `-missions.txt`。下列坐标均为设备原始 1308 × 2880 像素：

| 步骤 | 实际动作及观察 | 证据编号 |
| --- | --- | --- |
| 启动 | 首页显示分类、限时精选、Xiaomi 17T Pro ￥3999.00 等公共商品内容 | `01-launched` |
| 商品详情 | 点首页商品 `(200,2225)`，显示 Xiaomi 17T Pro，底部有“加入购物车”“立即购买” | `02-goods` |
| 选择规格 | 点“立即购买” `(1100,2700)`，弹出规格；点黑色 12GB+256GB `(240,1500)`，显示库存238、数量1 | `03-buy-now`、`04-spec-selected` |
| 立即购买入口 | 点弹层“立即购买” `(970,2715)`，显示登录选择页“验证码登录”“账号密码登录”，未进入确认订单页 | `05-buy-confirm` |
| 登录前置 | 点“账号密码登录” `(650,2000)`，两个 TextInput 均空；本题 inputs/spec/README 未发现明确测试凭据。未提交未知账号 | `06-account-login` |
| 添加购物车 | Back 两次返回商品；点加入购物车 `(700,2700)` 后点规格层加入 `(350,2715)`，出现“添加购物车成功” | `07-return-login` 至 `10-added-cart` |
| 详情购物车图标 | 点详情底部购物车 `(240,2720)`，仍停在商品页，未观察到跳转；此项不是本题 Spec 必需入口 | `11-goods-cart` |
| 主 Tab 购物车 | Back 回首页，点购物车 Tab `(820,2715)`，显示该商品黑色 12GB+256GB ×1 | `12-home`、`13-cart` |
| 选择结算 | 勾选该规格 `(130,715)`，合计￥3999.00，按钮“结算(1)” | `14-cart-selected` |
| 购物车结算入口 | 点结算 `(1100,2480)`，同样转到登录选择页，未进入确认订单页 | `15-cart-checkout` |

运行网络日志 `app-hilog.log` 使用应用 PID 3496 非阻塞抓取（命令及 exit 0 单独保存）。商品详情、规格列表、类型列表请求均观察到 HTTP 200；15:54:02 与 15:55:57 各出现 `Intercepting route to order/confirm, redirecting to Login`。这证明本次相关公共数据和登录拦截可观察，不证明有认证请求权限或创建订单接口可用。未直接探测私有接口。

首页合并 UI 树同时含“加载中...”“网络连接失败”等未显示状态节点；截图实际呈现商品内容，不能只凭树中文字断言整页网络失败。后续测试须区分可见性和隐藏组件。最初采证脚本给 hdc 传 `/` 风格 Windows 绝对目标路径，hdc 返回 `[Fail]` 但进程码0，未拉回图片；已改成 Windows 路径并检查 `[Fail]`，重新采证成功。失败尝试仍在原始操作日志中，未当作有效截图。

## 按 Spec 步骤记录运行状态

`blocked` 表示本次真实前置条件阻断，不能记 pass；静态缺口单独列出。未调用未实现函数来伪造 UI 通过。

| 来源 | 可观察要求 | 状态 | 本次证据 / 限制 |
| --- | --- | --- | --- |
| 场景一 步骤1 | 确认页浏览商品、填备注、确认地址 | blocked | 两条既有入口都被登录拦截；无合法凭据，未进入确认页 |
| 场景一 步骤2 | 有地址点“提交订单”发请求 | blocked | 同上；没有执行提交 |
| 场景一 步骤3 | 商品列表、地址ID、备注、优惠券ID请求参数 | blocked | 无创建订单请求可抓取；静态模型存在不等于实际参数正确 |
| 场景一 步骤4 | 创建成功返回订单ID和实付金额 | blocked | 未发送创建请求、未获得订单返回 |
| 场景一 步骤5 | 用返回ID及金额跳支付页 | blocked | 未创建订单、未进入支付页 |
| 场景二 步骤1 | 无默认地址进入确认页 | blocked | 需要合法登录及无默认地址测试数据 |
| 场景二 步骤2 | 点击提交检测缺失地址 | blocked | 确认页未可达 |
| 场景二 步骤3 | Toast“请选择收货地址”，阻止提交 | blocked | 未实测 Toast、未进行无请求断言 |
| 场景二 步骤4 | 地址列表选择/新增后返回 | blocked | 地址路由也需登录；未读取真实地址数据、未创建地址 |
| 场景二 步骤5 | 补充地址后正常下单并跳支付 | blocked | 无登录/地址/创建订单链路前置条件 |
| 场景三 步骤1 | 购物车选择结算进入确认页 | blocked | 添加、选择和结算按钮已实测，但结算最终进入登录页，所以整步不记 pass |
| 场景三 步骤2 | 提交成功返回订单ID | blocked | 未进入确认页、未提交 |
| 场景三 步骤3 | 成功后逐项异步清理已购买内容 | blocked | 没有订单成功事件；未操作清理函数 |
| 场景三 步骤4 | 全规格已买删除整条商品记录 | blocked | 同上；未构造成功下单环境 |
| 场景三 步骤5 | 部分规格已买仅删选中规格 | blocked | 同上；未构造成功下单环境 |
| 额外边界 | 请求失败、取消、重入、重启、重复点击、清理失败、组合规格 | not_run | 0-analyze 基线且目标页面被阻断，不把边界推测写成运行结果 |

构建、安装、启动、公共商品展示、本地添加购物车、选中金额汇总的基础检查为 pass；这些不能替代上表的目标需求证据。本报告没有官方隐藏测试、成绩或通过率。

## 代码实证（非实测完成结论）

| 能力 / 风险 | 本题源码证据 |
| --- | --- |
| 既有确认入口 | `feature/goods/src/main/ets/viewmodel/GoodsDetailViewModel.ets:172` 的 buyNow 缓存商品，`:178` 调 OrderNavigator.toConfirm；`feature/main/src/main/ets/viewmodel/CartViewModel.ets:274` 结算调用同一路由 |
| 路由及登录前置 | `core/navigation/src/main/ets/order/OrderRoutes.ts:13` 为 order/confirm；OrderNavigator.ets:29 跳转；`RouteInterceptor.ts:24` 保护确认页；`NavigationService.ets:52` 检查登录并改为登录路由，与运行日志一致 |
| 确认页数据 | `core/network/src/main/ets/datasource/page/PageNetworkDataSourceImpl.ets:36` GET page/confirmOrder；`core/model/src/main/ets/entity/OrderConfirm.ets:12` 默认地址、`:16` 用户券；尚未认证实测其返回 |
| 状态与复用机制 | OrderConfirmViewModel 是 @ObservedV2，商品、备注、券和金额为 @Trace；继承 `core/base/src/main/ets/viewmodel/BaseNetWorkViewModel.ets:13`，其 uiState/data @Trace，`:48` 使用 RequestHelper 并转 LOADING/SUCCESS/ERROR。确认 VM `:84` 先发起异步缓存读取再调用基类网络生命周期，`:108` 清订单缓存；既有流程可复用，异步时序尚未实测 |
| 表单与提交 | `feature/order/src/main/ets/view/OrderConfirmPage.ets:79` 展示 vm.data.defaultAddress；`:247` 备注字段已有 `value: this.vm.remark!!` 绑定，输入回写未实测，不能因未显式 onChange 判定未绑定；`:311` 按钮调用 onSubmitOrderClick。对应 VM `:270` 函数体仅 TODO，缺少校验、组参、创建、跳转调用 |
| 地址选择 | VM `:257` 已能发起地址列表路由，回调 `:261` 只 console.log 返回地址，未赋给当前确认数据；此为代码缺口，未作运行复现 |
| 优惠券 | VM 有 selectedCoupon 与 couponModalVisible 及计算；确认页点击调用 showCouponModal，但未见消费该 visible 的弹层；实际选择流程因登录阻断未验证 |
| 请求接口 / 参数 | `core/data/src/main/ets/repository/OrderRepository.ets:74` 与 `core/network/src/main/ets/datasource/order/OrderNetworkDataSourceImpl.ets:71` 已封装 POST order/info/create；`core/model/src/main/ets/request/CreateOrderRequest.ets:7` 包装 data，包含 addressId/goodsList/remark/couponId；未接入提交函数 |
| 支付路由与可观测性 | `core/navigation/src/main/ets/order/OrderNavigator.ets:50` toPay 接 orderId、price、from；`feature/order/src/main/ets/view/OrderPayPage.ets:35` 仅占位文字，ViewModel 为空；未运行到此页。现有页面不直接展示参数，属于本次测试观测不足。Spec 要求按返回订单ID及实付金额跳转支付页，没有要求新增支付参数展示UI；不得将新增支付UI列为必需实现 |
| 购物车存储 | `core/data/src/main/ets/repository/CartRepository.ets:12` 用 CartLocalDataSource；`:57` 删除商品、`:67` 删除规格。确认订单缓存由 `core/datastore/src/main/ets/datasource/ordercache/OrderCacheStoreDataSourceImpl.ets:73` 的 order_cache_store Preferences 保存 carts / selectedGoodsList |
| 清理代码 | OrderConfirmViewModel.ets:278 已有 deleteCartItems，但提交函数没有调用；`:296` 用规格集合数量相等判断全买，未核对集合成员。它未运行，不能认定场景三已通过 |
| 返回购物车刷新风险 | `feature/main/src/main/ets/view/CartPage.ets:35` Monitor currentPageIndex，`:38` 只在索引变为2时调用 loadCartData；下单页返回而 Tab 索引不变时是否刷新需实测，当前只作风险，不认定已复现 |
| 测试可观测性 | 确认页没有为地址、备注、提交按钮提供固定 id；现有 IBestCell/Field 运行生成 id，不能当跨运行稳定业务选择器。登录页、购物车已有多处同名文本；应限定可见组件和父容器 |

提交 TODO、地址回传、优惠券入口和清理接入是提交方案/编码评审的代码缺口。备注已有 `!!` 绑定，输入回写尚未实测；支付参数展示属于测试观测不足，Spec 不要求新增支付UI。这两项不再列入已证业务缺口。上述静态代码事实均不能替代目标页面运行证据。

0-analyze 要求的八项调查映射：① 基线快照见输入/指纹；② 构建状态和告警见构建表及全量目录；③ 页面文件/路由/调用点见代码实证；④ 组件/状态/模型/网络/存储见代码实证；⑤ 可复用缓存、RequestHelper、路由及仓库见代码实证；⑥ 代码缺失能力见提交/地址/券/清理项，备注回写和支付参数观测另记未实测/观测不足；⑦ 登录、后端及数据前置见实际路径与阻断复现；⑧ 稳定 id 和同名文本风险见测试可观测性项。所有运行未到达处均明确保留为未验证。

## 最小阻断复现与下一步

- 关联全部三场景。前置：全新独立模拟器安装本次 HAP，未登录。
- 最小复现 A：主页选商品 → 立即购买 → 选黑色12GB+256GB → 立即购买。目标测试需要已登录后进入确认页；当前未登录，实际跳登录页。B：添加购物车 → 主 Tab 购物车 → 勾选 → 结算，也跳登录页。登录拦截本身符合基线路由配置，本项归类环境/账号前置阻断，不记作本题业务运行失败。
- 强证据：`05-buy-confirm`、`15-cart-checkout` 截图和 UI 树；`app-hilog.log` 两条 order/confirm 登录拦截；本题 RouteInterceptor 与 NavigationService。归因为既有认证前置条件，未发现启动崩溃或构建阻断。
- 需要主 Agent 决策/环境输入：合法测试账号或已授权登录方式，以及可控的有默认地址/无默认地址、可选券、商品和规格测试数据；成功创建订单后的可观察返回与购物车查询。用户凭据未提供前继续保持 blocked，不能通过改登录状态消除阻断。
- 主 Agent 若收到凭据，应沿相同 UI 重跑，补充确认页、地址回传、备注输入、请求体与返回、支付跳转、全/部分规格清理证据；当前 build/UI 证据不可被提升成整题通过。

## 输出及工具生成改动登记

首次采证的手写内容为 baseline-01 报告与 `workflow/verification/capture-baseline.ps1`、`summarize-baseline.py`。本轮仅新增 baseline-02 报告。原始构建、安装、设备、截图/UI树、指纹和警告清单均在 `traces/baseline-01/`。构建工具重新生成各模块 build、.hvigor 等忽略目录；模拟器生成本题 traces 下的实例镜像和日志（体积较大，不应把磁盘镜像当源码提交）。本次未创建业务测试替身、未改项目签名配置。设备维持本题独占实例，交由主 Agent 后续决定保留或停机。



## 复用时需要保留的状态与数据契约

以下为 `CODE_FACT` 与相应验证风险，未作为设备实测结果。

| 位置 | 现状、复用条件与观察要求 |
| --- | --- |
| `core/result/src/main/ets/RequestHelper.ets:41,68,104,107-129` | 接受已创建的 Promise；`.loading(enable=false)` 默认关闭，传 true 才显示；finally 负责该 loading 收尾。它不提供订单响应完整性或重复提交保护。创建请求与页面 GET 的状态须分别观察；不得根据出现 spinner 推断请求只发一次。 |
| `core/model/src/main/ets/entity/Order.ets:13,41,49`；`core/navigation/src/main/ets/order/OrderNavigator.ets:50-57` | 返回订单 id、price 与 realPrice 为不同字段；实付金额对应 realPrice，既有支付路由参数名为 price。正确带参需要单独观测；不要求新增真实支付或支付信息展示 UI。 |
| `entry/src/main/ets/entryability/EntryAbility.ets:94`；`core/database/src/main/ets/entity/CartEntity.ets:7-28` | 既有 ORM 数据库为 app.db，carts 表以 goodsId 为主键，多规格存于 specJson。`core/database/src/main/ets/datasource/cart/CartLocalDataSourceImpl.ets:92-113,128,146` 已有整商品删除、单规格过滤及重读；应区分 UI 内存变化与数据库重读结果。 |
| `feature/order/src/main/ets/viewmodel/OrderConfirmViewModel.ets:84-111` | 商品缓存读取与页面 GET 并行，创建之前就清除传递缓存，但内存保留本次购买快照。地址回流不应重新消费已清空缓存；GET 成功不能单独证明商品准备就绪。清理完成后持久结果与未提交草稿恢复属于不同观察范围。 |
| `feature/order/src/main/ets/view/OrderConfirmPage.ets:247`；本题依赖 `core/ibestui/oh_modules/@ibestservices/ibest-ui-v2/src/main/ets/s/j1/e.d.ets:407` | 备注使用 `value: this.vm.remark!!`，依赖声明含 `$value` 事件。已有绑定语法，输入回写仍需登录后实测；不能仅因未手写 onChange 就列为已证缺口。 |

完整入口/状态/缓存复审见 `workflow/design/analysis-review-01.md`；最终验收目标和证据等级见 `spec/acceptance.md`。可选券交互范围、离页后的导航和清理异常恢复仍按 U 项保留，未在分析阶段自行决定。

## 关键证据入口

- [全量构建原始日志](/D:/HCUP/cml-spec17/traces/baseline-01/full-build.log)
- [完整告警清单](/D:/HCUP/cml-spec17/traces/baseline-01/warnings-full.md)
- [直购进入登录页截图](/D:/HCUP/cml-spec17/traces/baseline-01/05-buy-confirm.png)
- [购物车选中截图](/D:/HCUP/cml-spec17/traces/baseline-01/14-cart-selected.png)
- [结算进入登录页截图](/D:/HCUP/cml-spec17/traces/baseline-01/15-cart-checkout.png)
- [应用运行网络及路由日志](/D:/HCUP/cml-spec17/traces/baseline-01/app-hilog.log)

## 复审修订说明（02）

本轮依据主 Agent 验证复审轮02派工，仅纠正文档事实精度。`baseline-01.md` 原文保留，SHA256 为 `6ab098060220f8ae196fe992986f854cc1d52cfedcc788f6af8bb8c0a23086c3`。以下构建、414块告警、HAP哈希、设备、15组UI证据和登录 blocked 均继承第一次真实采证；本轮未重新构建、未操作设备、未发业务请求、未修改源码、Spec或工作流状态，不能将本轮文档复审称为新增运行验证。

1. 纠正备注绑定判断：`feature/order/src/main/ets/view/OrderConfirmPage.ets:247` 已有 `value: this.vm.remark!!`。本题依赖 `core/ibestui/oh_modules/@ibestservices/ibest-ui-v2/Index.d.ets:39` 导出 IBestField，`src/main/ets/s/j1/e.d.ets:407` 声明 `@Event $value: (value: IBestFieldValueType) => void`。这些声明和调用说明已有绑定，不能仅因未显式 onChange 判定未绑定。结论修为“已有 `!!` 绑定，输入回写未实测”，从已证业务缺口移除；场景一备注输入/提交参数仍被登录前置阻断。
2. 纠正支付范围：支付页占位及未直接展示参数是本次可观测性限制。Spec 的验收行为是使用返回的订单ID和实付金额跳转支付页，不要求新增支付参数展示UI。将其与提交 TODO 等代码缺口分开，不把新增支付UI当成必须实现项。创建请求后的真实路由及参数仍需有账号后验证。

修订影响范围仅上述事实、缺口总结和八项调查索引；原始构建/运行证据及逐步骤状态保持不变。本轮只写 `workflow/verification/baseline-02.md`，下文“本次构建/操作”指第一次采证。

最终合成依据：`workflow/verification/baseline-02.md`、`workflow/design/analysis-review-01.md` 和 `workflow/implementation/analysis-audit-01.md`。修订仅校正文档，不产生新增运行通过证据。


## 无账号本地调查补充（用户追加授权）

本地入口已经可用，有/无默认地址两种场景均实际进入原确认订单页。测试包为 `com.hcup.cmlspec17.localanalysis`，独立于原包、独立数据库；使用本地合成商品/地址/券和测试运行期路由例外，不建立伪账号或token。原订单VM、提交TODO、地址回调及购物车逻辑保持HEAD原样。

- [本地入口使用说明](/D:/HCUP/cml-spec17/workflow/local-entry/README.md)
- [本地测试HAP](/D:/HCUP/cml-spec17/traces/local-entry-01/build-root/entry/build/default/outputs/default/entry-default-unsigned.hap)
- [有默认地址的确认页](/D:/HCUP/cml-spec17/traces/local-entry-01/verification/01-with-ready.png)
- [无默认地址的确认页](/D:/HCUP/cml-spec17/traces/local-entry-01/verification/03-noaddress-ready.png)
- [原购物车实际结算后的确认页](/D:/HCUP/cml-spec17/traces/local-entry-01/verification/49-cart-checkout.png)
- [普通无参数启动仍进入登录页](/D:/HCUP/cml-spec17/traces/local-entry-01/verification/61-normal-login-settled.png)

启动前加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`，安装上述HAP，每轮force-stop后冷启动。测试参数为 `--ps hcupLocalScenario with-address` 或 `no-address`，以及 `--ps hcupLocalEntry confirm` 或 `cart`。`confirm`为直购形状缓存注入；`cart`须从原主Tab实际选择并结算。完整可执行命令见使用说明；不带测试参数的冷启动保留原登录保护。

测试HAP SHA256为 `fc4b8cc4724b40b1f102dc2bdf4e491adab0e3ac753a01e94751e31bfde08736`，9,495,935字节。最终编译exit0；依赖155个junction全部位于本题测试副本内。847项源码及8项模板/工具冻结，原844项tracked、7个受保护业务handler/service、原HAP前后哈希保持不变。实现交接及三轮编译的真实失败/修复日志在 `workflow/implementation/local-entry-01.md` 和 `workflow/local-entry/generated/`，不能将测试构建编译结果替代原始414块告警目录。

| 观察主题 | 实际结果 | 证据与限制 |
| --- | --- | --- |
| 页面和商品 | 原确认页显示甲37×1、乙205×3/407×2，原代码计算合计5600；两场景分别显示地址701/既有空地址态 | 01–04截图、树、hilog和重组JSON；是本地固定数据观察，不是认证后端通过 |
| 缺地址提示 | 点提交后3.156秒连续查找未发现精确Toast；创建计数0、路由未变、车未改 | 05/06；原提交TODO无动作，零请求不等于校验已实现 |
| 地址选择返回 | 原列表能打开并选择907；返回后data.defaultAddress仍701；取消保持701 | 25–31截图/重组JSON；只打印而未写回的缺口已复现 |
| 优惠券 | 点原单元格后visible=true，但无弹层且selectedCoupon仍null | 33/34；不把测试直接赋券当用户交互通过 |
| 原购物车入口 | 选甲37、乙205/407后原结算能到确认页；isFromCart=true，购买项准确，未选项仍在仓库 | 43–50；种子为合成数据，选择/结算调用原代码 |
| 有地址提交与返回 | 原提交仍0次创建、无支付/清理，返回/切Tab后仓库不变 | 35/36、51–56；没有成功订单，未验证成功后清理/持久性 |
| 默认启动保护 | 测试包无测试Want强停冷启动，原购物车结算仍跳登录 | 57–61截图和NavSvc拦截日志；不改变普通认证保护 |
| 备注/新增输入 | 01轮几种输入路径均打开小艺首次隐私协议，未接受；02轮经用户明确授权选择基本模式后完成输入和新增选择返回 | 01轮08/20/23、40/41保留当时blocked；02轮中文/空串/三空格回写及新增闭环见下节，当前无输入协议待决项 |

全部本地原始证据在 `traces/local-entry-01/verification/`；独立报告为 `workflow/verification/local-entry-results-01.md`，检查范围见 `local-entry-preparation-01.md`。当前详细限制及目标映射也见验收矩阵第12节。大诊断JSON以runId/分片重组严格校验，读取真实对象；离开确认页后不把保留getter的旧VM当当前页面证据。可选增强V10/V11未运行。

本地入口解决了无账号查看原确认页的阻断，已完成本阶段现状调查。真实登录、服务端创建订单、支付与成功后购物车清理仍无通过证据；本轮没有补写这些业务。01轮输入阻断由下述02轮授权补测解除，不能把旧报告的blocked误读为当前仍待用户操作。

## 输入补测02：备注回写与新增地址

依据用户“允许，仅在本题测试模拟器中同意”的明确答复，验证角色在本题独占设备 `127.0.0.1:11243` 选择了小艺**“同意基本模式”**，并完成26键布局选择。未选择全量模式，未授予通讯录、相机或麦克风权限。[协议模式选择](/D:/HCUP/cml-spec17/traces/local-entry-02/04-ime-mode-options.png)、[基本模式后的页面](/D:/HCUP/cml-spec17/traces/local-entry-02/05-ime-basic-consent.png)及原始命令均保存；01轮证据未覆盖。

原备注字段 `OrderConfirmPage.ets:247` 的 `value: this.vm.remark!!` 已在本地测试构建得到实际输入回写证据：中文“请轻放，周末送达”、空串和三个空格，UI与当前确认页VM分别逐字一致。中文备注在选择907返回及再次进入列表取消后保持，商品也保持；空格未被trim是基线行为，Spec的空白处理策略仍按U01保留。[输入补测报告](/D:/HCUP/cml-spec17/workflow/verification/local-entry-results-02.md)包含每步UI、VM、路由与日志；[中文读数](/D:/HCUP/cml-spec17/traces/local-entry-02/10-remark-chinese-probe-reassembled.json)、[空串读数](/D:/HCUP/cml-spec17/traces/local-entry-02/13-remark-empty-probe-reassembled.json)、[空格读数](/D:/HCUP/cml-spec17/traces/local-entry-02/16-remark-spaces-probe-reassembled.json)、[往返后读数](/D:/HCUP/cml-spec17/traces/local-entry-02/26-after-cancel-remark-reassembled.json)。这补充了原始普通包记录中“输入回写未实测”的现状；提交TODO未改，因此不能证明备注已进入创建请求。

空地址列表新增闭环也已实际走完：原新增表单填写合成联系人“本地新增丙”、手机号13800000003、省市区“北京市/北京市/东城区”、详情“本地测试丙路1201号”，使用原地区选择器，点击原保存。一次本地POST `user/address/add`分配1201；原列表自动返回并刷新，POST `user/address/page`累计2次，新地址显示后点选返回。[完整表单](/D:/HCUP/cml-spec17/traces/local-entry-02/43-complete-address-form.png)、[刷新列表](/D:/HCUP/cml-spec17/traces/local-entry-02/45-refreshed-address-list.png)及[当前确认页读数](/D:/HCUP/cml-spec17/traces/local-entry-02/48-added-return-confirm-reassembled.json)互相对应。请求由本地fixture响应，无Authorization，不是线上地址保存通过。

原回调日志确实收到1201，但当前确认页 `data.defaultAddress`仍null，UI仍显示“您还没有选择收货地址”；选择已有907时也仍保留701。故新增、刷新和选择返回可用，**确认页未消费地址结果**的缺口在两种样本中复现，定位仍为 `OrderConfirmViewModel.ets:257-263` 只打印而未赋值。新地址已保存不能当作“补地址后能下单”通过；createCount仍0，未伪造订单成功或调用清理helper。最终设备保留在[该确认页](/D:/HCUP/cml-spec17/traces/local-entry-02/49-final-ready-for-user.png)，便于核查。

02轮[完整性检查](/D:/HCUP/cml-spec17/traces/local-entry-02/integrity-final.json)确认原844项、测试847项、冻结工具/模板8项与HAP均未变。测试HAP仍为 `fc4b8cc4724b40b1f102dc2bdf4e491adab0e3ac753a01e94751e31bfde08736`；本轮未重建或重装。7份分块日志严格重组无错误，17项[证据一致性检查](/D:/HCUP/cml-spec17/traces/local-entry-02/assertions-02.json)无不一致；这不是17条业务通过。`27-roundtrip-remark-visible.png`采集失败、为0字节，原样保留但排除有效截图，往返结论使用23/26的当前路由和实际VM证据。

O01–O08必要现状调查现已完成；O09/O10可选增强未运行。31条明文、11条推导、15步覆盖、28项边界及10项策略见 `spec/acceptance.md`。已证缺口为提交TODO、地址回写、券入口及清理接入/集合判断风险；备注已有绑定且回写可用。普通包登录blocked为历史真实前置限制，真实后端创建、响应参数、支付跳转与成功后清理仍未验证，不标记整题功能完成。
