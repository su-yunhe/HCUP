import { AppNavDestination } from "ui";
import UserAgreementViewModel from "../viewmodel/UserAgreementViewModel";

/**
 * @file 用户协议页面视图
 * @author Joker.X
 */
@ComponentV2
export struct UserAgreementPage {
  /**
   * 用户协议页面 ViewModel
   */
  @Local
  private vm: UserAgreementViewModel = new UserAgreementViewModel();

  /**
   * 构建用户协议页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: "用户协议",
      viewModel: this.vm
    }) {
      this.UserAgreementContent();
    }
  }

  /**
   * 用户协议页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private UserAgreementContent() {
    Scroll() {
      Text($r("app.string.local_user_agreement_body"))
        .id("common_user_agreement_content")
        .width("100%")
        .fontSize(16)
        .lineHeight(28)
        .fontColor($r("app.color.text_primary"))
        .padding(24);
    }
    .id("common_user_agreement_page")
    .width("100%")
    .height("100%")
    .align(Alignment.TopStart);
  }
}
