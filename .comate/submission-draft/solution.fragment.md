# jm-spec71 方案片段（供汇总进 `solution.md`）

索引路径：`tasks/jm-spec71/trace-index.md`。本片段中的完成情况只依据开发会话记录和工程文件；本阶段没有构建、安装或运行自测，所以下面的「通过」都是会话当时的结果，不是整理时的复验。

## 本题完成情况

- 题目：`jm-spec71`，需求「完成成语模块首屏随机展示功能」，共 4 个场景（`spec/requirement.md`）。
- 开发会话的最终说明称 4 个场景均已实现：
  - 场景一：首屏随机展示成语名称、拼音、解释，刷新、返回重进、重启后换一条（排除上次展示的 id）。
  - 场景二：首页收藏、详情页（出处、例句）、返回后收藏状态保持，收藏夹可见并可取消。
  - 场景三：搜索页，输入「一石二鸟」等关键字返回匹配列表。
  - 场景四：详情页近义词/反义词标签，词库中存在的词可链式跳转到该成语的详情页。
- 为让以上场景在无网络、未同步时也有数据，新增了 `IdiomSeeder` 与内置种子数据（49,639 条），来源见 `sources.fragment.md`。
- 代码范围：成语模块 `features/chinese/idiom`，首页入口与顶栏收藏夹入口 `features/home`，收藏夹页面与路由键名修正 `features/bookmark`，公共常量与数据库/偏好工具 `commons/*`，应用入口 `products/default`，自测脚本 `hypium_tests/test_idiom_module.py`。全部差异见 `changes/final.diff`。
- 会话记录的验证结果（2026-10-14，模拟器 127.0.0.1:5555）：`hvigorw assembleHap` BUILD SUCCESSFUL；`test_idiom_module.py` 5 个用例全部 OK（消息 7 / 元素 125）。该次自测用的是题包 `test-harness`；之后 `b566e7b` 把脚本改为引用 `common/test-harness`，没有找到改动后的运行记录。

## 未完成项与已知问题

- 团队填写的未完成项与已知问题（`submit-input.yaml` 的 `known_issues`）：【待补充】，用户未提供。
- 从记录中能核实的情况（不代表团队的结论）：
  - `logs/` 缺失，现行任务书要求的构建、安装、自测日志不存在；需要补跑后才能给出可复核的通过证据。
  - 没有 `spec/acceptance.md` 与 `spec/baseline-notes.md`，现行 `1-do.md` 的验收矩阵前置没有产物。
  - HAP 因内置数据约 24 MB（`default-default-unsigned.hap` 为 24,422,562 字节，2026-10-14 16:30 构建，早于 `1ede197` 与 `b566e7b`，不能确认它对应最终版本）。会话提出过约 1.5 万条子集（约 8.9 MB）的备选方案，未采用，代价是冷门成语搜索可能落空。
  - 工程中提交了 5 个构建生成的 `BuildProfile.ets`，见 `trace-index.md`。
  - 会话 `summary.md` 里还列有设计取舍（例如词库中不存在的近反义词置灰并 Toast），完整内容在 `.comate/specs/idiom-random-home/summary.md`。

## AI 参与环节

按会话 `a511b975-8bff-46d6-acd1-512909a75a03`（Comate「Spec」Agent，模型 opus 5.5 → Opus 5）：

- 需求与基线探索：读需求，委派 `Explore` 子代理梳理 idiom、bookmark、home 等模块，产出设计文档 `.comate/specs/idiom-random-home/doc.md` 与任务清单 `tasks.md`。
- 方案决策：发现基线 `chinese_idiom` 表初始为空，评估内置种子数据方案及体量取舍。
- 编码：路由、数据访问层、`IdiomSeeder`、首页/详情/搜索/收藏夹页面、共享组件。
- 构建与调试：运行 `ohpm install`、`hvigorw assembleHap`，修复 ArkTS 编译错误。
- 测试：编写 `hypium_tests/test_idiom_module.py`，运行、定位并修复失败用例，包括 5 次失败后重跑。
- 提交：按用户要求整理暂存区并创建提交 `1ede197`。
- 材料整理（本阶段）：由 `2-submit.md` 任务驱动的会话不在会话表内，未纳入记录范围。

## 人工参与与成员分工

- 团队成员及分工（`team.yaml`）：赵琳慧——需求分析与方案设计；苏云鹤——AI 指导与代码编写；罗智文——测试与验收。
- 这三位成员各自在本题具体做了什么、哪一位发出了会话中的 6 条提示、会话外 4 个提交由谁完成：【待补充】，记录中没有可核实的信息。
- 人工直接修改代码的情况：【待补充】（见 `trace-index.md`）。

## 来源保护措施（本题运行情况）

- 工作目录为独立目录 `harmonycup-work/jm-spec71`，自 `base_commit` 检出。
- `team.yaml` 对来源保护措施的描述与本题开发会话的记录不完全一致：开发会话使用的 `do-v1.md` 没有「禁止事项」，并指示读取题包文件，会话访问了题包 `specs/`、`metadata/`、`examples/`（含另一题 `jm-spec7`）、`test-harness/` 等目录，详见 `sources.fragment.md`。汇总进 `solution.md` 时请你据实改写这一段，不要沿用与记录相反的表述。
