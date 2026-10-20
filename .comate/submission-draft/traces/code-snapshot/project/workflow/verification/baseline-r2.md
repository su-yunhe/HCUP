# cml-spec1 独立基线设备核验 r2

时间：2026-10-20 11:29–11:31 +08:00；阶段：分析阶段，生产代码/Spec/配置未修改。

结论：**设备运行验证仍 blocked**。仅执行设备占用只读查询；未安装、启动、点击、滑动或读取其他任务应用 UI。未重复启动上轮已崩溃的独立实例。原 r1 clean/build 证据仍适用于相同源码与 HAP；不把成功构建算作功能完成。

## 本轮指纹复核

- HEAD `7014cebd60f2181fac2a36d399ca16b3d6a175ab`；tracked diff 空。
- 全部 677 个 tracked 文件逐一 SHA256，与 r1 `source-before.json` 差异为零，见 `traces/baseline-analysis/r2/source-before.json`、`source-comparison.json`。
- 待装 HAP 仍为 r1 独立构建产物 `entry/build/default/outputs/default/entry-default-unsigned.hap`；SHA256 `49a5284455f6b6f9c29873da1431d7542bfd233071b67b46e5f52851d68906a4`。
- Spec/metadata/HAP/指纹文件本轮哈希汇总 `traces/baseline-analysis/r2/evidence-hashes.json`。

## 只读命令、退出码与原始记录

所有 PowerShell 工具进程加载 `D:/hongmengcup/Enter-HarmonyEnv.ps1`；设备命令前另外加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。工作目录均为 `D:/HCUP/cml-spec1`。

| 时间（UTC） | 命令 | 退出码 | 原始结果文件 |
| --- | --- | --- | --- |
| 03:29:09.193 | `hdc list targets` | 0 | `logs/analysis-baseline-r2-devices.json` |
| 03:29:09.534 | `hdc -t 127.0.0.1:11237 shell aa dump -l` | 0 | `logs/analysis-baseline-r2-occupation-127_0_0_1_11237.json` |
| 03:29:09.740 | `hdc -t 127.0.0.1:11239 shell aa dump -l` | 0 | `logs/analysis-baseline-r2-occupation-127_0_0_1_11239.json` |
| 03:29:10.145 | `hdc -t 127.0.0.1:11241 shell aa dump -l` | 0 | `logs/analysis-baseline-r2-occupation-127_0_0_1_11241.json` |
| 03:29:10.391 | `hdc -t 127.0.0.1:11243 shell aa dump -l` | 0 | `logs/analysis-baseline-r2-occupation-127_0_0_1_11243.json` |

四台仍各有其他任务前台应用。占用查询只取系统 mission 元数据，未读取其他任务源码、应用 UI 树或应用内容。主 Agent 尚未分配任一已有 target，不能把相同 bundle 名视为本题产物，也不能根据应用看似空闲推断已释放。

系统只读资源查询 `Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory` 随外层工具进程退出 0，原始结果 `logs/analysis-baseline-r2-memory.json`：

- TotalVisibleMemorySize：16,483,540 KB。
- FreePhysicalMemory：1,140,244 KB（约 1.09 GiB）。

查询 `Get-CimInstance Win32_Process -Filter "Name='Emulator.exe'"` 后只保留命令行含 `CmlSpec1Baseline` 的本题进程：匹配列表为空，详见 `logs/analysis-baseline-r2-own-process.json`。hdc 不含本题预留 11245；专用实例没有自行恢复。

## 为什么本轮不再重试独立实例

r1 本题专用实例创建成功，但以 2GB 启动时崩溃：自己的 `Emulator.log` 记主机剩余 1385MB / 小于 3GB 告警，随后 minidump；自己的 `qemu.log` 记 `CreateFiber failed`。完整证据与重现命令见 `workflow/verification/baseline-r1.md` 及本题实例 Log。

安装工具自带 `-help` 的 `-memory` 明文范围为 2–32 GB（日志 `logs/analysis-baseline-emulator-help.log`），自己的 config.ini 已是 `hw.ramSize=2048`。本轮专用实例配置快照保留在 `traces/baseline-analysis/r2/own-emulator-config.txt`。因此没有比现有 2GB 更低的**文档支持**内存配置；当前空闲内存还低于 r1，未进行无新条件的重复启动，也未修改共享镜像、主机内存配置或其他实例。

归因假设保持为主机内存/提交资源不足（中等证据），不把假设写成已证明根因。该阻断与业务代码无直接关联。

## 逐需求状态

| Spec 步骤 | 本轮状态 | 缺少的运行证据 |
| --- | --- | --- |
| S1.1 四标签显示 | blocked | 本轮 HAP 安装启动后的 dump/截图 |
| S1.2 首页默认选中/内容 | blocked | 同上 |
| S1.3 分类点击切页 | blocked | 点击前后页面证据 |
| S1.4 分类动画/黑灰颜色重置 | blocked | 动态帧/颜色；截图单帧不够证明动画 |
| S1.5 购物车切页/动画 | blocked | 页面与动态图标 |
| S2.1 首页左滑分类 | blocked | swipe 与页面观测 |
| S2.2 底栏联动/分类动画 | blocked | 同步选中态/动态图标 |
| S2.3 再左滑购物车 | blocked | 第二次 swipe |
| S2.4 点击我的/动画 | blocked | 页面与动态图标 |
| S3.1 首次首页自动动画 | blocked | 从冷启动开始的动态观测 |
| S3.2 我的动画/首页第一帧静止 | blocked | 动态与终帧证据 |
| S3.3 首页返回重播 | blocked | 动态证据 |
| S3.4 首页内容/文字黑色 | blocked | 页面与颜色 |
| S4.1 滚动后领取不可见前置 | blocked | 真实首页数据与滚动前置 |
| S4.2 点击已选首页 | blocked | 保持已选首页的前置 |
| S4.3 回顶/领取重新可见 | blocked | 点击前后可见性与位置 |
| S4.4 保持选中/无切页及重播 | blocked | 负向动画断言需动态采样 |

附加边界操作仍 not_run。未实际安装，因此未证实 unsigned HAP 是否会被当前模拟器拒绝；签名仅为恢复后待检查项。没有可用运行环境，故本轮没有应用截图/UI dump；缺证据不记通过。

## 最小外部操作与恢复入口

由主 Agent 协调完成下面任一项即可继续，无需改业务代码：

1. 明确把一台现有 target 交给本题独占使用，并授权安装覆盖相同 bundle 的本轮基线；保留其余实例不受影响。
2. 若需维持独立实例，让对应任务所有者停掉一台其他模拟器，释放主机内存；随后允许本题重新启动已创建的 `CmlSpec1Baseline`（11245）。只退出前台 app 通常不足以释放 emulator 的主体内存，不能据此认为资源已满足。

获得可用设备后，先重新核对源码/HAP 指纹与占用，记录安装/启动命令退出码及设备规格，再采集首屏、底栏点击、横向滑动、首页重入、滚动后重复点首页的 UI/截图/动态证据。若签名或服务数据阻断，继续如实分层报告，不降低断言。
