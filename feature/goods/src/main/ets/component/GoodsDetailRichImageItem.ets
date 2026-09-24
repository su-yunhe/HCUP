import { ColumnStart, P100, SpaceVerticalSmall } from "designsystem";
import { NetWorkImage } from "ui";

/**
 * @file 商品详情图片项组件
 * @author Joker.X
 */
@ComponentV2
export struct GoodsDetailRichImageItem {
  /**
   * 商品详情图片项
   */
  @Param
  pic: string = "";
  /**
   * 是否最后一张图片
   */
  @Param
  isLast: boolean = false;

  /**
   * 构建商品详情图片项
   * @returns {void} 无返回值
   */
  build(): void {
    ColumnStart({
      widthValue: P100,
      paddingValue: {
        left: $r("app.float.space_horizontal_medium"),
        right: $r("app.float.space_horizontal_medium")
      }
    }) {
      NetWorkImage({
        model: this.pic,
        widthValue: P100,
        imageFit: ImageFit.Contain,
        cornerRadius: this.isLast ? $r("app.float.radius_medium") : 0
      });

      if (this.isLast) {
        SpaceVerticalSmall();
      }
    }
  }
}
