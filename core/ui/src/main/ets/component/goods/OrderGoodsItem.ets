import {
  ColumnStart,
  P100,
  RowSpaceBetweenCenter,
  RowStartCenter,
  SpaceHorizontalMedium,
  SpaceVerticalMedium
} from "designsystem";
import { CartGoodsSpec } from "model";
import { IBestPrice, IBestStepper } from "ibestui";
import { NetWorkImage } from "../image/NetWorkImage";

/**
 * @file 订单商品条目组件
 * @author Joker.X
 */
@ComponentV2
export struct OrderGoodsItem {
  /**
   * 规格数据
   */
  @Param
  data: CartGoodsSpec = new CartGoodsSpec();
  /**
   * 商品 id
   */
  @Param
  goodsId: number = 0;
  /**
   * 商品名称
   */
  @Param
  goodsName: string = "";
  /**
   * 商品主图
   */
  @Param
  goodsMainPic: string = "";
  /**
   * 规格点击回调
   */
  @Param
  onSpecClick: (specId: number) => void = () => {
  };
  /**
   * 数量变更回调
   */
  @Param
  onQuantityChanged: (count: number) => void = () => {
  };
  /**
   * 是否启用数量调节器
   */
  @Param
  enableQuantityStepper: boolean = true;
  /**
   * 选择框插槽
   */
  @BuilderParam
  selectSlot?: CustomBuilder;
  /**
   * 操作插槽
   */
  @BuilderParam
  actionSlot?: CustomBuilder;

  /**
   * 构建订单商品条目
   * @returns {void} 无返回值
   */
  build(): void {
    RowStartCenter({
      widthValue: P100,
      paddingValue: {
        left: this.selectSlot ? 0 : $r("app.float.space_horizontal_large"),
        right: $r("app.float.space_horizontal_large"),
        bottom: $r("app.float.space_vertical_large")
      }
    }) {
      // 选择框插槽（购物车场景）
      if (this.selectSlot) {
        Column() {
          this.selectSlot();
        }
        .padding({ left: $r("app.float.space_horizontal_large") });

        SpaceHorizontalMedium();
      }

      // 商品图片
      NetWorkImage({
        model: this.data.images?.[0] ?? this.goodsMainPic,
        sizeValue: 90,
        showBackground: true,
        cornerRadius: $r("app.float.radius_small")
      });

      SpaceHorizontalMedium();

      // 商品信息
      Column() {
        ColumnStart() {
          // 商品规格 - 使用卡片样式
          Text(this.data.name)
            .fontSize($r("app.float.body_medium"))
            .fontColor($r("app.color.text_secondary"))
            .backgroundColor($r("app.color.bg_content"))
            .borderRadius(4)
            .padding({
              left: $r("app.float.space_padding_small"),
              right: $r("app.float.space_padding_small"),
              top: $r("app.float.space_padding_small_x"),
              bottom: $r("app.float.space_padding_small_x")
            })
            .onClick((): void => {
              this.onSpecClick(this.data.id);
            });

          SpaceVerticalMedium();

          // 价格和数量/操作区域
          RowSpaceBetweenCenter({ widthValue: P100 }) {
            // 价格
            IBestPrice({ value: this.data.price });

            // 数量控制器或自定义操作区域
            if (this.actionSlot) {
              this.actionSlot();
            } else if (this.enableQuantityStepper) {
              IBestStepper({
                value: this.data.count,
                min: 1,
                max: this.data.stock > 0 ? this.data.stock : 99,
                buttonRadius: 999,
                minusBtnBgColor: "#fff",
                minusBtnIconColor: $r("app.color.primary"),
                minusBtnBorderColor: $r("app.color.primary"),
                plusBtnBgColor: $r("app.color.primary"),
                plusBtnIconColor: "#fff",
                inputBgColor: "transparent",
                iconSize: 14,
                buttonSize: 22,
                onChange: (value: number): void => {
                  this.onQuantityChanged(value);
                }
              });
            } else {
              Text(`x${this.data.count}`)
                .fontSize($r("app.float.body_medium"))
                .fontColor($r("app.color.text_secondary"));
            }
          }
        }
      }
      .layoutWeight(1)
      .alignItems(HorizontalAlign.Start);
    }
  }
}
