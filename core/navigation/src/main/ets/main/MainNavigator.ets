import { navigateTo } from "../NavigationService";
import { MainRoutes } from "./MainRoutes";
import { MainCartParam } from "./MainParam";

/**
 * @file 主模块导航封装
 * @author Joker.X
 */
export class MainNavigator {
  /**
   * 跳转到主框架
   * @returns {void} 无返回值
   */
  static toMain(): void {
    navigateTo(MainRoutes.Main);
  }

  /**
   * 跳转到首页
   * @returns {void} 无返回值
   */
  static toHome(): void {
    navigateTo(MainRoutes.Home);
  }

  /**
   * 跳转到分类页
   * @returns {void} 无返回值
   */
  static toCategory(): void {
    navigateTo(MainRoutes.Category);
  }

  /**
   * 跳转到购物车页
   * @param {boolean} [showBackIcon] - 是否显示返回按钮
   * @returns {void} 无返回值
   */
  static toCart(showBackIcon?: boolean): void {
    if (showBackIcon !== undefined) {
      const params: MainCartParam = { showBackIcon };
      navigateTo(MainRoutes.Cart, params);
      return;
    }
    navigateTo(MainRoutes.Cart);
  }

  /**
   * 跳转到我的页面
   * @returns {void} 无返回值
   */
  static toMine(): void {
    navigateTo(MainRoutes.Me);
  }
}
