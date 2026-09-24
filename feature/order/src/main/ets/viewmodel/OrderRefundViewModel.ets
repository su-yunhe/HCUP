import { BaseNetWorkUiState, BaseNetWorkViewModel } from "base";
import { CommonRepository, OrderRepository } from "data";
import {
  Cart,
  CartGoodsSpec,
  DictDataRequest,
  DictDataResponse,
  DictItem,
  NetworkResponse,
  Order,
  OrderGoods,
  RefundOrderRequest
} from "model";
import { OrderIdParam, RefreshResult, getRouteParams, navigateBackWithResult } from "navigation";
import { OrderRoutes } from "navigation/src/main/ets/order/OrderRoutes";
import { RequestHelper } from "result";

/**
 * @file 订单退款页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class OrderRefundViewModel extends BaseNetWorkViewModel<Order> {
  /**
   * 订单仓库
   */
  private readonly repository: OrderRepository = new OrderRepository();
  /**
   * 公共仓库
   */
  private readonly commonRepository: CommonRepository = new CommonRepository();
  /**
   * 路由参数
   */
  private readonly routeParam: OrderIdParam | undefined = getRouteParams<OrderIdParam>(OrderRoutes.Refund);
  /**
   * 订单 ID
   */
  private readonly orderId: number = this.routeParam?.orderId ?? 0;
  /**
   * 订单商品列表（购物车结构）
   */
  @Trace
  cartList: Cart[] = [];
  /**
   * 退款原因弹窗显示状态
   */
  @Trace
  refundModalVisible: boolean = false;
  /**
   * 退款原因弹窗网络状态
   */
  @Trace
  refundReasonsUiState: BaseNetWorkUiState = BaseNetWorkUiState.LOADING;
  /**
   * 退款原因列表
   */
  @Trace
  refundReasonList: DictItem[] = [];
  /**
   * 选中的退款原因
   */
  @Trace
  selectedRefundReason: DictItem | null = null;

  /**
   * 请求订单详情数据
   * @returns {Promise<NetworkResponse<Order>>} 网络请求 Promise
   */
  protected requestRepository(): Promise<NetworkResponse<Order>> {
    return this.repository.getOrderInfo(this.orderId);
  }

  /**
   * 请求成功回调
   * @param {Order} data - 订单数据
   * @returns {void} 无返回值
   */
  protected onRequestSuccess(data: Order): void {
    this.cartList = this.convertOrderGoodsToCart(data);
    super.onRequestSuccess(data);
  }

  /**
   * 显示退款原因选择弹窗
   * @returns {void} 无返回值
   */
  showRefundModal(): void {
    this.refundModalVisible = true;
    this.loadRefundReasons();
  }

  /**
   * 隐藏退款原因选择弹窗
   * @returns {void} 无返回值
   */
  hideRefundModal(): void {
    this.refundModalVisible = false;
  }

  /**
   * 选择退款原因
   * @param {DictItem | null} reason - 退款原因
   * @returns {void} 无返回值
   */
  selectRefundReason(reason: DictItem | null): void {
    this.selectedRefundReason = reason;
  }

  /**
   * 加载退款原因字典数据
   * @returns {void} 无返回值
   */
  loadRefundReasons(): void {
    if (this.refundReasonsUiState === BaseNetWorkUiState.SUCCESS && this.refundReasonList.length > 0) {
      return;
    }
    const params: DictDataRequest = new DictDataRequest();
    params.types = ["orderRefundReason"];
    RequestHelper.repository<DictDataResponse>(this.commonRepository.getDictData(params))
      .toast(false)
      .start((): void => {
        this.refundReasonsUiState = BaseNetWorkUiState.LOADING;
      })
      .execute()
      .then((data: DictDataResponse): void => {
        this.refundReasonList = data.orderRefundReason ?? [];
        this.refundReasonsUiState = BaseNetWorkUiState.SUCCESS;
      })
      .catch((): void => {
        this.refundReasonList = [];
        this.refundReasonsUiState = BaseNetWorkUiState.ERROR;
      });
  }

  /**
   * 提交退款申请
   * @returns {void} 无返回值
   */
  submitRefundApplication(): void {
    if (!this.selectedRefundReason) {
      return;
    }
    const params: RefundOrderRequest = new RefundOrderRequest();
    params.orderId = this.orderId;
    params.reason = this.selectedRefundReason.name ?? "";
    RequestHelper.repository<boolean>(this.repository.refundOrder(params))
      .loading(true)
      .execute()
      .then((): void => {
        const result: RefreshResult = { refresh: true };
        navigateBackWithResult(result);
      });
  }

  /**
   * 将订单商品列表转换为购物车结构
   * @param {Order} order - 订单数据
   * @returns {Cart[]} 购物车列表
   */
  private convertOrderGoodsToCart(order: Order): Cart[] {
    return order.goodsList?.length ? this.buildCartList(order.goodsList) : [];
  }

  /**
   * 构建购物车列表
   * @param {OrderGoods[]} goodsList - 订单商品列表
   * @returns {Cart[]} 购物车列表
   */
  private buildCartList(goodsList: OrderGoods[]): Cart[] {
    const groupedMap = new Map<number, OrderGoods[]>();

    for (const goods of goodsList) {
      const existingList = groupedMap.get(goods.goodsId);
      if (existingList) {
        existingList.push(goods);
      } else {
        groupedMap.set(goods.goodsId, [goods]);
      }
    }

    const result: Cart[] = [];

    groupedMap.forEach((items: OrderGoods[], goodsId: number) => {
      const firstItem = items[0];

      const cart = new Cart();
      cart.goodsId = goodsId;
      cart.goodsName = firstItem.goodsInfo?.title ?? "";
      cart.goodsMainPic = firstItem.goodsInfo?.mainPic ?? "";

      const allSpecs: CartGoodsSpec[] = [];

      for (const orderGoods of items) {
        if (orderGoods.spec) {
          const cartSpec = new CartGoodsSpec();
          cartSpec.id = orderGoods.spec.id;
          cartSpec.goodsId = orderGoods.spec.goodsId;
          cartSpec.name = orderGoods.spec.name;
          cartSpec.price = orderGoods.spec.price;
          cartSpec.stock = orderGoods.spec.stock;
          cartSpec.count = orderGoods.count;
          cartSpec.images = orderGoods.spec.images;
          allSpecs.push(cartSpec);
        }
      }

      cart.spec = allSpecs;
      result.push(cart);
    });

    return result;
  }
}
