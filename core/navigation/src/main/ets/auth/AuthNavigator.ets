import { navigateTo } from "../NavigationService";
import { AuthRoutes } from "./AuthRoutes";

/**
 * @file 认证模块导航封装
 * @author Joker.X
 */
export class AuthNavigator {
  /**
   * 跳转到登录主页
   * @returns {void} 无返回值
   */
  static toLogin(): void {
    navigateTo(AuthRoutes.Login);
  }

  /**
   * 跳转到账号密码登录
   * @returns {void} 无返回值
   */
  static toAccountLogin(): void {
    navigateTo(AuthRoutes.AccountLogin);
  }

  /**
   * 跳转到短信验证码登录
   * @returns {void} 无返回值
   */
  static toSmsLogin(): void {
    navigateTo(AuthRoutes.SmsLogin);
  }

  /**
   * 跳转到注册页面
   * @returns {void} 无返回值
   */
  static toRegister(): void {
    navigateTo(AuthRoutes.Register);
  }

  /**
   * 跳转到重置密码页面
   * @returns {void} 无返回值
   */
  static toResetPassword(): void {
    navigateTo(AuthRoutes.ResetPassword);
  }
}
