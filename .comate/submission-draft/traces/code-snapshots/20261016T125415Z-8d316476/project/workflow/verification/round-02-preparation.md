# vg-spec9 独立验证准备

角色原生会话：`01a14492-d90e-7c23-aa1e-0deef1467f23`。仅在本题编写验证文件，读取 `common/test-harness`；未改生产、Spec、调度状态，未创建子 Agent。准备阶段尚未获得源码冻结与模拟器独占，因此未构建、安装或运行设备测试。

输入为批准的 `spec/requirement.md`、`metadata.json`、`acceptance.md`、`baseline-notes.md`，以及本轮 `workflow/requirements/round-02-implementation-review.md`、`workflow/implementation/orchestrator-decisions.md`、`workflow/design/round-01-plan.md`。测试沿正常导航文本 `⚙` → `WebDAV 配置`，返回用 `←`；目标组件使用方案 §5 的实际稳定 ID，不要求未实现的建议导航 ID。

## 准备检查

- `traces/implementation-validation/preparation/read-only-environment.log` 保存 `hdc list targets`、`hdc fport ls`、`hdc shell bm dump -n io.qzz.weiyu`，退出码均为 0。在线设备为 `127.0.0.1:5555`，原 `18769 → 18769 [Reverse]` 仍存在；本轮未改变映射、未尝试绕过先前被拒的清理操作。此查询不证明当前安装产物属于本轮。
- `python-and-fixture-check.log`、`python-and-fixture-recheck.log` 保存 Python 编译、框架发现和主机夹具协议检查，退出码为 0；可发现 10 组继承 `HarnessTestCase` 的测试。主机检查只证明夹具的认证／HTTP403／HEAD／GET404／PUT真实存储／GET读回／DELETE／重定向和目录创建协议，不能计作应用验收通过。
- 服务仅绑定 `127.0.0.1`，使用本轮合成凭据；每个场景使用独立远端根目录。日志记录请求、认证匹配布尔值、内容长度与 SHA256、响应状态及接收／完成时间，保留应用实际 PUT 字节。普通成功夹具允许现有词条和事件 GET404 代表远端初始为空，并可读回应用真实上传的加密内容。

## 待执行覆盖

| 测试 | 验收与策略 | 准备阶段状态 |
| --- | --- | --- |
| test_01 | A1—A15，有效成功、指定组件类型/可见性与真实请求重叠，多阶段采样 | not_run |
| test_02 | A16、B10，HTTP403后终态恢复，改正并真实成功重试 | not_run |
| test_03 | A17/A18、B5—B7，空远端、快连点、busy中重复、终态后新轮 | not_run |
| test_04 | B3/B4/B9/B11/B12，未点同步的编辑/收起键盘/保存/返回/冷启动 | not_run |
| test_05 | B1/B2，四项必填字段分别空值/纯空格后的终态恢复 | not_run |
| test_06 | A14、B9/B13，7层新目录递归准备、每条8s、总时长>120s | not_run |
| test_07 | 已采用U4、B11，在途标题返回再入并绑定同轮 | not_run |
| test_08 | B1/B2，空/空格目录沿用默认，地址/账号两端空格沿用trim | not_run |
| test_09 | A16/B10，连接拒绝与有效端点重试 | not_run |
| test_10 | 已采用U6、B15，在途编辑下一轮、五个提交按钮busy拒绝 | not_run |

未新增同步取消按钮、启动确认框或分页需求，三者分别不适用。只测试连接的归因、密码中空格、系统返回再入、运行中force-stop和自动任务竞争没有从本准备脚本推称覆盖；后两者按主 Agent 定位为扩展探索。A17 的“本地无增量”须由实际协议及应用日志补证，不能仅因远端为空或再次点击就宣布。

## 执行与证据规则

主 Agent 确认源码冻结与设备租用后，使用 `run_frozen_validation.ps1 -Action Build -RunId <round>` 重新构建；随后 `-Action Run` 每次先安装刚构建HAP，再在本题 `logs/` 运行 `harness.runner`。调用进程设置 `VGSPEC9_SOURCE_FROZEN=1`。所有 PowerShell 进程先加载两份指定环境入口。脚本保存命令、退出码、源码前后指纹、原始输出、框架 JSON；HAP SHA256 与基线告警差分另入最终报告。

测试在首个服务请求保持窗口核验实际 `LoadingProgress` 类型、ID、可见性、屏幕范围和截图，同时核对请求尚未完成。长流程不依赖旧包装超时，也不挂起单条请求120秒；沿原递归父目录 HEAD/.keep PUT/recheck，所有响应延迟8秒。首/中/末请求持续取证；最终界面按实际可见性判断隐藏，允许隐藏组件保留在树中。

每个测试前后以及完整轮次前后核对工程指纹；变化将使相关证据失效。测试失败保留最小复现、期望/实际、关联A/B、原始日志及归因强度，交主 Agent 决策，验证角色不改生产代码或删除断言。
