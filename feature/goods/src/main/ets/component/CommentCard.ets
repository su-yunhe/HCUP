import { IBestRate } from "ibestui";
import {
  P100,
  RowSpaceBetweenCenter,
  RowStartTop,
  SpaceHorizontalMedium,
  SpaceVerticalMedium,
  SpaceVerticalXSmall,
  columnStart
} from "designsystem";
import { Comment } from "model";
import { bp } from "state";
import { Avatar, Card, NetWorkImage } from "ui";

/**
 * @file 商品评价卡片组件
 * @author Joker.X
 */
@ComponentV2
export struct CommentCard {
  /**
   * 评论信息
   */
  @Param
  comment: Comment = new Comment();
  /**
   * 图片点击回调
   */
  @Param
  onImageTap: ((images: string[], index: number) => void) | undefined = undefined;

  /**
   * 构建商品评价卡片
   * @returns {void} 无返回值
   */
  build(): void {
    Card({ widthValue: P100, radiusValue: $r("app.float.radius_medium") }) {
      RowStartTop({
        widthValue: P100,
        paddingValue: $r("app.float.space_padding_medium")
      }) {
        Avatar({
          src: this.comment.avatarUrl ?? "",
          avatarSize: 40
        });

        SpaceHorizontalMedium();

        Column() {
          RowSpaceBetweenCenter({ widthValue: P100 }) {
            Text(this.comment.nickName ?? $r("app.string.anonymous_user"))
              .fontSize($r("app.float.body_large"))
              .fontColor($r("app.color.text_primary"));

            if (this.comment.createTime) {
              Text(this.comment.createTime)
                .fontSize($r("app.float.body_medium"))
                .fontColor($r("app.color.text_tertiary"));
            }
          }

          SpaceVerticalXSmall();

          IBestRate({
            value: this.comment.starCount,
            count: 5,
            iconSize: 16,
            readOnly: true
          });

          if (this.comment.content) {
            SpaceVerticalMedium();
            Text(this.comment.content)
              .fontSize($r("app.float.body_medium"))
              .fontColor($r("app.color.text_secondary"))
              .width(P100);
          }

          if (this.comment.pics && this.comment.pics.length > 0) {
            SpaceVerticalMedium();
            this.CommentImageGrid(this.comment.pics);
          }
        }
        .layoutWeight(1)
        .attributeModifier(columnStart());
      }
    }
  }

  /**
   * 评论图片九宫格
   * @param {string[]} images - 图片列表
   * @returns {void} 无返回值
   */
  @Builder
  private CommentImageGrid(images: string[]): void {
    Grid() {
      ForEach(this.getDisplayImages(images), (image: string, index: number): void => {
        GridItem() {
          Stack() {
            NetWorkImage({
              model: image,
              showBackground: true,
              backgroundColorValue: $r("app.color.bg_content"),
              cornerRadius: $r("app.float.radius_small")
            });
          }
          .aspectRatio(1)
          .onClick((): void => this.handleImageTap(images, index));
        }
      }, (image: string, index: number): string => `${image}-${index}`);
    }
    .columnsTemplate(bp({
      sm: "1fr 1fr 1fr",
      md: "1fr 1fr 1fr 1fr 1fr",
      lg: "1fr 1fr 1fr 1fr 1fr 1fr"
    }))
    .columnsGap($r("app.float.space_padding_small"))
    .rowsGap($r("app.float.space_padding_small"))
    .width(P100);
  }

  /**
   * 获取展示图片列表
   * @param {string[]} images - 图片列表
   * @returns {string[]} 展示图片列表
   */
  private getDisplayImages(images: string[]): string[] {
    return images.slice(0, 9);
  }

  /**
   * 处理图片点击
   * @param {string[]} images - 图片列表
   * @param {number} index - 图片索引
   * @returns {void} 无返回值
   */
  private handleImageTap(images: string[], index: number): void {
    if (!this.onImageTap) {
      return;
    }
    this.onImageTap(this.getDisplayImages(images), index);
  }
}
