import { navigateTo } from "../NavigationService";
import { OrderRoutes } from "./OrderRoutes";
import { OrderIdParam } from "../NavigationParam";
import { OrderCommentParam, OrderListParam, OrderPayParam } from "./OrderParam";

/**
 * @file 订单模块导航封装
 * @author Joker.X
 */
export class OrderNavigator {
  /**
   * 跳转到订单列表
   * @param {string} [tab] - Tab 标签
   * @returns {void} 无返回值
   */
  static toList(tab?: string): void {
    if (tab) {
      const params: OrderListParam = { tab };
      navigateTo(OrderRoutes.List, params);
      return;
    }
    navigateTo(OrderRoutes.List);
  }

  /**
   * 跳转到确认订单
   * @returns {void} 无返回值
   */
  static toConfirm(): void {
    navigateTo(OrderRoutes.Confirm);
  }

  /**
   * 跳转到订单详情
   * @param {number} orderId - 订单 ID
   * @returns {void} 无返回值
   */
  static toDetail(orderId: number): void {
    const params: OrderIdParam = { orderId };
    navigateTo(OrderRoutes.Detail, params);
  }

  /**
   * 跳转到订单支付
   * @param {number} orderId - 订单 ID
   * @param {number} price - 支付价格
   * @param {string} [from] - 来源
   * @returns {void} 无返回值
   */
  static toPay(orderId: number, price: number, from?: string): void {
    if (from) {
      const params: OrderPayParam = { orderId, price, from };
      navigateTo(OrderRoutes.Pay, params);
      return;
    }
    const params: OrderPayParam = { orderId, price };
    navigateTo(OrderRoutes.Pay, params);
  }

  /**
   * 跳转到退款申请
   * @param {number} orderId - 订单 ID
   * @returns {void} 无返回值
   */
  static toRefund(orderId: number): void {
    const params: OrderIdParam = { orderId };
    navigateTo(OrderRoutes.Refund, params);
  }

  /**
   * 跳转到订单评价
   * @param {number} orderId - 订单 ID
   * @param {number} goodsId - 商品 ID
   * @returns {void} 无返回值
   */
  static toComment(orderId: number, goodsId: number): void {
    const params: OrderCommentParam = { orderId, goodsId };
    navigateTo(OrderRoutes.Comment, params);
  }

  /**
   * 跳转到订单物流
   * @param {number} orderId - 订单 ID
   * @returns {void} 无返回值
   */
  static toLogistics(orderId: number): void {
    const params: OrderIdParam = { orderId };
    navigateTo(OrderRoutes.Logistics, params);
  }
}
