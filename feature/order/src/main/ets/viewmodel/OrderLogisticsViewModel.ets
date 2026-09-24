import { BaseNetWorkViewModel } from "base";
import { OrderRepository } from "data";
import { Logistics, NetworkResponse, Order } from "model";
import { OrderIdParam, getRouteParams } from "navigation";
import { OrderRoutes } from "navigation/src/main/ets/order/OrderRoutes";
import { RequestHelper } from "result";

/**
 * @file 订单物流页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class OrderLogisticsViewModel extends BaseNetWorkViewModel<Order> {
  /**
   * 订单仓库
   */
  private readonly repository: OrderRepository = new OrderRepository();
  /**
   * 路由参数
   */
  private readonly routeParam: OrderIdParam | undefined = getRouteParams<OrderIdParam>(OrderRoutes.Logistics);
  /**
   * 订单 ID
   */
  private readonly orderId: number = this.routeParam?.orderId ?? 0;
  /**
   * 订单物流信息
   */
  @Trace
  logisticsInfo: Logistics = new Logistics();

  /**
   * 请求订单详情数据
   * @returns {Promise<NetworkResponse<Order>>} 网络请求 Promise
   */
  protected requestRepository(): Promise<NetworkResponse<Order>> {
    return this.repository.getOrderInfo(this.orderId);
  }

  /**
   * 页面出现时加载数据
   * @returns {void} 无返回值
   */
  aboutToAppear(): void {
    this.loadOrderLogistics();
    super.aboutToAppear();
  }

  /**
   * 获取订单物流信息
   * @returns {void} 无返回值
   */
  loadOrderLogistics(): void {
    if (!this.orderId) {
      this.logisticsInfo = new Logistics();
      return;
    }
    RequestHelper.repository<Logistics>(this.repository.getOrderLogistics(this.orderId))
      .toast(false)
      .execute()
      .then((data: Logistics): void => {
        this.logisticsInfo = data;
      });
  }
}
