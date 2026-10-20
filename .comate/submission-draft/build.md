# vg-spec8 构建与运行

本题项目目录为成果包内 `tasks/vg-spec8/project/`；在该目录执行以下命令。构建App不依赖参赛电脑的私有环境脚本。工具由使用者安装并加入 PATH。

## 环境与依赖

实测工具：DevEco Studio 6.1.0.860，SDK 6.1.0.105 / API 23；工程 targetSdkVersion、compatibleSdkVersion 为 `6.0.2(22)`。Node 18.20.1、JBR/OpenJDK 21.0.8、Hvigor 6.23.7、HDC 3.2.0c。设备为 API 23、系统6.1.0.115、1308×2880模拟器。OHPM与Python的历史精确版本尚未核实，记【待补充】，不得猜测。

根 `oh-package.json5` 与 `oh-package-lock.json5` 固定 `@ohos/hypium 1.0.24`、`@ohos/hamock 1.0.0`，锁版本3。entry模块没有新增外部依赖。安装依赖、构建：

```powershell
ohpm install
hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon
```

若系统使用 `hvigorw` 命令，去掉 `.bat` 后缀即可；需先配置SDK、JDK、Node与OHPM工具环境。原始构建记录见 `logs/implementation-validation/round-01/build-clean-assembleHap.log`，exit0；764条既有ArkTS告警，新增0。生产源码未在材料阶段重建或修改。

## 安装和启动

应用 `io.qzz.weiyu`，模块 `entry`，入口 `EntryAbility`，版本1.0.0。调试产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。原项目签名配置为空，实测模拟器允许此unsigned HAP；其他设备如需签名，须使用其合法配置，包内没有私钥。

```powershell
hdc list targets
$device = '127.0.0.1:5555' # 改为实际列出的目标序列号
hdc -t $device install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t $device shell bm dump -n io.qzz.weiyu
hdc -t $device shell aa start -a EntryAbility -b io.qzz.weiyu
```

安装需同时检查成功文本和bm updateTime，不能只信退出码；实测某些HDC文件路径失败时仍返回0。被测HAP SHA256 为 `c30a83a3523e83ee77db7ba8a827ca781aad5cd0d4f2669de293fef19b4bf229`，材料 `artifacts/` 保留该产物。

## 初始化与手工复现

首次安装如出现隐私/引导，按实际页面完成；本题功能不要求应用账号登录。首页齿轮→设置→「WebDAV 配置」，滚动到手动操作区。可先使用空配置验证确认与取消；证明网络门槛时应保存有效、可达的独立测试端点，并持久关闭自动同步，确保没有在途请求。

点击「从云端恢复」，观察第一层「取消／继续」。点击「取消」后弹层关闭、仍回到WebDAV操作区，恢复按钮原文且可用；再次打开、反复取消，未明确点本轮「继续」前所有HTTP方法累计请求应为0。系统返回/遮罩关闭亦不授权。不要点击测试连接、同步或备份污染计数。独立点「继续」后才允许现有下载/预览流程，云端无备份时可返回原有失败结果；后续覆盖确认保持原行为。

## 自测证据和复现边界

本地Python Hypium为6.1.0.210，测试类继承公共HarnessTestCase。工程保留 `test-harness/` 框架副本、`hypium_tests/`、逐轮原始日志、测试脚本快照和源码/安装清单。完整轮4pass/2skip，补测4pass/0skip，合并6个唯一方法均有真实pass。20个空/空格保存与未保存边界、重复点击、返回/重启、空数据、非空哨兵及真实请求正控均有记录。

**自动脚本移植限制**：`hypium_tests/run_validation.ps1` 含开发机工具/工程路径，`verification_support.py` 另有固定ROOT检查和本轮manifest/HAP/源码指纹门槛。它们原样保留以对应历史证据，不能仅换成相对runner命令就声称任意目录可自动重跑。本阶段禁止修改脚本；后续适配须单独完成并重测。App本身可使用上述PATH命令构建、安装、手工复现。

未测：官方隐藏用例、D2预览取消/完整成功恢复、自动同步并发。自动同步关闭是本地测量隔离前置，不是全局并发零请求的证明。
