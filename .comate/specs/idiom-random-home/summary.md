# 成语模块实施总结（idiom-random-home）

需求：`SWE-OpenHarmony/specs/jm-spec71.md`（4 个场景）。基线 `3eb576cf2f`，已先执行官方 `prepare_baseline.py`。
10 个任务全部完成，构建通过，5 条 Hypium 自测用例在 Pura 模拟器（127.0.0.1:5555）全部 OK，官方示例 `examples/jm-spec7` 亦通过。

## 做了什么

**路由与入口**：成语模块补齐 `route_map.json`（`IdiomIndexPage` / `IdiomDetailPage` / `IdiomSearchPage`）与 `module.json5` 的 `routerMap`；首页 `MenuList.ets:55` 的「成语」补上 `pushPathByName`；`TopBar.ets` 新增收藏夹图标入口；修正 `features/bookmark/.../route_map.json` 的键名（`routeMap` → `routerMap`），使收藏夹页面真正可路由。

**数据可用性（关键）**：基线 `chinese_idiom` 表初始为空，只能在「设置 → 同步/导入」里联网下载，离线或未同步时成语模块必然无数据。新增 `IdiomSeeder.ets` + 内置种子数据 `src/main/resources/rawfile/chinese_idiom_seed/`（49,639 条，20 个分片，约 22MB），`EntryAbility` 启动即后台导入，实测模拟器首启 2.4s 完成。使用远端原始 id 与 `ON_CONFLICT_IGNORE`，与「设置」同步写入的数据完全一致，不会重复或覆盖。`DbUtil` 新增 `ready()`，所有查询先等建表完成，消除启动竞态。

**数据访问层**：`Idiom.ets` 的 `parse` 对 NULL/空串/非法 JSON 容错（原实现会抛异常）；新增排除上次 id 的随机查询、按 id 查询、按词批量查 id（判断近/反义词可否跳转）、模糊搜索（word/pinyin/abbr，`%`/`_`/`\` 转义，精确与前缀匹配优先）、计数。新增 `IdiomBookmark.ets` 基于既有 `bookmarks` 表（`bookmarkable_model = 'chinese_idiom'`）实现查/增/删/切换/列表，添加前判重避免重复行。

**页面**：共享组件 `IdiomView` 渲染成语名、拼音、释义、出处、例句（`～` 还原为成语本身）、用法、名著引用、成语故事、注意，以及近义词/反义词标签组——词库中存在则可点击跳转该成语详情，不存在则置灰并 Toast 提示。首页（随机展示 + 下拉刷新 + 底部搜索/收藏/刷新）、详情页（按 id 展示 + 收藏，可从标签无限链式跳转并逐级返回）、搜索页（300ms 防抖 + 回车即搜 + 结果列表）、收藏夹页（已收藏成语列表，`onShown` 重载）均复用该组件。首页 `onShown` 只同步收藏状态、不重新随机，保证返回后成语与滚动位置不变。

## 边界处理

上次展示 id 存入 Preferences，刷新/返回重进/重启都换一条；表内仅 1 条时回退普通随机；刷新与收藏有 in-flight 保护，重复点击不叠加；加载 token 丢弃过期结果；空关键词不查询；搜索关键词通配符转义；种子导入失败只记日志并在下次进入重试，页面显示「暂无成语数据」提示而非崩溃。

## 验证

- 构建：`ohpm install --all` + `hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon`，BUILD SUCCESSFUL，产物 `products/default/build/default/outputs/default/default-default-unsigned.hap`。
- 自测：`hypium_tests/test_idiom_module.py`（场景一随机与刷新、场景二收藏+详情+返回保持+收藏夹、重启后收藏持久化与取消、场景三搜索「一石二鸟」、场景四近/反义词链式跳转与逐级返回）5/5 通过；另手动验证下拉刷新可换一条成语。

## 需要注意

- 内置种子数据来源：本应用自身的公开数据接口 `https://p1-cdn.jingmo.ruaruan.com/api/chinese_idiom_v5_*.json`（基线「设置 → 数据同步」运行时下载的同一数据，版本 v5，仅做字段裁剪与分片），提交材料的来源说明中需如实标注。
- HAP 体积因内置数据增至约 24MB；若需减小，可改用「有成语故事或反义词 + 近反义词闭包」的约 1.5 万条子集（约 8.9MB），代价是隐藏用例搜索冷门成语时可能落空。
- `features/bookmark/BuildProfile.ets` 为构建生成文件，与其他模块保持一致，已随工程保留。
