# jm-spec75 构建运行说明

以下命令均在本题工程根目录（成果包内 `tasks/jm-spec75/project/`）执行。公共环境（SDK、DevEco、Node/OHPM/Hvigor、hdc、Python 与 Hypium 版本）见成果包根目录 `README.md`。

## 应用标识

- bundleName：`com.hefengbao.jingmo.hw`（`AppScope/app.json5`），versionName `1.0.0`，versionCode `1000000`
- entry 模块：`default`（`products/default`），入口 Ability：`EntryAbility`（`products/default/src/main/module.json5` 的 `mainElement`）
- SDK：targetSdkVersion `6.0.1(21)`，compatibleSdkVersion `5.1.1(19)`，runtimeOS `HarmonyOS`（`build-profile.json5`）
- 本次构建与自测所用环境：DevEco Studio 6.1.0（`DS-243.24978.46.36.610860`），SDK HarmonyOS 6.1.0（API 23，`6.1.0.105`），本地模拟器

## 依赖

- 根 `oh-package.json5` 只有 devDependencies `@ohos/hypium 1.0.24`，锁文件 `oh-package-lock.json5`（registry `ohpm.openharmony.cn`）；各模块之间是 `file:` 本地依赖。
- 本题没有新增三方依赖，也没有改动任何 `oh-package.json5` 或锁文件（见 `changes/final.diff`）。

## 1. 环境变量

```bash
# DEVECO_CONTENTS 指 DevEco Studio 安装目录下的 Contents 目录（macOS 为 DevEco-Studio.app/Contents）
export DEVECO_CONTENTS="<DevEco Studio Contents 目录>"
export JAVA_HOME="$DEVECO_CONTENTS/jbr/Contents/Home"     # hvigor 打包（PackageHap）需要 Java；可用 DevEco 自带 JBR
export DEVECO_SDK_HOME="$DEVECO_CONTENTS/sdk"
export PATH="$JAVA_HOME/bin:$DEVECO_CONTENTS/tools/node/bin:$DEVECO_CONTENTS/tools/hvigor/bin:$DEVECO_CONTENTS/tools/ohpm/bin:$DEVECO_SDK_HOME/default/openharmony/toolchains:$PATH"
```

## 2. 依赖安装

```bash
ohpm install
```

基线准备脚本用的也是这条命令（题包 `reports/build-baselines/jm-spec75.log` 中的 `[ohpm install]` 段）。

## 3. 构建

```bash
hvigorw clean --no-daemon
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon
```

- 产物：`products/default/build/default/outputs/default/default-default-unsigned.hap`（未签名，模拟器可以直接安装）
- 构建日志：`logs/clean.log`、`logs/build.log`。告警与基线构建日志 `logs/baseline-build.log` 逐行一致。
- `buildMode=debug` 可能改写各模块的 `BuildProfile.ets`。如果工程在 git 下，构建后执行 `git checkout -- $(git diff --name-only | grep 'BuildProfile.ets')` 还原。

## 4. 安装与启动

```bash
hdc -t <设备序列号> install -r products/default/build/default/outputs/default/default-default-unsigned.hap
hdc -t <设备序列号> shell "bm dump -n com.hefengbao.jingmo.hw" | grep updateTime   # 确认装上的是本次产物
hdc -t <设备序列号> shell aa start -a EntryAbility -b com.hefengbao.jingmo.hw
```

同一上游项目的多道题共用这个 bundleName，自测前必须重新安装本题产物。

## 5. 必要初始化（测试数据）

- 不需要登录、服务端或 WebDAV，本题功能全部基于本地 RDB。
- 全新安装时诗词表、名句表都是空的，需要先写入数据，途径有两种：
  1. **设置 → 同步数据**：从应用内置的数据源 `https://p1-cdn.jingmo.ruaruan.com/api/` 拉取。本机模拟器解析不了这个域名，同步失败，所以本次没有走这条路。
  2. **设置 → 导入数据**（本次实际使用）：在系统文件选择器中选择 JSON 文件，文件格式为 `{"total": n, "data": [...], "next_page": null}`。
     先在宿主机从上面的数据源下载 `classicalliterature_classicpoem_v3_1.json`、`classicalliterature_sentence_v3_1.json`，
     再用 `hdc file send` 推到设备的 `/storage/media/100/local/files/Docs/Download/`（本次在设备上分别命名为 `jm_poem_v3_1.json`、`jm_sentence_v3_1.json`），
     最后在导入页的"经典诗文""诗文名句"两行分别选中对应文件。
- 场景四"查看原文"的正向用例需要 `poem_id` 非空的名句，而官方名句数据集的 `poem_id` 全部为 null。自测数据按以下步骤准备：

  ```bash
  python3 hypium_tests/make_fixture.py <名句 JSON> <诗词 JSON> hypium_tests/fixtures/jm_sentence_poem_link.json   # 工程内已附生成结果
  hdc -t <设备序列号> file send hypium_tests/fixtures/jm_sentence_poem_link.json /storage/media/100/local/files/Docs/Download/jm_sentence_poem_link.json
  ```

  然后在 设置 → 导入数据 → 诗文名句 中选择该文件，按 id 覆盖 2162 条名句：1162 条关联真实诗词，800 条指向不存在的 id 99999，200 条为 0。
  重新导入 `jm_sentence_v3_1.json` 可恢复为全部 null。
- 官方评测环境如何注入数据未知（见 `spec/acceptance.md` U4）。

## 6. 自测（Hypium）

需要 `hdc` 在 PATH 中、设备可连接，Python 环境装有 `hypium==6.1.0.210`。自测框架 `test-harness` 随成果包放在 `system-config/test-harness/`。

```bash
HARNESS="<test-harness 目录的上级目录>"   # 该目录下应有 test-harness/harness/
PROJ="$PWD"
cd logs   # Hypium 会在当前目录生成 reports/
PYTHONPATH="$HARNESS/test-harness" python -m harness.runner --project "$PROJ" --device <设备序列号> --json "$PROJ/logs/selftest.json" 2>&1 | tee selftest.log
```

用例在 `hypium_tests/test_*.py`。本次结果为 23 个用例全部通过（0 失败，0 跳过），见 `logs/selftest.json`、`logs/selftest.log`、`logs/reports/2026-10-17-23-50-46/task_log.log`。
场景四用例依赖上一节导入的 fixture。
