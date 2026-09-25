import { GoodsIdParam, OrderIdParam } from "../NavigationParam";

/**
 * @file 订单模块导航参数定义
 * @author Joker.X
 */

/**
 * 订单列表参数
 */
export interface OrderListParam {
  /**
   * Tab 标签（可选）
   */
  tab?: string;
}

/**
 * 订单支付参数
 */
export interface OrderPayParam extends OrderIdParam {
  /**
   * 支付价格
   */
  price: number;
  /**
   * 来源（可选）
   */
  from?: string;
}

/**
 * 订单评价参数
 */
export interface OrderCommentParam extends OrderIdParam, GoodsIdParam {}
