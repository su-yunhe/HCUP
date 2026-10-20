import { AppNavDestination } from "ui";
import PrivacyPolicyViewModel from "../viewmodel/PrivacyPolicyViewModel";

/**
 * @file 隐私政策页面视图
 * @author Joker.X
 */
@ComponentV2
export struct PrivacyPolicyPage {
  /**
   * 隐私政策页面 ViewModel
   */
  @Local
  private vm: PrivacyPolicyViewModel = new PrivacyPolicyViewModel();

  /**
   * 构建隐私政策页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: "隐私政策",
      viewModel: this.vm
    }) {
      this.PrivacyPolicyContent();
    }
  }

  /**
   * 隐私政策页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private PrivacyPolicyContent() {
    Scroll() {
      Text($r("app.string.local_privacy_policy_body"))
        .id("common_privacy_policy_content")
        .width("100%")
        .fontSize(16)
        .lineHeight(28)
        .fontColor($r("app.color.text_primary"))
        .padding(24);
    }
    .id("common_privacy_policy_page")
    .width("100%")
    .height("100%")
    .align(Alignment.TopStart);
  }
}
