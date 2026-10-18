# cmu-spec1 完成情况片段（供汇总进 `solution.md`）

## 题目与状态

- 题目：cmu-spec1，API 服务配置页面优化，共三个场景：结构化在线服务配置表单、发现页未配置引导与底部配置面板、本地曲库空列表引导。
- 建议状态：`submitted`，最终以队员在 `team.yaml` 的 `submitted_tasks` 中填写的为准。
- 记录索引：`tasks/cmu-spec1/trace-index.md`。

## 完成情况

以下据实列出，依据为 `logs/selftest.json` 与会话 `ecfd59f9…` 的结尾总结。

- 场景一：新增 `entry/src/main/ets/components/settings/ApiConfigForm.ets` 结构化表单，包含主机、端口、协议（HTTP/HTTPS）、路径、用户、密码；`ApiSetPage.ets` 改用这个表单。保存逻辑放在 `common/functions/app/settings.ets`，包括配置规范化、URL 拼装、旧版 `apiUrl` 解析、在途保护和过期结果丢弃。`RequestUtil.ets` 在配置了用户名和密码时，给在线服务请求附加 Basic 认证。设置页入口文案改为"在线服务"。
- 场景二：`common/view/Explore.ets` 在未配置或服务不可用时显示"如需连接在线内容，请设置在线服务"和"设置在线服务"按钮，点击后用 `bindSheet` 从底部弹出配置面板；保存并检查通过后刷新在线内容。
- 场景三：`pages/local/LocalSongPage.ets` 的空列表文案改为"本地文件列表为空\n右上方入口支持上传本地音频"。
- 构建：2026-10-18 10:22 clean 构建成功，0 个 ArkTS:ERROR，告警按文件和类别与基线一致（`logs/build.log`、`logs/baseline-build.log`）。
- 自测：用团队自测框架 `harness.runner` 在 ARM64 模拟器（API 23）上跑了 20 条，全部通过：场景一 9 条、场景二 8 条、场景三 3 条（`logs/selftest.json`，10:05）。最终 clean 构建产出的 HAP 已安装，但没有用它再跑一遍自测，两次构建的源码相同。

## 未完成项与已知问题

题目级声明 `known_issues`【待补充】（`spec/submit-input.yaml` 未提供）。以下是 AI 在会话 `ecfd59f9…` 第 1 轮结尾报告的问题，原样转述，由队员确认取舍：

1. 没有测"全新安装"。卸载重装会清掉同 bundleName 的数据，所以没做，改用"保存空主机"模拟未配置状态。
2. 旧版只存了一个 `apiUrl` 字符串时，把它解析回填到各字段（验收项 A18），没有自动化测试。
3. 已配置但服务不可达时，发现页要等启动检查超时（最长约 15 秒）才出现引导；未配置时约 1.5 秒内出现。
4. 本地曲库的空列表文案是一个 Text，中间是真实换行。如果官方测试只按第一行全等查找，可能匹配不上（验收文档中的 U9 残余风险）。
5. 密码以明文存在应用沙箱首选项 `Settings` 中，与基线保存 Cookie 的方式一致，没有加密。
6. 自测结束时，模拟器上的配置指向测试代理 `10.0.2.2:3901`，代理已停止。这只影响本机模拟器的状态，与提交的工程无关。

此外，`build-profile.json5` 中的 `"targetSdkVersion": "6.1.0(23)"` 不在官方基线里。本地所有构建都带着这处修改；去掉后能否构建没有验证，来源【待补充】（见 `trace-index.md`）。

## AI 参与环节

- 阶段 0 需求分析与基线核查，会话 `77b7ac42-d595-441e-bab6-f60246c0afd8`：阅读 Spec 和基线代码，构建、安装基线并在模拟器上实际操作，查阅赛事官网 FAQ，产出验收矩阵 `spec/acceptance.md` 和基线记录 `spec/baseline-notes.md`；按队员确认的假设更新验收矩阵。
- 阶段 1 功能实现：大部分业务代码在阶段 1 中断前的会话中完成，该会话 ID【待补充】，不在本次整理的会话表内。
- 阶段 1 续做，会话 `ecfd59f9-17e3-43b3-87b5-ea1858161860`：编写 Hypium 自测脚本（`hypium_tests/`），多轮失败、排查、重跑；修复发现页配置面板无法再次弹出的问题（`Explore.ets`）；全量自测，clean 构建，告警比对，安装。
- 阶段 2 材料整理：在单独的整理会话中由 AI 完成，不属于解题过程，不在会话表内。
- 人工参与：队员发起各阶段会话、补拷 `spec/metadata.json`、确认 12 条假设、填写会话表。人工直接修改代码的情况【待补充】。
