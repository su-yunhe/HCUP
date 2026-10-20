# 自动填入的事实及出处

以下是技术事实，用户未提供的人工声明/团队字段仍在pending-fields中。

|自动事实|出处|
|---|---|
|题号cml-spec28、官方base_commit与baseline_bundle标识|spec/metadata.json；workflow/baseline-provenance.json|
|团队HC2026-111、Ghost_London、online|只读common/spec-harness/team.yaml，读取摘要见pending-fields；未写回|
|正式10源码827文件聚合3eaa1310…、HAP 8,658,451B/51761093…|正式10冻结清单、boundary-phone-result-10.json、validation/business-frozen-before.json|
|实际clean成功、234/175诊断无新增|workflow/implementation/boundary-phone-formal-build-10.log、warnings-formal10.json及标准build.log|
|正式原六项1pass5AUTHskip、原测试7893587e…、进程开关=1|formal10-final-02的result/version-mapping/invocation；未在材料阶段重测|
|有限31主参数按08十五/09六/10十、额外10三项|boundary-completion-matrix.json、boundary-completion-01.json、需求终审|
|原始失败/重试/撤回结果、测试表达修正、脚本说明文字指纹漂移|原run目录、boundary-g4-01-timeout-audit、boundary-script-drift-01、workflow/events|
|当前root引擎UUID与app threadId均01a14f53-1fa0-72d2-b947-fa27e7fb37c7|workflow/submit-app-thread-proof.json的实际工具返回及session_meta；旧侧栏ID未推断|
|材料核查时桌面26.1013.40934/build20770/prod、OHPM6.1.1.830|reference/app-version-probe.json与ohpm-version-probe.json，只说明当前已安装值，不倒推历史|
|16个去重本题会话，native模型gpt-6.1-sol、effort=xhigh、runner0.163.0-alpha.10.2|traces/manifest.json及每份原生session_meta/turn_context；不是桌面产品版本或计费统计|
|Skill/角色/任务书配置及当前导出方法|本题system-config、trace-index、原始native；common四任务书SHA与本题history情况见trace-index|
|受控fixture独立bundle/loopback/SQLite、服务/Reverse清理与正式包恢复|boundary-completion-01.json、final-cleanup-01、final-environment-audit-01|
|通用地区数据@ibestservices/area-data0.0.6及Apache-2.0、官方API查阅|sources.fragment.md、development-sources.json、third_party许可、对应设计记录|
|106份已有日志逐字节复制，16份raw及完整Markdown派生副本|logs/manifest.json、traces/manifest.json及原导出审计|
|二进制资源/证据的实际路径、大小、SHA、基线同源标识|changes/binary-manifest.json；不是推测外部来源|
|完整差异是否可应用及canonical项目逐字节一致性|validation/patch-01的实际结果；生成前不预填通过|
|所有业务/资源/配置及原测试未因材料整理改变|validation/business-frozen-before.json与最终after/独立审查|

官方指定基线报告缺失、Comate索引不存在、opaque加密字段不可解密、历史桌面产品版本/旧侧栏ID缺证均据实标明。原首失败构建预指纹和旧完整结果JSON副本缺口保留。没有填“无人工修改”“无额外来源”“正式AUTH通过”或团队正式冻结时间。
