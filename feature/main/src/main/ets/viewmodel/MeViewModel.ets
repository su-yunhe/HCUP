import { BaseViewModel } from "base";
import { FootprintRepository, OrderRepository } from "data";
import { Footprint, OrderCount, User } from "model";
import { RequestHelper } from "result";
import { getUserState, UserState } from "state";
import {
  CommonRoutes,
  CsRoutes,
  FeedbackRoutes,
  GoodsRoutes,
  MarketRoutes,
  OrderRoutes,
  UserRoutes,
  navigateTo
} from "navigation";
import { MeMenuItem } from "../model/MeMenuItem";
import { OrderStatusItem } from "../model/OrderStatusItem";

/**
 * @file 我的页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class MeViewModel extends BaseViewModel {
  /**
   * 全局用户状态
   */
  private readonly userState: UserState = getUserState();
  /**
   * 足迹仓库
   */
  private readonly footprintRepository: FootprintRepository = new FootprintRepository();
  /**
   * 订单仓库
   */
  private readonly orderRepository: OrderRepository = new OrderRepository();
  /**
   * 登录状态
   */
  @Trace
  isLoggedIn: boolean = false;
  /**
   * 用户信息
   */
  @Trace
  userInfo: User = new User();
  /**
   * 订单统计
   */
  @Trace
  orderCount: OrderCount = new OrderCount();
  /**
   * 最近足迹列表
   */
  @Trace
  recentFootprints: Footprint[] = [];
  /**
   * 功能菜单列表
   */
  readonly primaryMenus: MeMenuItem[] = [
    {
      title: $r("app.string.coupons"),
      icon: $r("app.media.ic_coupon_fill"),
      iconColor: $r("app.color.main_coupon_icon"),
      onClick: (): void => this.toCouponPage(),
      showDivider: true
    },
    {
      title: $r("app.string.shipping_address"),
      icon: $r("app.media.ic_location_fill"),
      iconColor: $r("app.color.main_address_icon"),
      onClick: (): void => this.toAddressListPage(),
      showDivider: true
    },
    {
      title: $r("app.string.online_customer_service"),
      icon: $r("app.media.ic_service_fill"),
      iconColor: $r("app.color.main_service_icon"),
      onClick: (): void => this.toChatPage(),
      showDivider: true
    },
    {
      title: $r("app.string.feedback"),
      icon: $r("app.media.ic_creative_fill"),
      iconColor: $r("app.color.main_feedback_icon"),
      onClick: (): void => this.toFeedbackPage(),
      showDivider: true
    },
    {
      title: $r("app.string.about_us"),
      icon: $r("app.media.ic_tip_fill"),
      iconColor: $r("app.color.main_about_icon"),
      onClick: (): void => this.toAboutPage(),
      showDivider: false
    }
  ];
  /**
   * 设置菜单列表
   */
  readonly secondaryMenus: MeMenuItem[] = [
    {
      title: $r("app.string.settings"),
      icon: $r("app.media.ic_set_fill"),
      iconColor: $r("app.color.main_settings_icon"),
      onClick: (): void => this.toSettingsPage(),
      showDivider: false
    }
  ];

  /**
   * 页面显示完成
   * @param {VisibilityChangeReason} reason - 可见性变化原因
   * @returns {void} 无返回值
   */
  onShown(reason: VisibilityChangeReason): void {
    super.onShown(reason);
    this.refreshPageData();
  }

  /**
   * 刷新页面数据
   * @returns {void} 无返回值
   */
  private refreshPageData(): void {
    this.syncUserState();
    this.loadRecentFootprints();
    this.loadOrderCount();
  }

  /**
   * 同步用户登录状态与信息
   * @returns {void} 无返回值
   */
  private syncUserState(): void {
    this.isLoggedIn = this.userState.isLoggedIn();
    this.userInfo = this.userState.getUserInfo();
  }

  /**
   * 加载最近足迹
   * @returns {void} 无返回值
   */
  private loadRecentFootprints(): void {
    this.footprintRepository.getRecentFootprints(8)
      .then((list: Footprint[]): void => {
        this.recentFootprints = list;
      })
      .catch((): void => {
        // 本地数据库读取失败时重置为空列表
        this.recentFootprints = [];
      });
  }

  /**
   * 获取订单统计数据
   * @returns {void} 无返回值
   */
  private loadOrderCount(): void {
    if (!this.isLoggedIn) {
      this.orderCount = new OrderCount();
      return;
    }
    RequestHelper.repository<OrderCount>(this.orderRepository.getUserOrderCount())
      .toast(false)
      .execute()
      .then((data: OrderCount): void => {
        this.orderCount = new OrderCount(data);
      })
      .catch((): void => {
        // 请求失败时重置统计数据，避免脏数据
        this.orderCount = new OrderCount();
      });
  }

  /**
   * 获取展示用昵称
   * @returns {ResourceStr} 展示昵称
   */
  getDisplayName(): ResourceStr {
    if (this.isLoggedIn && this.userInfo.nickName) {
      return this.userInfo.nickName;
    }
    return $r("app.string.not_logged_in");
  }

  /**
   * 是否有手机号可展示
   * @returns {boolean} 是否展示手机号
   */
  hasPhone(): boolean {
    return this.isLoggedIn && !!this.userInfo.phone;
  }

  /**
   * 获取头像文字（无头像时使用）
   * @returns {string} 头像文字
   */
  getAvatarText(): string {
    if (this.userInfo.nickName) {
      return this.userInfo.nickName.substring(0, 1);
    }
    return "未";
  }

  /**
   * 是否存在头像地址
   * @returns {boolean} 是否有头像
   */
  hasAvatar(): boolean {
    return this.isLoggedIn && !!this.userInfo.avatarUrl;
  }

  /**
   * 获取订单状态列表
   * @returns {OrderStatusItem[]} 订单状态列表
   */
  getOrderStatusItems(): OrderStatusItem[] {
    return [
      {
        icon: $r("app.media.ic_pay"),
        label: $r("app.string.pending_payment"),
        count: this.orderCount.pendingPayment,
        tabIndex: 1
      },
      {
        icon: $r("app.media.ic_receipt"),
        label: $r("app.string.pending_shipment"),
        count: this.orderCount.pendingShipment,
        tabIndex: 2
      },
      {
        icon: $r("app.media.ic_logistics"),
        label: $r("app.string.pending_receipt"),
        count: this.orderCount.pendingReceive,
        tabIndex: 3
      },
      {
        icon: $r("app.media.ic_message"),
        label: $r("app.string.pending_review"),
        count: this.orderCount.pendingReview,
        tabIndex: 4
      },
      {
        icon: $r("app.media.ic_refund"),
        label: $r("app.string.refund_after_sale"),
        // 退款中 + 已退款合并展示
        count: this.orderCount.refunding + this.orderCount.refunded,
        tabIndex: 5
      }
    ];
  }

  /**
   * 格式化徽标数量
   * @param {number} count - 原始数量
   * @returns {string} 展示文本
   */
  formatBadgeCount(count: number): string {
    if (count > 99) {
      return "99+";
    }
    return `${count}`;
  }

  /**
   * 用户资料点击
   * @returns {void} 无返回值
   */
  onHeadClick(): void {
    this.toProfilePage();
  }

  /**
   * 跳转到订单列表
   * @returns {void} 无返回值
   */
  toOrderListPage(): void {
    navigateTo(OrderRoutes.List);
  }

  /**
   * 跳转到指定状态的订单列表
   * @param {number} tabIndex - 订单标签索引
   * @returns {void} 无返回值
   */
  toOrderListByTab(tabIndex: number): void {
    // TODO: 订单列表页支持 tab 参数后再传递
    navigateTo(OrderRoutes.List);
  }

  /**
   * 跳转到商品详情
   * @param {number} goodsId - 商品ID
   * @returns {void} 无返回值
   */
  toGoodsDetailPage(goodsId: number): void {
    // TODO: 商品详情页支持 goodsId 参数后再传递
    navigateTo(GoodsRoutes.Detail);
  }

  /**
   * 跳转到用户足迹
   * @returns {void} 无返回值
   */
  toUserFootprintPage(): void {
    navigateTo(UserRoutes.Footprint);
  }

  /**
   * 跳转到收货地址列表
   * @returns {void} 无返回值
   */
  toAddressListPage(): void {
    navigateTo(UserRoutes.AddressList);
  }

  /**
   * 跳转到我的优惠券
   * @returns {void} 无返回值
   */
  toCouponPage(): void {
    navigateTo(MarketRoutes.Coupon);
  }

  /**
   * 跳转到用户资料页面
   * @returns {void} 无返回值
   */
  toProfilePage(): void {
    navigateTo(UserRoutes.Profile);
  }

  /**
   * 跳转到客服聊天页面
   * @returns {void} 无返回值
   */
  toChatPage(): void {
    navigateTo(CsRoutes.Chat);
  }

  /**
   * 跳转到意见反馈页面
   * @returns {void} 无返回值
   */
  toFeedbackPage(): void {
    navigateTo(FeedbackRoutes.List);
  }

  /**
   * 跳转到关于我们页面
   * @returns {void} 无返回值
   */
  toAboutPage(): void {
    navigateTo(CommonRoutes.About);
  }

  /**
   * 跳转到设置页面
   * @returns {void} 无返回值
   */
  toSettingsPage(): void {
    navigateTo(CommonRoutes.Settings);
  }
}
