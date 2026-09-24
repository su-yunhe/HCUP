import { P100, SpaceVerticalMedium, SpaceVerticalXLarge, SpaceVerticalXXLarge } from "designsystem";
import { IBestButton } from "ibestui";
import { AppNavDestination } from "ui";
import { AnimatedAuthPage } from "../component/AnimatedAuthPage";
import { PasswordInputField } from "../component/PasswordInputField";
import { PhoneInputField } from "../component/PhoneInputField";
import { VerificationCodeField } from "../component/VerificationCodeField";
import ResetPasswordViewModel from "../viewmodel/ResetPasswordViewModel";

/**
 * @file 重置密码页面视图
 * @author Joker.X
 */
@ComponentV2
export struct ResetPasswordPage {
  /**
   * 重置密码页面 ViewModel
   */
  @Local
  private vm: ResetPasswordViewModel = new ResetPasswordViewModel();
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
   * 新密码输入
   */
  @Local
  private newPassword: string = "";
  /**
   * 确认新密码输入
   */
  @Local
  private confirmPassword: string = "";

  /**
   * 构建重置密码页面
   * @returns {void} 无返回值
   */
  build(): void {
    AppNavDestination({
      pageBackgroundColor: $r("app.color.bg_white"),
      titleOptions: { backgroundColor: $r("app.color.bg_white") },
      viewModel: this.vm
    }) {
      this.ResetPasswordContent();
    }
  }

  /**
   * 重置密码页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private ResetPasswordContent(): void {
    AnimatedAuthPage({ title: $r("app.string.reset_password") }) {
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
        password: this.newPassword,
        placeholder: $r("app.string.set_new_password"),
        onPasswordChange: (value: string): void => {
          this.newPassword = value;
          this.vm.updateNewPassword(value);
        }
      });

      SpaceVerticalXXLarge();

      PasswordInputField({
        password: this.confirmPassword,
        placeholder: $r("app.string.confirm_new_password"),
        onPasswordChange: (value: string): void => {
          this.confirmPassword = value;
          this.vm.updateConfirmPassword(value);
        }
      });

      SpaceVerticalMedium();

      Text($r("app.string.reset_password_tip"))
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.text_tertiary"))
        .width(P100)
        .textAlign(TextAlign.Start);

      // 密码不一致时提示错误信息
      if (this.newPassword.length > 0 && this.confirmPassword.length > 0 && this.newPassword !== this.confirmPassword) {
        SpaceVerticalMedium();
        Text($r("app.string.password_mismatch"))
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.danger"))
          .width(P100)
          .textAlign(TextAlign.Start);
      }

      SpaceVerticalXLarge();

      IBestButton({
        text: $r("app.string.reset_password_button"),
        type: "primary",
        round: true,
        btnWidth: P100,
        onBtnClick: (): void => {
          this.vm.resetPassword();
        }
      });
    }
  }
}
