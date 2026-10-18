# cmu-spec1 构建运行说明

以下路径均相对工程根目录（成果包内 `tasks/cmu-spec1/project/`）。工具链版本等公共环境见成果包根目录 `README.md`。

## 应用标识

- bundleName：`cc.chenlvin.cloudmusic`（`AppScope/app.json5`）
- 版本：versionName `1.4.6`，versionCode `10460`
- 模块：`entry`（type `entry`），入口 Ability：`EntryAbility`（`entry/src/main/module.json5` 的 `mainElement`）
- 产品配置（`build-profile.json5`）：product `default`，`runtimeOS` HarmonyOS，`compatibleSdkVersion` 5.0.4(16)，`targetSdkVersion` 6.1.0(23)，`signingConfigs` 为空（产物未签名）

## 环境

- DevEco Studio（自带 HarmonyOS SDK、hvigor、ohpm、node、JBR）。命令行构建需自行导出环境变量，`<DEVECO>` 指 DevEco Studio 安装目录下的 `Contents`（macOS）：

```bash
export JAVA_HOME=<DEVECO>/jbr/Contents/Home        # 未设置时打包阶段报 "Unable to locate a Java Runtime"
export DEVECO_SDK_HOME=<DEVECO>/sdk
export PATH="$JAVA_HOME/bin:<DEVECO>/tools/node/bin:<DEVECO>/tools/hvigor/bin:<DEVECO>/tools/ohpm/bin:<DEVECO>/sdk/default/openharmony/toolchains:$PATH"
```

- 设备：自测使用 ARM64 模拟器（API 23，aarch64，1308×2880），序列号下文记作 `<SN>`。

## 依赖安装

依赖清单 `oh-package.json5`，锁文件 `oh-package-lock.json5`（均随工程提交）。在工程根目录执行：

```bash
ohpm install
```

运行依赖：`@pura/harmony-utils`、`@pie/lazy-data`、`@pura/picker_utils`、`@sj/mediacache`、`@ohos/axios`、`@hw-agconnect/ui-skeleton`；开发依赖：`@ohos/hypium` 1.0.19、`@ohos/hamock` 1.0.0。本题未增删依赖；与官方基线相比，锁文件只多了 `"enableUnifiedLockfile": false`（基线准备流程中 `ohpm install` 写入，提交 `d03903a`）。

## 构建

```bash
hvigorw clean --no-daemon
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon > logs/build.log 2>&1
```

产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。

构建后若 `git status` 出现各模块 `BuildProfile.ets` 变更，属构建生成文件，应还原，不属于提交内容。

## 安装与启动

```bash
hdc -t <SN> install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t <SN> shell aa start -a EntryAbility -b cc.chenlvin.cloudmusic
```

未签名 HAP 在模拟器上可直接 `install -r`（见 `logs/install.log`）。

## 必要初始化

- 应用本身无需额外初始化。首次启动、未配置在线服务时，发现页显示"如需连接在线内容，请设置在线服务"引导和"设置在线服务"按钮（场景二）。
- 需要在线内容时，在"我的 → 应用设置 → 在线服务"或发现页"设置在线服务"面板中，填写一个兼容 NeteaseCloudMusicApi 的服务地址（主机、端口、协议、路径，可选用户/密码），点击"保存配置"。本地自测时用的是宿主机上的 docker 服务（镜像 `binaryify/netease_cloud_music_api`，`/inner/version` 返回 4.27.0），模拟器经 `10.0.2.2:3000` 访问。这个服务只用于测试，不随工程提交。
- 场景三的上传自测需要设备里有音频文件，自测脚本会把测试 mp3 推送到设备 `/storage/media/100/local/files/Docs/Download/`。

## 自测（可选）

自测脚本在 `hypium_tests/`（3 个场景，共 20 条），依赖团队自测框架（成果包 `system-config/test-harness/`，Python 依赖见其 `requirements.txt`，`hypium==6.1.0.210`）。在工程根目录执行：

```bash
cd logs && PYTHONPATH=<test-harness 目录> python -m harness.runner --project <工程根目录> --device <SN> --json <工程根目录>/logs/selftest.json > selftest.log 2>&1
```

场景一、二的部分用例会在宿主机 3901 端口起一个记录请求的转发代理，转发到 3000 端口（见 `hypium_tests/cmu_helpers.py`）。
