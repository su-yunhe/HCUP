import { Comment } from "./Comment";

/**
 * @file 商品评论提交请求模型
 * @author Joker.X
 */
export class GoodsCommentSubmitRequest {
  /**
   * 订单ID
   */
  orderId: number;
  /**
   * 评论数据
   */
  data: Comment;

  /**
   * @param {GoodsCommentSubmitRequest} init - 初始化数据
   */
  constructor(init: GoodsCommentSubmitRequest) {
    this.orderId = init.orderId;
    this.data = new Comment(init.data);
  }
}
