# jm-spec75 基线现状记录

标注约定：**[实测]** 在模拟器上实际操作/构建得到；**[代码]** 读代码得到（附 `文件:行号`）；**[推断]** 我的推测；**[未验证]** 未能确认。

## 1. 基线快照标识

- `base_commit`（`spec/metadata.json`）：`ff2fb39980fae320da49cd5c0470a37f3d83c369`
- 已存在 tag：`baseline-jm-spec75`、`base/jm-spec75`，均指向 `ff2fb39` [实测 `git rev-parse`]。本阶段未新建 tag。
- 分析时 HEAD：`6dfdf33`（分支 `dev`）。`ff2fb39..HEAD` 之间除 `spec/`、`logs/` 外无任何改动 [实测 `git diff --stat ff2fb39 HEAD -- . ':!spec' ':!logs'` 为空]，即构建产物等价于基线代码。
- 本阶段未修改任何业务代码；仅覆盖了 `logs/baseline-{clean,build,install}.log` 三个日志（这三个文件已被提交过，本次内容为重新构建结果）。

## 2. 构建基线状态

构建命令（工程根目录执行）：

```bash
export JAVA_HOME=/Applications/DevEco-Studio.app/Contents/jbr/Contents/Home
export DEVECO_SDK_HOME=/Applications/DevEco-Studio.app/Contents/sdk
export PATH=$JAVA_HOME/bin:/Applications/DevEco-Studio.app/Contents/tools/node/bin:/Applications/DevEco-Studio.app/Contents/tools/hvigor/bin:/Applications/DevEco-Studio.app/Contents/tools/ohpm/bin:$PATH
hvigorw clean --no-daemon > logs/baseline-clean.log 2>&1
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon > logs/baseline-build.log 2>&1
```

- 结果：`BUILD SUCCESSFUL in 6 s 164 ms` [实测]。产物 `products/default/build/default/outputs/default/default-default-unsigned.hap`（未签名）。
- 坑：不设 `JAVA_HOME` 时 `PackageHap` 失败，报 `Unable to locate a Java Runtime`（本机无系统 Java，需用 DevEco 自带 JBR）[实测]。
- 安装：`hdc -t 127.0.0.1:5555 install -r <hap>` → `install bundle successfully` [实测，见 `logs/baseline-install.log`]。
  之前提交的日志里那次失败是 `install version downgrade`（当时模拟器上装着更高版本的别题产物）[推断]。
- 设备：模拟器 `127.0.0.1:5555`，`const.product.model = emulator`，API 23 [实测]。

已有告警清单（共 23 行，后续用于对比是否新增）[实测 `grep -i warn logs/baseline-build.log | sort | uniq -c`]：

```
   1 > hvigor WARN: No signingConfig found for product default
   1 > hvigor WARN: Warning: 'app_name' conflict, first declared.
   7 Warning: 'page_show' conflict, first declared.
  10 Warning: 'page_text_font_size' conflict, first declared.
   1 Warning: 'settings' conflict, first declared.
   1 Warning: the media of 'app_icon.png' does not have a base resource.
   1 Warning: the media of 'icon.png' does not have a base resource.
   1 Warning: the media of 'icon_startwindow.png' does not have a base resource.
```

`page_show`/`page_text_font_size` 冲突来自各 feature 模块模板自带的 `resources/base/element/{string,float}.json`；新增模块若照抄模板会让计数增加。ArkTS 编译无 warning/error。

## 3. Spec 描述的入口当前在哪

实际操作结果 [实测，uitest dumpLayout]：

- 冷启动先显示启动页"献给\n\n喜欢中华文字、文学、文化的人"约 2s，再进入主页（`products/default/src/main/ets/pages/Index.ets:8-20`）。
- 主页：顶部"京墨文库" + 设置图标；下方 2 列网格，分组"古诗文 / 现代汉语 / 传统文化 / 中国"。
  "古诗文"下有"经典诗文"（左）和"诗文名句"（右，bounds `[675,515][1280,693]`）。
