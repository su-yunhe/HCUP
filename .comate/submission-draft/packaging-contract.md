# cml-spec24 的 3-package 接续约定

本轮仅生成单题草稿；用户的团队冻结时间、版本等仍待补齐，没有打 ZIP、上传或提交。

## project 与 final.diff 的同一边界

`changes/project-manifest.json` 中 `files` 是最终 `tasks/cml-spec24/project/` 的完整文件清单。3-package 应按清单复制原工程文件，逐个核对 SHA-256；源码/过程记录变动后须重新生成清单和补丁。保留清单中的 `spec/`、`hypium_tests/`、`workflow/`、`logs/`、`traces/`、`system-config/`、`.comate/submission-tools/` 等全部文件，不能改成只拷贝业务目录。

清单的 `exclusions` 逐项记录被排除的构建/依赖缓存、模拟器运行磁盘及精确宿主Log/运行缓存、混题初始化原始记录、Git 管理文件，以及 `.comate/submission-draft/` 和 `.comate/submission-check/`。这两个目录是提交输出和独立验证工作区；把它们递归装回 project 会要求 final.diff 包含自身，无法得到有限、稳定的补丁。其余 `.comate/` 文件仍纳入。原目录未删除或修改这些排除项。

历史 traces manifest 原样保留，因此会出现指向已排除混题总览原文件的旧索引。它们是历史快照声明，不能当成当前包完整性清单；当前相关会话以包根 `traces/cml-spec24/manifest.json` 为准。初始化的本题准备事实由本题日志和 provenance 关联，不以总览的其他题内容作为证据。

临时 Git 使用 `core.autocrlf=false` 保留工作区原字节；补丁可能显示原工作区 CRLF 与基线 LF 的差别。原工程、原 Git 索引和全局配置未被转换。5 个基线可执行模式 PNG 保留原 Git 模式，应用后树 ID 与文件摘要均须一致。

## 草稿材料的包内位置

|草稿内|成果包内|
|---|---|
|build.md、trace-index.md|tasks/cml-spec24/ 下同名文件|
|changes/（整目录）|tasks/cml-spec24/changes/|
|logs/（整目录）|tasks/cml-spec24/logs/|
|checks/、facts/（整目录）|tasks/cml-spec24/checks/、facts/|
|pending-fields.md、automatically-filled-facts.md、packaging-contract.md、MATERIALS.md、material-manifest.json|tasks/cml-spec24/ 下同名附件|
|traces/（整目录）|包根 traces/cml-spec24/|
|solution.fragment.md、sources.fragment.md|汇入根 solution.md、sources.md，并保留本题片段作依据|
|submission.json.fragment|合并入根 submission.json 的本题条目，最终提交选择由3-package输入决定|

不要仅照搬 3-package 的四个主文件而丢弃清单/校验附件。根团队文档及 system-config 汇总属于下一阶段，本轮未生成。完整工程仍必须交付，补丁和 HAP 不能替代它。

## 已运行校验和再次打包

`checks/diff-verification.json` 保存实际 clone、checkout、git apply --check --binary、git apply --binary 的命令/退出码，以及全文件集合、SHA-256 和 Git tree ID 的比较。`checks/independent-review-v1.md` 是另一角色的材料复核。它们只证明当前清单和补丁一致，不证明用户空字段已补齐、官方隐藏测试通过或完成赛事提交。

本题日志副本的逐文件摘要和运行磁盘排除原因见 `checks/log-copy-manifest.json`。截图、HAP、失败日志及实际输出保留；模拟器运行盘不作为工程资源或原始测试日志提交。单列二进制清单见 `changes/binary-resources.json`，内嵌 HAP 资源另由项目已有 `logs/development/verification-build-v4/independent-hap-manifest.json` 审计。

当前主会话原生导出只覆盖 `traces/manifest.json:exported_at` 之前的实际已落盘记录。最终主回复和此后的打包活动尚未发生，不能纳入当前快照。3-package 正式冻结时应重新导出本题原生尾部并保留脱敏记录；如果 project/ 的文件变动，必须重新核对该清单并生成补丁。

完整普通文本/二进制差异首次为1,294,184,961字节，git apply --check --binary 返回128及 patch too large；失败记录在 checks/patch-size-failure-01.json。最终同一完整文件集改用Git压缩二进制补丁表示文本/日志，临时属性仅在镜像.git/info/attributes，未改原工程字节。changes/source-review.diff 另供人读源码/测试/配置差异并忽略纯CR变化，它不是完整交付补丁替代。最终应用不依赖临时属性，仍须逐文件与树模式核验。
