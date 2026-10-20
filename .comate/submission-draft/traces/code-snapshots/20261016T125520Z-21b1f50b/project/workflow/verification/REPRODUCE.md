# vg-spec9 本地独立验收复现

先由主 Agent 确认本题生产源码暂停编辑并租用共享设备 `127.0.0.1:5555`。测试有 freeze guard，环境变量不是取消该协作约束的替代品。

在本题目录的新 PowerShell 执行：

```powershell
. 'D:/hongmengcup/Enter-HarmonyEnv.ps1'
. 'D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1'
Set-Location -LiteralPath 'D:/HCUP/vg-spec9'
$env:VGSPEC9_SOURCE_FROZEN = '1'
$env:VGSPEC9_TESTS = ''
& './workflow/verification/run_frozen_validation.ps1' -Action Build -RunId 'replay-all'
& './workflow/verification/run_frozen_validation.ps1' -Action Run -RunId 'replay-all'
```

不设置筛选或令 `VGSPEC9_TESTS=''` 会发现全部 12 项；`VGSPEC9_TESTS='10,11,12'` 只运行指定编号，其余仍是该轮未执行，不能计该轮通过。正常整轮较长，包含真实264秒左右的目录准备链以及逐字段输入和多次冷启动。

脚本始终在每次 runner 前真实安装本题新构建 HAP，再到 `logs/` 运行框架。其等价环境／运行命令如下：

```powershell
$env:HDC_DEVICE = '127.0.0.1:5555'
$env:PYTHONPATH = 'D:/HCUP/common/test-harness;D:/HCUP/vg-spec9'
$env:VGSPEC9_EVIDENCE = 'D:/HCUP/vg-spec9/traces/implementation-validation/replay-all'
$env:VGSPEC9_PORT = '18769'
# 使用已保留的 18769 -> 18769 Reverse 映射；不重试此前被拒的 fport 清理。
hdc -t 127.0.0.1:5555 install -r 'D:/HCUP/vg-spec9/entry/build/default/outputs/default/entry-default-unsigned.hap'
Set-Location -LiteralPath 'D:/HCUP/vg-spec9/logs'
& 'D:/HCUP/common/.venv/Scripts/python.exe' -m harness.runner --project 'D:/HCUP/vg-spec9' --device '127.0.0.1:5555' --json 'D:/HCUP/vg-spec9/traces/implementation-validation/replay-all/selftest.json'
```

`run_frozen_validation.ps1` 自动设置 HDC_DEVICE、PYTHONPATH 和 VGSPEC9_EVIDENCE；省略 VGSPEC9_PORT 时默认18769。服务随测试类在宿主loopback启动和正常close，不创建外部长期后台服务。必须保证设备到宿主该端口可达，端口未被其他服务占用；没有映射时先由主 Agent 协调设备环境，不对被拒命令做绕过。

证据目录保存源码指纹、实际使用测试源码、命令与退出码、原始UI树／截图／请求日志／上传字节和框架JSON。测试会拒绝无真实请求、非 LoadingProgress 类型、不可见加载、加载与未完成请求不重叠以及测试期生产源码变化；无效配置与连接失败只用于恢复回归，不能替代有效端点成功主路径。

最终本轮入口为 `logs/build.log`、`logs/install.log`、`logs/selftest.log`、`logs/selftest.json`，这些汇总保留分轮原报告引用。`traces/implementation-validation/round02-t1` 是首次测试脚本参数错误的历史，未删除、未计通过；T10的旧首闸风险以修正夹具的补测为最终依据。官方隐藏评测不可见；本地结果不是官方成绩。
