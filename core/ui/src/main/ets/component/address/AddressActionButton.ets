import { CommonIcon } from "../icon/CommonIcon";

/**
 * 地址列表场景的编辑按钮
 * @author Joker.X
 */
@ComponentV2
export struct AddressActionButton {
  /**
   * 点击回调
   */
  @Param
  onTap: () => void = () => {
  };
  /**
   * 图标资源
   */
  @Param
  @Require
  iconResId: ResourceStr = "";
  /**
   * 按钮尺寸（单位：vp）
   */
  @Param
  buttonSize: number = 32;
  /**
   * 图标尺寸（单位：vp）
   */
  @Param
  iconSize: number = 18;
  /**
   * 按钮背景色
   */
  @Param
  bgColor: ResourceColor = $r("app.color.bg_content");
  /**
   * 图标颜色
   */
  @Param
  iconColor: ResourceColor = $r("app.color.text_tertiary");

  /**
   * 构建地址操作按钮
   * @returns {void} 无返回值
   */
  build(): void {
    Row() {
      CommonIcon({
        icon: this.iconResId,
        iconSize: this.iconSize,
        tintColor: this.iconColor
      });
    }
    .width(this.buttonSize)
    .height(this.buttonSize)
    .backgroundColor(this.bgColor)
    .borderRadius(this.buttonSize / 2)
    .justifyContent(FlexAlign.Center)
    .alignItems(VerticalAlign.Center)
    .onClick((): void => this.onTap());
  }
}
