import { AppConst, Icon, ThemeConst } from 'constants';
import { ContentText } from 'uicomponents';
import { bundleManager } from '@kit.AbilityKit';
import { BusinessError } from '@kit.BasicServicesKit';
import { hilog } from '@kit.PerformanceAnalysisKit';

@Builder
export function AboutPageBuilder() {
  AboutPage()
}

@ComponentV2
export struct AboutPage {
  @Consumer('NavPathStack') pageStack: NavPathStack = new NavPathStack();
  @Local versionName: string = '';
  @Local desc: string = `
『京墨文库』开源的中华文化阅读 APP。献给喜欢中华文字、文学、文化的人。

本应用使用的数据来自网络（主要是 Github 开源的仓库），可在项目仓库查看 README.md 中的说明。

源码仓库：

https://github.com/hefengbao/jingmo-for-HarmonyOS

https://gitee.com/hefengbao/jingmo-for-HarmonyOS

关注公众号『NowInLife』获取更新消息。

如果在使用过程中，遇到内容错误，欢迎在公众号留言说明，我们共同改进。

如果有人想要♥赞助♥本项目，可在公众号文章中赞赏👍。
  `;

  aboutToAppear(): void {
    // 每次进入页面都从已安装包读取版本名称，应用升级后自动显示新版本
    try {
      const bundleInfo = bundleManager.getBundleInfoForSelfSync(bundleManager.BundleFlag.GET_BUNDLE_INFO_DEFAULT);
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

          ContentText({ text: '❤贺丰宝（hefengbao）设计和编码❤' })
          ContentText({ text: this.desc })
          ContentText({ text: '公众号：NowInLife' })

          Hyperlink('https://beian.miit.gov.cn', `备案号：${AppConst.ICP}`)
            .width('100%')
            .padding(ThemeConst.PY_16)
            .color(Color.Gray)
        }
      }
      .width('100%')
      .height('100%')
      .edgeEffect(EdgeEffect.Spring)
      .align(Alignment.TopStart)
    }
    .title($r('app.string.about'))
    .onReady((ctx: NavDestinationContext) => {
      this.pageStack = ctx.pathStack
    })
  }
}