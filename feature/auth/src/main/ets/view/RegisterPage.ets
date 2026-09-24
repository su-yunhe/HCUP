import { P100, SpaceVerticalMedium, SpaceVerticalXLarge, SpaceVerticalXXLarge } from "designsystem";
import { IBestButton } from "ibestui";
import { CommonNavigator, navigateBack } from "navigation";
import { AppNavDestination } from "ui";
import { AnimatedAuthPage } from "../component/AnimatedAuthPage";
import { BottomNavigationRow } from "../component/BottomNavigationRow";
import { PasswordInputField } from "../component/PasswordInputField";
import { PhoneInputField } from "../component/PhoneInputField";
import { UserAgreement } from "../component/UserAgreement";
import { VerificationCodeField } from "../component/VerificationCodeField";
import RegisterViewModel from "../viewmodel/RegisterViewModel";

/**
 * @file 注册页面视图
 * @author Joker.X
 */
@ComponentV2
export struct RegisterPage {
  /**
   * 注册页面 ViewModel
   */
  @Local
  private vm: RegisterViewModel = new RegisterViewModel();
  /**
   * 手机号输入
   */
  @Local
  private phone: string = "";
  /**
   * 验证码输入
   */
  @Local
  private verificationCode: string = "";
  /**
   * 密码输入
   */
  @Local
  private password: string = "";
  /**
   * 确认密码输入
   */
  @Local
  private confirmPassword: string = "";

  /**
   * 构建注册页面
   * @returns {void} 无返回值
   */
  build(): void {
    AppNavDestination({
      pageBackgroundColor: $r("app.color.bg_white"),
      titleOptions: { backgroundColor: $r("app.color.bg_white") },
      viewModel: this.vm
    }) {
      this.RegisterContent();
    }
  }

  /**
   * 注册页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private RegisterContent(): void {
    AnimatedAuthPage({ title: $r("app.string.welcome_register") }) {
      PhoneInputField({
        phone: this.phone,
        onPhoneChange: (value: string): void => {
          this.phone = value;
          this.vm.updatePhone(value);
        }
      });

      SpaceVerticalXXLarge();

      VerificationCodeField({
        verificationCode: this.verificationCode,
        onVerificationCodeChange: (value: string): void => {
          this.verificationCode = value;
          this.vm.updateVerificationCode(value);
        },
        onSendVerificationCode: (): void => {
          this.vm.onSendVerificationCode();
        }
      });

      SpaceVerticalXXLarge();

      PasswordInputField({
        password: this.password,
        placeholder: $r("app.string.set_password"),
        onPasswordChange: (value: string): void => {
          this.password = value;
          this.vm.updatePassword(value);
        }
      });

      SpaceVerticalXXLarge();

      PasswordInputField({
        password: this.confirmPassword,
        placeholder: $r("app.string.confirm_password"),
        onPasswordChange: (value: string): void => {
          this.confirmPassword = value;
          this.vm.updateConfirmPassword(value);
        }
      });

      SpaceVerticalMedium();

      UserAgreement({
        prefix: $r("app.string.register_agreement_prefix"),
        onUserAgreementClick: (): void => {
          CommonNavigator.toUserAgreement();
        },
        onPrivacyPolicyClick: (): void => {
          CommonNavigator.toPrivacyPolicy();
        }
      });

      SpaceVerticalXLarge();

      IBestButton({
        text: $r("app.string.register"),
        type: "primary",
        round: true,
        btnWidth: P100,
        onBtnClick: (): void => {
          this.vm.register();
        }
      });

      BottomNavigationRow({
        messageText: $r("app.string.have_account"),
        actionText: $r("app.string.go_login"),
        onActionClick: (): void => {
          navigateBack();
        }
      });
    }
  }
}
