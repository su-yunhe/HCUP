/**
 * @file navigation 模块统一导出
 * @author Joker.X
 */

export { RouteBuild } from "./src/main/ets/RouteBuild";

export { RouteGraph } from "./src/main/ets/RouteGraph";

export { AuthNavigator } from "./src/main/ets/auth/AuthNavigator";

export { CommonNavigator } from "./src/main/ets/common/CommonNavigator";

export { CsNavigator } from "./src/main/ets/cs/CsNavigator";

export { FeedbackNavigator } from "./src/main/ets/feedback/FeedbackNavigator";

export { GoodsNavigator } from "./src/main/ets/goods/GoodsNavigator";

export { LaunchNavigator } from "./src/main/ets/launch/LaunchNavigator";

export { MainNavigator } from "./src/main/ets/main/MainNavigator";

export { MarketNavigator } from "./src/main/ets/market/MarketNavigator";

export { OrderNavigator } from "./src/main/ets/order/OrderNavigator";

export { UserNavigator } from "./src/main/ets/user/UserNavigator";

export { GoodsIdParam, OrderIdParam } from "./src/main/ets/NavigationParam";

export { CommonWebParam } from "./src/main/ets/common/CommonParam";

export { GoodsCategoryParam } from "./src/main/ets/goods/GoodsParam";

export {
  OrderCommentParam, OrderListParam, OrderPayParam
} from "./src/main/ets/order/OrderParam";

export { UserAddressDetailParam, UserAddressListParam } from "./src/main/ets/user/UserParam";

export { LaunchGuideParam } from "./src/main/ets/launch/LaunchParam";

export { MainCartParam } from "./src/main/ets/main/MainParam";

export {
  NAV_PATH_STACK_KEY,
  getRouteParams,
  getNavPathStack,
  navigateBack,
  navigateBackWithResult,
  navigateTo,
  navigateToForResult,
  navigateToWithResult,
  popTo,
  setNavPathStack
} from "./src/main/ets/NavigationService";
