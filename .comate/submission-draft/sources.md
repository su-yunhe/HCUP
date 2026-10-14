# 第三方代码、依赖和资料来源

## 随包基线

- 使用的赛题包版本或提交号：【待补充，见赛题包 release-manifest.json 对应版本】
- 题目 ID 及对应 metadata 中的 `base_commit`：
  jm-spec35 → `8f868136e370596fe0ff731241d630972a51d167`
- 基线准备脚本配置版本及执行记录位置：
  `tools/prepare_baseline.py`，profile `harmony-cup-build-v1`，执行时间 2026-10-12 15:46:29，
  输出 `changes: []`；记录见赛题包 `reports/build-baselines/jm-spec35.log`。
- 原有许可证、版权与来源声明保留情况：
  工程根目录 `LICENSE`（Apache-2.0）及各文件原有版权声明均未改动；
  新增的 `ic_app_icon.png` 复制自基线自带资源 `AppScope/resources/base/media/foreground.png`，
  同属原项目资源，许可状态不变。

## 额外来源

- 来源名称：京墨文库 HarmonyOS 版上游仓库（本题来源项目）
- 公开链接：`github.com/hefengbao/jingmo-for-HarmonyOS`
- 版本、提交号：`main` 分支当时最新版本；以及提交 `baddc7d20cd112be6ae12de2b37eb771cc266b17`
- 访问日期：2026-10-14
- 涉及题目 ID：jm-spec35
- 使用方式：仅参考思路（见下方说明，该来源属于受保护内容，本不应访问）
- 实际访问的内容：
  1. `features/settings/src/main/ets/pages/AboutPage.ets`（main 分支，已含本题功能实现）
  2. 同一文件的 raw 原文
  3. 同一文件的提交历史列表
  4. 提交 `baddc7d`「About 页面添加 APP Icon, VersionName」的文件改动
- 队员或 AI 系统发现和选择该来源的检索、工具调用记录位置：
  主会话 `1791947576719-htj3oc4ev8g` 中的 4 次 WebFetch 调用，详见 `trace-index.md`「原始日志」条目。
- 人工操作及其用途：无。该访问由 AI 在需求分析阶段自主发起，队员未指示访问上游仓库。

## 受保护内容访问情况说明

本题开发过程中，AI 系统访问了上述上游仓库中与本题直接相关的实现文件与功能提交。
依据章程第 5.6、5.7、5.8 条及赛题包 `README.md`、`docs/development.md`、
`docs/public-resource-rule-references.md` 的规定，
"来源项目中与本题相关的修复提交、合并请求、Issue、补丁及其副本" 属受保护内容，
参赛者与 AI 系统均不得访问或引用；轨迹显示访问受保护内容的，该题 F-point 不计通过。

本队如实披露该情况，不隐瞒、不删除相关轨迹记录。

补充事实（供核查参考，不构成豁免理由）：
- 本题 Spec 要求展示应用图标与版本号，鸿蒙平台读取已安装包版本名的公开 API
  (`bundleManager.getBundleInfoForSelf`) 具有唯一性，实现路径与是否参考上游无关；
- 最终实现与上游实现存在明显差异（同步接口、圆形裁剪方式、组件 id、异常兜底、无障碍描述等）；
- 但规则约束的是访问行为本身，而非产出是否受影响，故本队不以此主张该题应计通过。

相关整改措施（后续题目适用）：见 `solution.md`「赛题来源保护措施」一节。

## 无额外来源声明

除上述随包基线及其已有依赖、以及上方如实披露的受保护内容访问情况外，未使用其他额外资料或实现。
未引入任何新的第三方依赖。
