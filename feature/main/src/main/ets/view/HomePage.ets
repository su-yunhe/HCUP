import { AppNavDestination } from "ui";
import HomeViewModel from "../viewmodel/HomeViewModel";

/**
 * @file 首页视图
 * @author Joker.X
 */
@ComponentV2
export struct HomePage {
  /**
   * 首页 ViewModel
   */
  @Local
  private vm: HomeViewModel = new HomeViewModel();

  /**
   * 构建首页
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: "首页",
      viewModel: this.vm
    }) {
      this.HomeContent();
    }
  }

  /**
   * 首页内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private HomeContent() {
    Text("首页内容视图")
  }
}
