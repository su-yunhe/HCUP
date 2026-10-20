# cm-spec26 来源片段（供汇总进根 `sources.md`）

## 随包基线

- 来源：赛事官方题包提供的基线工程，上游项目 coolmallarkts（鸿蒙商城）的脱敏快照。
- 基线标识：`b2f0caacd0a9461648d06073abcbdcda79420f57`（`Harmony Cup sanitized baseline snapshot`），题包 bundle 名 `coolmallarkts-b2f0caacd0-base.bundle`（取自 `spec/metadata.json`）。
- 随包范围：`project/` 中除 `changes/final.diff` 所列新增、修改文件之外的全部文件均为该基线原样内容；`final.diff` 中 `core/*/oh-package-lock.json5`、`feature/*/oh-package-lock.json5`、`entry/oh-package-lock.json5`、`core/ibestui/oh-package.json5` 的改动来自基线准备步骤（`harmony-cup-build-v1`，见 `logs/prepare-baseline-cm-spec26.log`）和 `ohpm install`，不是本题功能改动。
- 文案与资源：本题没有新增或修改任何二进制资源（图片、字体等）。界面文案复用基线已有字符串资源 `goods_reviews`、`goods_detail`、`anonymous_user`（goods 模块）和 `modal_close`（ui 模块）。

## 依赖（来自 `ohpm.openharmony.cn`，版本据基线准备日志与 `oh-package.json5`）

| 包 | 版本 | 说明 |
| --- | --- | --- |
| `@ohos/axios` | 2.2.6 | 基线依赖 |
| `@ohos/lottie` | 2.0.25 | 基线依赖 |
| `@jjr/lottie_component_v2` | 1.0.1 | 基线依赖 |
| `@ibestservices/ibest-orm` | 2.0.2 | 基线依赖 |
| `@ibestservices/ibest-ui-v2` | 1.1.3 | 基线声明 `^1.0.8`，基线准备步骤固定为 1.1.3 |
| `@ohos/hypium` | 1.0.24 | 根 `oh-package.json5` 的 devDependencies |
| `@ohos/hamock` | 1.0.0 | 根 `oh-package.json5` 的 devDependencies |

没有新增依赖。

## 额外来源

- `extra_sources` 未提供：【待补充】（请队员确认是否参考过任何额外资料或代码）。
- 会话记录中可核实的外部访问（详见 `trace-index.md`）：
  - 赛事官方站点 `http://swe-openharmony.tech/#r-scoring` 的技术答疑页（`web_fetch`，3 次，用于了解评测方式与商城服务的约定）。
  - 题目使用的公共商城服务 `https://mall.dusksnow.top`（`curl`/`urllib` 查询商品与详情接口，用于了解数据形态和选取自测商品）。
- 对原生会话记录的机器检索没有发现访问来源项目 coolmallarkts 的修复提交、合并请求、Issue、补丁或其副本；页面内容层面的访问请队员复核。
- 代码来源：本题新增代码由 AI 在会话中生成。是否参考或复制过外部代码，本阶段无法从记录核实，请队员确认：【待补充】

## 本地自测工具

- 团队公共测试框架 `common/test-harness`（依赖 `hypium==6.1.0.210`），不在本工程内；本题自测用例在 `hypium_tests/test_goods_detail_comments.py`。
