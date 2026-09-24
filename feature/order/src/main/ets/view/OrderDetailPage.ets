import { BaseNetWorkUiState } from "base";
import {
  ColumnStart,
  P100,
  RowEndCenter,
  RowStartCenter,
  SpaceHorizontalSmall,
  SpaceHorizontalXSmall,
  SpaceVerticalMedium
} from "designsystem";
import { Cart, DictItem, Order } from "model";
import { OrderNavigator } from "navigation";
import { getWindowSafeAreaState, WindowSafeAreaState } from "state";
import {
  AddressCard,
  AppNavDestination,
  BaseNetWorkView,
  Card,
  DictSelectModal,
  OrderGoodsModal,
  OrderGoodsCard,
  TitleWithLine
} from "ui";
import { IBestCell, IBestCellGroup, IBestDialog, IBestPrice } from "ibestui";
import { OrderButtons } from "../component/OrderButtons";
import OrderDetailViewModel from "../viewmodel/OrderDetailViewModel";

/**
 * @file 订单详情页面视图
 * @author Joker.X
 */
@ComponentV2
export struct OrderDetailPage {
  /**
   * 订单详情页面 ViewModel
   */
  @Local
  private vm: OrderDetailViewModel = new OrderDetailViewModel();
  /**
   * 当前窗口安全区状态
   */
  @Local
  private windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();

  /**
   * 构建订单详情页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: this.getPageTitle(),
      viewModel: this.vm,
      paddingValue: {
        top: this.windowSafeAreaState.topInset,
        left: this.windowSafeAreaState.leftInset,
        right: this.windowSafeAreaState.rightInset
      }
    }) {
      this.PageContent();
    }
  }

  /**
   * 页面内容
   * @returns {void} 无返回值
   */
  @Builder
  private PageContent() {
    ColumnStart({ fillMaxSize: true }) {
      BaseNetWorkView({
        uiState: this.vm.uiState,
        onRetry: (): void => this.vm.retryRequest(),
        content: (): void => this.OrderDetailContent()
      })
        .layoutWeight(1);

      if (this.vm.uiState === BaseNetWorkUiState.SUCCESS) {
        this.BottomBar();
      }
    }

    // 取消订单弹窗
    DictSelectModal({
      visible: this.vm.cancelModalVisible,
      title: $r("app.string.select_cancel_reason"),
      uiState: this.vm.cancelReasonsUiState,
      dictList: this.vm.cancelReasonList,
      selectedItem: this.vm.selectedCancelReason,
      onDismiss: (): void => this.vm.hideCancelModal(),
      onItemSelected: (item: DictItem): void => this.vm.selectCancelReason(item),
      onConfirm: (): void => this.vm.confirmCancelOrder(),
      onRetry: (): void => this.vm.loadCancelReasons()
    });

    IBestDialog({
      visible: this.vm.showConfirmDialog,
      title: $r("app.string.confirm_receipt"),
      message: $r("app.string.confirm_receipt_message"),
      showCancelButton: true,
      confirmButtonText: $r("app.string.confirm"),
      cancelButtonText: $r("app.string.cancel"),
      onConfirm: (): void => this.vm.confirmReceiveOrder(),
      onCancel: (): void => this.vm.hideConfirmReceiveDialog(),
      onClose: (): void => this.vm.hideConfirmReceiveDialog()
    });

    OrderGoodsModal({
      visible: this.vm.rebuyModalVisible,
      title: $r("app.string.select_goods_to_buy"),
      buttonText: $r("app.string.rebuy"),
      cartList: this.vm.cartList,
      onDismiss: (): void => this.vm.hideRebuyModal(),
      onItemButtonClick: (goodsId: number): void => this.vm.toGoodsDetail(goodsId)
    });

    OrderGoodsModal({
      visible: this.vm.commentModalVisible,
      title: $r("app.string.select_goods_to_comment"),
      buttonText: $r("app.string.go_to_comment"),
      cartList: this.vm.cartList,
      onDismiss: (): void => this.vm.hideCommentModal(),
      onItemButtonClick: (goodsId: number): void => this.vm.toOrderCommentForGoods(goodsId)
    });
  }

