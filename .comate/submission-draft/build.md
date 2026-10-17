# jm-spec71 构建运行说明

本说明中的路径均相对工程根目录（成果包内为 `tasks/jm-spec71/project/`）；设备序列号以 `<设备序列号>` 表示。公共环境说明见成果包根 `README.md`。

## 应用标识

| 项 | 值 | 出处 |
| --- | --- | --- |
| bundleName | `com.hefengbao.jingmo.hw` | `AppScope/app.json5` |
| 入口模块 | `default`（type=entry，目录 `products/default`） | `products/default/src/main/module.json5` |
| 入口 Ability | `EntryAbility` | 同上 `mainElement` |
| 版本 | versionName `1.0.0` / versionCode `1000000` | `AppScope/app.json5` |
| 目标/兼容 SDK | targetSdk `6.0.1(21)` / compatibleSdk `5.1.1(19)`，runtimeOS `HarmonyOS` | `build-profile.json5` |

## 环境

- DevEco Studio（含 Node、ohpm、hvigor、HarmonyOS SDK、`hdc`）。整理时本机为 DevEco Studio 6.1.0.860、HarmonyOS SDK 6.1.0（API 23）、hvigor 6.23.7；这是整理时的安装版本，开发会话当时的版本未从记录中核实。
- 需要 `DEVECO_SDK_HOME`、`JAVA_HOME` 指向 DevEco 自带的 SDK 与 JBR，并把 DevEco 的 `tools/node/bin`、`tools/ohpm/bin`、`tools/hvigor/bin`、`sdk/default/openharmony/toolchains`（含 `hdc`）加入 `PATH`。
- 设备：与官方评测规格一致的模拟器（Pura 90 Pro Max，HarmonyOS 6.1.0 / API 23）。

## 依赖安装

```bash
ohpm install --all
```

依赖清单：根 `oh-package.json5`（devDependency `@ohos/hypium@1.0.24`）与各模块的 `oh-package.json5`；锁文件：根与各模块的 `oh-package-lock.json5`。本题新增的依赖都是工程内部模块的 `file:` 引用（`chinese_idiom`、`bookmark`、`utils`、`uicomponents`），没有新增第三方包。

## 构建

```bash
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

产物：`products/default/build/default/outputs/default/default-default-unsigned.hap`。

工程的 `build-profile.json5` 没有配置 `signingConfigs`，构建日志会出现 `No signingConfig found for product default`，产物为未签名 HAP；开发会话中该 HAP 用 `hdc install` 直接装进了模拟器。

构建会改写各模块下的 `BuildProfile.ets`，这是构建生成文件。

## 安装与启动

```bash
hdc -t <设备序列号> install -r products/default/build/default/outputs/default/default-default-unsigned.hap
hdc -t <设备序列号> shell aa start -a EntryAbility -b com.hefengbao.jingmo.hw
```

要从零状态验证首启，先卸载旧包：`hdc -t <设备序列号> uninstall com.hefengbao.jingmo.hw`。

同一上游项目的多道题共用同一个 bundleName，自测前必须先装本题刚构建的 HAP，可用 `hdc -t <设备序列号> shell "bm dump -n com.hefengbao.jingmo.hw"` 的 `updateTime` 核对。

## 必要初始化

- 无需手工导入数据。应用冷启动后由 `IdiomSeeder` 在后台把内置的 49,639 条成语（`features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/`）写入本地 `chinese_idiom` 表。开发会话在模拟器上实测首次启动约 2.4 秒完成（见 `traces/session-a511b975.md` 中 `IdiomSeeder` 日志）。
- 成语首页、收藏、详情、搜索、近反义词跳转不依赖网络；应用声明了 `ohos.permission.INTERNET`，仅用于基线原有的数据同步等功能。

## 自测

自测脚本：`hypium_tests/test_idiom_module.py`（5 个用例：随机展示与刷新、收藏与详情及返回保持、重启后收藏持久化、搜索「一石二鸟」、近反义词跳转）。

脚本通过相对路径引用与工程同级的 `common/test-harness`（`harness.driver.HarnessTestCase`），该目录不在本工程内，成果包中的位置【待补充】（由 3-package 阶段确定）。运行方式（在工程根目录）：

```bash
COMMON="$(cd ../common && pwd)"
python3 -m venv "$COMMON/.venv"
"$COMMON/.venv/bin/python" -m pip install -r "$COMMON/test-harness/requirements.txt"   # hypium==6.1.0.210
mkdir -p logs
PROJ="$PWD"
(cd logs && PYTHONPATH="$COMMON/test-harness" "$COMMON/.venv/bin/python" -m harness.runner \
    --project "$PROJ" --device <设备序列号> --json "$PROJ/logs/selftest.json" 2>&1 | tee selftest.log)
```
