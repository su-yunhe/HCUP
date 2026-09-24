import { Avatar } from "./Avatar";

/**
 * @file 小尺寸头像组件
 * @author Joker.X
 */
@ComponentV2
export struct SmallAvatar {
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
   * 构建小尺寸头像
   * @returns {void} 无返回值
   */
  build(): void {
    Avatar({
      src: this.src,
      avatarSize: 36,
      onTap: this.onTap
    });
  }
}
