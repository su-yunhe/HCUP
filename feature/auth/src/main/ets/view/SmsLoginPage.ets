import { P100, SpaceVerticalMedium, SpaceVerticalSmall, SpaceVerticalXLarge, SpaceVerticalXXLarge } from "designsystem";
import { IBestButton } from "ibestui";
import { CommonNavigator, navigateBack } from "navigation";
import { AppNavDestination } from "ui";
import { AnimatedAuthPage } from "../component/AnimatedAuthPage";
import { BottomNavigationRow } from "../component/BottomNavigationRow";
import { PhoneInputField } from "../component/PhoneInputField";
import { UserAgreement } from "../component/UserAgreement";
import { VerificationCodeField } from "../component/VerificationCodeField";
import SmsLoginViewModel from "../viewmodel/SmsLoginViewModel";

/**
 * @file 短信登录页面视图
 * @author Joker.X
 */
@ComponentV2
export struct SmsLoginPage {
  /**
   * 短信登录页面 ViewModel
   */
  @Local
  private vm: SmsLoginViewModel = new SmsLoginViewModel();
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
   * 构建短信登录页面
   * @returns {void} 无返回值
   */
  build(): void {
    AppNavDestination({
      pageBackgroundColor: $r("app.color.bg_white"),
      titleOptions: { backgroundColor: $r("app.color.bg_white") },
      viewModel: this.vm
    }) {
      this.SmsLoginContent();
    }
  }

  /**
   * 短信登录页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private SmsLoginContent(): void {
    AnimatedAuthPage({ title: $r("app.string.welcome_login") }) {
      PhoneInputField({
        phone: this.phone,
        onPhoneChange: (value: string): void => {
          this.phone = value;
          this.vm.updatePhone(value);
        }
      });

      SpaceVerticalXXLarge();
      SpaceVerticalSmall();

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
        onBtnClick: (): void => {
          this.vm.login();
        }
      });

      BottomNavigationRow({
        messageText: $r("app.string.sms_not_available"),
        actionText: $r("app.string.use_third_party_login"),
        onActionClick: (): void => {
          navigateBack();
        }
      });
    }
  }
}
