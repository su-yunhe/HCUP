# 基线现状记录（完善收藏夹支持更多内容类型）

标注约定：【代码实证】= 读代码得出并给出 `文件:行号`；【运行实证】= 在模拟器上实际操作观察到；【推断】= 未验证的推测。

## 1. 基线快照标识

| 项 | 值 |
| --- | --- |
| metadata `base_commit` | `b2e40f69dde450852d977c9555a9b12d59508c0d` |
| 当前 HEAD | `264a375d83db8191c12b695a003e85a64676f21c`（base 之上仅有 BuildProfile.ets 重新生成 + spec 文档，无业务代码差异，`git diff b2e40f6 HEAD --stat` 已核对） |
| git tag | `baseline-jm-spec7` → `264a375`（题目 ID 按工程目录名取 `jm-spec7`，如官方 ID 不同请告知） |
| 分支 | `dev`，工作区干净 |

## 2. 构建基线状态

构建命令（命令行，需显式指定 DevEco 自带 JBR，否则 PackageHap 报 `00308018 Unable to locate a Java Runtime`）：

```bash
export JAVA_HOME=/Applications/DevEco-Studio.app/Contents/jbr/Contents/Home
export DEVECO_SDK_HOME=/Applications/DevEco-Studio.app/Contents/sdk
export PATH=$JAVA_HOME/bin:/Applications/DevEco-Studio.app/Contents/tools/node/bin:$PATH
H=/Applications/DevEco-Studio.app/Contents/tools/hvigor/bin/hvigorw.js
node $H clean --no-daemon
node $H --mode module -p module=default@default -p product=default -p buildMode=debug assembleHap --no-daemon
```

结果【运行实证】：`BUILD SUCCESSFUL`（clean 后全量约 11s），产物 `products/default/build/default/outputs/default/default-default-unsigned.hap`。

已有告警清单（clean 全量构建，用于后续对比是否引入新告警）：

| 类别 | 数量 | 说明 |
| --- | --- | --- |
| ArkTS:WARN `Function may throw exceptions. Special handling is required.` | 27 | 各 model 中 `JSON.parse` 等调用，如 `Lyric.ets:26/61`、`ModernPoetry.ets:33/71`、`ClassicPoem.ets:93/138`、`Writing.ets:187/240/327/331/335/337/338/339` 等 |
| ArkTS:WARN `The current component id "image" is duplicate ...` | 8 | 各 SnapshotPage.ets 的 `.id("image")` 重复 |
| ArkTS:WARN `WRITE_IMAGEVIDEO` 权限提示 | 1 | `commons/uicomponents/.../SnapshotComponent.ets:258` |
| 资源冲突 `'app_name' / 'page_text_font_size' / 'page_show' / 'settings' conflict` | 多条 | 多模块同名 string 资源 |
| `No signingConfig found for product default` | 1 | 题包已移除签名，产物为 unsigned |

ArkTS:WARN 合计 36 条。完整日志在本机 `/tmp/jm-spec7-baseline-build.keep.log`（临时文件，不入库）。

安装【运行实证】：`hdc list targets` → `127.0.0.1:5555`（模拟器，`const.product.model=emulator`）；`hdc install -r <unsigned.hap>` → `install bundle successfully`。bundleName `com.hefengbao.jingmo.hw`（`AppScope/app.json5:3`），Ability `EntryAbility`。

## 3. Spec 描述的入口当前在哪

