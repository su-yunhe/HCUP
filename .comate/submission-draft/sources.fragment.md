# cmu-spec114 来源声明片段（供汇总进根 `sources.md`）

## 1. 随包基线

- 来源项目：cloudmusic-harmonyosnex（云音汇），题包提供的 Harmony Cup sanitized 基线快照。
- 基线提交：`ebe2fbceaf5270ef0f5302edc4f77fa5962b0a3f`（题包 `metadata.base_commit`，本工程 `spec/metadata.json`）。
- 基线 bundle 标识：`repo_bundles/cloudmusic-harmonyosnex-ebe2fbceaf-base.bundle`（`spec/metadata.json` 的 `baseline_bundle`）。
- 获取方式：由赛事提供的基线准备脚本自该 bundle 克隆并检出（记录见 `tasks/cmu-spec114/logs/baseline-prepare.log`，2026-10-12 15:45:45，profile `harmony-cup-build-v1`）。
- 许可：随基线自带，本阶段未核对其许可文件，【待补充】。
- 基线自带的资源（图片、字体、`images/` 等）均沿用基线，本题没有新增、替换或删除任何二进制资源。

## 2. 第三方依赖（来自基线，本题未新增）

由 ohpm 自 `https://ohpm.openharmony.cn/ohpm` 安装，版本以 `oh-package-lock.json5` 为准，依赖本身不随包提供（`oh_modules/` 被排除）：

| 包 | 版本 | 类型 |
| --- | --- | --- |
| `@pura/harmony-utils` | 1.2.4 | dependencies |
| `@pura/spinkit` | 1.0.4 | dependencies |
| `@abner/refresh` | 1.3.8 | dependencies |
| `class-transformer`（`@pura/harmony-utils` 的传递依赖） | 0.5.1 | transitive |
| `@ohos/hypium` | 1.0.19 | devDependencies |
| `@ohos/hamock` | 1.0.0 | devDependencies |

`oh-package-lock.json5` 相对基线只多了 `"enableUnifiedLockfile": false`（提交 `bb23a62`，由 ohpm 重建锁文件产生），依赖版本没有变化。

## 3. 本题额外来源

- 外部代码、图片、文案：无。依据：两个已提交会话的工具调用中，检索类调用只有对赛事官网答疑页的 6 次 `web_fetch`；
  没有从其他项目复制代码的记录。会话外团队成员是否参考过其他资料，【待补充】由队员确认。
- 赛事官网答疑页 `http://swe-openharmony.tech/#r-scoring`：仅用于了解评分与环境约束，未复制其中内容进入工程。
- 自测框架：赛事提供的 `common/test-harness`（`hypium_tests/` 继承其 `HarnessTestCase`），不随本题工程提供；其来源与版本由 `3-package.md` 写入 `system-config/`。
- Skill：会话 71bc8e00 调用 `hmos-arkts-syntax-checker`（`common/skills/`）。其来源、版本与许可见 `common/skills/README.md`，由 `3-package.md` 汇总，此处【待补充】。

## 4. 本题新增代码的来源

- 本题新增或修改的源码由 Comate Agent（opus 5.5）在会话 `1611afd1-2e90-4647-ac14-b9bfc5fb0a02` 中生成，`PrivacyPage.ets` 参照基线内 `WebLogin` 页的写法；
  自测脚本 `hypium_tests/` 同为该会话生成。逐文件对应关系见 `trace-index.md` “与提交源码的对应关系”。

## 5. 来源保护相关披露

- 会话中对应用域名 `docs.chenlvin.cc`、`api.chenlvin.cc` 做过 ping、`curl`、`dig` 与 Web 加载探测（排查隐私页空白）。`docs.chenlvin.cc` 无法解析，未取回任何内容。
  这些域名是基线代码写明的服务地址；是否属于受保护的“来源项目内容”请队员判断（我没有替队员下结论），详见 `trace-index.md` “公开资料检索与代码复用记录”。
- 未发现对题包目录、其他赛题工程目录或来源项目修复提交、PR、Issue、补丁的访问记录（基于工具调用参数的检索，见 `trace-index.md`）。
