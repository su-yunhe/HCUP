import { BaseNetWorkListUiState, BaseViewModel } from "base";
import { FootprintRepository } from "data";
import { Footprint, Goods } from "model";
import { GoodsNavigator } from "navigation";

/**
 * @file 足迹页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class FootprintViewModel extends BaseViewModel {
  /**
   * 足迹仓库
   */
  private readonly repository: FootprintRepository = new FootprintRepository();
  /**
   * 足迹列表
   */
  @Trace
  footprints: Footprint[] = [];
  /**
   * 足迹商品列表
   */
  @Trace
  goodsList: Goods[] = [];
  /**
   * 足迹数量
   */
  @Trace
  footprintCount: number = 0;
  /**
   * 页面 UI 状态
   */
  @Trace
  uiState: BaseNetWorkListUiState = BaseNetWorkListUiState.LOADING;
  /**
   * 清空弹窗显示状态
   */
  @Trace
  showClearDialog: boolean = false;

  /**
   * 页面显示时回调
   * @returns {void} 无返回值
   */
  aboutToAppear(): void {
    this.loadFootprints();
  }

  /**
   * 加载足迹数据
   * @returns {void} 无返回值
   */
  loadFootprints(): void {
    this.uiState = BaseNetWorkListUiState.LOADING;
    Promise.all([
      this.repository.getAllFootprints(),
      this.repository.getFootprintCount()
    ])
      .then((result: (Footprint[] | number)[]): void => {
        const footprints: Footprint[] = result[0] as Footprint[];
        const count: number = result[1] as number;
        this.footprints = footprints;
        this.goodsList = this.convertFootprintsToGoods(footprints);
        this.footprintCount = count;
        this.uiState = footprints.length > 0
          ? BaseNetWorkListUiState.SUCCESS
          : BaseNetWorkListUiState.EMPTY;
      })
      .catch((): void => {
        this.uiState = BaseNetWorkListUiState.ERROR;
      });
  }

  /**
   * 是否显示清空操作
   * @returns {boolean} 是否显示
   */
  shouldShowClearAction(): boolean {
    return this.footprints.length > 0;
  }

  /**
   * 跳转商品详情
   * @param {number} goodsId - 商品 ID
   * @returns {void} 无返回值
   */
  toGoodsDetail(goodsId: number): void {
    GoodsNavigator.toDetail(goodsId);
  }

  /**
   * 显示清空弹窗
   * @returns {void} 无返回值
   */
  showClearDialogModal(): void {
    this.showClearDialog = true;
  }

  /**
   * 隐藏清空弹窗
   * @returns {void} 无返回值
   */
  hideClearDialogModal(): void {
    this.showClearDialog = false;
  }

  /**
   * 确认清空足迹
   * @returns {void} 无返回值
   */
  confirmClearAll(): void {
    this.repository.clearAllFootprints()
      .then((): void => {
        this.hideClearDialogModal();
        this.loadFootprints();
      })
      .catch((): void => {
        this.hideClearDialogModal();
      });
  }

  /**
   * 将足迹列表转换为商品列表
   * @param {Footprint[]} footprints - 足迹列表
   * @returns {Goods[]} 商品列表
   */
  private convertFootprintsToGoods(footprints: Footprint[]): Goods[] {
    return footprints.map((item: Footprint): Goods => {
      const goods = new Goods();
      goods.id = item.goodsId;
      goods.title = item.goodsName;
      goods.subTitle = item.goodsSubTitle ?? "";
      goods.mainPic = item.goodsMainPic;
      goods.price = item.goodsPrice;
      goods.sold = item.goodsSold;
      return goods;
    });
  }
}