| 项 | 现状 |
| --- | --- |
| 主页 | `features/home/src/main/ets/pages/HomePage.ets:45` `Navigation(this.pageStack)`，`TopBar` + `MenuList` |
| 收藏入口按钮 | `features/home/src/main/ets/view/TopBar.ets:17-21`，`CustomMenuItem({ icon: Icon.ic_bookmark_border, pathName: "BookmarkIndexPage" })`，点击 `TopBar.ets:56` `pushPathByName(this.pathName, null)` |
| 入口位置 | 【代码实证+运行实证】**在主页右上角**，不是 Spec 说的"左上角"：左侧是 `Text('京墨文库')`，`Blank()` 之后依次是 收藏 / 链接 / 设置 三个图标。模拟器坐标：收藏 Stack `[720,164][860,304]`、链接 `[916,..][1056,..]`、设置 `[1112,..][1252,..]`。三个图标均无文字、无 `.id()` |
| 路由名 | `BookmarkIndexPage`（`features/bookmark/src/main/resources/base/profile/route_map.json`，builder `IndexPageBuilder`） |
| 页面文件 | `features/bookmark/src/main/ets/pages/IndexPage.ets` |
| 页面标题 | `.title(String.bookmark)`（`IndexPage.ets:128`）→ 资源 `bookmark` = **"收藏夹"**（`commons/constants/src/main/resources/base/element/string.json`）。运行时 TitleBar 文字 `收藏夹`，id `__NavdestinationField__Text__MainTitle__` |

各内容模块入口（主页 `features/home/src/main/ets/view/MenuList.ets`，均为 `pushPathByName('<X>IndexPage', null)`）：

| 主页文字 | 路由 | MenuList 行 | 主页坐标（模拟器） |
| --- | --- | --- | --- |
| 经典诗文 | ClassicPoemIndexPage | 22 | [56,557][626,735] |
| 诗文 | WritingIndexPage | 30 | [682,557][1252,735] |
| 诗文名句 | SentenceIndexPage | 38 | [56,791][626,969] |
| 人物 | PeopleIndexPage | 46 | [682,791][1252,969] |
| 成语 | IdiomIndexPage | 78 | [56,1428][626,1606] |
| 歇后语 | WisecrackIndexPage | 86 | [682,1428][1252,1606] |
| 谚语 | ProverbIndexPage | 94 | [56,1662][626,1840] |
| 谜语 | RiddleIndexPage | 102 | [682,1662][1252,1840] |
| 歌词 | LyricIndexPage | 126 | [56,2130][626,2308] |
| 诗歌 | ModernPoetryIndexPage | 142 | [56,2364][626,2542] |

注意：主页同时存在分组标题 "古诗文"（`MenuList.ets:12`），Spec 中的"古诗文"在 UI 上是分组名，不是一个可点击模块。

## 4. 相关现状

### 4.1 收藏页（`features/bookmark/src/main/ets/pages/IndexPage.ets`）

- 状态：`@ComponentV2`，`@Local entities: BookmarkEntity[]`（:19）。
- 刷新：`aboutToAppear` 注册 `uiObserver.on('navDestinationUpdate')`，当 `info.name == 'BookmarkIndexPage' && info.state == 4`（ON_WILL_SHOW）时调用 `getEntities()` 重新查库（:21-30）。【运行实证】从详情页取消收藏后返回，列表即时刷新。
- 列表：`List` + `Repeat<BookmarkEntity>`，`.key(item => \`${item.id}\`)`（:38-117）。**无空状态提示**：无收藏时页面空白。
- 渲染分支 `if/else if` 只覆盖 8 种 `bookmarkable_model`（:42-114）：对联、汉字、词语、成语、知识卡片、句子、经典诗文、诗文名句。其他 model 的记录 **ListItem 为空**（不渲染内容但仍占一个 ListItem，带 divider；运行实证见 §7.1）。
- 条目组件 `Item`（:135-160）：`BlockTitle({ title: model })`（类型名，如"成语"）+ `Text(content)`（`maxLines(2)`、省略号）。只有 **一个** 摘要字段，没有作者字段。
- 点击：`pushPathByName('<X>ShowPage', new ParamNumberId(bookmarkable_id))`。
- 无任何 `.id()`。

### 4.2 数据模型与存储

