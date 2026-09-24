import { AppNavDestination, BaseNetWorkListView, GoodsGridItem, GoodsListItem, RefreshLayout, TitleWithLine } from "ui";
import { Goods } from "model";
import { HomeBanner } from "../component/HomeBanner";
import { HomeCategorySection } from "../component/HomeCategorySection";
import { HomeCouponSection } from "../component/HomeCouponSection";
import { HomeFlashSaleSection } from "../component/HomeFlashSaleSection";
import { HomeTopBar } from "../component/HomeTopBar";
import HomeViewModel from "../viewmodel/HomeViewModel";
import { P100, SpaceVerticalSmall } from "designsystem";
import { bp } from "state";
import { GoodsNavigator } from "navigation";

/**
 * @file 首页视图
 * @author Joker.X
 */
@ComponentV2
export struct HomePage {
  /**
   * 首页 ViewModel
   */
  @Local
  private vm: HomeViewModel = new HomeViewModel();
  /**
   * 列表滚动控制器，用于刷新同步
   */
  private listScroller: Scroller = new Scroller();

  /**
   * 构建首页
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      viewModel: this.vm,
      hideTitleBar: true,
    }) {
      HomeTopBar({
        onSearchTap: (): void => GoodsNavigator.toSearch()
      });
      BaseNetWorkListView({
        uiState: this.vm.uiState,
        onRetry: (): void => this.vm.retryRequest(),
        content: (): void => this.HomeContent()
      });
    }
  }

  /**
   * 首页内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private HomeContent() {
    RefreshLayout({
      loading: this.vm.isLoading,
      isEnableSlideUp: this.vm.isEnableSlideUp,
      scroller: this.listScroller,
      onRefresh: (direction): void => this.vm.onRefreshDirection(direction),
    }) {
      List({ space: 12, scroller: this.listScroller }) {
        ListItem() {
          HomeBanner({ bannerList: this.vm.pageData.banner ?? [] });
        }

        ListItem() {
          HomeCouponSection({ coupons: this.vm.pageData.coupon ?? [] });
        }

        ListItem() {
          HomeCategorySection({ categories: this.vm.pageData.category ?? [] });
        }

        ListItem() {
          HomeFlashSaleSection({
            goodsList: this.vm.pageData.flashSale ?? [],
            onGoodsClick: (id: number): void => {
              GoodsNavigator.toDetail(id);
            }
          });
        }

        ListItem() {
          TitleWithLine({ text: $r("app.string.recommend_goods") });
        }

        ListItem() {
          Grid() {
            ForEach(this.vm.pageData.recommend ?? [], (item: Goods): void => {
              GridItem() {
                GoodsListItem({
                  goods: item,
                  onItemClick: (id: number): void => {
                    GoodsNavigator.toDetail(id);
                  }
                });
              }
            }, (item: Goods): string => `${item.id}`);
          }
          .columnsTemplate(bp({ sm: "1fr", md: "1fr 1fr", lg: "1fr 1fr" }))
          .columnsGap($r("app.float.space_padding_small"))
          .rowsGap($r("app.float.space_padding_small"))
          .width(P100);
        }

        ListItem() {
          TitleWithLine({ text: $r("app.string.all_goods") });
        }

        ListItem() {
          Grid() {
            ForEach(this.vm.listData, (item: Goods): void => {
              GridItem() {
                GoodsGridItem({
                  goods: item,
                  onItemClick: (id: number): void => {
                    GoodsNavigator.toDetail(id);
                  }
                });
              }
            }, (item: Goods): string => `${item.id}`);
          }
          .columnsTemplate(bp({ sm: "1fr 1fr", md: "1fr 1fr 1fr", lg: "1fr 1fr 1fr 1fr" }))
          .columnsGap($r("app.float.space_padding_small"))
          .rowsGap($r("app.float.space_padding_small"))
          .width(P100);
        }

        SpaceVerticalSmall()

      }
      .edgeEffect(EdgeEffect.None)
      .padding($r("app.float.space_padding_medium"));
    }
  }
}
