## cml-combo-search（本题片段，供汇总进根 `sources.md`）

### 随包基线声明

- 随包工程以赛题官方基线为起点：来源项目 coolmallarkts，基线提交 `261589401b664d4a9a5622f748071d14e04108e2`（提交说明 "Harmony Cup sanitized baseline snapshot"），由题包提供，metadata 中的基线 bundle 标识为 `repo_bundles/coolmallarkts-261589401b-base.bundle`。基线协议：MIT（工程根 `LICENSE`，Copyright (c) 2025 Joker.X）。
- 基线之后没有任何 git 提交；本题改动全部在 `tasks/cml-combo-search/changes/final.diff` 中（39 个文件：修改 12、新增 27、删除 0）。
- 本题**没有新增任何二进制资源**，也没有引入新的第三方依赖（差异不涉及任何 `oh-package.json5` 或锁文件）。因此不存在需要标注"同源"的二进制摘要。
- 来源项目的上游仓库地址：【待补充】（本工程内未发现可核实的地址，不推测）。

### 第三方组件（均为基线原有，未改动版本）

- 运行依赖（各模块 `oh-package.json5`）：`@ibestservices/ibest-orm` 2.0.2（`core/database`）、`@ohos/axios` 2.2.6（`core/network`）；官方基线准备日志另记录拉取了 `@cashier_alipay/cashiersdk` 15.8.42、`@ohos/crypto-js` 2.0.5、`pako` 2.1.0、`@ibestservices/ibest-ui-v2` 1.1.1。获取方式：`ohpm install`，仓库 `https://ohpm.openharmony.cn/ohpm/`。
- 测试依赖（根 `oh-package.json5` 与 `oh-package-lock.json5`）：`@ohos/hypium` 1.0.24、`@ohos/hamock` 1.0.0。
- 自测框架：团队自研 `common/test-harness`（随 `system-config/test-harness/` 提供），依赖 Python 包 `hypium==6.1.0.210`（`requirements.txt`），获取方式 `pip install -r requirements.txt`。

### 本题额外来源与检索记录

- 赛事官网"具体赛题技术答疑"：`http://swe-openharmony.tech/#r-scoring`，会话中 `web_fetch` 共 3 次（分析会话 2 次、实现会话 1 次）；任务书 `1-do.md` 第 44 行要求查看。用途：了解评测环境、搜索题（cml-combo-search、cml-spec24）外部服务与测试数据的说明。
- 应用自身服务端 `https://mall.dusksnow.top/app/`（基线 `NetworkClient.ets` 的 `BASE_URL`）：会话用 `curl` 调用其搜索关键词与商品分页接口，仅用于确认接口行为与网络状况。是否属于来源保护范围，请队员复核。
- 本题依赖包源码阅读：`@ibestservices/ibest-orm@2.0.2` 的 README、类型声明及反汇编（来自 `ohpm install` 下载的依赖，位于工程 `oh_modules/.ohpm/`）。
- 来源项目保护：会话工具调用中**未出现**对来源项目仓库、提交、PR、Issue、补丁或镜像的访问，未出现题包 `SWE-OpenHarmony/` 或其他赛题工程目录的路径（依据：对两会话全部 `read_file`/`run_command`/`web_fetch` 参数中的路径与 URL 的扫描）。该结论只覆盖会话表中的两个会话。
- 队员补充的额外来源（`spec/submit-input.yaml` 的 `extra_sources`）：**【待补充】**（该文件不存在，未提供；"无"也需要队员明确填写）。