- 表 `bookmarks`（`commons/constants/src/main/ets/DbConst.ets:13`），建表 `DbConst.ets:83-85`：`id integer primary key autoincrement, bookmarkable_id integer, bookmarkable_model text`。只存 id + 类型，**不存标题/摘要快照**。
- DAO：`features/bookmark/src/main/ets/model/Bookmark.ets`：`addBookmark`（:22，`ON_CONFLICT_REPLACE`）、`cancelBookmark(id, model)`（:40，按 id+model 删除所有匹配行）、`getBookmark`（:59）、`getBookmarks`（:84）。模块导出 `features/bookmark/Index.ets`。
- 列表查询：`DbCRUDConst.BOOKMARKS`（`DbConst.ets:313-340`），`bookmarks` LEFT JOIN 8 张内容表，按 `b.id desc`。实体 `BookmarkEntity`（`features/bookmark/src/main/ets/model/BookmarkEntity.ets:9-47`）字段与 SQL 别名一一对应，`getEntities()`（:49）。
- 类型常量：`commons/constants/src/main/ets/PrefConst.ets:6-23`。
- 数据库：RDB `jingmo.db`（`DbConst.ets:6`），`DbUtil.objectiveRDB`（`commons/utils/src/main/ets/data/DbUtil.ets`）。

### 4.3 各内容类型的收藏能力【代码实证】

所有带收藏的模块写法一致：ViewModel 调 `bookmark` 模块的 `addBookmark(new Bookmark(YmdHisToNumber(), id, PrefConst.X))` 后再 `getBookmark` 回读；页面用 `@Local bookmarked` 控制 NavDestination toolbar 项的文字（`添加收藏`/`取消收藏`）和图标（`ic_bookmark_border`/`ic_bookmark`），`hideItemValue: true`，**无 toast**。IndexPage（随机一条）与 ShowPage（详情）都有收藏按钮。

| UI 名 | model 常量值 | 内容表 / 摘要候选字段 | ShowPage 路由 / 参数 | 收藏按钮位置 | 当前收藏页是否展示 |
| --- | --- | --- | --- | --- | --- |
| 歌词 | `chinese_lyric` | `chinese_lyric`: title, writer(可空), singer(可空), content | `LyricShowPage` / `ParamNumberId` | `lyric/.../ShowPage.ets:45-72` toolbar 第 1 项；IndexPage:63 第 1 项 | **否** |
| 诗歌 | `chinese_modernpoetry` | `chinese_modernpoetry`: title, author, content | `ModernPoetryShowPage` | `poetry/.../ShowPage.ets:45` 第 1 项 | **否** |
| 谜语 | `chinese_riddle` | `chinese_riddle`: puzzle, answer | `RiddleShowPage` | `riddle/.../ShowPage.ets:35-45` **第 2 项**（第 1 项是 显示/隐藏谜底） | **否** |
| 歇后语 | `chinese_wisecrack` | `chinese_wisecrack`: riddle, answer | `WisecrackShowPage` | `wisecrack/.../ShowPage.ets:34` 第 1 项 | **否** |
| 谚语 | `chinese_proverb` | `chinese_proverb`: content | `ProverbShowPage` | `proverb/.../ShowPage.ets:34` | **否** |
| 诗文 | `classicalliterature_writing` | `classicalliterature_writing`: title(**JSON 字符串**，模型 `Title: Clause{Content}`), author, dynasty | `WritingShowPage` | `writing/.../ShowPage.ets:47` | **否** |
| 人物 | `classicalliterature_people` | `classicalliterature_people`: name, dynasty | `PeopleShowPage` | `people/.../ShowPage.ets:42` | **否** |
| 经典诗文 | `classicalliterature_classicpoem` | `classicalliterature_classicpoem`: title, writer, dynasty | `ClassicPoemShowPage` | `classicpoem/.../ShowPage.ets:54-81`；IndexPage:85 | 是，**只显示 title，无作者**（`DbConst.ets:320`） |
| 成语 | `chinese_idiom` | word | `IdiomShowPage` | `idiom/.../ShowPage.ets:51-78` | 是（word） |
| 对联/汉字/词语/知识卡片/句子/诗文名句 | 见 PrefConst | body/character/word/content/content/content | 各自 ShowPage | — | 是 |
| 绕口令 | `chinese_tonguetwister` | — | — | ShowPage/IndexPage **无收藏按钮**（grep 无 bookmark 调用） | 不适用 |

