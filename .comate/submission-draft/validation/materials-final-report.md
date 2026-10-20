# cml-spec28：2-submit 材料整理交付说明

用户明确授权在保留 AUTH 阻断的条件下整理材料，并要求不再改业务代码。本次已完成可核技术材料的整理与校验；**1-do 未完成正式整体验收，AUTH 仍 blocked，原六项为 1 pass、5 AUTH skip**。没有新构建、设备复测、团队 ZIP 或对外提交，业务、资源、配置及原测试未改。

## 材料校验的实际结果

|项目|结果及证据|
|---|---|
|完整工程冻结|10029 文件，1,197,521,463 字节；[逐文件清单](../changes/project-files.json)|
|完整补丁|767,891,670 字节；SHA-256 `37e5b0a0bdf8e4885cd93f5ddeffd89ea220ab2f911b34057273d5bd1be0955f`；[final.diff](../changes/final.diff)|
|基线重建|基线 `9a1d608dc89acfc301657c33ce5dd6089cbf9572`；两个受限 clone 只含获准的基线和准备提交；30 条 Git 命令均 exit0，包含 `git apply --check --binary` 和实际 apply；[原始结果](patch-01/result.json)|
|逐文件核对|生成副本、重建副本与冻结清单全部一致；独立审核另复算原树与重建副本的全部 10029 文件，无 missing/extra/mismatch；[独立终审](independent-final-01/review.md)|
|二进制清单|669 个保守清单项，含路径、大小、摘要及可核基线同源信息；采用前缀等判定，**不等于 Git binary 块数量**；[清单](../changes/binary-manifest.json)|
|SQLite 证据|5 组非空 WAL，共 16,595,520 字节，随对应主 DB 保存；编码与独立审核各自只打开一次性审计副本，91 组完整性均 ok，原件及 canonical 的 DB/WAL 摘要和 mtime 稳定|
|业务保护|正式10的827文件差异0；HAP 8,658,451 字节、SHA-256 `51761093a48478502e5aac6f8e40678d00e1ed470c38c3c18140086cb8fad229`；原测试 SHA-256 `7893587e2eeb59a7d91b366621d6791cf46f95aa474e450581a494cb8955ef7f`；[前](business-frozen-before.json)/[后](business-frozen-after.json)|
|Git 原件保护|HEAD `b75aa21fdb29af1d3d00aa313360da85c6e05e4f`、分支 `cml-spec28` 及暂存条目逻辑 SHA-256 前后一致；没有宣称校验了共享 Git 管理目录物理 index 的所有字节/标志|
|已有材料|106 份日志摘要一致；初始16个本题会话 raw/Markdown 摘要一致；官方24字段、13项用户待填字段及8份材料合计60链接经独立核对，trace-index的41链接均可解析；[Root复核](root-materials-integrity.json)|

首轮材料校验因 linked worktree 的 Git 管理路径超出题目目录而被保护拦下，未开始冻结；[首轮失败原件](patch-01/20261019T023714.993699Z/result.json)及旧工具保留。第二轮改为本题暂存条目逻辑指纹保护和受限本地文件传输 clone，校验通过。独立审计工具的 schema 适配失败及后续修正也在其审计记录中保留。材料通过仅证明声明范围的重建一致性。

## 各次测试的版本边界

|已有测试层|实际版本与结论|
|---|---|
|主31中全集/空集/导航/pending/迟到读取|正式08 / app-r3，15 pass|
|主31中六参数真实客户端超时|正式09 / app-r4，6 pass|
|主31中历史字段/输入/六接口缺 code|正式10 / app-r5，10 pass|
|额外明确失败恢复、长旧号改坏还原及数字输入/IME|正式10 / app-r5，3 pass|
|最终原六项|正式10，1 pass、5 AUTH skip；runner exit0不表示全部通过|

主31与额外3合计34个有限 fixture 唯一 case，跨实际版本，未称正式10全套重跑。旧 R3 十例、08实际源码状态45、09日志11种场景分别保留，不累加为正式服务通过率或官方分数。失败、重试、测试表达修正、曾撤回的超时判断、formal10-final-01 的4 AUTH加1协调 guard 与后续 formal10-final-02 的5 AUTH均保持原记录。

