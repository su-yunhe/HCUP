import { ColumnStart, P100 } from "designsystem";
import { Goods } from "model";
import { BreakpointState, getBreakpointState, getWindowSafeAreaState, WindowSafeAreaState } from "state";
import { AppNavDestination, BaseNetWorkView } from "ui";
import { GoodsBanner } from "../component/GoodsBanner";
import { GoodsDetailBottomBar } from "../component/GoodsDetailBottomBar";
import { GoodsInfoCard } from "../component/GoodsInfoCard";
import { GoodsShippingServiceCard } from "../component/GoodsShippingServiceCard";
import GoodsDetailViewModel from "../viewmodel/GoodsDetailViewModel";

/**
 * @file 商品详情页面视图
 * @author Joker.X
 */
@ComponentV2
export struct GoodsDetailPage {
  /**
   * 商品详情页面 ViewModel
   */
  @Local
  private vm: GoodsDetailViewModel = new GoodsDetailViewModel();
  /**
   * 当前窗口安全区状态
   */
  @Param
  private windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();
  /**
   * 屏幕断点状态
   */
  @Local
  private breakpointState: BreakpointState = getBreakpointState();

  /**
   * 构建商品详情页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      hideTitleBar: true,
      viewModel: this.vm,
      paddingValue: {
        left: this.windowSafeAreaState.leftInset,
        right: this.windowSafeAreaState.rightInset,
      }
    }) {
      BaseNetWorkView({
        uiState: this.vm.uiState,
        onRetry: (): void => this.vm.retryRequest(),
        content: (): void => this.GoodsDetailContent()
      });
    }
  }

  /**
   * 商品详情页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private GoodsDetailContent() {
    ColumnStart({ fillMaxSize: true }) {
      this.GoodsDetailList();
      GoodsDetailBottomBar();
    }
  }

  /**
   * 商品详情滚动列表
   * @returns {void} 无返回值
   */
  @Builder
  private GoodsDetailList(): void {
    List() {
      ListItem() {
        GoodsBanner({
          bannerList: this.vm.data?.goodsInfo?.pics ?? [],
          autoPlay: false,
          loop: false,
          imageFit: ImageFit.Cover
        });
      }

      ListItem() {
        GoodsInfoCard({
          goodsInfo: this.vm.data?.goodsInfo ?? new Goods(),
          coupons: this.vm.data?.coupon ?? []
        });
      }

      ListItem() {
        GoodsShippingServiceCard();
      }
    }
    .layoutWeight(1)
    .width(P100)
    .height(P100);
  }
}
