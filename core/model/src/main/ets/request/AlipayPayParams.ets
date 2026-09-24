/**
 * @file 支付宝支付请求参数
 * @author Joker.X
 */
export interface AlipayPayParams extends Record<string, number> {
  /**
   * 订单 ID
   */
  orderId: number;
}
