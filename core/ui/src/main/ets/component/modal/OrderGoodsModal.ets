import {
  ColumnStart,
  P100,
  RowStartCenter,
  SpaceHorizontalMedium,
  SpaceVerticalMedium
} from "designsystem";
import { Cart } from "model";
import { IBestButton } from "ibestui";
import { BottomModal } from "./BottomModal";
import { Card } from "../card/Card";
import { NetWorkImage } from "../image/NetWorkImage";

/**
 * @file 订单商品选择弹窗组件
 * @author Joker.X
 */
@ComponentV2
export struct OrderGoodsModal {
  /**
   * 是否显示弹窗
   */
  @Param
  @Require
  visible: boolean = false;
  /**
   * 弹窗标题
   */
  @Param
  title: ResourceStr = "";
  /**
   * 操作按钮文案
   */
  @Param
  buttonText: ResourceStr = "";
  /**
   * 商品列表
   */
  @Param
  cartList: Cart[] = [];
  /**
   * 关闭回调
   */
  @Param
  onDismiss: () => void = () => {
  };
  /**
   * 商品操作按钮点击回调
   * @param {number} goodsId - 商品 ID
   */
  @Param
  onItemButtonClick: (goodsId: number) => void = () => {
  };

  /**
   * 构建订单商品选择弹窗
   * @returns {void} 无返回值
   */
  build(): void {
    BottomModal({
      visible: this.visible,
      title: this.title,
      onDismiss: this.onDismiss,
      containerColor: $r("app.color.bg_grey"),
      content: (): void => this.ModalContent()
    });
  }

  /**
   * 弹窗内容
   * @returns {void} 无返回值
   */
  @Builder
  private ModalContent(): void {
    ColumnStart({ widthValue: P100 }) {
      Scroll() {
        ColumnStart({ widthValue: P100 }) {
          ForEach(this.cartList, (cart: Cart, index: number): void => {
            this.OrderGoodsItem(cart);
            if (index !== this.cartList.length - 1) {
              SpaceVerticalMedium();
            }
          }, (cart: Cart, index: number): string => `${cart.goodsId}-${index}`);
        }
      }
      .width(P100)
      .constraintSize({ maxHeight: 500 })
      .scrollBar(BarState.Off);
    }
  }

  /**
   * 订单商品条目
   * @param {Cart} cart - 购物车商品数据
   * @returns {void} 无返回值
   */
  @Builder
  private OrderGoodsItem(cart: Cart): void {
    Card({ paddingValue: $r("app.float.space_padding_medium") }) {
      RowStartCenter({ widthValue: P100 }) {
        NetWorkImage({
          model: cart.goodsMainPic,
          sizeValue: 60,
          showBackground: true,
          cornerRadius: $r("app.float.radius_small")
        });

        SpaceHorizontalMedium();

        Text(cart.goodsName)
          .fontSize($r("app.float.body_large"))
          .fontColor($r("app.color.text_primary"))
          .layoutWeight(1);

        SpaceHorizontalMedium();

        IBestButton({
          text: this.buttonText,
          type: "primary",
          round: true,
          btnHeight: 32,
          onBtnClick: (): void => this.onItemButtonClick(cart.goodsId)
        });
      }
    }
  }
}
