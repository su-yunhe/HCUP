# 基线理解结论（cmu-spec102）

标注约定：**[代码]** = 读源码得出（附 `文件:行号`，路径相对 `entry/src/main/ets/`）；**[实测]** = 在模拟器上构建、安装、操作得到（证据在 `logs/baseline/`）；**[推断]** = 我的推测，没有验证；**[Spec]** = requirement.md 原文。

## 1 基线快照标识

- `spec/metadata.json` 的 `base_commit` = `00b3d8f4f471f31f024860c8d6dbac5df3f27756`。仓库里原本就有 tag `base/cmu-spec102` 指向它。
- 当前 HEAD = `9b19192c998aca785325ee978f7d1445cd7f5791`（分支 `dev`）。它和 base_commit 只差 `oh-package-lock.json5`（3 行，ohpm install 重建的锁文件），不含功能代码。
- 本阶段新打了 tag：**`baseline-cmu-spec102` → `9b19192`**。
- 开始本阶段时工作区就已经存在、不是本阶段做的改动：`build-profile.json5` 未提交，增加了 `"targetSdkVersion": "6.1.0(23)"`。去掉它能不能构建，**未验证**（没有动这个文件）。
- `spec/` 整个目录未纳入 git（`git status` 显示 `?? spec/`）。`logs/` 是本阶段生成的。

## 2 构建基线状态 [实测]

命令（在工程根目录执行）。注意必须设置 `JAVA_HOME`，否则 `PackageHap` 会失败，报 `00308018 Unable to locate a Java Runtime`：

```bash
export JAVA_HOME=/Applications/DevEco-Studio.app/Contents/jbr/Contents/Home
export DEVECO_SDK_HOME=/Applications/DevEco-Studio.app/Contents/sdk
export PATH=$JAVA_HOME/bin:/Applications/DevEco-Studio.app/Contents/tools/node/bin:/Applications/DevEco-Studio.app/Contents/tools/ohpm/bin:/Applications/DevEco-Studio.app/Contents/tools/hvigor/bin:/Applications/DevEco-Studio.app/Contents/sdk/default/openharmony/toolchains:$PATH
hvigorw clean --no-daemon
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon > logs/baseline-build.log 2>&1
hdc -t 127.0.0.1:5555 install -r entry/build/default/outputs/default/entry-default-unsigned.hap
```

- 结果：`BUILD SUCCESSFUL`（clean 后全量编译约 9 秒）。产物 `entry/build/default/outputs/default/entry-default-unsigned.hap`，2,203,667 字节。日志：`logs/baseline-build.log`、`logs/baseline-clean.log`。
- 未签名的 HAP 可以直接安装到模拟器：`install bundle successfully`（`logs/baseline-install.log`），安装后 `bm dump` 的 updateTime = `1792338243579`。
- 构建后 git 只多了 `logs/`，**没有** `BuildProfile.ets` 之类的构建噪声文件被改写。
- 已有告警清单（后续用来判断有没有新增告警）：
  - `hvigor WARN: No signingConfig found for product default` ×1
  - 资源重名：`'page_show' conflict` ×9，`'lib_name' conflict` ×3（来自 `@ohos/axios`、`@pura/harmony-utils` 的 string.json 和 entry 合并时）
  - ArkTS WARN 一共 613 条：`oh_modules` 里 558 条（三方库），`entry/src` 里 55 条
  - `entry/src` 的 55 条按消息分：`'px2vp' has been deprecated` 15、`Function may throw exceptions` 8、`'showToast' has been deprecated` 8、`'pushUrl' has been deprecated` 7、`'getParams' has been deprecated` 5、`backgroundTaskManager ... not supported on all devices` 3、`'getContext' has been deprecated` 3、`'replaceUrl'` 2、`'back'` 2、`'vp2px'` 1、`'decode'` 1
  - 涉及本题的文件：SearchComponent.ets:28（pushUrl）、BackButton.ets:13（back）、SongsListPage.ets:22/50/64/74（getParams、px2vp）、SongSheet.ets:115（px2vp）、Index.ets:33（px2vp）、ContinuousTask.ets:16/39/40/41/69
