# cml-spec17 完成情况与协作片段

本片段供第3阶段汇总到根 `solution.md`。团队已提供 `team_id=HC2026-111`、`team_name=Ghost_London`、`stage=online`；成果包版本、联系人、北京时间成果冻结时间、人工成员/实际分工及团队来源保护声明均为【待补充】。Agent角色不是人工成员名单。

## 本地完成范围

1-do 在隔离测试前置与受控本地 HTTP 条件下完成客户端实现和本地验证：正常23、故障3个唯一方法通过，按完整方法标识去重为26；E01–E31/D01–D11共42项需求受控样本及2项普通 guard 回归通过。它们不能相加为官方 F-point，也不代表认证线上后端、真实支付交易或官方隐藏测试通过。证据为 `tasks/cml-spec17/project/workflow/do-stage-result-03.json` 及 `workflow/verification/do-results-03.md/.json`。

已实现原确认页通过原创建接口提交商品/规格/数量、当前地址、原值备注和所选优惠券；缺地址时提示精确底部 Toast“请选择收货地址”，支持原地址选择/新增往返并保留草稿；成功响应的订单ID与realPrice进入原支付路由，零金额有效；包含同步重复提交保护、数据就绪门禁和有界失败重试。购物车来源成功后异步删除已购规格并刷新原购物车，保留未购规格和其他行。此前“VM已更新但实际地址卡仍显示旧默认地址”的E03/D02失败已局部修复，并由原强UI断言及全量回归验证。

U01–U10属于批准采用的有界策略，状态为 `adopted_bounded_strategy_not_spec_explicit`；详见工程 `workflow/state.json` 和批准需求/方案。不能据此承诺未运行的所有边界、跨进程清理补偿或服务端行为。构建诊断“新增观察0”受增量缓存限制，不表示全部告警消除。

## 仍未运行、外部阻断与用户声明

用户 `known_issues` 补充声明：【待补充】。下列为已有证据中的客观边界，不因该字段为空而省略：

| 标识 | 状态 | 当前边界 |
| --- | --- | --- |
| D09/B23-missing-entire-row | not_run | 整行预先不存在未单独动态运行；缺失购买规格91及后续商品继续已实测 |
| D09/B21-cross-goods-same-spec-id | not_run | 两个goodsId下完全相同spec.id未另建样本 |
| B11/address-pagination | not_run | 最后一页选址、长列表压力未测 |
| U01/max200-leading-trailing | not_run | 中文、空串、三个空格已测；200上限及带前后空格完整样本未重跑 |
| U02/no-coupon-list-and-cancel | not_run | 未选券/选券创建已测；空券列表和选后取消未单测 |
| U04/U06/B19-destroy-kill | not_run | 在途销毁、强杀及清理中强杀恢复未测；清理完成后重启已测 |
| U08/non-finite-id | not_run | null、缺id、缺金额、负金额及0已测；非有限金额、非正id未单测，不承诺非标准JSON数值 |
| U10/concurrent-same-spec-quantity | not_run | 并发新增同规格数量未测；按规格删除策略不承诺跨进程补偿 |
| address-add-failure-cancel | not_run | 原新增成功全链已测；保存失败、未保存Back取消未单测 |
| authenticated-live-backend | blocked | 未取得合法测试账号/认证线上数据；真实线上创建和支付未验；普通包与无Want测试包均被原guard送登录 |
| official hidden tests | unknown | 没有官方隐藏测试结果或官方分数 |

## AI参与、失败保留与人工记录

实际研发客户端为 Codex。分析主会话 `01a15320-35c3-7341-a387-a8c8cec04015`、1-do主会话 `01a15412-7c11-7292-b4ef-1b7d894060a9` 分别组织需求复核、方案、实施审计/实现和独立验证。本轮材料主会话 `01a15490-1423-7570-9c1c-98d9a6af515d` 及其角色只整理提交材料；它们不能替代原开发记录。全部相关主/子会话、事件截点、工具调用、模型及参数以 `tasks/cml-spec17/evidence-facts.json` 和 `tasks/cml-spec17/trace-index.md` 为准。已采集模型上下文为 `gpt-6.1-sol` / `xhigh`；逐会话 token 是原生最后累计快照，不跨父子或压缩相加为账单用量。Comate未使用，其sessionUuid和客户端/扩展取证不适用。

失败保留入口包括工程 `logs/implementation-build-01.log`、`logs/implementation-build-02.log`、`logs/implementation-build-03.log` 到 `logs/implementation-build-04.log`，do-01重试，`workflow/verification/do-results-02.md` 与 `logs/do-03/selftest-20261019-212521.json` 的E03/D02原失败，`workflow/implementation/do-implementation-02.md` 的fix-02，以及do-04回归。旧HAP、代码快照和失败截图/输出按实际状态保留；零字节失败截图不算有效图像证明。

人工 `human_edits`：【待补充】；用户额外来源 `extra_sources`：【待补充】；用户侧边栏Markdown导出目录 `md_export_dir`：【待补充】。详见 `tasks/cml-spec17/human-changes.md` 和 `missing-fields.md`。程序生成的Markdown仅便于阅读，非用户侧边栏导出；总体diff不能证明修改作者。团队来源保护声明 `source_guard`：【待补充】；本题已有AGENTS、任务书和system-config限制供核验，不替代用户声明。

## 工程版本、材料边界与后续汇总

官方基线为 `d6a6ba7480fbd0a30075462e46bb4344a430ba61`。生产844文件聚合摘要为 `2278a77074b39f8d97067beb853d7880bb91d3586dbf228992ffba2d9ccb03b5`，它只标识生产文件集。完整工程版本以 `tasks/cml-spec17/changes/project-files.json` 的冻结清单、聚合摘要和树OID为准，差异与回放见 `changes/final.diff` / `changes/validation.json`，不能用当前HEAD代称最终交付版本。

`.comate/submission-draft/` 是project外层材料暂存区D，不递归放入project；其他真实`.comate/`过程、spec/workflow/测试与失败记录保留。模拟器实例运行态子树、跨题初始化总览raw及明确缓存按排除清单处理。第3阶段按project-files清单逐文件核对后复制，不能递归复制仍变化的工作区。原生导出截点与工程冻结时点分别记录，用户正式冻结时间仍为【待补充】。

`submission.json.fragment` 的 `submitted` 仅表示本题拟提交候选：团队 `submitted_tasks` 尚未确认，仍需第3阶段统一冻结、填写团队信息并汇总。当前没有上传、正式提交邮件、团队ZIP或官方材料实质通过结论。
