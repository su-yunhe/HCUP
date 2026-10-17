# 成语模块：首屏随机展示 / 收藏 / 详情 / 搜索 / 近反义词关联浏览

特性名：`idiom-random-home`。需求来源：`SWE-OpenHarmony/specs/jm-spec71.md`（4 个场景）。基线已执行 `prepare_baseline.py`（成语/知识/语录 Index.ets 导出路径修正、锁文件更新），本需求在其上开发。

## 一、现状分析（基线）

| 位置 | 现状 | 问题 |
| --- | --- | --- |
| `features/home/src/main/ets/view/MenuList.ets:55` | "成语" GridItem 无 onClick | 入口不可用 |
| `features/chinese/idiom/src/main/ets/pages/IdiomIndexPage.ets` | 仅 Hello World 占位（struct 名 MainPage） | 无任何功能 |
| `features/chinese/idiom/src/main/module.json5` | 无 routerMap，无 `route_map.json` | 无法 `pushPathByName` |
| `features/chinese/idiom/src/main/ets/model/Idiom.ets` | 仅 `createIdiom`、`readRandomIdiom`；`parse` 对 NULL/空串 JSON.parse 会抛异常 | 缺按 id/词查询、搜索、收藏 |
| `commons/utils/src/main/ets/data/DbUtil.ets` | `getRdbStore` 回调式初始化，页面可能在建表完成前查询 | 无"就绪"等待机制 |
| `features/bookmark` | `BookmarkIndexPage` 空页面；`route_map.json` 键名写成 `routeMap`；未被任何模块依赖 | 收藏夹不可达、无内容 |
| `features/home/src/main/ets/view/TopBar.ets` | 仅设置图标 | 无收藏夹入口 |
| 数据 | `chinese_idiom` 表初始为空，只能在"设置→同步/导入"中从网络或文件导入（49639 条） | 新装应用进入成语页无数据，搜索"一石二鸟"必然失败 |

## 二、总体方案

1. **数据保障（内置种子数据）**：在成语模块 `rawfile/chinese_idiom_seed/` 内置从本应用自身公开数据接口（`NetworkConst.BASE_URL1` 的 `chinese_idiom_v5_*.json`）筛选出的约 1.5 万条成语，首次启动时批量写入 `chinese_idiom` 表（使用远端原始 id，`ON_CONFLICT_IGNORE`），与"设置→同步数据"写入的数据完全一致、不会重复。
   - 筛选规则：有"成语故事"或"反义词"的成语（11004 条，覆盖常用成语）+ 其近义词/反义词在全量库中可解析词条的**闭包**（迭代至不动点，约 14.9k 条，≈8.9MB，按 id 排序切分为每 2000 条一个文件）。保证种子库内任一成语的近/反义词标签，只要全量库中存在，种子库中也存在，近反义词跳转链路不断。
   - 一石二鸟(869) → 一箭双雕(915)/一举两得(44) 等均包含在内。
2. **DB 就绪等待**：`DbUtil` 增加 `ready(): Promise<RdbStore | undefined>`，在建表迁移完成后 resolve；成语所有查询先 `await` 就绪 + 种子导入完成。
3. **路由**：成语模块新增 `route_map.json`，注册 `IdiomIndexPage`、`IdiomDetailPage`、`IdiomSearchPage`；收藏夹 `route_map.json` 键名修正为 `routerMap`。所有页面沿用现有 `NavDestination + @Consumer('NavPathStack')` 模式。
4. **页面**：
   - `IdiomIndexPage`（标题"成语"）：随机成语内联完整展示 + 底部操作栏【搜索】【收藏/已收藏】【刷新】，支持下拉刷新；点击内容区进入详情。
   - `IdiomDetailPage`（标题"成语详情"）：按 id 展示完整信息 + 底部【收藏/已收藏】。
   - `IdiomSearchPage`（标题"搜索成语"）：Search 输入框，输入即搜（300ms 防抖）+ 回车/搜索按钮立即搜，结果 List，点击进详情。
   - `BookmarkIndexPage`（标题"收藏夹"）：列出已收藏成语，点击进详情；首页 TopBar 新增收藏图标入口。
5. **共享展示组件 `IdiomView`**：成语名、拼音、释义、出处、例句、用法、名著引用、成语故事、注意、近义词标签组、反义词标签组；首页与详情页共用。标签点击：词库中存在 → push 该成语的 `IdiomDetailPage`；不存在 → 置灰样式，点击 Toast 提示"词库中暂未收录"。

