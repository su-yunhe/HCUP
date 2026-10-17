# solution 片段：jm-spec7

> 供 `3-package.md` 汇总进 `solution.md`。事实来自 `logs/`、`spec/` 与 `.comate/specs/bookmark-more-types/summary.md`；
> 留空项为 `【待补充】`。详细过程索引见 `tasks/jm-spec7/trace-index.md`。

## 本题完成情况

- 题目：`jm-spec7`，需求「收藏夹支持更多内容类型」（`spec/requirement.md`）。
- 状态：功能已实现，构建、安装、冷启动成功；自测 13 个用例，12 通过、0 失败、1 跳过（`logs/selftest.json`）。
  跳过的是 `test_07_writing`（诗文），原因是模拟器没有诗文数据，该类型只做了代码审查，**不能视为通过**。
- 官方隐藏测试的结果无法得知，本片段不对线上得分做任何判断。
- 在 `submission.json` 中应标记为 `submitted` 还是 `not_completed`，取决于 `team.yaml` 的 `submitted_tasks`，该字段为空，片段里留 `【待补充】`。

### 实现概述（来自改动文件）

| 文件 | 内容 |
| --- | --- |
| `commons/constants/src/main/ets/DbConst.ets` | 重写收藏列表 SQL：按 `(model, bookmarkable_id)` 去重取最新，新增 歌词／诗歌／谜语／歇后语／谚语／诗文／人物 的表连接，过滤孤儿和未知 model，按收藏 id 倒序 |
| `features/bookmark/src/main/ets/model/Bookmark.ets` | 新增收藏不再写入 `id`，改走自增主键 |
| `features/bookmark/src/main/ets/model/BookmarkEntity.ets` | 实体新增字段；新增展示项转换（类型名、摘要、副摘要、路由）；诗文标题 JSON 解析失败时回退原串 |
| `features/bookmark/src/main/ets/pages/IndexPage.ets` | 单一分支渲染展示项，跳过未知 model，并补稳定 `.id()` |
| `features/home/src/main/ets/view/TopBar.ets` | 三个入口图标补 `.id()` |
| `hypium_tests/test_bookmark.py`（+`__init__.py`） | 13 个 Hypium 自测用例 |

## 未完成项与已知问题

团队在 `spec/submit-input.yaml` 的 `known_issues` 里没有填写，下面是 S2 在 `summary.md` 中自己列出的，**请团队确认或改写**：

1. 人物：基线的人物列表页和详情页收藏按钮被注释，用户无法收藏；未启用该按钮，也没写人物的 UI 用例（曾写过 `test_08_people`，失败后删除）。收藏页保留了人物的展示映射。
   `summary.md` 称 0-analyze 阶段对人物「有收藏按钮」的判断不对；但 `spec/acceptance.md`（U2、A6）仍把人物列在 U2 范围内，两份文档未统一，实现按 `summary.md` 的取舍。
2. 诗文：模拟器没有同步诗文数据（约 163 万条），`test_07_writing` 被跳过，只做了代码审查。
3. 查询层去重没有经过 UI 实测：快速双击时第二次点击前状态已回读，结果是「收藏再取消」，没有触发重复插入；去重仅在内存 SQLite 里做了逻辑验证。
4. 空收藏（0 条）没测：自动化会清空用户数据。代码路径保持基线行为（空白列表）。
5. 谜语 `puzzle` 为 NULL 的条目只显示类型名，没有摘要。
6. 历史数据：旧的时间戳式 id 之间的相对顺序仍不严格；新收藏一定排在旧数据之上，未做数据迁移。
7. harness 自带的 `restart_app` 不带 Ability 名会失败，测试文件里自行实现并显式传 `EntryAbility`。
8. 自测会修改模拟器上的收藏数据（新增若干收藏，取消一条成语）。

另有两项是整理材料时发现的，不在 `summary.md` 里：

9. `final.diff` 含 29 个 `BuildProfile.ets` 的 debug 构建噪声（来自提交 `64ee6ee`，不是本题会话写入）；`2-submit.md` 要求不含构建噪声，待团队决定是否还原，见 `trace-index.md`。
10. 官方基线准备记录 `reports/build-baselines/jm-spec7.log` 未找到；会话外人工修改说明、`extra_sources` 声明仍 `【待补充】`。

## AI 参与环节（本题）

- 工具与模型：Comate「Spec」智能体，模型 opus 5.5（effort high）。两个纳入的会话：
  - 分析会话 `aedc580f-d83d-4bd4-809a-64b398e1b786`（侧边栏 ID `1791984936543-ejf6y3cpdw5`）：读 Spec、勘察基线、跑基线构建与模拟器取证，产出验收矩阵和基线理解文档。
  - 实现会话 `f36c5de2-69f2-49a2-8bd3-9cfd22747bf0`（侧边栏 ID `1792034578870-motddituhaj`）：生成设计与任务拆分，修改 5 个业务源文件，编写并运行 Hypium 自测，构建、安装、修复，写完成总结。
- 人工环节：会话内的人工输入包括对歧义 U1–U3 的澄清、「继续生成 tasks.md」「确认并执行所有任务」的确认、对 harness 访问范围的选择、两次要求提交 commit。
  会话外的人工操作 `【待补充】`。
- 成员分工（`team.yaml` 的 `members`，团队声明，未按题拆分）：赵琳慧——需求分析与方案设计；苏云鹤——AI指导与代码编写；罗智文——测试与验收。
  本题具体由谁做了哪一步，记录里只有会话内的人工输入，没有署名；如需按题写分工请团队补充。
- 成果冻结时间：2026-10-17 20:47（北京时间，本题整理时取得；`3-package.md` 打包时统一）。
- 来源保护（`team.yaml` 的 `source_guard`，团队声明）：任务书「禁止事项」约束 Agent；来源项目仓库地址及镜像加入屏蔽列表；每题独立工作目录与独立 git 分支，会话只在本题目录启动；队员人工审查会话中的检索与访问记录。
  配置位置：`system-config/spec-harness/` 与 `system-config/history/<题目ID>/`。我只能核实任务书文字和会话工作区路径，屏蔽列表与人工审查的证据不在本题材料内，见 `trace-index.md`。
  会话记录中对题包目录的访问仅限 `test-harness`，经用户同意，同样见 `trace-index.md`。
