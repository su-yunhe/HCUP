import { ColumnStartCenter, LargePaddingVerticalScroll, P100, P60, P70, SpaceVerticalXXLarge } from "designsystem";
import { bp } from "state";

/**
 * @file 认证页面基础布局组件
 * @author Joker.X
 */
@ComponentV2
export struct AnimatedAuthPage {
  /**
   * 页面标题
   */
  @Param
  title: ResourceStr = "";
  /**
   * 是否启用淡入效果（待实现动画）
   */
  @Param
  withFadeIn: boolean = false;
  /**
   * 内容构建函数
   */
  @BuilderParam
  content: CustomBuilder;

  /**
   * 构建认证页面基础布局
   * @returns {void} 无返回值
   */
  build(): void {
    LargePaddingVerticalScroll({ fillMaxSize: true }) {
      ColumnStartCenter({ widthValue: P100 }) {
        Column() {
          Text(this.title)
            .fontSize(28)
            .fontWeight(FontWeight.Medium)
            .fontColor($r("app.color.text_primary"))
            .width(P100)
            .maxLines(2)
            .textOverflow({ overflow: TextOverflow.Clip })
            .textAlign(TextAlign.Start);

          SpaceVerticalXXLarge();
          SpaceVerticalXXLarge();

          if (this.content) {
            this.content();
          }
        }
        .justifyContent(FlexAlign.Start)
        .alignItems(HorizontalAlign.Start)
        .width(bp({
          sm: P100,
          md: P70,
          lg: P60
        }))
        .constraintSize({ minHeight: P100 })
        .padding({
          top: $r("app.float.space_vertical_large_xx"),
          left: $r("app.float.space_horizontal_medium"),
          right: $r("app.float.space_horizontal_medium")
        });
      }
    }
  }
}
