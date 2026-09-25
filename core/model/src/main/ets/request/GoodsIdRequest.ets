/**
 * @file 商品 ID 请求参数
 * @author Joker.X
 */
export class GoodsIdRequest {
  /**
   * 商品 ID
   */
  goodsId: number = 0;

  /**
   * @param {Partial<GoodsIdRequest>} init - 初始化数据
   */
  constructor(init?: Partial<GoodsIdRequest>) {
    if (!init) {
      return;
    }
    this.goodsId = init.goodsId ?? this.goodsId;
  }
}
