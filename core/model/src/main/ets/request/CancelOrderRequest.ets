/**
 * @file 取消订单请求模型
 * @author Joker.X
 */
export class CancelOrderRequest {
  /**
   * 订单ID
   */
  orderId: number;
  /**
   * 取消原因
   */
  remark: string;

  /**
   * @param {CancelOrderRequest} init - 初始化数据
   */
  constructor(init: CancelOrderRequest) {
    this.orderId = init.orderId;
    this.remark = init.remark;
  }
}
