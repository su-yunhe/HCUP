# 基线理解结论：sym-combo-customize

标注约定：【代码】= 读源码得到并给出 `文件:行号`；【实测】= 在模拟器上实际操作/抓取 UI 树得到（证据在 `logs/baseline/`）；【推测】= 推断，未验证；【Spec】= `spec/requirement.md` 明文。

## 1. 基线快照标识

- `spec/metadata.json` 的 `base_commit` = `21588d3f75b366c0d8de37b59b5634846ce5f347`，已有标签 `base/sym-combo-customize` 指向它。
- 当前 HEAD = `7a35025ad7ee63bccd46bef6fb2ee78bc3207be6`（相对 base 只改了 `oh-package-lock.json5`，ohpm install 产生）。
- 本阶段新打标签：`baseline-sym-combo-customize` → `7a35025`。后续 diff 基准用 `base/sym-combo-customize`（官方 base_commit）。
- 工作区未提交改动（非本阶段产生，来源未验证，【推测】为 DevEco 同步 SDK 时写入）：`build-profile.json5` 在 products[0] 增加 `"targetSdkVersion": "6.1.0(23)"`。基线构建是在该改动存在的状态下完成的。**2026-10-19 用户决定保留这处改动并纳入提交 diff**（acceptance.md U-13）；后续构建和自测都在保留它的状态下进行。
- `spec/`、`logs/` 目前均为未跟踪目录。

## 2. 构建基线状态

环境【实测】：DevEco Studio SDK HarmonyOS 6.1.0.105（API 23）；模拟器 `127.0.0.1:5555`，`harness.env_check` 输出"环境与官方评测规格一致"（Pura 90 Pro Max / 6.1.0.115 / 1308×2880）。

构建命令（工程根目录）：

```bash
D=/Applications/DevEco-Studio.app/Contents
export JAVA_HOME=$D/jbr/Contents/Home
export PATH=$JAVA_HOME/bin:$D/sdk/default/openharmony/toolchains:$D/tools/hvigor/bin:$D/tools/ohpm/bin:$D/tools/node/bin:$PATH
export DEVECO_SDK_HOME=$D/sdk
hvigorw clean --no-daemon
hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon > logs/baseline-build.log 2>&1
```

- 结果：`BUILD SUCCESSFUL`，产物 `entry/build/default/outputs/default/entry-default-unsigned.hap`（704,233 B）。日志 `logs/baseline-build.log`。
- 坑【实测】：不设 `JAVA_HOME` 时 `PackageHap` 失败，`Error Code: 00308018 ... Unable to locate a Java Runtime`。必须用 DevEco 自带 JBR。
- 基线已有告警清单（共 2 条，后续用于对比是否新增告警）：
  1. `ArkTS:WARN File: entry/src/main/ets/entryability/EntryAbility.ets:10:5 Function may throw exceptions. Special handling is required.`
  2. `hvigor WARN: No signingConfig found for product default`
- 构建后 `git status` 未出现 `BuildProfile.ets` 噪声（生成在 `entry/build/` 下，已被 .gitignore 忽略）。
- 安装【实测】：`hdc -t 127.0.0.1:5555 install -r <unsigned hap>` → `install bundle successfully`（`logs/baseline-install.log`）；未签名 HAP 可装到模拟器。bundleName `com.next.liny.symbolu`，`apiTargetVersion 60100023`。

## 3. Spec 描述的入口当前在哪

应用只有一个页面，无路由、无 Navigation：
- `entry/src/main/resources/base/profile/main_pages.json:3` 仅 `pages/Index`；`entry/src/main/ets/entryability/EntryAbility.ets:22` `loadContent('pages/Index')`。【代码】
- 冷启动直接进入符号网格页【实测 b0】。官方测试只能从这一页开始。

