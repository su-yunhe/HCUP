# cml-spec1 独立自测交付（run-r4）

2026-10-20，`127.0.0.1:11245` 专用模拟器实测结束。公共 runner 实际发现并完成 **8/8 用例，pass 8、fail 0、error 0、skip 0**；A1–A44 全部 pass。A1–A28 为明文，A29–A39 为派生边界，A40–A44 为主 Agent 批准的实现策略，不是官方隐藏测试或评分声明。当前没有未完成的本题业务验收项。

逐项结论及原始断言路径：[Markdown 矩阵](do-matrix-r4.md)、[机器矩阵](../../traces/verification-do-r1/run-r4/a-matrix.json)、[完整断言汇总](../../traces/verification-do-r1/run-r4/verification-summary.json)。原始 runner 报告：[selftest-run-r4.json](../../logs/selftest-run-r4.json)。

## 运行与来源绑定

只操作本题目录、只读公共 harness；自测未修改生产、Spec 或 workflow/state.json，未创建子 Agent。设备操作均经主 Agent 冻结授权。环境为 Python 3.12.3 / Hypium 6.1.0.210、Node 18.20.1、JBR 21.0.8、hdc 3.2.0c、DevEco 6.1.0.860 / SDK API23；模拟器系统 6.1.0.115，截图原始尺寸 1308×2880。公共 runner 的 env_warnings 为空。每个 PowerShell 工具进程先加载环境脚本及本题 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1` 覆盖配置。

| 绑定对象 | 最终值/记录 |
| --- | --- |
| 批准 Spec SHA256 | `491ea9b5efe284f449873234ba0c86345a0cc2eece2e097898de06a2c4f59d4b` |
| 批准 acceptance SHA256 | `7d7cedd00fb2c8cd5ce5be285da8428477a29ea1228cf63d0f8c9ec371b8497a` |
| 基线 HEAD | `7014cebd60f2181fac2a36d399ca16b3d6a175ab` |
| 最终生产输入 | 688 文件；聚合 `2cebe8ebb0c7fcc3d15058f9dedb0843580aacf5b1f41593f3dbe4200cf9d14c` |
| 最终 HAP | `entry/build/default/outputs/default/entry-default-unsigned.hap`，20739960 bytes |
| HAP SHA256 | `d54386d3d42a6049d5af9fcece16c9d0cdbd271a2217cb008c196af177202615` |
| test_main_tabs.py SHA256 | `4c7ce788e606dccccf2e42edb6084d177b8edb77f93236ec4919e214ce0204bb` |
| evidence.py SHA256 | `8c716e041bd5175bd991fc24f9ccd38adc725f793a36f55a8bdad09d6b4fc006` |
| 测试版本原文 | [script-versions/run-r4](../../traces/verification-do-r1/script-versions/run-r4/)；旧轮原文及可复原 diff 同目录保留 |
| 最终只读核验 | [final-audit.json](../../traces/verification-do-r1/run-r4/final-audit.json)：688 文件零变化，HAP/两测试 SHA 与 run-context 一致，git diff --check exit0，BuildProfile diff 为空 |

每个 case 均保存 source-before/after/difference，8 个 source-difference 全为空；本轮安装/runner 前后及最后再次核对冻结 manifest。生产冻结期间未并行编辑。设备与来源门禁放在本次执行辅助；业务测试继承 `harness.driver.HarnessTestCase`，从公共 runner 注入设备参数，无隐藏冻结环境开关或固定设备依赖。

## 命令、退出码与告警

| 操作 | 退出码 | 精确 argv、时间及原始输出 |
| --- | --- | --- |
| 独立首次 clean + assembleHap（r1 冻结） | 0 / 0 | [build-r1-commands](../../logs/verification-do-build-run-r1-commands.json)，同名前缀 clean/assembleHap.log |
| 唯一生产修复后独立 assembleHap（r2 冻结，增量任务多为 UP-TO-DATE） | 0 | [build-r2-commands](../../logs/verification-do-build-run-r2-commands.json)、[assembleHap 原文](../../logs/verification-do-build-run-r2-assembleHap.log) |
| run-r4 前重装上述同一 HAP、bm dump | 0 / 0 | [run-r4-commands](../../logs/verification-do-run-run-r4-commands.json)，安装明确返回成功；保存 bundle 更新时间 |
| 公共 runner，13:25:37–13:48:05 | 0，实际 8/8 pass | 同一 commands.json 的 runner 项；[原始输出](../../logs/verification-do-run-run-r4-runner.log) |
| 最终 faultlogger、git diff --check、BuildProfile diff、status | 均 0 | final-audit.json 中 argv/时间/退出码及对应 final-*.log |

普通复用命令（先激活公共 Python 环境及只读 harness 的 PYTHONPATH，从本题 logs 执行）：

```powershell
python -m harness.runner --project D:\HCUP\cml-spec1 --device 127.0.0.1:11245 --json D:\HCUP\cml-spec1\logs\selftest-run-r4.json
```

独立首次完整构建的文件诊断与基线均为 182 条，多重集合新增/删除均 0，其他 WARN 行也无增删：[告警比较](../../traces/verification-do-r1/independent-warning-compare-r1.json)。一行索引修复后的增量构建成功，保留其实际缓存任务输出；不把缓存日志冒称为重新输出 182 条诊断。未发现新告警；最终没有 BuildProfile 生成噪声待还原。无签名配置等既有告警保留。

## 实测证据

- 先完整执行四明文场景，随后复用相同动作/源码绑定证据覆盖派生项。case01–04、case05 双向/端点/非首页同击、case06 顶部及滚动中连击/部分横拖/快速交错、case07 空购物车/未登录/暖恢复、case08 冷启动/播放中切走均完成。
- 50 组采帧，每组 48 个真实成功样本，共 2400 张原始 JPEG；保留真实设备和主机时间、全部 capture-raw.log、UI 树、静态 PNG、ROI 样本和分析 JSON。动画断言同时要求实际引擎 frame/暂停/完成与至少 3 个真实形态，不用播放计数或单张截图替代动态证据。离开首帧/静止、黑灰像素、有限完成、同击无新增播放均有独立断言。
- 本轮场景三返首页的 frame1 有两次 screenshot 命令 exit255，按批准上限只重试该采集位置，第三次成功；两条 FRAME_FAIL 原文及真实时间完整保留。未重放用户动作或启动，未补造帧，最终该组48张真实帧及全部断言通过。[原始采集日志](../../traces/verification-do-r1/run-r4/test_03_scene_three_initial_reset_return/03_me_return_home/capture-raw.log)。
- 场景四初始领取锚点 `home_coupon_receive`/`领取` 的原生 accessibilityId=`58`，实例 `main-1792474186459`。真实 yOffset=402.2118 后入口离屏；跨标签返回保留滚动；点击已选首页后同一锚点回到可视区。已人工查看[离屏截图](../../traces/verification-do-r1/run-r4/test_04_scene_four_scroll_and_reselect/offscreen-coupon-1.png)与[回顶截图](../../traces/verification-do-r1/run-r4/test_04_scene_four_scroll_and_reselect/03_selected_home_scroll_to_top_settled.png)，与树/滚动/实例断言一致。SDK 会从树省略全裁剪节点，因此“缺节点=离屏”仅在原锚点已验证、真实正偏移、同一首页实例及截图支持下使用；回顶仍强检唯一ID、文案、同原生节点与可视交集。
- 冷启动夹具等待旧 bundle PID 连续三次为空并停稳，再且仅再发送一次正常 start；每次 cold-stop 原始状态保留。没有失败后补 start 或重放启动掩盖首次结果。

## 保留失败及限制

最初 r1 的单次原生分类点击曾 H→C→H：固定 `.index(0)` 在重渲染时重置，A4 fail；[最小复现报告](do-failure-r1.md)。主 Agent 仅批准编码改为 `.index(vm.selectedIndex)`；r2 原生单击/左滑均确认修复，再重新安装跑完整套件。本次自测未改生产。

旧轮失败没有删除或倒写：r1 时钟采样权限故障；r2 离屏节点解析缺口；r3 过短 stop/start 夹具下发生真实 `LIFECYCLE_TIMEOUT`，以及一次截图 exit255。全部原始日志、失败/中断记录及脚本版本保留。r3 [sysfreeze 原文](../../logs/verification-do-run-r3-sysfreeze.log)显示 13:19:16 的前台生命周期超时，线程阻塞于 Window/RenderService Binder；这只能支持**中等强度的系统生命周期/夹具交互归因**，根因未完全排除，不宣称生产源码已修复该超时。改进停止夹具后 run-r4 八组均成功；结束后 faultlogger 中本 bundle 仍只有该历史文件，**本轮未新增/未复现同类记录**。这属于历史稳定性限制，当前验收无阻断。

空输入、纯空格：N/A，Spec 无输入/提交控件。请求失败注入：N/A，本题批准实现的导航/内容无相关请求；A37 只表示本地导航完成路径通过，不声称故障注入通过。远端空分类：N/A，固定本地数据；实际空购物车和未登录页已测。覆盖子路由返回：N/A，无批准可达覆盖路由；实际后台/前台暖恢复已测。未执行官方隐藏测试，无官方得分结论。

自测已停止业务设备动作，交还主 Agent 最终审查。子会话标识仅保留已报告的候选 `CODEX_THREAD_ID=01a15798-0e52-7a10-bd8e-fd7c091bb41b`，不将继承父会话 ID 误用为本子会话已核验 UUID。
