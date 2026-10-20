# cml-spec17 已自动填入的事实及出处

本文件使用本题已有原始证据和 `evidence-facts.json`。该事实文件可能随本轮会话继续采集；会话数、token、最后事件及摘要须以最终导出清单为准，不把早期快照当全程最终记录。

| 自动事实 | 值或定位 | 证据出处 |
| --- | --- | --- |
| 题目/团队/阶段 | cml-spec17；HC2026-111；Ghost_London；online | project/spec/submit-input.yaml；公共team.yaml已读取字段 |
| 官方基线 | d6a6ba7480fbd0a30075462e46bb4344a430ba61 | project/spec/metadata.json |
| 随包基线元数据标识 | repo_bundles/coolmallarkts-d6a6ba7480-base.bundle，仅引用本题元数据，未读取bundle | project/spec/metadata.json |
| 本地基线准备 | profile=harmony-cup-build-v1；dry_run=false；changes=[]；setup记录prepared_at=2026-10-19T07:45:09.347162+00:00；基线构建exit0 | project/logs/prepare-baseline.log；project/workflow/setup-result.json；project/logs/baseline-build.log |
| 指定官方baseline日志 | 精确路径不存在；本地日志不是该官方日志 | evidence-facts.json / official_baseline_log |
| 生产bundle与入口 | com.joker.coolmall；entry；EntryAbility | project/AppScope/app.json5；project/entry/src/main/module.json5 |
| 工程SDK声明与签名 | target/compatible 6.0.1(21)；signingConfigs=[] | project/build-profile.json5 |
| 依赖/构建 | ohpm install --all；hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug assembleHap --no-daemon | project/oh-package.json5及各锁文件；project/logs/implementation-ohpm-install-01.log；project/logs/do-production-01/independent-build-command.txt |
| 产物位置 | entry/build/default/outputs/default/entry-default-unsigned.hap | project/workflow/do-stage-result-03.json；build.md |
| 生产HAP摘要与大小 | 5b835ea1f7b436e6b03234b86d88b48b5812a223d1052e08cb54b08dd6d4e8d3；9,489,353字节 | project/workflow/do-stage-result-03.json |
| 生产文件集 | 844文件；aggregate=2278a77074b39f8d97067beb853d7880bb91d3586dbf228992ffba2d9ccb03b5；采集drift=[] | project/workflow/do-implementation-fingerprint-02.json；evidence-facts.json / production_fingerprint |
| 本地验证结果 | 正常23、故障3，唯一method去重26；42项受控需求样本；2项普通guard另列 | project/workflow/do-stage-result-03.json；project/workflow/verification/do-results-03.md/.json |
| 未验证范围 | 9项not_run、authenticated-live-backend blocked、official_hidden_test_result unknown | 同上；solution.fragment.md逐项披露 |
| 失败与修复 | implementation-build-01/02/03→04；do-01重试；do-03的E03/D02失败→fix-02→do-04回归 | project/logs/；project/workflow/verification/do-results-02.md；project/workflow/implementation/do-implementation-02.md |
| 客户端/原生版本 | Codex Desktop Windows Appx 26.1013.4894.0；CLI 0.163.0-alpha.10.2 | traces/client-version.json（Get-AppxPackage OpenAI.Codex原输出）；evidence-facts.json / native_sessions[].originator、cli_version |
| 模型/effort | 已采集contexts为gpt-6.1-sol / xhigh；逐会话以实际contexts为准 | evidence-facts.json / native_sessions[].contexts |
| token口径 | 每会话last_reported_token_info为最后原生累计快照；非跨父子/压缩可相加的账单用量；context window非使用量 | evidence-facts.json / native_sessions[]及各原生token_count事件 |
| 主/子原生与侧边栏ID | 每会话native_id、sidebar_id、对应依据、真实parent_thread_id；不生成Comate UUID | evidence-facts.json / native_sessions[]；traces/过滤索引；trace-index.md |
| 轨迹选择与截点 | 题号及工作区多种表示分别检索，排除无关命中/跨题初始化总览；仅复制完整JSONL行；不包含未来事件 | evidence-facts.json / search、excluded_search_hits、snapshot_only、includes_future_events；traces/采集清单 |
| Markdown及日志 | Markdown程序从原生派生、非侧边栏导出；日志逐项源/副本大小与SHA-256 | evidence-facts.json / native_sessions[].markdown、copied_logs[] |
| 任务书仓库版本 | e9befa727bcd94f2eea263bd3c92c56d9f8ec6ac；本地四任务书摘要与公共副本相同；spec/history不存在 | evidence-facts.json / harness |
| 实际规则、工具和配置 | 原生工具序列及系统/开发提示；本题system-config快照；appliedRuleNames缺席不能解释为无规则 | project/system-config/；各原生JSONL；evidence-facts.json |
| 完整工程最终版本 | changes/project-files.json中的精确冻结清单、聚合摘要与tree OID；不是当前HEAD或生产844摘要 | changes/project-files.json |
| 全量差异/二进制/回放 | final.diff；binary-files.json；实际check/apply和全集比较结果 | changes/final.diff；changes/binary-files.json；changes/validation.json |
| project与材料边界 | D=.comate/submission-draft不递归入project；其他真实过程保留；运行态/总览raw及缓存有明确排除 | changes/project-files.json；changes/excluded-files.json；trace-index.md |
| 清单候选路径 | tasks/cml-spec17/project；tasks/cml-spec17/build.md；tasks/cml-spec17/trace-index.md | submission.json.fragment（submitted仅为拟提交候选） |

四任务书 SHA-256：

| 文件 | SHA-256 |
| --- | --- |
| 0-analyze.md | a0518cb663406e9a25c2a8096799ddbb79253e1f874819b6099a38c2819c944a |
| 1-do.md | 2f02be9274ea7e68e7863a319382fc250a9ea845fa5fa0c124effc5524ee337d |
| 2-submit.md | 43455fc9ef3c6d0ddbcf0dc101201796ebec865e214929f3137b1bb4036895f9 |
| 3-package.md | 3a97a8072042c29adde571af04da1658d0b1547e9c41cdd649e02fba04ae6b9c |

用户空字段与客观缺项分别列在missing-fields.md；已观察事实不替代用户人工/额外来源声明，也不形成官方材料实质通过或评分结论。
