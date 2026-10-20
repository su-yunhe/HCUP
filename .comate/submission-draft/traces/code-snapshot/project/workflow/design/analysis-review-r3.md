# cml-spec1 分析归档运行同步复审 r3

角色：`harmony_design`；会话 `01a15750-6e04-72b1-8b4d-5c2ff6dfc61b`。本轮仅只读复审当前题正式文档、r3报告和本题本轮原始证据，只写本文；没有修改正式文档、生产代码、测试、全局状态或操作设备，没有派生 Agent。

## 1. 最终正式文档与结论

**两份正式文档的运行同步可接受，可按当前分析范围归档。** 已明确基线成功构建、安装、启动和探索真实入口，但实际页面为通知演示，缺少 Spec 四标签；17步为 **2 fail、15 blocked、0 pass**。没有把通知页手势当作 Spec 首页完整用例，也没有把系统任务恢复当作标签返回、把没有图标当作“不重播”通过或把启动成功当作功能通过。

最终复核 SHA256：

| 正式文档 | SHA256 |
| --- | --- |
| `spec/acceptance.md` | `7d7cedd00fb2c8cd5ce5be285da8428477a29ea1228cf63d0f8c9ec371b8497a` |
| `spec/baseline-notes.md` | `4054cb1bf2d19fba66a13889684770a23ed1a21e16720e5fab62f485c8b034f6` |

前轮 r2 对44项、17步原文、八维、边界和网络适用性的结论仍成立。本轮结论只针对最终运行证据同步；不将分析归档扩为功能设计、实现或实现后验收。

另发现一个**派生命令索引的时区格式问题**，协调者已交 verification 修复；原始日志、截图、UI树及两份正式文档的运行结论不受影响，详见第5节。无需更改上述两份正式文档内容或重新操作设备。

## 2. 已独立核对的原始证据

| 核对对象 | 本轮只读复核及结果 |
| --- | --- |
| 安装对象与成功输出 | `logs/analysis-baseline-r3-install-unsigned.json` 绑定本题 `entry-default-unsigned.hap`、设备11245，03:33:10 UTC，exit 0，原文明确 `install bundle successfully`。`launch-first.json` 为03:33:27 UTC、exit 0、`start ability successfully`。不是只凭原生命令退出0推断传输或安装成功 |
| 包与源码绑定 | `traces/baseline-analysis/r3/source-final-comparison.json`：HEAD=`7014cebd60f2181fac2a36d399ca16b3d6a175ab`，677 tracked，changes为空，tracked_diff为空；前后清单哈希相等；HAP=`49a5284455f6b6f9c29873da1431d7542bfd233071b67b46e5f52851d68906a4`，与构建和安装记录一致 |
| 权限拒绝 | 目视 `permission-denied.png`：系统麦克风 sheet仍在，“不允许”有勾选，仍有“确定”。递归读取原始 `permission-denied.json`，“不允许”Flex节点 selected=true。重启后的 `restart-permission.json` 同样是“不允许”selected=true，支持权限保持拒绝；未将该文件名误解为弹窗已经关闭 |
| 最近任务恢复 | 目视 `recent-tasks-after.png`：青商城通知页卡片与系统设置卡片同时存在。原始probe记录点击青商城卡片空白区(654,2000)。`logs/analysis-baseline-r3-restored-app-missions.json` 显示EntryAbility Record33 FOREGROUND、Settings BACKGROUND；不是应用自发崩溃后被替代页面 |
| 无遮挡主窗口与重启窗口 | 目视 `existing-app-window.png` 和 `restarted-app-window-after.png`：标题“主页面”、正文“主页面内容视图”、10个通知演示按钮，无四标签底栏或“领取”。最终mission为EntryAbility Record39 FOREGROUND、Settings BACKGROUND；显式force-stop后的新窗口与原Record33区别得到记录 |
| 通知页横/纵滑结果 | 目视 `content-left-after.png`、`content-up-after.png`，均仍为通知演示页，未出现分类或滚动首页。原始JSONL明确两次swipe的args、exit 0和`No Error`；仅证明命令执行和采样页面状态，不证明 Spec 首页手势已完整执行 |
| 四份权威原始树 | 递归读取 existing-app-window / content-left / content-up / restarted-app-window 的原始 `.json`，只取bundleName=`com.joker.coolmall`窗口：各1个，abilityName=EntryAbility、pagePath=`view/EntryPage`、bounds=`[0,137][1308,2880]`；各有10个Button；四标签和“领取”文字均0，Tabs/TabContent/Swiper/Scroll/List均0。此结果与 `observed-app-summary.json` 一致；类型0不外推成穷尽一切可能实现形式 |
| 采集完整性 | 对manifest内8个选定证据（permission-denied.png、recent-tasks-after.png、existing-app-window.png / -after.png / .json、content-left.json、content-up.json、restarted-app-window-after.png）重算SHA256，全部相符；PNG条目尺寸均1308×2880。没有把一次截图的静态结果当作动画帧证明 |

r3报告 `workflow/verification/baseline-r3.md:42-44` 已说明早期first树/图时差、file recv失败保留、后续“截图→树→截图”的非原子采样。正式基线 `spec/baseline-notes.md:80` 使用恢复后的应用窗口作为权威，未把launcher的 `settled-home` 或早期first混合作为应用首页证据。这一证据选择可接受。

