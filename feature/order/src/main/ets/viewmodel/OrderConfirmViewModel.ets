import { BaseNetWorkUiState, BaseNetWorkViewModel } from "base";
import { CartRepository, OrderCacheStoreRepository, OrderRepository, PageRepository } from "data";
import {
  Address, Cart, CartGoodsSpec, ConfirmOrder, Coupon, CreateOrderRequest, Goods, GoodsSpec, NetworkResponse,
  Order, SelectedGoods
} from "model";
import { OrderNavigator, UserNavigator, UserSelectAddressResult } from "navigation";
import { RequestHelper } from "result";
import { ToastUtils } from "util";

enum PreparationState {
  IDLE,
  LOADING,
  SUCCESS,
  ERROR
}

class CreatedOrderReceipt {
  id: number;
  realPrice: number;

  constructor(id: number, realPrice: number) {
    this.id = id;
    this.realPrice = realPrice;
  }
}

/**
 * @file 订单确认页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class OrderConfirmViewModel extends BaseNetWorkViewModel<ConfirmOrder> {
  /**
   * 订单缓存本地存储仓库
   */
  private readonly orderCacheStoreRepository: OrderCacheStoreRepository = new OrderCacheStoreRepository();
  /**
   * 页面仓库
   */
  private readonly pageRepository: PageRepository = new PageRepository();
  /**
   * 购物车仓库
   */
  private readonly cartRepository: CartRepository = new CartRepository();
  private readonly orderRepository: OrderRepository = new OrderRepository();
  private initialized: boolean = false;
  private cacheState: PreparationState = PreparationState.IDLE;
  private pageState: PreparationState = PreparationState.IDLE;
  private addressChosen: boolean = false;
  private visible: boolean = false;
  private disposed: boolean = false;
  private pendingAutoPay: boolean = false;
  private payNavigationInProgress: boolean = false;
  private receipt: CreatedOrderReceipt | null = null;
  /** UI and requests share the same current address. */
  @Trace
  selectedAddress: Address | null = null;
  @Trace
  submitting: boolean = false;
  /**
   * 从购物车来的商品项（仅购物车页面会存储）
   */
  cachedCarts: Cart[] | null = null;
  /**
   * 选中的商品列表（从缓存中获取）
   */
  @Trace
  selectedGoodsList: SelectedGoods[] = [];
  /**
   * 购物车列表（用于页面展示）
   * 优先从 cachedCarts 获取，没有则从 selectedGoodsList 转换
   */
  @Trace
  cartList: Cart[] = [];
  /**
   * 订单备注
   */
  @Trace
  remark: string = "";
  /**
   * 优惠券弹出层的显示状态
   */
  @Trace
  couponModalVisible: boolean = false;
  /**
   * 选中的优惠券
   */
  @Trace
  selectedCoupon: Coupon | null = null;
  /**
   * 商品原价（单位：元）
   */
  @Trace
  originalPrice: number = 0;
  /**
   * 优惠券折扣金额（单位：元）
   */
  @Trace
  discountAmount: number = 0;
  /**
   * 最终价格（单位：元）
   */
  @Trace
  totalPrice: number = 0;

  /**
   * 请求确认订单页面数据
   * @returns {Promise<NetworkResponse<ConfirmOrder>>} 确认订单页面数据
   */
  protected requestRepository(): Promise<NetworkResponse<ConfirmOrder>> {
    return this.pageRepository.getConfirmOrder();
  }

  /**
   * 页面出现时加载数据
   * @returns {void} 无返回值
   */
  aboutToAppear(): void {
    if (this.initialized || this.disposed) {
      return;
    }
    this.initialized = true;
    this.loadOrderCache();
    super.aboutToAppear();
  }

  onShown(reason: VisibilityChangeReason): void {
    if (this.disposed) {
      return;
    }
    this.visible = true;
    this.payNavigationInProgress = false;
    if (this.pendingAutoPay) {
      this.navigateToCreatedOrder();
    }
  }

  onHidden(reason: VisibilityChangeReason): void {
    this.visible = false;
  }

  aboutToBeDeleted(): void {
    this.disposed = true;
    this.visible = false;
    this.pendingAutoPay = false;
  }

  protected onRequestStart(): void {
    if (!this.disposed) {
      this.pageState = PreparationState.LOADING;
      this.refreshReadyState();
    }
  }

  protected onRequestSuccess(data: ConfirmOrder): void {
    if (this.disposed) {
      return;
    }
    if (!data) {
      this.onRequestError();
      return;
    }
    this.data = data;
    if (!this.addressChosen) {
      const address = data.defaultAddress;
      this.selectedAddress = address && this.isPositiveNumber(address.id) ? new Address(address) : null;
    }
    this.pageState = PreparationState.SUCCESS;
    this.refreshReadyState();
  }

  protected onRequestError(): void {
    if (!this.disposed) {
      this.pageState = PreparationState.ERROR;
      this.refreshReadyState();
    }
  }

  retryRequest(): void {
    if (this.disposed) {
      return;
    }
    if (this.cacheState === PreparationState.ERROR) {
      this.loadOrderCache();
    }
    if (this.pageState === PreparationState.ERROR) {
      this.executeRequest();
    }
  }

  private refreshReadyState(): void {
    if (this.disposed) {
      return;
    }
    if (this.cacheState === PreparationState.ERROR || this.pageState === PreparationState.ERROR) {
      this.uiState = BaseNetWorkUiState.ERROR;
    } else if (this.cacheState === PreparationState.SUCCESS && this.pageState === PreparationState.SUCCESS) {
      this.uiState = BaseNetWorkUiState.SUCCESS;
    } else {
      this.uiState = BaseNetWorkUiState.LOADING;
    }
  }

  get canSubmit(): boolean {
    return !this.disposed && !this.submitting && this.uiState === BaseNetWorkUiState.SUCCESS &&
      this.hasValidGoods();
  }

  /**
   * 从缓存加载订单数据
   * @returns {Promise<void>} Promise<void>
   */
  async loadOrderCache(): Promise<void> {
    if (this.disposed || this.cacheState === PreparationState.LOADING ||
      this.cacheState === PreparationState.SUCCESS) {
      return;
    }
    this.cacheState = PreparationState.LOADING;
    this.refreshReadyState();
    try {
      // Publish both reads together; failed reads leave the cache available for retry.
      const carts = await this.orderCacheStoreRepository.loadCarts();
      const goods = await this.orderCacheStoreRepository.loadSelectedGoodsList() ?? [];
      if (this.disposed) {
        return;
      }
      this.cachedCarts = carts;
      this.selectedGoodsList = goods;
      this.cartList = carts && carts.length > 0 ? carts : this.convertSelectedGoodsToCartList(goods);
      this.calculateOriginalPrice();
      this.cacheState = PreparationState.SUCCESS;
      this.refreshReadyState();
      // Once published, this draft must not be replaced by a partially cleared cache.
      try {
        await this.orderCacheStoreRepository.clearAll();
      } catch (error) {
        console.error(`[OrderConfirm] clear consumed cache failed: ${String(error)}`);
      }
    } catch (error) {
      console.error(`[OrderConfirm] read order cache failed: ${String(error)}`);
      if (!this.disposed) {
        this.cacheState = PreparationState.ERROR;
        this.refreshReadyState();
      }
    }
  }

  /**
   * 将已选商品列表转换为购物车列表
   * @param {SelectedGoods[]} goodsList 已选商品列表
   * @returns {Cart[]} 购物车列表
   */
  private convertSelectedGoodsToCartList(goodsList: SelectedGoods[]): Cart[] {
    // 按商品ID分组
    const groupedMap = new Map<number, SelectedGoods[]>();

    for (const goods of goodsList) {
      const existingList = groupedMap.get(goods.goodsId);
      if (existingList) {
        existingList.push(goods);
      } else {
        groupedMap.set(goods.goodsId, [goods]);
      }
    }

    // 为每个商品ID创建一个Cart对象
    const result: Cart[] = [];

    groupedMap.forEach((items: SelectedGoods[], goodsId: number) => {
      const firstItem = items[0];

      const cart = new Cart();
      cart.goodsId = goodsId;
      cart.goodsName = firstItem.goodsInfo?.title ?? "";
      cart.goodsMainPic = firstItem.goodsInfo?.mainPic ?? "";

      // 收集该商品的所有规格
      const allSpecs: CartGoodsSpec[] = [];

      for (const selectedItem of items) {
        // 如果有规格信息，转换为CartGoodsSpec并添加
        if (selectedItem.spec) {
          const cartSpec = new CartGoodsSpec();
          cartSpec.id = selectedItem.spec.id;
          cartSpec.goodsId = selectedItem.spec.goodsId;
          cartSpec.name = selectedItem.spec.name;
          cartSpec.price = selectedItem.spec.price;
          cartSpec.stock = selectedItem.spec.stock;
          cartSpec.count = selectedItem.count;
          cartSpec.images = selectedItem.spec.images;
          allSpecs.push(cartSpec);
        }
      }

      cart.spec = allSpecs;
      result.push(cart);
    });

    return result;
  }

  /**
   * 是否从购物车来的
   * @returns {boolean} 是否从购物车来
   */
  get isFromCart(): boolean {
    return this.cachedCarts !== null && this.cachedCarts.length > 0;
  }

  /**
   * 购物车是否为空
   * @returns {boolean} 是否为空
   */
  get isEmpty(): boolean {
    return this.cartList.length === 0;
  }

  /**
   * 更新订单备注
   * @param {string} newRemark 新的备注内容
   * @returns {void} 无返回值
   */
  updateRemark(newRemark: string): void {
    this.remark = newRemark;
  }

  /**
   * 显示优惠券弹出层
   * @returns {void} 无返回值
   */
  showCouponModal(): void {
    if (!this.disposed && !this.submitting && !this.receipt) {
      this.couponModalVisible = true;
    }
  }

  /**
   * 隐藏优惠券弹出层
   * @returns {void} 无返回值
   */
  hideCouponModal(): void {
    this.couponModalVisible = false;
  }

  /**
   * 选择优惠券
   * @param {Coupon | null} coupon 选中的优惠券，null表示不使用优惠券
   * @returns {void} 无返回值
   */
  selectCoupon(coupon: Coupon | null): void {
    if (this.disposed || this.submitting || this.receipt) {
      return;
    }
    this.selectedCoupon = coupon;
    this.hideCouponModal();
    this.calculatePrices();
  }

  /**
   * 计算商品原价
   * @returns {void} 无返回值
   */
  private calculateOriginalPrice(): void {
    let price = 0;
    for (const cart of this.cartList) {
      for (const spec of cart.spec) {
        price += spec.price * spec.count;
      }
    }
    this.originalPrice = price;
    this.calculatePrices();
  }

  /**
   * 计算价格（包括优惠券折扣）
   * @returns {void} 无返回值
   */
  private calculatePrices(): void {
    let discountValue = 0;

    if (this.selectedCoupon && this.selectedCoupon.condition) {
      // 检查是否满足使用条件
      if (this.originalPrice >= this.selectedCoupon.condition.fullAmount) {
        discountValue = this.selectedCoupon.amount ?? 0;
      }
    }

    this.discountAmount = discountValue;
    this.totalPrice = Math.max(this.originalPrice - discountValue, 0);
  }

  /**
   * 跳转到地址选择页面
   * @returns {void} 无返回值
   */
  navigateToAddressSelection(): void {
    if (this.disposed || this.submitting || this.receipt) {
      return;
    }
    UserNavigator.toAddressList(true)
      .then((result?: UserSelectAddressResult): void => {
        if (!this.disposed && !this.submitting && !this.receipt && result?.address &&
          this.isPositiveNumber(result.address.id)) {
          this.selectedAddress = new Address(result.address);
          this.addressChosen = true;
        }
      })
      .catch((error: Error): void => {
        console.error(`[OrderConfirm] address selection failed: ${String(error)}`);
      });
  }

  /**
   * 提交订单点击事件
   * @returns {void} 无返回值
   */
  onSubmitOrderClick(): void {
    if (this.disposed || this.submitting) {
      return;
    }
    if (this.receipt) {
      this.navigateToCreatedOrder();
      return;
    }
    if (!this.canSubmit) {
      return;
    }
    if (!this.selectedAddress || !this.isPositiveNumber(this.selectedAddress.id)) {
      ToastUtils.showBottom($r("app.string.select_address"));
      return;
    }
    // Synchronous guard: even a second click before the first await cannot create another order.
    this.submitting = true;
    this.submitOrder();
  }

  private isPositiveNumber(value: number): boolean {
    return typeof value === "number" && Number.isFinite(value) && value > 0;
  }

  private hasValidGoods(): boolean {
    return this.selectedGoodsList.length > 0 && this.selectedGoodsList.every((goods: SelectedGoods): boolean =>
      this.isPositiveNumber(goods.goodsId) && !!goods.spec && this.isPositiveNumber(goods.spec.id) &&
        Number.isInteger(goods.count) && goods.count > 0);
  }

  private copySpec(source: GoodsSpec): GoodsSpec {
    const spec = new GoodsSpec(source);
    spec.images = source.images ? [...source.images] : source.images;
    return spec;
  }

  private copyPurchasedGoods(): SelectedGoods[] {
    return this.selectedGoodsList.map((source: SelectedGoods): SelectedGoods => {
      const goods = new SelectedGoods(source);
      goods.spec = source.spec ? this.copySpec(source.spec) : null;
      if (source.goodsInfo) {
        const info = new Goods(source.goodsInfo);
        info.pics = source.goodsInfo.pics ? [...source.goodsInfo.pics] : source.goodsInfo.pics;
        info.contentPics = source.goodsInfo.contentPics ? [...source.goodsInfo.contentPics] : source.goodsInfo.contentPics;
        info.specs = source.goodsInfo.specs ? source.goodsInfo.specs.map((spec: GoodsSpec): GoodsSpec =>
          this.copySpec(spec)) : source.goodsInfo.specs;
        goods.goodsInfo = info;
      }
      return goods;
    });
  }

  private async submitOrder(): Promise<void> {
    try {
      const request = new CreateOrderRequest({
        data: {
          addressId: this.selectedAddress!.id,
          goodsList: this.copyPurchasedGoods(),
          remark: this.remark,
          couponId: this.selectedCoupon?.id ?? null
        }
      });
      const fromCart = this.isFromCart;
      const order = await RequestHelper.repository<Order>(this.orderRepository.createOrder(request)).execute();
      // Validate the raw payload before any Order constructor can supply missing fields with zero.
      if (!order || !this.isPositiveNumber(order.id) || typeof order.realPrice !== "number" ||
        !Number.isFinite(order.realPrice) || order.realPrice < 0) {
        throw new Error("Invalid created order response");
      }
      this.receipt = new CreatedOrderReceipt(order.id, order.realPrice);
      if (fromCart) {
        this.deleteCartItems(request.data.goodsList).catch((error: Error): void => {
          console.error(`[OrderConfirm] cart cleanup failed: ${String(error)}`);
        });
      }
      if (!this.disposed) {
        this.pendingAutoPay = true;
        this.navigateToCreatedOrder();
      }
    } catch (error) {
      // A receipt is terminal even when a later UI operation fails.
      console.error(`[OrderConfirm] submit failed: ${String(error)}`);
      if (!this.disposed && !this.receipt) {
        ToastUtils.showError($r("app.string.order_submit_failed"));
      }
    } finally {
      if (!this.disposed) {
        this.submitting = false;
      }
    }
  }

  private navigateToCreatedOrder(): void {
    if (this.disposed || !this.visible || !this.receipt || this.payNavigationInProgress) {
      return;
    }
    this.pendingAutoPay = false;
    this.payNavigationInProgress = true;
    try {
      OrderNavigator.toPay(this.receipt.id, this.receipt.realPrice);
    } catch (error) {
      this.payNavigationInProgress = false;
      console.error(`[OrderConfirm] payment navigation failed: ${String(error)}`);
    }
  }

  /**
   * 删除购物车中已下单的商品
   * @returns {Promise<void>} Promise<void>
   */
  async deleteCartItems(purchasedGoods?: SelectedGoods[]): Promise<void> {
    if (!purchasedGoods && !this.isFromCart) {
      return;
    }
    const purchases = new Map<number, Set<number>>();
    for (const goods of purchasedGoods ?? this.copyPurchasedGoods()) {
      if (goods.spec) {
        let specIds = purchases.get(goods.goodsId);
        if (!specIds) {
          specIds = new Set<number>();
          purchases.set(goods.goodsId, specIds);
        }
        specIds.add(goods.spec.id);
      }
    }
    for (const entry of purchases) {
      const goodsId = entry[0];
      const purchasedIds = entry[1];
      try {
        const fullCart = await this.cartRepository.getCartByGoodsId(goodsId);
        if (!fullCart || fullCart.spec.length === 0) {
          continue;
        }
        if (fullCart.spec.every((spec: CartGoodsSpec): boolean => purchasedIds.has(spec.id))) {
          await this.cartRepository.removeFromCart(goodsId);
        } else {
          for (const spec of fullCart.spec) {
            if (purchasedIds.has(spec.id)) {
              try {
                await this.cartRepository.removeSpecFromCart(goodsId, spec.id);
              } catch (error) {
                console.error(`[OrderConfirm] cleanup ${goodsId}/${spec.id} failed: ${String(error)}`);
              }
            }
          }
        }
      } catch (error) {
        console.error(`[OrderConfirm] cleanup goods ${goodsId} failed: ${String(error)}`);
      }
    }
  }
}
