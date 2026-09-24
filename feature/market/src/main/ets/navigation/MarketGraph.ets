import { RouteBuild, RouteGraph } from "navigation";
import { MarketRoutes } from "navigation/src/main/ets/market/MarketRoutes";
import { CouponNav } from "./CouponNav";

/**
 * @file 营销模块导航图
 * @author Joker.X
 */
export class MarketGraph implements RouteGraph {
  /**
   * 注册营销模块导航路由
   */
  register(): void {
    RouteBuild.register(MarketRoutes.Coupon, wrapBuilder(CouponNav));
  }
}
