import { IBestAvatar } from "@ibestservices/ibest-ui-v2";

/**
 * @file 头像组件（基于 IBestAvatar 封装）
 * @author Joker.X
 */
@ComponentV2
export struct Avatar {
  /**
   * 头像地址
   */
  @Param
  src: ResourceStr | PixelMap | DrawableDescriptor = "";
  /**
   * 头像大小（单位：vp）
   */
  @Param
  avatarSize: number = 40;
  /**
   * 点击回调
   */
  @Param
  onTap: (() => void) | undefined = undefined;

  /**
   * 构建头像组件
   * @returns {void} 无返回值
   */
  build(): void {
    IBestAvatar({
      src: this.src,
      shape: "circle",
      avatarSize: this.avatarSize,
      onAvatarClick: (): void => this.handleAvatarTap()
    });
  }

  /**
   * 处理头像点击
   * @returns {void} 无返回值
   */
  private handleAvatarTap(): void {
    if (this.onTap) {
      this.onTap();
    }
  }
}
