import { CommonIcon } from "./CommonIcon";

/**
 * @file 右箭头图标组件
 * @author Joker.X
 */
@ComponentV2
export struct ArrowRightIcon {
  /**
   * 图标大小（单位：vp）
   */
  @Param
  iconSize: number = 24;
  /**
   * 图标颜色
   */
  @Param
  tintColor: ResourceColor = $r("app.color.text_tertiary");
  /**
   * 点击回调
   */
  @Param
  onTap: (() => void) | undefined = undefined;

  /**
   * 构建右箭头图标
   * @returns {void} 无返回值
   */
  build(): void {
    CommonIcon({
      icon: $r("app.media.ic_right"),
      iconSize: this.iconSize,
      tintColor: this.tintColor,
      onTap: this.onTap
    });
  }
}
