# cml-spec28 构建与运行说明

本文供放置于 `tasks/cml-spec28/build.md`；下列工程内路径均相对同题完整工程 `project/`。本材料只整理已有记录，未在材料阶段重新构建、安装或自测，也未证明干净机器已复现。

## 提交版本和实际结果

- 官方基线：`9a1d608dc89acfc301657c33ce5dd6089cbf9572`，见 `spec/metadata.json`。准备后HEAD为b75aa21f…，它不是最终功能提交标识；最终功能版本用正式10冻结清单 `workflow/implementation/development-frozen-fingerprint-10.json` 标识。
- 正式10的827文件聚合SHA256：`3eaa13107c4b8d83485fa473c8f83a42bedb8498783faa0539de4a9f12c0fa1c`。
- 正式产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`，8,658,451 bytes，SHA256 `51761093a48478502e5aac6f8e40678d00e1ed470c38c3c18140086cb8fad229`。bundle=`com.joker.coolmall`，模块=`entry`，入口=`EntryAbility`，版本1.0.0/1000000。
- 正式clean构建exit0；234条文件诊断、175条资源诊断与本题基线无新增。2026-10-19 00:17（北京时间）原六项正式自测为**1 pass、5 AUTH skip、0 fail/error**，runner exit0不代表全题通过。当前没有合法正式登录会话；登录后的地址真实服务契约、鉴权与持久化仍blocked。
- 标准日志：`logs/build.log`、`install.log`、`selftest.log`、`selftest.json`。`logs/boundary-completion/formal10-final-02/version-mapping.json`记录它们与正式10/原六项脚本的精确对应；build.log是已有正式10真实clean日志的逐字节归档，不是最后安装窗口又构建一次。原构建命令/时间见 `workflow/implementation/boundary-phone-formal-build-10-command.json`。

## 已验证环境与移植前提

|项目|本题实际记录|
|---|---|
|工具链|DevEco Studio 6.1.0.860；SDK 6.1.0.105/API23；Hvigor 6.23.7；随附Node18.20.1、JBR/OpenJDK21.0.8|
|工程声明|modelVersion6.0.1；target/compatible `6.0.1(21)`、runtimeOS HarmonyOS；不为材料改成API23声明|
|设备|HarmonyOS6.1.0.115(SP11DEVC00E115R4P11)，1308×2880、560dpi；本题专用序列号 `127.0.0.1:11239`；hdc3.2.0c|
|Python自测|Python3.12.3，Hypium6.1.0.210；精确依赖见 `test-harness/requirements.txt`。根OHPM的`@ohos/hypium:1.0.24`是另一项工程devDependency，不能与Python Hypium混淆。|
|依赖安装|实际执行`ohpm install --all`成功；保留根/各模块oh-package.json5和lock。材料核查时只读`ohpm --version`为6.1.1.830，证据reference/ohpm-version-probe.json；旧构建当时独立CLI版本未有专门日志，不由当前值倒推，不以modelVersion冒充。|
|签名|build-profile.json5的signingConfigs为空，交付为unsigned HAP；记录中的模拟器允许该包安装，不宣称已在要求正式签名的真机安装。|

工具版本证据为 `traces/analysis/baseline-runtime/tool-*-version.log` 和包内环境/准备记录；common README的Python3.13描述不是本题实际运行版本。

工程根没有随包hvigorw启动器；历史命令从已配置PATH中的DevEco工具调用。原环境脚本快照位于 `system-config/initial-20261018T112051Z/environment/`，包含固定安装目录、SDK/缓存目录和外部Python约束文件引用，**是历史配置证据，不能在异机原样执行**。本题也没有随包工具链二进制/预装虚拟环境或完整Python传递依赖冻结；需要评审环境安装对应工具，配置 `JAVA_HOME`、`DEVECO_SDK_HOME`（API23 SDK根）、`DEVECO_STUDIO_HOME`，将DevEco的Node、ohpm、hvigor和SDK hdc加入PATH。原外部Python约束文件的完整内容不在此材料中，完全一致的依赖环境尚不能据此保证。

随包必须保留 `test-harness/`（含harness全部模块及requirements）、`hypium_tests/`、正式10冻结清单及其引用文件、构建/测试记录目录，以及材料内 `tools/run-formal-acceptance.py`。当前工程内8个harness Python文件与只读common副本逐字节一致，新材料入口使用工程内副本，不依赖兄弟common或参赛机虚拟环境。历史 `workflow/verification/boundary-formal.py` 与原六项脚本锁定设备11239，作为实际运行证据保留；新材料入口的设备/输出适配必须如实记录，不能把新入口称为历史实际执行脚本。

## 基线准备和依赖

`logs/prepare-baseline.log`记录官方准备profile=`harmony-cup-build-v1`：固定ibest-ui-v2为1.1.3、移除失效1.1.0锁后由正常ohpm重建。`workflow/setup-result.json`、`baseline-provenance.json`记录从官方base准备、采用等价的依赖准备提交、业务源当时未改；`logs/ohpm-install.log`保留下载重试及最后成功。最终配置与锁已在工程中，不需重新寻找/下载来源应用或再执行题包准备脚本。

官方精确 `reports/build-baselines/cml-spec28.log` 在本轮获准检查的题包位置及其指定备用位置均不存在，**官方日志缺失【待补充】**。上述本题日志/JSON是可证替代记录，不标成该官方日志；准备阶段成功也不等于功能验收。

地区数据已静态生成在 `feature/user/src/main/ets/model/AddressRegionData.ets`，许可/来源在 `third_party/area-data-0.0.6/`；当前不需安装area-data HAR或再次联网导出。其余依赖按现有manifest/lock执行，不升级版本。

## 可移植命令及实际命令的关系

以下在工程根、已配置的Windows PowerShell终端执行；工具名与正式10实际命令一致，所有路径从当前工程解析。它们是后续复跑指引，本次材料整理未执行。输出使用新目录以保留旧证据；源码manifest必须仍匹配。重新构建的ZIP时间戳可能使HAP hash不同，应登记新包身份，不能把新包冒称原51761093…原件。

```powershell
$projectRoot = (Get-Location).Path
$DevEcoRoot = $env:DEVECO_STUDIO_HOME
$SdkRoot = $env:DEVECO_SDK_HOME
if (!$DevEcoRoot -or !$SdkRoot) { throw 'Set the installed DevEco and API23 SDK roots first' }
$Node = Join-Path $DevEcoRoot 'tools/node/node.exe'
$env:JAVA_HOME = Join-Path $DevEcoRoot 'jbr'
$env:Path = ((@(
  (Split-Path $Node),
  (Join-Path $env:JAVA_HOME 'bin'),
  (Join-Path $DevEcoRoot 'tools/ohpm/bin'),
  (Join-Path $DevEcoRoot 'tools/hvigor/bin'),
  (Join-Path $SdkRoot 'default/openharmony/toolchains')
)) -join ';') + ';' + $env:Path
$HvigorEntry = (Get-Command hvigorw -ErrorAction Stop).Source
$reproId = 'repro-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
$buildOut = Join-Path $projectRoot ('logs/' + $reproId)
New-Item -ItemType Directory -Path $buildOut | Out-Null
ohpm install --all
if ($LASTEXITCODE -ne 0) { throw 'ohpm install failed' }
& $HvigorEntry clean assembleHap --mode module -p product=default -p buildMode=debug --no-daemon 2>&1 |
  Tee-Object -FilePath (Join-Path $buildOut 'build.log')
