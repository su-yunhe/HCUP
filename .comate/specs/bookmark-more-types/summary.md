# 收藏夹支持更多内容类型 —— 完成总结

## 改动

| 文件 | 内容 |
| --- | --- |
| `commons/constants/src/main/ets/DbConst.ets` | `DbCRUDConst.BOOKMARKS` 重写：子查询按 `(model, bookmarkable_id)` 去重取 `max(id)`；新增 歌词/诗歌/谜语/歇后语/谚语/诗文/人物 7 张表 JOIN；经典诗文多取 `writer`；`where coalesce(tblN.id) is not null` 过滤孤儿与未知 model；`order by b.id desc` |
| `features/bookmark/src/main/ets/model/Bookmark.ets` | `addBookmark` 不再写入 `id`，主键走 autoincrement |
| `features/bookmark/src/main/ets/model/BookmarkEntity.ets` | 实体新增 11 个字段，`isColumnNull` 判空；新增 `BookmarkItem` / `toBookmarkItem`（15 类 → 类型名、摘要、副摘要、路由）；诗文 title JSON 解析失败时回退原串 |
| `features/bookmark/src/main/ets/pages/IndexPage.ets` | 单一分支渲染展示项，跳过未知 model；补 `.id()`：`bookmark_list`、`bookmark_item_<model>_<id>`、`_title`、`_content`/`_author` |
| `features/home/src/main/ets/view/TopBar.ets` | 三个图标补 `.id()`：`home_bookmark_entry` / `home_link_entry` / `home_settings_entry` |
| `hypium_tests/test_bookmark.py`（+ `__init__.py`） | 13 个 Hypium 用例 |
| `logs/` | `build.log`、`install.log`、`selftest.log`、`selftest.json` |

入口位置、页面标题 `收藏夹`、路由名和原有 8 类的展示文字都没有变。

## 验证

- 构建：clean 全量 `BUILD SUCCESSFUL`，ArkTS:WARN 36 条，和基线一样，改动文件没有产生新告警。
- 安装 / 冷启动：`install bundle successfully`，进入收藏页正常，没有崩溃。
- 自测：13 个用例中 12 个通过、1 个跳过、0 个失败（`logs/selftest.log`）。覆盖 A1 入口；歌词/诗歌/谜语/歇后语/谚语 收藏后排第一、摘要正确、能跳转详情、返回后条目仍在；混合顺序（最新在前）；经典诗文显示标题和作者且作者不含朝代，能跳转详情；成语 取消→再收藏→只有一条且排第一→再取消→消失，其他条目不受影响，重进后仍不存在；重启后收藏还在；连续点击后没有重复条目；没有空条目或 "null"。
- SQL 语义：在内存 SQLite 中按同样结构验证了去重、过滤孤儿和未知 model、谜语 puzzle 为 null 的行保留，以及显式插入大 id 后自增 id 接着往上排。设备日志里新收藏的 rowId 是 `20261015105741`，比库中旧 id 都大，所以排在最前。

## 已知问题与未覆盖项（交 2-submit 用）

1. **人物**：基线 People 的 IndexPage 和 ShowPage 收藏按钮都被注释掉了，用户没法收藏。0-analyze 阶段 BN §4.3 / 验收 A6 说人物"有收藏按钮"，这个说法不对。按 U2 原则"没有收藏按钮的类型不加"，没有启用这个按钮，也没写人物的 UI 用例。收藏页保留了人物的展示映射，库里如果有历史人物收藏还能正常显示。
2. **诗文**：模拟器没同步诗文数据（163 万条），`test_07_writing` 被跳过，只做了代码审查。
3. **查询层去重没有经过 UI 实测**：实测快速双击时，第二次点击前状态已经回读，结果是"收藏再取消"，不会插入重复行。去重只在 SQLite 里做了逻辑验证。
4. **空收藏（0 条）**：自动化会清空用户数据，所以没做。代码路径保持基线行为（空白列表）。
5. **谜语 puzzle 为 NULL**：这种条目只显示类型名，没有摘要。
6. **历史数据**：旧的时间戳 id 之间相对顺序还是不严格，新收藏一定排在所有旧数据之上，没有做数据迁移（acceptance A8 已说明）。
7. **harness 自带的 `restart_app` 不带 Ability 名，会失败**。测试文件里自己实现了 `restart_app`，显式传 `EntryAbility`。
8. 自测会改动模拟器上的收藏数据：新增若干收藏，取消一条成语。
