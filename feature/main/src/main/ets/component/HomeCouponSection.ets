import { P100, SpaceHorizontalSmall, size, RowStartCenter } from "designsystem";
import { Coupon } from "model";
import { Card } from "ui";

/**
 * @file 首页优惠券区域组件
 * @author Joker.X
 */
@ComponentV2
export struct HomeCouponSection {
  /**
   * 优惠券列表
   */
  @Param
  coupons: Coupon[] = [];

  /**
   * 构建优惠券区域
   * @returns {void} 无返回值
   */
  build(): void {
    Card({ paddingValue: $r("app.float.space_vertical_medium") }) {
      Row() {
        Swiper() {
          ForEach(this.coupons, (coupon: Coupon): void => {
            this.couponCard(coupon);
          }, (coupon: Coupon): string => `${coupon.id}-${coupon.title}`);
        }
        .indicator(false)
        .autoPlay(false)
        .loop(false)
        .layoutWeight(1);

        Column()
          .width($r("app.float.space_divider"))
          .height(20)
          .backgroundColor($r("app.color.border"))
          .margin({
            left: $r("app.float.space_padding_medium"),
            right: $r("app.float.space_padding_medium")
          });

        Text($r("app.string.receive"))
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.primary"));
      }
    }
  }

  /**
   * 构建优惠券卡片内容
   * @param {Coupon} coupon - 优惠券信息
   * @returns {void} 无返回值
   */
  @Builder
  private couponCard(coupon: Coupon): void {
    RowStartCenter({ widthValue: P100 }) {
      Row() {
        Image($r("app.media.ic_coupon"))
          .fillColor($r("app.color.text_primary"))
          .attributeModifier(size(18));
      }
      .padding($r("app.float.space_padding_small_x"))
      .backgroundColor($r("app.color.bg_grey"))
      .borderRadius($r("app.float.radius_small_x"));

      SpaceHorizontalSmall();

      Text(coupon.title)
        .fontSize($r("app.float.body_large"))
        .maxLines(1)
        .textOverflow({ overflow: TextOverflow.Ellipsis })
        .layoutWeight(1);
    }
  }
}