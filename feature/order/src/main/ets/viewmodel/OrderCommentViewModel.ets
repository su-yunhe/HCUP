import { BaseViewModel } from "base";
import { OrderCommentParam } from "navigation/src/main/ets/order/OrderParam";
import { OrderRoutes } from "navigation/src/main/ets/order/OrderRoutes";
import { getRouteParams } from "navigation";
import { IBestUploaderFile } from "ibestui";

/**
 * @file 订单评论页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class OrderCommentViewModel extends BaseViewModel {
  /**
   * 路由参数
   */
  private readonly routeParam: OrderCommentParam | undefined = getRouteParams<OrderCommentParam>(OrderRoutes.Comment);
  /**
   * 订单 ID
   */
  private readonly orderId: number = this.routeParam?.orderId ?? 0;
  /**
   * 商品 ID
   */
  private readonly goodsId: number = this.routeParam?.goodsId ?? 0;
  /**
   * 评分
   */
  @Trace
  rating: number = 5;
  /**
   * 评论内容
   */
  @Trace
  commentContent: string = "";
  /**
   * 选择的图片列表
   */
  @Trace
  imageList: IBestUploaderFile[] = [];

  /**
   * 更新评分
   * @param {number} value - 新评分
   * @returns {void} 无返回值
   */
  updateRating(value: number): void {
    this.rating = value;
  }

  /**
   * 更新评论内容
   * @param {string} value - 评论内容
   * @returns {void} 无返回值
   */
  updateCommentContent(value: string): void {
    this.commentContent = value;
  }

  /**
   * 更新选择的图片列表
   * @param {IBestUploaderFile[]} list - 图片列表
   * @returns {void} 无返回值
   */
  updateImageList(list: IBestUploaderFile[]): void {
    this.imageList = list;
  }

  /**
   * 提交评论点击事件
   * @returns {void} 无返回值
   */
  onSubmitComment(): void {
  }
}
