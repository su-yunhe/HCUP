import { ColumnStart, P100 } from "designsystem";
import { IBestField, IBestFieldValueType } from "ibestui";
import { FocusableDivider } from "./FocusableDivider";

/**
 * @file 手机号输入组件
 * @author Joker.X
 */
@ComponentV2
export struct PhoneInputField {
  /**
   * 手机号
   */
  @Param
  phone: string = "";
  /**
   * 占位提示
   */
  @Param
  placeholder: ResourceStr = $r("app.string.phone_hint");
  /**
   * 手机号变更回调
   */
  @Param
  onPhoneChange: (value: string) => void = () => {
  };
  /**
   * 输入框聚焦状态
   */
  @Local
  private isFocused: boolean = false;

  /**
   * 构建手机号输入组件
   * @returns {void} 无返回值
   */
  build(): void {
    ColumnStart({ widthValue: P100 }) {
      IBestField({
        value: this.phone,
        type: "phone",
        showLabel: false,
        labelWidth: 0,
        inputAlign: "left",
        inputFontSize: 16,
        inputFontColor: $r("app.color.text_primary"),
        placeholder: this.placeholder,
        placeholderColor: $r("app.color.text_quaternary"),
        prefix: $r("app.string.phone_code"),
        prefixSize: 16,
        prefixFontColor: $r("app.color.primary"),
        hasBorder: false,
        borderLeft: 0,
        fieldPadding: 0,
        onFieldFocus: (): void => {
          this.isFocused = true;
        },
        onFieldBlur: (): void => {
          this.isFocused = false;
        },
        onChange: (value: IBestFieldValueType): void => {
          this.onPhoneChange(`${value ?? ""}`);
        }
      })
        .width(P100);

      FocusableDivider({ focused: this.isFocused });
    }
  }
}
