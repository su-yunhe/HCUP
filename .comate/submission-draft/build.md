# cmu-spec102 构建与运行说明

公共环境（DevEco Studio / SDK、Node、OHPM、Hvigor、hdc、Python 与 Hypium 版本）见成果包根目录 `README.md`。
以下命令均在本题工程根目录（成果包内 `tasks/cmu-spec102/project/`）执行；`<DEVECO>` 指 DevEco Studio 安装目录，`<SN>` 指设备序列号。

## 应用标识

- bundleName：`cc.chenlvin.cloudmusic`（`AppScope/app.json5`）
- 版本：versionName `0.9.7`，versionCode `112`
- 入口模块 / Ability：`entry` / `EntryAbility`（`entry/src/main/module.json5` 的 `mainElement`）
- 工程配置：`build-profile.json5`，product `default`，`compatibleSdkVersion 5.0.1(13)`，`targetSdkVersion 6.1.0(23)`，`runtimeOS HarmonyOS`，`signingConfigs` 为空（产出未签名 HAP）

## 1. 环境变量

```bash
export JAVA_HOME=<DEVECO>/Contents/jbr/Contents/Home        # 必须：否则 PackageHap 报 00308018（找不到 Java 运行时）
export DEVECO_SDK_HOME=<DEVECO>/Contents/sdk
export PATH=$JAVA_HOME/bin:<DEVECO>/Contents/tools/node/bin:<DEVECO>/Contents/tools/ohpm/bin:<DEVECO>/Contents/tools/hvigor/bin:<DEVECO>/Contents/sdk/default/openharmony/toolchains:$PATH
```

## 2. 依赖安装

```bash
ohpm install
```

依赖清单 `oh-package.json5`，锁文件 `oh-package-lock.json5`（已随工程提交）。依赖：`@ohos/axios 2.2.4`、`@yunkss/ef_audio 1.0.1`、`class-transformer 0.5.1`、`@pura/harmony-utils 1.2.4`、`@pura/spinkit 1.0.4`，来源 `ohpm.openharmony.cn`。本题未新增依赖。

## 3. 构建

```bash
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon 2>&1 | tee logs/build.log
```

产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。

构建会因 `buildMode=debug` 改写各模块 `BuildProfile.ets`。如果 `git status` 里出现它，还原：

```bash
git checkout -- $(git diff --name-only | grep 'BuildProfile.ets')
```

## 4. 安装与启动

```bash
hdc -t <SN> install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t <SN> shell "bm dump -n cc.chenlvin.cloudmusic" | grep -m1 updateTime   # 核对装的是本次产物
hdc -t <SN> shell "aa start -a EntryAbility -b cc.chenlvin.cloudmusic"
```

未签名 HAP 可直接装到模拟器。本地自测设备为模拟器（API 23，`OpenHarmony-6.1.0.115`，1308×2880）。同一上游项目的多道题共用此 bundleName，自测前先重装本题产物。

## 5. 必要初始化

1. API 服务：应用依赖网易云音乐 API 兼容服务。本地自测用 docker 镜像 `binaryify/netease_cloud_music_api`（容器内 `package.json` version `4.27.0`），映射宿主机 `3000` 端口。
2. 在应用里设置服务地址：更多菜单 → 设置 → 打开"自定义API服务器地址" → 输入 `http://10.0.2.2:3000`（模拟器访问宿主机的地址）→ 点"设置"保存。该设置持久化，`install -r` 后保留。本题改动没有在源码中写入服务器地址；基线自带的默认地址 `Constants.ROOT_URL` 未改动，本地访问超时，不可用。
3. 不需要登录。歌单页（需登录）的迷你栏本地未实测。
4. 音频播放要求模拟器能访问音频 CDN。本地 2026-10-18 曾因模拟器 DNS 失败无法播放，2026-10-19 恢复；自测前先播一首完整版（非 VIP 试听）歌曲，确认进度在走。

## 6. 自测（Hypium）

自测脚本在 `hypium_tests/`，测试类继承自研框架 `harness.driver.HarnessTestCase`（框架源码由团队汇总时放入成果包 `system-config/test-harness/`）。`<TEST_HARNESS>` 为框架目录，`<PYTHON>` 为装有 Hypium 的 Python。

```bash
PROJ="$PWD"
(cd logs && PYTHONPATH="<TEST_HARNESS>" <PYTHON> -m harness.runner \
    --project "$PROJ" --device <SN> --json "$PROJ/logs/selftest.json" 2>&1 | tee selftest.log)
```

最近一次结果：16 例全部通过，见 `logs/selftest.json`、`logs/selftest.log`。
