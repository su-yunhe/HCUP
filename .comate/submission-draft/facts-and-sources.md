# 已自动填入的事实及出处

| 事实 | 核实来源 |
| --- | --- |
| 团队 `HC2026-111`、队名 `Ghost_London`、阶段 `online` | 只读 common/spec-harness/team.yaml |
| 题号 vg-spec9，基线 `a22f32b07bf81c6dde4367e2543ebac29186cbc1`，bundle `repo_bundles/vignette-a22f32b07b-base.bundle` | spec/submit-input.yaml、spec/metadata.json、Git基线对象 |
| bundleName io.qzz.weiyu，EntryAbility，versionName 1.0.0 / code1000000 | AppScope/app.json5、entry/src/main/module.json5 |
| product default，module entry，buildMode debug，SDK声明6.0.2(22)，未签名 | build-profile.json5、hvigor配置、独立Build-command.log |
| ArkTS开发依赖Hypium1.0.24、Hamock1.0.0，Python Hypium6.1.0.210 | oh-package.json5/锁文件、test-harness/requirements.txt、原生验证工具输出 |
| 独立构建/安装成功，12唯一最终有效用例通过；失败与重试仍保留 | logs/四入口、分轮raw_report、workflow/verification/round-02-final-report.md、checks/prior-evidence-review.md |
| 当前251项运行指纹和5份生产冻结文件一致，真实LoadingProgress与请求重叠 | 既有原始指纹、checks/prior-evidence-review.md的本轮静态复核 |
| HAP 8983170字节、SHA256 `b367da84359ad19ba9fad5e808f864fe06c10280850332da1c11615a8efe70b6` | 当前HAP文件、先前构建/安装哈希、changes/binary-files.json |
| 10个本题原生线程：8解题+2材料；主ID与侧边栏对应，子ID关联父sidebar | 两维文件名检索、session_meta、过滤session_index、本题workflow登记；traces/session-map.md |
| Codex CLI 0.162.0-alpha.17.2，模型gpt-6.1-sol，effort xhigh；逐线程原生token | 原生header、turn_context、最后token_count；traces/token-usage.md |
| common当前Git HEAD `e9befa727bcd94f2eea263bd3c92c56d9f8ec6ac`、四任务书内容摘要、本题history不存在 | 只读common Git与四文件、spec/history存在性；taskbook-version.md |
| 全工程快照 `1b5799251641879b65b9daed9c3a8073439773ab7f0692901ecd6103c81921e3`，776文件，补丁可应用且全字节还原 | changes/project-manifest.json、checks/diff-validation.json |
| 二进制路径/大小/SHA256及与同路径官方基线是否同源 | 逐文件字节与本地Git基线blob比较；changes/binary-files.* |
| 复制全部现有logs且摘要一致 | checks/copied-log-manifest.json |
| Comate库和指定基线报告缺失；初始化总览不作本题研发证据；字段空值 | 文件存在性、本题state的初始化purpose、真实输入YAML；未用推测补齐 |
