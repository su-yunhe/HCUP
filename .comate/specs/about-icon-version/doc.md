# 关于页展示应用图标和版本号（jm-spec35）

## 1. 需求与检查点拆解

| 维度 | 结论 |
|---|---|
| 入口 | 首页 TopBar 右上角设置图标 → `SettingPage` →「其他」分组下「关于」→ `AboutPage`（链路已存在，不改） |
| 前置数据 | 无登录、无网络、无持久化；仅依赖本地安装包信息（`bundleName=com.hefengbao.jingmo.hw`，`versionName=1.0.0`） |
| 用户动作 | 点击进入、滚动、返回、重复进入 |
| UI 结果 | 页面顶部居中显示圆形应用图标（Image）；图标正下方显示版本名称文本，文本内容**严格等于** `versionName`（如 `1.0.0`，不加"版本"/"v"前缀，兼容精确匹配与包含匹配两种断言）；其下保留原有作者、简介（含 GitHub/Gitee 仓库地址）、公众号、备案号 |
| 数据结果 | 版本号运行时从系统读取，不硬编码；无写入 |
| 网络结果 | 无网络请求 |
| 返回结果 | 返回设置页正常；再次进入时重新读取并显示，内容一致 |
| 边界条件 | 读取包信息失败时不崩溃，仅不显示版本文本并记录日志；深色模式下图标仍清晰（白底圆形） |
| 场景二（更新后同步） | 版本号来自 `bundleManager` 读取的已安装包 `versionName`，每次进入页面重新读取，升级后自然显示新版本 |

参考上游实现（hefengbao/jingmo-for-HarmonyOS 提交 `baddc7d`「About 页面添加 APP Icon, VersionName」）：只改动 `constants` 的 Icon 与媒体资源、`AboutPage.ets`，未修改 `AppScope/app.json5` 的 `versionName`。因此本次**不修改版本号配置**，测试侧应以已安装包的实际 `versionName`（当前 `1.0.0`）为准。

## 2. 技术方案

### 2.1 图标资源
- 新增 `/Users/bress/Documents/code/harmonycup-work/jm-spec35/commons/constants/src/main/resources/base/media/ic_app_icon.png`：复制自 `AppScope/resources/base/media/foreground.png`（1024×1024，应用启动图标「墨」字前景，与桌面图标一致，大尺寸保证高分屏清晰）。
- 使用独立名称 `ic_app_icon`，避免与 AppScope / entry 模块中已有的 `foreground`、`app_icon` 资源同名产生覆盖歧义。
- 放在 `constants` HAR 中：`settings` 已依赖 `constants`，且项目统一通过 `Icon` 常量引用媒体资源。

修改 `/Users/bress/Documents/code/harmonycup-work/jm-spec35/commons/constants/src/main/ets/Icon.ets`（新增一行）：
```ts
static readonly ic_app_icon: Resource = $r('app.media.ic_app_icon');
```

### 2.2 版本号读取
在 `AboutPage.aboutToAppear()` 中使用同步接口 `bundleManager.getBundleInfoForSelfSync(GET_BUNDLE_INFO_DEFAULT)`（API 10+，工程 compatibleSdk 19 可用），`versionName` 属于默认返回字段，无需额外 flag 和权限。
选择同步接口的原因：首帧即有版本文本，不存在空文本→有文本的闪变，UI 自动化查找无时序竞争。

### 2.3 AboutPage 修改
文件：`/Users/bress/Documents/code/harmonycup-work/jm-spec35/features/settings/src/main/ets/pages/AboutPage.ets`

