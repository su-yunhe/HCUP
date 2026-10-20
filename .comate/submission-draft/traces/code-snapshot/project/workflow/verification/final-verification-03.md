# cml-spec7 独立自测最终报告 03

结论：41项明文原子中 **38 pass、3 blocked、0 fail、0 not_run**。blocked仅B9/B10/B11真实第三方登录；没有平台签发的合法配置/账号条件，不能把不可用提示冒充授权启动。此为本地验收，不是隐藏测试或官方成绩。

自测角色 `/root/verification_do`，CODEX_THREAD_ID `01a158d3-1977-7490-b337-d28df9f59e73`；只写本题测试/验证记录，不改生产、Spec或全局state。

生产输入SHA256：`26307326248e8e874d1e2d8c3a4abf10e14008d5fd386b91682357a928f6f78e`。锁定独立全量构建HAP SHA256：`8aaa5de48b5664b92210fad7ffcddf9abbcebbb92e52faf7f5359bbeb3611863`。每一轮均重新安装此产物，并分别验证生产/测试助手首尾指纹一致；测试源码副本和SHA保存在各round的 `test-code/` 和 `test-code-fingerprint-before/after.json`。

## 原始运行统计

下表是实际脚本case数量，不能与41项合并矩阵混淆；未选用例见各子集selection.json，不记为pass。

| round | 实际执行/选择 | pass | fail/error | skip |
| --- | ---: | ---: | ---: | ---: |
| [verification-navigation-smoke-03](../../logs/verification-navigation-smoke-03/selftest.json) | 2 | 2 | 0 | 0 |
| [verification-phone-suite-03](../../logs/verification-phone-suite-03/selftest.json) | 48 | 39 | 1 | 8 |
| [verification-documents-03](../../logs/verification-documents-03/selftest.json) | 3 | 3 | 0 | 0 |
| [verification-phone-rotation-03](../../logs/verification-phone-rotation-03/selftest.json) | 1 | 1 | 0 | 0 |
| [verification-tablet-subset-03](../../logs/verification-tablet-subset-03/selftest.json) | 22 | 19 | 0 | 3 |
| [verification-large-subset-03](../../logs/verification-large-subset-03/selftest.json) | 22 | 19 | 0 | 3 |
| [verification-large-geometry-03](../../logs/verification-large-geometry-03/selftest.json) | 4 | 4 | 0 | 0 |

手机48case的唯一error是测试助手将Hypium滑动方向写成小写up；原始异常完整保留。结束该轮后仅修为官方API要求的UP/DOWN，重新安装同HAP，正文专项3/3及手机短横屏1/1通过；没有删除正文/滚动断言，也没有重跑无关普通case。手机8skip为B9–B11外部条件、C2–C5当前尺寸不适用、D5未派旋转；后者已由单独真实短横屏轮补齐。

名为verification-large-subset-03的22case轮实际仍是800vp平板窗口：首启权限设置将提前设置的横屏恢复竖屏，C4/C5按实际MD明确skip。该轮原始结果保留，绝不按目录名算大屏。结束后把请求方向应用时机改到权限处理、稳定登录页之后，新装同HAP仅补C4/C5/C6/C7；verification-large-geometry-03四项均在真实1200vp通过。

## 三类真实窗口

| 类别 | WMS窗口/Density | content宽px | region宽px | 比例/中心 | 证据 |
| --- | --- | ---: | ---: | --- | --- |
| 手机 | 1308px / 3.5 = 373.714vp | 1308 | 1308 | 100%；中心一致（≤1物理px舍入） | [test_C01](../../logs/verification-phone-suite-03/test_C01.observations.json) |
| 平板窗口 | 1600px / 2.0 = 800.000vp | 1600 | 1120 | 70%；中心一致（≤1物理px舍入） | [test_C02](../../logs/verification-tablet-subset-03/test_C02.observations.json) |
| 大屏窗口 | 2400px / 2.0 = 1200.000vp | 2400 | 1440 | 60%；中心一致（≤1物理px舍入） | [test_C04](../../logs/verification-large-geometry-03/test_C04.observations.json) |

U1按真实WMS窗口逻辑宽分类；U3比例与Logo中心固定以扣安全区、业务padding前的auth_login_content为基准，同时保留window/page/content/region原始边界。Logo三类窗口120×120vp均由实际边界与DMS密度换算；图标间距/包含关系C6/C7只在三类各有pass后合并。没有注入bp或用设备名称替代窗口。