## 三、受影响文件

| 类型 | 绝对路径（根：`/Users/bress/Documents/code/harmonycup-work/jm-spec71`） | 内容 |
| --- | --- | --- |
| 修改 | `commons/utils/src/main/ets/data/DbUtil.ets` | 新增 `ready()`；迁移结束后统一 resolve |
| 修改 | `commons/utils/src/main/ets/data/PrefUtil.ets` | 新增 `saveChineseIdiomId/getChineseIdiomId`（上次展示 id）、`saveChineseIdiomSeedVersion/getChineseIdiomSeedVersion` |
| 修改 | `commons/constants/src/main/ets/PrefConst.ets` | 新增 `CHINESE_IDIOM_SEED_VERSION`（复用已有 `CHINESE_IDIOM_ID`） |
| 修改 | `commons/constants/src/main/ets/DbConst.ets` | `DbCRUDConst` 新增成语按 id/排除随机/搜索、收藏增删查 SQL |
| 修改 | `features/chinese/idiom/src/main/ets/model/Idiom.ets` | 健壮 `parse`；新增 `readRandomIdiom(excludeId)`、`readIdiomById`、`readIdiomIdsByWords`、`searchIdioms`、`countIdioms` |
| 新增 | `features/chinese/idiom/src/main/ets/model/IdiomBookmark.ets` | `isIdiomBookmarked`、`addIdiomBookmark`、`removeIdiomBookmark`、`toggleIdiomBookmark`、`readBookmarkedIdioms` |
| 新增 | `features/chinese/idiom/src/main/ets/model/IdiomSeeder.ets` | `ensureIdiomReady(context)`：单例 Promise，DB 就绪 + 种子导入 |
| 新增 | `features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/manifest.json`、`part_*.json` | 种子数据 |
| 新增 | `features/chinese/idiom/src/main/ets/view/IdiomView.ets`、`view/IdiomActionBar.ets` | 共享展示组件、底部操作按钮 |
| 重写 | `features/chinese/idiom/src/main/ets/pages/IdiomIndexPage.ets` | 成语首页 |
| 新增 | `features/chinese/idiom/src/main/ets/pages/IdiomDetailPage.ets`、`IdiomSearchPage.ets` | 详情页、搜索页 |
| 新增/修改 | `features/chinese/idiom/src/main/resources/base/profile/route_map.json`、`module.json5` | 路由注册 |
| 修改 | `features/chinese/idiom/Index.ets`、`oh-package.json5` | 导出新 API；新增 `uicomponents` 依赖 |
| 修改 | `features/bookmark/...`：`BookmarkIndexPage.ets`、`route_map.json`、`oh-package.json5`、`Index.ets` | 收藏夹列表；依赖 `chinese_idiom`、`utils` |
| 修改 | `features/home/src/main/ets/view/MenuList.ets`、`TopBar.ets`、`oh-package.json5` | 成语入口 onClick；收藏夹图标；依赖 `bookmark` |
| 修改 | `products/default/src/main/ets/entryability/EntryAbility.ets`、`oh-package.json5` | 启动即后台预导入种子（依赖 `chinese_idiom`） |
| 更新 | 各模块 `oh-package-lock.json5` | `ohpm install --all` 重新生成 |

## 四、实现细节

### 4.1 DbUtil 就绪

```ts
private store?: relationalStore.RdbStore; private initialized = false;
private waiters: Array<(s: relationalStore.RdbStore | undefined) => void> = [];
ready(): Promise<relationalStore.RdbStore | undefined> {
  if (this.initialized) return Promise.resolve(this.objectiveRDB);
  return new Promise((resolve) => { this.waiters.push(resolve) });
}
// init 回调：error 或迁移结束（rdbStore.version 赋值后）调用 markReady()
```

### 4.2 种子导入 `ensureIdiomReady(context)`

