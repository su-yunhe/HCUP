# cml-spec1 功能实现交接 r1

- 编码角色：`/root/implementation_do`；本子会话环境实读候选 `CODEX_THREAD_ID=01a1579e-dd21-7b11-a80b-23fc553e29e4`。没有使用继承的 `CODEX_SESSION_ID` 冒充身份，待主 Agent 核对原生日志。
- 范围：仅本题生产源码、实际 ohpm 锁文件及本交接/logs/traces。未访问其他题、题包、来源应用同功能代码/历史/Issue/PR/补丁/副本或初始化总览会话；未操作设备，未改测试、需求、设计、全局调度状态、通用权限组件；未提交或推送。
- 首次写生产代码前已读 `workflow/setup-result.json` 和 `logs/prepare-baseline.log`，官方准备 pass，无变更、HEAD=`7014cebd60f2181fac2a36d399ca16b3d6a175ab`，没有重初始化。
- 批准输入实算一致：Spec `491ea9b5efe284f449873234ba0c86345a0cc2eece2e097898de06a2c4f59d4b`；acceptance `7d7cedd00fb2c8cd5ce5be285da8428477a29ea1228cf63d0f8c9ec371b8497a`；需求复核 `14cb73d680630c50190a066fb0c1de4090f2e328e55ef1ed2b1404cc9d06b332`；方案 `c65d814c0e25a9df868ac125d3cc3619fc10517e34c5e6e6caaf6b80b5ffae25`。

## 实现与文件

共 22 个生产文件（11 个 tracked 修改、11 个新增），逐文件 SHA256 见 `traces/do-implementation/source-frozen-r1.json`。

| 文件 | 行为 |
| --- | --- |
| `feature/main/src/main/ets/view/MainPage.ets` | 保留 MainPage/AppNavDestination 入口，隐藏标题，四个固定 embedded 子页、非循环横向 Swiper、固定底栏；点击只请求 changeIndex，onChange 唯一提交；页间忙时合并最后点击。已选首页仅调用同一个 Scroller 回顶。 |
| `feature/main/src/main/ets/viewmodel/MainViewModel.ets` | @ObservedV2/@Trace 初始首页 index=0、epoch=1；commitSelection 去重/边界检查。 |
| `feature/main/src/main/ets/view/HomePage.ets` | 保留独立路由默认包装，embedded 为普通内容；真实 Scroll、顶部逐字“领取”、限时精选/推荐商品、足量自然本地商品内容；持久传入 Scroller 保留滚动。 |
| `feature/main/src/main/ets/viewmodel/HomeViewModel.ets` | 明确类型 HomeProduct，稳定 id，八条本地生活用品展示数据，无网络或交易成功宣称。 |
| `feature/main/src/main/ets/view/CategoryPage.ets`、`CartPage.ets`、`MePage.ets` | embedded + 独立路由模式；本地分类、现有 EmptyCart、未登录个人内容；空数据/无账号不门控导航。 |
| `feature/main/src/main/ets/component/TabLottieIcon.ets` | 真正 @ohos/lottie Canvas AnimationItem；rawfile 字节读取/UTF-8 解码/animationData 加载；DOMLoaded 才 reconcile，generation 防过期回调，epoch 消费去重，有限播放，选中黑色、离开灰色首帧暂停；独立 name 销毁和移除监听。 |
| `feature/main/src/main/resources/rawfile/lottie/tab_home.json`、`tab_category.json`、`tab_cart.json`、`tab_me.json` | 自制标准 shape Lottie，清楚的房屋/网格/购物车/人物图形；48 帧/30fps，可见缩放、轻转、弹起关键帧；不含外部图像/表达式。 |
| `feature/main/src/main/resources/rawfile/products/{bag,kettle,lamp,mug,speaker,vase}.svg` | 六张自制本地商品插画，配合自然内容而非空白高度/测试占位滚动。 |
| `feature/main/oh-package.json5`、`feature/main/oh-package-lock.json5`、`entry/oh-package-lock.json5` | 精确 @ohos/lottie 2.0.33，官方 registry；锁文件由 ohpm 实际生成，没有手改依赖代码。 |
| `entry/src/main/ets/entryability/EntryAbility.ets` | 仅移除启动时无关麦克风请求及未用 import；ORM、路由、ContextUtil、IBest 初始化保留。 |

A1–A44 均有对应实现；这是实现落点声明，功能是否通过由独立自测判定：

| 验收项 | 实现落点 |
| --- | --- |
| A1–A3 | 原入口、固定四标签、初始首页/上方内容。 |
| A4–A15 | 点击/左右滑动四页对应内容，onChange 同步唯一选中，Lottie 黑色选中/灰色复位。 |
| A16–A22 | 首页初始 epoch 1 加载后播放；真实离开首帧暂停；真实返回新 epoch 播放一次及黑色文字。 |
| A23–A28 | 真实本地首页滚动使领取离开视口；已选首页仅回顶，选中/epoch 不变，不新增切页或 play 请求。 |
| A29–A30 | 固定首页、分类、购物车、我的顺序；相邻正反向滑动同一提交入口。 |
| A31–A35 | 顶部/连续首页重击、请求合并、单 epoch 去重；垂直 Scroll 与横向 Swiper；手势取消无不同 onChange 就不提交。 |
| A36–A37 | 空购物车/未登录可导航；四页内容及动画均本地，无本题内容请求，pending/失败注入不适用，不声称网络请求验证通过。 |
| A38–A39 | 新 MainPage 实例初始化首页；离开当前首页统一复位，播放未完成也停止。 |
| A40–A44（获准实现约定） | 端点不循环；非首页同击无操作；暖恢复无初始化重置；四图标有限播放且离开灰色首帧；跨标签返回首页不调用回顶并保留同一 Scroller。 |

