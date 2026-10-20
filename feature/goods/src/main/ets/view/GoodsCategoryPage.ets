import { BaseNetWorkListUiState } from "base";
import { Goods } from "model";
import { GoodsNavigator, navigateBack } from "navigation";
import { GoodsCategoryParam } from "navigation/src/main/ets/goods/GoodsParam";
import { AppNavDestination, EmptyData, EmptyNetwork, GoodsGridItem, GoodsListItem,
  SearchTopAppBar } from "ui";
import { GoodsCategoryGroup, GoodsCategoryLoadPhase, GoodsCategorySort, GoodsCategoryTag } from "../model/GoodsCategoryState";
import GoodsCategoryViewModel from "../viewmodel/GoodsCategoryViewModel";

/**
 * @file 商品分类页面视图
 * @author Joker.X
 */
@ComponentV2
export struct GoodsCategoryPage {
  /**
   * 商品分类页面 ViewModel
   */
  @Param
  vm: GoodsCategoryViewModel = new GoodsCategoryViewModel();
  private gridScroller: Scroller = new Scroller();
  private listScroller: Scroller = new Scroller();

  @Monitor("vm.scrollRevision")
  private onFirstPageCommitted(): void {
    setTimeout((): void => {
      try {
        (this.vm.isGridMode ? this.gridScroller : this.listScroller).scrollTo({ xOffset: 0, yOffset: 0 });
      } catch (error) {
        console.info("[GoodsCategory] scroll container is not attached");
      }
    }, 0);
  }

