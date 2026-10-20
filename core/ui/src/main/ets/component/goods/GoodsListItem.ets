import {
  SpaceHorizontalSmall,
  SpaceVerticalXSmall,
  P100,
  RowSpaceBetweenCenter,
  columnSpaceBetweenStart,
  ColumnStart
} from "designsystem";
import { IBestPrice } from "ibestui";
import { Goods } from "model";
import { NetWorkImage } from "../image/NetWorkImage";
import { Card } from "../../../../../Index";

/**
 * @file 商品列表卡片组件
 * @author Joker.X
 */
@ComponentV2
export struct GoodsListItem {
  @Param
  idPrefix: string = "";
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
   * 构建商品列表卡片
   * @returns {void} 无返回值
   */
  build(): void {
    Column() {
    Card({
      onTap: (): void => this.onItemClick(this.goods.id)
    }) {
      Row() {
        Stack() {
        NetWorkImage({
          model: this.goods.mainPic,
          sizeValue: 100,
          imageFit: ImageFit.Cover,
          showBackground: true,
          cornerRadius: $r("app.float.radius_small")
        });
        }.id(this.idPrefix.length > 0 ? `${this.idPrefix}.image.${this.goods.id}` : "");

        SpaceHorizontalSmall();

        Column() {
          ColumnStart() {
            Text(this.goods.title)
              .id(this.idPrefix.length > 0 ? `${this.idPrefix}.name.${this.goods.id}` : "")
              .fontSize($r("app.float.body_large"))
              .fontColor($r("app.color.text_primary"))
              .maxLines(2)
              .textOverflow({ overflow: TextOverflow.Ellipsis });

            if (this.goods.subTitle && this.goods.subTitle.length > 0) {
              SpaceVerticalXSmall();
              Text(this.goods.subTitle)
                .fontSize($r("app.float.body_medium"))
                .fontColor($r("app.color.text_tertiary"))
                .maxLines(1)
                .textOverflow({ overflow: TextOverflow.Ellipsis });
            }
          }

          RowSpaceBetweenCenter({ widthValue: P100 }) {
            Row() {
              IBestPrice({ value: this.goods.price });
            }.id(this.idPrefix.length > 0 ? `${this.idPrefix}.price.${this.goods.id}` : "");

            Text($r("app.string.goods_sold", this.goods.sold))
              .id(this.idPrefix.length > 0 ? `${this.idPrefix}.sold.${this.goods.id}` : "")
              .fontSize($r("app.float.body_medium"))
              .fontColor($r("app.color.text_tertiary"));
          };
        }
        .height(100)
        .width(P100)
        .layoutWeight(1)
        .padding({
          top: $r("app.float.space_padding_small"),
          bottom: $r("app.float.space_padding_small")
        })
        .attributeModifier(columnSpaceBetweenStart())
      }
      .width(P100)
      .padding($r("app.float.space_padding_small"));
    }
    }.id(this.idPrefix.length > 0 ? `${this.idPrefix}.goods.${this.goods.id}` : "").width(P100);
  }
}
