# cmu-spec114 构建与运行说明

本题工程位于成果包 `tasks/cmu-spec114/project/`，以下命令均在该目录（工程根目录）执行。

## 1. 环境

| 项 | 版本 / 说明 | 来源 |
| --- | --- | --- |
| DevEco Studio | 6.1.0.860（Build 243.24978.46.36.610860） | DevEco `product-info.json` |
| HarmonyOS SDK | 6.1.0，API 23（工程 `compatibleSdkVersion` 5.0.0(12)，`targetSdkVersion` 6.1.0(23)） | DevEco `sdk-pkg.json`、`build-profile.json5` |
| hvigor | 6.23.7 | DevEco `tools/hvigor` |
| ohpm | 6.1.1.830 | `ohpm -v` |
| Node.js | v18.20.1（DevEco 自带） | `node -v` |
| hdc | 3.2.0c | `hdc -v` |
| 目标设备 | HarmonyOS 6.1.0 模拟器，API 23；自测时设备序列号 `127.0.0.1:5555` | `hdc shell param get` |

先把 DevEco 自带工具加入 `PATH`（`DEVECO` 为 DevEco Studio 的 `Contents` 目录，按本机实际位置设置）：

```bash
export DEVECO=/path/to/DevEco-Studio.app/Contents          # 按本机安装位置修改
export DEVECO_SDK_HOME="$DEVECO/sdk"
export JAVA_HOME="$DEVECO/jbr/Contents/Home"
export PATH="$DEVECO/tools/node/bin:$DEVECO/tools/hvigor/bin:$DEVECO/tools/ohpm/bin:$DEVECO/sdk/default/openharmony/toolchains:$JAVA_HOME/bin:$PATH"
```

## 2. 依赖安装

依赖清单：`oh-package.json5`（`@pura/harmony-utils`、`@pura/spinkit`、`@abner/refresh`；dev：`@ohos/hypium`、`@ohos/hamock`），
锁文件：`oh-package-lock.json5`，源为 `https://ohpm.openharmony.cn/ohpm`。需要联网。

```bash
ohpm install
```

## 3. 构建

```bash
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

产物（未签名 debug HAP，工程未配置 `signingConfigs`，构建会提示 `No signingConfig found for product default`，属预期）：

```
entry/build/default/outputs/default/entry-default-unsigned.hap
```

构建会改写各模块 `BuildProfile.ets`（构建噪声）；本题成果中该类文件未纳入差异。

## 4. 安装

先启动模拟器并确认设备在线（`hdc list targets`），再安装（`<设备序列号>` 换成实际值）：

```bash
hdc -t <设备序列号> install -r entry/build/default/outputs/default/entry-default-unsigned.hap
```

安装成功输出 `install bundle successfully.`。同一上游项目的多道题共用同一 bundleName，
评测或自测前务必重装本题 HAP，可用 `hdc -t <设备序列号> shell "bm dump -n cc.chenlvin.cloudmusic"`
核对 `versionName` 为 `0.9.3`、`versionCode` 为 `103`。

## 5. 启动与应用标识

- bundleName：`cc.chenlvin.cloudmusic`（`AppScope/app.json5`）
- 版本：versionName `0.9.3`，versionCode `103`
- 入口 Ability：`EntryAbility`（`entry/src/main/module.json5` 的 `mainElement`，`srcEntry` 为 `./ets/entryability/EntryAbility.ets`）
- 启动：点击桌面应用图标，或

  ```bash
  hdc -t <设备序列号> shell aa start -a EntryAbility -b cc.chenlvin.cloudmusic
  ```

  （`aa start` 命令为标准用法，本题会话中未直接执行；本题自测由 Hypium 的 `start_app` 启动应用。）

## 6. 必要初始化

无需账号、数据库或其他初始化。本题功能路径：首页右上角更多按钮 → “设置” → 查看“0.9.3 - 测试版”；
点击“前往查看本软件的隐私政策”进入应用内 `PrivacyPage`；首页搜索框留空点击搜索应提示“请输入搜索内容”。

注意：隐私页加载的网络地址 `https://docs.chenlvin.cc/cloudmusic/#/privacy` 在本题会话的排查中无法解析（见 `solution` 片段“已知问题”），
页面正文可能为空白，标题“隐私政策”、Web 组件与返回行为不受影响。

## 7. 自测（可选）

自测脚本在 `hypium_tests/`，继承赛事公共自测框架 `common/test-harness` 的 `harness.driver.HarnessTestCase`。
该框架与其 Python 环境不在本工程内，也不在本包 `project/` 中，需要参赛团队的 `common/` 目录才能复现运行；
本工程的构建与安装不依赖它。自测结果与日志见成果包 `tasks/cmu-spec114/logs/selftest.json`、`selftest.log`（22 条，全部通过）。
