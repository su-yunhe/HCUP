# vg-spec9 编码交接 round 01

状态：生产源码已冻结，可独立构建、安装与自测。本记录不是验收通过声明。

- 原生 `CODEX_THREAD_ID`：`01a14496-c173-76b3-ac93-888a4286fe9d`。
- Spec SHA256：`c6236994e253c6de9f6decd99d7c0637620027ac16ce3699154796cba7a5edbf`。
- 基线：`a22f32b07bf81c6dde4367e2543ebac29186cbc1`；首次改代码前已读 `logs/prepare-baseline.log`、`resume-checkpoint.json`，确认正式准备完成且工程未变。按主 Agent 批准的 `workflow/design/round-01-plan.md` v1.0 实施。

## 修改及覆盖

仅修改以下五个生产文件；导航、协议、数据库、依赖、备份恢复主体及他人改动均保留。

| 文件（相对 entry/src/main/ets） | 行数 | 实现落点 |
| --- | ---: | --- |
| `sync/ManualWebDavSyncController.ets` | 100 | 进程期手动任务所有者；首次异步前锁定 running，复制本轮配置；保存后直接 await 原 `syncIncremental()`；失败/异常/成功均 finally 清理；类型化快照和订阅，通知异常隔离。外部 manager 已占用则拒绝，不改其配置或状态。 |
| `pages/settings/SettingsSyncSection.ets` | 489 | 挂载订阅、销毁注销；组合其他操作 busy 与手动 running；同步入口只抓表单快照并启动；保存/测试/备份/恢复入口 guard，恢复确认后再检查。密码原值、trim 和空目录默认值保持。 |
| `pages/settings/SettingsSyncConfigCard.ets` | 106 | 原基础卡片原样抽出，保留 @Link 绑定，给实际输入设置稳定 ID。 |
| `pages/settings/SettingsSyncActionCard.ets` | 188 | 原操作卡片与说明原样抽出；实际 `LoadingProgress` 的 ID 为 `webdav_sync_loading`，可见性仅绑定 manual running；按钮与结果稳定 ID 按方案。 |
| `sync/WebDavSyncManager.ets` | 1218 | 仅把已有预检纳入原 try/catch/finally，预检异常不会遗留 SYNCING。此文件不是 UI 组件。 |

A1/A2 保留入口与配置；A3/A6/A10 保留原按钮并加 ID；A4/A5/A7/A11 绑定真实手动状态和加载组件；A8/A9/A12/A13 继续原真实同步链；A14 由单所有者、直接 await 和重入订阅保证；A15/A16 由终态发布与 manager finally 收束；A17 不添加空数据短路；A18 同步 guard 忽略重复。B1—B15 按方案保持原校验、未触发不启动、单轮防重、真实多阶段、恢复及进程内重入策略；分页及不存在的手动取消控件不新增。上述是实现映射，实际结论由独立验证决定。

## 局部检查

- 构建前加载 `. D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`（其内部加载 `D:/hongmengcup/Enter-HarmonyEnv.ps1`）。命令：`hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon`。
- 首次构建成功，退出码 0，日志：`logs/implementation-build-01.log`、`logs/implementation-build-01-exit-code.txt`。无依赖安装或编译修复轮次；既有未签名产品提示保留。
- ArkTS 告警按文件和消息归一化、忽略迁移后的行列号：基线 759，本轮 754，无新增种类或数量。完整差分见 `logs/implementation-checks.json`；增量构建未重新报告的两条既有 LoadingAnimations 告警不算本题修复。
- `git diff --check` 退出 0；构建未产生额外 tracked 源文件变更。未安装、未运行设备或 Hypium；独立验证不由局部构建代替。
- 使用本地 ArkTS 检索技能。其检索脚本报缺 `references/doc_index.json`；直接读取包内 `Basic-Syntax/functions.md` 的 Function Types、`classes.md` 的 Static Members、`error-handling.md` 的 finally/async 错误处理作为依据，未修改技能包。

## 指纹与待验证

实际完整生产差分：`logs/implementation-production.diff`。五文件各自 SHA256、行数、告警差分和输入指纹：`logs/implementation-checks.json`。

五文件合并 SHA256：`bc10b92786d5502b5a6b132a78728711e590560ca9ada73b10e64153b1f2386a`；算法为按相对路径排序，将每项 `path + NUL + sha256 + LF` 拼接后取 SHA256。

未解决实现项：无。待独立实证：真实组件类型及可见性与同轮网络请求重叠、完整成功/失败重试、无增量、快速/重复操作、运行中离页再入、重启、配置交错、旧 120 秒时限之外的持续流程。保留其他非手动同步动作既有 timeout 包装，未扩大修复范围。最终结论由主 Agent 结合独立自测作出。
