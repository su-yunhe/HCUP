# 2-submit 草稿交付结论

本题材料整理及独立校验完成；正式团队成果包仍待人工信息和记录适用性确认。本轮未改业务代码、资源、构建配置，未构建/占用设备，未创建ZIP、提交Git或向外发送成果。

- 工程输入：`../project/`，1991个文件，必须按此冻结副本进入3-package。
- 完整差异：`../changes/final.diff`，299361773字节，SHA256 `7a88908dc1a6b79c31f3f71bdc100de7a83991f223a64bd6013d3fe83e78eeb2`。
- 工程清单SHA256：`444b98d793f8d057a33490bedb3b4f8056b9fd068602e2a7a26c193ffaeb8520`；材料revision2技术冻结时间见该清单，团队正式freeze_time仍待补。
- 本地基线check/apply及独立fresh clone round03均退出0，1991个路径/大小/SHA全部一致。258项生产输入与1-do版本不变。
- 官方24字段、14本题原生会话、756本题源日志、397二进制清单均已核对。失败/重试、旧材料revision1及独立检查器修正证据保留。

首次把`.git`指针误计入工程清单，以及来源正文未限定AI观察范围，两项发现已修正并重新验完整补丁；没有修改业务文件或降低断言。过程证据见本目录的metadata-boundary-fix、revision2-resolution、独立报告和重建各轮记录。

## 仍需用户补充/确认

完整列表：[pending-fields.md](../pending-fields.md)。包括成果包版本、联系人、团队正式冻结时间、成员与实际分工、来源保护声明，题目人工修改/已知问题/额外来源声明，以及IDE导出目录。仅供3-package的全阶段题目列表和ZIP路径也未提供，不推断其他题。

本次实际使用Codex原生JSONL；Comate引擎sessionUuid与Comate IDE双ID不存在，不能补造。官方清单允许原生JSON/JSONL或等效完整记录，但本地任务书的Comate字面双ID项仍需在最终团队材料中明确不适用/待确认。官方规定位置的baseline准备日志缺失，已提供本题实际prepare日志并披露，未伪造历史执行时间。

自动测试脚本固定开发机ROOT/安装manifest，移植限制已写入build.md；本阶段禁止改脚本。D2深恢复、自动同步并发及隐藏用例未测。人工空声明不会被机器观察代填。

## 已自动填入的事实及出处

完整列表：[auto-facts.md](../auto-facts.md)。含基线、应用/入口、依赖锁/SDK、构建安装自测、HAP摘要、实际工具/模型/会话、任务书SHA、来源访问、完整diff与二进制、所有校验结果。

单题映射见[PACKAGING-HANDOFF.md](../PACKAGING-HANDOFF.md)。本目录只复制最终JSON/MD/原始失败日志及必要历史证据；不要把临时clone、`.git`元数据或缓存放进正式包。

材料收尾两会话的后续原生前缀及Markdown已保存[closing-traces/index.json](closing-traces/index.json)，建议3-package放入`tasks/vg-spec8/traces/material-closing/`。它们不修改冻结project；当前主会话导出后的收尾调用/最终消息仍需3-package在其最终截点补存。本轮草稿准备完成不等于可跳过人工字段直接正式提交。