- **对开发阶段的影响**：新代码如果照搬基线写法，用了全局 `router.pushUrl` / `router.back` / `px2vp` / `promptAction.showToast`，会产生**新的** deprecated 告警。建议改用 `this.getUIContext().getRouter()`、`this.getUIContext().px2vp()` 等写法，或者接受并在 2-submit 里说明。

## 3 Spec 入口当前在哪

| Spec 入口 | 现状 | 证据 |
| --- | --- | --- |
| 首页 | `pages/Index` 是启动页：`EntryAbility.ets:29` `loadContent('pages/Index')` | [代码] |
| 首页搜索框 | `components/main/SearchComponent.ets:14` TextInput（占位 `请输入搜索内容`），:20-33 搜索按钮 → :28 `router.pushUrl({url:'pages/SongsListPage', params:{searchKeyword}})`；空串时 :32 toast | [代码][实测 b01→b02] |
| 搜索结果列表 | `pages/SongsListPage.ets`：:25-30 `onPageShow` 里靠 `hasLoaded` 防止重复加载；:57 标题 `"${kw}" 的搜索结果`；:58-69 List + `SongCard` | [代码][实测 b02] |
| 歌曲操作面板 | `components/main/SongCard.ets:53-58` `bindSheet`（高 70%），点击切换 `isShowSheet` → `components/sheets/SongSheet.ets` | [代码][实测 b03] |
| 面板"播放" | `SongSheet.ets:65-86`，文字 `播放`（:68）→ :79 先关面板 → :80 `playMusicByUrl(song, artists, picUrl, isValidCookie)`；:77/:85 用 3 秒锁防重复 | [代码][实测 b04] |
| 迷你栏 / 底部播放控制栏 | **不存在**。只有右上角圆形"播控组件"`components/main/PlayController.ets`，挂在 SearchComponent.ets:35 和 ListHead.ets:15，点击弹出 `bindPopup`（标题、歌手、`m:ss / m:ss`、Progress、暂停/继续、`结束播放`） | [代码][实测 b05] |
| 全屏播放页 / 向下箭头 / 进度条拖动 | **不存在**。`resources/base/profile/main_pages.json:2-12` 只注册了 9 个页面，没有播放页 | [代码] |
| 返回首页 | 结果页左上角 `BackButton.ets:13` `router.back()`，或系统返回键 | [代码][实测] |

页面路由方式：全工程都用 `@ohos.router` 的 `pushUrl` / `back` / `replaceUrl`，没有 Navigation / NavDestination。[代码，grep `router\.`]

## 4 相关现状

### 4.1 播放状态模型：全局 AppStorage，没有 ViewModel [代码]

| key | 含义 | 写入位置 | 读取位置 |
| --- | --- | --- | --- |
| `player-isplaying` | 当前有没有活动的播放会话。暂停时**不会**变 false | 置 true：AudioPlayUtils.ets:32/53（调用 `play()` 后立刻置，不等真正开播）；置 false：playerControl.ets:22/49（开新歌前）、:67（stop）、AudioPlayUtils.ets:37/58（异常）、appInit.ets:18（启动） | PlayController.ets:12（`@StorageLink`） |
| `player-ispaused` | 是否暂停 | playerControl.ets:21/48（false）、:74（pause→true）、:80（resume→false）；ContinuousTask.ets:57/59/60（paused / stopped / completed → true） | PlayController.ets:17 |
| `player-song` | 当前 `Song` 对象 | playerControl.ets:23；mode 0 时写空对象 `SongClass`（:50） | PlayController.ets:15 |
| `player-artists` | 歌手字符串（`getArtists` 用 `', '` 拼接）；mode 0 时写的是文件名 | playerControl.ets:24/51 | PlayController.ets:16 |
| `player-picurl` | 封面 URL，渲染时再拼 `?param=NxN` | playerControl.ets:25 | PlayController.ets:18、:91 |
| `player-time` | 当前进度，**毫秒** | AudioPlayUtils.ets:34/55（timeUpdate 回调）。**切歌时不会复位** | PlayController.ets:19、:87、:94-95 |
| `player-mode` | 1 = 在线 URL，0 = 本地文件 | playerControl.ets:20/46 | PlayController.ets:13 |
| `player-fileName` | 本地文件名 | playerControl.ets:47 | PlayController.ets:14 |
| `set-playQuality` | 音质下标 0-3 | Settings.ets:102、appInit.ets:66-73 | playerControl.ets:16、PlayController.ets:20 |

