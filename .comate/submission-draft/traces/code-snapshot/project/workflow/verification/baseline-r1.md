# cml-spec1 独立基线核验 r1

核验时间：2026-10-20 11:16–11:25 +08:00。阶段：分析阶段；仅验证未修改基线。本报告可供主 Agent 合并 `spec/baseline-notes.md`，不等于功能验收完成。

当前结论：**独立 clean / assembleHap 成功；安装、启动、交互和动画验证 blocked（设备占用；独立新实例启动失败）。** 未修改业务代码、Spec、构建配置、公共工具或其他任务；未安装/覆盖/停止任何已有设备上的应用。没有官方评测结论。

## 输入、工具及指纹

- 根目录：`D:/HCUP/cml-spec1`；HEAD `7014cebd60f2181fac2a36d399ca16b3d6a175ab`。
- Spec SHA256 `491ea9b5efe284f449873234ba0c86345a0cc2eece2e097898de06a2c4f59d4b`；metadata SHA256 `8b4f53895d59cc4a74780c9d6d24d80ae59d236965755a7091f92375eb695768`。符合派工批准值。
- 每个 PowerShell 工具进程加载 `D:/hongmengcup/Enter-HarmonyEnv.ps1`；每个构建或设备命令进程另外加载本地覆盖 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。
- DevEco Studio 6.1.0.860；Node v18.20.1；Java JBR 21.0.8；SDK `D:/HarmonyDev/sdk/api23`；Python `D:/HCUP/common/.venv/Scripts/python.exe` 3.12.3。
- 工具定位与版本原始记录：`logs/analysis-baseline-env.json`。
- `traces/baseline-analysis/source-before.json`、`source-after-build.json` 对全部 677 个 tracked 文件逐个 SHA256；构建前后变化为零，`git diff` 空。`source-compare-setup.json` 另与准备阶段指纹比较；此比较仅证明代码相同，不证明功能。
- 指纹汇总：`traces/baseline-analysis/evidence-hashes.json`。源码清单不包含 ignored 的构建缓存或新增记录文档。
- 环境观察 `CODEX_THREAD_ID=01a1574f-c26c-7e20-9ea9-ad83cbe0762a`、`CODEX_SESSION_ID=01a1574d-f7fd-7032-96ff-7fec7f78a664`；仅观察到环境变量，未独立证明前者是本子 Agent 的 native UUID（可能继承，交由主 Agent 核对）。未读取初始化总览会话。

## 独立构建证据

可重跑脚本：`traces/baseline-analysis/build-baseline.ps1`。工作目录均为本题根目录。

| 命令 | UTC 开始/结束 | 退出码 | 原始日志 |
| --- | --- | --- | --- |
| `hvigorw clean --mode module -p product=default -p buildMode=debug --no-daemon` | 03:18:06.423 / 03:18:10.839 | 0 | `logs/analysis-baseline-clean.log` |
| `hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon` | 03:18:10.842 / 03:18:32.588 | 0 | `logs/analysis-baseline-assembleHap.log` |

构建返回 `BUILD SUCCESSFUL in 18 s 633 ms`。先 clean，故不是仅以缓存增量成功代替诊断。准确命令、起止时间和退出码另存 `logs/analysis-baseline-build-results.json`。

