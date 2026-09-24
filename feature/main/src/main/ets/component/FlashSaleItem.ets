import { ColumnStart, SpaceVerticalSmall, SpaceVerticalXSmall } from "designsystem";
import { Goods } from "model";
import { IBestPrice, NetWorkImage } from "ui";

/**
 * @file 限时精选卡片项
 * @author Joker.X
 */
@ComponentV2
export struct FlashSaleItem {
  /**
   * 商品数据
   */
  @Param
  goods: Goods = new Goods();
  /**
   * 点击回调
   */
  @Param
  onItemClick: (id: number) => void = () => {
  };

  /**
   * 构建限时精选卡片项
   * @returns {void} 无返回值
   */
  build(): void {
    ColumnStart({
      widthValue: 120,
      paddingValue: {
        left: $r("app.float.space_horizontal_small"),
        right: $r("app.float.space_horizontal_small"),
      },
      onTap: (): void => this.onItemClick(this.goods.id)
    }) {
      NetWorkImage({
        model: this.goods.mainPic,
        sizeValue: 120,
        imageFit: ImageFit.Cover,
        cornerRadius: $r("app.float.radius_small"),
        showBackground: false
      });

      SpaceVerticalXSmall();

      Text(this.goods.title)
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.text_primary"))
        .maxLines(1)
        .textOverflow({ overflow: TextOverflow.Ellipsis });

      SpaceVerticalXSmall();
      IBestPrice({ value: this.goods.price });
      SpaceVerticalSmall();
    }
  }
}
