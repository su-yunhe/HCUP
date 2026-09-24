import { P100 } from "designsystem";

/**
 * @file 通用卡片容器组件
 * @author Joker.X
 */
@ComponentV2
export struct Card {
  /**
   * 宽度
   */
  @Param
  widthValue: Length | undefined = P100;
  /**
   * 高度
   */
  @Param
  heightValue: Length | undefined = undefined;
  /**
   * 背景色
   */
  @Param
  bgColor: ResourceColor = $r("app.color.bg_white");
  /**
   * 圆角大小
   */
  @Param
  radiusValue: Length = $r("app.float.radius_medium");
  /**
   * 内边距
   */
  @Param
  paddingValue: Padding | Length | LocalizedPadding | undefined = undefined;
  /**
   * 点击回调
   */
  @Param
  onTap: () => void = () => {
  };
  /**
   * 卡片内容
   */
  @Require
  @BuilderParam
  content: CustomBuilder;

  /**
   * 构建卡片视图
   * @returns {void} 无返回值
   */
  build(): void {
    Column() {
      if (this.content) {
        this.content();
      }
    }
    .width(this.widthValue)
    .height(this.heightValue)
    .padding(this.paddingValue)
    .backgroundColor(this.bgColor)
    .borderRadius(this.radiusValue)
    .onClick((): void => this.onTap());
  }
}
