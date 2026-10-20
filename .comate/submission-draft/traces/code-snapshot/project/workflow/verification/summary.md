# vg-spec13 验证结果摘要

同一 v2 冻结源码按每用例最新实际结果合并：{'pass': 17, 'fail': 0, 'error': 0, 'skip': 0}；17 个独立用例。不是单次17/17全套。

- 原始 run02：14 pass / 1 fail（test14 判据过度）；原报告保留。
- run04：test14 精准修正复测及 test15/test16 补充；实际结果见下表。
- run01/run03：interrupted/not_run，均不计通过。
- 全指纹匹配：e463b2682fed306471dc9068eadf9666cc9928c02a297363a334bf70ff7b30d3，逐文件核对 299 项，无差异。

| 用例 | 最新结果 | 原始运行 |
| --- | --- | --- |
| test_00_unsaved_slow_backup_and_repeated_click | pass | run02 |
| test_01_first_entry_and_cancel_without_backup | pass | run02 |
| test_02_current_endpoint_snapshot_and_restart_saved_config | pass | run02 |
| test_03_return_during_pending_then_second_backup | pass | run02 |
| test_04_empty_and_space_fields_no_requests | pass | run02 |
| test_05_restore_cancel_and_close_no_requests | pass | run02 |
| test_06_http_failure_codes_release_busy | pass | run02 |
| test_07_auth_rejection_then_recovery | pass | run02 |
| test_08_network_read_timeout_then_late_response | pass | run02 |
| test_09_connection_refused_releases_busy | pass | run02 |
| test_10_fast_success_and_default_remote_directory | pass | run02 |
| test_11_empty_local_data_structural_backup | pass | run02 |
| test_12_system_return_background_and_inflight_restart | pass | run02 |
| test_13_preflight_snapshot_and_conflicting_controls | pass | run02 |
| test_14_other_testing_task_survives_page_reentry | pass | run04 |
| test_15_other_actions_then_backup_and_failed_reentry | pass | run04 |
| test_16_fast_double_click_single_task | pass | run04 |

A01–A16 明文项均由 run02 核心真实备份取得证据；R01–R10 的已批准可执行分支已覆盖。
未安全注入的本地导出/加密/TaskPool异常仍为 not_run；详细逐项矩阵、原始证据与限制见 final-report.md。
