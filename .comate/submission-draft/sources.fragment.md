# sources.fragment.md — cmu-spec34

供 `3-package.md` 汇总进根 `sources.md`。涉及题目：`cmu-spec34`。

## 随包基线声明

- 基线工程：官方题包提供的 cloudmusic-harmonyosnex 基线（bundle `cloudmusic-harmonyosnex-edc3a3d6d2-base.bundle`，`base_commit` = `edc3a3d6d27b0bf60b3e18477a30f4d85142d0ce`，提交说明 “Competition baseline snapshot; local signing removed”）。随包 `project/` 中除 `changes/final.diff` 所列文件外，均为该基线原样内容，包括基线自带的 `LICENSE`（MIT License，Copyright (c) 2024-present Chenlvin）、`images/`、`entry/src/main/resources/` 下的全部资源。
- 本题**没有新增或修改任何二进制资源**（`changes/final.diff` 无二进制补丁），不存在需另列摘要的外部素材。
- 依赖：沿用基线 `oh-package.json5` 与锁文件，来源 ohpm 仓库（`ohpm.openharmony.cn`）：`@pura/harmony-utils 1.2.4`、`@pie/lazy-data 1.0.0`、`class-transformer 0.5.1`、`@ohos/hypium 1.0.19`、`@ohos/hamock 1.0.0`。本题未新增依赖；`oh-package-lock.json5` 有一处 +2/−1 行的锁文件更新（提交 `b256c8f`，ohpm install 重建，见 `trace-index.md`）。

## 额外来源与第三方组件

- 外部代码、片段、网页、文档：**未使用**。依据：对会话 A `39649b73-d6f6-439f-b7f1-7bc77cc45e16` 与会话 B `16786162-2757-4ccd-a27f-3b71c2342c4b` 全部工具调用参数的扫描——无网页抓取／搜索类工具调用，网络请求仅发往本机 `127.0.0.1:3000`。此结论只覆盖这两个会话。
- 运行时服务端（不属于提交代码，仅用于自测）：用户在宿主机以 Docker 运行的 NeteaseCloudMusicApi（应用 README 指明的基线依赖，项目地址见基线 `README.md`），监听 `3000`，模拟器内应用通过 `http://10.0.2.2:3000` 访问。镜像名／版本／获取方式：`【待补充】`（会话记录中未记载）。
- 测试框架：Hypium `6.1.0.210`（Python 包，`common/test-harness/requirements.txt` 指定）与团队自研 `harness` 封装，见成果包 `system-config/test-harness/`。
- 接口路径（`/personal_fm`、`/personal/fm/mode`、`/fm_trash`）最初来自模型对 NeteaseCloudMusicApi 公开接口的记忆，随后用本机服务端实测核实；未查阅接口文档页面（会话 A 记载）。

## 来源保护

- 未访问来源项目中与本题相关的提交、PR、Issue、补丁及其副本（两个会话的工具调用中无任何外部域名，也无对题包、其他赛题目录的访问）。实际访问范围与措施见 `trace-index.md`。
- 额外来源／访问过来源项目相关提交的人工声明（`spec/submit-input.yaml` 的 `extra_sources`）：`【待补充】`（该文件不存在）。
