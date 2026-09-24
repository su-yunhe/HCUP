import { BaseNetWorkListViewModel } from "base";
import { OrderRepository } from "data";
import { Cart, CartGoodsSpec, Order, OrderGoods, OrderPageRequest, NetworkPageData, NetworkResponse } from "model";
import { GoodsNavigator, OrderNavigator } from "navigation";

/**
 * @file 订单列表页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class OrderListViewModel extends BaseNetWorkListViewModel<Order> {
  /**
   * 订单仓库
   */
  private readonly repository: OrderRepository = new OrderRepository();
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
   * 再次购买商品列表
   */
  @Trace
  rebuyCartList: Cart[] = [];
  /**
   * 再次购买当前订单
   */
  @Trace
  rebuyCurrentOrder: Order | null = null;
  /**
   * 商品评论商品列表
   */
  @Trace
  commentCartList: Cart[] = [];
  /**
   * 商品评论当前订单
   */
  @Trace
  commentCurrentOrder: Order | null = null;

  /**
   * 请求订单分页数据（暂时拉取全部状态）
   * @returns {Promise<NetworkResponse<NetworkPageData<Order>>>} 网络请求 Promise
   */
  protected requestListData(): Promise<NetworkResponse<NetworkPageData<Order>>> {
    const request: OrderPageRequest = new OrderPageRequest();
    request.page = this.currentPage;
    request.size = this.pageSize;
    return this.repository.getOrderPage(request);
  }

  /**
   * 跳转订单支付
   * @param {Order} order - 订单信息
   * @returns {void} 无返回值
   */
  toPay(order: Order): void {
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
   * @param {Order} order - 订单信息
   * @returns {void} 无返回值
   */
  handleRebuy(order: Order): void {
    this.rebuyCurrentOrder = null;
    this.rebuyCartList = [];

    const cartList: Cart[] = this.convertOrderGoodsToCart(order);
    if (cartList.length > 1) {
      this.rebuyCurrentOrder = order;
      this.rebuyCartList = cartList;
      this.showRebuyModal();
      return;
    }
    const goodsId: number = cartList[0]?.goodsId ?? 0;
    if (!goodsId) {
      return;
    }
    this.toGoodsDetailForRebuy(goodsId);
  }

  /**
   * 处理订单评价逻辑
   * @param {Order} order - 订单信息
   * @returns {void} 无返回值
   */
  handleOrderComment(order: Order): void {
    this.commentCurrentOrder = null;
    this.commentCartList = [];

    const cartList: Cart[] = this.convertOrderGoodsToCart(order);
    if (cartList.length > 1) {
      this.commentCurrentOrder = order;
      this.commentCartList = cartList;
      this.showCommentModal();
      return;
    }
    const goodsId: number = cartList[0]?.goodsId ?? 0;
    if (!goodsId) {
      return;
    }
    OrderNavigator.toComment(order.id, goodsId);
  }

  /**
   * 跳转到指定商品的订单评价页面
   * @param {number} goodsId - 商品 ID
   * @returns {void} 无返回值
   */
  toOrderCommentForGoods(goodsId: number): void {
    const order: Order | null = this.commentCurrentOrder;
    if (!order || !goodsId) {
      return;
    }
    OrderNavigator.toComment(order.id, goodsId);
    this.hideCommentModal();
  }

  /**
   * 跳转到指定商品详情页面（再次购买）
   * @param {number} goodsId - 商品 ID
   * @returns {void} 无返回值
   */
  toGoodsDetailForRebuy(goodsId: number): void {
    if (!goodsId) {
      return;
    }
    GoodsNavigator.toDetail(goodsId);
    this.hideRebuyModal();
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
}