临时CmlSpec7_Layout采用当前官方Phone/API23镜像的独立任务配置，实际1600×2400/Density2（800vp），真实旋转为2400×1600（1200vp）；不是冒称另一官方平板机型。手机另有373.714→822.857vp短横屏，UP滚动至完整页脚、70%比例/图标间距通过，方向恢复证据及像素review齐全。未额外测拖拽resize或600/840vp等值边界；不宣称这些派生边界已执行。

## 41项逐项结果

| 原子项 | 状态 | 主要证据 |
| --- | --- | --- |
| A1 | pass | [verification-navigation-smoke-03](../../logs/verification-navigation-smoke-03/test_A01.observations.json)；[verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A01.observations.json) |
| A2 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A02.observations.json) |
| A3 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A03.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_A03.observations.json)；[verification-large-subset-03](../../logs/verification-large-subset-03/test_A03.observations.json) |
| A4 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A04.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_A04.observations.json)；[verification-large-subset-03](../../logs/verification-large-subset-03/test_A04.observations.json) |
| A5 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A05.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_A05.observations.json)；[verification-large-subset-03](../../logs/verification-large-subset-03/test_A05.observations.json) |
| A6 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A06.observations.json) |
| A7 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A07.observations.json) |
| A8 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A08.observations.json) |
| A9 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A09.observations.json) |
| A10 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A10.observations.json) |
| A11 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A11.observations.json) |
| A12 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A12.observations.json) |
| A13 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A13.observations.json) |
| A14 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A14.observations.json) |
| A15 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_A15.observations.json) |
| B1 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B01.observations.json) |
| B2 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B02.observations.json) |
| B3 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B03.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_B03.observations.json)；[verification-large-subset-03](../../logs/verification-large-subset-03/test_B03.observations.json) |
| B4 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B04.observations.json) |
| B5 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B05.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_B05.observations.json)；[verification-large-subset-03](../../logs/verification-large-subset-03/test_B05.observations.json) |
| B6 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B06.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_B06.observations.json)；[verification-large-subset-03](../../logs/verification-large-subset-03/test_B06.observations.json) |
| B7 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B07.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_B07.observations.json)；[verification-large-subset-03](../../logs/verification-large-subset-03/test_B07.observations.json) |
| B8 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B08.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_B08.observations.json)；[verification-large-subset-03](../../logs/verification-large-subset-03/test_B08.observations.json) |
| B9 | blocked | 外部接入条件缺失；原始脚本明确skip，合并记blocked |
| B10 | blocked | 外部接入条件缺失；原始脚本明确skip，合并记blocked |
| B11 | blocked | 外部接入条件缺失；原始脚本明确skip，合并记blocked |
| B12 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B12.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_B12.observations.json)；[verification-large-subset-03](../../logs/verification-large-subset-03/test_B12.observations.json) |
| B13 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B13.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_B13.observations.json)；[verification-large-subset-03](../../logs/verification-large-subset-03/test_B13.observations.json) |
| B14 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B14.observations.json)；[verification-documents-03](../../logs/verification-documents-03/test_B14.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_B14.observations.json) |
| B15 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B15.observations.json)；[verification-documents-03](../../logs/verification-documents-03/test_B15.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_B15.observations.json) |
| B16 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B16.observations.json) |
| B17 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B17.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_B17.observations.json)；[verification-large-subset-03](../../logs/verification-large-subset-03/test_B17.observations.json) |
| B18 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B18.observations.json) |
| B19 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_B19.observations.json) |
| C1 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_C01.observations.json) |
| C2 | pass | [verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_C02.observations.json)；[verification-large-subset-03](../../logs/verification-large-subset-03/test_C02.observations.json) |
| C3 | pass | [verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_C03.observations.json)；[verification-large-subset-03](../../logs/verification-large-subset-03/test_C03.observations.json) |
| C4 | pass | [verification-large-geometry-03](../../logs/verification-large-geometry-03/test_C04.observations.json) |
| C5 | pass | [verification-large-geometry-03](../../logs/verification-large-geometry-03/test_C05.observations.json) |
| C6 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_C06.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_C06.observations.json)；[verification-large-geometry-03](../../logs/verification-large-geometry-03/test_C06.observations.json) |
| C7 | pass | [verification-phone-suite-03](../../logs/verification-phone-suite-03/test_C07.observations.json)；[verification-tablet-subset-03](../../logs/verification-tablet-subset-03/test_C07.observations.json)；[verification-large-geometry-03](../../logs/verification-large-geometry-03/test_C07.observations.json) |

## 像素、恢复与限制

