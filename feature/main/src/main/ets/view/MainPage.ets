import { Lottie } from "@jjr/lottie_component_v2";
import { AppNavDestination } from "ui";
import MainViewModel from "../viewmodel/MainViewModel";
import { HomePage } from "./HomePage";
import { CategoryPage } from "./CategoryPage";
import { CartPage } from "./CartPage";
import { MePage } from "./MePage";
import { ColumnCenter, P100, size, SpaceVerticalXSmall } from "designsystem";
import {
  bp, BreakpointState, getBreakpointState, getWindowSafeAreaState, WindowSafeAreaState
} from "state";

/**
 * @file 主页面视图
 * @author Joker.X
 */
@ComponentV2
export struct MainPage {
  /**
   * 主页面 ViewModel
   */
  @Local
  private vm: MainViewModel = new MainViewModel();
  /**
   * 窗口安全区状态
   */
  @Local
  private windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();
  /**
   * 屏幕断点状态
   */
  @Local
  private breakpointState: BreakpointState = getBreakpointState();

  /**
   * 构建主页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      hideTitleBar: true,
      viewModel: this.vm,
      safeAreaEnabled: false
    }) {
      this.MainContent();
    }
  }

  /**
   * 主页面内容视图，包含可左右滑动的页面与底部 Lottie 导航
   * @returns {void} 无返回值
   */
  @Builder
  private MainContent() {
    Tabs({
      index: this.vm.currentPageIndex,
      barPosition: this.breakpointState.isLG() ? BarPosition.Start : BarPosition.End
    }) {
      TabContent() {
        HomePage();
      }.tabBar(this.tabBarItem(0));

      TabContent() {
        CategoryPage();
      }.tabBar(this.tabBarItem(1));

      TabContent() {
        CartPage({ currentPageIndex: this.vm.currentPageIndex });
      }.tabBar(this.tabBarItem(2));

      TabContent() {
        MePage({ currentPageIndex: this.vm.currentPageIndex });
      }.tabBar(this.tabBarItem(3));
    }
    .width(P100)
    .height(P100)
    .barWidth(this.breakpointState.isLG() ? 96 : P100)
    .divider({ strokeWidth: 1, color: $r('app.color.border') })
    .backgroundColor($r("app.color.bg_white"))
    .cachedMaxCount(this.vm.tabItems.length, TabsCacheMode.CACHE_BOTH_SIDE)
    .barMode(BarMode.Fixed)
    .scrollable(true)
    .vertical(this.breakpointState.isLG())
    .onChange((index: number) => this.vm.updateCurrentPage(index))
    .onAnimationStart((_, targetIndex: number) => {
      this.vm.playSelectedAnimation(targetIndex);
    })
    .padding({ bottom: this.windowSafeAreaState.bottomInset });
  }

  /**
   * Tabs 的底部导航项
   * @param {number} index - 索引
   * @returns {void} 无返回值
   */
  @Builder
  private tabBarItem(index: number) {
    ColumnCenter() {
      Lottie({
        loop: false,
        autoPlay: this.vm.currentPageIndex === index,
        controller: this.vm.lottieControllers[index],
        animationData: this.vm.tabItems[index].animationData
      })
        .attributeModifier(size(bp({
          sm: 24,
          md: 28,
          lg: 32,
        })))
        .onAppear(() => this.vm.handleTabAppear(index));

      SpaceVerticalXSmall();

      Text(this.vm.tabItems[index].title)
        .fontSize(bp({
          sm: $r("app.float.body_medium"),
          md: $r("app.float.body_large"),
          lg: $r("app.float.headline_large")
        }))
        .fontColor(this.vm.currentPageIndex === index ?
          $r("app.color.primary") :
          $r("app.color.text_subtitle"))
        .textAlign(TextAlign.Center);
    };
  }
}
