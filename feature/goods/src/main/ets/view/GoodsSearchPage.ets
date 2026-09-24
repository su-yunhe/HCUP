import { IBestDialog } from "ibestui";
import {
  ColumnStart,
  MediumPaddingVerticalScroll,
  P100,
  RowSpaceBetweenCenter,
  SpaceVerticalSmall,
  SpaceVerticalXSmall
} from "designsystem";
import { GoodsSearchKeyword, SearchHistory } from "model";
import { navigateBack } from "navigation";
import { AppNavDestination, BaseNetWorkView, CommonIcon, SearchTopAppBar } from "ui";
import GoodsSearchViewModel from "../viewmodel/GoodsSearchViewModel";

/**
 * @file 商品搜索页面视图
 * @author Joker.X
 */
@ComponentV2
export struct GoodsSearchPage {
  /**
   * 商品搜索页面 ViewModel
   */
  @Local
  private vm: GoodsSearchViewModel = new GoodsSearchViewModel();
  /**
   * 内容滚动控制器
   */
  private contentScroller: Scroller = new Scroller();

  /**
   * 构建商品搜索页面
   * @returns {void} 无返回值
   */
  build(): void {
    AppNavDestination({
      viewModel: this.vm,
      hideTitleBar: true
    }) {
      SearchTopAppBar({
        value: this.vm.searchValue,
        autoFocus: true,
        onValueChange: (value: string): void => this.vm.onSearchValueChange(value),
        onSearch: (value: string): void => {
          this.vm.onSearch(value);
        },
        onBackClick: (): void => navigateBack()
      });
      BaseNetWorkView({
        uiState: this.vm.uiState,
        onRetry: (): void => this.vm.retryRequest(),
        content: (): void => this.GoodsSearchContent()
      });

      IBestDialog({
        visible: this.vm.isClearHistoryDialogVisible,
        title: $r("app.string.clear_search_history_title"),
        message: $r("app.string.clear_search_history_message"),
        showCancelButton: true,
        confirmButtonText: $r("app.string.confirm"),
        cancelButtonText: $r("app.string.cancel"),
        onConfirm: (): void => this.vm.confirmClearSearchHistory(),
        onCancel: (): void => this.vm.hideClearHistoryDialog(),
        onClose: (): void => this.vm.hideClearHistoryDialog()
      });
    }
  }

  /**
   * 商品搜索页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private GoodsSearchContent(): void {
    MediumPaddingVerticalScroll({ scroller: this.contentScroller, fillMaxSize: true }) {
      ColumnStart({ fillMaxSize: true, widthValue: P100 }) {
        if (this.vm.searchHistoryList.length > 0) {
          this.SearchHistorySection();
          SpaceVerticalXSmall();
        }
        this.RecommendSearchSection(this.vm.data ?? []);
      }
    }
  }

  /**
   * 搜索历史区域
   * @returns {void} 无返回值
   */
  @Builder
  private SearchHistorySection(): void {
    RowSpaceBetweenCenter({ widthValue: P100 }) {
      Text($r("app.string.search_history"))
        .fontSize($r("app.float.headline_large"))
        .fontColor($r("app.color.text_primary"));

      CommonIcon({
        icon: $r("app.media.ic_delete"),
        iconSize: 18,
        tintColor: $r("app.color.text_subtitle"),
        onTap: (): void => this.vm.showClearHistoryDialog()
      });
    }

    SpaceVerticalSmall();

    Flex({ wrap: FlexWrap.Wrap }) {
      ForEach(this.vm.searchHistoryList, (item: SearchHistory): void => {
        this.SearchTag(item.keyword, (): void => {
          void this.vm.onSearchHistoryClick(item);
        });
      }, (item: SearchHistory, index: number): string => `${item.keyword}-${index}`);
    }
    .width(P100);
  }

  /**
   * 推荐搜索区域
   * @param {GoodsSearchKeyword[]} keywordList - 推荐关键词列表
   * @returns {void} 无返回值
   */
  @Builder
  private RecommendSearchSection(keywordList: GoodsSearchKeyword[]): void {
    Text($r("app.string.recommended_search"))
      .fontSize($r("app.float.headline_large"))
      .fontColor($r("app.color.text_primary"));

    SpaceVerticalSmall();

    Flex({ wrap: FlexWrap.Wrap }) {
      ForEach(keywordList, (item: GoodsSearchKeyword): void => {
        this.SearchTag(item.name, (): void => {
          void this.vm.onKeywordClick(item.name);
        });
      }, (item: GoodsSearchKeyword, index: number): string => `${item.id}-${index}`);
    }
    .width(P100);
  }

  /**
   * 搜索标签
   * @param {string} text - 标签文本
   * @param {() => void} onTap - 点击回调
   * @returns {void} 无返回值
   */
  @Builder
  private SearchTag(text: string, onTap: () => void): void {
    Row() {
      Text(text)
        .fontSize($r("app.float.body_medium"))
        .fontColor($r("app.color.text_secondary"));
    }
    .padding({
      left: $r("app.float.space_horizontal_large"),
      right: $r("app.float.space_horizontal_large"),
      top: $r("app.float.space_vertical_small"),
      bottom: $r("app.float.space_vertical_small")
    })
    .backgroundColor($r("app.color.bg_white"))
    .borderRadius(100)
    .margin({
      right: $r("app.float.space_horizontal_small"),
      bottom: $r("app.float.space_vertical_small")
    })
    .onClick((): void => onTap());
  }
}
