import { BaseViewModel } from "base";
import { navigateBack } from "navigation";

/**
 * @file 注册页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class RegisterViewModel extends BaseViewModel {
  /**
   * 更新手机号
   * @param {string} value - 手机号
   * @returns {void} 无返回值
   */
  updatePhone(value: string): void {
  }

  /**
   * 更新验证码
   * @param {string} value - 验证码
   * @returns {void} 无返回值
   */
  updateVerificationCode(value: string): void {
  }

  /**
   * 更新密码
   * @param {string} value - 密码
   * @returns {void} 无返回值
   */
  updatePassword(value: string): void {
  }

  /**
   * 更新确认密码
   * @param {string} value - 确认密码
   * @returns {void} 无返回值
   */
  updateConfirmPassword(value: string): void {
  }

  /**
   * 发送验证码
   * @returns {void} 无返回值
   */
  onSendVerificationCode(): void {
  }

  /**
   * 注册按钮点击
   * @returns {void} 无返回值
   */
  register(): void {
  }
}
