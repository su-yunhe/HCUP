# cml-spec28 单题提交材料草案

按用户2026-10-19的明确指示，在保留AUTH阻断的条件下整理2-submit材料。业务代码、资源、配置和原测试均保持正式10原件；本阶段没有新构建或设备复测，没有生成团队ZIP或对外提交。

**1-do正式整体验收尚未完成。** 原六项正式测试为1 pass、5 AUTH skip。有限fixture主31项及额外3项通过，按08/09/10实际版本记录，不能作为正式登录验收或官方分数。

## 主要文件

|文件|用途|
|---|---|
|[build.md](build.md)|环境、依赖、构建/安装/启动和复测指引，已有结果及移植限制|
|[trace-index.md](trace-index.md)|官方24字段、真实会话、模型/参数/工具、失败及记录缺口|
|[solution.fragment.md](solution.fragment.md)|供3-package汇总的完成情况/未完成项/AI参与片段|
|[sources.fragment.md](sources.fragment.md)|官方基线、通用地区数据与技术资料来源及许可|
|[submission.json.fragment](submission.json.fragment)|本题候选条目，status=not_completed；三个路径按预期成果包布局填写|
|[pending-fields.md](pending-fields.md)|所有用户空白字段及技术记录缺口，不代填“无”|
|[facts-and-sources.md](facts-and-sources.md)|自动填入的事实及出处|
|[changes/project-scope.md](changes/project-scope.md)|完整工程冻结范围、所有排除及后续拷贝约定|
|[changes/project-files.json](changes/project-files.json)|冻结工程每个文件的SHA-256及大小|
|[changes/final.diff](changes/final.diff)|从官方base_commit生成的完整二进制补丁|
|[changes/binary-manifest.json](changes/binary-manifest.json)|二进制路径、大小、摘要和基线同源信息|
|[logs/manifest.json](logs/manifest.json)|106份本题已有日志的拷贝摘要，含失败与重试|
|[traces/manifest.json](traces/manifest.json)|16个去重本题会话的原生及完整Markdown派生副本|
|[validation/](validation/)|基线clone/apply/逐文件比较、材料独立终审和业务未改校验结果|

候选not_completed是如实保留当前未验收状态，不代表团队已经决定放弃提交。本题是否最终以submitted列入成果包，必须在3-package结合团队最终清单决定；本草案没有代填空白submitted_tasks或人工声明。

## 最终结果与版本

|证据|实际版本|结果|
|---|---|---|
|主31中的全集/空集/导航/pending及迟到读取|正式08/app-r3|15 pass|
|主31中的六参数真实超时|正式09/app-r4|6 pass|
|主31中的历史字段/输入/六接口缺code|正式10/app-r5|10 pass|
|明确业务失败恢复、长旧号改坏还原、数字号码与IME|正式10/app-r5|3 pass|
|原始正式六项|正式10|1 pass、5 AUTH skip|

正式10的827文件聚合为`3eaa13107c4b8d83485fa473c8f83a42bedb8498783faa0539de4a9f12c0fa1c`，HAP为`51761093a48478502e5aac6f8e40678d00e1ed470c38c3c18140086cb8fad229`。旧R3十例、45种源码状态、11种日志回归分别保留，不累加为当前版本的完整功能通过数。

## 冻结、补丁与校验

补丁包含源码、资源、配置、锁文件以及spec、hypium_tests、workflow、logs、traces和已完成的.comate材料过程文件。具体文件以冻结清单为准；完整重建的每个文件都必须与清单逐字节匹配。补丁生成/应用只在validation下的临时clone内进行，不改原工程Git index、HEAD或业务文件。

缓存、依赖安装目录、live模拟器镜像、空WAL/SHM/临时journal和两份已知混合初始化总览raw不进入工程。非空WAL可能含提交数据，随对应主DB成套静态保存，须通过前后稳定性和审计副本完整性检查，不能当无用缓存丢弃。补丁本身、它的文件清单和验证输出、末次材料事件导出也不递归包含自身；这些都是明确的范围例外，详见scope与excluded清单，不声称毫无例外满足自包含要求。

3-package必须采用本次manifest对应的重建工程或按清单取冻结字节，不能直接复制之后仍增长的工作树。final.diff/清单/验证报告放在任务changes/validation位置；末次材料原生记录独立放在包根traces/cml-spec28/materials-final。布局映射见[materials-layout.json](materials-layout.json)。未在本阶段打ZIP或运行完整团队ZIP校验器。

## 保留限制

- AUTH未解除；没有合法真实服务会话，5项正式功能仍未测通过。
- 官方指定本题基线报告未找到；使用本题实际prepare/setup/provenance作替代证据并标清身份。
- 首轮失败构建缺精确预构建全源指纹，旧fixture-matrix完整历史结果JSON独立副本未找到；两处说明文字漂移有原生FileChange还原证据。
- Comate索引不存在；实际产品是Codex，不能编造Comate会话。当前桌面产品版本已由只读工具核为26.1013.40934/build20770；旧运行时点桌面版本、旧会话侧栏ID、用户人工修改/额外来源声明与成果冻结时间仍有缺证/待补项。
- Markdown是逐事件原生记录的派生可读副本，不是IDE侧栏明文导出；原生opaque加密字段保留，未解密。
- 新材料测试入口只执行过帮助/静态核对，未实跑设备。它保留11239专用设备约束，要求工程内新输出目录，含skip返回2。它记录传入HAP身份，不单独证明该包来自前一步clean build。

正式可上传状态取决于团队字段、冻结打包及实际验收/提交选择，不由本次材料整理自动成立。
