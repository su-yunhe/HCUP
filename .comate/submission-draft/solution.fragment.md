# cml-spec7 完成情况与协作片段

本题为本地部分完成：41项明文原子验收中38项pass，B9/B10/B11真实微信、QQ、支付宝授权流程blocked。用户没有第三方开发者账号，缺少合法平台应用身份、签名/回调登记及确认的服务端换票条件；现有点击、缺配置反馈与恢复不计真实授权通过。构建、安装、冷启动和已实现范围适用回归通过；不是官方F-point/成绩，不宣称全部完成。

实现范围为正常“我的”入口到登录页、120vp基线Logo、两种登录目标页导航、三品牌图标和标签、两份独立协议链接及原创本地长正文、逐字页脚、100%/70%/60%自适应与入口去重。未新增SDK依赖或伪造认证结果。原始需求与blocked项继续有效。详见 `workflow/delivery-01.md`、`workflow/verification/final-verification-03.md` 和 `logs/verification-final-03.json`。

## AI实际参与及证据

AI参与需求拆解和复核、基线代码审计、方案与修订、14个生产文件实施和修复、独立构建/设备回归、失败诊断、材料整理与交付校验。主调度按需求/方案/编码/独立自测四角色派工；真实Agent角色、父子关系、模型/effort、工具调用及事件范围见 `trace-index.md` 和 `traces/session-metadata.json`。AI角色分工不等于人工成员分工；真实 `members[].name/work` 为 **【待补充】**。

有效03轮保留完整原始结果：手机原轮39通过/8跳过/1测试错误，文档助手大小写修正后3/3通过；平板800vp补测、大屏真实1200vp四项和短横屏另有原始记录。曾标称large的旧轮实际800vp、旧导航/布局失败、02b并发改源失效、原始stdout缺口和清理拒绝均保留并标范围。合并验收仍为38pass/3blocked，不通过堆叠用例数扩大结论。

## 已观察问题与验证边界（自动取证）

除B9–B11外，未执行已登录个人资料分支、恰好600/840vp断点、拖拽调整和真实授权；没有抓包证明网络请求数量。短信/密码目标页仅验证导航，不宣称认证成功。初始化独立hdc stdout未被最初Transcript捕获；保留原生工具结果、明确标注转录和之后完整设备输出。临时模拟器磁盘清理被工具自动审批拒绝，未执行删除；原磁盘保留，生成缓存从提交清单排除。具体证据见 `workflow/delivery-01.md`、`logs/analysis-baseline/initial-device-observation-transcription.json`、`logs/verification-closeout-03/temporary-disk-cleanup-rejected.json`。

这些已知事实不代填人工 `known_issues`；该输入仍为 **【待补充】**。人工修改、额外来源、IDE导出路径及团队人工声明亦待补，见 `missing-fields.md`、`human-changes.md`。

## 版本、来源保护与正式提交边界

官方基线为 `75fd0066a7fc0c1e8cedb6218df081f86d307f45`。完整生产输入聚合SHA-256为 `26307326248e8e874d1e2d8c3a4abf10e14008d5fd386b91682357a928f6f78e`；它与14个变更文件的聚合范围不同。HAP SHA-256为 `8aaa5de48b5664b92210fad7ffcddf9abbcebbb92e52faf7f5359bbeb3611863`，大小 `17068002` bytes，证据为 `facts.json` 及最终验证记录。完整交付文件树标识以 `project-manifest.json.final_version` 为准，不能用仍停留基线的Git HEAD代替。

当前材料草案拟映射到 `tasks/cml-spec7/`，工程必须精确取 `traces/code-snapshot/project/`，避免把包含自身补丁/快照的 `.comate/submission-draft/` 递归塞回project。其他真实过程文件按完整清单纳入；二进制、排除项及补丁校验见 `DELIVERY.md`。当前补丁状态：已通过；完整命令、退出码、逐文件比较与当前摘要见 `patch-validation.json`（`passed=true`）。

`submission.json.fragment` 仅一个本题对象；`team.yaml.submitted_tasks=[]` 尚未选择本题，因此保守为 `not_completed`。三个非空路径是拟供3-package采用的真实材料位置，非“全部功能通过”或“已正式提交”的声明；最终是否标submitted由3-package依据真实选择决定。

团队正式版本 `version`、联系人 `contact`、成果冻结北京时间 `freeze_time`、成员姓名/分工及 `source_guard` 均为 **【待补充】**。材料导出/快照时间不能代替正式冻结时间。本阶段不生成团队根solution/sources/README、system-config或ZIP。实际保护配置见本题 `AGENTS.md` 与已有 `system-config/`，原生记录索引见 `trace-index.md`；人工来源保护声明仍待提供。
