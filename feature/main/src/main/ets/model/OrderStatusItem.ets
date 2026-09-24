/**
 * @file 订单状态展示模型
 * @author Joker.X
 */
export interface OrderStatusItem {
  /**
   * 图标资源
   */
  icon: Resource;

  /**
   * 标题文案
   */
  label: ResourceStr;

  /**
   * 徽标数量
   */
  count: number;

  /**
   * 对应的订单 Tab 索引
   */
  tabIndex: number;
}
