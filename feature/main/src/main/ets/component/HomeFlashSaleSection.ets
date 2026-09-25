import { ColumnStart, P100, SpaceVerticalSmall } from "designsystem";
import { Goods } from "model";
import { Card, CardTitleCell } from "ui";
import { FlashSaleItem } from "./FlashSaleItem";

/**
 * @file 首页限时精选卡片组件
 * @author Joker.X
 */
@ComponentV2
export struct HomeFlashSaleSection {
  /**
   * 商品列表
   */
  @Param
  goodsList: Goods[] = [];
  /**
   * 商品点击回调
   */
  @Param
  onGoodsClick: (id: number) => void = () => {
  };
  /**
   * 查看全部回调
   */
  @Param
  onMoreClick: () => void = () => {
  };

  /**
   * 构建限时精选卡片
   * @returns {void} 无返回值
   */
  build(): void {
    if (this.goodsList && this.goodsList.length > 0) {
      Card() {
        CardTitleCell({
          leftIcon: $r("app.media.ic_time"),
          title: $r("app.string.flash_sale"),
          value: $r("app.string.view_all"),
          onTap: (): void => this.onMoreClick()
        });

        List({ space: 8 }) {
          ForEach(this.goodsList, (goods: Goods): void => {
            ListItem() {
              FlashSaleItem({
                goods: goods,
                onItemClick: this.onGoodsClick
              });
            }
          }, (goods: Goods): string => `${goods.id}-${goods.title}`);

        }
        .listDirection(Axis.Horizontal)
        .width(P100)
        .scrollBar(BarState.Off);
      }
    }
  }
}
