import { BaseNetWorkViewModel, BaseNetWorkUiState } from "base";
import { CartRepository, FootprintRepository, GoodsRepository, OrderCacheStoreRepository, PageRepository } from "data";
import {
  Cart,
  CartGoodsSpec,
  Footprint,
  Goods,
  GoodsDetail,
  GoodsIdRequest,
  GoodsSpec,
  NetworkResponse,
  SelectedGoods
} from "model";
import { getRouteParams, GoodsIdParam, OrderNavigator } from "navigation";
import { GoodsRoutes } from "navigation/src/main/ets/goods/GoodsRoutes";
import { RequestHelper } from "result";
import { ToastUtils } from "util";

/**
 * @file 商品详情页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class GoodsDetailViewModel extends BaseNetWorkViewModel<GoodsDetail> {
  /**
   * 顶部导航栏透明度（0-255）
   */
  @Trace
  topBarAlpha: number = 0;
  /**
   * 累计滚动距离
   */
  private totalScrollOffset: number = 0;
  /**
   * 是否显示规格选择弹窗
   */
  @Trace
  showSpecSelectModal: boolean = false;
  /**
   * 规格列表数据
   */
  @Trace
  specList: GoodsSpec[] = [];
  /**
   * 规格列表网络请求状态
   */
  @Trace
  specUiState: BaseNetWorkUiState = BaseNetWorkUiState.LOADING;
  /**
   * 当前选中的规格
   */
  @Trace
  selectedSpec: GoodsSpec | null = null;
  /**
   * 页面仓库
   */
  private readonly pageRepository: PageRepository = new PageRepository();
  /**
   * 商品仓库
   */
  private readonly goodsRepository: GoodsRepository = new GoodsRepository();
  /**
   * 足迹仓库
   */
  private readonly footprintRepository: FootprintRepository = new FootprintRepository();
  /**
   * 订单缓存本地存储仓库
   */
  private readonly orderCacheStoreRepository: OrderCacheStoreRepository = new OrderCacheStoreRepository();
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

  /**
   * 请求成功回调
   * @param {GoodsDetail} data - 商品详情数据
   * @returns {void} 无返回值
   */
  protected onRequestSuccess(data: GoodsDetail): void {
    super.onRequestSuccess(data);
    this.addToFootprint(data.goodsInfo);
  }

  /**
   * 加载商品规格
   */
  loadGoodsSpecs() {
    // 如果 ui 状态为成功，则不重复加载
    if (this.specUiState === BaseNetWorkUiState.SUCCESS) {
      return;
    }

    const params: GoodsIdRequest = new GoodsIdRequest();
    params.goodsId = this.goodsId;
    RequestHelper.repository <GoodsSpec[]>(this.goodsRepository.getGoodsSpecList(params))
      .toast(false)
      .start(() => {
        this.specUiState = BaseNetWorkUiState.LOADING;
      })
      .execute()
      .then((data: GoodsSpec[]) => {
        this.specList = data;
        this.specUiState = BaseNetWorkUiState.SUCCESS;
      })
      .catch(() => {
        this.specUiState = BaseNetWorkUiState.ERROR;
      });
  }

  /**
   * 选择规格
   * @param {GoodsSpec} spec - 选中的规格
   */
  selectSpec(spec: GoodsSpec): void {
    // 如果点击的是已选中的规格，则取消选择
    if (this.selectedSpec?.id === spec.id) {
      this.selectedSpec = null;
    } else {
      this.selectedSpec = spec;
    }
  }

  /**
   * 加入购物车
   * @param {SelectedGoods} selectedGoods - 已选商品信息
   */
  async addToCart(selectedGoods: SelectedGoods): Promise<void> {
    const cartRepository = new CartRepository();

    // 检查购物车中是否已存在该商品
    const existingCart = await cartRepository.getCartByGoodsId(selectedGoods.goodsId);

    if (existingCart && selectedGoods.spec) {
      // 商品已存在，检查是否有相同规格
      const existingSpec = existingCart.spec.find(s => s.id === selectedGoods.spec?.id);

      if (existingSpec) {
        // 规格已存在，更新数量
        const newCount = existingSpec.count + selectedGoods.count;
        await cartRepository.updateCartSpecCount(selectedGoods.goodsId, selectedGoods.spec.id, newCount);
      } else {
        // 规格不存在，添加新规格
        const newSpec = new CartGoodsSpec();
        newSpec.id = selectedGoods.spec.id;
        newSpec.goodsId = selectedGoods.goodsId;
        newSpec.name = selectedGoods.spec.name;
        newSpec.price = selectedGoods.spec.price;
        newSpec.stock = selectedGoods.spec.stock;
        newSpec.count = selectedGoods.count;
        newSpec.images = selectedGoods.spec.images;
        existingCart.spec.push(newSpec);
        await cartRepository.updateCart(existingCart);
      }
    } else {
      // 商品不存在，创建新的购物车项
      const newCart = new Cart();
      newCart.goodsId = selectedGoods.goodsId;
      newCart.goodsName = selectedGoods.goodsInfo?.title ?? "";
      newCart.goodsMainPic = selectedGoods.goodsInfo?.mainPic ?? "";

      if (selectedGoods.spec) {
        const newSpec = new CartGoodsSpec();
        newSpec.id = selectedGoods.spec.id;
        newSpec.goodsId = selectedGoods.goodsId;
        newSpec.name = selectedGoods.spec.name;
        newSpec.price = selectedGoods.spec.price;
        newSpec.stock = selectedGoods.spec.stock;
        newSpec.count = selectedGoods.count;
        newSpec.images = selectedGoods.spec.images;
        newCart.spec = [newSpec];
      }

      await cartRepository.addToCart(newCart);
    }
    ToastUtils.showSuccess($r("app.string.add_to_cart_success"));
  }

  /**
   * 立即购买
   * @param {SelectedGoods} selectedGoods - 已选商品信息
   * @returns {Promise<void>} Promise<void>
   */
  async buyNow(selectedGoods: SelectedGoods): Promise<void> {
    // 保存已选商品列表到本地存储（存储为数组格式）
    await this.orderCacheStoreRepository.saveSelectedGoodsList([selectedGoods]);
    // 关闭规格选择弹窗
    this.dismissSpecModal();
    // 跳转到订单确认页面
    OrderNavigator.toConfirm();
  }

  /**
   * 更新顶部导航栏透明度
   * @param {number} scrollOffset - 当前滚动增量
   * @param {number | undefined} absoluteOffset - 当前滚动绝对距离
   * @returns {void} 无返回值
   */
  updateTopBarAlpha(scrollOffset: number, absoluteOffset?: number): void {
    if (absoluteOffset !== undefined) {
      this.topBarAlpha = this.clampAlpha(Math.floor(absoluteOffset));
      this.totalScrollOffset = this.topBarAlpha;
      return;
    }

    this.totalScrollOffset += scrollOffset;
    this.topBarAlpha = this.clampAlpha(Math.floor(this.totalScrollOffset));
    this.totalScrollOffset = this.topBarAlpha;
  }

  /**
   * 透明度取值修正
   * @param {number} alpha - 透明度
   * @returns {number} 修正后的透明度
   */
  private clampAlpha(alpha: number): number {
    if (alpha < 0) {
      return 0;
    }
    if (alpha > 255) {
      return 255;
    }
    return alpha;
  }

  /**
   * 显示规格选择弹窗
   * @returns {void} 无返回值
   */
  showSpecModal(): void {
    this.showSpecSelectModal = true;
    // 显示弹窗时加载规格数据
    this.loadGoodsSpecs();
  }

  /**
   * 关闭规格选择弹窗
   * @returns {void} 无返回值
   */
  dismissSpecModal(): void {
    this.showSpecSelectModal = false;
  }

  /**
   * 添加商品到足迹
   * @param {Goods} goods - 商品信息
   * @returns {void} 无返回值
   */
  private addToFootprint(goods: Goods): void {
    if (!goods.id) {
      return;
    }
    const footprint = new Footprint();
    footprint.goodsId = goods.id;
    footprint.goodsName = goods.title;
    footprint.goodsSubTitle = goods.subTitle;
    footprint.goodsMainPic = goods.mainPic;
    footprint.goodsPrice = goods.price;
    footprint.goodsSold = goods.sold;
    footprint.viewTime = Date.now();
    this.footprintRepository.addFootprint(footprint);
  }
}
