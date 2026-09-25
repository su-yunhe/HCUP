import { BaseViewModel } from "base";
import { AccountStoreRepository, AuthRepository } from "data";
import { Auth, PasswordLoginRequest } from "model";
import { navigateBack } from "navigation";
import { RequestHelper } from "result";
import { getUserState, UserState } from "state";
import { ContextUtil, ToastUtils, ValidationUtil } from "util";

/**
 * @file 账号登录页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class AccountLoginViewModel extends BaseViewModel {
  /**
   * 全局用户状态
   */
  private readonly userState: UserState = getUserState();
  /**
   * 认证仓库
   */
  private readonly authRepository: AuthRepository = new AuthRepository();
  /**
   * 账号存储仓库
   */
  private readonly accountStoreRepository: AccountStoreRepository =
    new AccountStoreRepository(ContextUtil.getUIAbilityCtx());
  /**
   * 账号输入
   */
  @Trace
  account: string = "";
  /**
   * 密码输入
   */
  @Trace
  password: string = "";
  /**
   * 登录按钮加载状态
   */
  @Trace
  isLoginLoading: boolean = false;

  /**
   * 页面出现前生命周期
   * @returns {void} 无返回值
   */
  aboutToAppear(): void {
    super.aboutToAppear();
    this.loadSavedCredentials();
  }

  /**
   * 执行登录操作
   * @returns {void} 无返回值
   */
  login(): void {
    if (!ValidationUtil.isValidPhone(this.account)) {
      ToastUtils.showError($r("app.string.invalid_phone_number"));
      return;
    }
    if (!ValidationUtil.isValidPassword(this.password)) {
      ToastUtils.showError($r("app.string.invalid_password"));
      return;
    }
    const params: PasswordLoginRequest = new PasswordLoginRequest(this.account, this.password);
    RequestHelper.repository(this.authRepository.loginByPassword(params))
      .start((): void => {
        this.isLoginLoading = true;
      })
      .execute()
      .then((authData: Auth): void => {
        this.onLoginSuccess(authData);
      })
      .finally((): void => {
        this.isLoginLoading = false;
      });
  }

  /**
   * 登录成功处理
   * @param {Auth} authData - 认证数据
   * @returns {Promise<void>} Promise<void>
   */
  private async onLoginSuccess(authData: Auth): Promise<void> {
    await this.saveCredentials(this.account, this.password);
    this.userState.updateAuth(authData);
    this.userState.refreshUserInfo();
    ToastUtils.showSuccess($r("app.string.login_success"));
    navigateBack();
    navigateBack();
  }

  /**
   * 加载已保存的账号密码
   * @returns {Promise<void>} Promise<void>
   */
  private async loadSavedCredentials(): Promise<void> {
    const savedAccount: string = await this.accountStoreRepository.loadAccount();
    const savedPassword: string = await this.accountStoreRepository.loadPassword();
    if (savedAccount) {
      this.account = savedAccount;
    }
    if (savedPassword) {
      this.password = savedPassword;
    }
  }

  /**
   * 保存账号密码
   * @param {string} account - 账号
   * @param {string} password - 密码
   * @returns {Promise<void>} Promise<void>
   */
  private async saveCredentials(account: string, password: string): Promise<void> {
    await Promise.all([
      this.accountStoreRepository.saveAccount(account),
      this.accountStoreRepository.savePassword(password)
    ]);
  }

  /**
   * 更新账号输入
   * @param {string} value - 账号值
   * @returns {void} 无返回值
   */
  updateAccount(value: string): void {
    this.account = value;
  }

  /**
   * 更新密码输入
   * @param {string} value - 密码值
   * @returns {void} 无返回值
   */
  updatePassword(value: string): void {
    this.password = value;
  }
}
