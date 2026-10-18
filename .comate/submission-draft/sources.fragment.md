# jm-spec75 来源片段（供汇总进根 `sources.md`）

## 随包基线声明

- 本题工程以官方基线为起点，未引入其他工程代码：jingmo-for-harmonyos，`base_commit` 为 `ff2fb39980fae320da49cd5c0470a37f3d83c369`，题包 `repo_bundles/jingmo-for-harmonyos-ff2fb39980-base.bundle`，提交说明为 "Harmony Cup sanitized baseline snapshot"。
- 基线自带的依赖 `@ohos/hypium 1.0.24`（`oh-package.json5` devDependencies，来自 ohpm.openharmony.cn）没有变动。
- 本题没有新增依赖，没有新增或修改二进制资源，也没有从外部复制代码；复用的只有基线工程自身的组件（如 `ClassicPoemView`）。

## 额外来源

1. **京墨应用数据源** `https://p1-cdn.jingmo.ruaruan.com/api/`
   - 性质：基线应用"设置 → 同步数据"使用的运行时数据接口，地址写在基线代码 `NetworkConst.ets` 中。它不是来源项目的代码仓库，也不是提交、PR、Issue 或补丁。
   - 使用：会话 `282ee238-cd27-46dc-afe3-1dc208a36ee6` 的 #28、#29 在宿主机用 `curl` 下载了 `dataset_v2.json`、`classicalliterature_sentence_v3_{1,2,3}.json`、`classicalliterature_classicpoem_v3_1.json`。用途有两个：
     - 分析数据结构，发现名句 `poem_id` 全部为 null；
     - 把诗词与名句数据经"设置 → 导入数据"导入模拟器，作为自测数据。
   - 派生物：`hypium_tests/fixtures/jm_sentence_poem_link.json`，由 `hypium_tests/make_fixture.py` 基于上述官方数据生成，只用于自测，不进入应用代码。
   - 下载的原始数据文件没有随包提交，宿主机副本已在会话内删除。
2. **自测工具**：Hypium `6.1.0.210`（PyPI 包，团队自测框架 `test-harness` 的依赖，安装源见 `test-harness/README.md`），属于团队公共环境，汇总时可与其他题合并。
3. 用户声明的其他额外来源（`spec/submit-input.yaml` 的 `extra_sources`）：【待补充】

## 来源保护相关的检索结果（事实陈述）

两个指定会话（含子代理）没有调用网页检索或网页抓取工具。工具参数中没有出现题包目录、其他赛题目录或代码托管站点地址。详见 `tasks/jm-spec75/trace-index.md`"公开资料检索"与"来源保护"两项。
