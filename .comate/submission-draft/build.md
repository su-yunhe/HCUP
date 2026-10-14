# 构建与运行说明：jm-spec35

## 应用标识

- bundleName：`com.hefengbao.jingmo.hw`
- 入口 Ability：`EntryAbility`（entry 模块 `products/default`）
- 启动入口：桌面图标「京墨文库」，或 `hdc shell aa start -b com.hefengbao.jingmo.hw -a EntryAbility`

## 环境

| 项目 | 版本 |
| --- | --- |
| DevEco Studio | 6.1.0 |
| SDK | HarmonyOS 6.1.0（API 23） |
| 测试设备 | Pura 90 Pro Max 模拟器，HarmonyOS 6.1.0（API 23） |
| Hypium | 6.1.0.210（仅本地自测用，不参与构建） |

环境变量（macOS，按本机 DevEco 安装位置调整）：

```bash
export DEVECO=/Applications/DevEco-Studio.app/Contents
export DEVECO_SDK_HOME="$DEVECO/sdk"
export JAVA_HOME="$DEVECO/jbr/Contents/Home"
export PATH="$DEVECO/tools/node/bin:$DEVECO/tools/ohpm/bin:$DEVECO/tools/hvigor/bin:$DEVECO/sdk/default/openharmony/toolchains:$JAVA_HOME/bin:$PATH"
```

## 依赖安装

工程使用本地 HAR 模块（`commons/*`、`features/*`），依赖关系已在各模块 `oh-package.json5` 中声明，锁文件 `oh-package-lock.json5` 随工程提交。在工程根目录执行：

```bash
ohpm install --all
```

未引入任何新的第三方依赖，`oh-package.json5` 与基线一致。

## 构建

```bash
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

产物（未签名 HAP）：

```
products/default/build/default/outputs/default/default-default-unsigned.hap
```

模拟器自测无需签名配置；基线已移除原作者签名配置，构建时 `No signingConfig found for product default` 属预期告警。

## 安装与启动

```bash
hdc -t <设备序列号> install -r products/default/build/default/outputs/default/default-default-unsigned.hap
hdc -t <设备序列号> shell aa start -b com.hefengbao.jingmo.hw -a EntryAbility
```

## 必要初始化

首次安装后冷启动会弹出隐私确认对话框，需点击「同意」才能进入首页。本题功能位于「首页 → 右上角设置图标 → 其他 → 关于」。

## 本地自测（可选）

自测脚本位于工程内 `hypium_tests/`，依赖赛题包中的 `test-harness`：

```bash
cd <赛题包根目录>
PYTHONPATH=test-harness .venv/bin/python -m harness.runner \
    --project <本工程路径> --device <设备序列号>
```

自测结果不代表正式评测结果。
