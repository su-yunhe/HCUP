import { BaseNetWorkUiState } from "base";
import {
  P100,
  RowSpaceBetweenCenter,
  RowStartCenter,
  SpaceHorizontalSmall,
  SpaceVerticalMedium
} from "designsystem";
import { Cart, Coupon } from "model";
import { GoodsNavigator } from "navigation";
import { getWindowSafeAreaState, WindowSafeAreaState } from "state";
import {
  AddressCard, AppNavDestination, BaseNetWorkView, BottomModal, Card, OrderGoodsCard, TitleWithLine
} from "ui";
import { IBestButton, IBestCell, IBestCellGroup, IBestField, IBestPrice } from "ibestui";
import OrderConfirmViewModel from "../viewmodel/OrderConfirmViewModel";

/**
 * @file 订单确认页面视图
 * @author Joker.X
 */
@ComponentV2
export struct OrderConfirmPage {
  /**
   * 订单确认页面 ViewModel
   */
  @Local
  private vm: OrderConfirmViewModel = new OrderConfirmViewModel();
  /**
   * 当前窗口安全区状态
   */
  @Local
  private windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();

  /**
   * 构建订单确认页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: $r("app.string.order_confirm"),
      viewModel: this.vm,
      paddingValue: {
        top: this.windowSafeAreaState.topInset,
        left: this.windowSafeAreaState.leftInset,
        right: this.windowSafeAreaState.rightInset
      }
    }) {
      this.PageContent();
      BottomModal({
        visible: this.vm.couponModalVisible,
        title: $r("app.string.coupon"),
        onDismiss: (): void => this.vm.hideCouponModal(),
        content: (): void => this.CouponContent()
      });
    }
  }

  /**
   * 页面内容
   * @returns {void} 无返回值
   */
  @Builder
  private PageContent() {
    BaseNetWorkView({
      uiState: this.vm.uiState,
      onRetry: (): void => this.vm.retryRequest(),
      content: (): void => this.OrderConfirmContent()
    });
  }

