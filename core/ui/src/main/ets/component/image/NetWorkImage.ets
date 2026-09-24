import { P100 } from "designsystem";

/**
 * @file 网络图片组件（仅设置背景色与圆角）
 * @author Joker.X
 */
@ComponentV2
export struct NetWorkImage {
  /**
   * 图片资源（URL / Resource / PixelMap）
   */
  @Param
  model: string | Resource | PixelMap | null = null;
  /**
   * 图片大小（宽高相等）
   */
  @Param
  sizeValue: Length | undefined = undefined;
  /**
   * 图片宽度
   */
  @Param
  widthValue: Length | undefined = undefined;
  /**
   * 图片高度
   */
  @Param
  heightValue: Length | undefined = undefined;
  /**
   * 图片缩放模式
   */
  @Param
  imageFit: ImageFit = ImageFit.Cover;
  /**
   * 是否显示背景色
   */
  @Param
  showBackground: boolean = false;
  /**
   * 背景颜色
   */
  @Param
  backgroundColorValue: ResourceColor = $r("app.color.bg_content");
  /**
   * 圆角大小
   */
  @Param
  cornerRadius: Length | undefined = undefined;

  /**
   * 构建网络图片组件
   * @returns {void} 无返回值
   */
  build(): void {
    Stack() {
      if (this.showBackground) {
        Column()
          .width(P100)
          .height(P100)
          .backgroundColor(this.backgroundColorValue)
          .borderRadius(this.cornerRadius ?? 0);
      }

      if (this.model) {
        if (
          (this.widthValue ?? this.sizeValue) !== undefined &&
          (this.heightValue ?? this.sizeValue) !== undefined
        ) {
          Image(this.model)
            .objectFit(this.imageFit)
            .borderRadius(this.cornerRadius ?? 0)
            .width(P100)
            .height(P100);
        } else if ((this.widthValue ?? this.sizeValue) !== undefined) {
          Image(this.model)
            .objectFit(this.imageFit)
            .borderRadius(this.cornerRadius ?? 0)
            .width(P100);
        } else if ((this.heightValue ?? this.sizeValue) !== undefined) {
          Image(this.model)
            .objectFit(this.imageFit)
            .borderRadius(this.cornerRadius ?? 0)
            .height(P100);
        } else {
          Image(this.model)
            .objectFit(this.imageFit)
            .borderRadius(this.cornerRadius ?? 0);
        }
      }
    }
    .width(this.widthValue ?? this.sizeValue)
    .height(this.heightValue ?? this.sizeValue)
    .borderRadius(this.cornerRadius ?? 0);
  }
}
