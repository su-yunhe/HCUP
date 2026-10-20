# cml-spec7 独立材料验证

结果：fail；真实 CODEX_THREAD_ID=01a15914-c10a-7f52-8c6b-5180f42bb365。

本报告只校验材料及既有功能证据对应关系；未重跑构建、设备或功能测试。生产文件与测试按字节核对。

| 检查 | 状态 | 证据 |
| --- | --- | --- |
| production_and_tests_unchanged | pass | production-before.json |
| final_verification_source_identity | pass | workflow/verification/final-evidence-fingerprint-03.json |
| hap_and_matrix_identity | pass | facts.json; logs/verification-final-03.json |
| matrix_observation_paths | pass | logs/verification-final-03.json |
| logs_copy_complete_and_exact | pass | logs-copy-manifest.json |
| logs_exclusions_are_declared_runtime_disks | pass | logs-copy-manifest.json |
| failed_round_and_rejection_preserved | pass | ['logs/verification-closeout-03/temporary-disk-cleanup-rejected.json', 'logs/verification-final-03.json', 'logs/verification-phone-suite-02/hypium-runner.stderr.txt'] |
| native_two_dimension_discovery | fail | traces/native-discovery-search.json; traces/discovery.json |
| native_metadata_latest_cumulative_and_identity | pass | traces/session-metadata.json; traces/native/*.jsonl |
| project | not_run | Pending material file |
| documents | not_run | Pending material file |
| audit_inputs_stable | pass | SHA-256 at first read and final report |

全部命令、退出码、stdout/stderr、各会话ID/父ID、原始行数、输入SHA-256及失败详情见同名JSON。

待解决：B9/B10/B11外部接入条件、空白人工/团队声明、正式冻结时间/提交选择、已声明的原始日志及ID缺口。当前草案不代表整题完成或正式提交。
