import { Goods } from "./Goods";
import { GoodsSpec } from "./GoodsSpec";

/**
 * @file 已选商品项模型
 *
 * 用于规格选择后返回的数据，表示用户选择的单个商品规格项
 * @author Joker.X
 */
export class SelectedGoods {
  /**
   * 商品ID
   */
  goodsId: number = 0;
  /**
   * 商品信息
   */
  goodsInfo?: Goods | null = null;
  /**
   * 规格
   */
  spec?: GoodsSpec | null = null;
  /**
   * 数量
   */
  count: number = 0;

  /**
   * @param {Partial<SelectedGoods>} init - 初始化数据
   */
  constructor(init?: Partial<SelectedGoods>) {
    if (!init) {
      return;
    }
    this.goodsId = init.goodsId ?? this.goodsId;
    this.goodsInfo = init.goodsInfo ?? this.goodsInfo;
    this.spec = init.spec ?? this.spec;
    this.count = init.count ?? this.count;
  }
}
