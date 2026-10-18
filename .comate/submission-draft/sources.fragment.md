# cmu-spec1 来源片段（供汇总进根 `sources.md`）

## 随包基线声明

- 工程基线：题包提供的 `repo_bundles/cloudmusic-harmonyosnex-17549abcf6-base.bundle`，`base_commit` 为 `17549abcf6ffa4ee3ff90115945646b4a0018688`，提交说明为 "Harmony Cup sanitized baseline snapshot"。来源项目是 cloudmusic-harmonyosnex，bundleName 为 `cc.chenlvin.cloudmusic`。
- 基线之上只有一个提交 `d03903a`，即 `ohpm install` 重建的锁文件（`oh-package-lock.json5` 增加 `"enableUnifiedLockfile": false`），由基线准备流程产生，不含功能实现。
- 三方依赖：全部来自基线 `oh-package.json5` 原有声明，从 ohpm 中心仓 `https://ohpm.openharmony.cn` 拉取（见 `logs/prepare_baseline.cmu-spec1.log`）。本题没有新增、删除或升级依赖。
- 二进制资源：本题没有新增或修改二进制资源，`final.diff` 中没有二进制变更。

## 额外来源

题目级声明 `extra_sources`【待补充】（`spec/submit-input.yaml` 未提供）。以下是从会话表内两个会话的原始记录中核实到的外部资料与工具使用，供队员核对后确认：

1. 赛事官网常见问题，`http://swe-openharmony.tech/`（含 `/#faq`、`/faq`），阶段 0 会话 `77b7ac42…` 第 1.10—1.12 步用 `web_fetch` 读取了 4 次。目的是按任务书 `spec/0-analyze.md` 的要求查阅赛题技术答疑。只阅读规则说明，没有复用其中的代码。
2. 本地测试服务：docker 镜像 `binaryify/netease_cloud_music_api`，`/inner/version` 返回 4.27.0。仅在本机自测中作为兼容 NeteaseCloudMusicApi 的服务端，不随工程提交，工程代码中也没有它的代码。获取方式与镜像拉取时间【待补充】，会话表内的会话没有执行过拉取。
3. HarmonyOS SDK 类型声明，即本机 DevEco Studio SDK 的 `ets/component/common.d.ts`。阶段 1 会话 `ecfd59f9…` 第 1.36—1.38 步查阅了 `bindSheet` 和 `onWillDisappear` 的声明，属于官方 SDK 文档性质的查阅。
4. 自测框架依赖 Hypium `6.1.0.210`，位于 `harmonycup-work/common/.venv`，阶段 1 会话查阅过其 API。版本与获取方式在团队级 `system-config/test-harness/requirements.txt` 中说明。

核实范围：对两个会话全部工具调用的参数做了 URL 与网络命令扫描。除官网外，只访问了本机或模拟器的本地地址；没有 `git clone`／`fetch`／`pull`，也没有访问来源项目的提交、PR、Issue 或其副本。会话表以外的会话（包括阶段 1 中断前的开发会话）没有核查，结论【待补充】。
