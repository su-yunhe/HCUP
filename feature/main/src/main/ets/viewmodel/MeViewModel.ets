import { BaseViewModel } from "base";
import { OrderRepository } from "data";
import { Footprint, OrderCount } from "model";
import { RequestHelper } from "result";
import { getUserState, UserState } from "state";
import {
  CommonNavigator,
  CsNavigator,
  FeedbackNavigator,
  MarketNavigator,
  UserNavigator
} from "navigation";
import { MeMenuItem } from "../model/MeMenuItem";

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
   * 订单仓库
   */
  private readonly orderRepository: OrderRepository = new OrderRepository();
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
      onClick: (): void => MarketNavigator.toCoupon(),
      showDivider: true
    },
    {
      title: $r("app.string.shipping_address"),
      icon: $r("app.media.ic_location_fill"),
      iconColor: $r("app.color.main_address_icon"),
      onClick: (): void => UserNavigator.toAddressList(),
      showDivider: true
    },
    {
      title: $r("app.string.online_customer_service"),
      icon: $r("app.media.ic_service_fill"),
      iconColor: $r("app.color.main_service_icon"),
      onClick: (): void => CsNavigator.toChat(),
      showDivider: true
    },
    {
      title: $r("app.string.feedback"),
      icon: $r("app.media.ic_creative_fill"),
      iconColor: $r("app.color.main_feedback_icon"),
      onClick: (): void => FeedbackNavigator.toList(),
      showDivider: true
    },
    {
      title: $r("app.string.about_us"),
      icon: $r("app.media.ic_tip_fill"),
      iconColor: $r("app.color.main_about_icon"),
      onClick: (): void => CommonNavigator.toAbout(),
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
      onClick: (): void => CommonNavigator.toSettings(),
      showDivider: false
    }
  ];

  /**
   * 页面出现前
   * @returns {void} 无返回值
   */
  aboutToAppear(): void {
    this.userState.refreshUserInfo();
  }

  /**
   * 用户订单统计
   * @returns {void} 无返回值
   */
  getUserOrderStatistics(): void {
    if (!this.userState.isLoggedIn()) {
      return;
    }
    RequestHelper.repository<OrderCount>(this.orderRepository.getUserOrderCount())
      .toast(false)
      .execute()
      .then((data: OrderCount): void => {
        this.orderCount = OrderCount.fromResponse(data);
      });
  }

}
