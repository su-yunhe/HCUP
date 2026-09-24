import { ColumnStart, P100, SpaceVerticalMedium } from "designsystem";

/**
 * @file 用户协议组件
 * @author Joker.X
 */
@ComponentV2
export struct UserAgreement {
  /**
   * 协议前缀文案
   */
  @Param
  prefix: ResourceStr = $r("app.string.login_agreement_prefix");
  /**
   * 是否居中对齐
   */
  @Param
  centerAlignment: boolean = false;
  /**
   * 用户协议点击回调
   */
  @Param
  onUserAgreementClick: () => void = () => {
  };
  /**
   * 隐私政策点击回调
   */
  @Param
  onPrivacyPolicyClick: () => void = () => {
  };

  /**
   * 构建用户协议区域
   * @returns {void} 无返回值
   */
  build(): void {
    ColumnStart({ widthValue: P100 }) {
      Text() {
        Span(this.prefix)
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.text_tertiary"));

        Span($r("app.string.user_agreement"))
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.primary"))
          .onClick((): void => {
            this.onUserAgreementClick();
          });

        Span($r("app.string.and"))
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.text_tertiary"));

        Span($r("app.string.privacy_policy"))
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.primary"))
          .onClick((): void => {
            this.onPrivacyPolicyClick();
          });
      }
      .width(P100)
      .textAlign(this.centerAlignment ? TextAlign.Center : TextAlign.Start);

      if (!this.centerAlignment) {
        SpaceVerticalMedium();
      }
    }
  }
}
