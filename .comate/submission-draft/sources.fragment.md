# sources 片段：cmu-spec99

## 随包基线声明

- 工程基线：官方题包 `repo_bundles/cloudmusic-harmonyosnex-34bbc9d862-base.bundle`，`base_commit` `34bbc9d862701e28718383f6a62fd99f801176ec`（`spec/metadata.json`），由官方基线准备脚本于 2026-10-12 15:46:19 克隆（profile `harmony-cup-build-v1`，`changes: []`）。
- 基线之后的提交 `1e6a42a` 只改了 `oh-package-lock.json5` 两行，是 `ohpm install` 重建的锁文件，不含功能实现。
- 第三方依赖均由 `oh-package.json5` / `oh-package-lock.json5` 声明、经 ohpm 安装，与基线一致，本题未新增依赖：`@pura/harmony-utils`、`@pura/spinkit`、`@yunkss/ef_audio`、`@ohos/axios`、`@ohos/hypium`、`@ohos/hamock`。
- 本题分页写法沿用基线自带的 `entry/src/main/ets/pages/PlayListPage.ets`、`api/playListApi.ets`，属于基线内复用。
- `final.diff` 中 4 个二进制文件（`logs/baseline-*.jpeg`）是 AI 会话在模拟器上截的屏，不是外部素材，也不是基线资源。

## 额外来源

题目级声明 `extra_sources`：【待补充】（`spec/submit-input.yaml` 不存在）。

会话记录中实际发生的公开资料访问（会话 `7d051084-780e-4b8f-82e8-44b79034fa33` 消息 [1]，TOOL #53～#56）：

| 来源 | 结果 | 用途 | 是否复用代码 |
| --- | --- | --- | --- |
| web_search “NeteaseCloudMusicApi /search 接口 limit offset 返回 hasMore songCount” | 返回 5 条结果 | 了解 API 服务 `/search` 的分页参数与返回字段 | 否 |
| `https://twesix.github.io/NeteaseCloudMusicApi`（NeteaseCloudMusicApi 文档） | 抓取失败 | 同上 | 否 |
| `https://docs-neteasecloudmusicapi.focalors.ltd`（NeteaseCloudMusicApi Enhanced 文档） | 抓取失败 | 同上 | 否 |
| `https://github.com/Binaryify/NeteaseCloudMusicApi/issues/497`（“搜索接口返回搜索结果数量”） | 抓取成功 | 了解 `songCount` 字段表现 | 否 |

这些都属于第三方 API 服务端项目 NeteaseCloudMusicApi 的文档或 Issue，不属于本题来源项目 cloudmusic-harmonyosnex。最终是否单列为来源条目，由团队判断。

运行环境中使用的第三方服务（非代码来源）：团队自建的 NeteaseCloudMusicApi 服务（docker 镜像 `binaryify/netease_cloud_music_api`），仅用于基线实测和真实数据自测。
