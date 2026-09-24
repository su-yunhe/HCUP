import { P80, SpaceVerticalMedium } from "designsystem";
import { Cart, CartGoodsSpec } from "model";
import { IBestCell, IBestCellGroup } from "ibestui";
import { Card } from "../card/Card";
import { OrderGoodsItem } from "./OrderGoodsItem";

/**
 * @file 订单商品卡片组件
 * @author Joker.X
 */
@ComponentV2
export struct OrderGoodsCard {
  /**
   * 购物车数据
   */
  @Param
  data: Cart = new Cart();
  /**
   * 正在删除的规格ID集合
   */
  @Param
  deletingSpecIds: Set<number> = new Set();
  /**
   * 商品点击回调
   */
  @Param
  onGoodsClick: (goodsId: number) => void = () => {
  };
  /**
   * 规格点击回调
   */
  @Param
  onSpecClick: (specId: number) => void = () => {
  };
  /**
   * 数量变更回调
   * @param specId 规格ID
   * @param count 新数量
   */
  @Param
  onQuantityChanged: (specId: number, count: number) => void = () => {
  };
  /**
   * 是否启用数量调节器
   */
  @Param
  enableQuantityStepper: boolean = true;
  /**
   * 商品选择框插槽生成器
   */
  @BuilderParam
  itemSelectSlotBuilder?: (spec: CartGoodsSpec) => void;
  /**
   * 商品操作区域插槽生成器
   */
  @BuilderParam
  itemActionSlotBuilder?: (spec: CartGoodsSpec) => void;

  /**
   * 构建订单商品卡片
   * @returns {void} 无返回值
   */
  build(): void {
    Card() {
      // 商品标题
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        IBestCell({
          title: this.data.goodsName,
          isLink: true,
          hasBorder: true,
          leftContentWidth: P80,
          onCellClick: (): void => {
            this.onGoodsClick(this.data.goodsId);
          }
        });
      }

      SpaceVerticalMedium();

      // 商品规格项列表
      ForEach(this.data.spec, (item: CartGoodsSpec) => {
        // 过滤正在删除的规格
        if (!this.deletingSpecIds.has(item.id)) {
          OrderGoodsItem({
            data: item,
            goodsId: this.data.goodsId,
            goodsName: this.data.goodsName,
            goodsMainPic: this.data.goodsMainPic,
            onSpecClick: this.onSpecClick,
            onQuantityChanged: (count: number): void => {
              this.onQuantityChanged(item.id, count);
            },
            enableQuantityStepper: this.enableQuantityStepper,
            selectSlot: this.itemSelectSlotBuilder ? (): void => {
              if (this.itemSelectSlotBuilder) {
                this.itemSelectSlotBuilder(item);
              }
            } : undefined,
            actionSlot: this.itemActionSlotBuilder ? (): void => {
              if (this.itemActionSlotBuilder) {
                this.itemActionSlotBuilder(item);
              }
            } : undefined
          });
        }
      }, (item: CartGoodsSpec): string => `${item.id}`);
    }
  }
}