- **点击"诗文名句"：无任何反应**，仍停留主页（点击后 UI 树中无 NavDestination）。
- 点击"经典诗文"：进入标题"经典诗文"的页面；空库时只有标题与底部一个刷新按钮；同步/导入数据后显示一首随机诗词。
- 主页没有底部 Tab 栏，App 内也不存在任何"收藏"入口。

对应代码 [代码]：

- 入口页：`products/default/src/main/ets/pages/Index.ets:15-19` → `HomePage`。
- 主页：`features/home/src/main/ets/pages/HomePage.ets:5-19`，`@Provider('NavPathStack') pageStack` + `Navigation(this.pageStack)`，`hideTitleBar(true)`、`hideToolBar(true)`、`NavigationMode.Stack`。
- 菜单网格：`features/home/src/main/ets/view/MenuList.ets`
  - "经典诗文"：`MenuList.ets:19-25`，`onClick → this.pageStack.pushPathByName('ClassicPoemIndexPage', null)`（第 23 行）。
  - "诗文名句"：`MenuList.ets:27-31`，**没有 onClick**。
  - 其他格子（汉字、词语……世界遗产名录）同样无 onClick。
- 设置入口：`features/home/src/main/ets/view/TopBar.ets:13-16`，`pushPathByName("SettingPage", null)`。
- 格子组件：`features/home/src/main/ets/view/Menu.ets:3-23`（`Item`，纯 Text，无 id）。
- 路由注册方式：系统路由表 `routerMap`。HAR 模块 `module.json5` 声明 `"routerMap": "$profile:route_map"`，
  例：`features/classicalliterature/classicpoem/src/main/module.json5:10`，
  `classicpoem/src/main/resources/base/profile/route_map.json:1-12`（`name: ClassicPoemIndexPage`，`buildFunction: ClassicPoemIndexPageBuilder`）。
- 依赖链：`products/default/oh-package.json5:8-11` 只依赖 `home`、`utils`；`features/home/oh-package.json5:8-12` 依赖 `constants`、`settings`、`classicalliterature_classicpoem`；
  `features/settings/oh-package.json5:18` 依赖 `classicalliterature_sentence`。即 sentence 模块目前**经 settings 间接**打进 HAP，home 不直接依赖它。
  新页面要能被 `pushPathByName` 找到，模块需在依赖链中且声明 `routerMap` [推断：基于 classicpoem 的现有写法，未单独实验]。

## 4. 相关现状

### 4.1 sentence 模块（`features/classicalliterature/sentence/`）

- `module.json5:1-11`：`type: har`，**无 `routerMap`**；无 `resources/base/profile/route_map.json`。
- `Index.ets:1-3`：导出 `MainPage`、`Sentence`、`createSentence`、`readRandomSentence`。
- `src/main/ets/pages/MainPage.ets:1-19`：模板占位页（`@Component`，"Hello World"），未被任何地方引用。
- `src/main/ets/model/Sentence.ets`：
  - 类 `Sentence { id; content; from; poem_id: number | null }`（9-26 行）。
  - `createSentence`（28-45）：插入时 `from → from_txt` 列，`ON_CONFLICT_REPLACE`。
  - `readRandomSentence`（47-66）：执行 `DbCRUDConst.READ_RANDOM_CLASSICALLITERATURE_SENTENCE`，`objectiveRDB` 未就绪时直接返回 null。
  - `parse`（71-78）：`poem_id` 用 `getLong` 读取——数据库值为 NULL 时很可能得到 0 而不是 null [推断，未验证]。
- 依赖：`oh-package.json5:8-11` 只有 `constants`、`utils`（没有 `uicomponents`，也没有 `classicpoem`）。

### 4.2 classicpoem 模块（`features/classicalliterature/classicpoem/`）

- `ClassicPoemIndexPage.ets:10-51`：`@ComponentV2`，`@Consumer('NavPathStack')`，`aboutToAppear → refresh() → readRandomClassicPoem()`；
  `NavDestination().title(String.classicalliterature_classicpoem).toolbarConfiguration([{value: 刷新, icon: ic_public_refresh, action}], {hideItemValue: true})`；
  `onReady` 里 `this.pageStack = ctx.pathStack`。**只有随机，没有按 id 读取的函数，也不接收路由参数**。
