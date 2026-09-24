import { ColumnStart, P100, RowSpaceBetweenCenter } from "designsystem";
import { CommonIcon } from "ui";

/**
 * @file 商品详情顶部导航栏组件
 * @author Joker.X
 */
@ComponentV2
export struct GoodsDetailTopBar {
  /**
   * 顶部导航栏透明度（0-255）
   */
  @Param
  topBarAlpha: number = 0;
  /**
   * 顶部安全区高度
   */
  @Param
  topInset: number = 0;
  /**
   * 返回按钮点击回调
   */
  @Param
  onBackClick: () => void = (): void => {
  };
  /**
   * 分享按钮点击回调
   */
  @Param
  onShareClick: () => void = (): void => {
  };
  /**
   * 是否显示分享按钮
   */
  @Param
  showShare: boolean = true;

  /**
   * 构建商品详情顶部导航栏
   * @returns {void} 无返回值
   */
  build(): void {
    Stack({ alignContent: Alignment.TopStart }) {
      Column() {
        if (this.topInset > 0) {
          Blank().height(this.topInset);
        }
        this.TopBarRow(false);
      }
      .width(P100)
      .backgroundColor($r("app.color.bg_white"))
      .opacity(this.getBackgroundOpacity())
      .alignItems(HorizontalAlign.Start);

      ColumnStart({ widthValue: P100 }) {
        if (this.topInset > 0) {
          Blank().height(this.topInset);
        }
        this.TopBarRow(true);
      }
    }
  }

  /**
   * 顶部导航栏内容行
   * @param {boolean} showIcons - 是否显示图标
   * @returns {void} 无返回值
   */
  @Builder
  private TopBarRow(showIcons: boolean): void {
    RowSpaceBetweenCenter({
      widthValue: P100,
      paddingValue: {
        left: $r("app.float.space_padding_medium"),
        right: $r("app.float.space_padding_medium"),
        top: $r("app.float.space_padding_small"),
        bottom: $r("app.float.space_padding_small")
      }
    }) {
      if (showIcons) {
        this.CircleIconButton(
          $r("app.media.ic_left"),
          28,
          (): void => this.onBackClick()
        );
      } else {
        Blank().width(38).height(38);
      }

      if (this.showShare) {
        if (showIcons) {
          this.CircleIconButton(
            $r("app.media.ic_share_triangle"),
            20,
            (): void => this.onShareClick()
          );
        } else {
          Blank().width(38).height(38);
        }
      } else {
        Blank().width(38).height(38);
      }
    }
  }

  /**
   * 圆形图标按钮
   * @param {ResourceStr} iconResId - 图标资源
   * @param {number} iconSize - 图标大小
   * @param {() => void} onTap - 点击回调
   * @returns {void} 无返回值
   */
  @Builder
  private CircleIconButton(iconResId: ResourceStr, iconSize: number, onTap: () => void): void {
    Row() {
      CommonIcon({
        icon: iconResId,
        iconSize: iconSize,
        tintColor: $r("app.color.text_white")
      });
    }
    .width(38)
    .height(38)
    .borderRadius(19)
    .backgroundColor($r("app.color.press"))
    .justifyContent(FlexAlign.Center)
    .alignItems(VerticalAlign.Center)
    .onClick((): void => onTap());
  }

  /**
   * 获取顶部导航栏背景透明度
   * @returns {number} 透明度（0-1）
   */
  private getBackgroundOpacity(): number {
    const alpha = Math.min(Math.max(this.topBarAlpha, 0), 255);
    return alpha / 255;
  }
}
