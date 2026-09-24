import { navigateTo } from "../NavigationService";
import { FeedbackRoutes } from "./FeedbackRoutes";

/**
 * @file 反馈模块导航封装
 * @author Joker.X
 */
export class FeedbackNavigator {
  /**
   * 跳转到反馈列表
   * @returns {void} 无返回值
   */
  static toList(): void {
    navigateTo(FeedbackRoutes.List);
  }

  /**
   * 跳转到提交反馈
   * @returns {void} 无返回值
   */
  static toSubmit(): void {
    navigateTo(FeedbackRoutes.Submit);
  }
}
