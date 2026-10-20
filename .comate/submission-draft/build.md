# 构建运行说明：cml-combo-search（商品搜索功能）

本文只写本题特有的内容；公共环境（DevEco、SDK、Node/OHPM/Hvigor、hdc、Python/Hypium 版本）见成果包根 `README.md`。
下文以 `<DEVECO>` 表示 DevEco Studio 的 `Contents` 目录，`<PROJECT>` 表示本题工程根目录（成果包内为 `tasks/cml-combo-search/project/`），`<SN>` 表示设备序列号。

## 1. 应用标识

| 项 | 值 | 来源 |
| --- | --- | --- |
| bundleName | `com.joker.coolmall` | `AppScope/app.json5` |
| versionName / versionCode | `1.0.0` / `1000000` | `AppScope/app.json5` |
| 入口 Ability | `EntryAbility`（`mainElement`） | `entry/src/main/module.json5` |
| 入口模块 | `entry`，deviceTypes: phone / tablet / 2in1 | `entry/src/main/module.json5` |
| 权限 | `ohos.permission.INTERNET` | `entry/src/main/module.json5` |
| SDK | targetSdkVersion = compatibleSdkVersion = `6.0.1(21)`，runtimeOS `HarmonyOS` | `build-profile.json5` |
| 签名 | `signingConfigs` 为空，产物为未签名 HAP | `build-profile.json5` |

## 2. 环境变量

命令行构建需要先设置下列变量（CLI 下默认都不在 PATH 中；缺少 `JAVA_HOME` 时 `PackageHap` 阶段会报 "Unable to locate a Java Runtime"）：

```bash
D=<DEVECO>
export JAVA_HOME=$D/jbr/Contents/Home
export DEVECO_SDK_HOME=$D/sdk
export PATH=$JAVA_HOME/bin:$D/tools/hvigor/bin:$D/tools/node/bin:$D/tools/ohpm/bin:$D/sdk/default/openharmony/toolchains:$PATH
```

## 3. 依赖安装

```bash
cd <PROJECT>
ohpm install
```

- 根 `oh-package.json5` 的 devDependencies：`@ohos/hypium@1.0.24`、`@ohos/hamock@1.0.0`；锁文件 `oh-package-lock.json5` 已随工程提供。
- 各模块的第三方依赖（如 `@ibestservices/ibest-ui-v2`、`@cashier_alipay/cashiersdk`、`@ohos/crypto-js`、`pako`）由各模块自己的 `oh-package.json5` 声明，`ohpm install` 从 `ohpm.openharmony.cn` 拉取（官方基线准备脚本的输出见 `logs/prepare_baseline.official.log`）。
- 需要可访问 ohpm 仓库的网络。

## 4. 构建

```bash
cd <PROJECT>
mkdir -p logs
hvigorw clean --no-daemon
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon 2>&1 | tee logs/build.log
```

- 产物（相对路径）：`entry/build/default/outputs/default/entry-default-unsigned.hap`
- 构建会改写各模块的 `BuildProfile.ets`，这些文件在 `.gitignore` 中，不属于交付内容。
- 编译期有若干基线就存在的告警（`@BuilderParam`、`sourceMapsPath`、资源重名等），未新增告警的对比见 `logs/baseline-warnings.txt` 与 `logs/build-warnings.txt`。

## 5. 安装与启动

本题自测所用设备为 arm64 模拟器（hdc 序列号形如 `127.0.0.1:5555`）。

```bash
hdc -t <SN> install -r entry/build/default/outputs/default/entry-default-unsigned.hap
hdc -t <SN> shell "aa start -a EntryAbility -b com.joker.coolmall"
```

- 同一上游项目的多道题共用 bundleName `com.joker.coolmall`，跑测试前务必先装本题刚构建的 HAP，可用 `hdc -t <SN> shell "bm dump -n com.joker.coolmall"` 的 `updateTime` 核对。
- Hypium 的 `start_app("com.joker.coolmall")` 不带 ability 会报找不到主 Ability，必须显式传 `"EntryAbility"`。

## 6. 必要的初始化与外部依赖

- 无需账号、登录或手工造数据。应用首页的商品、推荐搜索词、搜索结果都来自 `core/network/src/main/ets/NetworkClient.ets` 中的 `BASE_URL = https://mall.dusksnow.top/app/`，运行（含自测）时设备需要能访问该服务。
- 推荐搜索词接口：`POST goods/search/keyword/list`；搜索结果接口：`POST goods/info/page`（参数 `keyWord`）。
- 搜索历史保存在本地数据库表 `goods_search_history`（本题把基线的 `search_history` 表改名并调整了结构，见成果包根 `solution.md` 中本题一节）。
- 模拟器网络有时不稳：首次启动首页若显示"网络连接失败"，先重试/重启应用，确认首页能加载商品后再跑依赖网络的用例。

## 7. 自测（Hypium）

自测脚本在 `hypium_tests/`，通过成果包内 `system-config/test-harness/` 中的自研框架运行（框架用法见该目录 README）。命令在 `<PROJECT>` 根目录执行：

```bash
COMMON=<成果包内 system-config/test-harness 的上级目录>   # 其下含 test-harness/ 与 Python 虚拟环境
PROJ="$PWD"
(cd logs && PYTHONPATH="$COMMON/test-harness" python -m harness.runner \
    --project "$PROJ" --device <SN> --json "$PROJ/logs/selftest.json" 2>&1 | tee selftest.log)
```

- Python 依赖：`hypium==6.1.0.210`（见 `test-harness/requirements.txt`）。
- 本题最终一次自测结果：26 条用例全部 `pass`，见 `logs/selftest.json`；完整过程日志见 `logs/selftest.log`、`logs/reports/`。
- 自测在 `logs/` 目录下运行，Hypium 会在当前目录生成 `reports/`，避免污染工程根目录。
