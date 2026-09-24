import {
  ColumnCenter, P100, P70, RowEndCenter, SpaceVerticalXSmall
} from "designsystem";
import { IBestCell, IBestCellGroup, IBestPrice } from "ibestui";
import { Order, OrderGoods } from "model";
import { Card, NetWorkImage } from "ui";
import { OrderButtons } from "./OrderButtons";

/**
 * @file 订单卡片组件
 * @author Joker.X
 */
@ComponentV2
export struct OrderCard {
  /**
   * 订单数据
   */
  @Param
  order: Order = new Order();
  /**
   * 跳转订单详情
   */
  @Param
  toOrderDetail: (orderId: number) => void = () => {
  };
  /**
   * 跳转商品详情
   */
  @Param
  toGoodsDetail: () => void = () => {
  };
  /**
   * 跳转支付
   */
  @Param
  toPay: () => void = () => {
  };
  /**
   * 跳转物流
   */
  @Param
  toLogistics: () => void = () => {
  };
  /**
   * 跳转评价
   */
  @Param
  toComment: () => void = () => {
  };
  /**
   * 跳转退款/售后
   */
  @Param
  toRefund: () => void = () => {
  };
  /**
   * 取消订单点击回调
   */
  @Param
  onCancelClick: () => void = () => {
  };
  /**
   * 确认收货点击回调
   */
  @Param
  onConfirmClick: () => void = () => {
  };

  /**
   * 构建订单卡片
   * @returns {void} 无返回值
   */
  build(): void {
    Card({
      onTap: (): void => this.toOrderDetail(this.order.id)
    }) {
      this.buildHeader();
      this.buildGoodsPreview();
      this.buildDivider();
      this.buildActionBar();
    }
  }

  /**
   * 构建订单头部
   * @returns {void} 无返回值
   */
  @Builder
  private buildHeader(): void {
    IBestCellGroup({
      inset: true,
      radius: $r("app.float.radius_medium"),
      outerMargin: 0
    }) {
      IBestCell({
        title: this.order.orderNum,
        value: this.getStatusText(this.order.status),
        isLink: false,
        hasBorder: true,
        leftContentWidth: P70,
        onCellClick: (): void => this.toOrderDetail(this.order.id)
      });
    }
  }

  /**
   * 构建订单商品预览
   * @returns {void} 无返回值
   */
  @Builder
  private buildGoodsPreview(): void {
    Stack({ alignContent: Alignment.Center }) {
      List({ space: 8 }) {
        ForEach(this.getGoodsList(), (goods: OrderGoods): void => {
          ListItem() {
            NetWorkImage({
              model: goods.spec?.images?.[0] ?? goods.goodsInfo?.mainPic ?? "",
              sizeValue: 80,
              showBackground: true,
              cornerRadius: $r("app.float.radius_small")
            });
          }
        }, (goods: OrderGoods): string => `${goods.id}`);
      }
      .width(P100)
      .listDirection(Axis.Horizontal)
      .scrollBar(BarState.Off)
      .padding({
        left: $r("app.float.space_horizontal_medium"),
        right: 80,
        top: $r("app.float.space_vertical_medium"),
        bottom: $r("app.float.space_vertical_medium")
      });

      RowEndCenter({
        widthValue: P100,
        paddingValue: { right: $r("app.float.space_horizontal_medium") }
      }) {
        ColumnCenter({ widthValue: 80 }) {
          this.buildPriceValue(this.order.price);
          SpaceVerticalXSmall();
          Text($r("app.string.total_items", this.getGoodsList().length))
            .fontSize($r("app.float.body_medium"))
            .fontColor($r("app.color.text_tertiary"));
        }
      }
    }
    .width(P100);
  }

  /**
   * 构建底部操作栏
   * @returns {void} 无返回值
   */
  @Builder
  private buildActionBar(): void {
    RowEndCenter({
      widthValue: P100,
      paddingValue: $r("app.float.space_padding_medium")
    }) {
      OrderButtons({
        order: this.order,
        onCancelClick: this.onCancelClick,
        onPayClick: this.toPay,
        onRefundClick: this.toRefund,
        onConfirmClick: this.onConfirmClick,
        onLogisticsClick: this.toLogistics,
        onCommentClick: this.toComment,
        onRebuyClick: this.toGoodsDetail
      });
    }
  }

  /**
   * 构建分割线
   * @returns {void} 无返回值
   */
  @Builder
  private buildDivider(): void {
    Column()
      .width(P100)
      .height($r("app.float.space_divider"))
      .backgroundColor($r("app.color.border"));
  }

  /**
   * 获取订单商品列表
   * @returns {OrderGoods[]} 商品列表
   */
  private getGoodsList(): OrderGoods[] {
    return this.order.goodsList ?? [];
  }

  /**
   * 获取订单状态文案
   * @param {number} status - 订单状态
   * @returns {ResourceStr} 状态文案
   */
  private getStatusText(status: number): ResourceStr {
    // 与安卓订单状态保持一致
    switch (status) {
      case 0:
        return $r("app.string.order_status_unpaid");
      case 1:
        return $r("app.string.order_status_unshipped");
      case 2:
        return $r("app.string.order_status_unreceived");
      case 3:
        return $r("app.string.order_status_unevaluated");
      case 4:
        return $r("app.string.order_status_completed");
      case 5:
        return $r("app.string.order_status_refunding");
      case 6:
        return $r("app.string.order_status_refunded");
      case 7:
        return $r("app.string.order_status_closed");
      default:
        return $r("app.string.order_status_unknown");
    }
  }

  /**
   * 构建价格文本
   * @param {number} price - 价格（单位：分）
   * @returns {void} 无返回值
   */
  @Builder
  private buildPriceValue(price: number): void {
    IBestPrice({
      value: price,
      integerFontSize: 14,
      decimalFontSize: 12,
      symbolFontSize: 12
    });
  }
}