  /**
   * 订单确认页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private OrderConfirmContent() {
    Column() {
      // 可滚动内容区域
      Scroll() {
        Column() {
          // 地址选择卡片
          ForEach([JSON.stringify(this.vm.selectedAddress)], (addressKey: string): void => {
            AddressCard({
              address: this.vm.selectedAddress,
              addressSelected: true,
              onTap: (): void => this.vm.navigateToAddressSelection()
            }).id("order_confirm_address");
          }, (addressKey: string): string => addressKey);

          SpaceVerticalMedium();

          // 订单商品卡片
          ForEach(this.vm.cartList, (cart: Cart) => {
            OrderGoodsCard({
              data: cart,
              idPrefix: "order_confirm",
              enableQuantityStepper: false,
              onGoodsClick: (goodsId: number): void => {
                GoodsNavigator.toDetail(goodsId);
              }
            });
            SpaceVerticalMedium();
          }, (cart: Cart): string => `${cart.goodsId}`);

          if (this.vm.isEmpty) {
            Text($r("app.string.order_goods_empty"))
              .fontColor($r("app.color.text_subtitle"));
          }

          // 价格明细卡片
          this.PriceDetailCard();

          SpaceVerticalMedium();

          // 订单备注卡片
          this.RemarkCard();

          SpaceVerticalMedium();
        }
        .padding({
          left: $r("app.float.space_horizontal_medium"),
          right: $r("app.float.space_horizontal_medium"),
          top: $r("app.float.space_vertical_medium"),
          bottom: $r("app.float.space_vertical_medium")
        })
      }
      .layoutWeight(1)
      .scrollBar(BarState.Off)

      // 底部操作栏
      if (this.vm.uiState === BaseNetWorkUiState.SUCCESS) {
        this.BottomBar();
      }
    }
    .id("order_confirm_page")
    .width(P100)
    .height(P100)
    .alignItems(HorizontalAlign.Start)
  }

  /**
   * 价格明细卡片
   * @returns {void} 无返回值
   */
  @Builder
  private PriceDetailCard() {
    Card() {
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        // 标题
        IBestCell({
          hasBorder: true,
          titleBuilder: (): void => this.PriceDetailTitle()
        });

        // 商品总价
        IBestCell({
          title: $r("app.string.goods_total_price"),
          leftIcon: $r("app.media.ic_shop"),
          hasBorder: true,
          valueBuilder: (): void => this.PriceValue(this.vm.originalPrice)
        });

        // 优惠券
        IBestCell({
          title: $r("app.string.coupon"),
          leftIcon: $r("app.media.ic_coupon"),
          value: this.vm.selectedCoupon?.title ?? $r("app.string.coupon_select"),
          isLink: true,
          hasBorder: true,
          onCellClick: (): void => {
            this.vm.showCouponModal();
          }
        }).id("order_confirm_coupon");

        // 优惠券折扣（仅当有折扣时显示）
        if (this.vm.discountAmount > 0) {
          IBestCell({
            title: $r("app.string.coupon_discount"),
            leftIcon: $r("app.media.ic_refund"),
            hasBorder: true,
            valueBuilder: (): void => this.DiscountPriceValue(this.vm.discountAmount)
          });
        }

        // 合计
        IBestCell({
          title: $r("app.string.total"),
          leftIcon: $r("app.media.ic_money"),
          hasBorder: false,
          valueBuilder: (): void => this.PriceValue(this.vm.totalPrice)
        });
      }
    }
  }

  @Builder
  private CouponContent() {
    Scroll() {
      Column() {
        IBestCell({
          title: $r("app.string.order_coupon_none"),
          onCellClick: (): void => this.vm.selectCoupon(null)
        }).id("order_coupon_none");
        ForEach(this.vm.data?.userCoupon ?? [], (coupon: Coupon): void => {
          IBestCell({
            title: coupon.title,
            label: coupon.description,
            onCellClick: (): void => this.vm.selectCoupon(coupon)
          }).id(`order_coupon_item_${coupon.id}`);
        }, (coupon: Coupon): string => `${coupon.id}`);
        if (!this.vm.data?.userCoupon || this.vm.data.userCoupon.length === 0) {
          Text($r("app.string.order_coupon_empty"))
            .fontColor($r("app.color.text_subtitle"))
            .padding($r("app.float.space_padding_medium"));
        }
      }
      .width(P100)
    }
    .constraintSize({ maxHeight: 360 })
    .width(P100)
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
   * 价格值（使用 IBestPrice 组件）
   * @param {number} price 价格（单位：分）
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
   * 折扣价格值（负数显示）
   * @param {number} price 价格（单位：分）
   * @returns {void} 无返回值
   */
  @Builder
  private DiscountPriceValue(price: number) {
    IBestPrice({
      value: -price,
      integerFontSize: 14,
      decimalFontSize: 12,
      symbolFontSize: 12,
      color: $r("app.color.danger")
    });
  }

  /**
   * 订单备注卡片
   * @returns {void} 无返回值
   */
  @Builder
  private RemarkCard() {
    Card() {
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        // 标题
        IBestCell({
          hasBorder: true,
          titleBuilder: (): void => this.RemarkTitle()
        });

        // 备注输入框
        IBestField({
          showLabel: false,
          value: this.vm.remark!!,
          placeholder: $r("app.string.order_remark_placeholder"),
          rows: 3,
          maxlength: 200,
          showWordLimit: true,
          hasBorder: false,
          autosize: true
        }).id("order_confirm_remark_input");
      }
    }
  }

  /**
   * 订单备注标题
   * @returns {void} 无返回值
   */
  @Builder
  private RemarkTitle() {
    TitleWithLine({
      text: $r("app.string.order_remark_title")
    });
  }

  /**
   * 底部操作栏
   * @returns {void} 无返回值
   */
  @Builder
  private BottomBar() {
    Column() {
      RowSpaceBetweenCenter({
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
        // 左侧：合计 + 价格
        RowStartCenter() {
          Text($r("app.string.total"))
            .fontSize($r("app.float.body_large"))
            .fontColor($r("app.color.text_primary"));

          SpaceHorizontalSmall();

          IBestPrice({
            value: this.vm.totalPrice,
            integerFontSize: 20,
            decimalFontSize: 14,
            symbolFontSize: 14
          }).id("order_confirm_total");
        }

        // 右侧：提交订单按钮
        IBestButton({
          text: $r("app.string.submit_order"),
          type: "primary",
          round: true,
          loading: this.vm.submitting,
          loadingText: $r("app.string.submit_order"),
          disabled: !this.vm.canSubmit,
          btnWidth: 100,
          btnHeight: 36,
          onBtnClick: (): void => this.vm.onSubmitOrderClick()
        }).id("order_confirm_submit");
      }

      // 底部安全区
      if (this.windowSafeAreaState.bottomInset > 0) {
        Blank().height(this.windowSafeAreaState.bottomInset);
      }
    }
    .width(P100)
    .backgroundColor($r("app.color.bg_white"))
    .border({
      width: { top: 1 },
      color: $r("app.color.border")
    })
  }
}
