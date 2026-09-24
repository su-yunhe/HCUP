import { P100, SpaceVerticalMedium, SpaceVerticalSmall, SpaceVerticalXLarge, SpaceVerticalXXLarge } from "designsystem";
import { IBestButton } from "ibestui";
import { AuthNavigator, CommonNavigator } from "navigation";
import { AppNavDestination } from "ui";
import { AnimatedAuthPage } from "../component/AnimatedAuthPage";
import { BottomNavigationRow } from "../component/BottomNavigationRow";
import { PasswordInputField } from "../component/PasswordInputField";
import { PhoneInputField } from "../component/PhoneInputField";
import { UserAgreement } from "../component/UserAgreement";
import AccountLoginViewModel from "../viewmodel/AccountLoginViewModel";

/**
 * @file 账号登录页面视图
 * @author Joker.X
 */
@ComponentV2
export struct AccountLoginPage {
  /**
   * 账号登录页面 ViewModel
   */
  @Local
  private vm: AccountLoginViewModel = new AccountLoginViewModel();

  /**
   * 构建账号登录页面
   * @returns {void} 无返回值
   */
  build(): void {
    AppNavDestination({
      pageBackgroundColor: $r("app.color.bg_white"),
      titleOptions: { backgroundColor: $r("app.color.bg_white") },
      viewModel: this.vm
    }) {
      this.AccountLoginContent();
    }
  }

  /**
   * 账号登录页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private AccountLoginContent(): void {
    AnimatedAuthPage({ title: $r("app.string.welcome_login") }) {
      PhoneInputField({
        phone: this.vm.account,
        onPhoneChange: (value: string): void => {
          this.vm.updateAccount(value);
        }
      });

      SpaceVerticalXXLarge();
      SpaceVerticalSmall();

      PasswordInputField({
        password: this.vm.password,
        onPasswordChange: (value: string): void => {
          this.vm.updatePassword(value);
        }
      });

      SpaceVerticalMedium();

      UserAgreement({
        onUserAgreementClick: (): void => {
          CommonNavigator.toUserAgreement();
        },
        onPrivacyPolicyClick: (): void => {
          CommonNavigator.toPrivacyPolicy();
        }
      });

      SpaceVerticalXLarge();

      IBestButton({
        text: $r("app.string.login"),
        type: "primary",
        round: true,
        btnWidth: P100,
        loading: this.vm.isLoginLoading,
        disabled: this.vm.isLoginLoading,
        onBtnClick: (): void => this.vm.login()
      });

      BottomNavigationRow({
        messageText: $r("app.string.go_register"),
        actionText: $r("app.string.forgot_password"),
        divider: true,
        onCancelClick: (): void => {
          AuthNavigator.toRegister();
        },
        onActionClick: (): void => {
          AuthNavigator.toResetPassword();
        }
      });
    }
  }
}
