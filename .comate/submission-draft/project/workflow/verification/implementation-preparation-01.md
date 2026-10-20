# vg-spec8 独立自测准备交接 01

准备会话 `01a14503-a32e-74c1-b3bc-c948f2f304ea`。已核对批准需求和 baseline-notes 哈希，读取公共 harness README/API，按批准方案 §6 的稳定 id 合同准备测试。测试计划先于脚本写入：`workflow/verification/implementation-test-plan-01.md`。

本阶段没有构建、安装、启动/停止应用、连接或操作共享设备，没有读取设备状态。未采集生产源码的最终验收指纹，因为生产编码锁尚未释放。未改生产代码、Spec、state 或公共框架。

## 准备产物

- `hypium_tests/test_restore_confirmation.py`：继承 `HarnessTestCase`；本轮源码/HAP/安装清单和明确 release 门槛；正常入口、10 轮连续取消重开、快速动作、系统返回、页内/路由返回、冷重启、跨 125 s 连续窗口、五字段空/纯空白的已保存/未保存分支、独立继续正控和其后新一轮取消；非空哨兵通过既有创建词书 UI 准备并以本题只读数据库实体快照对比。
- `hypium_tests/verification_support.py`：仅本题文件范围的输入指纹、命令/动作日志、UI 树/截图、本地真实 HTTP mock、全方法连续请求计数、可选本题数据库快照和证据 SHA256。导入模块不会连接设备。
- `hypium_tests/compare_warnings.py`：对照本题基线 764 条告警，用诊断消息及归一化源码语句匹配代码搬移，另存全部本轮定位和新增/消失诊断。
- `hypium_tests/offline_check.py`：只检查自测脚本语法、未释放保护和 mock 全 HTTP 方法计数，不导入设备 harness。

## 已运行的工具校验

命令在本题根目录、同时加载两个指定 Harmony 环境入口后执行：`D:/HCUP/common/.venv/Scripts/python.exe -m hypium_tests.offline_check`，退出码 0。真实 loopback HTTP 服务收到 HEAD、GET、PUT、DELETE、PROPFIND、MKCOL、OPTIONS、POST、TRACE、PATCH 以及非标准 FROB，均记录到服务端日志；release 未设置时保护正确抛错。5 个 Python 文件 AST 解析通过。

完整命令、原始日志、退出码和工具结果在 `logs/implementation-validation/preparation-offline/`。此处 mock 请求全是主机工具自检请求，没有来自被测应用；不得作为产品网络正控或功能通过证据。多次离线准备运行保留各次 mock start/stop 时间点和追加请求日志，没有删除早期工具记录。

## 当前逐需求状态

| 项目 | 结果 | 原因 |
| --- | --- | --- |
| A1、A2、A3、A4、A5、A6、A7、A8、A9、A10、A11、A12、A13、A14、A15、A16、A17、A18、A19 | not_run | 等待主 Agent 冻结生产输入并释放独占共享设备后重新构建、安装和实测。 |
| U1、U2、U3、U4、U5、U6 实现边界/回归 | not_run | 同上；D2 需可安全取得的有效备份，不阻塞核心 Spec 验收。 |

正式运行前须写本轮 `source-fingerprint-before.json` 和 `installation-manifest.json`，包含构建/安装退出码、设备、HAP 路径及 SHA256；同时保存 `bm` 安装前后 updateTime。Python 始终使用 `D:/HCUP/common/.venv/Scripts/python.exe`，不使用环境脚本输出的旧题包解释器。测试期间指纹改变则作废受影响证据，由主 Agent 决策回退。

已告知主 Agent 测试工具的输入键盘行为和数据库复制权限需在释放后的设备上确认；若工具不适配，修自测脚本并保留原始失败，不修改生产逻辑或放宽验收断言。当前没有产品失败或通过结论。
