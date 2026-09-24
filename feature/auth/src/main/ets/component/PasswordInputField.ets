import { ColumnStart, P100 } from "designsystem";
import { IBestField, IBestFieldValueType } from "ibestui";
import { FocusableDivider } from "./FocusableDivider";

/**
 * @file 密码输入组件
 * @author Joker.X
 */
@ComponentV2
export struct PasswordInputField {
  /**
   * 密码
   */
  @Param
  password: string = "";
  /**
   * 占位提示
   */
  @Param
  placeholder: ResourceStr = $r("app.string.password_hint");
  /**
   * 密码变更回调
   */
  @Param
  onPasswordChange: (value: string) => void = () => {
  };
  /**
   * 输入框聚焦状态
   */
  @Local
  private isFocused: boolean = false;
  /**
   * 密码是否隐藏
   */
  @Local
  private isPasswordHidden: boolean = true;

  /**
   * 构建密码输入组件
   * @returns {void} 无返回值
   */
  build(): void {
    ColumnStart({ widthValue: P100 }) {
      IBestField({
        value: this.password,
        type: this.isPasswordHidden ? "password" : "normal",
        showLabel: false,
        labelWidth: 0,
        inputAlign: "left",
        inputFontSize: 16,
        inputFontColor: $r("app.color.text_primary"),
        placeholder: this.placeholder,
        placeholderColor: $r("app.color.text_quaternary"),
        showPasswordIcon: false,
        rightIcon: this.isPasswordHidden ? $r("app.media.ic_eye_hide") : $r("app.media.ic_eye"),
        hasBorder: false,
        borderLeft: 0,
        fieldPadding: 0,
        onRightIconClick: (): void => {
          this.isPasswordHidden = !this.isPasswordHidden;
        },
        onFieldFocus: (): void => {
          this.isFocused = true;
        },
        onFieldBlur: (): void => {
          this.isFocused = false;
        },
        onChange: (value: IBestFieldValueType): void => {
          this.onPasswordChange(`${value ?? ""}`);
        }
      })
        .width(P100);

      FocusableDivider({ focused: this.isFocused });
    }
  }
}