实际本轮产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`，19,133,822 bytes；SHA256 `49a5284455f6b6f9c29873da1431d7542bfd233071b67b46e5f52851d68906a4`，详见 `logs/analysis-baseline-hap.json`。准备阶段 HAP 哈希不同；本轮只以本轮重建产物为待装对象。没有以旧 HAP 或其他任务相同 bundle 的已安装应用充当本轮测试。

`build-profile.json5` 中 signingConfigs 为 `[]`，构建明确告警 `No signingConfig found for product default`。这只确认产物未签名；由于设备尚未可用，**未实际尝试安装，不能把安装是否拒绝记为已知结果**。恢复设备后应先测试本轮 HAP，若实际遭签名拒绝，再用本题记录目录内的可逆本地签名流程排查，不改生产配置。

## 既有告警清单

完整诊断逐条含文件、行列和原文：`traces/baseline-analysis/warnings-file-diagnostics.csv` / `.json`；全部 warning 行索引 `warnings-index.txt`；完整上下文以构建原始日志为准。

| 类别 | 本轮数量 | 证据 |
| --- | --- | --- |
| ArkTS 带文件诊断 | 182（project 31，dependency 151） | `warnings-summary.json` |
| Function may throw exceptions. Special handling is required. | 31 | 项目 ContextUtil / PermissionUtils / ImageUtil / NotificationUtil / WindowAdapter 等，准确位置见 CSV |
| arkts-strict-typing-required | 140 | 依赖声明中关闭类型检查注释 |
| arkts-no-implicit-return-types | 8 | 依赖声明 |
| arkts-no-type-query | 2 | 依赖声明 |
| arkts-no-typing-with-this | 1 | 依赖声明 |
| 资源重名 | 原始日志出现 135 次（重复出现次数，非唯一资源数） | `placeholder` / `placeholder_float` 的 base/en 资源冲突；全位置见日志 |
| 重名文件 | 1 组告警 | dayjs.min.js 与 dayjs.min.js?commonjs-entry |
| 缺少 sourceMapsPath | 存在 | @ibestservices/ibest-ui-v2 |
| 未配置签名 | 存在 | product default |

与本题准备阶段 `logs/baseline-build.log` 的 182 条带文件诊断做有序多重集比较，差异为空，记录 `warnings-compare-preparation.json`。未抑制、删除或修复告警；不因既有告警而声称业务失败，也不将成功编译视为 Spec 通过。

## 设备占用与独立实例失败

只读预检：`hdc list targets`，随后对四个 target 执行 `hdc -t <target> shell aa dump -l`；外层工具进程退出 0，原始记录 `logs/analysis-baseline-device-preflight.txt`。四台 target 均有其他任务前台应用：11237 / 11239 / 11241 / 11243。主 Agent 明确要求不占用，故未向这些 target 安装、启动、点击、滑动、停止、清数据。

通过已安装工具 `D:/HarmonyDev/DevEcoStudio-6.1.0/tools/emulator/Emulator.exe -help` 获取 CLI 文档（`logs/analysis-baseline-emulator-help.log`）。`-imageList -downloaded true -imageRoot D:/HarmonyDev/emulator/images` 返回已下载 `HarmonyOS 6.1.0(23)` / 6.1.0.115；`-screenProfileList -deviceType Phone -details` 返回 Pura 90 Pro Max / 1308×2880 / 560dpi / 6.9 inch，两个命令退出 0，分别记录 images / profiles 日志。

创建命令（退出 0，返回 Device create success）：

```powershell
Emulator.exe -create CmlSpec1Baseline -deviceType Phone -osVersion 'HarmonyOS 6.1.0(23)' -instancePath D:/HCUP/cml-spec1/traces/baseline-analysis/emulator-instances -imageRoot D:/HarmonyDev/emulator/images -screenProfile 'Pura 90 Pro Max' -memory 2 -storage 6 -hotBoot false
```

启动前检查端口 11245 未被占用；用 `Start-Process -WindowStyle Hidden -PassThru` 启动，参数为：

```text
-start CmlSpec1Baseline -instancePath D:/HCUP/cml-spec1/traces/baseline-analysis/emulator-instances -imageRoot D:/HarmonyDev/emulator/images -hdcPort 11245 -bootmode coldboot
```

启动命令、进程号、stdout/stderr 记录在 `logs/analysis-baseline-emulator-start-*`；该异步启动没有取得子进程退出码（**未知，不能记 0**）。进程 14116 数秒后退出；hdc 始终仅原四台，未出现 11245。

最小复现：保留现有四台运行，执行上面的独立实例创建/启动命令。期望：独立 11245 在线并可供安装；实际：启动崩溃，无 target。

直接证据（本题独立实例日志）：

- `traces/baseline-analysis/emulator-instances/CmlSpec1Baseline/Log/Emulator.log`：11:20:31.931 主机剩余内存 1385MB，小于 3GB 提示；11:20:37.033 MinidumpCB。
- 同目录 `qemu.log`：11:20:36.665 `CreateFiber failed`。
- 实例 config.ini：2GB RAM（CLI 文档允许的最小值）、API23、PHEMU-FD00、1308×2880、560dpi。
- 主机 Win32_OperatingSystem：TotalVisibleMemorySize 16,483,540KB，崩溃后 FreePhysicalMemory 2,313,588KB。

归因假设：主机内存/提交资源不足导致新 emulator 的 fiber 创建失败；**中等证据**（相关日志很强，但未排除其他 native 资源限制）。无证据支持改业务代码。建议退回环境协调，释放一台已有模拟器或提供可用 target；由主 Agent 决策。独立实例创建仅写本题 traces 下实例数据，未修改公共镜像，也未停止其他实例。

## 逐 Spec 步骤运行状态

此处使用 `S<场景>.<步骤>` 作为本报告局部编号，主 Agent 可映射至正式验收矩阵。全部交互未执行；下表 blocked 的统一原因是无获授权可用 target。静态资源/调用存在也不据此记 runtime pass。

| 编号 | 可观察要求 | 状态 | 原因/待采证据 |
| --- | --- | --- | --- |
| S1.1 | 启动后显示首页、分类、购物车、我的四标签 | blocked | 待本轮 HAP 安装/启动、UI dump、全屏截图 |
| S1.2 | 首页默认选中且内容显示 | blocked | 待初始页面状态和选中态观测 |
| S1.3 | 点击分类切换对应内容 | blocked | 待点击前后树与截图 |
| S1.4 | 分类 Lottie、图标黑色，其余灰色重置 | blocked | 待帧序列/颜色证据，静态截图不足证明动画 |
| S1.5 | 点击购物车切换内容并播放图标动画 | blocked | 内容与动画分开断言 |
| S2.1 | 首页向左滑到分类 | blocked | 待内容区横向 swipe 与页面证据 |
| S2.2 | 滑动后分类联动高亮并动画 | blocked | 待页面/底栏同步与动态帧 |
| S2.3 | 继续左滑切换购物车 | blocked | 待第二次 swipe 证据 |
| S2.4 | 点击我的切换内容并图标动画 | blocked | 待对应内容/高亮/动态帧 |
| S3.1 | 首次初始化首页自动 Lottie | blocked | 待从本轮 app 冷启动开始的动态录制；后补截图不充分 |
| S3.2 | 我的播放，首页回第一帧静止 | blocked | 待两图标动态/终帧对比 |
| S3.3 | 返回首页图标重播 | blocked | 待点击前后动态图像 |
| S3.4 | 首页内容显示且标签文字黑色 | blocked | 待 UI/像素采样，不能仅用选中字段替代颜色 |
| S4.1 | 已选首页，下滑至优惠券领取滚出视区 | blocked | 待真实数据、滚动和领取可见性前置验证 |
| S4.2 | 重复点击已选首页 | blocked | 待保持首页前置，避免误测他页返回 |
| S4.3 | 自动回顶、优惠券领取重新可见 | blocked | 前置不满足时须 blocked，不可强行通过 |
| S4.4 | 保持选中，无切页动画/额外 Lottie | blocked | 待动态采样；无动画为负向断言，截图不足证明 |

附加边界（重复点击、快速切换、左右边界、后台再回、重启）本轮 not_run；未到正式实现回归阶段。网络、登录和真实首页数据可达性尚未验证。未生成伪造 UI dump/截图，没有动画通过结论。

## 构建生成改动与恢复入口

- tracked 文件和生产配置变化：0；构建生成 `**/build`、`.hvigor` 缓存/产物单独视为工具生成，未提交。
- 本自测写入范围：`workflow/verification/baseline-r1.md`、`traces/baseline-analysis/`、`logs/analysis-baseline-*`。
- 独立 emulator 实例及 crash 日志仅在本题 traces，进程已自行退出。未删原始证据。
- 恢复后应再次对 677 个 tracked 文件与 source-before 做指纹对比；若变动，相关证据作废并重建。指定获授权 target、安装本轮 HAP、保存 install/launch 命令退出码与设备规格，然后操作四场景。需要真实动画记录或可验证帧状态；若无法断言则保持 blocked/not_run，不能以静态阅读或成功构建补齐。