| Spec 对象 | 基线位置 | 状态 |
| --- | --- | --- |
| 场景一/三"点击 '^' 展开操作面板" | 无。`Index.ets` 中没有 '^'、`chevron_up` 或任何面板 | 缺失【代码+实测 b0】 |
| 颜色选择器、重置图标、SegmentButton、相应胶囊 | 无 | 缺失 |
| 符号网格 | `Index.ets:21-37` WaterFlow + LazyForEach；单项 `LinysSymbolDisplay` `Index.ets:97-123`，用 `Text(this.symbol.char)` 渲染（`:110-119`），颜色固定 `app.color.font_color_title`（`:111`） | 存在，但用 Text 渲染，无法应用 fontColor 列表/渲染策略 |
| 底部信息栏（No./字符/Unicode/名称） | `Index.ets:39-50`：`Scroll` + `Row{4×LinysCapsuleButton}`，`.scrollable(ScrollDirection.Horizontal)` `:48`、`.scrollBar(BarState.Off)` `:49`、`.edgeEffect(EdgeEffect.Spring)` `:50` | **已是水平可滚动容器**，见第 6 节 |
| 搜索栏 | `Index.ets:52-68`：`TextInput`（`:53-60`，`onSubmit` 触发 `searchFor`）+ 重置图标 `SymbolGlyph($r('sys.symbol.arrow_counterclockwise'))`（`:61-67`，清空输入并显示全部） | 存在 |
| 搜索逻辑 | `Index.ets:78-88`：`name.toUpperCase().includes(key.toUpperCase())` 子串匹配，不 trim | 存在 |
| 场景四拼写错误 | `entry/src/main/ets/objects/linysSymbol.ets:491` `new linysSymbol("󰇢", "U+0F01E2", "kmark_on_bookmark", 476)`；同样错误也在生成产物 `python_script/HMSymbolVF.txt:477` | 待修 |

## 4. 相关现状

**页面状态**【代码】（`Index.ets`）
- `@StorageLink('tablet_mode'/'screen_width'/'screen_height')` `:9-11`，由 `on_main_area_change` `:90-94` 写入 AppStorage；`screen_width` 决定网格列数 `:34`（实测 5 列）。
- `@State inputText` `:13`、`@State symbolTest`（未使用）`:14`、`@State selected: linysSymbol = allSymbols[0]` `:15`。
- `data: LinysSymbolDataSource` `:17`，普通成员（非状态）。

**子组件**【代码】
- `LinysSymbolDisplay` `:97-123`：`@Prop symbol`、`@Link selected`、`@Prop colors: ResourceColor`（声明了但未使用 `:102`）、`@Prop fontWeight` `:103`。点击设置 `selected` `:117-119`。
- `LinysCapsuleButton` `:125-150`：`@Prop text/fontSize/allowCopy`；`Button(text)` 胶囊样式；点击调用 `copy()` 写剪贴板 `:145-149`。`aboutToAppear` 把空串替换成 `¯\_(ツ)_/¯`，**只在首次出现时执行一次** `:131-134`。

**数据模型**【代码】
- `linysSymbol { char, unicode, name, id }` `linysSymbol.ets:1-13`；`allSymbols` 共 3195 条 `:15-3209`。名称来自字体 cmap 的 glyph 名（生成脚本 `python_script/traverseHMSymbolVF.py:22-24`），【推测】拼写错误源自字体本身的 glyph 名。
- 名称重复：`space`（id 0/1）、`line_viewfinder` 各 2 条。
- LazyForEach 数据源 `SymbolDataSource.ets:83-108`，`setData` → `notifyDataReload`；键生成器为 `s.unicode`（`Index.ets:27-29`）。

**网络 / 本地存储**【代码】：无任何网络请求；无 Preferences / PersistentStorage / 数据库；仅 AppStorage 存屏幕尺寸。剪贴板写入 `utils/clipboard_tools.ets:3-12`。

**资源**【代码】：`resources/base/element/color.json` 仅 `start_window_background`、`block_color`、`font_color_title`（dark 目录有对应深色值）；`string.json` 无界面文案资源。

## 5. 可复用的既有实现