```ts
import { AppConst, Icon, ThemeConst } from 'constants';
import { ContentText } from 'uicomponents';
import { bundleManager } from '@kit.AbilityKit';
import { BusinessError } from '@kit.BasicServicesKit';
import { hilog } from '@kit.PerformanceAnalysisKit';

@ComponentV2
export struct AboutPage {
  @Consumer('NavPathStack') pageStack: NavPathStack = new NavPathStack();
  @Local versionName: string = '';
  @Local desc: string = `...原文不变...`;

  aboutToAppear(): void {
    try {
      const bundleInfo = bundleManager.getBundleInfoForSelfSync(
        bundleManager.BundleFlag.GET_BUNDLE_INFO_DEFAULT);
      this.versionName = bundleInfo.versionName;
    } catch (error) {
      const err = error as BusinessError;
      hilog.error(0x0000, 'AboutPage', 'get bundleInfo failed, code: %{public}d, message: %{public}s',
        err.code, err.message);
    }
  }

  build() {
    NavDestination() {
      Scroll() {
        Column() {
          // 顶部：圆形应用图标 + 版本名称
          Column() {
            Image(Icon.ic_app_icon)
              .id('about_app_icon')
              .width(80)
              .height(80)
              .objectFit(ImageFit.Cover)
              .backgroundColor(Color.White)
              .borderRadius(40)
              .border({ width: 1, color: $r('sys.color.comp_divider') })
              .clip(true)
              .accessibilityText($r('app.string.app_icon_desc'))
            if (this.versionName.length > 0) {
              Text(this.versionName)
                .id('about_version_name')
                .margin({ top: 8 })
                .fontSize(ThemeConst.FontSize_14)
            }
          }
          .width('100%')
          .alignItems(HorizontalAlign.Center)
          .padding({ top: 24, bottom: 16 })

          // 以下为原有内容，保持不变
          ContentText({ text: '❤贺丰宝（hefengbao）设计和编码❤' })
          ContentText({ text: this.desc })
          ContentText({ text: '公众号：NowInLife' })
          Hyperlink(...)  // 原样保留
        }
      }
      ...  // Scroll / NavDestination 属性原样保留
    }
  }
}
```

要点：
- 圆形：等宽高 80vp + `borderRadius(40)` + `clip(true)`，白色底色保证深色模式下圆形轮廓可见；1vp `sys.color.comp_divider` 描边保证浅色模式（白底页面）下圆形轮廓可见。
- 图标与版本文本放在同一纵向 Column，版本文本必然位于图标下方、水平居中；该块位于 Scroll 内容最顶部。
- 为 Image 与版本 Text 设置 `id`，便于自测稳定定位；`accessibilityText` 为图标提供无障碍描述。
- 读取失败时 `versionName` 为空，不渲染空 Text 节点，页面其余内容正常。

### 2.4 字符串资源
`/Users/bress/Documents/code/harmonycup-work/jm-spec35/features/settings/src/main/resources/base/element/string.json` 新增：
```json
{ "name": "app_icon_desc", "value": "应用图标" }
```

## 3. 受影响文件

| 文件 | 类型 | 内容 |
|---|---|---|
| `commons/constants/src/main/resources/base/media/ic_app_icon.png` | 新增 | 应用图标图片 |
| `commons/constants/src/main/ets/Icon.ets` | 修改 | 新增 `ic_app_icon` 常量 |
| `features/settings/src/main/ets/pages/AboutPage.ets` | 修改 | 新增 `versionName` 状态、`aboutToAppear` 读取逻辑、顶部图标+版本 UI |
| `features/settings/src/main/resources/base/element/string.json` | 修改 | 新增 `app_icon_desc` |
| `hypium_tests/test_about_page.py`（工程根目录） | 新增 | 基于 test-harness 约定的 Python Hypium 自测脚本 |

不修改：`AppScope/app.json5`（版本号）、`SettingPage.ets`、`route_map.json`、首页入口。

## 4. 数据流

```
进入 AboutPage → aboutToAppear()
  → bundleManager.getBundleInfoForSelfSync(DEFAULT) → bundleInfo.versionName
  → @Local versionName 赋值 → 首帧渲染 Text(versionName)
Image(Icon.ic_app_icon) ← constants HAR 媒体资源（编译期合入 HAP）
返回 → 页面销毁；再次进入 → 新实例重新读取
```

## 5. 验证方案
1. `hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon` 构建通过。
2. 安装到已连接模拟器（`127.0.0.1:5555`），用 Python Hypium 脚本验证：
   - 首页 → 设置 → 关于：存在 `about_app_icon` 图片且宽高相等（圆形前提）；存在文本等于 `hdc shell bm dump -n com.hefengbao.jingmo.hw` 读到的 `versionName`；版本文本顶部 ≥ 图标底部，且二者水平中心接近。
   - 原有内容：含 `github.com/hefengbao/jingmo-for-HarmonyOS`、`gitee.com/hefengbao/jingmo-for-HarmonyOS` 的简介文本、`公众号：NowInLife`、备案号仍存在。
   - 返回设置页再次进入（重复 3 轮），图标与版本号均一致显示，无崩溃。
3. 截图人工确认圆形效果与深色模式显示。

## 6. 预期结果
- 关于页顶部居中显示圆形「墨」字应用图标，下方显示 `1.0.0`（与安装包一致），其余信息完整保留。
- 应用升级后，关于页显示新的 `versionName`，无需改代码。
