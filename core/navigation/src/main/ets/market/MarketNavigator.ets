import { navigateTo } from "../NavigationService";
import { MarketRoutes } from "./MarketRoutes";

/**
 * @file 营销模块导航封装
 * @author Joker.X
 */
export class MarketNavigator {
  /**
   * 跳转到优惠券页面
   * @returns {void} 无返回值
   */
  static toCoupon(): void {
    navigateTo(MarketRoutes.Coupon);
  }
}
