import { Cart, SelectedGoods } from "model";

/**
 * @file 订单缓存本地存储数据源接口
 *
 * 使用两个 key：
 * - carts: 从购物车来的商品项（仅购物车页面存储）
 * - selectedGoodsList: 选中的商品列表（购物车和商品详情页都存储）
 * @author Joker.X
 */
export interface OrderCacheStoreDataSource {
  /**
   * 保存选中的购物车项（仅购物车页面使用）
   * @param {Cart[]} carts 购物车列表
   * @returns {Promise<void>} Promise<void>
   */
  setCarts(carts: Cart[]): Promise<void>;

  /**
   * 读取选中的购物车项
   * @returns {Promise<Cart[] | null>} 购物车列表，不存在返回 null
   */
  getCarts(): Promise<Cart[] | null>;

  /**
   * 保存已选商品列表
   * @param {SelectedGoods[]} goodsList 已选商品列表
   * @returns {Promise<void>} Promise<void>
   */
  setSelectedGoodsList(goodsList: SelectedGoods[]): Promise<void>;

  /**
   * 读取已选商品列表
   * @returns {Promise<SelectedGoods[] | null>} 已选商品列表，不存在返回 null
   */
  getSelectedGoodsList(): Promise<SelectedGoods[] | null>;

  /**
   * 清除所有订单缓存（carts 和 selectedGoodsList）
   * @returns {Promise<void>} Promise<void>
   */
  clearAll(): Promise<void>;
}
