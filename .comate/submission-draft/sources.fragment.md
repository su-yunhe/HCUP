# sources 片段：cmu-spec102

## 随包基线声明

- 工程基线来自官方题包 `repo_bundles/cloudmusic-harmonyosnex-00b3d8f4f4-base.bundle`，`base_commit` `00b3d8f4f471f31f024860c8d6dbac5df3f27756`（提交说明 "Harmony Cup sanitized baseline snapshot"）。上游项目为 cloudmusic-harmonyosnex（基线 `README.md` 自述为 "Cloud Music For HarmonyOS NEXT"）。
- 基线自带的三方依赖，本题未增删：`@ohos/axios 2.2.4`、`@yunkss/ef_audio 1.0.1`、`class-transformer 0.5.1`、`@pura/harmony-utils 1.2.4`、`@pura/spinkit 1.0.4`。均由 `ohpm install` 从 `ohpm.openharmony.cn` 获取，版本以 `oh-package-lock.json5` 为准。
- 基线自带的图片与媒体资源（`images/`、`entry/src/main/resources/*/media/` 等），本题未改动。资源目录下只改了页面注册文件 `entry/src/main/resources/base/profile/main_pages.json`。
- `logs/baseline/*.jpeg` 是本题分析会话在模拟器上截取的基线应用截图，属于过程证据，不是外部素材。

## 额外来源

| 来源 | 获取方式 | 用途 | 是否进入提交代码 |
| --- | --- | --- | --- |
| 赛事官网技术答疑与评分说明 `http://swe-openharmony.tech/`（`#r-scoring`） | 会话内 `web_fetch`：aed0652d m1 两次，d114e8e5 m1 一次（任务书要求查看） | 确认测试环境约定：API 服务由考核环境准备，本地填 `10.0.2.2:3000`，不得在源码写死个人服务器地址 | 否 |
| NeteaseCloudMusicApi docker 镜像 `binaryify/netease_cloud_music_api`（digest `sha256:42e7d2bf4a705ba4bea74ef9635a24d2921fc3457430b6bf60c6bcc50320b3a3`，容器内 version 4.27.0） | 本机 docker 运行，宿主机 3000 端口 | 本地自测用的 API 兼容服务 | 否 |
| Hypium / xdevice 6.1.0.210（Python 3.13.16，`common/.venv`） | pip 安装 | 运行 `hypium_tests/` 自测 | 否（自测脚本依赖） |
| 团队自研测试框架 `common/test-harness/` | 团队自研 | 自测基类 `HarnessTestCase` 与运行器 `harness.runner` | 否（汇总时放 `system-config/test-harness/`） |

没有复用外部代码。`final.diff` 中新增和修改的源码、测试与文档，都在会话表所列两个会话中由 AI 生成，或按队员要求修改；`build-profile.json5` 的 `targetSdkVersion` 一行来源待确认（见 `trace-index.md`"人工修改索引位置"）。会话中没有访问来源项目仓库、提交、PR、Issue 或补丁。
