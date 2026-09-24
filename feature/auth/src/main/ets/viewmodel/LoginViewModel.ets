import { BaseViewModel } from "base";
/**
 * @file 登录页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class LoginViewModel extends BaseViewModel {
  /**
   * 微信登录点击
   * @returns {void} 无返回值
   */
  onWechatLoginClick(): void {
    // 第三方登录暂未接入，等待后续实现
  }

  /**
   * QQ 登录点击
   * @returns {void} 无返回值
   */
  onQQLoginClick(): void {
    // 第三方登录暂未接入，等待后续实现
  }

  /**
   * 支付宝登录点击
   * @returns {void} 无返回值
   */
  onAlipayLoginClick(): void {
    // 第三方登录暂未接入，等待后续实现
  }

}
