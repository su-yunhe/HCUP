import { AppNavDestination } from "ui";
import CategoryViewModel from "../viewmodel/CategoryViewModel";

/**
 * @file 分类页面视图
 * @author Joker.X
 */
@ComponentV2
export struct CategoryPage {
  /**
   * 分类页面 ViewModel
   */
  @Local
  private vm: CategoryViewModel = new CategoryViewModel();

  /**
   * 构建分类页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: "分类",
      viewModel: this.vm
    }) {
      this.CategoryContent();
    }
  }

  /**
   * 分类页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private CategoryContent() {
    Text("分类页面内容视图")
  }
}
