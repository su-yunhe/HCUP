# cml-spec24 单题提交材料

本轮完成2-submit材料整理；业务代码、资源和构建配置未修改。1-do的896个冻结文件再次核对无变化。当前是单题草稿，团队/人工空字段仍待补齐；未执行3-package、生成成果ZIP、上传或赛事提交。

- [仍需用户补充的字段](pending-fields.md)：10个空字段均保留【待补充】，另列客观记录缺口。
- [已自动填写的事实及出处](automatically-filled-facts.md)：每项事实链接真实工程、原生轨迹或日志。
- [后续打包契约](packaging-contract.md)：必须按工程清单物化project，保留本题过程文件，排除输出自包含和运行缓存。

## 主要材料

|文件|用途|
|---|---|
|[build.md](build.md)|依赖、构建、安装启动、初始化和自测命令；无本机私有绝对路径依赖|
|[trace-index.md](trace-index.md)|官方24字段、Codex引擎/IDE双ID逐项映射、模型/参数、任务书版本、脱敏和缺失|
|[solution.fragment.md](solution.fragment.md)|完成情况、AI参与、失败重试、局限及人工待补声明|
|[sources.fragment.md](sources.fragment.md)|基线、额外来源事实、检索行为及待核声明|
|[submission.json.fragment](submission.json.fragment)|本题相对路径JSON条目，供3-package汇总|
|changes/final.diff|完整可应用Git二进制补丁，覆盖全部清单文件|
|[changes/source-review.diff](changes/source-review.diff)|供人阅读的源码/测试/配置差异，忽略纯CR变化；不能代替完整补丁|
|[changes/project-manifest.json](changes/project-manifest.json)|完整工程文件SHA-256、模式、排除项及理由|
|[changes/binary-resources.json](changes/binary-resources.json)|二进制资源大小/SHA-256及68项基线同内容匹配|
|[changes/binary-diff-files.json](changes/binary-diff-files.json)|1050个实际二进制差异文件；未把压缩编码的文本误称资源|
|traces/|15个相关会话原生明细、真实过滤索引、Markdown副本、源码快照索引|
|logs/|15815个保留证据文件的副本，约1.098GB，含失败和重试|

## 已运行校验

完整基线为 `ab3dc7cd5d05a9a3fd7d4e9ddd0a49e1a05085d8`。主流程实际执行隔离clone、checkout、`git apply --check --binary`、`git apply --binary`，均退出0；对全部 **16970** 个文件集合和SHA-256比对一致，Git树ID/文件模式一致。临时Git关闭autocrlf，保留原工作区字节；未修改原Git索引或全局配置。

- project技术快照：`4c6693b5ae2c84b32e50a20eab4ada81b0a7e7247cf8137b1f435eeda2159d65`。
- 应用前预期树 = 应用后树：`4f9c2cff69b4ca8c2af427055a11bb9007115ea7`。
- final.diff：946,836,934字节，SHA-256 `21ecbc727bfe439bd529991289091f8d57ad439e226c5127598044a7d01b1a11`。
- 主校验证据：[checks/diff-verification.json](checks/diff-verification.json)。
- 另一角色的新clone独立check/apply及全部16970文件的源件/应用件大小、SHA、模式核验也通过，树ID与主流程一致；[checks/independent-review-v1.md](checks/independent-review-v1.md)，原始命令/退出码/结果见[checks/independent-apply-v1/result.json](checks/independent-apply-v1/result.json)。
- 日志副本：原件、复制件和清单逐项大小/SHA全部一致；[checks/log-copy-manifest.json](checks/log-copy-manifest.json)。
- 源码未改：[checks/source-integrity.json](checks/source-integrity.json)。

首次宿主运行日志变化F01、共享worktree本地clone范围问题、普通1.29GB补丁被Git以patch too large拒绝F02均保留真实记录，分别见checks/log-freeze-failure-01.json、clone-attempt-01.json、patch-size-failure-01.json及原生轨迹。最终补丁只改变表示方式：临时镜像Git属性使文本/日志也压缩编码，不改任何交付字节；独立应用无需这些属性。先前失败副本/补丁与验证工程保留在排除的submission-check内。

## 记录范围及剩余限制

本题登记研发/材料会话15份均找到；混题初始化总览和其他工作区会话排除，初始化仅引用本题原始准备日志/provenance。session_index真实只有3个主会话行，子会话由本题manifest和只读IDE线程筛选表关联；未伪造Comate字段或侧栏导出。

缺失的官方指定baseline log未补造，本题prepare-baseline及构建日志可用。Comate存储/产品文件未发现，实际为Codex；用户原生Markdown导出目录未提供。脱敏仅移除一条工具返回中的非本题会话ID/cwd元数据，行号与原始SHA见traces/redactions.json。当前主会话是当时快照，不包含导出后的未来事件与最终答复，3-package冻结时须补齐实际已发生尾部。

正常12项、受控9方法两轮组合、host14项、本地76项验收均引用1-do既有证据，本轮未重跑构建/设备。仅x86_64 API23运行，arm64仅构建；受控数据源不等同物理网络故障；截断App响应与独立oracle分开；隐藏用例及官方成绩未取得。技术快照时间不代替用户填写的团队成果冻结时间。

最终原生导出快照时间：`2026-10-19T07:31:32.253762+00:00` UTC；当前主会话未来尾部不在该快照中。材料全文件清单为 material-manifest.json（该清单不包含自身）。