if ($LASTEXITCODE -ne 0) { throw 'formal build failed' }
$hap = Join-Path $projectRoot 'entry/build/default/outputs/default/entry-default-unsigned.hap'
$hapSha = (Get-FileHash -LiteralPath $hap -Algorithm SHA256).Hash.ToLowerInvariant()
hdc -t 127.0.0.1:11239 install -r $hap
hdc -t 127.0.0.1:11239 shell bm dump -n com.joker.coolmall
hdc -t 127.0.0.1:11239 shell aa force-stop com.joker.coolmall
hdc -t 127.0.0.1:11239 shell aa start -a EntryAbility -b com.joker.coolmall
```

每次复测前必须安装刚构建包并核bundle/updateTime；核命令exit和安装成功原文。实际原六项用Hypium的stop_app/start_app显式EntryAbility冷启动，两自然入口到登录的原动作/截图见 `traces/boundary-completion/verification/formal10-final-02/ui/`。首次使用无需人为种地址；正式登录需要合法账号/会话，本题未取得，不注入fixture token。

Python环境在本机创建，不分发虚拟环境。材料内新入口 `tools/run-formal-acceptance.py` 使用原六项和原SHA校验，fresh install后在运行时重定向EVIDENCE到新输出目录；它属于提交材料适配，未改原测试文件/断言，且未在新机实跑。`--allow-own-address-writes`对应历史实际 `CML28_ALLOW_ADDRESS_WRITES=1` 设置，仅使已合法登录后的脚本可操作自己创建的地址，不绕过认证。使用前核设备归属；原测试的设备约束、入口的实际校验范围和命令参数以随包工具源码为准。

```powershell
python -m venv .venv-selftest
$testPython = Join-Path $projectRoot '.venv-selftest/Scripts/python.exe'
& $testPython -m pip install -r test-harness/requirements.txt
$portableRunner = Join-Path $projectRoot '.comate/submission-draft/tools/run-formal-acceptance.py'
& $testPython $portableRunner `
  --project $projectRoot --device 127.0.0.1:11239 --hap $hap `
  --out (Join-Path $projectRoot ('logs/' + $reproId + '-formal')) `
  --allow-own-address-writes
```

