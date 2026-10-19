# solution 片段：sym-combo-customize

（供 `3-package.md` 汇总进 `solution.md`。事实来源：会话 B 的最终说明、`logs/selftest.json`、`spec/acceptance.md`。）

## 完成情况

- 状态：完成并提交（`submitted`）。构建成功，自测 27 条全部通过（pass 27，fail / skip 0）。官方评测为隐藏 Hypium 用例，实际通过率未知。
- 实现内容：
  - 场景四：`kmark_on_bookmark` 改为 `bookmark_on_bookmark`（`linysSymbol.ets:491`，并同步 `python_script/HMSymbolVF.txt:477`）。
  - 网格由 `Text` 改为 `SymbolGlyph`（`$r('sys.symbol.' + name)`），颜色列表与渲染策略以 `@Prop` 下发，滚动新出现项与搜索结果沿用当前设置。
  - 场景一至三：搜索行最右侧 '^'（`chevron_up`）展开 / 收起操作面板；主色、副色、背景色三组各 6 个系统色圆点与可复制的色名胶囊；颜色重置图标（只重置三种颜色）；`SegmentButton`（`SINGLE` / `MULTIPLE_COLOR` / `MULTIPLE_OPACITY`）与策略名胶囊。
  - 场景五、六：信息栏水平滚动在基线已具备，作为回归保护项保留，自测覆盖。
  - 为组件补充 `.id()`（清单见 `spec/acceptance.md` 第 4 节）。
- 自测：`hypium_tests/` 27 条（颜色选择 8、重置 4、信息栏 5、生命周期 3、渲染策略 4、符号名/搜索 3），运行结果 `logs/selftest.json`。自测用例为本队自写，非官方用例。

## 未完成项与已知问题

来自会话 B 最终说明（原文要点）：

1. 模拟器上 `warning` 与 `handup` 解析为同一颜色 `#E84026`，两个圆点外观相同（按已确认的 6 色板 U-3，未修改）。
2. 数据中 442 个名称不在系统符号表（如 `space`、`heart_gap`），这些格子在网格中为空白。
3. 网格项组件类型由 `Text` 变为 `SymbolGlyph`，按组件类型计数的测试结果会随之改变。
4. 与官方参考实现可能不一致的未确认假设（`spec/acceptance.md` 第 5 节 U-1 ~ U-16）：'^' 的形式与位置、胶囊显示短名、背景色作为 fontColor 第 3 项、段按钮用英文枚举名、色板具体取值等。证据等级均为 `UNCONFIRMED_ASSUMPTION`。
5. 背景色一行胶囊显示 `foreground` 时右边缘距重置图标约 30px；窄于 1308px 的屏幕与深色模式未测。
6. 选中圆点的内圈描边（U-16）只做视觉，无自测断言。
7. 技术验证（U-15）期间的临时探测页面 / 脚本已删除，不在包内；仅在会话记录中可见。
8. 未提交最终 git 提交，最终版本以工作树为准（见 `trace-index.md`）。
9. 工程含 `build-profile.json5` 的 `targetSdkVersion: "6.1.0(23)"` 改动：非本题功能，开发前即存在，来源未核实，经用户决定保留。

## AI 参与环节

- 会话 A（`3533c74c-e720-4295-b5c9-52f73239dd5d`）：阶段 0，基线实测与需求分析，产出 `spec/baseline-notes.md`、`spec/acceptance.md`，并按人工决策更新文档。
- 会话 B（`b069b19e-996e-4c07-bc76-8ee98441ff63`）：阶段 1，业务代码修改、自测用例编写、构建、安装、自测与修复。
- Agent / 模型：Comate Agent，`opus 5.5`（modelId `Opus 5.5_143_69ecd21d3a3e213032bd925cfe9637c5`，mode MAX，effort xhigh）；Comate 1.108.2，扩展 4.13.4。
- 人工环节：触发各阶段任务书；对 U 项决策（会话 A 第 2 轮）；其余人工操作与是否手工改码：【待补充】（`spec/submit-input.yaml` 未提供）。
- 记录索引：`tasks/sym-combo-customize/trace-index.md`；原始记录 `traces/sym-combo-customize/`。

## 成员分工

由 `team.yaml` 汇总于团队级；本题具体由谁操作哪个会话：【待补充】（会话记录不含操作者身份）。
