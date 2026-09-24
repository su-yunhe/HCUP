import { P100 } from "designsystem";
import { Comment } from "model";
import { AppNavDestination, BaseNetWorkListView, RefreshLayout } from "ui";
import { CommentCard } from "../component/CommentCard";
import GoodsCommentViewModel from "../viewmodel/GoodsCommentViewModel";

/**
 * @file 商品评论页面视图
 * @author Joker.X
 */
@ComponentV2
export struct GoodsCommentPage {
  /**
   * 商品评论页面 ViewModel
   */
  @Local
  private vm: GoodsCommentViewModel = new GoodsCommentViewModel();

  /**
   * 列表滚动控制器
   */
  private listScroller: Scroller = new Scroller();

  /**
   * 构建商品评论页面
   * @returns {void} 无返回值
   */
  build(): void {
    AppNavDestination({
      title: $r("app.string.goods_comment_title"),
      viewModel: this.vm
    }) {
      BaseNetWorkListView({
        uiState: this.vm.uiState,
        onRetry: (): void => this.vm.retryRequest(),
        content: (): void => this.GoodsCommentContent()
      });
    }
  }

  /**
   * 商品评论页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private GoodsCommentContent(): void {
    RefreshLayout({
      loading: this.vm.isLoading,
      isEnableSlideUp: this.vm.isEnableSlideUp,
      scroller: this.listScroller,
      onRefresh: (direction: "pull" | "slideUp"): void => this.vm.onRefreshDirection(direction)
    }) {
      List({ space: 12, scroller: this.listScroller }) {
        ForEach(this.vm.listData, (item: Comment): void => {
          ListItem() {
            CommentCard({
              comment: item,
              onImageTap: (images: string[], index: number): void => {
                this.vm.openImagePreview(images, index);
              }
            });
          }
        }, (item: Comment, index: number): string => `${item.id}-${index}`);
      }
      .width(P100)
      .height(P100)
      .padding({
        left: $r("app.float.space_horizontal_medium"),
        right: $r("app.float.space_horizontal_medium")
      })
      .edgeEffect(EdgeEffect.None);
    }
  }
}
