import { BaseNetWorkUiState, BaseNetWorkViewModel } from "base";
import { CommonRepository, OrderRepository } from "data";
import {
  CancelOrderRequest,
  Cart,
  CartGoodsSpec,
  DictDataRequest,
  DictDataResponse,
  DictItem,
  NetworkResponse,
  Order,
  OrderGoods
} from "model";
import { GoodsNavigator, OrderIdParam, OrderNavigator, getRouteParams } from "navigation";
import { OrderRoutes } from "navigation/src/main/ets/order/OrderRoutes";
import { RequestHelper } from "result";

/**
 * @file 订单详情页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class OrderDetailViewModel extends BaseNetWorkViewModel<Order> {
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
  private readonly routeParam: OrderIdParam | undefined = getRouteParams<OrderIdParam>(OrderRoutes.Detail);
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
   * 再次购买弹窗显示状态
   */
  @Trace
  rebuyModalVisible: boolean = false;
  /**
   * 商品评论弹窗显示状态
   */
  @Trace
  commentModalVisible: boolean = false;
  /**
   * 取消原因弹窗显示状态
   */
  @Trace
  cancelModalVisible: boolean = false;
  /**
   * 取消原因弹窗网络状态
   */
  @Trace
  cancelReasonsUiState: BaseNetWorkUiState = BaseNetWorkUiState.LOADING;
  /**
   * 取消原因列表
   */
  @Trace
  cancelReasonList: DictItem[] = [];
  /**
   * 选中的取消原因
   */
  @Trace
  selectedCancelReason: DictItem | null = null;
  /**
   * 确认收货弹窗显示状态
   */
  @Trace
  showConfirmDialog: boolean = false;

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
   * 跳转支付页面
   * @returns {void} 无返回值
   */
  toPay(): void {
    const order: Order = this.data ?? new Order();
    const payPrice: number = order.price - order.discountPrice;
    OrderNavigator.toPay(order.id, payPrice);
  }

  /**
   * 显示再次购买弹窗
   * @returns {void} 无返回值
   */
  showRebuyModal(): void {
    this.rebuyModalVisible = true;
  }

  /**
   * 隐藏再次购买弹窗
   * @returns {void} 无返回值
   */
  hideRebuyModal(): void {
    this.rebuyModalVisible = false;
  }

  /**
   * 显示商品评论弹窗
   * @returns {void} 无返回值
   */
  showCommentModal(): void {
    this.commentModalVisible = true;
  }

  /**
   * 隐藏商品评论弹窗
   * @returns {void} 无返回值
   */
  hideCommentModal(): void {
    this.commentModalVisible = false;
  }

  /**
   * 处理再次购买逻辑
   * @returns {void} 无返回值
   */
  handleRebuy(): void {
    if (this.cartList.length > 1) {
      this.showRebuyModal();
      return;
    }
    const goodsId: number = this.getFirstCartGoodsId();
    if (!goodsId) {
      return;
    }
    this.toGoodsDetail(goodsId);
  }

  /**
   * 处理订单评价逻辑
   * @returns {void} 无返回值
   */
  handleOrderComment(): void {
    if (this.cartList.length > 1) {
      this.showCommentModal();
      return;
    }
    const orderId: number = this.data?.id ?? 0;
    const goodsId: number = this.getFirstCartGoodsId();
    if (!orderId || !goodsId) {
      return;
    }
    OrderNavigator.toComment(orderId, goodsId);
  }

  /**
   * 跳转商品详情页面（再次购买）
   * @param {number} goodsId - 商品 ID
   * @returns {void} 无返回值
   */
  toGoodsDetail(goodsId: number): void {
    if (!goodsId) {
      return;
    }
    this.hideRebuyModal();
    GoodsNavigator.toDetail(goodsId);
  }

  /**
   * 跳转订单评价页面（指定商品）
   * @param {number} goodsId - 商品 ID
   * @returns {void} 无返回值
   */
  toOrderCommentForGoods(goodsId: number): void {
    const orderId: number = this.data?.id ?? 0;
    if (!orderId || !goodsId) {
      return;
    }
    this.hideCommentModal();
    OrderNavigator.toComment(orderId, goodsId);
  }

  /**
   * 显示取消原因选择弹窗
   * @returns {void} 无返回值
   */
  showCancelModal(): void {
    this.cancelModalVisible = true;
    this.loadCancelReasons();
  }

  /**
   * 隐藏取消原因选择弹窗
   * @returns {void} 无返回值
   */
  hideCancelModal(): void {
    this.cancelModalVisible = false;
  }

  /**
   * 选择取消原因
   * @param {DictItem} reason - 取消原因
   * @returns {void} 无返回值
   */
  selectCancelReason(reason: DictItem): void {
    this.selectedCancelReason = reason;
  }

  /**
   * 加载取消原因字典数据
   * @returns {void} 无返回值
   */
  loadCancelReasons(): void {
    if (this.cancelReasonsUiState === BaseNetWorkUiState.SUCCESS && this.cancelReasonList.length > 0) {
      return;
    }
    const params: DictDataRequest = new DictDataRequest();
    params.types = ["orderCancelReason"];
    RequestHelper.repository<DictDataResponse>(this.commonRepository.getDictData(params))
      .toast(false)
      .start((): void => {
        this.cancelReasonsUiState = BaseNetWorkUiState.LOADING;
      })
      .execute()
      .then((data: DictDataResponse): void => {
        this.cancelReasonList = data.orderCancelReason ?? [];
        this.cancelReasonsUiState = BaseNetWorkUiState.SUCCESS;
      })
      .catch((): void => {
        this.cancelReasonList = [];
        this.cancelReasonsUiState = BaseNetWorkUiState.ERROR;
      });
  }

  /**
   * 确认取消订单
   * @returns {void} 无返回值
   */
  confirmCancelOrder(): void {
    const params: CancelOrderRequest = new CancelOrderRequest();
    params.orderId = this.orderId;
    params.remark = this.selectedCancelReason?.name ?? "";
    RequestHelper.repository<boolean>(this.repository.cancelOrder(params))
      .loading(true)
      .execute()
      .then((): void => this.retryRequest());
  }

  /**
   * 显示确认收货弹窗
   * @returns {void} 无返回值
   */
  showConfirmReceiveDialog(): void {
    this.showConfirmDialog = true;
  }

  /**
   * 隐藏确认收货弹窗
   * @returns {void} 无返回值
   */
  hideConfirmReceiveDialog(): void {
    this.showConfirmDialog = false;
  }

  /**
   * 确认收货订单
   * @returns {void} 无返回值
   */
  confirmReceiveOrder(): void {
    RequestHelper.repository<boolean>(this.repository.confirmReceive(this.orderId))
      .loading(true)
      .execute()
      .then((): void => {
        this.retryRequest();
        this.hideConfirmReceiveDialog();
      });
  }

  /**
   * 将订单商品转换为购物车列表
   * @param {Order} order - 订单信息
   * @returns {Cart[]} 购物车列表
   */
  private convertOrderGoodsToCart(order: Order): Cart[] {
    const goodsList: OrderGoods[] = order.goodsList ?? [];
    if (goodsList.length === 0) {
      return [];
    }

    const groupedMap = new Map<number, OrderGoods[]>();
    for (const goods of goodsList) {
      const exists = groupedMap.get(goods.goodsId);
      if (exists) {
        exists.push(goods);
      } else {
        groupedMap.set(goods.goodsId, [goods]);
      }
    }

    const result: Cart[] = [];
    groupedMap.forEach((items: OrderGoods[], goodsId: number): void => {
      const firstItem: OrderGoods = items[0];
      const cart = new Cart();
      cart.goodsId = goodsId;
      cart.goodsName = firstItem.goodsInfo?.title ?? "";
      cart.goodsMainPic = firstItem.goodsInfo?.mainPic ?? "";

      const specs: CartGoodsSpec[] = [];
      for (const orderGoods of items) {
        if (orderGoods.spec) {
          const spec = new CartGoodsSpec();
          spec.id = orderGoods.spec.id;
          spec.goodsId = orderGoods.spec.goodsId;
          spec.name = orderGoods.spec.name;
          spec.price = orderGoods.spec.price;
          spec.stock = orderGoods.spec.stock;
          spec.count = orderGoods.count;
          spec.images = orderGoods.spec.images;
          specs.push(spec);
        }
      }

      cart.spec = specs;
      result.push(cart);
    });

    return result;
  }

  /**
   * 获取购物车第一件商品 ID
   * @returns {number} 商品 ID
   */
  private getFirstCartGoodsId(): number {
    const cart: Cart | undefined = this.cartList[0];
    return cart?.goodsId ?? 0;
  }
}
