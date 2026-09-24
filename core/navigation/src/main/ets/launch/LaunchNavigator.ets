import { navigateTo } from "../NavigationService";
import { LaunchRoutes } from "./LaunchRoutes";
import { LaunchGuideParam } from "./LaunchParam";

/**
 * @file 启动流程模块导航封装
 * @author Joker.X
 */
export class LaunchNavigator {
  /**
   * 跳转到启动页
   * @returns {void} 无返回值
   */
  static toSplash(): void {
    navigateTo(LaunchRoutes.Splash);
  }

  /**
   * 跳转到引导页
   * @param {boolean} [fromSettings] - 是否从设置页进入
   * @returns {void} 无返回值
   */
  static toGuide(fromSettings?: boolean): void {
    if (fromSettings !== undefined) {
      const params: LaunchGuideParam = { fromSettings };
      navigateTo(LaunchRoutes.Guide, params);
      return;
    }
    navigateTo(LaunchRoutes.Guide);
  }
}
