# 收藏夹支持更多内容类型（bookmark-more-types）

依据：`spec/requirement.md`、`spec/acceptance.md`（A1–A16，U1–U10 已确认）、`spec/baseline-notes.md`（BN）。
网络维度不适用：收藏全部走本地 RDB `bookmarks` 表。

## 1. 需求与处理逻辑

| 需求 | 处理逻辑 | 对应验收 |
| --- | --- | --- |
| R1 收藏夹展示 歌词/诗歌/谜语/歇后语 + 谚语/诗文/人物 | SQL 多 JOIN 7 张内容表；页面按 model 映射 类型名 + 摘要 + 详情路由 | A2–A6、A9 |
| R2 经典诗文条目展示标题 + 作者 | SQL 多取 `tbl7.writer`；条目第二个 Text = writer | A10–A12 |
| R3 取消收藏后条目消失 | 基线已满足（state==4 重新查询），保持并对所有新类型生效 | A13–A16 |
| R4 列表无空条目、去重、最新在前 | 子查询 `group by (model, bookmarkable_id)` 取 `max(id)`；过滤 JOIN 不到内容的行；`order by id desc`；插入改为自增主键 | A8、U5、U9、U10 |
| R5 稳定选择器 | 主页收藏图标、收藏列表、条目及摘要 Text 加 `.id()` | 选择器汇总表 |

入口、标题文字（`收藏夹`）、路由名、已有 8 类的展示与跳转全部保持基线不变（U1、A7）。

## 2. 架构与技术方案

沿用基线结构：`HomePage → TopBar 第 1 个图标 → BookmarkIndexPage`，收藏页在 `navDestinationUpdate state==4` 时调 `getEntities()`，数据只来自 SQL 结果。bookmark 模块不能依赖内容模块（会循环依赖），所以继续在 SQL 层 JOIN 内容表取摘要字段。

页面渲染从"15 个 if/else 分支"改为"实体 → 展示项"映射：`toBookmarkItem(entity)` 返回 `{类型名 Resource, 摘要, 副摘要, 路由名}`，不支持的 model 返回 `undefined` 并被过滤，因此不再生成空 ListItem。路由名、参数（`new ParamNumberId(bookmarkable_id)`）与基线逐一相同。

## 3. 受影响文件

| 文件 | 修改 | 涉及函数/常量 |
| --- | --- | --- |
| `/Users/bress/Documents/code/harmonycup-work/jm-spec7/commons/constants/src/main/ets/DbConst.ets` | 修改 | `DbCRUDConst.BOOKMARKS` |
| `/Users/bress/Documents/code/harmonycup-work/jm-spec7/features/bookmark/src/main/ets/model/BookmarkEntity.ets` | 修改 | `BookmarkEntity`、`getEntities`；新增 `BookmarkItem`、`toBookmarkItem` |
| `/Users/bress/Documents/code/harmonycup-work/jm-spec7/features/bookmark/src/main/ets/model/Bookmark.ets` | 修改 | `addBookmark`（不再写 id） |
| `/Users/bress/Documents/code/harmonycup-work/jm-spec7/features/bookmark/src/main/ets/pages/IndexPage.ets` | 修改 | `IndexPage.build`、`Item` |
| `/Users/bress/Documents/code/harmonycup-work/jm-spec7/features/home/src/main/ets/view/TopBar.ets` | 修改 | `CustomMenuItem` 增加 `itemId` |
| `/Users/bress/Documents/code/harmonycup-work/jm-spec7/hypium_tests/test_bookmark.py` | 新增 | Hypium 自测 |
| `/Users/bress/Documents/code/harmonycup-work/jm-spec7/logs/*.log` | 新增 | 构建/安装/自测日志 |

各内容模块（ViewModel、ShowPage、IndexPage）不改：`new Bookmark(YmdHisToNumber(), ...)` 调用签名保留，只是 id 不再写入数据库。

## 4. 实现细节

### 4.1 SQL：`DbCRUDConst.BOOKMARKS`

```sql
select b.id, b.bookmarkable_id, b.bookmarkable_model,
  tbl1.body as chinese_antitheticalcouplet, tbl2.character as chinese_character,
  tbl3.word as chinese_expression, tbl4.word as chinese_idiom,
  tbl5.content as chinese_knowledge, tbl6.content as chinese_quote,
  tbl7.title as classicalliterature_classicpoem, tbl7.writer as classicalliterature_classicpoem_writer,
  tbl8.content as classicalliterature_sentence,
  tbl9.title as chinese_lyric, tbl9.content as chinese_lyric_content,
  tbl10.title as chinese_modernpoetry, tbl10.content as chinese_modernpoetry_content,
  tbl11.puzzle as chinese_riddle,
  tbl12.riddle as chinese_wisecrack,
  tbl13.content as chinese_proverb,
  tbl14.title as classicalliterature_writing, tbl14.author as classicalliterature_writing_author,
  tbl15.name as classicalliterature_people
from (select max(id) as id, bookmarkable_id, bookmarkable_model from bookmarks
      group by bookmarkable_model, bookmarkable_id) as b
left join chinese_antitheticalcouplet as tbl1 on b.bookmarkable_id = tbl1.id and b.bookmarkable_model = 'chinese_antitheticalcouplet'
... (tbl2–tbl15 同样写法，model 取 PrefConst 常量)
where coalesce(tbl1.id, tbl2.id, ..., tbl15.id) is not null
order by b.id desc
```

