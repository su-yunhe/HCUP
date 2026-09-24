import { BaseNetWorkListViewModel } from "base";
import { GoodsRepository } from "data";
import { Comment, GoodsCommentPageRequest, NetworkPageData, NetworkResponse } from "model";
import { getRouteParams, GoodsIdParam } from "navigation";
import { GoodsRoutes } from "navigation/src/main/ets/goods/GoodsRoutes";
import { IBestImagePreview } from "ibestui";

/**
 * @file 商品评论页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class GoodsCommentViewModel extends BaseNetWorkListViewModel<Comment> {
  /**
   * 商品仓库
   */
  private readonly repository: GoodsRepository = new GoodsRepository();
  /**
   * 路由参数
   */
  private readonly routeParam: GoodsIdParam = getRouteParams<GoodsIdParam>(GoodsRoutes.Comment);
  /**
   * 商品 ID
   */
  private readonly goodsId: number = this.routeParam.goodsId ?? 0;

  /**
   * 请求商品评论分页数据
   * @returns {Promise<NetworkResponse<NetworkPageData<Comment>>>} 网络请求 Promise
   */
  protected requestListData(): Promise<NetworkResponse<NetworkPageData<Comment>>> {
    const request: GoodsCommentPageRequest = new GoodsCommentPageRequest({
      goodsId: `${this.goodsId}`
    });
    request.page = this.currentPage;
    request.size = this.pageSize;
    return this.repository.getGoodsCommentPage(request);
  }

  /**
   * 打开图片预览
   * @param {string[]} images - 图片列表
   * @param {number} startIndex - 起始索引
   * @returns {void} 无返回值
   */
  openImagePreview(images: string[], startIndex: number): void {
    if (images.length === 0) {
      return;
    }
    IBestImagePreview.show(images, {
      startIndex
    });
  }
}
