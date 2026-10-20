# vg-spec13 冻结页面源码审查 v1

CODEX_THREAD_ID：`01a143bb-a10f-7601-a510-405d234afe12`（本角色直接读取环境变量）。

结论：**发现一处需回退编码确认修正的 Builder 参数刷新风险，暂不对页面闭环作无条件通过结论。** 本次仅静态审查，未构建、未操作设备、未运行测试、未改生产/测试/workflow 状态；控制器与经理沿已完成的中审，不重复检查。

审查对象：`SettingsSyncSection.ets`、`SettingsWebDavBuilders.ets`、`SettingsNavigationBuilders.ets`、`SettingsPage.ets`。四文件实际 SHA256 均与 `workflow/implementation/source-fingerprint-v1.json` 对应条目匹配；该清单 aggregate 为 `8b6683b8ca4fed2eb3e4ab743c0f2028cae4a50ea1b8d7ae08fac77ca4e63db1`。本次没有重新计算整个工程 aggregate，不将逐文件匹配冒称完整复算。

## 唯一发现 F01：多层 Builder 在输入/开关层转成多参数按值传递

`SettingsWebDavBuilders.ets:57,81,119` 的 `WebDavInputField`、`WebDavPasswordField`、`WebDavToggleRow` 均为全局 `@Builder`，接收多个参数；`:153–157,180,203,207` 使用相同多参数调用。虽上层卡片接收的是单参数对象字面量，最内层却再次转成多参数值传递。

依据 [OpenHarmony 官方 @Builder 文档](https://raw.githubusercontent.com/openharmony/docs/master/zh-cn/application-dev/ui/state-management/arkts-builder.md) 的“参数传递规则”“限制条件”“多层 @Builder 函数嵌套”：未使用回调绑定的多个参数不能承担动态刷新；嵌套各层应使用单个对象字面量按引用传参。这是公开官方通用技术文档，与本应用/赛题实现无关；Gitee 原文访问 405 后读取官方 GitHub 原文，未查应用上游。

由源码及该规则推导的风险：五输入的 disabled/value、密码显隐、自动同步 Toggle 状态可能停留初值；回调的业务 guard 仍可阻止设置写入，但不能证明控件实际禁用或回填/显隐正常。此为静态风险，**未宣称已在设备复现**。

建议最小调整：只为上述三个 helper 增加有名 Options 接口，各改一个参数；调用点逐字段传对象字面量，保证引用链连续。可执行字段约定：`WebDavInputOptions` 含 colors/disabled/inputId/label/value/placeholder/onChange；`WebDavPasswordOptions` 再含 isVisible/onToggle（可继承前者）；`WebDavToggleOptions` 含 colors/title/subtitle/isOn/onChange。三个签名分别为 `WebDavInputField(options: WebDavInputOptions)`、`WebDavPasswordField(options: WebDavPasswordOptions)`、`WebDavToggleRow(options: WebDavToggleOptions)`，内部只把原参数引用替换成 options 对应属性；所有8处调用用 `{ colors: options.colors, ... }` 的逐字段对象字面量，不经临时 Options 变量，也不把整个 options 对象直接转传。回调仍更新原组件状态，helper 不修改入参属性。不改控制器、经理、路由或产品策略，保留 id。需主 Agent 解除生产冻结并派回编码，再重建、更新指纹及验证；本角色未擅改源码。

## 其余限定检查

| 检查 | 静态结论 |
| --- | --- |
| 订阅与释放 | `SettingsSyncSection:45–69` 保存同一 `backupListener` 字段，appear 注册、disappear 先 mounted=false 再注销；监听器和自动配置加载回写前有 mounted guard |
| 真实指示器 | `SettingsSyncSection:386–388` 将 `@State manualBackupBusy` 与结果直接交单 options 对象字面量；`SettingsWebDavBuilders:325–340` 据 backupBusy 构建真实 `LoadingProgress`（24vp、固定 id）与专属状态 Text。此链无多参中转；实际类型、可见区域和 pending 重叠仍待设备证明 |
| 配置与动作 guard | 输入/显隐回调均查 `isWebDavBusy()`；保存检查 controller busy；测试/同步/恢复/备份入口检查 aggregate busy；恢复第一次确认后补查 busy。嵌套输入 `.enabled(!disabled)` 的刷新受 F01 影响，故不能作完整 UI 锁定通过 |
| 顶层 Builder | Basic/Auto/Action、导航 Header/Menu 均由调用者直接传单参数对象字面量、逐属性列出状态和回调，符合引用传递形状；未保留独立业务状态或动态属性。F01 限于其内部多参数 helper |
| 原返回路径 | `SettingsPage:155–164` 原 `handleHeaderBack` 保留：先退分区，再保存设置并 router.back；Header 只回调原方法。分区选择仍写 activeSectionId，WebDAV 仍构建原 SettingsSyncSection；无新路由 |
| LazyForEach 导航 | 使用固定 SETTINGS_SECTIONS 与 item.id 唯一 key、IDataSource 注册/注销、cachedCount(2)；7 个原 section id/标题保留，点击仍把原 item.id 送回父页；内 List 禁止独立滚动并按行数定高，外层原 Scroll 保留。无路由偏离的静态证据，实际滚动/点击仍待设备验证 |
| 受改 UI 行数 | SettingsSyncSection 400、SettingsWebDavBuilders 404、SettingsNavigationBuilders 129、SettingsPage 498，均≤500。F01 修正后须重新核对行数 |

除 F01 外，本次限定源码范围未发现其它需扩展方案的点。运行通过、失败恢复、重入刷新、请求归属及样式可见性由独立验证给出，本文不替代其结论。
