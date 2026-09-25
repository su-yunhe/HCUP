import {
  ColumnCenter,
  LargePaddingVerticalScroll,
  P100,
  P60,
  P70,
  RowSpaceEvenlyCenter,
  SpaceVerticalLarge,
  SpaceVerticalSmall,
  SpaceVerticalXLarge,
  SpaceVerticalXXLarge
} from "designsystem";
import { IBestButton } from "ibestui";
import { AuthNavigator, CommonNavigator } from "navigation";
import { AppNavDestination, CommonIcon, LogoIcon } from "ui";
import { bp } from "state";
import { UserAgreement } from "../component/UserAgreement";
import LoginViewModel from "../viewmodel/LoginViewModel";

/**
 * @file 登录页面视图
 * @author Joker.X
 */
@ComponentV2
export struct LoginPage {
  /**
   * 登录页面 ViewModel
   */
  @Local
  private vm: LoginViewModel = new LoginViewModel();

  /**
   * 构建登录页面
   * @returns {void} 无返回值
   */
  build(): void {
    AppNavDestination({
      viewModel: this.vm,
      pageBackgroundColor: $r("app.color.bg_white"),
      titleOptions: { backgroundColor: $r("app.color.bg_white") }
    }) {
      this.LoginContent();
    }
  }

  /**
   * 登录页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private LoginContent(): void {
    LargePaddingVerticalScroll({ fillMaxSize: true }) {
      Column() {
        LogoIcon({ iconSize: 120 });
        SpaceVerticalLarge();
        Blank().layoutWeight(1);
        this.buildActionSection();
      }
      .constraintSize({ minHeight: P100 });
    }
  }

  /**
   * 构建底部操作区域
   * @returns {void} 无返回值
   */
  @Builder
  private buildActionSection(): void {
    ColumnCenter({
      widthValue: bp({
        sm: P100,
        md: P70,
        lg: P60
      })
    }) {
      this.buildLoginButtons();
      this.buildThirdPartySection();
      this.buildUserAgreementSection();
    }
  }

  /**
   * 构建登录按钮区域
   * @returns {void} 无返回值
   */
  @Builder
  private buildLoginButtons(): void {
    IBestButton({
      text: $r("app.string.sms_login"),
      type: "primary",
      round: true,
      btnWidth: P100,
      onBtnClick: (): void => {
        AuthNavigator.toSmsLogin();
      }
    });

    SpaceVerticalXLarge();

    IBestButton({
      text: $r("app.string.account_login"),
      type: "primary",
      plain: true,
      hairline: true,
      round: true,
      btnWidth: P100,
      onBtnClick: (): void => {
        AuthNavigator.toAccountLogin();
      }
    });

    SpaceVerticalXXLarge();
    SpaceVerticalLarge();
  }

  /**
   * 构建第三方登录区域
   * @returns {void} 无返回值
   */
  @Builder
  private buildThirdPartySection(): void {
    Text($r("app.string.other_login_methods"))
      .fontSize($r("app.float.body_medium"))
      .fontColor($r("app.color.text_tertiary"));

    SpaceVerticalXLarge();

    RowSpaceEvenlyCenter({ widthValue: P100 }) {
      // 第三方登录按钮
      this.buildThirdPartyLoginButton($r("app.media.ic_wechat"), $r("app.string.wechat"), () => {
        this.vm.onWechatLoginClick();
      });

      this.buildThirdPartyLoginButton($r("app.media.ic_qq"), $r("app.string.qq"), () => {
        this.vm.onQQLoginClick();
      });

      this.buildThirdPartyLoginButton($r("app.media.ic_alipay"), $r("app.string.alipay"), () => {
        this.vm.onAlipayLoginClick();
      });
    }

    SpaceVerticalXXLarge();
  }

  /**
   * 构建第三方登录按钮
   * @param {ResourceStr} icon - 图标资源
   * @param {ResourceStr} name - 文案资源
   * @param {() => void} onTap - 点击回调
   * @returns {void} 无返回值
   */
  @Builder
  private buildThirdPartyLoginButton(icon: ResourceStr, name: ResourceStr, onTap: () => void): void {
    ColumnCenter({
      onTap: (): void => {
        onTap();
      }
    }) {
      CommonIcon({
        icon: icon,
        iconSize: bp({
          sm: 32,
          md: 36,
          lg: 40
        })
      });

      SpaceVerticalSmall();

      Text(name)
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.text_tertiary"));
    }
  }

  /**
   * 构建用户协议区域
   * @returns {void} 无返回值
   */
  @Builder
  private buildUserAgreementSection(): void {
    UserAgreement({
      centerAlignment: true,
      onUserAgreementClick: (): void => {
        CommonNavigator.toUserAgreement();
      },
      onPrivacyPolicyClick: (): void => {
        CommonNavigator.toPrivacyPolicy();
      }
    });
  }
}
