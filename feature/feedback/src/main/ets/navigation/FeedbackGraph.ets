import { RouteBuild, RouteGraph } from "navigation";
import { FeedbackRoutes } from "navigation/src/main/ets/feedback/FeedbackRoutes";
import { FeedbackListNav } from "./FeedbackListNav";
import { FeedbackSubmitNav } from "./FeedbackSubmitNav";

/**
 * @file 反馈模块导航图
 * @author Joker.X
 */
export class FeedbackGraph implements RouteGraph {
  /**
   * 注册反馈模块导航路由
   */
  register(): void {
    RouteBuild.register(FeedbackRoutes.List, wrapBuilder(FeedbackListNav));
    RouteBuild.register(FeedbackRoutes.Submit, wrapBuilder(FeedbackSubmitNav));
  }
}
