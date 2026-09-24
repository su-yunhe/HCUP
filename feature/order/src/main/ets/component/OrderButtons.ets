import { RowStartCenter, SpaceHorizontalSmall } from "designsystem";
import { IBestButton } from "ibestui";
import { Order } from "model";

/**
 * @file 订单操作按钮组件
 * @author Joker.X
 */
@ComponentV2
export struct OrderButtons {
  /**
   * 订单数据
   */
  @Param
  order: Order = new Order();
  /**
   * 取消订单按钮点击回调
   */
  @Param
  onCancelClick: () => void = () => {
  };
  /**
   * 去支付按钮点击回调
   */
  @Param
  onPayClick: () => void = () => {
  };
  /**
   * 退款/售后按钮点击回调
   */
  @Param
  onRefundClick: () => void = () => {
  };
  /**
   * 确认收货按钮点击回调
   */
  @Param
  onConfirmClick: () => void = () => {
  };
  /**
   * 查看物流按钮点击回调
   */
  @Param
  onLogisticsClick: () => void = () => {
  };
  /**
   * 去评价按钮点击回调
   */
  @Param
  onCommentClick: () => void = () => {
  };
  /**
   * 再次购买按钮点击回调
   */
  @Param
  onRebuyClick: () => void = () => {
  };

  /**
   * 构建订单按钮区域
   * @returns {void} 无返回值
   */
  build(): void {
    RowStartCenter() {
      if (this.order.status === 0) {
        this.buildOrderButton($r("app.string.cancel_order"), false, this.onCancelClick);
        SpaceHorizontalSmall();
        this.buildOrderButton($r("app.string.pay_now"), true, this.onPayClick);
      }

      if (this.order.status === 1 || this.order.status === 2) {
        this.buildOrderButton($r("app.string.order_refund_button"), false, this.onRefundClick);
        SpaceHorizontalSmall();
      }

      if (this.order.status === 2) {
        this.buildOrderButton($r("app.string.confirm_receive"), false, this.onConfirmClick);
        SpaceHorizontalSmall();
      }

      if ([2, 3, 4, 5, 6].includes(this.order.status)) {
        this.buildOrderButton($r("app.string.view_logistics"), this.order.status === 2, this.onLogisticsClick);
        SpaceHorizontalSmall();
      }

      if (this.order.status === 3 || this.order.status === 4) {
        this.buildOrderButton($r("app.string.comment_now"), false, this.onCommentClick);
        SpaceHorizontalSmall();
      }

      if (this.order.status !== 0 && this.order.status !== 2) {
        this.buildOrderButton($r("app.string.rebuy_now"), true, this.onRebuyClick);
      }
    }
  }

  /**
   * 构建单个订单操作按钮
   * @param {ResourceStr} text - 按钮文本
   * @param {boolean} isPrimary - 是否为主要按钮
   * @param {() => void} onTap - 点击回调
   * @returns {void} 无返回值
   */
  @Builder
  private buildOrderButton(text: ResourceStr, isPrimary: boolean, onTap: () => void): void {
    IBestButton({
      text: text,
      type: isPrimary ? "primary" : "default",
      plain: true,
      round: true,
      hairline: true,
      btnHeight: 30,
      fontColor: isPrimary ? undefined : $r("app.color.text_primary"),
      btnBorder: {
        width: 1,
        color: isPrimary ? $r("app.color.primary") : $r("app.color.text_primary")
      },
      onBtnClick: (): void => onTap()
    });
  }
}
