# jm-spec7 构建与运行说明

对应赛题：jm-spec7（收藏夹支持更多内容类型）。完整工程在成果包 `tasks/jm-spec7/project/`，下文命令均在该目录执行。

## 1. 应用标识

| 项 | 值 | 出处 |
| --- | --- | --- |
| bundleName | `com.hefengbao.jingmo.hw` | `AppScope/app.json5` |
| versionName / versionCode | `1.1.1` / `1001001` | `AppScope/app.json5` |
| 入口模块 | `default`（目录 `products/default`，type=entry） | `products/default/src/main/module.json5` |
| 入口 Ability | `EntryAbility`（`./ets/entryability/EntryAbility.ets`） | 同上 |
| 设备类型 | phone、tablet | 同上 |
| SDK | targetSdkVersion `6.0.1(21)`，compatibleSdkVersion `5.1.1(19)`，runtimeOS `HarmonyOS` | `build-profile.json5` |

## 2. 环境

- DevEco Studio 6.1.0.860（macOS arm64；版本取自本机 `product-info.json`），使用其自带的 JBR、Node、hvigor 与 SDK。
  构建时本机实际执行环境：`JAVA_HOME=<DEVECO>/jbr/Contents/Home`、`DEVECO_SDK_HOME=<DEVECO>/sdk`，
  `<DEVECO>` 指 DevEco Studio 安装目录下的 `Contents`。未设置 JBR 时 PackageHap 会报 00308018 找不到 Java Runtime。
- 设备：HarmonyOS 模拟器（自测使用 `127.0.0.1:5555`），`hdc` 位于 `<DEVECO>/sdk/default/openharmony/toolchains`，需放入 `PATH`。

## 3. 依赖安装

- 根 `oh-package.json5`：`dependencies.tyme4oh = ^1.3.9`；`devDependencies.@ohos/hypium = 1.0.24`。
- 锁文件 `oh-package-lock.json5` 已随工程提交，锁定 `tyme4oh@1.3.9`、`@ohos/hypium@1.0.24`，来源 `https://ohpm.openharmony.cn/ohpm/`。
- 各功能模块通过 `file:` 本地依赖互相引用（见 `products/default/oh-package.json5`），无需额外下载。
- 依赖由 DevEco Studio 打开工程时自动安装，或在工程根目录执行 `ohpm install --all`。`oh_modules/` 不随包提供。

## 4. 构建

```bash
export JAVA_HOME="<DEVECO>/jbr/Contents/Home"
export DEVECO_SDK_HOME="<DEVECO>/sdk"
export PATH="$JAVA_HOME/bin:<DEVECO>/tools/node/bin:$PATH"
H="<DEVECO>/tools/hvigor/bin/hvigorw.js"
node "$H" clean --no-daemon
node "$H" --mode module -p module=default@default -p product=default -p buildMode=debug assembleHap --no-daemon
```

- 产物：`products/default/build/default/outputs/default/default-default-unsigned.hap`。
- `build-profile.json5` 中 `signingConfigs` 为空，产物是未签名 HAP（构建日志含 `No signingConfig found for product default`）。
  模拟器可直接 `install -r`；真机需使用者自行配置签名。
- 构建会把各模块 `BuildProfile.ets` 改写为 debug 值（`BUILD_MODE_NAME='debug'`、`DEBUG=true`）。
  本工程提交的 `BuildProfile.ets` 已是这一内容（见 `trace-index.md` 的说明）。
- 本题构建结果：`BUILD SUCCESSFUL`，`ArkTS:WARN` 36 条，`ERROR` 0 条（`logs/build.log`）。
  基线构建同为 36 条 WARN（`logs/baseline-build.keep.log`）。

## 5. 安装与启动

```bash
hdc -t <设备序列号> install -r products/default/build/default/outputs/default/default-default-unsigned.hap
hdc -t <设备序列号> shell aa start -a EntryAbility -b com.hefengbao.jingmo.hw
```

安装结果见 `logs/install.log`（`install bundle successfully`）。也可在桌面点击应用图标启动。

## 6. 必要初始化（内容数据）

应用以离线数据方式提供内容，内容表默认为空，收藏按钮在无内容时置灰。使用前需：
首页右上角「设置」→「同步数据」（或「导入数据」）获取内容，同步需要设备能联网访问应用自身的内容 CDN。
本题自测时模拟器上有数据的类型：经典诗文、歌词、诗歌、谚语、谜语、歇后语、成语；诗文（约 163 万条）未同步。
因此 `test_07_writing`（诗文）被跳过，见 `solution.fragment.md`。

## 7. 自测

自测脚本：`hypium_tests/test_bookmark.py`（13 个用例，继承 harness 的 `HarnessTestCase`）。
harness 不在工程内，使用赛事提供的 test-harness 及其 Python 环境。先安装本题刚构建的 HAP，再执行：

```bash
export PATH="<DEVECO>/sdk/default/openharmony/toolchains:$PATH"
PYTHONPATH="<TEST_HARNESS_PARENT>" "<TEST_HARNESS_PYTHON>" -m harness.runner \
  --project "$PWD" --device <设备序列号> --json "$PWD/logs/selftest.json"
```

`<TEST_HARNESS_PARENT>` 为含 `harness/` 包的目录，`<TEST_HARNESS_PYTHON>` 为已装 Hypium 的 Python 解释器。
最终结果（`logs/selftest.json`）：13 个用例，12 通过、0 失败、1 跳过。自测会修改模拟器上的收藏数据。
