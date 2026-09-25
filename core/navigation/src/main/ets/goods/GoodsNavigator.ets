import { GoodsIdParam } from "../NavigationParam";
import { navigateTo } from "../NavigationService";
import { GoodsRoutes } from "./GoodsRoutes";
import { GoodsCategoryParam } from "./GoodsParam";

/**
 * @file 商品模块导航封装
 * @author Joker.X
 */
export class GoodsNavigator {
  /**
   * 跳转到商品详情
   * @param {number} goodsId - 商品 ID
   * @returns {void} 无返回值
   */
  static toDetail(goodsId: number): void {
    const params: GoodsIdParam = { goodsId };
    navigateTo(GoodsRoutes.Detail, params);
  }

  /**
   * 跳转到商品评价
   * @param {number} goodsId - 商品 ID
   * @returns {void} 无返回值
   */
  static toComment(goodsId: number): void {
    const params: GoodsIdParam = { goodsId };
    navigateTo(GoodsRoutes.Comment, params);
  }

  /**
   * 跳转到商品搜索
   * @returns {void} 无返回值
   */
  static toSearch(): void {
    navigateTo(GoodsRoutes.Search);
  }

  /**
   * 跳转到商品分类
   * @param {GoodsCategoryParam} [params] - 商品分类参数
   * @returns {void} 无返回值
   */
  static toCategory(params?: GoodsCategoryParam): void {
    if (params) {
      navigateTo(GoodsRoutes.Category, params);
      return;
    }
    navigateTo(GoodsRoutes.Category);
  }
}
