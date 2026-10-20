# vg-spec13 单题材料交付

本目录为2-submit单题材料暂存产物。业务代码、资源、工程配置未改。根团队solution/sources/README/system-config、成果ZIP及任何外部提交均未在本阶段生成。

## 阶段3复制约定与完整差异

必须把 `traces/code-snapshot/project/` 复制为成果包 `tasks/vg-spec13/project/`；其文件集合、每文件SHA和内容Git树以 `traces/code-snapshot/manifest.json` 为准，最终树 `93dafec8eb504b56d1329df5e5ad59110c66d27e`。把本目录的build/trace-index/fragments/changes/logs/repro-support等复制为project的同级任务材料。`traces/code-snapshot/project/`是完整封存工程，不是仅业务文件。

不要从仍活跃的工作区递归复制`.comate/submission-draft/`进入project：补丁和快照无法包含它们自己。此目录仅是工程外材料的staging，所有其它实际Git可见工程文件均纳入，含spec、inputs、hypium_tests、workflow、logs、相关traces、既有system-config及任意非staging的.comate文件。忽略的build/oh_modules/.hvigor/cache不属于源码交付。没有改源Git索引、HEAD或历史。

已存在的六份初始化跨题总览会话原文被排除，没有读取它们作为本题开发证据；既有manifest引用保留作原始历史文件说明，不假称原件都随包。所有选择/脱敏与原件/封存SHA见snapshot清单。账号标识脱敏不遮蔽代码与来源；本题已登记专用会话保留完整记录格式、失败重试及派生Markdown。

`changes/final.diff`为官方base到该封存工程树的完整--binary差异。校验使用本题仓库的两份临时单分支clone，各checkout到官方base；先 `git apply --check --binary`，再实际apply，与完整封存工程比较文件集合及每文件SHA。结果、补丁大小/SHA、比较数见 `changes/patch-validation.json`，不是只检查六个业务文件。临时clone完成后清理，不提交.git目录。二进制清单另列官方同源与新增本地截图证据。

## 剩余事项

输入空字段统一【待补充】，见 `NEEDS-INPUT.md`；自动填充事实及来源见 `AUTO-FACTS.md`。本阶段17项本地通过的准确范围及限制见solution片段，不能声称官方通过。历史构建、自测、安装与失败日志均已复制，不为材料补录而重新测试。官方基线准备报告缺失不通过重跑替换历史原件；本题已有本地准备日志保留。活动会话尾部只能在阶段3真正停止后再导出，当前有限快照的截止时间明示，不冒充全时段最终归档。

打包器还应将 `submission.json.fragment` 合并到官方全题清单；本片段的submitted是本题拟纳入评分工程的候选条目，团队最终submitted_tasks仍由阶段3确认，所有相对路径均为包内路径。本阶段未生成完整团队清单。
