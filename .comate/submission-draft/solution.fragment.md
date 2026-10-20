# cml-spec24 方案汇总片段

团队 ID：HC2026-111；队名：Ghost_London；阶段：online。提交版本、成果冻结时间、联系人、成员姓名及人工分工均为【待补充】，依据 `../common/spec-harness/team.yaml` 空字段保留，不能用最后一次测试时间代替人工确认的成果冻结时间。

## 完成情况与实现位置

本题需求为商品分类页的搜索、分类和价格筛选、五种排序、双布局与分页。`workflow/development-result.json` 的状态为 `local_validation_complete`，仅表示 1-do 的本地开发和验证完成；未执行外部提交。

| 内容 | 当前实现与本地证据 |
| --- | --- |
| 进入、搜索及布局 | 首页/分类/搜索入口；可编辑搜索框、空白搜索拒绝；默认两列网格与单列列表往返，卡片显示商品主图、名称、价格；入口位于 `feature/main/`、`GoodsSearchViewModel.ets`，目标页位于 `feature/goods/src/main/ets/view/GoodsCategoryPage.ets` |
| 筛选 | 多组分类多选、高亮边框、价格草稿与确认、重置、遮罩/back 取消；根分类展开真实叶分类；非法及单边价格处理；实现位于目标 Page、`GoodsCategoryViewModel.ets` 与 `GoodsCategoryState.ets` |
| 排序 | 综合、价格升/降、销量升/降，选择后关闭菜单、更新标题并重新查询；综合查询省略排序字段 |
| 分页、刷新与并发 | 原生 Refresh + Grid/List；page1 替换、后续页追加、在途去重、同页重试、可信末页及短页终态；查询快照与 owner/version 隔离，旧 success/error/finally 不覆盖新查询，back/重入隔离 |
| 服务接入与恢复 | 沿原 GoodsRepository/RequestHelper 发送真实服务参数；首屏、刷新、追加和分类错误分支；真实 retry / emptyRefresh 控件可见且可点击 |

逐项映射为 `spec/acceptance-implementation.md`，A01–A76 实际结果为 `workflow/verification/development-status-v5.json`。价格 `(min,max]`、根分类展开、重置仅清可编辑分类和价格且保留关键词/外部 flags/排序等语义经过真实服务取证和需求裁决；不把这些边界冒称为 Spec 原句。

## 测试范围、失败与局限

最终验证依据 `workflow/verification/development-verification-v5.md`。本地 76 pass / 0 fail / 0 blocked / 0 not_run 含明文原子项和推导/裁决边界，不能等同官方 F-point 数量或得分。

| 证据 | 实际范围与结果 |
| --- | --- |
| 正常设备套件 | 最终 x86_64 API23 独立模拟器、正常 main HAP、真实服务，12 pass / 0 fail / 0 skip、exit 0；`logs/development/normal-final-v1/` |
| 原生受控套件 | 同一 v4 源码和双包的两轮有效方法记录合计 9/9；首轮 C01–C06 pass、C07 宿主输入前置失败且 exit 1、C08/C09 未执行；第二轮 C07–C09 pass、exit 0。保留 `logs/development/controlled-run-v1/`、`controlled-run-v2/` 和 `controlled-current-v4.json`，不声称单轮九例 exit 0 |
| 宿主补充 | 原 VM/Repository/RequestHelper 转译，外部 datasource/装饰器/Toast 替身，14 pass / 0 fail；`logs/development/state-v4/`；不等同 ArkTS 编译、原生 UI 或真实网络错误 |
| 构建 | default/emulator 最终独立增量构建 exit 0；ohosTest 沿已实际构建、安装并受控验证的同一包；原 `No signingConfig` 告警保留，未宣称 clean build |
| 商品及网络取证 | 完整可见卡 437 项比较 pass、51 唯一商品；58 组实际 App 请求/响应，其中 13 组响应 JSON 完整、45 组截断；58 份独立即时 oracle 始终分开保存。另有 32 次只读服务探测和 26 项服务契约断言 |
| 历史继承 | v2 的完整 Q 设备补测属于历史证据，未在最终轮重跑；最终报告按源码影响范围说明继承依据，不冒充本轮新结果 |

失败和修复记录保留：v1 原 RefreshLayout 真实触发同次 UP 后 P2 再 P1，后改 native Refresh；v2 固定手势长 DOWN 越顶为测试前置问题，修正手势后重测；v3 错误态 retry 越界为生产布局缺陷，v4 限制 Empty 剩余空间后实际点击恢复通过；v4 首轮 C07 输入仍 X、Y 前置未建立，修测试宿主输入观测后仅重跑 C07–C09，生产未改。报告还保留服务探测首次因环境变量错误退出 1，以及 ABI 诊断阶段的安装失败，不只保留成功日志。

