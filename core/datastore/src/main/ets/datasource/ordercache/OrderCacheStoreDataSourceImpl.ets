import common from "@ohos.app.ability.common";
import preferences from "@ohos.data.preferences";
import { Cart, CartGoodsSpec, Goods, GoodsSpec, SelectedGoods } from "model";
import { ContextUtil, PreferencesUtil } from "util";
import { OrderCacheStoreDataSource } from "./OrderCacheStoreDataSource";

/**
 * Cart JSON 数据结构
 */
interface CartJson {
  goodsId: number;
  goodsName: string;
  goodsMainPic: string;
  spec: CartGoodsSpecJson[];
}

/**
 * CartGoodsSpec JSON 数据结构
 */
interface CartGoodsSpecJson {
  id: number;
  goodsId: number;
  name: string;
  price: number;
  stock: number;
  count: number;
  images: string[] | null;
}

/**
 * SelectedGoods JSON 数据结构
 */
interface SelectedGoodsJson {
  goodsId: number;
  count: number;
  goodsInfo: GoodsInfoJson | null;
  spec: GoodsSpecJson | null;
}

/**
 * Goods JSON 数据结构
 */
interface GoodsInfoJson {
  id: number;
  title: string;
  mainPic: string;
}

/**
 * GoodsSpec JSON 数据结构
 */
interface GoodsSpecJson {
  id: number;
  goodsId: number;
  name: string;
  price: number;
  stock: number;
  images: string[] | null;
}

/**
 * @file 订单缓存本地存储数据源实现，基于 Preferences 封装
 * @author Joker.X
 */
export class OrderCacheStoreDataSourceImpl implements OrderCacheStoreDataSource {
  /**
   * Preferences 工具实例
   */
  private prefs: PreferencesUtil;
  /**
   * Preferences 文件名
   */
  private static readonly PREFS_NAME: string = "order_cache_store";
  /**
   * 购物车缓存键名
   */
  private static readonly KEY_CARTS: string = "carts";
  /**
   * 已选商品列表键名
   */
  private static readonly KEY_SELECTED_GOODS_LIST: string = "selectedGoodsList";

  /**
   * 构造函数
   * @param {common.Context} [context] UIAbility 上下文
   */
  constructor(context?: common.Context) {
    const resolvedContext: common.Context = context ?? ContextUtil.getUIAbilityCtx();
    this.prefs = new PreferencesUtil(resolvedContext, OrderCacheStoreDataSourceImpl.PREFS_NAME);
  }

  /**
   * 保存选中的购物车项
   * @param {Cart[]} carts 购物车列表
   * @returns {Promise<void>} Promise<void>
   */
  async setCarts(carts: Cart[]): Promise<void> {
    const jsonStr: string = JSON.stringify(carts);
    await this.prefs.set(OrderCacheStoreDataSourceImpl.KEY_CARTS, jsonStr);
  }

  /**
   * 读取选中的购物车项
   * @returns {Promise<Cart[] | null>} 购物车列表
   */
  async getCarts(): Promise<Cart[] | null> {
    const value: preferences.ValueType =
      await this.prefs.get(OrderCacheStoreDataSourceImpl.KEY_CARTS, "");
    if (typeof value === "string" && value.length > 0) {
      try {
        const parsed: CartJson[] = JSON.parse(value) as CartJson[];
        return this.parseCartList(parsed);
      } catch {
        return null;
      }
    }
    return null;
  }

  /**
   * 保存已选商品列表
   * @param {SelectedGoods[]} goodsList 已选商品列表
   * @returns {Promise<void>} Promise<void>
   */
  async setSelectedGoodsList(goodsList: SelectedGoods[]): Promise<void> {
    const jsonStr: string = JSON.stringify(goodsList);
    await this.prefs.set(OrderCacheStoreDataSourceImpl.KEY_SELECTED_GOODS_LIST, jsonStr);
  }

  /**
   * 读取已选商品列表
   * @returns {Promise<SelectedGoods[] | null>} 已选商品列表
   */
  async getSelectedGoodsList(): Promise<SelectedGoods[] | null> {
    const value: preferences.ValueType =
      await this.prefs.get(OrderCacheStoreDataSourceImpl.KEY_SELECTED_GOODS_LIST, "");
    if (typeof value === "string" && value.length > 0) {
      try {
        const parsed: SelectedGoodsJson[] = JSON.parse(value) as SelectedGoodsJson[];
        return this.parseSelectedGoodsList(parsed);
      } catch {
        return null;
      }
    }
    return null;
  }

  /**
   * 清除所有订单缓存
   * @returns {Promise<void>} Promise<void>
   */
  async clearAll(): Promise<void> {
    await this.prefs.remove(OrderCacheStoreDataSourceImpl.KEY_CARTS);
    await this.prefs.remove(OrderCacheStoreDataSourceImpl.KEY_SELECTED_GOODS_LIST);
  }

  /**
   * 解析购物车列表
   * @param {CartJson[]} jsonList JSON 数据列表
   * @returns {Cart[]} 购物车列表
   */
  private parseCartList(jsonList: CartJson[]): Cart[] {
    const result: Cart[] = [];

    for (const item of jsonList) {
      const cart = new Cart();
      cart.goodsId = item.goodsId ?? 0;
      cart.goodsName = item.goodsName ?? "";
      cart.goodsMainPic = item.goodsMainPic ?? "";

      // 解析规格列表
      const specs: CartGoodsSpec[] = [];
      if (item.spec && Array.isArray(item.spec)) {
        for (const specItem of item.spec) {
          const spec = new CartGoodsSpec();
          spec.id = specItem.id ?? 0;
          spec.goodsId = specItem.goodsId ?? 0;
          spec.name = specItem.name ?? "";
          spec.price = specItem.price ?? 0;
          spec.stock = specItem.stock ?? 0;
          spec.count = specItem.count ?? 0;
          spec.images = specItem.images ?? null;
          specs.push(spec);
        }
      }
      cart.spec = specs;

      result.push(cart);
    }

    return result;
  }

  /**
   * 解析已选商品列表
   * @param {SelectedGoodsJson[]} jsonList JSON 数据列表
   * @returns {SelectedGoods[]} 已选商品列表
   */
  private parseSelectedGoodsList(jsonList: SelectedGoodsJson[]): SelectedGoods[] {
    const result: SelectedGoods[] = [];

    for (const item of jsonList) {
      const selectedGoods = new SelectedGoods();
      selectedGoods.goodsId = item.goodsId ?? 0;
      selectedGoods.count = item.count ?? 0;

      // 解析商品信息
      if (item.goodsInfo) {
        const goodsInfo = new Goods();
        goodsInfo.id = item.goodsInfo.id ?? 0;
        goodsInfo.title = item.goodsInfo.title ?? "";
        goodsInfo.mainPic = item.goodsInfo.mainPic ?? "";
        selectedGoods.goodsInfo = goodsInfo;
      }

      // 解析规格信息
      if (item.spec) {
        const spec = new GoodsSpec();
        spec.id = item.spec.id ?? 0;
        spec.goodsId = item.spec.goodsId ?? 0;
        spec.name = item.spec.name ?? "";
        spec.price = item.spec.price ?? 0;
        spec.stock = item.spec.stock ?? 0;
        spec.images = item.spec.images ?? null;
        selectedGoods.spec = spec;
      }

      result.push(selectedGoods);
    }

    return result;
  }
}
