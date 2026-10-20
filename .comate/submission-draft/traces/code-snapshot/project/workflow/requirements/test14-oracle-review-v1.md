# test14 测试判据冲突复审 v1

CODEX_THREAD_ID：`01a143b9-c1b8-7721-9a85-0962250f5524`。

**结论：当前断言过度。允许本次备份被拒绝的警告终态描述其它任务仍在进行；该文字不证明本次备份仍忙。应精准修正 test14 的拒绝分支判据，不修改生产代码，也不普遍放宽终态检查。**

依据：`spec/requirement.md:7,20,27,33` 的加载与进行中文字要求均针对真实备份的运行期间。它没有禁止终态说明拒绝原因。前次复审 R05/R07 要求真实备份终结后释放自身进行态，R08 允许其它任务占用时拒绝，R09 要求区分任务归属。因此“⚠️ 同步操作正在进行中：请等待当前同步完成后再试”明确说明其它同步占用，不等价于“正在备份到云端...”。

读取的直接证据：

- `logs/implementation-verification/run02/selftest.json`：14 pass、1 fail；唯一失败为 test14，消息正是上述拒绝警告。
- `logs/implementation-verification/run02/selftest-raw.log:1726–1730`：test14 调用 `settled(False)`，通用判据把任意“正在”或“处理中”都判为未收敛。
- `logs/implementation-verification/run02/test_14_other_testing_task_survives_page_reentry-01-settled.json`：备份按钮为 `Button`、文字“立即备份”、enabled=`true`；状态为上述警告；该采集内无 `webdav_backup_loading` 或 `LoadingProgress` 节点。其它 TESTING 任务 pending 及无新备份请求属于本次派工已给定事实，本角色未另外核验服务端日志或运行设备。

精准修正边界：

1. 仅对“已确认其它任务占用、当前手动备份未启动”的拒绝分支启用显式例外，校验该拒绝消息或等价明确拒绝语义；不能只因有 `⚠️` 就允许任意进行中文字。
2. 仍须断言本轮 `webdav_backup_loading` 不存在/不可见，按钮恢复“立即备份”且可用；保持其它原有终态检查。
3. 仍须独立断言点击前后没有新增备份任务或备份上传请求；原 TESTING 的 HEAD 可以继续 pending，不能将其算成本轮备份请求，也不能要求它因拒绝备份而结束。
4. 成功终态、已启动真实备份的失败终态，以及其它用例的默认 `settled` 判据保持严格：无本轮 spinner、按钮恢复，且不残留本轮“正在备份...”或“处理中...”状态。不能全局删除关键词断言或豁免所有失败警告。
5. 后续必须重跑修正后的 test14；本复审不能将现有 run02 的 fail 改记为 pass。若实际仍有 spinner、按钮禁用或新备份请求，应继续按实现失败处理。

本角色只新增本文，未改生产、测试、状态，未操作设备，未派生 Agent。建议主 Agent 路由验证角色修正上述测试语义并回归；无需产品需求变更或用户决策。
