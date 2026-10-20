import { AppNavDestination, LogoIcon } from "ui";
import { P100, P60, P70 } from "designsystem";
import { BreakpointState, getBreakpointState, getWindowSafeAreaState, WindowSafeAreaState } from "state";
import LoginViewModel, { LoginProvider } from "../viewmodel/LoginViewModel";

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

  @Local
  private breakpointState: BreakpointState = getBreakpointState();
  @Local
  private safeArea: WindowSafeAreaState = getWindowSafeAreaState();
  @Local
  private viewportHeight: number = 0;

  /**
   * 构建登录页面
   * @returns {void} 无返回值
   */
  build(): void {
    AppNavDestination({
      title: "登录",
      viewModel: this.vm,
      safeAreaEnabled: false,
      paddingValue: { top: this.safeArea.topInset, left: 0, right: 0, bottom: 0 },
      pageBackgroundColor: $r("app.color.bg_white")
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
    Column() {
      Column() {
        Scroll() {
          Column() {
            this.MainActions();
            this.AgreementFooter();
          }
          .width(P100)
          .constraintSize({ minHeight: this.viewportHeight })
          .justifyContent(FlexAlign.SpaceBetween);
        }
        .id("auth_login_scroll")
        .width(P100)
        .height(P100)
        .scrollBar(BarState.Off)
        .onAreaChange((_: Area, area: Area): void => {
          this.viewportHeight = Number(area.height);
        });
      }
      .id("auth_login_content")
      .width(P100)
      .height(P100);
    }
    .id("auth_login_page")
    .width(P100)
    .height(P100)
    .padding({
      top: 0,
      left: this.safeArea.leftInset,
      right: this.safeArea.rightInset,
      bottom: this.safeArea.bottomInset
    });
  }

  @Builder
  private MainActions(): void {
    Column() {
      Stack() {
        LogoIcon({ iconSize: 120 });
      }
      .id("auth_login_logo")
      .width(120)
      .height(120)
      .margin({ top: 24, bottom: 40 });

      Column() {
        Column({ space: 16 }) {
          Button($r("app.string.login_phone_action"))
            .id("auth_login_phone")
            .width(P100)
            .height(48)
            .fontSize($r("app.float.headline_large"))
            .fontColor(Color.White)
            .backgroundColor($r("app.color.primary"))
            .borderRadius($r("app.float.radius_large"))
            .onClick((): void => this.vm.toSmsLogin());

          Button($r("app.string.account_login"))
            .id("auth_login_account")
            .width(P100)
            .height(48)
            .fontSize($r("app.float.headline_large"))
            .fontColor($r("app.color.primary"))
            .backgroundColor(Color.Transparent)
            .border({ width: 1, color: $r("app.color.primary") })
            .borderRadius($r("app.float.radius_large"))
            .onClick((): void => this.vm.toAccountLogin());

          Text($r("app.string.other_login_methods"))
            .id("auth_login_other_methods")
            .fontSize($r("app.float.body_large"))
            .fontColor($r("app.color.text_tertiary"))
            .margin({ top: 16, bottom: 4 });

          Row() {
            this.ProviderItem(LoginProvider.Wechat, $r("app.media.ic_login_wechat"),
              $r("app.string.wechat"), "wechat");
            this.ProviderItem(LoginProvider.QQ, $r("app.media.ic_login_qq"),
              $r("app.string.qq"), "qq");
            this.ProviderItem(LoginProvider.Alipay, $r("app.media.ic_login_alipay"),
              $r("app.string.alipay"), "alipay");
          }
          .id("auth_login_social_row")
          .width(P100)
          .alignItems(VerticalAlign.Top);

          if (this.vm.errorMessage !== "") {
            Column() {
              Text(this.vm.errorMessage)
                .id("auth_login_error")
                .fontSize($r("app.float.body_large"))
                .fontColor($r("app.color.danger"))
                .textAlign(TextAlign.Center);
            }
            .id("auth_login_provider_state")
            .width(P100);
          }
        }
        .width(P100)
        .padding({ left: 24, right: 24 });
      }
      .id("auth_login_button_region")
      .width(this.breakpointState.getValue({ xs: P100, sm: P100, md: P70, lg: P60 }));
    }
    .width(P100)
    .alignItems(HorizontalAlign.Center);
  }

  @Builder
  private ProviderItem(provider: LoginProvider, icon: Resource, label: Resource, suffix: string): void {
    Column({ space: 8 }) {
      Stack() {
        Image(icon)
          .width(36)
          .height(36)
          .objectFit(ImageFit.Contain);
      }
      .id(`auth_login_${suffix}_icon`)
      .width(48)
      .height(48)
      .accessibilityText(label)
      .onClick((): void => this.vm.startProviderLogin(provider));

      Text(label)
        .id(`auth_login_${suffix}_label`)
        .fontSize($r("app.float.body_large"))
        .fontColor($r("app.color.text_secondary"))
        .textAlign(TextAlign.Center);
    }
    .layoutWeight(1)
    .alignItems(HorizontalAlign.Center);
  }

  @Builder
  private AgreementFooter(): void {
    Flex({ wrap: FlexWrap.Wrap, justifyContent: FlexAlign.Center, alignItems: ItemAlign.Center }) {
      Text($r("app.string.login_main_agreement_prefix"))
        .fontSize(12)
        .lineHeight(22)
        .fontColor($r("app.color.text_tertiary"));
      Text($r("app.string.user_agreement"))
        .id("auth_login_user_agreement")
        .fontSize(12)
        .lineHeight(22)
        .fontColor($r("app.color.primary"))
        .onClick((): void => this.vm.toUserAgreement());
      Text($r("app.string.and"))
        .fontSize(12)
        .lineHeight(22)
        .fontColor($r("app.color.text_tertiary"));
      Text($r("app.string.privacy_policy"))
        .id("auth_login_privacy_policy")
        .fontSize(12)
        .lineHeight(22)
        .fontColor($r("app.color.primary"))
        .onClick((): void => this.vm.toPrivacyPolicy());
    }
    .id("auth_login_agreement_footer")
    .width(P100)
    .padding({ left: 16, right: 16, bottom: 16 })
    .margin({ top: 48 });
  }
}
