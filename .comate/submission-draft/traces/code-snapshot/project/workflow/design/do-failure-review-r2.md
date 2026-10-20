# cml-spec1 切页回零失败诊断 r2

结论：先做 **一行索引绑定修复**，无需改动状态机、页面结构或Lottie。由唯一编码者将 `feature/main/src/main/ets/view/MainPage.ets:84` 的 `.index(0)` 改为 `.index(this.vm.selectedIndex)`；仍只允许 `Swiper.onChange → vm.commitSelection` 提交索引/epoch，保留同索引去重。不要采用直接写VM的双向绑定绕开epoch，也不要在点击或animationEnd再增一次epoch。

## 实证

- 独立原生最小复现：`traces/verification-do-r1/repro-tab-reset-r1/commands.json`。force-stop/start，等待2秒，仅一次分类中心 `uitest uiInput click 490 2671`，无其他导航输入，0.5秒后采集。
- `before-summary.json`：root/pager为index=0、epoch=1；`after-summary.json`：同一 `instanceId=main-1792472377459`，root/pager为index=0、epoch=3，分类selected=false。
- 从原始before/after JSON读取图标实际快照：分类consumedEpoch由0变2，返回后的首页consumedEpoch=3、observedPlaySeq由1变2，frame=22.8且paused=false。说明分类选择确曾被消费，随后出现一次没有用户输入的首页返回；不是分类点击未命中，也不是新MainPage实例默认初始化。
- `source-before.json` 与 `source-after.json` 的688个文件映射相同；当前复现没有源码并发变更。首轮业务测试的failure.png也实际显示首页内容和首页选中，与节点状态一致。

## 原因与归类

当前Swiper在 `MainPage.ets:84` 声明 `.index(0)`；同一属性构建路径在`:91`使用依赖VM的diagnostic描述，`:92–95` onChange又更新 `@Trace selectedIndex/selectionEpoch`。controller先请求分类，onChange把VM从0/1提交成1/2，随之的属性更新仍向Swiper提供声明式index=0，足以解释原生页回0及第二次onChange提交成0/3。`.index`表示当前页索引，不能把常量0当成只执行一次的初始化参数。

这是**实现层声明式索引配置缺陷**；onChange唯一提交架构仍可用。r1方案未把“Swiper声明式index必须跟随已提交索引”写成明确约束，前次静态审查也未识别该风险，本r2补足这一点。运行证据已推翻前次“未发现明确偏离”结论在此处的适用性，不将其归因于测试或降低A4/A10等需求。

## 最小验证与回退路径

编码修复并构建后，独立verification每次先安装本题刚构建HAP，再复跑上述原生单击及首页左滑：分类应保持index=1、epoch=2，首页首帧停、分类真实播放，不自动回首页。再测购物车/我的/真实回首页、同首页回顶、连续快速输入，确认每次实际不同选择只增一个epoch，同标签点击不增。

若一行修复后仍有回零或重复通知，再采request/index/onChange/animationStart/End时序，最小处理controller与队列的原生回调顺序；当前没有证据需要先重构队列、网络、缓存、资源或Lottie。首次修复不要扩范围，以便验证此因果假设。

本角色只读本题源码、既有复现记录和failure.png，只新增本文；未修改生产代码/测试/state，未构建或操作设备，未访问应用上游/其他题/题包/总览会话。源码归因是与实证高度一致的可验证解释，修复成功仍须以上述新运行结果确认。