所有 ShowPage 都在 `onReady` 里 `ctx.pathInfo.param as ParamNumberId` 按 id 查库（如 `lyric/.../ShowPage.ets:73-87`），所以收藏页只需传 `ParamNumberId(bookmarkable_id)` 即可复用。

### 4.4 收藏 id 生成（基线缺陷，仅记录）

`commons/utils/src/main/ets/DatetimeUtil.ets:1-13` `YmdHisToNumber()` 拼接 `${year}${month}${day}${hours}${minutes}${seconds}` **不补零**：

1. 同一秒内收藏两条不同内容 → 主键相同 → `ON_CONFLICT_REPLACE` 覆盖前一条，前一条收藏丢失。
2. 不同时刻可能产生相同数字（如 1 日 12:3:4 与 11 日 2:3:4 → 都可能拼成同一串），同样会覆盖。
3. 位数不固定，`order by b.id desc` 不是严格的"最新在前"。【运行实证，§7.1：11:00 收藏的《长恨歌》排在更早收藏的"精锐之师"之后】

另：页面在 `addBookmark` 的 Promise 返回前 `bookmarked` 仍为 undefined，快速连点两次会插入两行（不同秒时）→ 收藏页出现重复条目；`cancelBookmark` 会一次删掉全部匹配行【推断，未运行验证】。

## 5. 可复用的既有实现

- 收藏页现有的 "LEFT JOIN + 别名字段 + if/else 分支渲染 + `pushPathByName(<X>ShowPage, ParamNumberId)`" 模式，新增类型直接沿用最省改动，官方测试从主页收藏图标进入同一页面。
- 各模块自己的 `<X>BookmarkPage` 已经定义了该类型的"摘要"写法，可作为收藏夹摘要字段的依据：
  - 歌词 `lyric/.../BookmarkPage.ets:36-38`：`Text(item.title)` + `Text(item.content)`
  - 诗歌 `poetry/.../BookmarkPage.ets:37-39`：`title` + `content`
  - 谜语 `riddle/.../BookmarkPage.ets:37`：`puzzle`
  - 歇后语 `wisecrack/.../BookmarkPage.ets:37`：`riddle`
  - 谚语 `proverb/.../BookmarkPage.ets:37`：`content`
  - 经典诗文 `classicpoem/.../BookmarkPage.ets:74,82`：`title` + `` `${dynasty}·${writer}` ``
  - 诗文 `writing/.../BookmarkPage.ets:38-41`：`Title.Content` + `Author`
  - 人物 `people/.../BookmarkPage.ets:22` 查询被注释掉，无可用实现
- 字符串资源 `String.chinese_lyric` 等类型名已存在（`commons/constants/src/main/ets/String.ets:6-22`），可直接作为 BlockTitle。
- `bookmark` 模块依赖只有 constants/utils/uicomponents（`features/bookmark/oh-package.json5`），各内容模块反向依赖 bookmark；收藏页**不能 import 内容模块的 model**（会循环依赖），只能像现在这样在 SQL 层 JOIN。

## 6. 缺失项（Spec 要求而基线没有）

