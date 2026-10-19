# 构建与运行说明：sym-combo-customize

本说明只使用相对路径与环境变量，不依赖参赛电脑的私有路径。命令均在 `tasks/sym-combo-customize/project/`（即工程根目录）下执行。

## 应用标识

| 项 | 值 | 出处 |
| --- | --- | --- |
| bundleName | `com.next.liny.symbolu` | `AppScope/app.json5` |
| versionName / versionCode | `0.0.1` / `1` | `AppScope/app.json5` |
| 入口模块 | `entry`（type `entry`，deviceTypes: phone / tablet / 2in1） | `entry/src/main/module.json5` |
| 入口 Ability | `EntryAbility`（`./ets/entryability/EntryAbility.ets`），加载 `pages/Index` | `module.json5`、`main_pages.json` |
| product / buildMode | `default` / `debug` | `build-profile.json5` |
| compatibleSdkVersion / targetSdkVersion | `5.0.4(16)` / `6.1.0(23)` | `build-profile.json5`（`targetSdkVersion` 为相对基线新增，见 trace-index.md） |
| runtimeOS | `HarmonyOS` | `build-profile.json5` |

## 环境

- DevEco Studio 6.1.0，内置 HarmonyOS SDK 6.1.0.105（API 23）、JBR、hvigor、ohpm、node、hdc（`sdk/default/openharmony/toolchains`）。
- 必须使用 DevEco 自带 JBR 作为 `JAVA_HOME`；不设置时 `PackageHap` 会报 `00308018 Unable to locate a Java Runtime`。
- 运行与自测设备：API 23 模拟器（Pura 90 Pro Max，HarmonyOS 6.1.0，1308x2880）。
- 无签名配置（`signingConfigs` 为空），产物为未签名 HAP，模拟器可直接安装。
- 本应用不需要登录、服务端、账号、网络或预置测试数据；全部符号数据内置在 `entry/src/main/ets/objects/linysSymbol.ets`。

## 1. 依赖安装

依赖清单 `oh-package.json5`，锁文件 `oh-package-lock.json5`（随工程提交）。无运行期依赖，仅 devDependencies：`@ohos/hypium@1.0.21`、`@ohos/hamock@1.0.0`（来自 `ohpm.openharmony.cn`，需要联网）。

```bash
DEVECO=<DevEco Studio 安装目录>/Contents      # macOS 示例: /Applications/DevEco-Studio.app/Contents
export JAVA_HOME="$DEVECO/jbr/Contents/Home"
export DEVECO_SDK_HOME="$DEVECO/sdk"
export PATH="$JAVA_HOME/bin:$DEVECO/sdk/default/openharmony/toolchains:$DEVECO/tools/hvigor/bin:$DEVECO/tools/ohpm/bin:$DEVECO/tools/node/bin:$PATH"
ohpm install
```

## 2. 构建

```bash
hvigorw clean --no-daemon
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。

本次自测所用构建（2026-10-19 20:42，日志 `logs/build.log`）结果 `BUILD SUCCESSFUL`，产物 738,647 B，SHA-256 `dc0f07d96fdc47b6e64b15e7ea90070a18b7ad70fb7e0f01b0f1b35a55e41474`。HAP 不随成果包提交，请按上述命令重新构建（重新构建的字节级哈希不保证一致）。

构建告警 2 条，均为基线已有：`EntryAbility.ets:10:5 Function may throw exceptions`、`No signingConfig found for product default`。

## 3. 安装

```bash
hdc list targets                                  # 取得设备序列号 <SN>
hdc -t <SN> install -r entry/build/default/outputs/default/entry-default-unsigned.hap
```

预期输出含 `install bundle successfully`（见 `logs/install.log`）。同一上游项目的多道赛题共用同一个 bundleName，测试前须重新安装本题 HAP。

## 4. 启动

```bash
hdc -t <SN> shell aa start -a EntryAbility -b com.next.liny.symbolu
```

冷启动直接进入 `pages/Index`（符号网格页）。无需其他初始化。

## 5. 自测（可选）

自测用例位于 `hypium_tests/`（27 条 Hypium 用例），依赖随成果包的 `system-config/test-harness/`（`hypium==6.1.0.210`）。运行命令见 `spec/1-do.md`（`harness.runner`，`--project` 指向工程根目录），结果见 `logs/selftest.json`（27 条全部 `pass`）。
