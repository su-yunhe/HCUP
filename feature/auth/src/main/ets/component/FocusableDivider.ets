import { ColumnStart, P100, SpaceVerticalLarge } from "designsystem";

/**
 * @file 可聚焦分割线组件
 * @author Joker.X
 */
@ComponentV2
export struct FocusableDivider {
  /**
   * 是否处于聚焦状态
   */
  @Param
  focused: boolean = false;
  /**
   * 是否在分割线上方添加间距
   */
  @Param
  withSpacing: boolean = true;
  /**
   * 激活颜色
   */
  @Param
  activeColor: ResourceColor = $r("app.color.primary");
  /**
   * 非激活颜色
   */
  @Param
  inactiveColor: ResourceColor = $r("app.color.border");
  /**
   * 分割线厚度
   */
  @Param
  thickness: Length = $r("app.float.space_divider");

  /**
   * 构建分割线
   * @returns {void} 无返回值
   */
  build(): void {
    ColumnStart({ widthValue: P100 }) {
      if (this.withSpacing) {
        SpaceVerticalLarge();
      }

      Column()
        .width(P100)
        .height(this.thickness)
        .backgroundColor(this.focused ? this.activeColor : this.inactiveColor);
    }
  }
}