### 4.2 数据模型 [代码]

- `Song { id, name, artists: Artist[], duration }`，duration 单位是**毫秒**（common/entities/SongsResult.ets:6-11）；空对象常量 `SongClass`（:21-31，id = 0）。
- 时间格式化 `changeDuration(ms)` → `m:ss`，分钟不补零（common/functions/functions.ets:41-46）。
- 歌手拼接 `getArtists()`（functions.ets:28-34）。

### 4.3 网络服务 [代码][实测]

- 基地址：`getApiUrl()`（functions.ets:14-21）。打开"自定义API服务器地址"时用 `set-customApiUrl`，否则用 `Constants.ROOT_URL = 'http://111.229.38.178:3000'`（common/constants/Constants.ets:13）。
- 请求封装 `HttpRequest`（common/utils/HttpRequestUtils.ets）：`Request()` 是 POST（:28-63），`RequestWithVipType()` 是 GET（:128-167），都带 cookie，都开着 `usingCache: true`；出错时 1 秒后弹 `网络请求出错` 对话框（:57-59、:161-163）。
- 本题用到的接口（api/songApi.ets）：搜索 `/search?keywords=`（:15-32）；播放地址 `/song/url/v1?id=&level=`（:53-68）；封面 `/song/detail?ids=`（:75-88，失败时返回字符串 `'NULL'`）。
- 播放流程：`playMusicByUrl`（common/functions/playerControl.ets:14-37）→ 写 AppStorage → `mPlayer.reset()` → `ContinuousTask.stopTask()` → `ContinuousTask.startPlay(1, url)`（common/utils/ContinuousTask.ets:26-66：申请长时任务 → 创建 AVSession → `AudioPlayUtils.playWithUrl`）。

### 4.4 播放器 [代码]

- `AudioPlayUtils`（common/utils/AudioPlayUtils.ets）是单例，内部是 `@yunkss/ef_audio@1.0.1` 的 `EfAVPlayer`，`init({immediately:true, loop:false})`。
- `EfAVPlayer`（oh_modules/@yunkss/ef_audio/src/main/ets/audio/EfAVPlayer.ets）提供：`seek(time)`（:207-210，**基线业务代码没有调用过**）、`duration`（prepared 时赋值，:138）、`currentTime`（:198）、`pause` / `play` / `stop` / `reset` / `release`。
- **只能挂一个回调**：`onTimeUpdate`（:216-218）、`onStateChange`（:168-171）、`onError`（:177-179）都是直接赋值，后注册的会覆盖前面的。现在 timeUpdate 被 AudioPlayUtils.ets:33/54 占用，stateChange 被 ContinuousTask.ets:56 占用。新代码再注册的话，会覆盖掉 completed / paused 状态同步或进度写入。
- `release()`（:282-293）会把回调全部清空。`stopMusic` 之后再播，会在 `playWithUrl` 里重新注册 timeUpdate，但 stateChange 要等 `startPlay` 里重新注册。

### 4.5 本地存储 [代码]

- `PreferencesUtils` 存的是设置项（`Settings`：hasAnimation、isCustomApiUrl、customApiUrl、isUsePubCookie、playQuality，appInit.ets:27-74）和用户信息（`UserPreference`）。
- 播放状态**不持久化**，重启后清空 [代码 + 实测 b12：重启后右上角按钮背景 `#FF808080`，即未播放的灰色]。