  /**
   * 订单详情页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private OrderDetailContent() {
    Scroll() {
      Column() {
        AddressCard({
          address: this.getOrderData().address ?? null,
          onTap: (): void => {
          }
        });

        SpaceVerticalMedium();

        ForEach(this.vm.cartList, (cart: Cart): void => {
          OrderGoodsCard({
            data: cart,
            enableQuantityStepper: false
          });
          SpaceVerticalMedium();
        }, (cart: Cart): string => `${cart.goodsId}`);

        this.PriceDetailCard(this.getOrderData());

        if (this.shouldShowRefundInfo(this.getOrderData())) {
          SpaceVerticalMedium();
          this.RefundInfoCard(this.getOrderData());
        }

        SpaceVerticalMedium();

        this.OrderInfoCard(this.getOrderData());

        SpaceVerticalMedium();
      }
      .padding({
        left: $r("app.float.space_horizontal_medium"),
        right: $r("app.float.space_horizontal_medium"),
        top: $r("app.float.space_vertical_medium"),
        bottom: $r("app.float.space_vertical_medium")
      });
    }
    .scrollBar(BarState.Off);
  }

  /**
   * 价格明细卡片
   * @returns {void} 无返回值
   */
  @Builder
  private PriceDetailCard(order: Order) {
    Card() {
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        IBestCell({
          hasBorder: true,
          titleBuilder: (): void => this.PriceDetailTitle()
        });

        IBestCell({
          title: $r("app.string.goods_total_price"),
          leftIcon: $r("app.media.ic_shop"),
          hasBorder: true,
          valueBuilder: (): void => this.PriceValue(order.price)
        });

        IBestCell({
          title: $r("app.string.discount_amount"),
          leftIcon: $r("app.media.ic_coupon"),
          hasBorder: true,
          valueBuilder: (): void => this.DiscountPriceValue(order.discountPrice)
        });

        IBestCell({
          title: $r("app.string.actual_payment"),
          leftIcon: $r("app.media.ic_money"),
          hasBorder: false,
          valueBuilder: (): void => this.PriceValue(this.getActualPayment(order))
        });
      }
    }
  }

  /**
   * 价格明细标题
   * @returns {void} 无返回值
   */
  @Builder
  private PriceDetailTitle() {
    TitleWithLine({
      text: $r("app.string.price_detail")
    });
  }

  /**
   * 退款信息卡片
   * @returns {void} 无返回值
   */
  @Builder
  private RefundInfoCard(order: Order) {
    Card() {
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        IBestCell({
          hasBorder: true,
          titleBuilder: (): void => this.RefundInfoTitle()
        });

        IBestCell({
          title: $r("app.string.refund_amount"),
          hasBorder: true,
          valueBuilder: (): void => this.PriceValue(this.getRefundAmount(order))
        });

        IBestCell({
          title: $r("app.string.refund_status"),
          hasBorder: true,
          value: this.getRefundStatusText(order)
        });

        IBestCell({
          title: $r("app.string.refund_reason"),
          hasBorder: true,
          value: order.refund?.reason ?? $r("app.string.none")
        });

        IBestCell({
          title: $r("app.string.refund_apply_time"),
          hasBorder: false,
          value: order.refundApplyTime ?? $r("app.string.none")
        });
      }
    }
  }

  /**
   * 退款信息标题
   * @returns {void} 无返回值
   */
  @Builder
  private RefundInfoTitle() {
    TitleWithLine({
      text: $r("app.string.refund_info")
    });
  }

  /**
   * 订单信息卡片
   * @returns {void} 无返回值
   */
  @Builder
  private OrderInfoCard(order: Order) {
    Card() {
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        IBestCell({
          hasBorder: true,
          titleBuilder: (): void => this.OrderInfoTitle()
        });

        IBestCell({
          title: $r("app.string.order_number"),
          hasBorder: true,
          leftContentWidth: 100,
          valueBuilder: (): void => this.OrderNumberValue(order)
        });

        IBestCell({
          title: $r("app.string.payment_method"),
          hasBorder: true,
          value: this.getPaymentMethodText(order)
        });

        IBestCell({
          title: $r("app.string.payment_time"),
          hasBorder: true,
          value: order.payTime ?? $r("app.string.unpaid")
        });

        IBestCell({
          title: $r("app.string.order_time"),
          hasBorder: true,
          value: order.createTime ?? $r("app.string.none")
        });

        IBestCell({
          title: $r("app.string.order_remark"),
          hasBorder: false,
          value: order.remark ?? $r("app.string.none")
        });
      }
    }
  }

  /**
   * 订单信息标题
   * @returns {void} 无返回值
   */
  @Builder
  private OrderInfoTitle() {
    TitleWithLine({
      text: $r("app.string.order_info")
    });
  }

  /**
   * 订单号展示区域
   * @returns {void} 无返回值
   */
  @Builder
  private OrderNumberValue(order: Order) {
    RowStartCenter() {
      Text(order.orderNum)
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.text_secondary"));

      SpaceHorizontalSmall();

      Text($r("app.string.copy"))
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.primary"));

      SpaceHorizontalXSmall();
    }
  }

  /**
   * 底部操作栏
   * @returns {void} 无返回值
   */
  @Builder
  private BottomBar() {
    Column() {
      RowEndCenter({
        widthValue: P100,
        paddingValue: {
          left: $r("app.float.space_horizontal_medium"),
          right: $r("app.float.space_horizontal_medium"),
          top: $r("app.float.space_vertical_medium"),
          bottom: this.windowSafeAreaState.bottomInset > 0
            ? 0
            : $r("app.float.space_vertical_medium")
        }
      }) {
        OrderButtons({
          order: this.getOrderData(),
          onCancelClick: (): void => this.vm.showCancelModal(),
          onPayClick: (): void => this.vm.toPay(),
          onRefundClick: (): void => OrderNavigator.toRefund(this.getOrderId()),
          onConfirmClick: (): void => this.vm.showConfirmReceiveDialog(),
          onLogisticsClick: (): void => OrderNavigator.toLogistics(this.getOrderId()),
          onCommentClick: (): void => this.vm.handleOrderComment(),
          onRebuyClick: (): void => this.vm.handleRebuy()
        });
      }

      if (this.windowSafeAreaState.bottomInset > 0) {
        Blank().height(this.windowSafeAreaState.bottomInset);
      }
    }
    .width(P100)
    .backgroundColor($r("app.color.bg_white"))
    .border({
      width: { top: 1 },
      color: $r("app.color.border")
    });
  }

  /**
   * 构建价格值
   * @param {number} price - 价格（单位：分）
   * @returns {void} 无返回值
   */
  @Builder
  private PriceValue(price: number) {
    IBestPrice({
      value: price,
      integerFontSize: 14,
      decimalFontSize: 12,
      symbolFontSize: 12
    });
  }

  /**
   * 构建优惠金额值
   * @param {number} price - 优惠金额（单位：分）
   * @returns {void} 无返回值
   */
  @Builder
  private DiscountPriceValue(price: number) {
    IBestPrice({
      value: price,
      integerFontSize: 14,
      decimalFontSize: 12,
      symbolFontSize: 12,
      color: $r("app.color.danger")
    });
  }

  /**
   * 是否显示退款信息卡片
   * @returns {boolean} 是否显示
   */
  private shouldShowRefundInfo(order: Order): boolean {
    return order.refund !== null || order.refundStatus !== null;
  }

  /**
   * 获取实付金额
   * @returns {number} 实付金额
   */
  private getActualPayment(order: Order): number {
    return order.price - order.discountPrice;
  }

  /**
   * 获取退款金额
   * @returns {number} 退款金额
   */
  private getRefundAmount(order: Order): number {
    return order.refund?.amount ?? 0;
  }

  /**
   * 获取退款状态文案
   * @returns {ResourceStr} 退款状态文案
   */
  private getRefundStatusText(order: Order): ResourceStr {
    switch (order.refundStatus) {
      case 0:
        return $r("app.string.refund_status_applying");
      case 1:
        return $r("app.string.refund_status_refunded");
      case 2:
        return $r("app.string.refund_status_rejected");
      default:
        return $r("app.string.refund_status_unknown");
    }
  }

  /**
   * 获取支付方式文案
   * @returns {ResourceStr} 支付方式文案
   */
  private getPaymentMethodText(order: Order): ResourceStr {
    switch (order.payType) {
      case 1:
        return $r("app.string.pay_method_wechat");
      case 2:
        return $r("app.string.pay_method_alipay");
      default:
        return $r("app.string.unpaid");
    }
  }

  /**
   * 获取页面标题
   * @returns {ResourceStr} 标题文案
   */
  private getPageTitle(): ResourceStr {
    if (this.vm.uiState !== BaseNetWorkUiState.SUCCESS) {
      return $r("app.string.order_detail");
    }
    switch (this.getOrderData().status) {
      case 0:
        return $r("app.string.order_status_pending_payment");
      case 1:
        return $r("app.string.order_status_pending_shipment");
      case 2:
        return $r("app.string.order_status_pending_receipt");
      case 3:
        return $r("app.string.order_status_pending_comment");
      case 4:
        return $r("app.string.order_status_completed");
      case 5:
        return $r("app.string.order_status_refunding");
      case 6:
        return $r("app.string.order_status_refunded");
      case 7:
        return $r("app.string.order_status_closed");
      default:
        return $r("app.string.order_detail");
    }
  }

  /**
   * 获取订单数据（空时返回默认对象）
   * @returns {Order} 订单数据
   */
  private getOrderData(): Order {
    return this.vm.data ?? new Order();
  }

  /**
   * 获取订单 ID
   * @returns {number} 订单 ID
   */
  private getOrderId(): number {
    return this.getOrderData().id;
  }
}
