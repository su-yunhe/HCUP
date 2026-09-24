/**
 * @file 商品模块导航参数定义
 * @author Joker.X
 */

/**
 * 商品分类参数
 */
export interface GoodsCategoryParam {
  /**
   * 类型 ID（可选）
   */
  typeId?: string;
  /**
   * 是否精选
   */
  featured?: boolean;
  /**
   * 是否推荐
   */
  recommend?: boolean;
  /**
   * 关键词（可选）
   */
  keyword?: string;
  /**
   * 最小金额（可选）
   */
  minPrice?: string;
}
