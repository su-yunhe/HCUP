import { IBestCell, IBestCellGroup } from "ibestui";
import { ColumnStart, P100 } from "designsystem";
import { TitleWithLine } from "ui";

/**
 * @file 发货与服务卡片组件
 * @author Joker.X
 */
@ComponentV2
export struct GoodsShippingServiceCard {
  /**
   * 构建发货与服务卡片
   * @returns {void} 无返回值
   */
  build(): void {
    ColumnStart({
      widthValue: P100,
      paddingValue: {
        left: $r("app.float.space_horizontal_medium"),
        right: $r("app.float.space_horizontal_medium"),
      }
    }) {
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        IBestCell({
          isLink: false,
          clickable: false,
          titleBuilder: (): void => this.buildTitle()
        });

        IBestCell({
          title: $r("app.string.shipping"),
          value: $r("app.string.shipping_location"),
          isLink: false,
          clickable: false
        });

        IBestCell({
          title: $r("app.string.service"),
          value: $r("app.string.service_details"),
          leftContentWidth: 80,
          isLink: false,
          clickable: false,
          hasBorder: false
        });
      }
    }
  }

  /**
   * 构建标题区域
   * @returns {void} 无返回值
   */
  @Builder
  private buildTitle(): void {
    TitleWithLine({ text: $r("app.string.shipping_and_service") });
  }
}
