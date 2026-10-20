# cml-spec28 2-submit 独立终审

当前**冻结候选的技术材料审查通过**，可由 Root 保存末次五会话并收束本次材料整理。该结论不等于 1-do 完成、正式功能全通过、材料无例外满足全部官方规则或已完成 3-package/上传。正式 AUTH 仍 blocked；用户仅明确授权越过 2-submit 的 1-do 前置进行材料整理。

审计角色 `submit_verification`；实际 `CODEX_THREAD_ID=01a14f55-5f14-7860-976f-10407965f444`（本轮环境直接读取）。范围为本题工程、只读 common/team 输入及官方三个模板；只在本目录写派生审计结果。未构建、安装、操作设备、启动服务、重跑完整 apply，未改生产、原测试、原 DB、canonical 或冻结清单内文件。

|核验项|状态|独立核实结果及证据|
|---|---|---|
|业务冻结保护|pass|正式10清单827项逐文件SHA一致，HAP及原六项测试SHA一致；before/after均为同一正式10，AUTH与1-do状态未改变。见 [technical-summary.json](technical-summary.json)。|
|完整范围|pass（有明示例外）|tracked、正常untracked及AGENTS覆盖，包含spec/hypium/workflow/logs/traces/.comate过程材料；10029项唯一安全相对路径。manifest与冻结副本SHA相同。见 [byte-parity.json](byte-parity.json)、[project-scope.md](../../changes/project-scope.md)。|
|补丁真实生成与应用|pass|读取成功run的30条真实Git命令，均exit0；逐份复算stdout/stderr大小与SHA。含临时生成器`diff --cached --binary --full-index`、另一clone的`apply --check --binary`及实际`apply --binary`。本角色未重新apply。见 [git-command-evidence.json](git-command-evidence.json)、[原始result.json](../patch-01/result.json)。|
|完整工程字节对应|pass|独立复算原现场及canonical全部10029项尺寸/SHA，均与manifest一致；canonical排除.git后10029项、无额外/缺失；总1197521463 bytes。见逐文件 [byte-parity.json](byte-parity.json)。|
|clone与原Git保护|pass|独立只读核两个clone仅可达已知base9a1d…和prepared b75…，refs仅本题分支及其origin；两个HEAD均为base。原HEAD/branch与staged逻辑指纹未变，不读取共享物理index。见 [repository-guards.json](repository-guards.json)。|
|二进制清单|pass|669个保守清单项的路径/大小/SHA均在manifest并经全字节验证；清单含已知后缀、NUL或非UTF8前缀判定，可能保守包含文本，不等于669个Git binary块。基线同源标记保留。见 [binary-summary.json](binary-summary.json)。|
|SQLite/WAL|pass|在本角色独立复制的91个audit副本上运行integrity_check，全部ok；5个非空WAL与主DB均入manifest。检查复制前后原件及canonical SHA/mtime不变；原件和canonical从未通过SQLite连接。原实现91组稳定复制/完整性证据亦逐项核对。见 [sqlite-independent.json](sqlite-independent.json)。|
|既有日志与原生轨迹|pass（限已采集时点）|106日志原件/材料副本/canonical SHA与大小一致；16个去重本题native/Markdown指纹及native首行id/cwd一致。未打开两份初始化总览raw正文，未访问外部native原件。见 [logs-native-parity.json](logs-native-parity.json)。|
|官方字段/路径/版本|pass|官方24个trace字段齐全；13个空输入均【待补充】；fragment为not_completed，三个路径用包内相对路径，后两项为文件；8份材料合计60个Markdown链接核查，trace-index的41个链接全部可按包布局解析。build无私有绝对路径依赖。见 [materials-fields-links.json](materials-fields-links.json)。|
|材料复跑入口|pass（静态）|安装前device==原模块DEVICE(11239)；out为工程内新目录；六例/原SHA/827源校验；只配置EVIDENCE输出并复用同模块；旧证据指纹保护；skip返回2。AST解析通过，本角色未执行该入口；新机复现及新正式验收为not_run。|
|末次五材料会话|not_run|本审计结束后由Root导出，须单独核原生/Markdown摘要、截取边界与索引；不得预称已覆盖未来事件。此项不反写冻结project或diff。|
|真实正式AUTH|blocked|既有正式10-final-02原六例为1pass、5AUTHskip；没有新合法会话/真实服务端到端验收，不把skip记pass。|
|3-package/团队最终声明|not_run/待补|本阶段无团队ZIP、上传或正式提交。13字段与声明/记录缺口仍需在最终材料如实保留。|