- 去重（U9）：子查询按 `(model, bookmarkable_id)` 分组，`max(id)` 作为该组 id 与排序键。
- 孤儿/未知 model 过滤：所有 JOIN 都没命中的行被 `where` 排除；用 `tblN.id` 判断，避免谜语 `puzzle` 为 null 时被误过滤。
- 歇后语 `riddle` 列统一用别名 `chinese_wisecrack`，不与谜语混用（BN §8）。
- 15 张内容表都在 `DbUtil` 迁移中创建（已核对 `DbUtil.ets:57/106/184/190` 等），不会因表不存在导致整条查询失败。

### 4.2 `BookmarkEntity` 与展示项

- `BookmarkEntity` 字段改为带默认值 `null` 的声明，构造函数只收 `id/bookmarkable_id/bookmarkable_model`，其余字段在 `getEntities` 中逐个赋值，新增 11 个字段（见 SQL 别名）。
- 读列使用 `isColumnNull` 判空，空列得到 `null`，界面不会出现 "null"。
- 新增：

```ts
export class BookmarkItem {
  key: string; id: string;            // id = `bookmark_item_${model}_${bookmarkable_id}`
  title: Resource;                    // 类型名，如 String.chinese_lyric
  content: string | null;             // 第一个摘要 Text
  sub: string | null;                 // 第二个摘要 Text（可空）
  subSuffix: string;                  // 'content' | 'author'
  route: string;                      // 如 'LyricShowPage'
  bookmarkable_id: number;
}
export function toBookmarkItem(e: BookmarkEntity): BookmarkItem | undefined
```

映射表（摘要字段表落地）：

| model | title | content | sub (suffix) | route |
| --- | --- | --- | --- | --- |
| chinese_antitheticalcouplet | 对联 | body | — | AntitheticalCoupletShowPage |
| chinese_character | 汉字 | character | — | CharacterShowPage |
| chinese_expression | 词语 | word | — | ExpressionShowPage |
| chinese_idiom | 成语 | word | — | IdiomShowPage |
| chinese_knowledge | 知识卡片 | content | — | KnowledgeShowPage |
| chinese_quote | 句子 | content | — | QuoteShowPage |
| classicalliterature_classicpoem | 经典诗文 | title | writer (author) | ClassicPoemShowPage |
| classicalliterature_sentence | 诗文名句 | content | — | SentenceShowPage |
| chinese_lyric | 歌词 | title | content (content) | LyricShowPage |
| chinese_modernpoetry | 诗歌 | title | content (content) | ModernPoetryShowPage |
| chinese_riddle | 谜语 | puzzle | — | RiddleShowPage |
| chinese_wisecrack | 歇后语 | riddle | — | WisecrackShowPage |
| chinese_proverb | 谚语 | content | — | ProverbShowPage |
| classicalliterature_writing | 诗文 | JSON.parse(title).Content，失败回退原串 | author (author) | WritingShowPage |
| classicalliterature_people | 人物 | name | — | PeopleShowPage |
| 其他 | — | — | — | 返回 undefined，不渲染 |

诗文标题解析在 bookmark 模块内定义最小类 `WritingTitle { Content: string }`，`try { JSON.parse(raw) as WritingTitle } catch { raw }`，不 import writing 模块。

### 4.3 `Bookmark.ets`：`addBookmark`

valuesBucket 去掉 `'id'`，主键走 `autoincrement`。SQLite 的 autoincrement 取 `sqlite_sequence` 中的历史最大值 +1，库中已有的时间戳 id（最大 14 位）会被计入，所以新 id 恒大于旧数据，新收藏恒排第一（U5/U10）。`Bookmark` 类、`cancelBookmark`、`getBookmark` 不变。

### 4.4 `IndexPage.ets`

```ts
@Local items: BookmarkItem[] = [];
// state==4 时：
getEntities().then((value) => {
  this.items = value.map(toBookmarkItem).filter(...) as BookmarkItem[];
})

List() {
  Repeat<BookmarkItem>(this.items)
    .each((ri) => {
      ListItem() {
        Item({ item: ri.item })
          .onClick(() => this.pageStack.pushPathByName(ri.item.route, new ParamNumberId(ri.item.bookmarkable_id)))
      }
    })
    .key((item) => item.key)
}
.id('bookmark_list')
```