上例引用工具在完整工程中的材料保留路径；若最终打包把tools移到build.md旁，应把 `$portableRunner` 指向该真实包内位置，不依赖不存在的外部脚本。工具仅做静态/帮助检查，不代表上述设备命令已通过。若安装版工具布局有别，先确认其启动器/SDK路径再执行，不把变量映射视为干净环境验证。

新材料入口会在六项中存在skip时返回exit2，并在completion.json分别记录原runner和wrapper退出码；这与历史原runner的exit0语义不同，是防止把AUTH skip当全通过。该入口不能解除原脚本11239设备约束；本说明使用已验证的专用设备号，其他设备需安装前确认入口支持范围。

实际历史最终运行名为formal10-final-02，包hash固定为51761093…、原六项源SHA256为 `7893587e2eeb59a7d91b366621d6791cf46f95aa474e450581a494cb8955ef7f`；原wrapper的argv、harness.runner参数及输出目录配置见该run的invocation.json。上面的新run须另存命令/退出码、当前包hash `$hapSha` 和适配记录，不能覆盖历史日志/输出。若源码或测试hash不符，保留失败并解决版本差异，不取消保护断言。

六项分别是冷启动双入口、空表单、地区确认/取消、非法手机号、订单取消选择、创建→仅姓名编辑→重开→选行→删除。实际只有第一项pass，其余均AUTH skip；详见 `logs/selftest.json`。合法会话缺失尚未解除。

## fixture证据的独立身份

隔离bundle始终 `com.joker.coolmall.fixture28`，公开fixture身份→loopback HTTP→SQLite，不能代替正式登录/真实服务。主31有限参数按版本分别完成：08/app-r3共15、09/app-r4共6真实timeout、10/app-r5共10；另3项设备回归通过。最新app-r5的源聚合2e1a4c15…、HAP bfafeec3…，不是正式51761093…包。原R3核心10和45个源码状态case也各保留其证据层，不累计成官方检查点。

完整版本/命令/原始截图/HTTP/DB、失败重试及清理见 `workflow/verification/boundary-completion-01.md`、`boundary-completion-matrix.json` 和 `traces/boundary-completion/verification/`。测试服务/Reverse已清理、正式10已恢复；正式构建/启动不依赖fixture服务。现有fixture/状态脚本仍含设备、路径与工具位置约束，未宣称可在干净环境直接复现；若需重跑，须按各run已保存配置进行可审计适配。
