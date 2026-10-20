## cml-combo-search（商品搜索功能）

### 完成情况

- 状态：已提交工程（`submitted`）。构建成功，应用已安装到 arm64 模拟器并冷启动运行，本地 Hypium 自测 26 条用例全部通过（`tasks/cml-combo-search/logs/selftest.json`：26 pass、0 fail、0 skip）。
- 这是本地自测结果，不代表官方 F-point 通过情况；官方隐藏测试的判定方式未知。
- 实现范围（对照 `spec/requirement.md` 的四个场景：进入搜索页与搜索、点击历史/推荐词、清空历史确认、边界输入）：
  - 首页顶部搜索框点击进入商品搜索页（`HomePage.ets`、`HomeTopBar.ets`、`HomeViewModel.ets`）。
  - 搜索页（`GoodsSearchPage.ets`、`GoodsSearchViewModel.ets`）：进入即自动聚焦并弹出软键盘；"搜索历史"（最多 10 条，同词去重并置顶）与"推荐搜索"（服务端关键词）两个标签区；"搜索"按钮与键盘搜索键共用同一提交入口，去除首尾空格，空/纯空格不提交；历史标签与推荐标签点击即搜索；历史右侧垃圾桶图标触发确认框"确认清空所有搜索历史吗？"（取消/确认），确认后清空并隐藏历史区。
  - 结果页（`GoodsCategoryPage.ets`、`GoodsCategoryViewModel.ets`）：读取路由参数 `keyword`，按 `keyWord` 请求 `goods/info/page`，双列网格展示商品。
  - 数据层（`SearchHistoryEntity.ets`、`SearchHistoryLocalDataSourceImpl.ets`、`core/data/Index.ets`）：搜索历史持久化并导出 `SearchHistoryRepository`。
  - 资源：`feature/goods` 的 base / en 两份 `string.json` 各增 8 行文案（含"确认"的独立资源 key，因基线 `confirm` 编译后显示为"确定"）。
  - 自测脚本：`hypium_tests/` 下 6 个文件（4 个场景脚本 + helpers），为关键组件补了稳定的 `.id()`。

### 对基线的非显然改动（需如实披露）

- 基线的 `search_history` 表实际写不进数据（`@PrimaryKey` 把关键词字段固定成 INTEGER 导致插入报 `Data type mismatch`；`save()` 在主键有值时只做 UPDATE）。本题把实体改为自增 `id` + `keyword TEXT`，并把表名改成 `goods_search_history`（避免与设备上可能残留的旧结构表冲突）；写入改为"先删同名再插入"以实现去重置顶。这一改动不在验收矩阵 U1–U17 的决策里。
- 验收矩阵 U1–U17 共 17 项是 Spec 没有明文规定、由我方确定的做法（队员 2026-10-20 13:33 确认全部采用推荐方案），属于假设而非 Spec 明文。

### 未完成项与已知问题

以下 1–8 条来自实现会话 `b362b3f8` 末轮总结（AI 自述，Agent 未独立复核）：

1. 连点类用例证明不了"提交锁"本身有效：临时去掉提交锁和首页防连点后，三条连点用例仍通过（第一次点击已在后一次触摸前完成跳转），它们只能说明"连点后只有一个结果页"。
2. 首页防连点用 1 秒节流，与 U12 约定的"页面重新显示时才解锁"不同；搜索页按 U12 实现。
3. 改了基线实体和表名（见上）。
4. 结果页的空态与错误态分不开：`BaseNetWorkListView` 各层状态一直留在组件树里，空结果用例只能断言"没有商品卡片且页面有 `暂无数据`"。
5. 软键盘是否弹出，自测用 `hidumper` 窗口列表里的 `softKeyboard*` 判断；官方判定方式不明。
6. 键盘弹出时靠下的推荐标签点不到，需滚动后键盘才收起。
7. 模拟器网络不稳（自测期间 ping 延迟一度约 30 秒），网络相关用例前需确认首页能加载数据。
8. `common/test-harness` 的 `restart_app` 对本应用不可用（必须显式传 `EntryAbility`）。

队员补充的未完成项/已知问题（`spec/submit-input.yaml` 的 `known_issues`）：**【待补充】**（该文件不存在，未提供）。

### AI 参与环节

- 分析阶段（会话 `9fac2284-d547-4fc5-852e-bc2833089adb`）：读取需求与基线、探测模拟器 UI 与线上接口、重建基线并保留告警清单、产出 `spec/acceptance.md`（验收矩阵）与 `spec/baseline-notes.md`；队员在其中做了"采用全部推荐"的人工决策。
- 实现阶段（会话 `b362b3f8-b428-4220-b57b-989aab79ddb5`）：全部源码与资源改动、Hypium 自测脚本、构建/安装/自测与日志、已知问题整理。
- 构建与测试环境（模拟器、网络）的准备方式与操作人：**【待补充】**（会话记录只显示模拟器 `127.0.0.1:5555` 已在线，看不出由谁准备）。
- 人工改代码情况：**【待补充】**（`human_edits` 未提供；客观证据见 `trace-index.md`）。
- 记录索引：`tasks/cml-combo-search/trace-index.md`；原始记录：`traces/cml-combo-search/`。
