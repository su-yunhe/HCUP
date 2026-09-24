import { SpaceHorizontalSmall } from "designsystem";

/**
 * @file 带有垂直装饰线的标题组件
 * @author Joker.X
 */
@ComponentV2
export struct TitleWithLine {
  /**
   * 标题文本
   */
  @Param
  text: string | Resource = "";
  /**
   * 文本颜色
   */
  @Param
  textColor: ResourceColor = $r("app.color.text_primary");
  /**
   * 装饰线颜色
   */
  @Param
  lineColor: ResourceColor = $r("app.color.primary");

  /**
   * 构建标题组件
   * @returns {void} 无返回值
   */
  build(): void {
    Row() {
      Column()
        .width($r("app.float.space_padding_small_x"))
        .height(20)
        .backgroundColor(this.lineColor)
        .borderRadius($r("app.float.radius_small_x"));

      SpaceHorizontalSmall();

      Text(this.text)
        .fontSize($r("app.float.headline_large"))
        .fontColor(this.textColor)
        .maxLines(1)
        .textOverflow({ overflow: TextOverflow.Ellipsis });
    }
    .alignItems(VerticalAlign.Center);
  }
}
