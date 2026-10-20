# vg-spec1：WebDAV还原确认

本题已完成本地有限计划验收：R01–R28共28条通过，最终采用19项不同计划用例通过，0失败、0跳过。它们不是官方F-point、隐藏测试或官方成绩。依据：`tasks/vg-spec1/project/workflow/development-handoff.md`、`tasks/vg-spec1/project/workflow/verification/coordinator-final-audit-08.json`、`tasks/vg-spec1/project/workflow/requirements/final-coverage-review-07.json`。

设置→WebDAV→从云端恢复入口在校验、下载前显示第一层风险确认，标题“⚠️ 从云端恢复”，正文“本地未同步的学习记录将会丢失”，提供取消和继续。等待、取消、实际边缘手势及框外点击均不进入恢复链；phase/ticket和页面活动状态约束重复交接、旧回调与离页后续跑。继续后沿用基线下载、预览、第二次确认和merge导入语义。6个生产组件均不超过500行，服务、schema、权限及路由未改动。完整改动见 `tasks/vg-spec1/changes/final.diff`。

AI实际参与需求拆解/复审、方案设计、6个生产组件实现、构建、自测、失败分析、测试设施修订和终审；可核对 `tasks/vg-spec1/project/workflow/requirements/`、`design/`、`implementation/`、`verification/` 及 `traces/vg-spec1/sessions.json` 中8个开发/分析会话。另5个本次材料会话仅作整理证据。初始化混合总览会话被排除，不作研发证据。模型原生字段为gpt-6.1-sol、effort=xhigh；逐会话版本、工具和token截点值见该JSON，不用重复快照累加。

最终19项来自完整回归13项、继续分支4项、同进程Home温返1项、真实出站隔离1项。完整13项、温返、隔离使用当前HAP SHA256 `a3574072f81f37e14c0f0c1b335673d44e7aa1691c83488a065d4b7c91278a36`。4项继续分支使用旧HAP `435d64b4b825cc85071e60feb617d77f76347973e6ea0570c07c5f22df823954`，旧设备1256×2760；各轮222个生产/构建输入与当前相同，是未变源码回归证据，不声称全19项运行过当前HAP或目标分辨率。额外两项旧补测不重复计数。764条既有ArkTS及原签名警告保留，规范化新增0、缺失0。

真实网络验证采用人工管理员启动的审查后helper，对本题专用模拟器程序副本作动态WFP出站过滤。同NAT路径完成在线GET200/1324字节→过滤中code2300028超时且服务端0到达→三取消→移除后GET200/1324字节。guest仍报告可用/LinkUp，不声称系统LinkDown、离线回调或独立IPv6目标已实测；服务端0到达不等于直接量出应用0请求尝试。清理、过滤器精确NOT_FOUND、helper/controller退出的证据见 `tasks/vg-spec1/project/workflow/verification/offline-round-03.json` 及 `tasks/vg-spec1/logs/development-round-02/wfp-offline-round-03/final-audit/audit.json`。

所有失败/重试保留：基线自动同步状态描述纠正、初轮手势坐标及双击预期问题、新实例设施准备失败、Wi-Fi关闭后NAT仍可达、helper05回读失败、06 IPC失败。05缺实际不匹配字段，06缺traceback/filename/winerror，不能反推唯一根因。IME首次声明被Agent误点“同意”的事件已披露；随后停止，用户完成输入法设置后才继续。人工还执行Wi-Fi开关和审查后的管理员启动。入口见 `tasks/vg-spec1/human-changes.md`。这些事实不能反推“无人工直接修改代码”。

未完成项与已知问题（用户声明）：【待补充】。现有证据披露继续后基线Promise.race不取消底层操作的风险；坏密文、空包、预览/导入失败及独立真实120秒超时注入不属于本次承诺计划，未追加通过声明。官方隐藏测试不可见。

团队ID HC2026-111，队名Ghost_London，阶段online；包版本、联系人、成员姓名/分工、团队来源保护声明、成果冻结时间（北京时间）：【待补充】。本题角色约束/路径隔离的实际配置在 `tasks/vg-spec1/project/AGENTS.md` 与 `tasks/vg-spec1/project/system-config/`；它们不替代用户的来源保护完整性声明。额外来源、人工改码声明和IDE Markdown导出目录仍待用户补充。

本次材料工程快照版本 `sha256:2968c3ebfe338969634f8d28fece3c28fce3f71e87a2901d52538a3412787bba`；它是清单摘要，不是新Git提交或团队正式冻结时间。基线 `9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`。工程交付范围必须遵守 `tasks/vg-spec1/changes/project-manifest.json`：保留源码、spec、hypium_tests、真实过程文件和所有其他已有.comate文件；剔除模拟器运行磁盘/缓存、6个pyc、14份初始化混合会话原文，以及本次submission-draft自身，避免diff递归。排除文件逐项见 `tasks/vg-spec1/audit/excluded-files.json`（3-package须随任务审计材料携带）。该投影已实际应用补丁并全文件比对；不能把它称作未经筛选的本地全目录差异。
