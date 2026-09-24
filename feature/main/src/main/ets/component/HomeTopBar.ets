import { P100, SpaceHorizontalSmall, rowCenter, size } from "designsystem";
import { IBestNavBar } from "ui";

/**
 * @file 首页顶部标题栏组件
 * @author Joker.X
 */
@ComponentV2
export struct HomeTopBar {
  /**
   * 搜索框点击回调
   */
  @Param
  onSearchTap: () => void = (): void => {
  };
  /**
   * 左侧图标点击回调
   */
  @Param
  onLeftTap: () => void = (): void => {
  };
  /**
   * 右侧图标点击回调
   */
  @Param
  onRightTap: () => void = (): void => {
  };

  /**
   * 构建顶部标题栏
   * @returns {void} 无返回值
   */
  build() {
    IBestNavBar({
      isShowRight: true,
      leftRightPadding: 12,
      isShowBorder: false,
      titleBuilder: (): void => this.titleBuilder(),
      leftBuilder: (): void => this.leftBuilder(),
      rightBuilder: (): void => this.rightBuilder(),
      navBarBgColor: $r("app.color.bg_grey")
    });
  }

  /**
   * 标题区域构建
   * @returns {void} 无返回值
   */
  @Builder
  private titleBuilder() {
    Row() {
      Image($r("app.media.ic_search"))
        .fillColor($r("app.color.text_tertiary"))
        .attributeModifier(size(18));

      SpaceHorizontalSmall();

      Text($r("app.string.search_goods"))
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.text_tertiary"));
    }
    .attributeModifier(rowCenter())
    .width(P100)
    .height(38)
    .padding({
      left: $r("app.float.space_horizontal_medium"),
      right: $r("app.float.space_horizontal_medium")
    })
    .backgroundColor($r("app.color.bg_white"))
    .borderRadius($r("app.float.radius_medium"))
    .onClick((): void => this.onSearchTap());
  }

  /**
   * 左侧图标构建
   * @returns {void} 无返回值
   */
  @Builder
  private leftBuilder() {
    Image($r("app.media.ic_logo"))
      .attributeModifier(size(34))
      .onClick((): void => this.onLeftTap());
  }

  /**
   * 右侧图标构建
   * @returns {void} 无返回值
   */
  @Builder
  private rightBuilder() {
    Image($r("app.media.ic_github"))
      .attributeModifier(size(27))
      .onClick((): void => this.onRightTap());
  }
}
