import { BaseViewModel } from "base";
import { User } from "model";
import { navigateBack } from "navigation";
import { getUserState, UserState } from "state";

/**
 * @file 个人中心页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class ProfileViewModel extends BaseViewModel {
  /**
   * 全局用户状态
   */
  private readonly userState: UserState = getUserState();
  /**
   * 退出登录弹窗显示状态
   */
  @Trace
  showLogoutDialog: boolean = false;

  /**
   * 页面显示时回调
   * @returns {void} 无返回值
   */
  aboutToAppear(): void {
    this.userState.refreshUserInfo();
  }

  /**
   * 触发退出登录弹窗
   * @returns {void} 无返回值
   */
  requestLogout(): void {
    this.showLogoutDialog = true;
  }

  /**
   * 退出登录点击
   * @returns {void} 无返回值
   */
  onLogoutClick(): void {
    this.requestLogout();
  }

  /**
   * 确认退出登录
   * @returns {void} 无返回值
   */
  confirmLogout(): void {
    this.userState.logout();
    this.hideLogoutDialog();
    navigateBack();
  }

  /**
   * 隐藏退出登录弹窗
   * @returns {void} 无返回值
   */
  hideLogoutDialog(): void {
    this.showLogoutDialog = false;
  }

  /**
   * 获取用户信息
   * @returns {UserState} 用户状态
   */
  getUserState(): UserState {
    return this.userState;
  }

  /**
   * 获取用户信息
   * @returns {User} 用户信息
   */
  getUserInfo(): User {
    return this.userState.getUserInfo();
  }

  /**
   * 获取头像地址
   * @returns {ResourceStr} 头像地址
   */
  getAvatarUrl(): ResourceStr {
    return this.getUserInfo().avatarUrl;
  }

  /**
   * 获取昵称展示文本
   * @returns {ResourceStr} 昵称文本
   */
  getNickNameText(): ResourceStr {
    return this.getUserInfo().nickName ?? $r("app.string.not_set");
  }

  /**
   * 获取手机号展示文本
   * @returns {ResourceStr} 手机号文本
   */
  getPhoneText(): ResourceStr {
    const phone: string = this.getUserInfo().phone ?? "";
    return phone ? phone : $r("app.string.not_bound");
  }

  /**
   * 获取账号展示文本
   * @returns {ResourceStr} 账号文本
   */
  getAccountText(): ResourceStr {
    const id: number | null = this.getUserInfo().id ?? null;
    return id ? `${id}` : $r("app.string.not_set");
  }
}