```ts
let readyPromise: Promise<void> | null = null;
export function ensureIdiomReady(context: Context): Promise<void> {
  if (!readyPromise) readyPromise = doSeed(context).catch(() => { readyPromise = null });
  return readyPromise;
}
async function doSeed(context) {
  const store = await DbUtil.ready(); if (!store) return;
  if (PrefUtil.getChineseIdiomSeedVersion() >= SEED_VERSION && await countIdioms() > 0) return;
  manifest = JSON.parse(decode(await context.resourceManager.getRawFileContent('chinese_idiom_seed/manifest.json')))
  for (file of manifest.files) {
    rows = JSON.parse(decode(await getRawFileContent(`chinese_idiom_seed/${file}`)))
    await store.batchInsertWithConflictResolution(CHINESE_IDIOM_TABLE, rows.map(toBucket),
      relationalStore.ConflictResolution.ON_CONFLICT_IGNORE)   // API 18+，工程 compatibleSdk=19
  }
  PrefUtil.saveChineseIdiomSeedVersion(SEED_VERSION)
}
```
`toBucket` 与 `createIdiom` 存储格式一致（JSON 字段 `null` 存为 `"null"`）。失败只记日志，不阻塞页面（页面显示空数据提示）。EntryAbility 在 `DbUtil.init` 后立即调用，页面进入时再次 `await`（同一 Promise）。

### 4.3 数据访问（全部参数化查询）

- 随机且不同于上一次：`select * from chinese_idiom where id = (select id from chinese_idiom where id != ? order by random() limit 1)`；若结果为空（表内仅 1 条）回退到原 `READ_RANDOM_CHINESE_IDIOM`。上次展示 id 存 `PrefUtil`（`chinese_idiom_id`），覆盖"刷新"、"返回后重新进入"、"重启应用后进入"三种情况。
- 按 id：`select * from chinese_idiom where id = ? limit 1`。
- 标签解析：`select id, word from chinese_idiom where word in (?,?,…)` → `Map<string, number>`。
- 搜索：关键词 `trim()`，转义 `\ % _`，`word like %k% or abbr like %k% or pinyin like %k% escape '\'`，排序 `case when word = k then 0 when word like k% then 1 else 2 end, length(word), id`，`limit 100`。
- 收藏（`bookmarks` 表，`bookmarkable_model = 'chinese_idiom'`）：存在性 `count(*)`；添加前先判重，避免重复行；取消删除全部匹配行；列表 `select i.* from bookmarks b join chinese_idiom i on i.id = b.bookmarkable_id where b.bookmarkable_model = ? order by b.id desc`。
- `parse` 健壮化：JSON 列为 NULL/空串/非法时返回 null，不抛异常。

### 4.4 IdiomView（`@ComponentV2`）

- `@Param @Require idiom: Idiom`；`@Event onOpenIdiom: (id: number) => void`；`@Local linkedIds: Map<string, number>`。
- `aboutToAppear` 与 `@Monitor('idiom')` 时调用 `readIdiomIdsByWords(similar ∪ opposite)`。
- 布局：成语名（28 号粗体，独立 Text，内容恰为 `word`）、拼音（独立 Text，内容恰为 `pinyin`）；分节标题沿用 `BoldTitle`：
  `释义`（无则"暂无"）、`出处`（`text ——book`，无则"暂无"）、`例句`（`～` 替换为成语本身，附 `——book`，无则"暂无"）、`用法`、`名著引用`、`成语故事`、`注意`（这些有才显示）、`近义词`、`反义词`（有数据才显示，Flex 换行标签）。
- 标签：存在于词库 → 主题色描边可点，点击 `onOpenIdiom(id)`；否则灰色，点击 Toast"词库中暂未收录「X」"。标签自身 onClick 会消费点击，不触发外层"进入详情"。

### 4.5 IdiomIndexPage

- 状态：`idiom`、`loading`、`bookmarked`、`toggling`、`refreshing`、`loadToken`。
- `aboutToAppear` → `load()`：`await ensureIdiomReady` → `readRandomIdiom(PrefUtil.getChineseIdiomId())` → 保存 id → 查询收藏状态。`loadToken` 防止并发刷新结果乱序；`loading` 时忽略重复刷新。
- `onShown`：仅重新查询当前成语收藏状态（从详情页返回后状态同步），**不**重新随机，保证返回后成语与滚动位置保持。
- 布局：`Refresh`（下拉刷新）包裹 `Scroll`，内容区 `Column.onClick → push IdiomDetailPage(id)`；底部 `IdiomActionBar`：`搜索`（push `IdiomSearchPage`）、`收藏`/`已收藏`（图标 `ic_bookmark_border`/`ic_bookmark`）、`刷新`。按钮为 `Button` 包裹图标 + 文本（文本恰为上述文案），带 `id`。
- 空/异常：加载中显示 `LoadingProgress` + "加载中…"；无数据显示"暂无成语数据，请在 设置 → 数据同步 中下载"。

### 4.6 IdiomDetailPage

