/**
 * @file 商品评论分页查询请求模型
 * @author Joker.X
 */
/**
 * 商品评论分页请求初始化参数
 */
interface IGoodsCommentPageRequestInit {
  goodsId: string;
  page?: number;
  size?: number;
}

export class GoodsCommentPageRequest {
  /**
   * 商品ID
   */
  goodsId: string;
  /**
   * 页码
   */
  page: number = 1;
  /**
   * 每页大小
   */
  size: number = 20;

  /**
   * @param {IGoodsCommentPageRequestInit} init - 初始化数据
   */
  constructor(init: IGoodsCommentPageRequestInit) {
    this.goodsId = init.goodsId;
    this.page = init.page ?? this.page;
    this.size = init.size ?? this.size;
  }
}
