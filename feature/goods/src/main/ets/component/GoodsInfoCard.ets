import { IBestPrice } from "ibestui";
import {
  ColumnStart,
  P100,
  RowSpaceBetweenCenter,
  SpaceHorizontalXSmall,
  SpaceVerticalMedium,
  SpaceVerticalSmall,
  SpaceVerticalXSmall
} from "designsystem";
import { Coupon, Goods, GoodsSpec } from "model";
import { ArrowRightIcon, Card, CommonIcon } from "ui";

/**
 * @file 商品信息卡片组件
 * @author Joker.X
 */
@ComponentV2
export struct GoodsInfoCard {
  /**
   * 商品信息
   */
  @Param
  goodsInfo: Goods = new Goods();
  /**
   * 优惠券列表
   */
  @Param
  coupons: Coupon[] = [];
  /**
   * 已选规格
   */
  @Param
  selectedSpec: GoodsSpec | undefined = undefined;
  /**
   * 规格选择点击回调
   */
  @Param
  onSpecClick: () => void = (): void => {
  };
  /**
   * 优惠券点击回调
   */
  @Param
  onCouponClick: () => void = (): void => {
  };

  /**
   * 构建商品信息卡片视图
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
      Card({
        widthValue: P100,
        paddingValue: $r("app.float.space_padding_medium")
      }) {
        ColumnStart({ widthValue: P100 }) {
          RowSpaceBetweenCenter({ widthValue: P100 }) {
            IBestPrice({
              value: this.goodsInfo.price,
              integerFontSize: 20
            });

            Text($r("app.string.sold_count", this.goodsInfo.sold))
              .fontSize($r("app.float.body_medium"))
              .fontColor($r("app.color.text_white"))
              .padding({
                left: $r("app.float.space_padding_small"),
                right: $r("app.float.space_padding_small"),
                top: $r("app.float.space_padding_small_x"),
                bottom: $r("app.float.space_padding_small_x")
              })
              .backgroundColor($r("app.color.primary"))
              .borderRadius(100);
          }

          this.CouponList();

          Text(this.goodsInfo.title)
            .fontSize($r("app.float.headline_large"))
            .fontColor($r("app.color.text_primary"))
            .fontWeight(FontWeight.Bold)
            .maxLines(2)
            .textOverflow({ overflow: TextOverflow.Ellipsis });

          if (this.goodsInfo.subTitle) {
            SpaceVerticalXSmall();
            Text(this.goodsInfo.subTitle ?? "")
              .fontSize($r("app.float.body_medium"))
              .fontColor($r("app.color.text_subtitle"))
              .maxLines(2)
              .textOverflow({ overflow: TextOverflow.Ellipsis });
          }

          SpaceVerticalMedium();

          this.SpecSelection();
        }
      }
    }
  }

  /**
   * 优惠券标签列表
   * @returns {void} 无返回值
   */
  @Builder
  private CouponList(): void {
    if (this.coupons.length > 0) {
      SpaceVerticalSmall();
      Flex({ wrap: FlexWrap.Wrap }) {
        ForEach(this.coupons, (coupon: Coupon, index: number): void => {
          this.CouponTag(coupon);
        }, (coupon: Coupon, index: number): string => `${coupon.id}-${index}`);
      }
      .width(P100);
    }
  }

  /**
   * 优惠券标签
   * @param {Coupon} coupon - 优惠券信息
   * @returns {void} 无返回值
   */
  @Builder
  private CouponTag(coupon: Coupon): void {
    Row() {
      CommonIcon({
        icon: $r("app.media.ic_coupon"),
        iconSize: 14,
        tintColor: $r("app.color.danger")
      });

      SpaceHorizontalXSmall();

      Text($r(
        "app.string.coupon_text",
        coupon.condition?.fullAmount ?? 0,
        coupon.amount ?? 0
      ))
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.danger"));
    }
    .padding({
      left: $r("app.float.space_padding_small"),
      right: $r("app.float.space_padding_small"),
      top: $r("app.float.space_padding_small_x"),
      bottom: $r("app.float.space_padding_small_x")
    })
    .margin({
      right: $r("app.float.space_horizontal_small"),
      bottom: $r("app.float.space_vertical_small")
    })
    .border({
      width: 1,
      color: $r("app.color.danger"),
      radius: $r("app.float.radius_small_x")
    })
    .onClick((): void => {
      this.onCouponClick();
    });
  }

  /**
   * 规格选择区域
   * @returns {void} 无返回值
   */
  @Builder
  private SpecSelection(): void {
    Row() {
      Row() {
        CommonIcon({
          icon: $r("app.media.ic_cube"),
          iconSize: 16,
          tintColor: $r("app.color.text_subtitle")
        });

        SpaceHorizontalXSmall();

        Text(this.selectedSpec
          ? $r("app.string.selected_spec", this.selectedSpec.name)
          : $r("app.string.select_spec"))
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.text_secondary"));
      }
      .alignItems(VerticalAlign.Center);

      ArrowRightIcon({ iconSize: 16 });
    }
    .width(P100)
    .justifyContent(FlexAlign.SpaceBetween)
    .alignItems(VerticalAlign.Center)
    .padding($r("app.float.space_padding_medium"))
    .border({
      width: 1,
      color: $r("app.color.text_quaternary"),
      radius: $r("app.float.radius_small")
    })
    .onClick((): void => {
      this.onSpecClick();
    });
  }
}