- `onReady` 读取 `ctx.pathInfo.param as number` → `readIdiomById`；`onShown` 刷新收藏状态。
- 底部【收藏/已收藏】；标签点击 push 新的 `IdiomDetailPage`（可无限关联浏览，返回逐级回退）。
- id 无效/不存在：显示"未找到该成语"。

### 4.7 IdiomSearchPage

- `Search({ value, placeholder: '输入成语或拼音首字母' }).searchButton('搜索').defaultFocus(true)`；`onChange` 300ms 防抖，`onSubmit` 立即搜索；`searchToken` 丢弃过期结果；`aboutToDisappear` 清理定时器。
- 状态：空关键词 → 提示文案；搜索中 → Loading；无结果 → "未找到与「k」相关的成语"；有结果 → `List`（成语名 / 拼音 / 释义两行省略），点击 push 详情。返回后关键词、结果、滚动位置保持（页面仍在栈中）。

### 4.8 收藏夹与首页入口

- `TopBar` 在设置图标左侧增加 `Icon.ic_bookmark_border` → `pushPathByName('BookmarkIndexPage')`。
- `BookmarkIndexPage`：`onShown` 重新加载 `readBookmarkedIdioms()`；始终渲染 `List`，空时 ListItem 显示"暂无收藏"；点击 push `IdiomDetailPage`。
- `MenuList` 成语 GridItem：`onClick → pushPathByName('IdiomIndexPage', null)`。

## 五、数据流

```
EntryAbility.onWindowStageCreate → DbUtil.init → (建表) → markReady
                                 → ensureIdiomReady(context) → rawfile 种子 → batchInsert(IGNORE) → pref 记录版本
首页 MenuList「成语」→ IdiomIndexPage → await ensureIdiomReady → readRandomIdiom(排除上次 id) → IdiomView
  ├ 收藏按钮 → toggleIdiomBookmark → bookmarks 表 → 按钮文案「已收藏」
  ├ 内容区 → IdiomDetailPage(id) → readIdiomById → IdiomView → 近/反义词标签 → IdiomDetailPage(新 id) …
  ├ 搜索 → IdiomSearchPage → searchIdioms(k) → List → IdiomDetailPage(id)
  └ 刷新/下拉 → readRandomIdiom(排除当前 id)
首页 TopBar 收藏图标 → BookmarkIndexPage → readBookmarkedIdioms → IdiomDetailPage(id)
返回 → onShown → isIdiomBookmarked 同步按钮状态
```

## 六、边界条件

| 场景 | 处理 |
| --- | --- |
| DB 未就绪 / 种子导入中 | 页面 Loading，等待 `ensureIdiomReady` |
| 种子导入失败且未同步 | 空数据提示，不崩溃；下次进入重试 |
| 已通过"设置"同步全量数据 | 种子 `IGNORE` 不覆盖；id 一致无重复 |
| 表内仅 1 条 | 排除查询为空时回退普通随机 |
| 快速重复点刷新 / 收藏 | `loading` / `toggling` 标志忽略重入 |
| 收藏后进入详情再取消，返回首页 | `onShown` 重新查询，状态一致 |
| 搜索空串 / 纯空格 / 含 `%` `_` | 空串不查询；通配符转义 |
| 标签词不在词库 | 灰色样式 + Toast，不跳转 |
| JSON 字段 NULL / 非法 | `parse` 返回 null，对应分节隐藏或"暂无" |
| 例句中的 `～` | 替换为成语本身 |

## 七、预期结果

- 场景一：主页点"成语"进入标题为"成语"的页面，显示成语名、拼音、释义等；点"刷新"/下拉/返回再进入/重启，均显示与上次不同的成语。
- 场景二：点"收藏"→ Toast"收藏成功"，按钮变"已收藏"；点内容区进入"成语详情"，含出处、例句等；返回后仍为同一成语且"已收藏"；重启后收藏仍在，收藏夹可见。
- 场景三：点"搜索"进入搜索页，输入"一石二鸟"后列表出现"一石二鸟"条目（精确匹配排第一）。
- 场景四：详情页在释义、出处（名著引用、成语故事）后显示"近义词""反义词"标签；点"一箭双雕"跳到其详情页，可继续点其标签链式浏览，返回逐级回退。

## 八、验证方式

- `ohpm install --all` + `hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon` 构建通过。
- 在已连接模拟器（127.0.0.1:5555）安装 HAP，用 Hypium 编写本地自测脚本（放在本题工作目录 `hypium_tests/`，不进入提交工程源码）覆盖四个场景及返回/重进/重复点击。

