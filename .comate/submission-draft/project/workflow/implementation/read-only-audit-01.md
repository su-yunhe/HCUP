# vg-spec8 只读实现审计 01

## 范围与身份

- 本轮仅执行主 Agent 指定的静态审计，唯一写入本文件；没有实施、修复、构建、依赖安装、网络调用或设备操作。没有修改生产、测试、全局 state/events 或其他角色文档，不以本审计替代独立运行验收。
- 根目录为 `D:/HCUP/vg-spec8`；仅核查本题指定源码、Spec 和分析记录，另读取授权 ArkTS 技能配置。未读取其他题、来源工程、上游修复历史、Issue、PR、补丁、副本、总览会话或 agent-system 历史。
- 实读 `HEAD=9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`，与 `spec/metadata.json:2` 一致。
- 原生子会话：`CODEX_THREAD_ID=01a144f2-adb3-7f82-b090-505bdb99a517`。`CODEX_SESSION_ID=01a144eb-32eb-7cb3-b4d6-daea0ae599b7` 是环境原值，不能作为独立子会话 UUID。

## 可直接汇编的短结论

| 结论 | 核对证据与限制 |
| --- | --- |
| 基线缺少请求前第一层确认与明确「继续」授权门槛。 | `SettingsSyncSection.ets:507-516` 点击恢复，`:164-165` 直接进入包装器，`:199-200` 开始下载，`:206` 预览，`:215-220` 才显示「取消／确认恢复」。`spec/requirement.md:7`、`:33`、`:40` 指向第一层取消和继续前零请求，不能用此后置弹窗替代。 |
| 提前下载具有真实请求路径，不能把 `false` 解释为不联网。 | `WebDavSyncManager.ets:471` 参数名为 `force`，`:472-484` 是本地配置检查、preflight、备份下载；`WebDavBackupManager.ets:78-101` 在 `!force` 分支 HEAD，随后可 GET；`WebDavClient.ets:146` 调用 `request.request`。这是静态路径证据，真实请求数量和可达分支尚未运行验证。 |
| 已有预览取消具备返回和 busy 复位路径，无证据认定 Promise 悬挂。 | `SettingsSyncSection.ets:224-226` index 0 返回 `ok('已取消恢复')`，`:229-230` catch 同样返回，`:148-156` 外层 finally 赋值 `webdavBusy=false`，`:514` 恢复按钮绑定 `enabled(!webdavBusy)`。因此不能宣称“取消必然不 resolve”；实际弹窗关闭、按钮重新可点仍需设备证据。 |
| 目标控件的稳定 id 在基线缺失；后续拟议名称合理也不等于已存在。 | `TopNavigation.ets:69-79` 齿轮点击容器无 `.id()`；`SettingsPage.ets:487-517` 列表项使用 `item.id` 作数据/ForEach key，无组件 id；`SettingsSyncSection.ets:262-336` 输入/开关 builder 与 `:507-525` 恢复按钮/结果无 `.id()`。目标三个文件的 `.id(` 检索只命中 `SettingsPage.ets:549` 动态页面根。 |
| 需求稿已区分明文、推导与未确认假设，没有把后置确认算作「继续」。 | `workflow/requirements/analysis-01.md:10` 定义需求等级，`:43-44` 区分 D1/D2，`:53` 标明选择器为建议契约，`:57-68` 标记待补 id，`:123-127` 将数据不覆盖、loading 分层等列作推导。快速动作的明文约束仅是未继续时零请求；节奏和额外 UI 策略仍是测试策略/推导。 |
| 完整恢复成功不是这三场景的明文验收。 | Spec `:7`、`:20`、`:33-40` 均围绕第一层取消、重开、继续前零请求。需求稿 `:202-203`、`:234`、`:246` 已把继续后结果、D2 取消和成功恢复放在原有流程回归/未确认扩展范围，不应升级为核心必过项。 |

上表源码短名均位于 `entry/src/main/ets/`：页面文件分别为 `pages/settings/SettingsSyncSection.ets`、`pages/SettingsPage.ets`、`pages/index/components/TopNavigation.ets`；同步文件分别为 `sync/WebDavSyncManager.ets`、`sync/webdav/WebDavBackupManager.ets`、`sync/webdav/WebDavClient.ets`。

## 汇编时保留的措辞边界

