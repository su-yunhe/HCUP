/**
 * @file 退款请求实体类
 * @author Joker.X
 */
export class RefundOrderRequest {
  /**
   * 订单ID
   */
  orderId: number;
  /**
   * 退款原因
   */
  reason: string;

  /**
   * @param {RefundOrderRequest} init - 初始化数据
   */
  constructor(init: RefundOrderRequest) {
    this.orderId = init.orderId;
    this.reason = init.reason;
  }
}