## 5 可复用的既有实现

| 需求 | 复用 | 位置 |
| --- | --- | --- |
| 跨页面共享播放状态 | AppStorage + `@StorageProp` / `@StorageLink`（PlayController 已经这样用） | PlayController.ets:12-20 |
| 播放 / 暂停 / 结束 | `pauseMusic` / `resumeMusic` / `stopMusic` | playerControl.ets:65-82 |
| 跳转 | `AudioPlayUtils.mPlayer.seek(ms)`（需要包一层，同时写 `player-time`） | EfAVPlayer.ets:207 |
| 时间格式 | `changeDuration` | functions.ets:41 |
| 页面跳转 / 返回 | router `pushUrl` / `back`，新页面要在 main_pages.json 注册 | SearchComponent.ets:28、BackButton.ets:13 |
| 页面骨架 | `Stack` + `padding({top: px2vp(topRectHeight)})` + `backgroundColor($r('app.color.main'))`；底部避让用 `bottomRectHeight` | SongsListPage.ets:16-17、:74-75 |
| 文本样式 | 各文件内的 `@Extend(Text) textStyle`，颜色 `$r('app.color.reverse')` | PlayController.ets:155-161 |
| 图标 | `ic_play_fill`、`ic_public_pause`、`ic_music_fill`、`ic_public_back`（左箭头，可以旋转成向下） | resources/base/media/ |
| 封面 URL 规格 | `picUrl + '?param=256y256'`（大图）、`'?param=100y100'`（小图） | SongSheet.ets:48、SongCard.ets:32 |

## 6 缺失项（Spec 要求但基线完全没有）

1. 底部迷你栏组件：封面、标题、歌手、当前时间、播放/暂停按钮。没有任何页面在底部挂播放 UI [代码 + 实测 b01/b04/b08]。
2. 全屏播放页：页面文件、main_pages.json 注册、向下箭头、可拖动 Slider、当前时间和总时长、播放/暂停按钮。
3. 跳转能力：AudioPlayUtils 没有 seek 方法，seek 后也不会写 `player-time`。
4. 切歌时把进度复位到 0 的逻辑。
5. "向下箭头"图标资源（只能用 `ic_public_back` 旋转，或者用系统资源）。
6. 任何 `.id()`：全工程 0 处 [代码，grep `\.id\(`]。
7. 防止重复打开播放页 / 重复返回的保护。
8. 纯空白关键词校验：基线 SearchComponent.ets:27 的 `if(this.searchKeyword)` 会让 `"   "` 通过，然后跳转并请求 `keywords=%20%20` [代码]。用户已决定要拦截（acceptance.md A47、D2）。

基线缺陷（只记录，本阶段不修）：

- 搜索结果为空时，`dataGot.result.songs` 为 undefined，for-of 抛异常 → `loadSongs` 的 catch 不会把 `isLoading` 复位 → 一直转圈（songApi.ets:22、SongsListPage.ets:32-41）[代码，未实测]。
- `player-isplaying` 在调用 `play()` 后立刻置 true，不管有没有真正开播：资源加载失败时一直显示"播放中"、时间是 0 [实测：b05/b07 弹窗显示 `0:00 / 4:38`，同时 hilog 有 `EfAVPlayer IO Cannot Find Host 5411001`]。
- 切歌时 `player-time` 不复位 [代码]。
- PlayController 的 `dialogController` 在构造时就绑定了 song1 等值，下载对话框里可能是旧歌曲（PlayController.ets:27-41）[代码，未实测，和本题无关]。

## 7 前置环境需求

