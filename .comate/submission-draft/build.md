# cm-spec26 构建与运行说明

本题基于 coolmall（鸿蒙商城）基线，改动集中在 `feature/goods` 模块的商品详情页（评价区、详情图、评价图片全屏查看器）。

## 应用标识

| 项 | 值 | 出处 |
| --- | --- | --- |
| bundleName | `com.joker.coolmall` | `AppScope/app.json5` |
| 入口模块 / 入口 Ability | `entry` / `EntryAbility` | `entry/src/main/module.json5`（`mainElement`） |
| 版本 | `1.0.0`（versionCode `1000000`） | `AppScope/app.json5` |
| 声明权限 | `ohos.permission.INTERNET` | `entry/src/main/module.json5` |
| 目标 / 兼容 SDK | `6.0.1(21)` | `build-profile.json5` |

同一上游项目的多道题共用同一个 bundleName。测试前必须先安装本题构建的 HAP，再用 `bm dump -n com.joker.coolmall` 核对 `updateTime`。

## 环境

- DevEco Studio（本机 `Info.plist` 记录版本 `6.1.0`），其 `tools/hvigor`、`tools/ohpm`、`tools/node`、`jbr`、`sdk` 随 IDE 提供。
- 构建命令前设置：

```bash
DEVECO=<DevEco-Studio 安装目录>/Contents
export JAVA_HOME="$DEVECO/jbr/Contents/Home" DEVECO_SDK_HOME="$DEVECO/sdk"
export PATH="$JAVA_HOME/bin:$DEVECO/tools/hvigor/bin:$DEVECO/tools/node/bin:$DEVECO/tools/ohpm/bin:$DEVECO/sdk/default/openharmony/toolchains:$PATH"
```

- 设备：模拟器（arm64，API 23，分辨率 1308×2880），通过 `hdc` 连接。以下 `<SN>` 为 `hdc list targets` 给出的设备序列号。
- 网络：应用从公共服务 `https://mall.dusksnow.top` 取商品数据，设备须能访问该域名。

## 依赖安装

依赖由各模块 `oh-package.json5` 与 `oh-package-lock.json5` 锁定，仓库为 `https://ohpm.openharmony.cn/ohpm/`。本题把 `core/ibestui` 的 `@ibestservices/ibest-ui-v2` 固定为 `1.1.3`（基线准备步骤的结果，已含在 `changes/final.diff`）。

在工程根目录执行：

```bash
ohpm install --all
```

说明：基线准备脚本的原始日志只记录了 `ohpm install` 的输出，没有记录完整命令行参数，上面的 `--all` 是标准用法，未在本机原样复现过。

## 构建

在工程根目录执行：

```bash
mkdir -p logs
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon 2>&1 | tee logs/build.log
```

产物：`entry/build/default/outputs/default/entry-default-unsigned.hap`。`build-profile.json5` 的 `signingConfigs` 为空，构建日志中有 `No signingConfig found for product default` 警告，产物为未签名 HAP，在模拟器上可直接安装（见 `logs/install.log`）。

构建会改写各模块的 `BuildProfile.ets`；该文件已在 `.gitignore` 中，不进入版本控制。

## 安装与启动

```bash
hdc -t <SN> install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t <SN> shell "aa force-stop com.joker.coolmall; aa start -a EntryAbility -b com.joker.coolmall"
```

## 必要初始化与操作路径

- 无需额外初始化数据。自测路径不经过登录：从首页商品入口进入商品详情，向下滚动即依次出现“商品评价”卡片、“商品详情”标题与详情图；点击评价缩略图打开全屏查看器。
- 本地自测用例对 `mall.dusksnow.top` 的 DNS 解析失败（模拟器偶发）按 skip 处理，不算通过；跑之前先在设备上 `ping mall.dusksnow.top` 确认网络。

## 自测

自测脚本在 `hypium_tests/test_goods_detail_comments.py`（17 条），使用团队公共测试框架 `common/test-harness`（`hypium==6.1.0.210`）。该框架不在本工程内。运行方式：

```bash
COMMON=<公共目录 common 的路径>   # 内含 test-harness 与已按 requirements.txt 建好的 .venv
PROJ="$PWD"
(cd logs && PYTHONPATH="$COMMON/test-harness" "$COMMON/.venv/bin/python" -m harness.runner \
    --project "$PROJ" --device <SN> --json "$PROJ/logs/selftest.json" 2>&1 | tee selftest.log)
```

最近一次结果见 `logs/selftest.json`：17 条全部 `pass`。成果包中 `common/test-harness` 的存放位置【待补充】（由 `3-package.md` 阶段确定）。
