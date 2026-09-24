import { Avatar } from "./Avatar";

/**
 * @file 中等尺寸头像组件
 * @author Joker.X
 */
@ComponentV2
export struct MediumAvatar {
  /**
   * 头像地址
   */
  @Param
  src: ResourceStr | PixelMap | DrawableDescriptor = "";
  /**
   * 点击回调
   */
  @Param
  onTap: (() => void) | undefined = undefined;

  /**
   * 构建中等尺寸头像
   * @returns {void} 无返回值
   */
  build(): void {
    Avatar({
      src: this.src,
      avatarSize: 48,
      onTap: this.onTap
    });
  }
}
