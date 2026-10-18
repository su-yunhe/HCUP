# cmu-spec34 构建与运行说明

本文件所有命令均在**工程根目录**（即本题 `project/` 目录）执行。文中不含参赛电脑私有路径；`$DEVECO` 为 DevEco Studio 的默认安装位置，按实际安装位置替换。

## 1. 应用标识

| 项 | 值 | 来源 |
| --- | --- | --- |
| bundleName | `cc.chenlvin.cloudmusic` | `AppScope/app.json5` |
| 版本 | versionName `1.3.6.2` / versionCode `10362` | `AppScope/app.json5` |
| 入口模块 / Ability | `entry` / `EntryAbility`（`mainElement`） | `entry/src/main/module.json5` |
| 设备类型 | phone、tablet、2in1 | `entry/src/main/module.json5` |
| compatibleSdkVersion / targetSdkVersion | `5.0.2(14)` / `6.1.0(23)` | `build-profile.json5` |
| 签名 | `signingConfigs` 为空，产物为 unsigned HAP（基线即如此） | `build-profile.json5` |

## 2. 环境

本次实际使用的版本（macOS，Apple Silicon）：

- DevEco Studio 6.1.0.860（`product-info.json`），SDK HarmonyOS 6.1.0 / API 23（`sdk-pkg.json` 6.1.0.105）
- hvigor 6.23.7，ohpm 6.1.1.830，DevEco 自带 Node v18.20.1
- JDK：DevEco 自带 JBR（OpenJDK 21.0.8）。**必须设置 `JAVA_HOME`**，否则 `PackageHap` 阶段失败（Error Code 00308018，基线构建已复现）
- hdc 3.2.0c；设备：HarmonyOS 模拟器，序列号 `127.0.0.1:5555`
- 自测：Python 3.13 + `hypium==6.1.0.210`，以及团队自研 `test-harness`（见成果包 `system-config/test-harness/`，不在本工程内）

```bash
DEVECO=/Applications/DevEco-Studio.app/Contents
export JAVA_HOME=$DEVECO/jbr/Contents/Home
export DEVECO_SDK_HOME=$DEVECO/sdk
export PATH=$JAVA_HOME/bin:$DEVECO/tools/hvigor/bin:$DEVECO/tools/node/bin:$DEVECO/tools/ohpm/bin:$DEVECO/sdk/default/openharmony/toolchains:$PATH
```

## 3. 依赖安装

依赖清单 `oh-package.json5`：`@pura/harmony-utils ^1.2.4`、`@pie/lazy-data ^1.0.0`；devDependencies：`@ohos/hypium 1.0.19`、`@ohos/hamock 1.0.0`。锁文件 `oh-package-lock.json5` 已随工程提交（解析出 `@pura/harmony-utils 1.2.4`、`class-transformer 0.5.1` 等，来源 `ohpm.openharmony.cn`）。

```bash
ohpm install
```

需要能访问 ohpm 仓库；`oh_modules/` 为安装产物，不随包提供。

## 4. 构建

```bash
mkdir -p logs
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon 2>&1 | tee logs/build.log
```

产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。本机最后一次构建（2026-10-18 17:30）该文件为 4641257 字节，SHA-256 `b5e83d2a4626d514fb92ff5553eef5ba4f052caa44fc2f12795bb97ce64b47f4`（构建不保证逐字节复现，仅供对照）。

构建后 `BuildProfile.ets` 若被改写，应还原：`git checkout -- $(git diff --name-only | grep BuildProfile.ets)`。

## 5. 安装与启动

```bash
hdc -t 127.0.0.1:5555 install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t 127.0.0.1:5555 shell "bm dump -n cc.chenlvin.cloudmusic"   # 核对 updateTime，确认装的是本次构建
hdc -t 127.0.0.1:5555 shell "aa start -a EntryAbility -b cc.chenlvin.cloudmusic"
```

同一上游项目的多道题共用该 bundleName，自测前务必重新安装本题 HAP。该 HAP 未签名，已验证可装入模拟器；真机需自行配置签名。

## 6. 必要初始化（服务端与 API 地址）

应用依赖自建的 NeteaseCloudMusicApi 服务端，API 地址默认为空。未配置时发现页只显示“本地曲库”，三张网络类卡片被隐藏；本题实现的“私人FM”卡片不受此限，始终显示，但没有服务端时请求会失败（提示“获取推荐歌曲失败”，仍进入 FM 状态、队列为空）。

本次自测环境：

1. 在宿主机运行 NeteaseCloudMusicApi（Docker，监听 `3000` 端口）。
2. 在应用内的 API 设置页（源码 `entry/src/main/ets/pages/settings/ApiSetPage.ets`）把 API 地址填为 `http://10.0.2.2:3000`（模拟器访问宿主机）。
3. 本次测试**未登录**，也未提供登录 Cookie；“不喜欢”上报在未登录时服务端返回 HTTP 301，应用照常切歌。登录后的行为未验证。

## 7. 自测（Hypium）

测试脚本在 `hypium_tests/`，继承 `harness.driver.HarnessTestCase`。`$COMMON` 指 test-harness 所在目录（其 `.venv` 为 Python 环境）：

```bash
PROJ="$PWD"
(cd logs && PYTHONPATH="$COMMON/test-harness" "$COMMON/.venv/bin/python" -m harness.runner \
    --project "$PROJ" --device 127.0.0.1:5555 --json "$PROJ/logs/selftest.json" 2>&1 | tee selftest.log)
```

本次最后一次运行：22 个用例，22 通过、0 失败、0 跳过（`logs/selftest.json`、`logs/selftest.log`）。测试会临时改写模拟器上的 API 地址（失败路径用例改为 `:3999`，结束时恢复为 `http://10.0.2.2:3000`）。
