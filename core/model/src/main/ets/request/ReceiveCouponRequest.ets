/**
 * @file 领取优惠券请求参数
 * @author Joker.X
 */
export class ReceiveCouponRequest {
  /**
   * 优惠券ID
   */
  couponId: number;

  /**
   * @param {ReceiveCouponRequest} init - 初始化数据
   */
  constructor(init: ReceiveCouponRequest) {
    this.couponId = init.couponId;
  }
}