1. S7 `webdav_restore_request_loading`、S8 `webdav_restore_result` 是未来观测既有状态的候选契约（需求稿 `:64-65`）。本题不因此新增进度组件、结果组件或成功恢复要求；如后续方案采用其他可验证方式，应同步选择器和测试。
2. A17 的“不能启动请求计时/后台恢复任务”（需求稿 `:125`）宜限定为不得提前调度真实恢复请求。本地弹窗超时、纯模态 busy 本身不等同于 WebDAV 请求，不能仅凭内部字段/定时器判断场景三失败。需求稿 `:133` 已区分模态禁用与真实请求 loading。
3. 基线 `Promise.race` 超时与原操作缺少显式取消，是源码可见风险（`SettingsSyncSection.ets:115-121`），并非已复现的本题取消缺陷，不扩成本轮修复或必过验收。
4. 前台自动同步可能是独立请求来源；本轮未重做该链路探索，沿用 mapper 的本题静态证据。测量时应明确隔离条件；不得把有效配置缺失造成的零请求误作确认 gate 正确，也不得默默过滤并发自动同步而声称满足“任何请求为零”。

## 未改业务代码与输入完整性

以下只读命令均正常退出（exit 0）：

- `git diff --name-only`：仅 `AGENTS.md`。
- `git diff --cached --name-only`：空。
- `git status --short`：已跟踪差异仅 `AGENTS.md`；另有 inputs、logs、spec-harness、spec、system-config、test-harness、traces、workflow 等未跟踪记录目录。
- `git ls-files --others --exclude-standard -- entry AppScope hvigor build-profile.json5 hvigorfile.ts oh-package.json5 oh-package-lock.json5`：空，未见这些业务源码/配置范围的新未跟踪文件。
- `git diff -- AGENTS.md`：仅追加“本题自动调度”和工作区阶段说明，与首次检查已存在差异一致；本角色未改动，不能算作本轮业务实现。
- `Get-FileHash -Algorithm SHA256` 前后复读一致：需求为 `256038a2336dce8956585ff92c18e7ec9e5cd79d736f7b7f56021dbf646af592`，元数据为 `92a41fc04e0bb8ff18e0fce0e9324039fb369a4c879cffd2477c2e9b15e58c9c`。

未进入改代码阶段，未检查或运行官方基线准备脚本；后续首次改代码前仍需确认其已执行。未执行构建/设备，不能据本审计声称基线编译或 Spec 场景通过。

## 核查源码 SHA-256 指纹

| 文件（相对 `entry/src/main/ets/`） | SHA-256 |
| --- | --- |
| `pages/settings/SettingsSyncSection.ets` | `5a54092f181b28f263265c2d6c83429f1122298b456a04d531679a8f852836c3` |
| `pages/SettingsPage.ets` | `46cdc00a6b95ca899dbba56299eea5223149637cb7b9f17b4710e1a116be968b` |
| `pages/index/components/TopNavigation.ets` | `a83305eb61bfb259d875d947a95eccf1329b5cee7ef116edc9eede290fcf6709` |
| `sync/WebDavSyncManager.ets` | `300cd1d88fb576b7d570698ae1df61ff5cfce9670f47f846e4f5d3d4ccec452b` |
| `sync/webdav/WebDavBackupManager.ets` | `4942e2666a73d7b5938c483046f9d7daad40c737fef4fe2cfaacc7c74434f87b` |
| `sync/webdav/WebDavClient.ets` | `b4200f8c685907e1ebc8e3740f27a5a6414b2bfdee2758183d1adc823d2f487b` |

## 检索失败与未解决项

- 已读取 `C:/Users/22580/.codex/skills/hmos-arkts-knowledge-retriever/SKILL.md`。执行其 `scripts/search_docs.py --query 'async Promise try catch finally'`，exit 1，`FileNotFoundError` 指向该技能缺少 `references/doc_index.json`；随后对技能约定 `docs/ArkTS-Language-Guide/02-Basic-Syntax` 和 `exception-handling.md` 的 `rg` 读取也 exit 1（路径不存在）。保留此真实失败，不伪称已完成官方 API 文档验证，没有安装/修复技能包。
- 结论只依据本题源码调用、返回和赋值次序，不对原生弹窗运行行为或 API 兼容性作外部事实背书。独立设备验收、构建、网络计数及歧义裁定仍交主 Agent 后续处理。本轮发现的措辞提醒不需要修改业务代码。