逐 case 的版本/包身份及原 run 见冻结工程的 `workflow/verification/boundary-completion-matrix.json`、`workflow/verification/boundary-completion-01.md` 和 `traces/boundary-completion/verification/`。历史阶段另见 `workflow/verification/fixture-ui-result.md`、`workflow/verification/development-result.md`。本次未产生新的应用测试结果。

## 末次材料会话快照与范围例外

初始 [16会话清单](../traces/manifest.json)保持不变；另保存 [末次5个材料会话](../traces/materials-final/manifest.json)，共 8,926 条完整原生记录，29,796,516 字节 raw 和 31,833,669 字节 Markdown，末尾未完成记录排除字节为0。5个会话均为已登记本题 UUID，元数据 cwd/ID、逐行解析、raw/MD摘要、Markdown逐事件序号及源文件相同前缀已由Root核对：[补充审计](materials-final-export-audit.json)。该补充完成独立终审 SM09 的待办；独立终审原报告保留其当时 not_run 状态。

这5份是16个唯一会话中当前5份的更新时点副本，**不相加成21个会话**。它们只覆盖各自实际采集时点，不包含未来收尾事件，时间不冒充团队正式 freeze_time。它们是 Codex 原生记录与完整逐事件 Markdown 派生副本，不是 Comate 或 IDE 侧栏明文导出；opaque 加密字段未解密、未删除，原始本机路径和账号标识仍存在。官方要求的旧侧栏 ID/历史客户端版本缺证仍披露。

完整工程的范围及例外在冻结前已声明：[scope](../changes/project-scope.md)、[exclusions](../changes/excluded-files.json)。补丁及清单自身、validation派生输出、末次材料记录不递归进入项目；live模拟器镜像、缓存、空WAL/SHM/临时journal及两份已知混合初始化总览 raw 排除，初始化 raw 只按文件名排除、未读正文。没有声称毫无例外满足自包含要求。

**3-package 的 project 来源只能是** `validation/patch-01/20261019T024945.263008Z/reconstructed-project`，去掉 `.git`，与冻结清单对应；不能复制继续增长的真实工作树。最终 workflow 状态、此说明和末次材料快照为冻结后的外部审计附件。validation只带报告及必要审计附件，不拷 generator/reconstructed/SQLite审计临时大树；末次5份记录独立映射到包根 `traces/cml-spec28/materials-final/`。详见 [布局](../materials-layout.json)。

## 仍需补充的字段与记录缺口

完整字段见 [pending-fields.md](../pending-fields.md)：题目级 `human_edits`、`known_issues`、`extra_sources`、`md_export_dir`；团队级 `version`、`contact`、`freeze_time`、成员姓名/分工、`source_guard`、`submitted_tasks`、`attempted_not_submitted`、`zip_out`，共13项。空白不代表“无”，没有自动填入用户声明或最终提交选择。候选条目仍 `not_completed`，不代表团队决定放弃提交。

冻结前待补表中的完整 diff、末次5会话导出等技术待办现由本报告和实际结果补齐；13项用户字段不受此更新影响。AUTH 合法会话、真实服务端到端验收继续未完成。官方指定本题基线报告未找到；首失败构建精确预构建全源指纹和独立完整旧 fixture-matrix 结果 JSON 副本仍缺失；脚本两处说明文字漂移已有原生 FileChange 还原证据，但不声称旧完整结果逐字节对比。

## 已自动填入的事实及其出处

完整清单见 [facts-and-sources.md](../facts-and-sources.md)，包括本题基线、应用标识、依赖与许可、已有构建/测试/各版本指纹、真实会话/模型/工具/规则、当前客户端与 OHPM 查询值、日志拷贝和未改业务的证据。完整差异、SQLite配套与末次会话的最终自动事实由本报告补充；最终交付摘要和材料哈希见同目录 `delivery-manifest.json`。
