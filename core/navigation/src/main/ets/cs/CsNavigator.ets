import { navigateTo } from "../NavigationService";
import { CsRoutes } from "./CsRoutes";

/**
 * @file 客服模块导航封装
 * @author Joker.X
 */
export class CsNavigator {
  /**
   * 跳转到客服聊天
   * @returns {void} 无返回值
   */
  static toChat(): void {
    navigateTo(CsRoutes.Chat);
  }
}