- `ClassicPoemView.ets:5-48`：`@Param @Require classicPoem`；依次渲染 标题（11）、"【朝代】作者"（13，合并为一个 Text）、序言（16-21）、正文（22-24）、
  注释/译文/创作背景/赏析/点评（25-44，`BoldTitle` + `Content`）。不显示 `subtitle`。无任何 `.id()`。
- `ClassicPoem.ets`：字段 9-24；`readRandomClassicPoem` 91-110；`parse` 115-133。
- `Index.ets:1`：只导出 `ClassicPoem`、`createClassicPoem`、`readRandomClassicPoem`，**不导出 `ClassicPoemView`**。

### 4.3 收藏（bookmark）

- 表：`bookmarks (id integer primary key autoincrement, bookmarkable_id integer, bookmarkable_model text)`，
  `commons/constants/src/main/ets/DbConst.ets:70-72`，在 `DbUtil.init` 首次建库时创建（`DbUtil.ets:103-108`）。无唯一约束、无任何 CRUD 代码。
- 模块 `features/bookmark/`：`BookmarkIndexPage.ets:1-21`（空 `NavDestination`，标题 `String.bookmark` = "收藏夹"）；`model/Bookmark.ets:1-5`（类名小写 `bookmark`）。
  `route_map.json:2` 键名为 **`routeMap`**（classicpoem/settings 用的是 `routerMap`）；
  该模块虽在 `build-profile.json5:73-74` 注册，但**没有任何模块依赖它**，不会被打进 HAP [代码]。
- 图标：`Icon.ic_bookmark`、`Icon.ic_bookmark_border`（`commons/constants/src/main/ets/Icon.ets:2-3`），目前无人使用。

### 4.4 状态模型、数据层、网络、本地存储

- 状态管理：全部页面用 V2 装饰器（`@ComponentV2`、`@Local`、`@Param`、`@Consumer/@Provider('NavPathStack')`）[代码，见 4.2 与 `HomePage.ets:4-6`]。
- RDB：`commons/utils/src/main/ets/data/DbUtil.ets`
  - 库名 `jingmo.db`，`SecurityLevel.S1`，`ICU_TOKENIZER`（15-19）。
  - `init` 在 `EntryAbility.onWindowStageCreate` 调用（`products/default/src/main/ets/entryability/EntryAbility.ets:24`），回调式异步；
    `storeVersion == 0` 时建全部表并置 version=1（32-113）。
  - 第 24 行在判断 `error` 之前就读 `rdbStore.version`，出错时会抛异常 [代码，基线问题，只记录]。
  - 模块里通过 `import DbUtil from 'utils/src/main/ets/data/DbUtil'` 直接拿单例（`Sentence.ets:5`），`utils/Index.ets` 未导出 DbUtil。
- SQL 常量：`DbConst.ets`；随机读 `READ_RANDOM_CLASSICALLITERATURE_SENTENCE`（107-110）、`READ_RANDOM_CLASSICALLITERATURE_CLASSICPOEM`（103-106）。
  `READ_CHINA_WORLDCULTUREHERITAGE`（76-78）缺空格（`...TABLE + 'where id = ?'`），说明按 id 读的写法基线中尚无可用样例 [代码]。
- Preferences：`commons/utils/src/main/ets/data/PrefUtil.ets`，只存各数据集版本号。
- 网络：`commons/utils/src/main/ets/network/HttpUtil.ets:8-40`（`httpRequestGet`），只用于"设置→同步数据"；本题功能不涉及。
- 字符串资源：`commons/constants/src/main/resources/base/element/string.json`，`classicalliterature_sentence` = "诗文名句"（80-81）、
  `classicalliterature_classicpoem` = "经典诗文"（72-73）、`refresh` = "刷新"（112-113）、`bookmark` = "收藏夹"（120-121）；
  通过 `commons/constants/src/main/ets/String.ets` 以 `String.xxx` 引用。主题常量 `ThemeConst.ets`。
