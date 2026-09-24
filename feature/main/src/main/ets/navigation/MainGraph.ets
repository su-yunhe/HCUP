import { RouteBuild, RouteGraph } from "navigation";
import { MainRoutes } from "navigation/src/main/ets/main/MainRoutes";
import { MainNav } from "./MainNav";
import { HomeNav } from "./HomeNav";
import { CategoryNav } from "./CategoryNav";
import { CartNav } from "./CartNav";
import { MeNav } from "./MeNav";

/**
 * @file 主模块导航图
 * @author Joker.X
 */
export class MainGraph implements RouteGraph {
  /**
   * 注册主模块导航路由
   */
  register(): void {
    RouteBuild.register(MainRoutes.Main, wrapBuilder(MainNav));
    RouteBuild.register(MainRoutes.Home, wrapBuilder(HomeNav));
    RouteBuild.register(MainRoutes.Category, wrapBuilder(CategoryNav));
    RouteBuild.register(MainRoutes.Cart, wrapBuilder(CartNav));
    RouteBuild.register(MainRoutes.Me, wrapBuilder(MeNav));
  }
}