Root分别直接查看phone/tablet/large新source/HAP截图，11项图案、顶部归属、实心/空心圆角、底部文案/主题色有独立review：root-visual-review-*-03.json。正文B14/B15另由需求角色批准本地原创资源；真实链接、正文片段、滚动、返回后重进均实测，两份完整结束标记由验证角色和Root分别view确认，见root-document-end-review-03.json。

正常/头像连点、同入口三连点、两按钮交错连点、目标页未提交返回/重进、三方缺配置可恢复、无账号冷启动均保留真实观察。缺配置提示不算B9–B11通过；没有伪Token/凭据/授权成功。空输入/纯空格不适用：登录主页无输入字段；分页最后一页不适用，协议长文滚动已实际执行。认证HTTP次数/Token写入没有独立网络抓包证据，不把静态无调用当实测网络pass。

独立project clean与entry全量clean assembleHap退出均0；207条ArkTS诊断按文件+消息+次数（忽略行列偏移）对基线新增0，资源冲突170，duplicate/sourceMapsPath/signing各1，原始stdout/stderr及语义比对保留。构建未产生生产输入变化（build-generated-input-changes=[]）；entry/build为工具产物单独登记。

旧标题/状态栏重叠和Me入口返回后持久锁均已退回主调度修复并形成新冻结回归；旧A01过渡帧假阳性作废，诊断02b因父调度并发改源而末尾指纹失败，不作为新版本通过依据。详见safety-regression-01.md、navigation-regression-02.md，原始失败没有删除。

收尾：两设备方向0、仅停止本角色创建的CmlSpec7_Layout（原PID35092）及主实例30856/5555仍Connected，见[closeout.json](../../logs/verification-closeout-03/closeout.json)。官方-stop退出0并明确successfully，进程已消失；hdc保留5557 Offline条目，首次收尾助手误将该条目当仍连接，原始日志保留后修正为核对Connected状态和进程，不重复stop。共享实例3份微型配置SHA与测试前一致，临时实例大文件保留待主调度决定清理。

## 复现命令

每个新PowerShell先加载D:/hongmengcup/Enter-HarmonyEnv.ps1和D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1；Python使用common/.venv，工作目录/报告位于本题logs。首个独立构建轮：

```powershell
./workflow/verification/run-verified-round.ps1 -RoundName <new-name> -ExpectedSourceSha256 26307326248e8e874d1e2d8c3a4abf10e14008d5fd386b91682357a928f6f78e -Device 127.0.0.1:5555 -Mode suite -SuiteKind smoke
```

后续每轮加 `-BuiltManifest logs/verification-navigation-smoke-03/install-manifest.json` 复用锁定产物并强制新装；full手机/ documents正文/rotation短横屏/layout宽窗选择与确切命令，均以各round的hypium-runner.json、install.json、selection.json和归档PS/Python为准。临时实例已停止时由主调度按保留配置重启，不能直接测试模拟器上来源不明的同bundle应用。

## 最后一轮运行时测试代码指纹

每轮各自的归档SHA已独立保留；以下是最后4case轮及收尾时仍一致的文件。

| 文件 | SHA256 |
| --- | --- |
| hypium_tests/test_login_acceptance.py | `571726e60cb15fa4f5fa2ce2bb54e454432595f9b4904ffd510b2610df738841` |
| workflow/verification/cml_evidence.py | `81c9d641c8ae36dd68d577a82264f4b2888a712d7706e2c5c58bb4280f640b0b` |
| workflow/verification/run_verified_round.py | `04dfd4931c4b2e55f80b1c15586dccc873a7f13e26a1d5a57e0412877a38b230` |
| workflow/verification/run_navigation_smoke.py | `c9004bd884c66b5f8a287c83f6e68655dd53292a7ee6718de74ef438d2afd149` |
| workflow/verification/run_selected_checks.py | `b66d49437e0a45f47e5c11b8fdaca2a9e3d13751b438199f6ce4c8c4b52453e4` |
| workflow/verification/run-verified-round.ps1 | `926bf7ce8b74875ae8bb56f2ea531e404d37f31a19b126cec560888ed455f59f` |
| workflow/verification/approved-document-fragments.json | `e4f4c7d0296e09ae9217747eb6df33d4a831de34d3e35f52602b2441cb01a05c` |
| workflow/verification/provider-error-expectations.json | `389812ddb40d4b8ef71f05d646e2bc49d075b547de79f9a3305d3523efd77464` |

Root对最终C04实际1200vp截图另有[root-final-large-geometry-review-03.json](root-final-large-geometry-review-03.json)独立像素补证。最终生产/测试/Spec/报告指纹见[final-evidence-fingerprint-03.json](final-evidence-fingerprint-03.json)。
