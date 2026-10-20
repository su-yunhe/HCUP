# 已自动填写的事实及出处

|事实|出处|
|---|---|
|HC2026-111 / Ghost_London / online|common/spec-harness/team.yaml（用户已填字段）|
|cml-spec24 与完整 base_commit|spec/metadata.json、workflow/baseline-provenance.json|
|官方三个模板与四份任务书 SHA-256、common仓库HEAD、未发现spec/history|facts/official-inputs.json、facts/harness-version.json|
|bundle、入口、模块、SDK目标、依赖/锁、真实构建参数与产物|AppScope/app.json5、entry/src/*/module.json5、build-profile.json5、oh-package*.json5、logs命令；归纳见build.md|
|实际模型、effort、工具调用、累计token、原生UUID与IDE ID|traces/manifest.json、traces/ide-threads.filtered.json、逐会话原生JSONL|
|当前桌面包版本、历史CLI版本与Comate文件不存在|facts/client-version.json、每会话session_meta|
|1-do的12/9/14测试结果、76项本地验收、范围限制|workflow/development-result.json、development-verification-v5.md及原始logs|
|896个冻结文件本轮未变|checks/source-integrity.json、workflow/final-code-fingerprint-v2.json|
|完整差异、交付文件清单、二进制大小/SHA与同源比对|changes/final.diff、project-manifest.json、binary-resources.json、binary-diff-files.json|
|日志逐文件副本与排除的运行缓存|checks/log-copy-manifest.json|
|基线clone后check/apply及全树字节一致|checks/diff-verification.json、checks/independent-review-v1.md|
|失败/重试/检索行为、脱敏说明|原生轨迹、workflow报告、traces/redactions.json、sources.fragment.md|

这些事实不补全人工声明、不代表官方评分或来源合规裁决。工程物化与补丁边界以packaging-contract.md为准。
