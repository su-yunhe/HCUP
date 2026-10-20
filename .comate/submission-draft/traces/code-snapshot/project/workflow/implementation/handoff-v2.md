# vg-spec13 F01 修复交接 v2

编码角色真实 `CODEX_THREAD_ID=01a143bf-40f7-7d62-b34c-af46d1698de6`。本轮只完成主 Agent 回派的最小 F01 修复及局部构建，不替代独立自测。v1 交接、指纹、构建日志与既有失败/暂停记录均保留。

## 授权、依据与范围

主 Agent 先派只读准备，随后明确确认本题 runner 和设备采样均已停止、端口及本题转发已清理，正式解冻并授权只改 `SettingsWebDavBuilders.ets`。本角色在解冻前只读官方依据、设计审查及当前指纹，没有源码写入；六个生产文件与 v1 指纹逐项匹配。

批准方案补充为 `workflow/design/final-source-review-v1.md`，SHA256 `38c145abcde428de9645855b84f14cc1c77ca60560c8d482616c9674ac27d465`。修复依据是 [OpenHarmony 官方 @Builder 文档](https://raw.githubusercontent.com/openharmony/docs/master/zh-cn/application-dev/ui/state-management/arkts-builder.md) 的参数规则及“多层 @Builder 函数嵌套”段落：动态 UI 更新需要在嵌套调用的每一层保持单对象字面量的引用传参。该公开通用技术文档已实际读取；没有访问应用上游实现或其它题工程。

F01 是设计源码审查发现的静态参数刷新风险，未由本角色宣称为设备已复现故障。主 Agent 告知 run01 因测试 CLI 滑动耗时暂停，没有产品结论；本轮未改测试来制造通过。

## 唯一生产修改

文件：`entry/src/main/ets/pages/settings/SettingsWebDavBuilders.ets`。

- 新增有名 `WebDavInputOptions`、`WebDavPasswordOptions`（继承输入 Options）、`WebDavToggleOptions`。
- `WebDavInputField`、`WebDavPasswordField`、`WebDavToggleRow` 各只接收一个 Options 参数；内部读取 `options` 明确字段。
- 三个输入、两个密码输入、三个开关共 **8 处调用**，均直接传逐字段对象字面量，使上层卡片到最内层 helper 的参数链连续。
- 保留原输入 id、密码显隐按钮、布局/样式、enabled 语义及原回调；顶层卡片和进度条渲染不调整。

相对 v1 六个生产文件的 SHA256 比较，仅此文件变化；控制器、经理、路由与其它生产文件未改。最终该文件 **455 行**，其余受改 UI 仍为 SettingsPage 498、SettingsSyncSection 400、SettingsNavigationBuilders 129 行。无 any/unknown token，`git diff --check` 退出 0。

本修复支持原 R02/R08 的控件锁定和配置刷新、R01 的表单行为，并保留自动同步 Toggle 和密码显隐的原界面含义；不增加产品需求。

## 本轮真实构建

每个构建 PowerShell 首先加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。在本题根运行已有 `workflow/implementation/build.ps1`，先依赖安装，再构建 HAP：

```powershell
hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug assembleHap --no-daemon
```

依赖安装退出 **0**，HAP 构建退出 **0**，`BUILD SUCCESSFUL in 9 s 18 ms`。本轮没有构建失败。

- 原始日志：`logs/implementation-build/20261016-162656-ohpm.log`、`20261016-162656-build.log`。
- 命令/时间/退出码：`logs/implementation-build/20261016-162656-result.json`。
- 静态和产物检查：`workflow/implementation/implementation-checks-v2.json`。
- 告警：`logs/implementation-build/warnings-full-v2.json`、`warnings-comparison-v2.json`。源码诊断 754，按文件+消息多重集对基线比较新增组 0；新增生产文件诊断 0。与 v1 一样，未修改 LoadingAnimations 的两条诊断在增量日志未出现，不能说本修复消除了它们，最终以独立 clean build 为准。

## v2 指纹及再次冻结

- 源码完整指纹：`workflow/implementation/source-fingerprint-v2.json`，与 v1 相同算法。
- 聚合 SHA256：`e463b2682fed306471dc9068eadf9666cc9928c02a297363a334bf70ff7b30d3`。
- 本角色最后构建 HAP：`entry/build/default/outputs/default/entry-default-unsigned.hap`，SHA256 `212fb45ccf577011aefb3d1596b6239a3d0a571bcc3226076cf9b1a69abebfa9`。
- 已向主 Agent 明确发送重新冻结信号，从该消息起没有后续生产写入，仅补本文。v2 采集脚本独立为 `workflow/implementation/collect-evidence-v2.py`，没有覆盖 v1 证据文件。

## 验证接续与未解决项

本角色未操作设备、未执行 Hypium 或服务端请求采样。F01 参数形状已按官方规则修正并构建通过；五输入在途实际禁用、输入回填、密码显隐、自动同步开关刷新仍由独立设备回归确认。原 R01–R10 的真实备份、进度类型/可见性/请求同窗、终态、失败、重入与重启验证继续有效，不能用本轮构建代替。

当前无编译阻断或待完成的本轮生产修改；最终结论由主 Agent 结合独立自测作出。