实际局限：仅 x86_64 模拟器运行；default 包保留原 arm64 库，但 arm64 真机与原生支付等能力未测。受控错误/延迟/乱序是外部 Promise 控制，未实测物理断网、HTTP 超时或生产服务器乱序。CDN 全量下载、所有图片像素对比和官方隐藏测试未完成。自动审核曾拒绝递归删除 Python 缓存，真实缓存保留并用 `hypium_tests/.gitignore` 排除生成字节码。

用户填写的未完成项与已知问题 `spec/submit-input.yaml:known_issues`：**【待补充】**。上述已知技术边界仍保留，不能将空字段解释为“无已知问题”。

## AI 四角色参与与人机分工

本题按主 Agent 调度的需求、方案、编码、自测四角色推进；配置快照保存在 `system-config/analysis-20261019T031827Z/` 与 `system-config/development-20261019T041612Z/`，manifest 记录实际文件摘要。该配置存在本身不替代原始会话证据；会话和工具调用对应关系由本题 `trace-index.md` 关联。

| AI 角色 | 参与用途与现有本题交接 |
| --- | --- |
| 需求 | 拆解验收、裁决服务边界、复审最终证据；`workflow/requirements/acceptance-v1.md`、`development-review-v2.md`、`final-evidence-review-v2.md` |
| 方案 | 页面/状态/请求隔离设计、ABI 双目标与受控验证安排、实现审计；`workflow/design/development-plan-v3.md`、`device-fixture-feasibility-v1.md`、`implementation-audit-v3.md` |
| 编码 | 商品分类页及相关入口实现、真实构建、按失败证据修复与交接；`workflow/implementation/development-handoff-v1.md` 至 `development-handoff-v4.md`，保留各版源码/产物/告警摘要 |
| 独立自测 | 真实服务契约、冻结后双包/设备/host 验证、失败与重测、证据归档；`workflow/verification/development-verification-v5.md`、`DEVICE_TESTS.md` 及其原始 logs；实际自测会话 ID `01a1525d-74e1-7c63-9036-70f1490169f9` |

当前材料子会话实际 `CODEX_THREAD_ID` 为 `01a152ef-e16d-77d3-8237-b522d7e8dcfd`，只生成三个提交片段和本角色材料交接，不修改生产源码/资源/配置，不构成新的功能测试。

- 人工直接改代码及其操作人/目的/文件/前后标识/原始证据：**【待补充】**（`human_edits` 为空，不填写“无人工直接修改代码”）。
- 团队成员姓名、具体人工贡献、AI 指导及人工操作：**【待补充】**。
- 额外来源用户确认：**【待补充】**；已发现来源与检索疑点见 `sources.fragment.md`。
- 用户 Markdown 导出目录：**【待补充】**；原生记录导出与缺失说明以主 Agent 的记录索引为准。
- 团队级 `source_guard`：**【待补充】**。已生效题目录指令、实际范围控制及过宽搜索行为均须据原始轨迹披露，不能将字段空白替换成来源保护完全满足声明。

最终源码摘要引用：`workflow/final-code-fingerprint-v2.json` SHA-256 `7587e6980c87ddc4fb5971c4e080da0f1a00d4f432b2b85844913075961b74f2`；设备测试冻结 `workflow/verification-freeze-v4.json` SHA-256 `a93ebf579fbb5a9ec957f056b1b7bda3fb92f077c258abbdd67af94d207219d4`。最终报告记录被测 895 文件未变；测试后仅 `hypium_tests/.gitignore` 排除生成字节码。本材料以这些既有证据说明范围，不重新声明独立验收通过。

## 本轮材料校验的失败与调整

初次日志复制全量复核发现宿主模拟器 Log/ 下5个源文件与2个副本摘要不符；首次补丁生成也在 crash_server.log 检出复制时变化，未得到有效补丁。失败证据在 checks/log-freeze-failure-01.json 与独立报告F01。随后把精确宿主运行缓存目录排除，保留主动捕获的设备测试日志、截图、HAP及所有历史失败，再重新校验；这不代表生产代码回归。

首次普通本地 clone 面对共享 worktree，其行政对象复制范围可能包含共享对象；未把这些对象作为实现资料读取。本轮改用 --no-local --depth 1 --single-branch --no-tags 请求本题基线可达对象。首次尝试与终止/失败事实保留在 checks/clone-attempt-01.json 和原生工具调用，临时目录排除，不据此代作来源保护合规判断。

完整普通文本/二进制差异首次为1,294,184,961字节，git apply --check --binary 返回128及 patch too large；失败记录在 checks/patch-size-failure-01.json。最终同一完整文件集改用Git压缩二进制补丁表示文本/日志，临时属性仅在镜像.git/info/attributes，未改原工程字节。changes/source-review.diff 另供人读源码/测试/配置差异并忽略纯CR变化，它不是完整交付补丁替代。最终应用不依赖临时属性，仍须逐文件与树模式核验。
