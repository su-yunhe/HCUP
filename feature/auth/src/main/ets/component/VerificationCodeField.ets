import { ColumnStart, P100 } from "designsystem";
import { IBestField, IBestFieldValueType } from "ibestui";
import { FocusableDivider } from "./FocusableDivider";

/**
 * @file 验证码输入组件
 * @author Joker.X
 */
@ComponentV2
export struct VerificationCodeField {
  /**
   * 验证码
   */
  @Param
  verificationCode: string = "";
  /**
   * 占位提示
   */
  @Param
  placeholder: ResourceStr = $r("app.string.verification_code");
  /**
   * 手机号是否有效
   */
  @Param
  isPhoneValid: boolean = true;
  /**
   * 验证码变更回调
   */
  @Param
  onVerificationCodeChange: (value: string) => void = () => {
  };
  /**
   * 发送验证码回调
   */
  @Param
  onSendVerificationCode: () => void = () => {
  };
  /**
   * 输入框聚焦状态
   */
  @Local
  private isFocused: boolean = false;

  /**
   * 构建验证码输入组件
   * @returns {void} 无返回值
   */
  build(): void {
    ColumnStart({ widthValue: P100 }) {
      IBestField({
        value: this.verificationCode,
        type: "number",
        showLabel: false,
        labelWidth: 0,
        inputAlign: "left",
        inputFontSize: 16,
        inputFontColor: $r("app.color.text_primary"),
        placeholder: this.placeholder,
        placeholderColor: $r("app.color.text_quaternary"),
        maxlength: 4,
        hasBorder: false,
        borderLeft: 0,
        fieldPadding: 0,
        buttonBuilder: (): void => this.buildSendCodeText(),
        onFieldFocus: (): void => {
          this.isFocused = true;
        },
        onFieldBlur: (): void => {
          this.isFocused = false;
        },
        onChange: (value: IBestFieldValueType): void => {
          const nextValue = `${value ?? ""}`;
          // 只允许输入数字且长度不超过 4 位
          if (/^\\d*$/.test(nextValue) && nextValue.length <= 4) {
            this.onVerificationCodeChange(nextValue);
          }
        }
      })
        .width(P100);

      FocusableDivider({ focused: this.isFocused });
    }
  }

  /**
   * 构建发送验证码按钮
   * @returns {void} 无返回值
   */
  @Builder
  private buildSendCodeText(): void {
    Text($r("app.string.get_verification_code"))
      .fontSize($r("app.float.headline_large"))
      .fontColor(this.getSendCodeTextColor())
      .onClick((): void => {
        if (this.isPhoneValid) {
          this.onSendVerificationCode();
        }
      });
  }

  /**
   * 获取发送验证码文本颜色
   * @returns {ResourceColor} 文本颜色
   */
  private getSendCodeTextColor(): ResourceColor {
    return this.isPhoneValid ? $r("app.color.warning") : $r("app.color.text_quaternary");
  }
}
