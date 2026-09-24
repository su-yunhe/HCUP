/**
 * @file 用户订单统计
 * @author Joker.X
 */
export class OrderCount {
  /**
   * 待付款订单数量
   */
  pendingPayment: number = 0;
  /**
   * 待发货订单数量
   */
  pendingShipment: number = 0;
  /**
   * 待收货订单数量
   */
  pendingReceive: number = 0;
  /**
   * 待评价订单数量
   */
  pendingReview: number = 0;
  /**
   * 退款中订单数量
   */
  refunding: number = 0;
  /**
   * 已退款订单数量
   */
  refunded: number = 0;

  constructor(init?: Partial<OrderCount>) {
    if (!init) {
      return;
    }
    this.pendingPayment = init.pendingPayment ?? this.pendingPayment;
    this.pendingShipment = init.pendingShipment ?? this.pendingShipment;
    this.pendingReceive = init.pendingReceive ?? this.pendingReceive;
    this.pendingReview = init.pendingReview ?? this.pendingReview;
    this.refunding = init.refunding ?? this.refunding;
    this.refunded = init.refunded ?? this.refunded;
  }

  /**
   * 从接口响应构建订单统计（兼容中文字段）
   * @param {object} data - 接口原始数据
   * @returns {OrderCount} 订单统计
   */
  static fromResponse(data: object): OrderCount {
    if (data instanceof OrderCount) {
      return new OrderCount(data);
    }
    const result: OrderCount = new OrderCount();
    const source: Object = data as Object;
    result.pendingPayment = OrderCount.pickNumber(source, "pendingPayment", "待付款", result.pendingPayment);
    result.pendingShipment = OrderCount.pickNumber(source, "pendingShipment", "待发货", result.pendingShipment);
    result.pendingReceive = OrderCount.pickNumber(source, "pendingReceive", "待收货", result.pendingReceive);
    result.pendingReview = OrderCount.pickNumber(source, "pendingReview", "待评价", result.pendingReview);
    result.refunding = OrderCount.pickNumber(source, "refunding", "退款中", result.refunding);
    result.refunded = OrderCount.pickNumber(source, "refunded", "已退款", result.refunded);
    return result;
  }

  /**
   * 读取数字字段（优先英文，回退中文）
   * @param {Object} source - 原始对象
   * @param {string} key - 英文字段
   * @param {string} cnKey - 中文字段
   * @param {number} fallback - 回退值
   * @returns {number} 解析后的数值
   */
  private static pickNumber(source: Object, key: string, cnKey: string, fallback: number): number {
    const englishValue: number | null = OrderCount.readNumber(source, key);
    if (englishValue !== null) {
      return englishValue;
    }
    const chineseValue: number | null = OrderCount.readNumber(source, cnKey);
    if (chineseValue !== null) {
      return chineseValue;
    }
    return fallback;
  }

  /**
   * 读取数值字段
   * @param {Object} source - 原始对象
   * @param {string} key - 字段名
   * @returns {number | null} 数值或空
   */
  private static readNumber(source: Object, key: string): number | null {
    const value: string | number | undefined = Reflect.get(source, key) as string | number | undefined;
    if (typeof value === "number") {
      return value;
    }
    if (typeof value === "string") {
      const parsed: number = Number(value);
      return Number.isNaN(parsed) ? null : parsed;
    }
    return null;
  }
}