1. 收藏页不展示 歌词 / 诗歌 / 谜语 / 歇后语（场景一明文类型）。存在收藏记录时只会出现空 ListItem。
2. 收藏页不展示 谚语 / 诗文 / 人物（场景一"等"可能覆盖，见 acceptance.md 的 U2）。
3. 经典诗文条目只显示标题，**缺少作者**（场景二明文要求"标题和作者名称"）。
4. 上述新增类型点击后的跳转分支不存在。
5. `BookmarkEntity` / `DbCRUDConst.BOOKMARKS` 缺少对应别名字段和 JOIN。
6. 无空状态提示、无去重（Spec 未明文要求，记录供判断）。

基线已满足：场景三（成语取消收藏后返回列表消失）、收藏页从主页进入、成语等 8 类的展示与跳转、收藏持久化。

## 7. 前置环境需求

| 需求 | 本地情况 |
| --- | --- |
| 登录账号 / 服务端 / WebDAV | 不需要。收藏完全是本地 RDB，无网络请求 |
| 内容数据 | **需要**。App 是"离线数据"模式，内容表靠 设置→同步数据（`NetworkConst.ets:7-9` `p1/p2/p3-cdn.jingmo.ruaruan.com/api/`）或 导入数据 填充。首启弹窗原文：`APP 以【离线数据】的方式提供服务，所以首次使用时请点击右上角【设置】，点击【同步数据】或者【导入数据】获取数据。`（`HomePage.ets:64`） |
| 模拟器数据现状（首轮）【运行实证】 | 只有 **成语** 有数据（且有 4 条已收藏成语：精锐之师、终始若一、横眉瞪目、糠豆不瞻）。其余模块进入后内容为空，收藏按钮置灰（`ToolbarItemStatus.DISABLED`）；同步数据报 `Failed to resolve the host name` |
| 模拟器数据现状（配网后第二轮）【运行实证】 | 设置→同步数据 成功同步：经典诗文 955、歌词 499、诗歌 62、谚语 964、谜语 42446、歇后语 14026（同步页显示的远端条数）。**未同步**：诗文（1631471 条，体量大，同步页提示"请一项一项同步"避免内存崩溃，暂未做）、人物（点同步时 DNS 再次失败，网络不稳定）、诗文名句/汉字/词语/对联/句子/知识卡片/绕口令（与本题无关） |
| 结论 | 场景一的 歌词/诗歌/谜语/歇后语、追加的谚语，以及场景二经典诗文，现在都能在本地实测；诗文、人物（U2 范围）仍只能靠代码审查 |

本次操作对模拟器数据的影响：
- 首轮：场景三实测时取消了"精锐之师"，再通过成语搜索重新收藏，收藏的条目和之前一样（该条 bookmark id 变为新时间戳）。
- 第二轮：新增收藏 歌词《时间情缘》、诗歌《幻象》、谜语"分房制度被取消 （五字口语）"、歇后语"织布机上的梭子"、谚语"四月八，苋莱掐，四乡人家把秧插。"、经典诗文《长恨歌》。《长恨歌》在测试中取消过一次，又通过 经典诗文→搜索→ShowPage 重新收藏。这些收藏保留着，后续实现阶段可直接用来验证。

### 7.1 配网后基线实测结果【运行实证】

