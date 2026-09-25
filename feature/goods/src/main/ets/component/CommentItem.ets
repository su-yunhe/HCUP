import { IBestRate } from "ibestui";
import { P100, RowStartTop, SpaceHorizontalMedium, SpaceVerticalXSmall, columnStart } from "designsystem";
import { Comment } from "model";
import { Avatar, NetWorkImage } from "ui";

/**
 * @file 商品评价 Item 组件
 * @author Joker.X
 */
@ComponentV2
export struct CommentItem {
  /**
   * 评论信息
   */
  @Param
  comment: Comment = new Comment();
  /**
   * 点击回调
   */
  @Param
  onTap: (() => void) | undefined = undefined;

  /**
   * 构建评论 Item
   * @returns {void} 无返回值
   */
  build(): void {
    RowStartTop({
      widthValue: P100,
      paddingValue: $r("app.float.space_padding_medium"),
      onTap: this.onTap ? (_: ClickEvent): void => this.handleTap() : undefined
    }) {
      Avatar({
        src: this.comment.avatarUrl ?? "",
        avatarSize: 32
      });

      SpaceHorizontalMedium();

      Column() {
        Text(this.comment.nickName ?? $r("app.string.anonymous_user"))
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.text_primary"));

        SpaceVerticalXSmall();

        IBestRate({
          value: this.comment.starCount,
          count: 5,
          iconSize: 14,
          readOnly: true
        });

        if (this.comment.content) {
          SpaceVerticalXSmall();
          Text(this.comment.content)
            .fontSize($r("app.float.body_medium"))
            .fontColor($r("app.color.text_secondary"))
            .width(P100);
        }
      }
      .layoutWeight(1)
      .attributeModifier(columnStart());

      if (this.comment.pics && this.comment.pics.length > 0) {
        SpaceHorizontalMedium();
        this.CommentImagePreview(this.comment.pics);
      }
    }
  }

  /**
   * 评论图片预览
   * @param {string[]} images - 图片列表
   * @returns {void} 无返回值
   */
  @Builder
  private CommentImagePreview(images: string[]): void {
    Stack({ alignContent: Alignment.BottomEnd }) {
      NetWorkImage({
        model: images[0],
        sizeValue: 60,
        showBackground: true,
        cornerRadius: $r("app.float.radius_small")
      });

      if (images.length > 1) {
        Text(`+${images.length - 1}`)
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.text_white"))
          .padding({
            left: $r("app.float.space_padding_small"),
            right: $r("app.float.space_padding_small"),
            top: $r("app.float.space_padding_small_x"),
            bottom: $r("app.float.space_padding_small_x")
          })
          .backgroundColor($r("app.color.mask"))
          .borderRadius($r("app.float.radius_small"))
          .margin({
            right: $r("app.float.space_padding_small_x"),
            bottom: $r("app.float.space_padding_small_x")
          });
      }
    }
    .width(60)
    .height(60)
    .borderRadius($r("app.float.radius_small"));
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
