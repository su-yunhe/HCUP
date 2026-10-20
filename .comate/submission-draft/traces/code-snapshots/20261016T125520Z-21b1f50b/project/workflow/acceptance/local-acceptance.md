# vg-spec9 本地验收

范围：完成 `spec-harness/1-do.md` 的开发与本地验收；未执行赛事提交。

## 实现与审查

原有 WebDAV 配置入口、保存语义及实际同步协议保留。新增真实 ArkUI `LoadingProgress`，由进程内手动同步控制器拥有运行状态；立即同步直接等待真实 `syncIncremental()`，不再由 UI 的 120 秒包装提前结束。页面离开注销监听，重入绑定同一在途任务；重复触发及在途配置提交受到保护。原配置、操作卡片拆分后，改动组件分别为 489、106、188 行。

实际生产变更为五个文件，交接与完整差分见 `workflow/implementation/round-01-handoff.md`、`logs/implementation-production.diff`。主 Agent 已审查生产差分、状态生命周期和恢复 guards。

## 实测证据

- 独立 clean 构建、安装、冷启动成功，退出码为 0；基线 ArkTS 告警 759，本轮 756，按源文件与消息多重集无净新增。
- 12 个唯一 Hypium 用例最新有效结果全部通过，失败、错误、跳过均为 0。汇总见 `logs/selftest.json`；各结果保留分轮原报告引用，不删除首轮脚本参数失败历史。
- 真实成功链包含认证 HEAD、下载 GET 和应用生成的加密 PUT。实际 UI 树及截图确认同轮请求进行时的节点类型为 `LoadingProgress` 且可见，真实终态后隐藏。
- 无业务增量的上传载荷已校验 MAC 并解密核对结构，words、definitions、userBooks 均为 0；仍有真实同步与加载证据。
- 长请求链实际成功耗时 264.469 秒；超过旧 120 秒边界后，加载类型、可见性与活动请求重叠均已核验。
- 回归覆盖错误响应及更正重试、连接拒绝及有效重试、空值和纯空格、未触发/取消输入、保存、重复/快速点击、标题与系统返回在途重入、冷启动、默认目录、地址/账号 trim、密码空格及在途配置隔离。

逐项 A1—A18、B1—B15 判定和未测子项见 `workflow/verification/round-02-final-report.md`，主 Agent 已核对其结果及限制。原始命令、退出码、请求、UI 树、截图、上传内容哈希和源码指纹位于 `traces/implementation-validation/`；复现命令见 `workflow/verification/REPRODUCE.md`。

## 最终版本核对

主 Agent 审计见 `final-audit.json`：Spec、metadata 未变；五文件冻结指纹及最后设备测试的 251 个源码/资源文件与当前文件一致。当前 HAP 与独立构建并安装验收的文件一致：

`entry/build/default/outputs/default/entry-default-unsigned.hap`

SHA256：`b367da84359ad19ba9fad5e808f864fe06c10280850332da1c11615a8efe70b6`。

Git 差异只有真实生产、测试和流程资料；`AGENTS.md` 的准备期追加为本轮开始前已有。没有需恢复的 tracked `BuildProfile.ets`。Python 生成缓存的递归删除被自动审批拒绝（仅返回 `blocked by policy`），随后采用保留内容的安全方案移入本题已忽略的 `.hvigor/vg-spec9-selftest-cache-20261016-1238/`；记录见 `cleanup.log`。

## 范围与限制

- 官方隐藏用例及成绩不可见，本地验收不代表官方评分。
- HAP 为现有配置生成的 unsigned 产物，已在本机 API 23 模拟器安装验证；其他签名/设备未验证。
- Spec 不包含同步取消按钮、分页；这些不适用，不新增相应业务。未启动同步时取消/离页无本轮请求已实测。
- 跨进程在途任务恢复、运行中强停、自动同步竞争及无关旧 ohosTest 套件不是本次已通过的 12 组证据，不声称其通过。
- 临时夹具正常关闭，设备租用已释放；此前保留的 hdc 映射未执行被拒绝的删除重试。

需求复审与采用的可逆策略：`workflow/requirements/round-02-implementation-review.md`、`workflow/implementation/orchestrator-decisions.md`；批准方案：`workflow/design/round-01-plan.md`。当前实现的明文需求与必要回归已取得本地实测证据，无未解决的功能阻断项。
