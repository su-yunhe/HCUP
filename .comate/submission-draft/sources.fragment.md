# jm-spec71 来源声明片段（供汇总进根 `sources.md`）

以下按事实陈述；是否构成违规由参赛队判断，我没有做有利解释。

## 一、随包基线声明

- 官方基线：来源项目 jingmo-for-harmonyos，题包基线 bundle `repo_bundles/jingmo-for-harmonyos-3eb576cf2f-base.bundle`，`base_commit` 为 `3eb576cf2fc348f86eb9f83348be74bd44b662d1`（提交说明 "Harmony Cup sanitized baseline snapshot"）。
- 工程由该基线检出，随包工程中源码、资源、依赖清单（`oh-package.json5`、`oh-package-lock.json5`）的原始内容均来自此基线；基线与最终版本的全部差异见 `changes/final.diff`。
- 官方基线准备脚本（profile `harmony-cup-build-v1`）在基线上改了 3 个文件：`features/chinese/idiom/Index.ets`、`features/chinese/knowledge/Index.ets`、`features/chinese/quote/Index.ets`（修正已有页面导出路径）。记录见 `traces/baseline-prepare.log`。这些改动属于官方准备步骤，已计入 `final.diff`。
- 基线中原有的第三方依赖只有 `@ohos/hypium@1.0.24`（devDependency，锁文件来自 ohpm 官方源 `ohpm.openharmony.cn`）。本题没有新增第三方依赖，新增的依赖都是工程内部模块的 `file:` 引用。
- 基线自带资源：`final.diff` 中没有二进制文件，没有复制基线自带的二进制资源。

## 二、额外来源

### 1. 内置成语种子数据（来自应用公开数据接口）

- 内容：`features/chinese/idiom/src/main/resources/rawfile/chinese_idiom_seed/` 下 `manifest.json` 与 `part_01.json`–`part_20.json`，共 21 个文件、23,241,388 字节，收录 49,639 条成语。逐文件大小与 SHA-256 见 `changes/data-resources.md`。
- 来源：开发会话中用 `curl` 访问 `https://p1-cdn.jingmo.ruaruan.com/api/dataset_v2.json`（数据集索引）和 `https://p1-cdn.jingmo.ruaruan.com/api/chinese_idiom_v5_1.json` 至 `chinese_idiom_v5_5.json`（共 5 页），随后用 `python3` 脚本裁剪字段并分成 20 片写入工程（会话消息 1 / 元素 11–16、20，消息 7 / 元素 37；命令与返回见 `traces/session-a511b975.md`）。会话 `summary.md` 的说法是：这是基线「设置 → 数据同步」运行时下载的同一份数据，版本 v5，仅做字段裁剪与分片。
- 与基线的关系：该域名已写在基线 `commons/constants/src/main/ets/NetworkConst.ets` 第 7 行（`BASE_URL1`），即应用自身的数据接口，不是 Git 仓库、提交、合并请求、Issue 或补丁。
- 访问时间：消息 1 的时间范围为 2026-10-14 11:41–12:47，三条命令的精确时刻在原生明细中没有单独时间戳，【待补充】。
- 数据的许可或使用条款：记录中没有核对，【待补充】。
- 会话 `summary.md` 提示：提交材料的来源说明需如实标注这份数据，本文件即为该标注；是否属于「来源项目中与本题相关的内容」需要你判断。如果判断为受限，影响面是 21 个种子文件及依赖它们的首屏随机、搜索、近反义词跳转等功能。

### 2. 题包 `SWE-OpenHarmony/` 下的资料（开发会话访问）

开发会话使用的任务书 `spec/history/do-v1.md` 第一段明确指示读取 `SWE-OpenHarmony/specs/jm-spec71.md`、`README.md`、`docs/development.md`。按 `fileCache` 和工具调用，会话实际访问了：

- `specs/jm-spec71.md`、`README.md`、`docs/development.md`（`read_file`，2026-10-14 11:42:00）。
- `metadata/jm-spec71.json`（`cat`，消息 1 / 元素 1）。
- 目录列表 `SWE-OpenHarmony/`、`SWE-OpenHarmony/tools`、`SWE-OpenHarmony/examples/jm-spec7/` 及其 `README.md`、示例脚本 `test_favorites_navigation.py`（消息 1 / 元素 8–9）；其中 `examples/jm-spec7` 是另一道赛题 `jm-spec7` 的示例。
- `SWE-OpenHarmony/test-harness/`（含 `README.md`、`harness/app.py`、`harness/driver.py`）和 `SWE-OpenHarmony/reports/2026-10-14-11-51-22`（消息 1 / 元素 10、18，消息 7 / 元素 101）。
- 会话还用题包的 Python 环境 `SWE-OpenHarmony/.venv` 运行自测，并运行了 `examples/jm-spec7/test_favorites_navigation.py` 来确认收藏夹页面结构（消息 7 / 元素 128，输出 `Ran 1 test … OK`）。

这些访问发生在 `1-do.md`、`2-submit.md` 现行访问范围限制之前；现行限制把题包 `specs/`、`metadata/`、`repo_bundles/` 及其他目录列为禁止访问。我只陈述事实，是否合规由你判断。

### 3. 其他

- 本地 SDK 头文件：消息 1 / 元素 19 在 DevEco 自带 SDK 的 `@ohos.data.relationalStore` 声明文件中 `grep` 了批量插入接口，属于官方 SDK 文档类资料。
- 会话工具调用中没有网页搜索、网页抓取，也没有访问 gitee、github、gitcode 等来源项目仓库的记录（按工具参数中的 URL 与路径核对）。该结论不包含模型自身的训练知识。
- 额外来源（`submit-input.yaml` 的 `extra_sources`）：用户未填写，上面各条是我从记录核实出的事实，是否还有其他来源【待补充】。
