import { ColumnStart, P100, P50, RowStartTop, SpaceVerticalMedium } from "designsystem";
import { Goods } from "model";
import { navigateBack } from "navigation";
import { BreakpointState, getBreakpointState, getWindowSafeAreaState, WindowSafeAreaState } from "state";
import { AppNavDestination, BaseNetWorkView } from "ui";
import { SpecSelectModal } from "ui/src/main/ets/component/modal/SpecSelectModal";
import { GoodsBanner } from "../component/GoodsBanner";
import { GoodsDetailBottomBar } from "../component/GoodsDetailBottomBar";
import { GoodsCommentsCard } from "../component/GoodsCommentsCard";
import { GoodsInfoCard } from "../component/GoodsInfoCard";
import { GoodsShippingServiceCard } from "../component/GoodsShippingServiceCard";
import GoodsDetailViewModel from "../viewmodel/GoodsDetailViewModel";
import { GoodsDetailRichHeader } from "../component/GoodsDetailRichHeader";
import { GoodsDetailRichImageItem } from "../component/GoodsDetailRichImageItem";
import { GoodsDetailTopBar } from "../component/GoodsDetailTopBar";

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
   * 列表滚动控制器
   */
  private listScroller: Scroller = new Scroller();
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
    Stack({ alignContent: Alignment.TopStart }) {
      if (this.breakpointState.isLG()) {
        this.GoodsDetailLargeLayout();
      } else {
        this.GoodsDetailSmallLayout();
      }

      GoodsDetailTopBar({
        topBarAlpha: this.breakpointState.isLG() ? 0 : this.vm.topBarAlpha,
        topInset: this.windowSafeAreaState.topInset,
        onBackClick: (): void => navigateBack()
      });

      // 规格选择弹窗
      SpecSelectModal({
        visible: this.vm.showSpecSelectModal,
        onDismiss: (): void => this.vm.dismissSpecModal(),
        goods: this.vm.data?.goodsInfo ?? null,
        uiState: this.vm.specUiState,
        specList: this.vm.specList,
        selectedSpec: this.vm.selectedSpec,
        onSpecSelected: (spec): void => this.vm.selectSpec(spec),
        onAddToCart: async (selectedGoods): Promise<void> => await this.vm.addToCart(selectedGoods),
        onBuyNow: (selectedGoods): void => {
          this.vm.buyNow(selectedGoods);
        },
        onRetry: (): void => this.vm.loadGoodsSpecs()
      });
    }
  }

  /**
   * 小屏商品详情布局
   * @returns {void} 无返回值
   */
  @Builder
  private GoodsDetailSmallLayout(): void {
    ColumnStart({ fillMaxSize: true }) {
      this.GoodsDetailList(true);
      GoodsDetailBottomBar({
        onBuyNowClick: (): void => this.vm.showSpecModal(),
        onAddToCartClick: (): void => this.vm.showSpecModal()
      });
    }
  }

  /**
   * 大屏商品详情布局（左右等分）
   * @returns {void} 无返回值
   */
  @Builder
  private GoodsDetailLargeLayout(): void {
    RowStartTop({ fillMaxSize: true }) {
      ColumnStart({ widthValue: P50, heightValue: P100 }) {
        GoodsBanner({
          bannerList: this.vm.data?.goodsInfo?.pics ?? [],
          autoPlay: false,
          loop: false,
          imageFit: ImageFit.Cover,
          useSquareRatio: false
        });
      }

      ColumnStart({ widthValue: P50, heightValue: P100 }) {
        Blank().height(this.windowSafeAreaState.topInset ?? 0);
        this.GoodsDetailList(false);
        GoodsDetailBottomBar({
          onBuyNowClick: (): void => this.vm.showSpecModal(),
          onAddToCartClick: (): void => this.vm.showSpecModal()
        });
      }
    }
  }

  /**
   * 商品详情滚动列表
   * @param {boolean} showBanner - 是否展示轮播图
   * @returns {void} 无返回值
   */
  @Builder
  private GoodsDetailList(showBanner: boolean): void {
    List({ scroller: this.listScroller }) {
      if (showBanner) {
        ListItem() {
          GoodsBanner({
            bannerList: this.vm.data?.goodsInfo?.pics ?? [],
            autoPlay: false,
            loop: false,
            imageFit: ImageFit.Cover
          });
        }

        ListItem() {
          SpaceVerticalMedium();
        }
      } else {
        ListItem() {
          SpaceVerticalMedium();
        }
      }

      ListItem() {
        GoodsInfoCard({
          goodsInfo: this.vm.data?.goodsInfo ?? new Goods(),
          coupons: this.vm.data?.coupon ?? [],
          selectedSpec: this.vm.selectedSpec ?? undefined,
          onSpecClick: (): void => this.vm.showSpecModal(),
          onCouponClick: (): void => {
            // TODO: 实现优惠券弹窗功能
          }
        });
      }

      ListItem() {
        SpaceVerticalMedium();
      }

      ListItem() {
        GoodsShippingServiceCard();
      }

      ListItem() {
        SpaceVerticalMedium();
      }

      if (this.vm.data?.comment && this.vm.data.comment.length > 0) {
        ListItem() {
          GoodsCommentsCard({ comments: this.vm.data?.comment ?? [] });
        }

        ListItem() {
          SpaceVerticalMedium();
        }
      }

      if (this.vm.data?.goodsInfo?.contentPics && this.vm.data.goodsInfo.contentPics.length > 0) {
        ListItem() {
          GoodsDetailRichHeader();
        }

        ForEach(this.vm.data.goodsInfo.contentPics, (pic: string, index: number): void => {
          ListItem() {
            GoodsDetailRichImageItem({
              pic: pic,
              isLast: index === this.vm.data!.goodsInfo!.contentPics!.length - 1
            });
          }
        }, (pic: string, index: number): string => `${pic}-${index}`);
      }

      ListItem() {
        SpaceVerticalMedium();
      }
    }
    .layoutWeight(1)
    .width(P100)
    .height(P100)
    .onDidScroll((scrollOffset: number): void => {
      if (!this.breakpointState.isLG()) {
        this.onScrollChanged(scrollOffset);
      }
    });
  }

  /**
   * 列表滚动距离回调
   * @param {number} scrollOffset - 当前滚动距离
   * @returns {void} 无返回值
   */
  private onScrollChanged(scrollOffset: number): void {
    const offset = this.listScroller.currentOffset();
    if (offset) {
      this.vm.updateTopBarAlpha(scrollOffset, offset.yOffset);
    } else {
      this.vm.updateTopBarAlpha(scrollOffset);
    }
  }
}
