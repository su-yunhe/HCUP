import { P100 } from "designsystem";

/**
 * 无法得知图片尺寸时的占位宽高比
 */
const DEFAULT_ASPECT_RATIO: number = 1;

/**
 * @file 商品详情图片组件
 */
@ComponentV2
export struct GoodsDetailImage {
  /**
   * 图片地址
   */
  @Param
  url: string = "";
  /**
   * 图片序号（用于生成稳定 id）
   */
  @Param
  index: number = 0;
  /**
   * 图片加载完成后的真实宽高比
   */
  @Local
  private loadedRatio: number = 0;

  /**
   * 构建商品详情图片
   * @returns {void} 无返回值
   */
  build(): void {
    Stack() {
      Column()
        .width(P100)
        .height(P100)
        .backgroundColor($r("app.color.bg_content"));

      Image(this.url)
        .id(`goods_detail_image_${this.index}`)
        .width(P100)
        .height(P100)
        .objectFit(ImageFit.Auto)
        .onComplete((event): void => {
          if (event && event.width > 0 && event.height > 0) {
            this.loadedRatio = event.width / event.height;
          }
        });
    }
    .width(P100)
    .aspectRatio(this.getAspectRatio());
  }

  /**
   * 获取占位宽高比：优先使用加载结果，其次使用地址中的 w/h 参数
   * @returns {number} 宽高比
   */
  private getAspectRatio(): number {
    if (this.loadedRatio > 0) {
      return this.loadedRatio;
    }
    const width: number = this.getUrlParam("w");
    const height: number = this.getUrlParam("h");
    return width > 0 && height > 0 ? width / height : DEFAULT_ASPECT_RATIO;
  }

  /**
   * 读取地址中的数字参数
   * @param {string} name - 参数名
   * @returns {number} 参数值，不存在时为 0
   */
  private getUrlParam(name: string): number {
    const match: RegExpMatchArray | null = this.url.match(new RegExp(`[?&]${name}=(\\d+)`));
    return match ? Number(match[1]) : 0;
  }
}
