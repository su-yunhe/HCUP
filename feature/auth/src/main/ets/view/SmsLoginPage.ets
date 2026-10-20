import { AppNavDestination } from "ui";
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
   * 构建短信登录页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: "短信登录",
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
  private SmsLoginContent() {
    Column() {
      Text("手机短信验证码登录")
        .fontSize($r("app.float.display_medium"))
        .fontColor($r("app.color.text_primary"));
    }
    .id("auth_sms_login_page")
    .width("100%")
    .height("100%")
    .padding(24);
  }
}