| 需求 | 复用对象 | 依据 |
| --- | --- | --- |
| 显示颜色名 / 策略名、点击复制 | `LinysCapsuleButton`（胶囊 + 点击 copy） | `Index.ets:125-150`；Spec"方便复制代码/API 参数" |
| 重置图标、'^' 图标 | 与搜索重置同款 `SymbolGlyph(...).fontColor([...]).fontSize(36).onClick` | `Index.ets:61-67` |
| 颜色下发到网格项 | `LinysSymbolDisplay` 已预留 `@Prop colors` | `Index.ets:102` |
| 动态按名称渲染符号 | 作者注释掉的尝试 `SymbolGlyph($r('sys.symbol.'.concat(this.symbol.name)))` | `Index.ets:107-109`（说明作者意图是 SymbolGlyph 渲染，但该写法未启用，可行性未验证） |
| 页面状态 | `@State` 放在 `Index`，以 `@Prop`/`@Link` 下发 | `Index.ets:13-15,23-26` |
| 水平滚动容器 | 信息栏 Scroll 写法 | `Index.ets:39-50` |

## 6. 缺失项（Spec 要求但基线没有）

1. '^' 入口与可展开的操作面板（场景一、三）。
2. 三组颜色选择器（主色/副色/背景色）、颜色圆点、对应胶囊、重置图标（场景一、二）。
3. 渲染策略 SegmentButton（SINGLE/MULTIPLE_COLOR/MULTIPLE_OPACITY）与策略胶囊（场景三）。`SegmentButton` 在 SDK `openharmony/ets/api/@ohos.arkui.advanced.SegmentButton.d.ets`；`SymbolRenderingStrategy { SINGLE=0, MULTIPLE_COLOR=1, MULTIPLE_OPACITY=2 }` 见 `openharmony/ets/component/symbolglyph.d.ts:103-175`。
4. **网格必须改为 SymbolGlyph（或 Text+SymbolSpan）渲染**：`Text` 只能设单一 fontColor，不支持 fontColor 数组和 renderingStrategy【代码/SDK 声明】。这是本题最大的技术风险：
   - `SymbolGlyph` 入参是 `Resource`，`$r()` 需要字面量；按名称动态构造资源的方式需在开发阶段先做技术验证（未验证）。
   - 【实测 SDK】编译期系统资源表 `openharmony/ets/build-tools/ets-loader/sysResource.js` 的 `sys.symbol` 有 4027 项：`bookmark_on_bookmark` 存在（id 125831608），`kmark_on_bookmark` 不存在。app 的 3195 个名称中有 442 个不在该表（如 `space`、`heart_gap`、`uF0118`、`kmark_on_bookmark`）。若按名称取资源，这些格子可能空白（运行时行为未验证）。这也解释了场景四"引用该符号时失败"。
5. 场景四：改名 `kmark_on_bookmark` → `bookmark_on_bookmark`。
6. 全工程没有任何 `.id()`。

**场景五/六在基线已基本满足**【代码+实测】：信息栏已是水平 Scroll + Spring。实测选中长名称 `headphones_badge_checkmark_shield_filled_battery_filled` 后左滑，名称胶囊完整显示到末尾（b5→b6）；选中 `kmark_on_bookmark` 后名称胶囊初始不在 UI 树中，左滑后出现（b3→b4）。网格 WaterFlow `layoutWeight(1)` 占主体 `Index.ets:33`。弹簧回弹视觉效果未做截图逐帧验证。【推测】上游在该改动前信息栏是 Row，被清理后的基线快照已包含 Scroll；开发阶段把它当作**回归保护项**，加面板时不得破坏。

## 7. 前置环境需求

- 不需要登录、服务端、WebDAV、测试账号或测试数据；全部数据内置在 `linysSymbol.ets`。本地可完全满足。
- 需要：DevEco 自带 JBR（构建）、`hdc` 在 PATH、API 23 模拟器（已就绪）。
- 系统颜色/符号资源依赖设备系统资源；`sys.color` 表中**没有名为 accent 的系统颜色**（SDK 全表搜索 `accent` 无结果），`ohos_id_color_connected` 存在。已决定 `accent` 映射到 `sys.color.ohos_id_color_emphasize`（acceptance.md U-3、U-8）。

## 8. 测试可观测性风险

