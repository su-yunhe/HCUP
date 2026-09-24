import { BusinessError } from "@kit.BasicServicesKit";
import { Pay } from "@cashier_alipay/cashiersdk";
import { BaseViewModel } from "base";
import { OrderRepository } from "data";
import { AlipayPayParams } from "model";
import {
  OrderPayParam,
  RefreshResult,
  getNavPathStack,
  getRouteParams,
  navigateBack,
  navigateBackWithResult
} from "navigation";
import { OrderRoutes } from "navigation/src/main/ets/order/OrderRoutes";
import { OrderNavigator } from "navigation/src/main/ets/order/OrderNavigator";
import { RequestHelper } from "result";
import { ToastUtils } from "util";

/**
 * @file 订单支付页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class OrderPayViewModel extends BaseViewModel {
  /**
   * 订单支付路由参数
   */
  private readonly routeParam: OrderPayParam | undefined = getRouteParams<OrderPayParam>(OrderRoutes.Pay);
  /**
   * 订单 ID
   */
  private readonly orderId: number = this.routeParam?.orderId ?? 0;
  /**
   * 来源
   */
  private readonly from: string | undefined = this.routeParam?.from;
  /**
   * 支付金额
   */
  @Trace
  payPrice: number = this.routeParam?.price ?? 0;
  /**
   * 订单仓库
   */
  private readonly orderRepository: OrderRepository = new OrderRepository();

  /**
   * 支付按钮点击事件
   * @returns {void} 无返回值
   */
  onPayClick(): void {
    this.startAlipayPayment();
  }

  /**
   * 发起支付宝支付
   * @returns {void} 无返回值
   */
  startAlipayPayment(): void {
    if (!this.orderId) {
      return;
    }
    const params: AlipayPayParams = { orderId: this.orderId };
    RequestHelper.repository<string>(this.orderRepository.alipayAppPay(params))
      .execute()
      .then((payInfo: string): void => {
        this.startAlipaySdk(payInfo);
      });
  }

  /**
   * 调起支付宝 SDK
   * @param {string} payInfo - 支付参数
   * @returns {void} 无返回值
   */
  private startAlipaySdk(payInfo: string): void {
    const navStack: NavPathStack | undefined = getNavPathStack();
    if (!navStack) {
      ToastUtils.showError($r("app.string.payment_failed"));
      return;
    }
    new Pay().payWithNav(payInfo, true, undefined, navStack)
      .then((result: Map<string, string>): void => {
        this.processAlipayResult(result);
      })
      .catch((error: BusinessError): void => {
        console.error(error.message);
        ToastUtils.showError($r("app.string.payment_failed"));
      });
  }

  /**
   * 处理支付宝支付结果
   * @param {Map<string, string>} result - 支付结果
   * @returns {void} 无返回值
   */
  processAlipayResult(result: Map<string, string>): void {
    const resultStatus: string | undefined = result.get("resultStatus");
    if (resultStatus === "9000") {
      ToastUtils.showSuccess($r("app.string.payment_success"));
      this.handleBackAfterPayment(true);
      return;
    }
    if (resultStatus === "6001") {
      ToastUtils.showError($r("app.string.payment_cancel"));
      this.handleBackAfterPayment(false);
      return;
    }
    ToastUtils.showError($r("app.string.payment_failed"));
    this.handleBackAfterPayment(false);
  }

  /**
   * 处理系统返回按钮点击
   * @returns {void} 无返回值
   */
  handleBackClick(): void {
    this.handleBackAfterPayment(false);
  }

  /**
   * 处理支付后的返回逻辑
   * @param {boolean} isPaySuccess - 是否支付成功
   * @returns {void} 无返回值
   */
  private handleBackAfterPayment(isPaySuccess: boolean): void {
    if (this.from === "confirm") {
      navigateBack();
      OrderNavigator.toDetail(this.orderId);
      return;
    }

    if (isPaySuccess) {
      const result: RefreshResult = { refresh: true };
      navigateBackWithResult(result);
      return;
    }

    navigateBack();
  }
}
