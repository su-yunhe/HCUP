import { OrderCacheStoreDataSource, OrderCacheStoreDataSourceImpl } from "datastore";
import { Cart, SelectedGoods } from "model";

/**
 * @file 订单缓存本地存储仓库，封装存取逻辑
 *
 * 使用两个 key：
 * - carts: 从购物车来的商品项（仅购物车页面存储）
 * - selectedGoodsList: 选中的商品列表（购物车和商品详情页都存储）
 * @author Joker.X
 */
export class OrderCacheStoreRepository {
  /**
   * 本地数据源实例
   */
  private dataSource: OrderCacheStoreDataSource;

  /**
   * 构造函数
   * @param {OrderCacheStoreDataSource} [dataSource] 可选自定义数据源
   */
  constructor(dataSource?: OrderCacheStoreDataSource) {
    this.dataSource = dataSource ?? new OrderCacheStoreDataSourceImpl();
  }

  /**
   * 保存选中的购物车项（仅购物车页面使用）
   * @param {Cart[]} carts 购物车列表
   * @returns {Promise<void>} Promise<void>
   */
  saveCarts(carts: Cart[]): Promise<void> {
    return this.dataSource.setCarts(carts);
  }

  /**
   * 读取选中的购物车项
   * @returns {Promise<Cart[] | null>} 购物车列表，不存在返回 null
   */
  loadCarts(): Promise<Cart[] | null> {
    return this.dataSource.getCarts();
  }

  /**
   * 保存已选商品列表
   * @param {SelectedGoods[]} goodsList 已选商品列表
   * @returns {Promise<void>} Promise<void>
   */
  saveSelectedGoodsList(goodsList: SelectedGoods[]): Promise<void> {
    return this.dataSource.setSelectedGoodsList(goodsList);
  }

  /**
   * 读取已选商品列表
   * @returns {Promise<SelectedGoods[] | null>} 已选商品列表，不存在返回 null
   */
  loadSelectedGoodsList(): Promise<SelectedGoods[] | null> {
    return this.dataSource.getSelectedGoodsList();
  }

  /**
   * 清除所有订单缓存（carts 和 selectedGoodsList）
   * @returns {Promise<void>} Promise<void>
   */
  clearAll(): Promise<void> {
    return this.dataSource.clearAll();
  }
}
