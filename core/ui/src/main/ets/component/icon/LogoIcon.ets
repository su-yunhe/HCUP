import { CommonIcon } from "./CommonIcon";

/**
 * @file 应用 Logo 图标组件
 * @author Joker.X
 */
@ComponentV2
export struct LogoIcon {
  /**
   * 图标大小（单位：vp）
   */
  @Param
  iconSize: number = 24;
  /**
   * 点击回调
   */
  @Param
  onTap: (() => void) | undefined = undefined;

  /**
   * 构建 Logo 图标
   * @returns {void} 无返回值
   */
  build(): void {
    CommonIcon({
      icon: $r("app.media.ic_logo"),
      iconSize: this.iconSize,
      onTap: this.onTap
    });
  }
}
