# cml-spec7 实施与本地验证交接

当前源码的本地明确验收条目为38项通过、3项阻断。构建、安装、冷启动和适用回归已经完成；三方真实授权尚未完成，因此本题不能标记全部完成或 `local_validation_complete`。逐项矩阵与证据见 `workflow/verification/final-verification-03.md`、`logs/verification-final-03.json`。

## 实施范围

沿用指定基线 `75fd0066a7fc0c1e8cedb6218df081f86d307f45` 的真实“我的”登录入口、路由、ViewModel、Logo、主题与窗口断点。实现登录主页、两种登录方式目标页导航、三方品牌图标及标签、独立协议链接、底部逐字文案与100%/70%/60%自适应。两份用户授权原创本地协议可离线阅读，已经需求角色事实复核。

生产变更为14个文件，见 `workflow/implementation/source-fingerprint-01.json` 及后续交接02/03。最终布局采用方案01+02，入口去重采用方案03；14文件最终聚合 SHA256 为 `cac8fa6d77121e87efb2e40913b74ed564c0eeac9cc9fa23151382cfd89c0a9b`。没有新增SDK依赖、改写共享网络/路由契约或伪造认证数据。

## 当前冻结产物

- 独立全量构建产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。
- HAP SHA256：`8aaa5de48b5664b92210fad7ffcddf9abbcebbb92e52faf7f5359bbeb3611863`。
- 验证角色完整生产输入聚合 SHA256：`26307326248e8e874d1e2d8c3a4abf10e14008d5fd386b91682357a928f6f78e`。它与上述14文件聚合范围不同，不混用。
- 构建命令、退出码、源码首尾指纹、测试代码归档和安装记录均保存在各 `logs/verification-*-03/` 目录。

## 实测结果

| 范围 | 结果与证据 |
| --- | --- |
| 独立全量构建 | `logs/verification-navigation-smoke-03/build.json`，退出码0。与基线按路径、完整告警消息及出现次数比较，ArkTS告警207→207，无新增；资源冲突与其他原有告警未增加。 |
| 入口与返回重进 | `verification-navigation-smoke-03` 2/2通过；同进程正常返回、入口连点、头像连点各一轮，均确认稳定完整窗口，而非页面过渡帧。 |
| 手机全量用例 | `verification-phone-suite-03` 原始39通过、8跳过、1测试错误。跳过含B9–B11真实授权、非本窗口的C2–C5及另行分配的旋转测试。唯一错误是测试库滑动方向参数大小写，下一行定向修复验证通过，原始失败保留。 |
| 两份正文与滚动终点 | 修正测试调用为大写方向后，`verification-documents-03` 3/3通过；两份不同正文均实际滑至末尾，根直接检查可读终点截图。 |
| 手机短横屏 | `verification-phone-rotation-03` 1/1通过；真实旋转到822.857vp，验证70%布局和页脚可滚动显示，再恢复方向。 |
| 平板800vp | `verification-tablet-subset-03` 19通过、3项尺寸不适用跳过；实际窗口1600px、Density2，区域1120/1600=70%，水平居中。 |
| 大屏1200vp | `verification-large-geometry-03` C4–C7四项全部通过；实际窗口2400px、Density2，区域1440/2400=60%，中心1200px，三图标中心间隔448px且均不越界。 |

`verification-large-subset-03` 的22项原始记录实际仍在800vp（19通过、3尺寸不适用跳过）：权限设置流程曾重置预设方向。它按实际平板证据保存，未冒充大屏。随后将测试旋转移至权限处理后，才获得上述真实1200vp四项补测。C6/C7最终通过必须且已经覆盖手机、平板、大屏三类窗口。

全部适用断言通过后未继续扩大测试；没有隐藏用例或官方分数。共享测试框架未修改；当前源码的有效03验证轮次生产输入保持不变，早期02b并发改源诊断明确作废。测试工具修复均在轮次结束后进行，各轮归档实际脚本及首尾哈希。当前 `hypium_tests/test_login_acceptance.py` 提供41条明确需求及关键导航/边界检查，继承只读公共 `HarnessTestCase`。

## 命令和复核位置

所有构建、设备命令先加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。实际独立构建为：

```powershell
hvigorw --mode module -p product=default -p module=entry@default -p buildMode=debug clean assembleHap --no-daemon --no-incremental
```

受控自测入口为 `workflow/verification/run-verified-round.ps1`：每轮先校验当前生产源码与锁定HAP哈希、重新安装本题HAP，再调用Hypium，并归档安装、stdout/stderr、树、截图、真实WMS窗口、密度与测试代码。各轮实际完整命令/退出码见对应 `hypium-runner.json` 与 `install.json`；构建记录见 `build.json`。禁止将旧轮HAP或目录名称当作当前设备/尺寸依据。

构建生成的生产输入变化为空；根复核 `git diff --check` 通过，`logs/final-build-noise-check.json` 的BuildProfile噪声计数为0。工作流、规格输入、日志、Hypium脚本和原始会话记录均保留在本题目录。

两设备方向恢复0，任务专用大屏实例已停止，原共享手机实例仍Connected且其配置哈希不变。停止后的临时磁盘清理被工具自动审批拒绝（`blocked by policy`），未执行删除，约914MB生成磁盘及配置仍保留于 `logs/verification-emulator/instances/CmlSpec7_Layout`；详见 `logs/verification-closeout-03/temporary-disk-cleanup-rejected.json`。没有换用其他机制重试删除。

## 真实限制

用户最后确认没有第三方开发者账号。B9/B10/B11的微信、QQ、支付宝真实授权流程尚未完成，当前只有可点击入口、准确的不可用反馈与恢复；不将该分支算作真实登录通过。后续需要平台签发应用身份、签名/回调登记和确认的服务端凭据交换契约，见 `workflow/implementation/third-party-setup.md`、`workflow/provider-research-01.md`。

未执行已登录用户的个人资料分支、恰好600/840vp断点、拖拽窗口调整及真实平台账户授权；没有抓包证明网络请求数量。登录主页没有文本输入或分页，空输入/纯空格与分页终止不适用；实际两种目标页导航和正文滚动已验证。手机号及账号页本题仅要求跳转，本次未扩展完整认证表单。原创协议为用户授权的本地应用说明，并非平台或运营主体签发文件。

两个已修复回归及原始失败均保留：标题/返回覆盖状态栏（方案02修复）；返回“我的”后持久防重锁未释放（方案03修复，同进程三轮返回/入口和头像连点最小回归已通过）。首轮PNG采集限制、过渡帧假阳性和测试滚动方向大小写错误分别保留在验证记录；旧版或无效证据不用于新源码通过判断。

本地验收矩阵的条数不代表官方F-point数量或分值；没有访问官方隐藏脚本或获得官方评分。没有对外提交、发布或创建PR。
