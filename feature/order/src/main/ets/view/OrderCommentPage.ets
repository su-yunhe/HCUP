import {
  ColumnStart,
  LargePaddingVerticalScroll,
  P100,
  SpaceVerticalLarge,
  SpaceVerticalSmall,
  SpaceVerticalXSmall,
  SpaceVerticalXXLarge
} from "designsystem";
import { getWindowSafeAreaState, WindowSafeAreaState } from "state";
import { AppBottomButton, AppNavDestination } from "ui";
import {
  IBestField,
  IBestFieldValueType,
  IBestRate,
  IBestUploader,
  IBestUploaderFile
} from "ibestui";
import OrderCommentViewModel from "../viewmodel/OrderCommentViewModel";

/**
 * @file 订单评论页面视图
 * @author Joker.X
 */
@ComponentV2
export struct OrderCommentPage {
  /**
   * 订单评论页面 ViewModel
   */
  @Local
  private vm: OrderCommentViewModel = new OrderCommentViewModel();
  /**
   * 当前窗口安全区状态
   */
  @Local
  private windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();

  /**
   * 构建订单评论页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: $r("app.string.order_comment"),
      viewModel: this.vm,
      pageBackgroundColor: $r("app.color.bg_white"),
      titleOptions: {
        backgroundColor: $r("app.color.bg_white")
      },
      paddingValue: {
        top: this.windowSafeAreaState.topInset,
        left: this.windowSafeAreaState.leftInset,
        right: this.windowSafeAreaState.rightInset
      }
    }) {
      this.PageContent();
    }
  }

  /**
   * 页面内容
   * @returns {void} 无返回值
   */
  @Builder
  private PageContent(): void {
    ColumnStart({ fillMaxSize: true }) {
      Column() {
        LargePaddingVerticalScroll({ fillMaxSize: true }) {
          Column() {
            SpaceVerticalXXLarge();

            this.RateSection();

            SpaceVerticalLarge();

            this.CommentFieldCard();

            SpaceVerticalSmall();

            this.ImagePickerSection();

            SpaceVerticalSmall();
          }
          .width(P100)
          .constraintSize({ minHeight: P100 });
        }
      }
      .layoutWeight(1);

      AppBottomButton({
        text: $r("app.string.submit_comment"),
        onTap: (): void => this.vm.onSubmitComment()
      });
    }
  }

  /**
   * 评分区域
   * @returns {void} 无返回值
   */
  @Builder
  private RateSection(): void {
    Column() {
      IBestRate({
        value: this.vm.rating,
        count: 5,
        iconSize: 32,
        onChange: (value: number): void => this.vm.updateRating(value)
      });

      SpaceVerticalSmall();

      Text(this.getRatingText(this.vm.rating))
        .fontSize($r("app.float.headline_large"))
        .fontColor($r("app.color.text_secondary"));
    }
    .alignItems(HorizontalAlign.Center)
    .width(P100);
  }

  /**
   * 评论输入框卡片
   * @returns {void} 无返回值
   */
  @Builder
  private CommentFieldCard(): void {
    IBestField({
      showLabel: false,
      value: this.vm.commentContent!!,
      placeholder: $r("app.string.comment_placeholder"),
      rows: 6,
      maxlength: 200,
      showWordLimit: true,
      hasBorder: false,
      autosize: true,
      fieldPadding: $r("app.float.space_padding_medium"),
      bgColor: $r("app.color.bg_content"),
      radius: $r("app.float.radius_medium"),
      onChange: (value: IBestFieldValueType): void => this.vm.updateCommentContent(`${value ?? ""}`)
    })
      .width(P100);
  }

  /**
   * 图片选择区域
   * @returns {void} 无返回值
   */
  @Builder
  private ImagePickerSection(): void {
    IBestUploader({
      fileList: this.vm.imageList!!,
      max: 9,
      previewSize: 90,
      cornerRadius: 8,
      uploaderBgColor: $r("app.color.bg_content"),
      onChange: (list: IBestUploaderFile[], _allList: IBestUploaderFile[]): void => this.vm.updateImageList(list)
    });
  }

  /**
   * 获取评分提示文案
   * @param {number} rating - 评分
   * @returns {string | Resource} 评分提示文案
   */
  private getRatingText(rating: number): string | Resource {
    if (rating <= 0) {
      return $r("app.string.please_rate");
    }
    if (rating === 1) {
      return $r("app.string.rating_very_poor");
    }
    if (rating === 2) {
      return $r("app.string.rating_poor");
    }
    if (rating === 3) {
      return $r("app.string.rating_average");
    }
    if (rating === 4) {
      return $r("app.string.rating_good");
    }
    return $r("app.string.rating_excellent");
  }
}
