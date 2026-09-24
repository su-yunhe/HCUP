import { IBestCell, IBestCellGroup, IBestCheckbox, IBestPrice } from "ibestui";
import {
  ColumnCenter,
  ColumnStart,
  P100,
  SpaceVerticalMedium,
  SpaceVerticalSmall,
  SpaceVerticalXXLarge
} from "designsystem";
import { getWindowSafeAreaState, WindowSafeAreaState } from "state";
import { AppBottomButton, AppNavDestination } from "ui";
import OrderPayViewModel from "../viewmodel/OrderPayViewModel";

/**
 * @file 订单支付页面视图
 * @author Joker.X
 */
@ComponentV2
export struct OrderPayPage {
  /**
   * 订单支付页面 ViewModel
   */
  @Local
  private vm: OrderPayViewModel = new OrderPayViewModel();
  /**
   * 当前窗口安全区状态
   */
  @Param
  private windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();

  /**
   * 构建订单支付页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: $r("app.string.order_pay"),
      viewModel: this.vm,
      paddingValue: {
        top: this.windowSafeAreaState.topInset,
        left: this.windowSafeAreaState.leftInset,
        right: this.windowSafeAreaState.rightInset
      }
    }) {
      this.OrderPayContent();
    }
  }

  /**
   * 订单支付页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private OrderPayContent() {
    ColumnStart({ fillMaxSize: true }) {
      Scroll() {
        ColumnStart({
          fillMaxSize: true,
          paddingValue: {
            left: $r("app.float.space_horizontal_medium"),
            right: $r("app.float.space_horizontal_medium"),
            top: $r("app.float.space_vertical_small"),
            bottom: $r("app.float.space_vertical_medium")
          }
        }) {
          SpaceVerticalXXLarge();
          this.PriceSection();
          SpaceVerticalXXLarge();
          this.PayMethodCard();
          SpaceVerticalSmall();
          this.PayTipText();
          SpaceVerticalMedium();
        }
      }
      .layoutWeight(1)
      .scrollBar(BarState.Off);

      AppBottomButton({
        text: $r("app.string.order_pay_button"),
        onTap: (): void => {
          this.vm.onPayClick();
        }
      });
    }
  }

  /**
   * 支付金额展示区域
   * @returns {void} 无返回值
   */
  @Builder
  private PriceSection(): void {
    ColumnCenter({ widthValue: P100 }) {
      IBestPrice({
        value: this.vm.payPrice,
        symbolFontSize: 22,
        integerFontSize: 42,
        decimalPointFontSize: 22,
        decimalFontSize: 22
      });
    }
  }

  /**
   * 支付方式卡片
   * @returns {void} 无返回值
   */
  @Builder
  private PayMethodCard(): void {
    IBestCellGroup({
      inset: true,
      radius: $r("app.float.radius_medium"),
      outerMargin: 0
    }) {
      IBestCell({
        title: $r("app.string.pay_method_alipay"),
        center: true,
        hasBorder: true,
        iconBuilder: (): void => this.PayMethodIcon($r("app.media.ic_alipay")),
        rightIconBuilder: (): void => this.PayMethodCheckbox(true)
      });

      IBestCell({
        title: $r("app.string.pay_method_wechat"),
        center: true,
        hasBorder: true,
        iconBuilder: (): void => this.PayMethodIcon($r("app.media.ic_wechat")),
        rightIconBuilder: (): void => this.PayMethodCheckbox(false)
      });

      IBestCell({
        title: $r("app.string.pay_method_qq"),
        center: true,
        hasBorder: false,
        iconBuilder: (): void => this.PayMethodIcon($r("app.media.ic_qq")),
        rightIconBuilder: (): void => this.PayMethodCheckbox(false)
      });
    }
  }

  /**
   * 支付方式左侧图标插槽
   * @param {ResourceStr} iconRes - 图标资源
   * @returns {void} 无返回值
   */
  @Builder
  private PayMethodIcon(iconRes: ResourceStr): void {
    Image(iconRes)
      .width(24)
      .height(24);
  }

  /**
   * 支付方式右侧勾选插槽
   * @param {boolean} checked - 是否选中
   * @returns {void} 无返回值
   */
  @Builder
  private PayMethodCheckbox(checked: boolean): void {
    IBestCheckbox({
      value: checked,
      disabled: true
    });
  }

  /**
   * 支付提示文案
   * @returns {void} 无返回值
   */
  @Builder
  private PayTipText(): void {
    Text($r("app.string.order_pay_tip"))
      .fontSize($r("app.float.body_medium"))
      .fontColor($r("app.color.text_tertiary"));
  }
}
