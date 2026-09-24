import {
  SpaceVerticalXSmall,
  P100,
  RowSpaceBetweenCenter,
  ColumnStart,
  ColumnCenter,
  ColumnSpaceBetween,
  ColumnSpaceBetweenStart,
  ColumnSpaceBetweenEnd
} from "designsystem";
import { IBestPrice } from "@ibestservices/ibest-ui-v2";
import { Goods } from "model";
import { NetWorkImage } from "../image/NetWorkImage";
import { Card } from "../../../../../Index";
import { bp } from "state";

/**
 * @file 商品网格卡片组件
 * @author Joker.X
 */
@ComponentV2
export struct GoodsGridItem {
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
   * 构建商品网格卡片
   * @returns {void} 无返回值
   */
  build(): void {
    Card({
      heightValue: bp({ sm: 230, md: 250, lg: 270 }),
      paddingValue: $r("app.float.space_padding_small"),
      onTap: (): void => this.onItemClick(this.goods.id)
    }) {
      ColumnSpaceBetween({ heightValue: P100 }) {
        NetWorkImage({
          model: this.goods.mainPic,
          sizeValue: bp({ sm: 120, md: 140, lg: 160 }),
          imageFit: ImageFit.Cover,
          showBackground: false,
          cornerRadius: $r("app.float.radius_small")
        });

        ColumnStart({ widthValue: P100 }) {
          Text(this.goods.title)
            .fontSize($r("app.float.body_large"))
            .fontColor($r("app.color.text_primary"))
            .maxLines(2)
            .textOverflow({ overflow: TextOverflow.Ellipsis });

          if (this.goods.subTitle && this.goods.subTitle.length > 0) {
            SpaceVerticalXSmall();
            Text(this.goods.subTitle)
              .fontSize($r("app.float.body_medium"))
              .fontColor($r("app.color.text_tertiary"))
              .maxLines(2)
              .textOverflow({ overflow: TextOverflow.Ellipsis });
          }
        }

        RowSpaceBetweenCenter({ widthValue: P100 }) {
          IBestPrice({ value: this.goods.price });

          Text($r("app.string.goods_sold", this.goods.sold))
            .fontSize($r("app.float.body_medium"))
            .fontColor($r("app.color.text_tertiary"));
        };
      }
    }
  }
}
