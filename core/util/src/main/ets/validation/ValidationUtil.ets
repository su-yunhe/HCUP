/**
 * @file 验证工具类
 * @author Joker.X
 */
export class ValidationUtil {
  /**
   * 手机号校验正则
   */
  private static readonly PHONE_REGEX: RegExp = /^1[3-9]\d{9}$/;

  /**
   * 邮箱校验正则
   */
  private static readonly EMAIL_REGEX: RegExp = /^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$/;

  /**
   * 验证手机号是否有效
   * @param {string} phone - 手机号
   * @returns {boolean} 是否有效
   */
  static isValidPhone(phone: string): boolean {
    return phone.length === 11 && ValidationUtil.PHONE_REGEX.test(phone);
  }

  /**
   * 验证短信验证码是否有效（4位数字）
   * @param {string} code - 验证码
   * @returns {boolean} 是否有效
   */
  static isValidSmsCode(code: string): boolean {
    if (code.length !== 4) {
      return false;
    }
    for (let i = 0; i < code.length; i += 1) {
      const current: string = code[i];
      if (current < "0" || current > "9") {
        return false;
      }
    }
    return true;
  }

  /**
   * 验证图形验证码是否有效（4位数字或字母）
   * @param {string} code - 验证码
   * @returns {boolean} 是否有效
   */
  static isValidImageCode(code: string): boolean {
    if (code.length !== 4) {
      return false;
    }
    for (let i = 0; i < code.length; i += 1) {
      const current: string = code[i];
      const isNumber: boolean = current >= "0" && current <= "9";
      const isUpper: boolean = current >= "A" && current <= "Z";
      const isLower: boolean = current >= "a" && current <= "z";
      if (!isNumber && !isUpper && !isLower) {
        return false;
      }
    }
    return true;
  }

  /**
   * 验证邮箱地址是否有效
   * @param {string} email - 邮箱地址
   * @returns {boolean} 是否有效
   */
  static isValidEmail(email: string): boolean {
    return ValidationUtil.EMAIL_REGEX.test(email);
  }

  /**
   * 验证密码是否有效（长度至少6位）
   * @param {string} password - 密码
   * @returns {boolean} 是否有效
   */
  static isValidPassword(password: string): boolean {
    return password.length >= 6;
  }
}
