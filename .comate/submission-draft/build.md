# cmu-spec99 构建与运行说明

命令均在工程根目录（成果包内 `tasks/cmu-spec99/project/`）执行。`<DEVECO>` 指 DevEco Studio 安装目录下的 `Contents`（macOS 默认 `/Applications/DevEco-Studio.app/Contents`），`<设备>` 指 `hdc list targets` 给出的设备序列号。公共环境见成果包根目录 `README.md`。

## 应用标识

| 项 | 值 | 出处 |
| --- | --- | --- |
| bundleName | `cc.chenlvin.cloudmusic` | `AppScope/app.json5` |
| versionName / versionCode | `0.9.7.1` / `113` | `AppScope/app.json5` |
| 模块 / 入口 Ability | `entry`（type `entry`）/ `EntryAbility` | `entry/src/main/module.json5` |
| 首页 | `pages/Index`（搜索入口），结果页 `pages/SongsListPage` | `entry/src/main/resources/base/profile/main_pages.json` |
| 产品 / SDK | product `default`，runtimeOS `HarmonyOS`，compatibleSdkVersion `5.0.1(13)`，targetSdkVersion `6.1.0(23)` | `build-profile.json5` |
| 签名 | `signingConfigs` 为空，产物为未签名 HAP | `build-profile.json5` |

## 本题实测使用的工具版本

DevEco Studio 6.1.0（SDK HarmonyOS 6.1.0.105，API 23），hvigor 6.23.7，DevEco 自带 Node v18.20.1，hdc 3.2.0c；自测用 Python 3.13.16 + hypium 6.1.0.210。设备为模拟器（`OpenHarmony-6.1.0.115`，1308×2880）。

## 1. 安装依赖

依赖清单 `oh-package.json5`，锁文件 `oh-package-lock.json5`（均随工程提交）。`oh_modules/` 不随包提交，需联网从 ohpm 仓库安装：

```bash
<DEVECO>/tools/ohpm/bin/ohpm install
```

运行依赖：`@pura/harmony-utils`、`@pura/spinkit`、`@yunkss/ef_audio`、`@ohos/axios`；开发依赖：`@ohos/hypium 1.0.19`、`@ohos/hamock 1.0.0`。

## 2. 构建

```bash
D=<DEVECO>
export JAVA_HOME=$D/jbr/Contents/Home DEVECO_SDK_HOME=$D/sdk PATH=$D/jbr/Contents/Home/bin:$D/tools/node/bin:$PATH
$D/tools/hvigor/bin/hvigorw clean --no-daemon
$D/tools/hvigor/bin/hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon 2>&1 | tee logs/build.log
```

- 产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。
- 必须把 `JAVA_HOME` 设为 DevEco 自带 JBR，否则 clean 后在 `PackageHap` 报 `00308018 Unable to locate a Java Runtime`（见 `spec/baseline-notes.md` 第 2 节）。
- 预期输出 `BUILD SUCCESSFUL`，告警 `No signingConfig found for product default` 属基线既有。

## 3. 安装与启动

```bash
export PATH=<DEVECO>/sdk/default/openharmony/toolchains:$PATH
hdc -t <设备> install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t <设备> shell "bm dump -n cc.chenlvin.cloudmusic" | grep updateTime   # 核对装的是刚构建的包
hdc -t <设备> shell aa start -a EntryAbility -b cc.chenlvin.cloudmusic
```

未签名 HAP 只在模拟器上实测安装成功；真机需自行配置签名，未验证。同一来源项目的其他赛题使用相同 bundleName，测试前必须重装本题 HAP。

## 4. 必要初始化

- 搜索不需要登录。
- 需要可访问的 NeteaseCloudMusicApi 兼容服务。应用默认地址为 `Constants.ROOT_URL`（`entry/src/main/ets/common/constants/Constants.ets`，`http://111.229.38.178:3000`），2026-10-18 本地两次实测均不可达；按 acceptance U10 决议未修改源码。
- 默认地址不可达时，在应用内 设置 → 打开“自定义API服务器地址” → 填入可用地址 → 点“设置”。该设置存于应用 Preferences，`install -r` 覆盖安装会保留，卸载重装会丢失。
- 本题自测使用的真实服务是团队局域网内自建的 NeteaseCloudMusicApi（docker 镜像 `binaryify/netease_cloud_music_api`），地址写在 `hypium_tests/helpers.py` 的 `REAL_API`，在团队网络之外不可达。

## 5. 自测（可选）

依赖团队自研测试框架 `common/test-harness`（成果包 `system-config/test-harness/`）及其 Python 环境。在工程根目录执行：

```bash
COMMON=<test-harness 与 .venv 所在的 common 目录>
PROJ="$PWD"
(cd logs && PYTHONPATH="$COMMON/test-harness" "$COMMON/.venv/bin/python" -m harness.runner \
    --project "$PROJ" --device <设备> --json "$PROJ/logs/selftest.json" 2>&1 | tee selftest.log)
```

- `hypium_tests/test_search_paging_mock.py`（15 条）：脚本自行在本机 `127.0.0.1:3999` 启动 `hypium_tests/mock_server.py`，并执行 `hdc rport tcp:3999 tcp:3999`，通过应用设置页切换 API 地址，结束后改回 `REAL_API`；要求本机 3999 端口空闲、`hdc` 在 PATH 中。
- `hypium_tests/test_search_paging_real.py`（3 条）：依赖上面的 `REAL_API` 可达。
- 本次结果：18 条全部通过（`logs/selftest.json`、`logs/selftest.log`）。
