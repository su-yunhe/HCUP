import { BaseNetWorkUiState } from "base";
import {
  ColumnStart,
  P100,
  SpaceVerticalMedium
} from "designsystem";
import { Cart, DictItem, Order } from "model";
import { getWindowSafeAreaState, WindowSafeAreaState } from "state";
import {
  AppBottomButton,
  AppNavDestination,
  BaseNetWorkView,
  Card,
  DictSelectModal,
  OrderGoodsCard,
  TitleWithLine
} from "ui";
import { IBestCell, IBestCellGroup, IBestPrice } from "ibestui";
import OrderRefundViewModel from "../viewmodel/OrderRefundViewModel";

/**
 * @file 订单退款页面视图
 * @author Joker.X
 */
@ComponentV2
export struct OrderRefundPage {
  /**
   * 订单退款页面 ViewModel
   */
  @Local
  private vm: OrderRefundViewModel = new OrderRefundViewModel();
  /**
   * 当前窗口安全区状态
   */
  @Local
  private windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();

  /**
   * 构建订单退款页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: $r("app.string.order_refund"),
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
  private PageContent(): void {
    ColumnStart({ fillMaxSize: true }) {
      BaseNetWorkView({
        uiState: this.vm.uiState,
        onRetry: (): void => this.vm.retryRequest(),
        content: (): void => this.OrderRefundContent()
      })
        .layoutWeight(1);

      if (this.vm.uiState === BaseNetWorkUiState.SUCCESS) {
        AppBottomButton({
          text: $r("app.string.submit"),
          onTap: (): void => this.vm.submitRefundApplication()
        });
      }
    }

    DictSelectModal({
      visible: this.vm.refundModalVisible,
      title: $r("app.string.select_cancel_reason"),
      uiState: this.vm.refundReasonsUiState,
      dictList: this.vm.refundReasonList,
      selectedItem: this.vm.selectedRefundReason,
      onDismiss: (): void => this.vm.hideRefundModal(),
      onItemSelected: (item: DictItem): void => this.vm.selectRefundReason(item),
      onConfirm: (item: DictItem | null): void => this.vm.selectRefundReason(item),
      onRetry: (): void => this.vm.loadRefundReasons()
    });
  }

  /**
   * 订单退款页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private OrderRefundContent(): void {
    Scroll() {
      Column() {
        this.RefundInfoCard(this.getOrderData());

        SpaceVerticalMedium();

        ForEach(this.vm.cartList, (cart: Cart): void => {
          OrderGoodsCard({
            data: cart,
            enableQuantityStepper: false
          });
          SpaceVerticalMedium();
        }, (cart: Cart): string => `${cart.goodsId}`);
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
   * 退款信息卡片
   * @param {Order} order - 订单数据
   * @returns {void} 无返回值
   */
  @Builder
  private RefundInfoCard(order: Order): void {
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
          title: $r("app.string.refund_reason"),
          value: this.getRefundReasonText(),
          hasBorder: true,
          isLink: true,
          onCellClick: (): void => this.vm.showRefundModal()
        });

        IBestCell({
          title: $r("app.string.refund_amount"),
          hasBorder: false,
          valueBuilder: (): void => this.PriceValue(order.realPrice)
        });
      }
    }
  }

  /**
   * 退款信息标题
   * @returns {void} 无返回值
   */
  @Builder
  private RefundInfoTitle(): void {
    TitleWithLine({
      text: $r("app.string.refund_info")
    });
  }

  /**
   * 退款金额值
   * @param {number} price - 金额
   * @returns {void} 无返回值
   */
  @Builder
  private PriceValue(price: number): void {
    IBestPrice({
      value: price,
      integerFontSize: 14,
      decimalFontSize: 12,
      symbolFontSize: 12
    });
  }

  /**
   * 获取退款原因文本
   * @returns {string | Resource} 退款原因文本
   */
  private getRefundReasonText(): string | Resource {
    return this.vm.selectedRefundReason?.name ?? $r("app.string.please_select");
  }

  /**
   * 获取订单数据
   * @returns {Order} 订单数据
   */
  private getOrderData(): Order {
    return this.vm.data ?? new Order();
  }
}