- 通用组件：`commons/uicomponents`，只有 `BlockTitle`、`BoldTitle`、`Content`（`Index.ets:1-3`）。

## 5. 可复用的既有实现

| 需求 | 可复用 | 位置 |
| --- | --- | --- |
| 入口跳转 | `pageStack.pushPathByName('<RouteName>', param)` | `MenuList.ets:22-24` |
| 页面骨架 | `@Builder XxxBuilder()` + `NavDestination` + `onReady(ctx => pageStack = ctx.pathStack)` + `route_map.json` | `ClassicPoemIndexPage.ets:5-50`、classicpoem `route_map.json` |
| 随机读名句 | `readRandomSentence()` | `Sentence.ets:47-66` |
| 名句模型 | `Sentence` | `Sentence.ets:9-26` |
| 诗词展示 | `ClassicPoemView`（需从 classicpoem `Index.ets` 导出） | `ClassicPoemView.ets:5-48` |
| 诗词模型/解析 | `ClassicPoem`、`parse` | `ClassicPoem.ets:9-133` |
| 刷新工具栏写法 | `toolbarConfiguration` + `Icon.ic_public_refresh` | `ClassicPoemIndexPage.ets:36-46`（观测性问题见 §8） |
| 收藏存储 | `bookmarks` 表（多态：`bookmarkable_model` + `bookmarkable_id`） | `DbConst.ets:70-72` |
| 收藏图标 | `ic_bookmark` / `ic_bookmark_border` | `Icon.ets:2-3` |
| 列表/标题样式 | `BlockTitle`、`Content`、`ThemeConst.P_X16_Y8` | `commons/uicomponents`、`ThemeConst.ets` |
| 带参数路由的接收 | 基线无样例（所有 push 都传 `null`），需自行用 `NavDestinationContext.pathInfo.param` 或 `getParamByName` | — |

## 6. 缺失项（Spec 要求但基线完全没有）

1. "诗文名句"格子的点击跳转（`MenuList.ets:27-31`）。
2. sentence 模块的路由注册（`module.json5` 无 `routerMap`，无 `route_map.json`），以及名句首页、收藏列表页、名句详情页三个页面。
3. sentence 模块对 `uicomponents`、`classicpoem` 的依赖（若要复用 `ClassicPoemView`/`ClassicPoem`）；home 是否直接依赖 sentence。
4. 名句按 id 读取、诗词按 id 读取的查询函数与 SQL。
5. 收藏的增/删/查/判断是否已收藏（`bookmarks` 表有结构无代码）。
6. 诗词详情页（按 id 展示的路由页）。现有 `ClassicPoemIndexPage` 只能随机。
7. "查看原文"入口与判定逻辑。
8. "生成图片"能力（工程中无 `componentSnapshot`/`image.createImagePacker`/`SaveButton` 的任何使用 [代码，grep 为空]）。
9. 底部 Tab / 全局"收藏"入口（基线无 `Tabs`，[代码 grep 为空] + [实测]）。
10. 全部稳定 `.id()`（`features/`、`commons/`、`products/` 的 `src/main` 下没有任何 `.id(` / `.key(` 调用 [代码 grep 为空]；dumpLayout 中应用组件 key 全为空 [实测]）。

## 7. 前置环境需求

- 登录账号 / 服务端 / WebDAV：**不需要**。本题全部功能基于本地 RDB [代码]。
- 测试数据：**需要**。全新安装时 `classicalliterature_sentence`、`classicalliterature_classicpoem` 均为空 [实测：经典诗文页空白]。写入途径：
  1. 设置 → 同步数据：从 `https://p1-cdn.jingmo.ruaruan.com/api/` 拉取（`NetworkConst.ets:7`，`DatasetViewModel.ets:58-73`）。
     本次实测：页面能列出远端数量（经典诗文 955、诗文名句 10000），但点同步时模拟器 DNS 解析失败
     （hilog：`Failed to resolve the host name`；模拟器内 `ping` 该域名返回 `Try again`），界面显示 `code = undefined, msg = undefined`
     （`SyncDataList.ets:299-301` 把字符串当 BusinessError 读，基线问题，只记录）。**同步不可依赖**。
  2. 设置 → 导入数据：系统文件选择器选 JSON 文件（`ImportDataList.ets:404-424`），格式 `{"total": n, "data": [...], "next_page": null}`。
     本次实测可用：在宿主机从同一 CDN 下载 `classicalliterature_classicpoem_v3_1.json`、`classicalliterature_sentence_v3_1.json`（各一页即全集），
     `hdc file send` 到模拟器 `/storage/media/100/local/files/Docs/Download/`（文件名 `jm_poem_v3_1.json`、`jm_sentence_v3_1.json`，**已保留在模拟器上**供后续阶段复用），
     在导入页分别选择后显示 955 / 10000，之后经典诗文页能正常显示随机诗词 [实测]。
