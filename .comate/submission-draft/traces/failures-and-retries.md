# 失败、重试与未采用方案（cmu-spec102）

范围：仅会话表所列两个会话。每条给出原生明细中的定位：`m<消息序号>.e<元素序号>`，
对应 `native/chat_session_<uuid>` 的 `messages[m].elements[e]`；Markdown 副本 `markdown/<uuid>.md` 中按同一消息序号可查到全文。
以下由脚本从工具调用状态、退出码和输出关键字中筛出，再逐条对照原始记录写明原因。原生记录未做删改。

## aed0652d-3906-4632-8dd6-79c640ec113e（0-analyze：基线分析与验收矩阵）

| 位置 | 事件 | 结果与后续 |
| --- | --- | --- |
| m1.e17–e19 | 基线全量构建 `hvigorw` 退出码 255，`logs/baseline-build.log` 显示 `PackageHap` 失败（`00308018`、`BUILD FAILED`） | 判断为缺 Java 运行时，改用 DevEco 自带 JBR 设 `JAVA_HOME` 后重建成功（m1.e19） |
| m1.e25 | `curl` 探测接口，退出码 28（超时） | 探测对象包含基线默认 API 地址 `ROOT_URL`（`Constants.ets`），超时；改用本地 docker API |
| m1.e28 | 截图/抓布局命令退出码 127：`HDC` 变量连同 `-t` 参数被当成一个路径 | 下一条命令改为把 `toolchains` 加入 `PATH` 后重跑成功 |
| m2→m3 | 用户首次提问使用 `Auto` 模型，助手回复状态 `cancelled`，元素 `discard=true` 且为空 | 用户 16 秒后以 `opus 5.5` 重发同一问题（m4），得到回复（m5） |
| m5.e0 | 地址探测退出码 28：旧局域网地址 `192.168.1.97:3000` 不通 | 随后在模拟器上验证 `10.0.2.2:3000`（m7） |
| m7.e1 | 用 Hypium 设置自定义 API 地址失败：`hdc` 不在 PATH，`ConnectionRefusedError` | m7.e2 补 PATH 后重试成功，地址由 `http://192.168.1.97:3000` 改为 `http://10.0.2.2:3000` |
| m7.e3 | 搜索验证脚本 `IndexError`：返回键只收起了键盘，"夜曲"误输入到设置页地址框（未点保存，不落盘） | m7.e4 重启应用确认保存的地址仍为 `10.0.2.2`，m7.e5 从首页重新搜索 |
| m8–m13 | 用户对风险结论追问、补充"进度条最大值取歌曲信息时长"、裁定 U9 纯空格搜索需校验 | 助手据此修改 `spec/acceptance.md`、`spec/baseline-notes.md`（人工提示，非人工改码） |

## d114e8e5-c419-4b59-8a2d-2cdc504837fe（1-do：功能实现与自测）

| 位置 | 事件 | 结果与后续 |
| --- | --- | --- |
| m1.e27 | `edit_file main_pages.json` 被工具拒绝（未先读文件） | m1.e28 读取，m1.e29 重做成功 |
| m1.e42 | `edit_file PlayPage.ets` 被拒（Stale context） | m1.e43 重读；m1.e44 助手判断是自己先前用 `sed` 改的、编辑器尚未同步，重做编辑 |
| m1.e54 | `edit_file helpers.py` 失败：新旧字符串相同 | 同一元素内改正后成功 |
| m1.e62 | `edit_file MEMORY.md` 被拒（未先读） | m1.e64 重做成功（记忆文件，不在工程内） |
| m1.e67 | 第 1 轮全量自测：17 例 16 过 1 失败，`test_01_play_from_sheet_shows_mini_player` 断言"点一次播放应恰好请求 1 次 /song/url/v1，实际 0" | 查明本地 API 对同一 URL 有 120 s 缓存（`max-age=120`），命中缓存的请求不进容器日志；用例改为等缓存过期再计数 |
| m1.e72 | 单例复跑仍失败（同上原因） | 继续排查请求计数 |
| m1.e79 | 只跑 S2：3 例失败，"搜索结果中没有 晴天(深情版)" | 发现本地 API `/search` 中文关键词返回异常结果 |
| m1.e82 | 对比应用搜索结果与原始 API，`json.decoder.JSONDecodeError`，退出码 1 | 确认是服务端问题；自测改为从结果中自动挑一首可完整播放、时长不少于 2 分钟的歌 |
| m1.e105 | 第 2 轮全量自测：17 例 16 过 1 失败，`test_02_repeat_play_within_3s_is_throttled` 期望"操作过于频繁"，实际"开始播放歌曲: 九三" | 判断为验收矩阵 §3.1 推导有误：基线防抖状态在面板组件内，重开面板即重置；Spec 未要求防抖，未改基线，删除该用例 |
| m1（末尾） | 第 3 轮全量自测：16 例全过 | 即 `logs/selftest.json` / `logs/selftest.log` |

各轮自测的 Hypium 原始报告在 `logs/reports/<时间戳>/task_log.log`（6 个目录，含单例与分组复跑）。

## 未采用的候选方案（来自 1-do 会话最终答复，m1 末尾 TEXT）

- 向下箭头放左上角：因与下层结果页返回按钮重叠、连点会多退一层而未采用，改放顶部正中。
- 用 `accessibilityText('向下箭头')` 暴露文字：UI dump 中不可见，改为另加 `accessibilityDescription`。
- 迷你栏显示条件直接用 `player-isplaying`：切歌瞬间为 false 会闪烁，改为新增 `player-hasSong`。
- 自测写死"晴天(深情版)"：因本地 API 搜索异常改为动态选歌。