## 3. 17步状态、权限和手势边界

对 `workflow/verification/baseline-r3.md:65-83` 的S项表解析：17行，fail=2、blocked=15，没有pass行；编号及原因与正式文档匹配。

| 范围 | 数量 | 当前合法结论 |
| --- | --- | --- |
| S1.1 / S1.2 | 2 fail | 已恢复实际主入口并在重启后重复观察：四标签不存在，当前内容是通知演示而非默认首页。这是直接运行观察 |
| S1.3–S1.5 | 3 blocked | 没有分类/购物车标签或图标可操作，未伪造坐标点击及颜色/动画结果 |
| S2.1–S2.4 | 4 blocked | 已对当前通知页探索左滑，但正式首页/底栏前置不存在；不能写作首页→分类完整用例已执行，也不能继续虚构分类→购物车 |
| S3.1–S3.4 | 4 blocked | 无首页/我的图标或返回标签；首次播放、首帧静止、重播一次和文字黑色未验证。最近任务恢复不是Spec标签返回 |
| S4.1–S4.4 | 4 blocked | 无可滚动首页和顶部“领取”，通知页纵滑未滚动不等于已建立场景四前置；没有“不切页/不额外重播”的通过结论 |

正式验收 `spec/acceptance.md:29-36`、`:316` 和正式基线 `spec/baseline-notes.md:16`、`:86-94`、`:158` 均保留上述区分。A38只得到应用force-stop/start的探索事实，未声称默认首页或自动播放通过；派生边界仍not_run/blocked，A40–A44仍为未确认假设。

权限流程叙述也准确：首次拒绝后出现系统sheet，确认或关闭走Settings.AppDetail，Back可到launcher，再启动再请求；通过系统最近任务正常恢复尚存窗口，麦克风没有点允许。重启后再现拒绝sheet并重复恢复。正式基线 `:76-80`、`:88`、`:166` 与原始截图/树/mission相符，没有混写为授权成功、绕过权限校验、应用自发崩溃或“从我的标签返回首页”。

## 4. 正式文档残留状态修正与范围确认

| 复核点 | 结论 |
| --- | --- |
| 旧“待运行角色验证” | 已指出并由协调者修正。`spec/acceptance.md:72` 现明确源码链由r3实际入口/权限流程交叉验证，同时不暗示四独立占位目标页都已访问；本角色重新读取确认 |
| “功能验收尚未实施”歧义 | 已指出并由协调者修正。`spec/baseline-notes.md:16` 现为本轮基线17步2fail/15blocked/0pass，未开展实现后验收；与第3节一致 |
| tracked/ignored边界 | `spec/baseline-notes.md:13` 仍限定677 tracked及指定源码目录检查；明确ignored安装依赖/本地配置没有完整前后指纹，不扩成全构建环境未变。r3指纹只支持其记录范围，没有边界回退 |
| ID建议地位 | `spec/baseline-notes.md:171` 保留本地自动化可观测性建议、非Spec指定名称/独立业务项；没有因runtime树内系统生成id而声称已有业务选择器 |
| 零功能pass | 验收 `:11/:29-36/:316`、基线 `:16/:94/:180` 与r3结论相符。构建/安装/启动的成功是执行事实，未扩大为功能项pass或官方成绩 |
| 动画/网络限制 | 无Lottie动态图标证据，首帧/颜色/次数/不重播仍blocked；未实测后台可达性或领券交易。两正式文档没有新增硬性网络义务或用无图标证明静止 |

两正式文档无需进一步实质修正；原有“构建通过、unsigned”记录与r3实际接受unsigned包并不冲突，文档也未将未签名继续描述为安装障碍。

## 5. 派生索引时区问题与交接

**R3-I1（仅证据索引格式，原始证据未错）**：初读 `traces/baseline-analysis/r3/command-index.csv` 的列名为 `utc`，但混合了无偏移的03:xx与11:xx时间。例如：

- install-unsigned行是 `2026/10/20 3:33:10`；原始安装JSON为03:33:10Z。
- existing-app-window-click行是 `2026/10/20 11:42:26`，但原始 `logs/analysis-baseline-r3-probe-commands.jsonl` 明确为 `2026-10-20T03:42:26.864745+00:00`；content-left-swipe同样将03:42:52+00写成11:42:52无偏移。

这会误导只看CSV列名的时间顺序/间隔判断。原始JSONL保留UTC偏移，`device_probe.py:18` 使用UTC时间；两正式文档的北京时间和流程顺序正确，不影响2fail/15blocked及权限/入口结论。

已向协调者交回最小调整：**不修改原始日志**，保留旧派生CSV，按raw offset将新索引统一为ISO8601 UTC，更新派生manifest和r3注记。协调者已明确派 verification 修复，设备保持冻结；本复审交付时该回包尚待协调者最终检查。此修复不需要修改两份正式文档或本题代码，不要求重跑安装/手势。

本角色的工作已完成：运行同步可接受，正式文档最终哈希如第1节。剩余仅为协调者接收上述派生索引规范化回包并完成分析归档，不进入功能实现。