  /**
   * 构建商品分类页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      hideTitleBar: true,
      viewModel: this.vm,
      onReady: (context: NavDestinationContext): void => {
        this.vm.initialize(context.pathInfo.param as GoodsCategoryParam | undefined);
      },
      onBackPressed: (): boolean => this.vm.closeMenus()
    }) {
      Column() {
        Row() {
          SearchTopAppBar({
            idPrefix: "gc.search",
            value: this.vm.searchValue,
            onValueChange: (value: string): void => this.vm.onSearchValueChange(value),
            onSearch: (value: string): void => this.vm.submitSearch(value),
            onBackClick: (): void => {
              if (!this.vm.closeMenus()) { navigateBack(); }
            }
          });
        }.id("gc.header").width("100%");
        this.Controls();
        Stack({ alignContent: Alignment.Top }) {
          this.GoodsCategoryContent();
          if (this.vm.filterVisible || this.vm.sortVisible) {
            Column() {}
              .id(this.vm.filterVisible ? "gc.filter.mask" : "gc.sort.mask")
              .width("100%").height("100%")
              .backgroundColor("#66000000")
              .onClick((): void => { this.vm.closeMenus(); });
            if (this.vm.filterVisible) { this.FilterPanel(); }
            else { this.SortPanel(); }
          }
        }.width("100%").layoutWeight(1);
      }.id("gc.page").width("100%").height("100%");
    }
  }

  @Builder
  private Controls(): void {
    Row() {
      Row({ space: 6 }) {
        Text("筛选").fontColor(this.vm.hasAppliedFilter ? $r("app.color.primary") : $r("app.color.text_primary"));
        Image($r("app.media.ic_down")).width(12).height(12);
      }.id("gc.filter.trigger").height(48).layoutWeight(1).justifyContent(FlexAlign.Center)
      .onClick((): void => this.vm.openFilter());
      Row({ space: 6 }) {
        Text(this.vm.sortTitle).id("gc.sort.title")
          .fontColor(this.vm.sortTouched ? $r("app.color.primary") : $r("app.color.text_primary"));
        Image($r("app.media.ic_down")).width(12).height(12);
      }.id("gc.sort.trigger").height(48).layoutWeight(2).justifyContent(FlexAlign.Center)
      .onClick((): void => this.vm.openSort());
      Image(this.vm.isGridMode ? $r("app.media.ic_menu_list") : $r("app.media.ic_menu"))
        .id("gc.layout.toggle").width(48).height(48).padding(13)
        .accessibilityText(this.vm.isGridMode ? "切换为列表布局" : "切换为网格布局")
        .onClick((): void => this.vm.toggleLayout());
    }.id("gc.controls").width("100%").backgroundColor($r("app.color.bg_white"));
  }

  /**
   * 商品分类页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private GoodsCategoryContent() {
    if (this.vm.uiState === BaseNetWorkListUiState.LOADING) {
      Column({ space: 12 }) {
        LoadingProgress().width(40).height(40);
        Text("加载中");
      }.id("gc.state.loading").width("100%").height("100%").justifyContent(FlexAlign.Center);
    } else if (this.vm.uiState === BaseNetWorkListUiState.ERROR) {
      Column() {
        Column() {
          EmptyNetwork({ description: this.vm.errorMessage });
        }.width("100%").layoutWeight(1).clip(true);
        Button("重试").id("gc.state.retry").height(40).margin({ top: 8, bottom: 16 })
          .onClick((): void => this.vm.retryRequest());
      }.id("gc.state.error").width("100%").height("100%").justifyContent(FlexAlign.Center);
    } else if (this.vm.uiState === BaseNetWorkListUiState.EMPTY) {
      Column() {
        Column() {
          EmptyData();
        }.width("100%").layoutWeight(1).clip(true);
        Button("刷新").id("gc.state.emptyRefresh").height(40).margin({ top: 8, bottom: 16 })
          .onClick((): void => this.vm.onRefresh());
      }.id("gc.state.empty").width("100%").height("100%").justifyContent(FlexAlign.Center);
    } else {
      Column() {
        if (this.vm.phase === GoodsCategoryLoadPhase.REFRESH) {
          Text("刷新中…").id("gc.state.refreshing").padding(6);
        }
        if (this.vm.refreshError.length > 0) {
          Text("刷新失败，点击重试").fontColor($r("app.color.primary"))
            .padding(8).onClick((): void => this.vm.onRefresh());
        }
        Refresh({ refreshing: this.vm.phase === GoodsCategoryLoadPhase.REFRESH }) {
          if (this.vm.isGridMode) { this.GoodsGrid(); }
          else { this.GoodsList(); }
        }.id("gc.refresh").layoutWeight(1).width("100%")
        .onRefreshing((): void => {
          console.info("[GoodsCategory] native-refresh");
          this.vm.onRefresh();
        });
        if (this.vm.phase === GoodsCategoryLoadPhase.MORE) {
          Text("加载更多中…").id("gc.state.loadingMore").padding(8);
        } else if (this.vm.moreError.length > 0) {
          Text("加载失败，点击重试").id("gc.state.moreError").padding(8)
            .fontColor($r("app.color.primary")).onClick((): void => this.vm.onLoadMore());
        } else if (!this.vm.hasMore) {
          Text("没有更多商品了").id("gc.state.end").padding(8).fontColor($r("app.color.text_tertiary"));
        }
      }.width("100%").height("100%");
    }
  }

  @Builder
  private GoodsGrid(): void {
    Grid(this.gridScroller) {
      ForEach(this.vm.listData, (goods: Goods): void => {
        GridItem() {
          GoodsGridItem({ goods: goods, idPrefix: "gc",
            onItemClick: (id: number): void => GoodsNavigator.toDetail(id) });
        }
      }, (goods: Goods): string => `${goods.id}`);
    }.id("gc.grid").columnsTemplate("1fr 1fr").columnsGap(8).rowsGap(8)
    .padding(12).width("100%").height("100%")
    .onReachEnd((): void => this.vm.onLoadMore());
  }

  @Builder
  private GoodsList(): void {
    List({ space: 8, scroller: this.listScroller }) {
      ForEach(this.vm.listData, (goods: Goods): void => {
        ListItem() {
          GoodsListItem({ goods: goods, idPrefix: "gc",
            onItemClick: (id: number): void => GoodsNavigator.toDetail(id) });
        }
      }, (goods: Goods): string => `${goods.id}`);
    }.id("gc.list").padding(12).width("100%").height("100%")
    .onReachEnd((): void => this.vm.onLoadMore());
  }

  @Builder
  private FilterPanel(): void {
    Column() {
      Scroll() {
        Column({ space: 16 }) {
          Text("价格区间").width("100%").fontWeight(FontWeight.Medium);
          Row({ space: 12 }) {
            TextInput({ text: this.vm.draftMinPrice, placeholder: "最低价" })
              .id("gc.filter.min").layoutWeight(1).type(InputType.Normal)
              .onChange((value: string): void => { this.vm.draftMinPrice = value; this.vm.filterError = ""; });
            Text("—").id("gc.filter.separator");
            TextInput({ text: this.vm.draftMaxPrice, placeholder: "最高价" })
              .id("gc.filter.max").layoutWeight(1).type(InputType.Normal)
              .onChange((value: string): void => { this.vm.draftMaxPrice = value; this.vm.filterError = ""; });
          }.width("100%");
          if (this.vm.filterError.length > 0) {
            Text(this.vm.filterError).id("gc.filter.error").fontColor(Color.Red).width("100%");
          }
          if (this.vm.categoriesLoading) {
            Text("分类加载中…").id("gc.filter.categories.loading");
          } else if (this.vm.categoriesError.length > 0) {
            Column({ space: 8 }) {
              Text(this.vm.categoriesError).id("gc.filter.categories.error");
              Button("重试分类").id("gc.filter.categories.retry").onClick((): void => this.vm.retryCategories());
            }
          } else {
            ForEach(this.vm.categoryGroups, (group: GoodsCategoryGroup): void => {
              Column({ space: 10 }) {
                Text(group.name).width("100%").fontWeight(FontWeight.Medium);
                Flex({ wrap: FlexWrap.Wrap }) {
                  ForEach(group.tags, (tag: GoodsCategoryTag): void => {
                    Text(tag.name).id(`gc.filter.tag.${tag.id}`)
                      .fontSize(14).padding({ left: 12, right: 12, top: 8, bottom: 8 })
                      .margin({ right: 10, bottom: 10 }).borderRadius(6)
                      .borderWidth(1)
                      .borderColor(this.vm.draftTypeIds.includes(tag.id) ? $r("app.color.primary") : $r("app.color.border"))
                      .fontColor(this.vm.draftTypeIds.includes(tag.id) ? $r("app.color.primary") : $r("app.color.text_primary"))
                      .accessibilitySelected(this.vm.draftTypeIds.includes(tag.id))
                      .onClick((): void => this.vm.toggleCategory(tag.id));
                  }, (tag: GoodsCategoryTag): string => `${tag.id}`);
                }.width("100%");
              }.id(`gc.filter.group.${group.id}`).width("100%");
            }, (group: GoodsCategoryGroup): string => `${group.id}`);
          }
        }.width("100%").padding(16);
      }.id("gc.filter.scroll").width("100%").layoutWeight(1).align(Alignment.Top);
      Row({ space: 16 }) {
        Button("重置").id("gc.filter.reset").layoutWeight(1)
          .backgroundColor($r("app.color.bg_grey")).fontColor($r("app.color.text_primary"))
          .onClick((): void => this.vm.resetDraft());
        Button("确认").id("gc.filter.confirm").layoutWeight(1)
          .backgroundColor($r("app.color.primary")).onClick((): void => this.vm.confirmFilter());
      }.width("100%").padding(12);
    }.id("gc.filter.panel").width("100%").height("78%")
    .backgroundColor($r("app.color.bg_white"));
  }

  @Builder
  private SortPanel(): void {
    Column() {
      ForEach(this.vm.sortOptions, (mode: GoodsCategorySort): void => {
        Text(this.vm.sortLabel(mode)).id(`gc.sort.option.${mode}`)
          .width("100%").height(48).padding({ left: 24, right: 24 })
          .fontColor(this.vm.query.sortMode === mode ? $r("app.color.primary") : $r("app.color.text_primary"))
          .accessibilitySelected(this.vm.query.sortMode === mode)
          .onClick((): void => this.vm.selectSort(mode));
      }, (mode: GoodsCategorySort): string => mode);
    }.id("gc.sort.panel").width("100%").backgroundColor($r("app.color.bg_white"));
  }
}
