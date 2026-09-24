import { P100 } from "designsystem";

/**
 * @file 商品详情轮播图组件
 * @author Joker.X
 */
@ComponentV2
export struct GoodsBanner {
  /**
   * 轮播图数据
   */
  @Param
  bannerList: string[] = [];
  /**
   * 是否自动轮播
   */
  @Param
  autoPlay: boolean = false;
  /**
   * 是否循环轮播
   */
  @Param
  loop: boolean = false;
  /**
   * 图片缩放模式
   */
  @Param
  imageFit: ImageFit = ImageFit.Cover;

  /**
   * 构建轮播图视图
   * @returns {void} 无返回值
   */
  build(): void {
    if (this.bannerList && this.bannerList.length > 0) {
      Swiper() {
        ForEach(this.bannerList, (item: string, index: number): void => {
          Image(item)
            .width(P100)
            .height(P100)
            .objectFit(this.imageFit);
        }, (item: string, index: number): string => `${item}-${index}`);
      }
      .displayCount(1)
      .displayMode(SwiperDisplayMode.STRETCH)
      .indicator(Indicator.dot()
        .color($r("app.color.bg_purple_light"))
        .selectedColor($r("app.color.primary")))
      .autoPlay(this.autoPlay)
      .loop(this.loop)
      .width(P100)
      .height(P100)
      .aspectRatio(1);
    }
  }
}