| 项 | 需要吗 | 本地情况 |
| --- | --- | --- |
| 登录账号 | **不需要**。未登录时搜索、取播放地址都正常 [实测：首页显示 `登录账号\n以显示你的歌单`，照样能搜索、能拿到播放 URL] | 不满足也不影响本题；只有歌单页（A43）需要登录，本地验证不了 |
| API 服务 | 需要 | 本机有 docker 容器 `binaryify/netease_cloud_music_api`，监听 `*:3000` [实测]。App 里**要填 `http://10.0.2.2:3000`**（设置 → 打开"自定义API服务器地址" → 输入 → 点`设置`）。2026-10-19 已经改好并实测：重启后设置仍然保留（v2）；搜索"夜曲"返回列表，播放时 `/song/url/v1` 拿到了播放 URL；docker 日志里有对应的 `/song/detail`、`/song/url/v1` 请求。原先保存的 `http://192.168.1.97:3000` 是之前装 App 留下的旧值（`install -r` 会保留偏好），宿主机 IP 变了以后就不通了；不要再用局域网 IP，换网络就会失效。默认的 `111.229.38.178:3000` 从本机 curl 超时，不可用 [实测] |
| 技术答疑要求 | 正式考核环境会"按题目需要准备相应的服务和初始状态"；本地自测要自己部署兼容服务，在 API 设置页填 `10.0.2.2` + `3000`；**不能在源码里写死个人服务器地址**（swe-openharmony.tech 技术答疑） | 符合，已部署，App 里填的就是 `http://10.0.2.2:3000` [实测] |
| 音频流 / 外网 DNS | **需要**（S4 进度递增、跳转，S1-4 暂停 / 播放的可观测效果） | **现在满足，但不稳定**。2026-10-18 23:50：模拟器解析不了外网域名，AVPlayer 报 `IO Cannot Find Host 5411001`，进度一直是 `0:00` [实测]。2026-10-19 10:02 复测：`晴天(深情版)` 播放后，弹窗进度依次是 `0:07 / 4:38` → `0:12 / 4:38` → `0:17 / 4:38`（每次间隔约 4.5 秒），没有 DNS 报错 [实测]。但模拟器里 `ping m802.music.126.net` 仍然报 `Try again`，恢复的原因**没有确认**。推测和宿主机换了网络有关（IP 从 192.168.1.97 变成 172.24.16.249），**未验证**。每次自测前要先播一首歌，确认进度在走 |
| 歌曲版权 / 试听 | 自测要用完整版歌曲 | 没登录时，VIP 歌只返回 30 秒试听片段：`夜曲`（歌手 Xai小爱，id 2725685941）的 `freeTrialInfo.end=30`、`time=30040`，弹窗停在 `0:30 / 3:53` [实测]。`晴天(深情版)`（id 2652820720）的 `freeTrialInfo` 为 null，是完整版 [实测]。进度条 max 已确定用歌曲信息时长（acceptance.md D1），所以试听歌曲的进度条会比实际能播放的部分长，见 acceptance.md U13 |
| WebDAV / 测试数据 | 不需要 | — |
| 模拟器 | 需要 | `127.0.0.1:5555`，`emulator`，API 23，`OpenHarmony-6.1.0.115`，截图 1308×2880，和官方规格一致 [实测] |
| Hypium 环境 | 需要 | `../common/.venv`（python 3.13 + hypium 6.1.0.210）已存在；本阶段没有跑测试 |

**音频方案现状**：2026-10-19 复测时音频已经能直接播放，所以原先列的 (a) 修 DNS、(b) 本地 mp3 加代理、(c) 只验证 UI 三个方案**暂时都不用做**。如果之后网络变化，又出现 `IO Cannot Find Host`、进度停在 `0:00`，再回到这三个方案里选（推荐 (b)：可控、可重复，和官方"准备相应服务"的思路一致）。

## 8 测试可观测性风险