| 验证点 | 操作 | 观察结果 | 对应验收项 |
| --- | --- | --- | --- |
| 新类型可在内容页收藏 | 歌词/诗歌/歇后语/谚语/经典诗文 IndexPage 点 toolbar 第 1 项；谜语 IndexPage 点第 2 项 | 6 处图标均变为实心；各模块自己的 `<X>BookmarkPage`（IndexPage 右上第 1 个菜单）都能列出刚收藏的条目 → `bookmarks` 表确有记录 | A2-A6、A10 |
| 收藏夹不展示新类型 | 主页→收藏图标 | 只显示 `经典诗文/长恨歌` 和 4 条成语；歌词/诗歌/谜语/歇后语/谚语 **全部缺失**。截图上缺失的 5 条在列表中表现为叠在一起的一条粗分割线（空 ListItem 高度为 0，divider 叠加）；uitest dump **不输出**这些空 ListItem（dump 只有 5 个 ListItem） | A2-A6、A8 |
| 经典诗文只有标题 | 同上 | 条目只有 `经典诗文` + `长恨歌`，**无作者**；详情页才有 `【唐】白居易`（ClassicPoemView 的显示格式） | A11 |
| 经典诗文条目跳转 | 点 `长恨歌` | 进入 ClassicPoemShowPage，标题 `经典诗文`，正文 `长恨歌 / 【唐】白居易 / …`，收藏图标实心 | A12 |
| 经典诗文取消后消失 | 详情页点收藏取消 → Back | 列表中 `长恨歌` 消失，成语 4 条不受影响 | A16 |
| ShowPage 路径可收藏 | 经典诗文→搜索"长恨歌"→ShowPage→收藏 | 收藏成功，返回收藏夹可见 | A10 / U8 |
| **排序不是最新在前** | 11:00 重新收藏《长恨歌》 | 《长恨歌》排在 `精锐之师`（更早收藏）**之后**；10:56 收藏的 5 条新类型（空 ListItem）排在最前。原因：10 点的 id 是 14 位数，11:0x 的 id 少了补零位只有 12–13 位，数值更小（§4.4） | A8 / U5 / U10 |
| 搜索结果 | 经典诗文搜"长恨歌" | FTS 返回多篇无关诗文，《长恨歌》在第 3 条（与本题无关，仅说明搜索路径可用） | — |

## 8. 测试可观测性风险

1. **入口无 id 无文字**：主页三个图标（`TopBar.ets:17-31`）只有 Image，无 `.id()`、无 text，测试只能按坐标或第 N 个 Image 找；收藏是三者中第 1 个。实现时可补 `.id()`，但官方脚本用什么选择器未知。
2. **收藏页条目无 id**：`IndexPage.ets:41-115` ListItem / Item 均无 `.id()`。
3. **同名文本歧义**：
   - 类型名 BlockTitle（"成语"、"歌词"…）在列表中每条都重复出现，且与主页网格文字、详情页标题同名。
   - 摘要文字与详情页正文相同（如"精锐之师"在列表和 IdiomShowPage 都有），按文本断言时要先确认当前页面（标题 `收藏夹` vs `成语`）。
   - 歇后语 `riddle` 字段名与谜语类型名英文同名，实现时别名要区分，避免 SQL 别名冲突。
4. **收藏按钮无文字**：toolbar `hideItemValue: true`，运行时 MenuItem 只有系统 id `__NavdestinationField__ToolBar__MenuItem1__`（谜语页收藏是 `MenuItem2`），文字 `添加收藏/取消收藏` 不出现在控件树 text 中【运行实证：dump 里 MenuItem text 为空】。
5. **页面标题**：Spec 写"收藏"页面，实际标题 `收藏夹`；按 EQUALS 匹配 "收藏" 会失败，按 CONTAINS 可通过。**另外各内容模块自己的 `<X>BookmarkPage` 标题同样是 `收藏夹`**【运行实证：歌词/诗歌/谜语/歇后语/谚语 的收藏子页 TitleBar 都是 `收藏夹`】，只看标题无法区分"主页收藏夹"和"模块收藏子页"，需结合类型名 BlockTitle 或补 id 区分。
6. **长文本**：摘要 `maxLines(2)` 省略显示；uitest dump 的 text 属性是全文【运行实证：成语释义长文本完整出现在 dump 中】，断言不受截断影响。
7. **刷新时机**：依赖 `navDestinationUpdate` state==4；如果测试在返回后立即断言，查询是异步的，可能需要等待【推断】。
8. **空 ListItem 不可见**：不支持的类型渲染成 0 高度 ListItem，uitest dump 中不出现【运行实证】，但截图上会叠成粗分割线。实现后这些类型变成可见条目；不支持的 model 应直接跳过，不要再生成空 ListItem。

