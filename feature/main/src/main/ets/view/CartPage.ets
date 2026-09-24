import { AppNavDestination } from "ui";
import CartViewModel from "../viewmodel/CartViewModel";

/**
 * @file 购物车页面视图
 * @author Joker.X
 */
@ComponentV2
export struct CartPage {
  /**
   * 购物车页面 ViewModel
   */
  @Local
  private vm: CartViewModel = new CartViewModel();

  /**
   * 构建购物车页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: "购物车",
      viewModel: this.vm
    }) {
      this.CartContent();
    }
  }

  /**
   * 购物车页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private CartContent() {
    Text("购物车页面内容视图")
  }
}
