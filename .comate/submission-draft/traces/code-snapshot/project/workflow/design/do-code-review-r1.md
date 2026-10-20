# cml-spec1 聚焦方案符合性审查 r1

## 结论与证据边界

本轮只读审查当前工作树已落盘实现，对照批准的 `workflow/design/do-design-r1.md` 和 A1–A44。**未发现可凭当前源码确认的需求偏离或必须先回退方案的缺陷，可继续构建与独立动态验证。** 此结论不是构建通过、运行通过或功能验收通过；快速事件、缓存保留及图标真实渲染仍需设备证据。

未构建、安装、操作设备或改动生产/测试/依赖/state；仅新增本文。没有检查其他题、题包、来源应用上游或初始化总览会话。图标首次查看时正在写入，之后一次查看取得完整文件，未把暂时不存在误判为实现遗漏。

审查快照指纹（SHA256，小写）：

| 文件 | SHA256 |
| --- | --- |
| `feature/main/src/main/ets/view/MainPage.ets` | `1984ec6d83162ffca09e2e6640c17e65b1de5189986fed588a7e650042f2336b` |
| `feature/main/src/main/ets/viewmodel/MainViewModel.ets` | `f81e133e62ec8d9605d9e32dbd3eaa7f8b1b9d74940d67e9fd9b61a21cbba9ed` |
| `feature/main/src/main/ets/view/HomePage.ets` | `55c45cde1b56f17a938dc0ac00fc891b57f9b83af3af459fc9e74389c9b4f8f8` |
| `feature/main/src/main/ets/view/CategoryPage.ets` | `5bf579bf39d5580cbd180886668b34e14f9b77b83cd35b5e3198ef03bb9e58de` |
| `feature/main/src/main/ets/view/CartPage.ets` | `4a5777226744657de49f2513284996c415a8f9674e3174011d988e22d4396628` |
| `feature/main/src/main/ets/view/MePage.ets` | `dc3ce64baec979bcb21cd215c8cacbbbac42764a6f7add5ce7dce310d5f53308` |
| `feature/main/src/main/ets/component/TabLottieIcon.ets` | `30c0d7be175d0ad5dd407f7ae9a7342b3e52531ded44f593e4d9b4c49a0a743a` |

MainPage 与图标文件在审查末次读取时指纹仍相同。后续编码变化超出此快照，需要按变更内容复审，不能据此自动覆盖新版本。

## 聚焦核对结果