## 可观察契约

稳定 ID 全部沿用方案第 5 节。非可见 accessibilityDescription：

- `main_root` / `main_content_pager`：JSON `{"selectedIndex":0,"selectionEpoch":1,"instanceId":"main-..."}`。
- tab 父区域：JSON `{"selected":true}`；accessibilityText 含真实标签及“已选中”语义。
- 四个 icon Canvas：JSON `{"ready":true,"frame":0,"paused":true,"consumedEpoch":1,"observedPlaySeq":1,"completeSeq":0,"instanceId":"main-...-home","error":""}`。frame/paused 直接取 AnimationItem；observedPlaySeq 只在本次选中 epoch 的引擎帧实际前进后增长；completeSeq 只来自真实 complete。无可见调试 UI，不把 goToAndPlay 调用等同播放成功。
- `home_scroll`：JSON `{"yOffset":0}`，值由真实 Scroller.currentOffset 在 onDidScroll 读取。
- 结构化 console 标签 `MainTabsLottie` 保留 DOMLoaded、playRequested、observedPlay、complete、reset、error 事件及同一 JSON，供屏幕多帧与动作时间交叉核对。

## 技能、构建与检查

读取并应用：
- `C:/Users/22580/.codex/skills/arkts-syntax-assistant/SKILL.md`：遵循 V2/明确类型/无 any 或抑制；按其实际 `scripts/run.ps1` 完成安装+编译。
- `C:/Users/22580/.codex/skills/hmos-arkts-knowledge-retriever/SKILL.md`：首次 search_docs.py 因包内缺 `references/doc_index.json` 失败，未修技能包；改用 rg 直读包内 linter 摘要和官方 API `docs/ArkTS-API-Reference/js-apis-util.md` TextDecoder.create/decodeToString；Lottie 签名以安装包 index.d.ts/README 为准，Swiper 签名以本机 API23 官方 SDK swiper.d.ts 为准。
- `C:/Users/22580/.codex/skills/hmos-arkts-syntax-checker/SKILL.md`：使用真实 hvigor 编译诊断代替不存在的 MCP/linter；P0=0，完成明确 debug HAP 构建。没有放宽编译规则或 SDK 声明。

每个构建 PowerShell 进程先加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。保留以下原始记录：

| 检查 | 结果 / 日志 |
| --- | --- |
| 官方依赖安装 | exit 0；`logs/do-ohpm-install-r1.log`；2.0.33 HAR integrity 与锁文件一致。 |
| 首轮技能脚本（ohpm install --all + hvigorw assembleApp，含 entry assembleHap） | 12:48:53–12:50:02，exit 0，BUILD SUCCESSFUL；`logs/do-build-r1.log` / `do-build-r1-result.json`。 |
| 明确 debug HAP：`hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon` | 12:50:35–12:51:02，exit 0，BUILD SUCCESSFUL；`logs/do-build-r2-debug.log` / `do-build-r2-result.json`。 |
| 编译告警基线对比 | 两次均 182 条带文件诊断，与分析基线多重集新增/删除均为空；`traces/do-implementation/local-check-r1.json`、`debug-warning-compare-r1.json`。原有资源重名/dayjs/sourceMapsPath/未签名配置告警仍保留。 |
| 本地资源结构/打包 | 四 JSON 48 帧/30fps、有 shape、无外部 assets；HAP 内四 JSON+六 SVG 均存在。仅静态/打包检查，不代替播放验收。 |
| git diff --check / 构建噪声 | 无 diff 错误；仅原仓库 autocrlf 提示，`logs/do-diff-check-r1.log`。核对 tracked diff 没有 BuildProfile.ets 噪声，无需还原任何生产文件。 |

没有编译失败或修复重试。首个整块写入 apply_patch 因重复 delete/add 同路径校验拒绝，未改变文件；随后正常写入授权文件。没有删除测试或降低断言。

## 冻结与未决验证

**生产代码已冻结；独立验证期间不编辑生产源码。**

- 指纹：688 文件（677 tracked + 11 新增生产文件），`traces/do-implementation/source-frozen-r1.json`，聚合 SHA256=`23536b99f2e971b386cdf4583e614217015c01966f6436e54c52e271decdebc6`。算法为排序后的 path→SHA256 JSON（UTF-8 / ensure_ascii=False / separators comma-colon）再 SHA256。
- 最终局部 debug HAP：`entry/build/default/outputs/default/entry-default-unsigned.hap`，20,739,858 bytes，SHA256=`e647a66dcd2718dca7f5333dfade8255ab9eb8f98c69e737f0b8be86b44442c6`。
- 未发现需修改批准需求或核心方案的情况。设备从未被本角色占用；不能据构建声称动态通过。
- 独立设备验证重点：Swiper 快速点击/横滑混用实际事件顺序；取消及端点；Lottie 首帧、颜色、真实多帧/一次完成和无新增播放；首页真实滚动/跨标签保留/同页回顶；后台恢复与冷启动；首次无麦克风弹窗。最终结论由主 Agent 结合独立自测得出。
