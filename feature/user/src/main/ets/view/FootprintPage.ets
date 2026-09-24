import { ColumnStart, P100, SpaceVerticalMedium } from "designsystem";
import { Goods } from "model";
import { AppNavDestination, BaseNetWorkListView, GoodsGridItem } from "ui";
import { IBestDialog } from "ibestui";
import { bp } from "state";
import FootprintViewModel from "../viewmodel/FootprintViewModel";

/**
 * @file 足迹页面视图
 * @author Joker.X
 */
@ComponentV2
export struct FootprintPage {
  /**
   * 足迹页面 ViewModel
   */
  @Local
  private vm: FootprintViewModel = new FootprintViewModel();

  /**
   * 构建足迹页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: $r("app.string.footprint_title"),
      viewModel: this.vm,
      menus: this.vm.shouldShowClearAction() ? [
        {
          value: "",
          icon: $r("app.media.ic_delete"),
          action: (): void => this.vm.showClearDialogModal()
        }
      ] : []
    }) {
      this.FootprintContent();

      IBestDialog({
        visible: this.vm.showClearDialog,
        title: $r("app.string.clear_footprint_title"),
        message: $r("app.string.clear_footprint_message"),
        showCancelButton: true,
        confirmButtonText: $r("app.string.confirm"),
        cancelButtonText: $r("app.string.cancel"),
        onConfirm: (): void => this.vm.confirmClearAll(),
        onCancel: (): void => this.vm.hideClearDialogModal(),
        onClose: (): void => this.vm.hideClearDialogModal()
      });
    }
  }

  /**
   * 足迹页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private FootprintContent(): void {
    BaseNetWorkListView({
      uiState: this.vm.uiState,
      onRetry: (): void => this.vm.loadFootprints(),
      content: (): void => this.FootprintGridContent()
    });
  }

  /**
   * 足迹网格内容
   * @returns {void} 无返回值
   */
  @Builder
  private FootprintGridContent(): void {
    ColumnStart({ fillMaxSize: true }) {
      List() {
        ListItem() {
          SpaceVerticalMedium();
        }

        ListItem() {
          Grid() {
            ForEach(this.vm.goodsList, (item: Goods): void => {
              GridItem() {
                GoodsGridItem({
                  goods: item,
                  onItemClick: (id: number): void => this.vm.toGoodsDetail(id)
                });
              }
            }, (item: Goods): string => `${item.id}`);
          }
          .columnsTemplate(bp({ sm: "1fr 1fr", md: "1fr 1fr 1fr", lg: "1fr 1fr 1fr 1fr" }))
          .columnsGap($r("app.float.space_padding_small"))
          .rowsGap($r("app.float.space_padding_small"))
          .width(P100);
        }

        ListItem() {
          SpaceVerticalMedium();
        }
      }
      .padding({
        left: $r("app.float.space_horizontal_medium"),
        right: $r("app.float.space_horizontal_medium")
      });
    }
  }
}
