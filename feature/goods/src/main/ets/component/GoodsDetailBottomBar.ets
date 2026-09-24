import { P100, RowSpaceBetweenCenter } from "designsystem";

/**
 * @file 商品详情底部操作栏组件
 * @author Joker.X
 */
@ComponentV2
export struct GoodsDetailBottomBar {
  /**
   * 构建商品详情底部操作栏
   * @returns {void} 无返回值
   */
  build(): void {
    RowSpaceBetweenCenter({
      widthValue: P100,
      paddingValue: {
        left: $r("app.float.space_horizontal_medium"),
        right: $r("app.float.space_horizontal_medium"),
        top: $r("app.float.space_vertical_small"),
        bottom: $r("app.float.space_vertical_small")
      },
      bgColor: $r("app.color.bg_white")
    }) {
      Text("操作栏")
    }
  }
}
