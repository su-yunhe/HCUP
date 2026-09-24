import { AppNavDestination } from "ui";
import MeViewModel from "../viewmodel/MeViewModel";

/**
 * @file 我的页面视图
 * @author Joker.X
 */
@ComponentV2
export struct MePage {
  /**
   * 我的页面 ViewModel
   */
  @Local
  private vm: MeViewModel = new MeViewModel();

  /**
   * 构建我的页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: "我的",
      viewModel: this.vm
    }) {
      this.MeContent();
    }
  }

  /**
   * 我的页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private MeContent() {
    Text("我的页面内容视图")
  }
}
