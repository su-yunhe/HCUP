import { navigateTo } from "../NavigationService";
import { CommonRoutes } from "./CommonRoutes";
import { CommonWebParam } from "./CommonParam";

/**
 * @file 公共模块导航封装
 * @author Joker.X
 */
export class CommonNavigator {
  /**
   * 跳转到关于我们
   * @returns {void} 无返回值
   */
  static toAbout(): void {
    navigateTo(CommonRoutes.About);
  }

  /**
   * 跳转到设置页
   * @returns {void} 无返回值
   */
  static toSettings(): void {
    navigateTo(CommonRoutes.Settings);
  }

  /**
   * 跳转到用户协议
   * @returns {void} 无返回值
   */
  static toUserAgreement(): void {
    navigateTo(CommonRoutes.UserAgreement);
  }

  /**
   * 跳转到隐私政策
   * @returns {void} 无返回值
   */
  static toPrivacyPolicy(): void {
    navigateTo(CommonRoutes.PrivacyPolicy);
  }

  /**
   * 跳转到贡献者列表
   * @returns {void} 无返回值
   */
  static toContributors(): void {
    navigateTo(CommonRoutes.Contributors);
  }

  /**
   * 跳转到 WebView 页面
   * @param {string} url - 页面 URL
   * @param {string} [title] - 页面标题
   * @returns {void} 无返回值
   */
  static toWeb(url: string, title?: string): void {
    const params: CommonWebParam = {
      url: url,
      title: title
    };
    navigateTo(CommonRoutes.Web, params);
  }
}
