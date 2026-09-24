import { ColumnStart, P100 } from "designsystem";
import { IBestCell, IBestCellGroup } from "ibestui";
import { TitleWithLine } from "ui";

/**
 * @file 商品详情图文组件
 * @author Joker.X
 */
@ComponentV2
export struct GoodsDetailRichHeader {
  /**
   * 构建商品详情图文标题
   * @returns {void} 无返回值
   */
  build(): void {
    ColumnStart({
      widthValue: P100,
      paddingValue: {
        left: $r("app.float.space_horizontal_medium"),
        right: $r("app.float.space_horizontal_medium")
      }
    }) {
      IBestCellGroup({
        inset: true,
        radius: {
          topLeft: $r("app.float.radius_medium"),
          topRight: $r("app.float.radius_medium"),
        },
        outerMargin: 0
      }) {
        IBestCell({
          isLink: false,
          clickable: false,
          hasBorder: true,
          titleBuilder: (): void => this.buildDetailTitle()
        });
      }
    }
  }

  /**
   * 商品详情标题构建
   * @returns {void} 无返回值
   */
  @Builder
  private buildDetailTitle(): void {
    TitleWithLine({ text: $r("app.string.goods_detail") });
  }
}