import { BaseNetWorkViewModel } from "base";
import { GoodsRepository, PageRepository } from "data";
import { GoodsDetail, NetworkResponse } from "model";
import { getRouteParams, GoodsIdParam } from "navigation";
import { GoodsRoutes } from "navigation/src/main/ets/goods/GoodsRoutes";

/**
 * @file 商品详情页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class GoodsDetailViewModel extends BaseNetWorkViewModel<GoodsDetail> {
  /**
   * 页面仓库
   */
  private readonly pageRepository: PageRepository = new PageRepository();
  /**
   * 商品仓库
   */
  private readonly goodsRepository: GoodsRepository = new GoodsRepository();
  /**
   * 路由参数
   */
  private readonly routeParam: GoodsIdParam = getRouteParams<GoodsIdParam>(GoodsRoutes.Detail);
  /**
   * 商品 ID
   */
  private readonly goodsId: number = this.routeParam.goodsId ?? 0;

  /**
   * 请求商品详情页面数据
   * @returns {Promise<NetworkResponse<GoodsDetail>>} 商品详情
   */
  protected requestRepository(): Promise<NetworkResponse<GoodsDetail>> {
    return this.pageRepository.getGoodsDetail(this.goodsId);
  }
}