1. **无任何稳定 id**：所有组件 `id/key` 为空【实测 b0 dump】。新增组件需补 `.id()`；但官方测试按参考实现编写，我们无法知道其 id，**官方测试大概率依赖文本、类型和顺序**，因此文本、组件类型、组件相对顺序同样要尽量贴合 Spec。
2. **UI 树只含可见组件**：完全滚出视口的胶囊不在 dumpLayout 中（b3 中名称胶囊缺失，滑动后 b4 才出现）；部分可见的组件 `bounds` 被裁剪、`origBounds` 为完整尺寸。断言名称胶囊前需先水平滑动。
3. **信息栏滚动偏移不随选中项复位**【实测 b5】：滑到末尾后再选另一个符号，`No. x` 和字符胶囊仍在视口外，不在 UI 树中。连续用例若先滑动再选中再查 `No.` 文本会失败。已决定保持基线、不复位（acceptance.md U-11），自测用例各自冷启动来规避。
4. **dump 不暴露 SymbolGlyph 颜色/渲染策略**：SymbolGlyph 节点只有 `backgroundColor/opacity/bounds/text(空)` 等通用属性【实测 b0 dump】。"网格以新颜色重新渲染"只能通过胶囊文本、组件 `backgroundColor`（如颜色圆点）、`selected` 属性或截图像素间接观测。
5. **类型+顺序选择器会被新增组件打乱**：当前 `Scroll` 唯一（信息栏），`Button` 前 4 个依次为 No./字符/Unicode/名称，`SymbolGlyph` 唯一（搜索重置）。若网格改用 SymbolGlyph，`SymbolGlyph` 数量会变成"网格可见项数 + 图标数"；若面板里再加 Scroll / Button，会改变信息栏的类型序号。
6. **同类同形图标歧义**：实现后会有两个 `arrow_counterclockwise`（搜索重置、颜色重置），类型相同、无文本，只能靠 id 或位置区分。
7. **同名文本歧义**：策略胶囊显示 `MULTIPLE_COLOR` 时，若 SegmentButton 的按钮文字也是 `MULTIPLE_COLOR`，`BY.text` 会匹配两个组件。
8. **网格项文本不可读**：基线网格项是 `Text`，文本为私有区字符（如 `\U000f0000`）；字符胶囊文本两侧带空格（`" 󰇢 "`，`Index.ets:42`）。
9. **搜索只在回车时触发**（`onSubmit` `Index.ets:58-60`），测试需输入后发送回车（实测 `uitest uiInput keyEvent 2054` 可触发）；纯空格不 trim，`"   "` 搜索得到空网格（由代码推出，未实测）。
10. **返回后重进保持状态**【实测 b7】：根页按两次返回，应用进入后台（mission 仍在），再次 `aa start` 搜索词和选中项都保留；`aa force-stop` 后冷启动恢复初始状态（`selected = allSymbols[0]`，显示 `No. 0`/`U+000020`/`space`）【实测 b0】。

## 附：基线实测记录（`logs/baseline/`）

| 文件 | 操作 | 关键观察 |
| --- | --- | --- |
| b0-launch | 冷启动 | 5 列网格；信息栏 `No. 0`/`"   "`/`U+000020`/`space`（`space` 被视口截断）；无 '^'、无面板 |
| b1-search-correct-name | 输入 `bookmark_on_bookmark` + 回车 | WaterFlow 0 个子项（场景四"修复前搜索无结果"复现） |
| b2-search-typo-name | 重置后输入 `kmark_on_bookmark` + 回车 | 1 个结果 |
| b3-select-typo | 点击该结果 | `No. 476`、字符、`U+0F01E2`；名称胶囊在视口外，不在 UI 树 |
| b4-infobar-swiped | 信息栏左滑 | 出现 `kmark_on_bookmark` 胶囊 |
| b5/b6 | 选中长名称后左滑 | 长名称胶囊完整可见至末尾 |
| b7-back-reenter | 返回两次后重新拉起 | 状态保留 |
| b8 | 网格纵向滑动 | 仅 1 个搜索结果，无参考价值 |