- 场景四正向用例的数据：官方数据集 10000 条名句 `poem_id` **全部为 null** [实测，宿主机分析下载的 JSON]，
  所以仅靠官方数据无法出现"查看原文"。自测需要自造 `poem_id` 指向已有诗词 id 的名句并通过"导入数据"写入。
  可用的真实配对样例（按"作者《标题》"与诗词 writer+title 匹配得到，仅供造数据）：
  名句 id 3"十年生死两茫茫，不思量，自难忘。"→ 诗词 id 400《江城子·乙卯正月二十日夜记梦》；
  名句 id 27"此情可待成追忆？只是当时已惘然。"→ 诗词 id 206《锦瑟》。
- 官方评测环境中数据如何注入：**未知**（见 acceptance U4）。
- 模拟器状态说明：同一 bundleName（`com.hefengbao.jingmo.hw`）被多道题共用；本次已在模拟器上导入上述两份数据，`install -r` 覆盖安装不会清除。

## 8. 测试可观测性风险

1. **全部缺 id**：见 §6 第 10 条。新增组件均需补 `.id()`（建议见 acceptance §0.4）。
2. **`toolbarConfiguration` 不可加 id 且文字不进树**：经典诗文页工具栏在 UI 树里只有
   `MenuItem key=__NavdestinationField__ToolBar__MenuItem1__` + 一个无文字 Image（`hideItemValue: true`）[实测]。若名句首页沿用此写法，
   收藏/生成图片/刷新/收藏入口都只能按序号定位，且无法按文字找到。
3. **同名文字**：
   - "诗文名句"：主页格子与名句首页标题同名；导入/同步页也有"诗文名句"行（不同页面，影响较小）。
   - "收藏"：若收藏切换按钮与收藏列表入口都用"收藏"，同屏重名（acceptance U1）；全局模块标题"收藏夹"含"收藏"子串，包含匹配会命中。
   - "经典诗文"：主页格子与经典诗文页标题同名；若诗词详情页标题也用"经典诗文"，与经典诗文首页难以区分（建议详情页标题用诗名或另起文案）。
   - 名句与诗词正文：名句文字通常是诗词正文的一部分，在诗词详情页用"包含"匹配会找到名句文字，可能误判"仍停留在名句页"。
   - 名句 `content` 重复 1049 条 [实测数据]：列表项需按 id 区分。
4. **系统 key 可用**：NavDestination 标题 `__NavdestinationField__Text__MainTitle__`、返回按钮 `__NavdestinationField__BackButton__Back__` 稳定存在 [实测]。
5. **自定义组件的点击区域**：主页格子 `Item` 的 onClick 挂在自定义组件上，dump 中 Text 节点 `clickable=false`，但按文字坐标点击能触发（"经典诗文"实测可进入）。
   给 `Item` 加 `.id()` 后 id 落在外层节点上 [推断，未验证]。
6. **异步初始化**：`DbUtil.init` 异步完成；启动页 2s 通常足够，但测试若跳过启动页极快进入名句首页，首次随机可能拿到 null [推断，未验证]。
7. **未验证项**：`getLong` 读 NULL 的返回值；Navigation 栈下层页面是否出现在 dumpLayout 中（本次只观察到栈顶页面）；
   工具栏 `status/activeIcon` 在 Hypium 中的可读字段。