| 核对点 | 源码证据与结论 | 影响项 |
| --- | --- | --- |
| 单一状态提交 | `MainViewModel.ets:5–16` 使用 V2 Trace 索引/epoch，初始0/1；越界与同索引返回false。`MainPage.ets:92–95` 是本次所读代码中唯一 commitSelection 调用；点击、animationEnd 没有再次提交或直接播放。符合方案。 | A2/A16/A20/A28/A29/A33 |
| 点击与快速输入 | `MainPage.ets:27–50`：忙/请求中只覆盖pendingTab；空闲不同标签仅changeIndex(false)；onChange释放requestInFlight；animationEnd清busy并drain。没有创建多份队列或双增epoch。原生回调顺序及同步drain是否稳定仍需动态验证，当前不能凭猜测认定失败。 | A33/A35/A40/A41 |
| 同首页仅回顶 | `MainPage.ets:32–37` 仅在index等于已提交索引且为0时scrollTo(y=0)，随后返回；不调用controller/commit，不改epoch。非首页同击直接返回。回顶使用纵向260ms动画，与禁止切页动画相容。 | A24–A28/A31/A32/A41 |
| 缓存及Scroller所有权 | `MainPage.ets:15` 持久实例字段homeScroller，`:76` 传给HomePage；四个子页固定构建，`:88` cache3。`HomePage.ets:8,28` 使用同一传入Scroller；`:93` 只读取偏移，无onShown重置。真实返回首页没有回顶调用。静态符合保留方案，运行时布局/缓存是否保留需实测。 | A23/A34/A42/A44 |
| embedded与原路由 | 四页 `@Param embedded=false`；Home:98、Category:27、Cart:22、Me:33：true仅普通内容，false保留AppNavDestination与各自VM。Main外层仍用AppNavDestination。没有以push四个路由替代tab，也没有把NavDestination嵌在Swiper内。 | A1–A4/A8/A10/A13/A14/A21 |
| 首页真实滚动前置 | `HomePage.ets` 顶部唯一 `home_coupon_receive` 逐字“领取”，下方两区标题及八个有名称/描述/价格/本地SVG的商品卡；Scroll内自然内容，不用隐藏锚点/空白高度。内容足够的最终判定应量目标视口与领取边界。 | A23–A25/A36 |
| 初始及未就绪播放 | `TabLottieIcon.ets:35–37,98–105,107–157`：Canvas.onReady触发资源读取；generation拒绝旧结果；autoplay=false；DOMLoaded和isLoaded补偿均走onLoaded防重；reconcile使用此刻selected/epoch，未ready时不提前消费。已离开后才加载完成走灰色首帧，不补播过期选择。 | A16/A19/A39 |
| 选择/重击去重 | `TabLottieIcon.ets:72–95`：选中且consumedEpoch不同才黑色goToAndPlay(0,true)；同epoch重复通知不播放；loop=false。Main同击不增epoch，因此图标旧播放可继续而不新增播放。 | A5/A9/A12/A15/A18/A20/A28/A43 |
| 离开统一首帧 | 图标`:81–84`：未选中changeColor灰色+goToAndStop(0,true)，并在控制后取真实快照；所有四图标策略相同。检查本地实际依赖JS，changeColor会请求重新渲染，goToAndStop会goToFrame后pause。 | A6/A7/A19/A39/A43 |
| 真实动画及观察 | manifest精确2.0.33；四个rawfile JSON均fr=30、ip=0、op=48、64×64、1个shape层、无外部assets。TabLottieIcon真用lottie.loadAnimation+Canvas，JSON包含真实关键帧；没有用外层原生位移动画替代。`:61–70,129–155` observedPlaySeq从引擎frame>0且当前epoch一致时增加，重复enterFrame/drawnFrame同epoch不双计，complete去重。此状态仍须与屏幕ROI联合验证，不能单独作为渲染成功。 | 全部动画项、A43 |
| 监听及销毁 | 图标`:166–175` generation失效，调用每次addEventListener返回的移除函数，清数组，按name destroy并item=null/ready=false。只读核对本题安装的2.0.33 BaseEvent实现，确实返回绑定的移除闭包，不是误将void入数组；未调用无参destroy误伤其他图标。 | A39/A42/A43 |
| 麦克风干扰 | EntryAbility diff只移除PermissionUtils import及loadContent回调中的requestAudioPermission，保留ORM/路由/ContextUtil/IBest初始化。符合最小方案，未绕开主入口或扩改权限通用模块。 | A1/A16/A38 |

## 必须交独立验证的运行观察

以下是尚未取得动态证据的验证点，**不是本轮已确认缺陷**，无理由现在要求编码按猜测重构：

1. 快速点击与有效/取消横拖混用：记录request→onAnimationStart→onChange→onAnimationEnd→drain时序，确认pending最后目标落定且后续点击仍可操作，重复同索引通知不增epoch。若原生不接受onChange回调内立即changeIndex，最小修复是延后drain/finishAnimation，仍保留onChange唯一提交；不能新增第二份选择源。
2. 首页下滚→任意其他标签→首页：对比真实yOffset/同一卡片屏幕位置，随后同首页点击才归零；暖恢复同样核对选择、偏移与播放序列。若固定缓存仍回收，按方案只对Home做真实offset备份/布局后恢复。
3. 离开时图标frame=0且连续ROI稳定；返回时新增一次播放且有限结束；同首页重击在旧播放结束/未结束两种前置下均不增加序列。灰色第一帧参照与黑色终态分开采样。
4. 只有DOMLoaded/帧事件、没有ROI变化不能判通过。确认四图标可见尺寸、黑灰图形像素与真实关键帧变化，错误字段为空。
5. 实际暖前后台时记录图标组件是否被销毁/Canvas重建。当前aboutToDisappear销毁引擎但保留consumedEpoch；正常组件删除会有新实例，正常暖恢复应保留原实例。若目标运行时出现“同一组件未删除却重新onReady创建引擎”，需收集生命周期证据再局部处理重建后的颜色/静态帧恢复，不能为了规避猜测而让暖恢复额外重播。
6. 首次启动、完整终止后启动与普通暖恢复分开测；领取必须真正滚出/重入视口，预构建节点存在不等于当前可见。

## 来源及交接

来源只限本题上表源码、批准方案、批准需求和本题已安装的通用 `@ohos/lottie@2.0.33` 的 `index.d.ts`、`AnimationItem.js`（changeColor/goToAndStop/goToAndPlay）与 `utils/BaseEvent.js`（监听移除闭包），未修改依赖，也未增加外部应用来源。

本轮建议：继续由唯一编码角色完成构建/API局部适配，由独立verification提供T01–T08和ROI证据。若上述任一运行点真实失败，先用其事件/布局证据判断实现偏离或原生时序适配，不把未运行结果记成功，也不降低A项。
