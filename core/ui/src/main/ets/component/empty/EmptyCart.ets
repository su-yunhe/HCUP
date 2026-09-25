import { Empty } from "./Empty";

/**
 * @file 购物车缺省页
 * @author Joker.X
 */
@ComponentV2
export struct EmptyCart {
  /**
   * 构建购物车缺省页视图
   * @returns {void} 无返回值
   */
  build(): void {
    Empty({
      description: $r("app.string.empty_cart"),
      imageRes: $r("app.media.ic_empty_cart")
    });
  }
}
