# vg-spec1 本地独立验证

在本题工程根、所有源码编辑者已停止修改、本题专用模拟器独占时执行：

```powershell
pwsh -File hypium_tests/run_verification.ps1 -SourceFrozen -RunName ("selftest-" + (Get-Date -Format yyyyMMdd-HHmmss))
```

脚本加载本题工具环境，独立 clean 构建，记录源码/HAP 指纹，重新安装刚构建 HAP，生成并设置 `VG_VERIFICATION_MANIFEST`，随后在日志目录调用标准 `python -m harness.runner --project D:/HCUP/vg-spec1 --device 127.0.0.1:11235 --json .../selftest.json`。每次重跑用新的 RunName 保留日志。脚本不接受跳过为通过，最终必须 0 skip；源码中途变化会令本轮失败并作废证据。

首次运行需本题专用模拟器已有自动同步关闭和仅本题合成数据；准备过程见 `workflow/verification/preparation-01.md`。13 个测试中第一项对本题 bundle 清数据后重装、走首次使用和空数据场景，再经现有本地 JSON 导入恢复合成 fixture。不要在真实用户设备运行此组测试。

直接执行标准 runner 时若没有由上述流程产生的新安装 manifest，测试类会明确报错并提示运行脚本，不会静默整类 skip 或伪报通过。没有固定 `settings_page` 根 id 依赖。

`run_verification.ps1` 仅交付可重复入口。编写/语法检查不代表已运行正式构建或验收；本轮实际状态以 workflow/verification 报告为准。
