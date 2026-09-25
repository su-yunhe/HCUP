import {
  ColumnCenter,
  P100,
  RowSpaceBetweenCenter,
  RowStartCenter,
  SpaceHorizontalLarge,
  SpaceVerticalXSmall
} from "designsystem";
import { IBestButton } from "ibestui";
import { getWindowSafeAreaState, WindowSafeAreaState } from "state";
import { CommonIcon } from "ui";

/**
 * @file 商品详情底部操作栏组件
 * @author Joker.X
 */
@ComponentV2
export struct GoodsDetailBottomBar {
  /**
   * 加入购物车按钮点击回调
   */
  @Param
  onAddToCartClick: () => void = (): void => {
  };
  /**
   * 立即购买按钮点击回调
   */
  @Param
  onBuyNowClick: () => void = (): void => {
  };
  /**
   * 客服入口点击回调
   */
  @Param
  onCsClick: () => void = (): void => {
  };
  /**
   * 购物车入口点击回调
   */
  @Param
  onCartClick: () => void = (): void => {
  };
  /**
   * 是否启用底部安全区
   */
  @Param
  safeAreaEnabled: boolean = true;
  /**
   * 当前窗口安全区状态（可外部传入，默认内部获取）
   */
  @Param
  windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();

  /**
   * 构建商品详情底部操作栏
   * @returns {void} 无返回值
   */
  build(): void {
    Column() {
      RowSpaceBetweenCenter({
        widthValue: P100,
        paddingValue: {
          top: $r("app.float.space_vertical_small"),
          bottom: this.safeAreaEnabled && this.windowSafeAreaState.bottomInset > 0
            ? 0
            : $r("app.float.space_vertical_small")
        }
      }) {
        RowStartCenter({
          paddingValue: { left: $r("app.float.space_horizontal_small") }
        }) {
          this.ActionIconButton(
            $r("app.media.ic_customer_service"),
            $r("app.string.customer_service"),
            (): void => this.onCsClick()
          );

          this.ActionIconButton(
            $r("app.media.ic_cart"),
            $r("app.string.shopping_cart"),
            (): void => this.onCartClick()
          );
        }

        RowStartCenter({
          paddingValue: { right: $r("app.float.space_horizontal_large") }
        }) {
          IBestButton({
            text: $r("app.string.add_to_cart"),
            type: "primary",
            plain: true,
            hairline: true,
            btnHeight: 34,
            btnBorder: {
              width: 1,
              color: $r("app.color.primary"),
            },
            onBtnClick: (): void => this.onAddToCartClick()
          });

          SpaceHorizontalLarge();

          IBestButton({
            text: $r("app.string.buy_now"),
            type: "primary",
            btnHeight: 34,
            onBtnClick: (): void => this.onBuyNowClick()
          });
        }
      }

      if (this.safeAreaEnabled && this.windowSafeAreaState.bottomInset > 0) {
        Blank().height(this.windowSafeAreaState.bottomInset);
      }
    }
    .width(P100)
    .backgroundColor($r("app.color.bg_white"));
  }

  /**
   * 操作入口按钮（图标 + 文案）
   * @param {ResourceStr} iconResId - 图标资源
   * @param {ResourceStr} text - 文案资源
   * @param {() => void} onTap - 点击回调
   * @returns {void} 无返回值
   */
  @Builder
  private ActionIconButton(iconResId: ResourceStr, text: ResourceStr, onTap: () => void): void {
    ColumnCenter({
      widthValue: 40,
      paddingValue: {
        top: $r("app.float.space_vertical_small_x"),
        bottom: $r("app.float.space_vertical_small_x")
      },
      onTap: (): void => onTap()
    }) {
      CommonIcon({
        icon: iconResId,
        iconSize: 20,
        tintColor: $r("app.color.text_secondary")
      });

      SpaceVerticalXSmall();

      Text(text)
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.text_secondary"));
    }
  }
}