`Item`：`BlockTitle({ title })` + `Text(content).id(`${id}_title`)`（content 为空不渲染）+ 可选 `Text(sub).id(`${id}_${subSuffix}`)`（fontSize 14，`maxLines(2)`）；Column `.id(id)`。样式（padding、stateStyles、maxLines/ellipsis）沿用基线。

### 4.5 `TopBar.ets`

`CustomMenuItem` 增加 `@Param itemId: string = ''`，Stack 上 `.id(this.itemId)`；三个图标分别传 `home_bookmark_entry` / `home_link_entry` / `home_settings_entry`。位置、图标、点击行为不变。

## 5. 数据流

```
内容页 点收藏 → ViewModel.addBookmark → INSERT bookmarks(bookmarkable_id, model)（id 自增）→ getBookmark 回读 → 图标实心
内容页 取消   → cancelBookmark(id, model) 删除全部匹配行 → 图标空心
收藏页 显示(state==4) → getEntities → BOOKMARKS SQL(去重/过滤/排序) → BookmarkEntity[] → toBookmarkItem → items 整体替换 → 列表重绘
收藏页 点条目 → pushPathByName(route, ParamNumberId(bookmarkable_id)) → ShowPage onReady 按 id 查库
```

## 6. 边界与异常

| 场景 | 处理 |
| --- | --- |
| 0 条收藏 | 列表空白，不加文案（U6） |
| 可空字段（谜语 puzzle、经典诗文 writer、诗文 author 等） | `isColumnNull` → null → 不渲染该 Text |
| 诗文 title 非法 JSON | 回退原串 |
| 孤儿收藏、未知 model | SQL `where` 过滤 + `toBookmarkItem` 返回 undefined 双重保证，不出空 ListItem |
| 快速连点收藏按钮插入重复行 | 查询层去重只显示一条；取消时删除全部重复行 |
| 同秒收藏两条 | 自增主键不再碰撞覆盖 |
| 取消后再收藏 | 新 id 更大，回到第一位 |
| 查询失败 | 基线行为：日志 + 空数组，不崩溃 |
| 返回 / 重进 / 重启 | 每次 state==4 重新查询；RDB 持久化 |
| 空输入、纯空格 | 不适用（无输入框） |

## 7. 自测方案（`hypium_tests/test_bookmark.py`）

继承 `harness.driver.HarnessTestCase`，从题包根目录以 `PYTHONPATH=test-harness .venv/bin/python -m harness.runner --project <本工程>` 运行。用例：

1. 入口：冷启动 → 点 `home_bookmark_entry` → 标题 `收藏夹`、`bookmark_list` 存在 → Back 回主页（A1）。
2. 场景一：歌词/诗歌/谜语/歇后语/谚语逐个在 IndexPage 点收藏（谜语点 MenuItem2）。用该类型条目数变化判断是否收藏成功（随机条目若已收藏会被取消，则重进再点）；断言新条目为列表第 1 条、类型名与摘要 Text 存在且非空、不含 "null"；点条目进详情，详情标题为类型名且摘要文字出现（A2–A5、A6 谚语、A8、A9）。
3. 场景二：经典诗文 IndexPage 收藏 → 条目有 `_title` 与 `_author` 两个 Text，作者不含 `·`/`【` → 点击进 `经典诗文` 详情，标题文字一致（A10–A12）。
4. 场景三：收藏页取一条成语（无则先收藏）→ 进详情取消 → 再收藏 → 返回：条目仅一条且排第一（A16）→ 再进详情取消 → 返回：条目消失，其他条目仍在（A13–A15）。
5. 重启持久化：收藏一条后 `restart_app` → 重进收藏页条目仍在。
6. 连续点击：收藏按钮快速双击后进入收藏页，所有条目 id 无重复。
7. 无空条目：收藏页所有 `bookmark_item_*` 条目都有非空 `_title`。

诗文、人物模拟器无数据（BN §7），对应用例用 `require_precondition` 记为 skip，只做代码审查，交付时列为未覆盖项。空收藏场景会清空用户数据，不做自动化，列为未覆盖项。

## 8. 构建与交付

- 构建命令见 BN §2（DevEco JBR），日志写 `logs/build.log`，与基线 36 条 ArkTS:WARN 对比，不新增告警。
- `hdc install -r` 安装，日志 `logs/install.log`；自测报告 `logs/selftest.json`、`logs/selftest.log`。
- 交付前 `git checkout` 还原 `BuildProfile.ets` 噪声。

## 9. 预期结果

- 收藏页展示 15 类收藏，每条为 类型名 + 摘要；新增 7 类可点击进入对应详情。
- 经典诗文条目显示标题和作者（独立 Text，作者 = writer）。
- 列表无空条目、无重复、新收藏在第一位；取消收藏后返回即消失。
- 主页入口、标题 `收藏夹`、已有类型行为不回归。