## 精确交付身份

- 官方base：`9a1d608dc89acfc301657c33ce5dd6089cbf9572`；准备HEAD：`b75aa21fdb29af1d3d00aa313360da85c6e05e4f`。
- manifest：`changes/project-files.json`，10029项，SHA256 `5ae3a07bf9a438352996379e8e84ff0375bad7186673059d1daa6d08f85d7405`；路径+NUL+SHA+LF聚合 `55b1d20a106fb42d57ee3a629a5243f7d4530cc419975defa804185da7f74404`。
- final.diff：767891670 bytes，SHA256 `37e5b0a0bdf8e4885cd93f5ddeffd89ea220ab2f911b34057273d5bd1be0955f`，两副本独立复算一致。
- canonical：`validation/patch-01/20261019T024945.263008Z/reconstructed-project`。3-package的project必须从该树去掉.git并按manifest复制，不能复制继续增长的现场工作树。
- 正式10源827聚合：`3eaa13107c4b8d83485fa473c8f83a42bedb8498783faa0539de4a9f12c0fa1c`；HAP `51761093a48478502e5aac6f8e40678d00e1ed470c38c3c18140086cb8fad229`，8658451 bytes；原测试 `7893587e2eeb59a7d91b366621d6791cf46f95aa474e450581a494cb8955ef7f`。
- 原staged逻辑SHA：`7ca4fad85b039541b7f29f2a2707b03ee3b68a05741c454ae39216031b6bff81`。这是`git ls-files --stage -z`输出指纹，不是物理index字节声明。

## 必须保留的范围例外与剩余项

完整diff按**明示冻结范围**与canonical逐字节对应；不声称diff包含自身。排除依赖/构建缓存、.git、live emulator磁盘、空WAL/SHM/临时journal、两份按UUID文件名识别的初始化raw，以及自引用final.diff/project-files/excluded-files、validation派生树和末次materials-final导出。5个非空WAL作为已停止写入的成套静态证据保留，不等同仍写数据库临时文件。实际580项排除与理由已在excluded-files清单；不隐藏这些例外。

validation报告及末次会话记录在冻结project之外随材料交付；3-package按reports-only选择审计附件，不复制generator/reconstructed/.git/临时SQLite审计大树。材料内生成前的阶段用语保留，实际通过结论由本派生审计及Root最终汇总共同说明，避免修改冻结材料造成递归。

仍待用户提供13项：human_edits、known_issues、extra_sources、md_export_dir；team.version、contact、freeze_time、members[0].name、members[0].work、source_guard、submitted_tasks、attempted_not_submitted、zip_out。不得从空串/空列表补成“无”，不得把本次快照时间当团队冻结时间。

其他已披露缺口继续保留：官方同题基线原日志未找到；首失败构建精确预指纹缺失；旧fixture完整结果JSON独立副本未找到；旧IDE侧栏ID/历史客户端版本未充分取得；Comate原生索引缺失而实际使用Codex；opaque/encrypted字段未解密；账户标识/本机路径及最终脱敏声明需在外部打包前处理。当前root的实际侧栏映射证据与其他旧映射待补分开，不伪造双ID。

版本表述经核对：主31为08十五＋09六＋10十，额外RG09/R10三项单列；旧R3十、状态45、日志同11种双角色复跑分别保留，不算22种或正式全通过。旧失败/重试及首轮patch边界保护失败`20261019T023714.993699Z`原件仍在，未翻记pass。

本次审计工具首次误用binary清单键files/entries而实际为items，停下后仅修validation续跑脚本，复用已完成全量散列，最终exit0；一次附加统计打印误读bytes字段也保留在原生工具记录。材料未因此发生修改或重跑apply。实际通过附件为本目录technical-summary、byte-parity、git-command-evidence、repository-guards、binary-summary、sqlite-independent、logs-native-parity、materials-fields-links及review.json。