1. **没有任何稳定 id** [代码]：新组件全部要补，id 清单见 acceptance.md §6。官方测试用的选择器不公开，所以也要让按文本 / 类型查找成立。
2. **歌名文本会在多处重复**：搜索结果项（SongCard.ets:34）、面板（SongSheet.ets:57）、右上角弹窗（PlayController.ets:92）、迷你栏、播放页。更麻烦的是首页 `TextInput` 的 `text` 就是搜索关键词 [实测 b08：`TextInput text='晴天'`]，歌名和关键词相同时 `BY.text(歌名)` 会先命中输入框。好在 router 下层页面不进 dump [实测：结果页 dump 里首页 TextInput 数量为 0]，所以播放页上没有这个问题。
3. **文本 `播放`**：面板按钮就是 `播放`（SongSheet.ets:68），面板打开时迷你栏还在下层的同一页面上。迷你栏里如果出现 `播放` 文本或同名的无障碍文本，`BY.text('播放')` 可能命中错误的组件。
4. **时间文本**：右上角弹窗的格式是 `0:00 / 4:38`，合在一个 Text 里（PlayController.ets:94）。迷你栏和播放页要用单独的 `m:ss` Text，避免和它混淆。弹窗只有点开才在树里。
5. **返回首页后软键盘自动弹出** [实测 b08]：搜索框重新获得焦点，键盘覆盖 y≈1780-2880 px，底部迷你栏会被挡住，点击会落在键盘上。
6. **图标按钮没有文字**：播放/暂停、向下箭头只能靠 id 或类型 + 位置定位。基线里的 Button 都是 `Button(){Image}`，dump 里 `text=''`。
7. **Image 组件很多**：列表每一项都有封面 Image，按类型找 Image 会有歧义，迷你栏封面必须有 id。
8. **资源加载失败时"播放中"是假的**（§6 基线缺陷）：如果音频流又拉不到（§7），按"时间是否递增"做的断言一定失败，不能当作功能失败来看。断言失败时，先看 hilog 里有没有 `IO Cannot Find Host`。
9. **试听片段歌曲**（§7）：进度在 `0:30` 左右就停了，按"时间递增""跳到后半段"做的断言也会失败。自测只能用 `freeTrialInfo` 为 null 的完整版歌曲。
10. **同一个 bundleName 被多道题共用**：每次自测前都要重新安装本题的 HAP，用 `bm dump -n cc.chenlvin.cloudmusic` 的 updateTime 核对。偏好数据（API 地址）会跨安装保留。

## 9 实测操作记录（logs/baseline/）

| 文件 | 内容 |
| --- | --- |
| b01-index | 冷启动首页：未登录，底部没有任何播放 UI，右上角按钮是灰色 |
| b02-search | 搜索"晴天" → 结果页，`"晴天" 的搜索结果`，13 项以上 |
| b03-sheet | 点第 1 项 → 面板：`晴天(深情版)`、`Lucky小爱`、`时长 4:38`、`播放`、`下载`、`无损` |
| b04-after-play | 点 `播放` → 面板关闭，右上角按钮变红；hilog 显示请求 `/song/url/v1` 成功、长时任务启动 |
| b05/b06-popup | 右上角弹窗：`正在播放 [标准]`、`0:00 / 4:38`，5 秒后仍是 0:00（音频 DNS 失败） |
| b07-paused | 弹窗里点暂停后的状态 |
| b08-index-after | 返回首页：搜索框保留"晴天"、键盘弹起、底部依然没有迷你栏 |
| b09/b10 | 更多菜单 → 设置页：当时的自定义 API = `http://192.168.1.97:3000`（已失效，见 §7） |
| v2-settings-after-restart | 改成 `http://10.0.2.2:3000` 并重启后，设置页显示的值仍是它（已持久化） |
| （无截图，Hypium 读取） | 2026-10-19 10:02：`晴天(深情版)` 播放，弹窗进度 `0:07` → `0:12` → `0:17`（共 4:38）；`夜曲`（Xai小爱）停在 `0:30 / 3:53`（试听片段） |
| b12-after-restart | 重启后右上角按钮回到灰色 `#FF808080` |

模拟器上的临时截图和 dump 文件已经从 `/data/local/tmp` 删除。本阶段没有修改任何业务代码。

