import { BaseNetWorkViewModel } from "base";
import { CartRepository, OrderCacheStoreRepository, OrderRepository, PageRepository } from "data";
import {
  Address,
  Cart,
  CartGoodsSpec,
  ConfirmOrder,
  Coupon,
  CreateOrderRequest,
  NetworkResponse,
  Order,
  SelectedGoods
} from "model";
import { OrderNavigator, UserNavigator, UserSelectAddressResult } from "navigation";
import { RequestHelper } from "result";
import { ContextUtil, ToastUtils } from "util";

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
   * 订单仓库
   */
  private readonly orderRepository: OrderRepository = new OrderRepository();
  /**
   * 购物车仓库
   */
  private readonly cartRepository: CartRepository = new CartRepository();
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
    // 先加载缓存数据
    this.loadOrderCache();
    // 再执行网络请求
    super.aboutToAppear();
  }

  /**
   * 从缓存加载订单数据
   * @returns {Promise<void>} Promise<void>
   */
  async loadOrderCache(): Promise<void> {
    // 1. 读取购物车缓存（仅购物车页面会存储）
    this.cachedCarts = await this.orderCacheStoreRepository.loadCarts();

    // 2. 读取已选商品列表
    this.selectedGoodsList = await this.orderCacheStoreRepository.loadSelectedGoodsList() ?? [];

    // 3. 购物车列表：优先从 cachedCarts 获取，没有则从 selectedGoodsList 转换
    if (this.cachedCarts && this.cachedCarts.length > 0) {
      this.cartList = this.cachedCarts;
    } else {
      this.cartList = this.convertSelectedGoodsToCartList(this.selectedGoodsList);
    }

    // 4. 清除缓存，避免重复使用
    await this.orderCacheStoreRepository.clearAll();

    // 5. 计算商品原价
    this.calculateOriginalPrice();
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
    this.couponModalVisible = true;
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
    UserNavigator.toAddressList(true)
      .then((result?: UserSelectAddressResult): void => {
        if (result?.address) {
          this.updateSelectedAddress(result.address);
        }
      });
  }

  /**
   * 提交订单点击事件
   * @returns {void} 无返回值
   */
  onSubmitOrderClick(): void {
    const addressId: number | undefined = this.data?.defaultAddress?.id;
    if (!addressId) {
      ToastUtils.showError($r("app.string.select_address"));
      return;
    }

    const title: string = this.getPurchaseTitle();
    const params: CreateOrderRequest = new CreateOrderRequest({
      data: {
        addressId,
        goodsList: this.selectedGoodsList,
        title: title.length > 0 ? title : undefined,
        remark: this.remark.length > 0 ? this.remark : undefined,
        couponId: this.selectedCoupon?.id
      }
    });

    RequestHelper.repository<Order>(this.orderRepository.createOrder(params))
      .execute()
      .then((order: Order): void => {
        if (this.isFromCart) {
          void this.deleteCartItems();
        }
        this.navigateToPayment(order);
      });
  }

  /**
   * 跳转到支付页面
   * @param {Order} order - 订单信息
   * @returns {void} 无返回值
   */
  private navigateToPayment(order: Order): void {
    const paymentPrice: number = order.price - order.discountPrice;
    OrderNavigator.toPay(order.id, paymentPrice, "confirm");
  }

  /**
   * 更新已选择的地址
   * @param {Address} address - 选择的地址
   * @returns {void} 无返回值
   */
  private updateSelectedAddress(address: Address): void {
    const currentData: ConfirmOrder = this.data ? new ConfirmOrder(this.data) : new ConfirmOrder();
    currentData.defaultAddress = address;
    this.data = currentData;
  }

  /**
   * 获取提交订单的标题
   * @returns {string} 标题文案
   */
  private getPurchaseTitle(): string {
    try {
      const titleRes: Resource = $r("app.string.purchase_goods");
      return ContextUtil.getUIAbilityCtx().resourceManager.getStringSync(titleRes.id);
    } catch (error) {
      return "";
    }
  }

  /**
   * 删除购物车中已下单的商品
   * @returns {Promise<void>} Promise<void>
   */
  async deleteCartItems(): Promise<void> {
    if (!this.cachedCarts || this.cachedCarts.length === 0) {
      return;
    }

    for (const cart of this.cachedCarts) {
      const goodsId = cart.goodsId;

      // 获取该商品所有的规格ID
      const specIds = new Set(cart.spec.map((s: CartGoodsSpec): number => s.id));

      // 判断是否需要删除整个商品
      const fullCart = await this.cartRepository.getCartByGoodsId(goodsId);

      if (fullCart) {
        // 所有规格是否都在订单中
        const allSpecIds = new Set(fullCart.spec.map((s: CartGoodsSpec): number => s.id));

        if (specIds.size === allSpecIds.size) {
          // 删除整个商品
          await this.cartRepository.removeFromCart(goodsId);
        } else {
          // 逐个删除规格
          for (const specId of specIds) {
            await this.cartRepository.removeSpecFromCart(goodsId, specId);
          }
        }
      }
    }
  }
}
