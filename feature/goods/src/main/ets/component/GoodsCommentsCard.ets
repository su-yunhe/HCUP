import { IBestCell, IBestCellGroup, IBestDivider } from "ibestui";
import { ColumnStart, P100, SpaceVerticalSmall } from "designsystem";
import { Comment } from "model";
import { Card, TitleWithLine } from "ui";
import { CommentItem } from "./CommentItem";

/**
 * @file 商品评论卡片组件
 * @author Joker.X
 */
@ComponentV2
export struct GoodsCommentsCard {
  /**
   * 评论列表
   */
  @Param
  comments: Comment[] = [];
  /**
   * 点击查看全部回调
   */
  @Param
  onTap: (() => void) | undefined = undefined;
  /**
   * 点击评论项回调
   */
  @Param
  onItemTap: (() => void) | undefined = undefined;

  /**
   * 构建商品评论卡片
   * @returns {void} 无返回值
   */
  build(): void {
    ColumnStart({
      widthValue: P100,
      paddingValue: {
        left: $r("app.float.space_horizontal_medium"),
        right: $r("app.float.space_horizontal_medium"),
      }
    }) {
      Card({
        widthValue: P100,
        radiusValue: $r("app.float.radius_medium")
      }) {
        ColumnStart({ widthValue: P100 }) {
          IBestCellGroup({
            inset: true,
            radius: $r("app.float.radius_medium"),
            outerMargin: 0
          }) {
            IBestCell({
              value: "查看全部",
              isLink: true,
              clickable: this.onTap !== undefined,
              onCellClick: (): void => this.handleTap(),
              titleBuilder: (): void => this.buildTitle(),
            });
          }

          SpaceVerticalSmall();

          ForEach(this.comments, (comment: Comment, index: number): void => {
            CommentItem({
              comment,
              onTap: this.onItemTap
            });
            if (index < this.comments.length - 1) {
              IBestDivider()
            }
          }, (comment: Comment, index: number): string => `${comment.id}-${index}`);
        }
      }
    }
  }

  /**
   * 构建标题区域
   * @returns {void} 无返回值
   */
  @Builder
  private buildTitle(): void {
    TitleWithLine({ text: $r("app.string.goods_reviews") });
  }

  /**
   * 处理点击事件
   * @returns {void} 无返回值
   */
  private handleTap(): void {
    if (this.onTap) {
      this.onTap();
    }
  }
}
