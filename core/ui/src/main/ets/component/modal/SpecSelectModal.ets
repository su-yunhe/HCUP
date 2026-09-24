import {
  ColumnStart,
  P100,
  P65,
  RowSpaceBetweenCenter,
  RowStartCenter,
  SpaceHorizontalSmall,
  SpaceVerticalMedium,
  SpaceVerticalSmall,
  SpaceVerticalXSmall
} from "designsystem";
import { Goods, GoodsSpec, SelectedGoods } from "model";
import { BaseNetWorkUiState } from "base";
import { BottomModal } from "./BottomModal";
import { NetWorkImage } from "../image/NetWorkImage";
import { IBestButton, IBestPrice, IBestStepper } from "ibestui";
import { TitleWithLine } from "../title/TitleWithLine";
import { CommonIcon } from "../icon/CommonIcon";
import { BaseNetWorkView } from "../network/BaseNetWorkView";
import { PageLoading } from "../loading/PageLoading";
import { EmptyNetwork } from "../empty/EmptyNetwork";

/**
 * @file 规格选择弹窗组件
 * @author Joker.X
 */
@ComponentV2
export struct SpecSelectModal {
  /**
   * 是否显示弹窗
   */
  @Param
  @Require
  visible: boolean = false;
  /**
   * 关闭回调
   */
  @Param
  onDismiss: () => void = () => {
  };
  /**
   * 商品信息
   */
  @Param
  goods: Goods | null = null;
  /**
   * 网络请求状态
   */
  @Param
  uiState: BaseNetWorkUiState = BaseNetWorkUiState.LOADING;
  /**
   * 规格列表数据
   */
  @Param
  specList: GoodsSpec[] = [];
  /**
   * 规格选择回调
   * @param {GoodsSpec} spec - 选中的规格
   */
  @Param
  onSpecSelected: (spec: GoodsSpec) => void = () => {
  };
  /**
   * 加入购物车回调
   * @param {SelectedGoods} selectedGoods - 已选商品信息
   */
  @Param
  onAddToCart: (selectedGoods: SelectedGoods) => Promise<void> = async () => {
  };
  /**
   * 立即购买回调
   * @param {SelectedGoods} selectedGoods - 已选商品信息
   */
  @Param
  onBuyNow: (selectedGoods: SelectedGoods) => void = () => {
  };
  /**
   * 重试回调（当网络请求失败时使用）
   */
  @Param
  onRetry: () => void = () => {
  };
  /**
   * 当前已选择的规格
   */
  @Param
  selectedSpec: GoodsSpec | null = null;
  /**
   * 是否为网格模式（true: 网格模式, false: 列表模式）
   */
  @Local
  isGridMode: boolean = true;
  /**
   * 选择的商品数量
   */
  @Local
  quantity: number = 1;

  /**
   * 构建规格选择弹窗
   * @returns {void} 无返回值
   */
  build() {
    BottomModal({
      visible: this.visible,
      title: $r("app.string.modal_select_spec"),
      onDismiss: this.onDismiss,
      content: (): void => this.ModalContentNetWorkLayout()
    });
  }

  /**
   * 弹窗内容包装器（包含网络状态处理）
   * @returns {void} 无返回值
   */
  @Builder
  private ModalContentNetWorkLayout(): void {
    BaseNetWorkView({
      uiState: this.uiState,
      onRetry: this.onRetry,
      loadingBuilder: (): void => this.CustomLoading(),
      errorBuilder: (): void => this.CustomError(),
      content: (): void => this.ModalContent()
    });
  }

  /**
   * 弹窗内容
   * @returns {void} 无返回值
   */
  @Builder
  private ModalContent(): void {
    ColumnStart({ widthValue: P100 }) {
      // 顶部商品信息
      if (this.goods) {
        this.SpecHeaderInfo();
      }

      SpaceVerticalMedium();

      // 规格分类标题和切换按钮
      RowSpaceBetweenCenter({ widthValue: P100 }) {
        TitleWithLine({ text: $r("app.string.spec_category") });

        CommonIcon({
          icon: this.isGridMode ? $r("app.media.ic_menu_list") : $r("app.media.ic_menu"),
          iconSize: 24,
          tintColor: $r("app.color.text_secondary"),
          onTap: () => {
            this.isGridMode = !this.isGridMode;
          }
        });
      }

      SpaceVerticalMedium();

      Scroll() {
        if (this.isGridMode) {
          this.GridSpecSelectionContent();
        } else {
          this.ListSpecSelectionContent();
        }
      }
      .width(P100)
      .constraintSize({ maxHeight: P65 })
      .scrollBar(BarState.Off);

      SpaceVerticalMedium();

      // 数量选择器
      if (this.selectedSpec) {
        this.QuantitySelector();
        SpaceVerticalMedium();
      }

      // 底部操作按钮
      this.SpecBottomButtons();
    }
  }

  /**
   * 顶部商品信息
   * @returns {void} 无返回值
   */
  @Builder
  private SpecHeaderInfo(): void {
    RowStartCenter({ widthValue: P100 }) {
      // 商品图片
      NetWorkImage({
        model: this.selectedSpec?.images?.[0] ?? this.goods?.mainPic ?? "",
        widthValue: 100,
        heightValue: 100,
        cornerRadius: $r("app.float.radius_small")
      });
      SpaceHorizontalSmall();
      // 商品信息
      ColumnStart() {
        // 价格
        IBestPrice({
          value: this.selectedSpec?.price ?? this.goods?.price ?? 0,
          symbolFontSize: 16,
          integerFontSize: 24,
          decimalFontSize: 16,
        });

        SpaceVerticalSmall();

        // 已选规格
        if (this.selectedSpec) {
          Text() {
            Span($r("app.string.spec_selected"))
              .fontSize($r("app.float.body_large"))
              .fontColor($r("app.color.text_secondary"));
            Span(`：${this.selectedSpec.name}`)
              .fontSize($r("app.float.body_large"))
              .fontColor($r("app.color.text_secondary"));
          }
        } else {
          Text($r("app.string.spec_not_selected"))
            .fontSize($r("app.float.body_large"))
            .fontColor($r("app.color.text_secondary"));
        }

        SpaceVerticalXSmall();

        // 库存
        Text() {
          Span($r("app.string.spec_stock"))
            .fontSize($r("app.float.body_large"))
            .fontColor($r("app.color.text_tertiary"));
          Span(`：${this.selectedSpec?.stock ?? 0}`)
            .fontSize($r("app.float.body_large"))
            .fontColor($r("app.color.text_tertiary"));
        }
      }
    }
  }

  /**
   * 底部操作按钮
   * @returns {void} 无返回值
   */
  @Builder
  private SpecBottomButtons(): void {
    Row({ space: 12 }) {
      // 加入购物车按钮
      IBestButton({
        text: $r("app.string.modal_add_to_cart"),
        type: "primary",
        plain: true,
        round: true,
        btnHeight: 38,
        disabled: this.selectedSpec === null || (this.selectedSpec?.stock ?? 0) <= 0,
        btnWidth: P100,
        onBtnClick: () => {
          this.handleAddToCart();
        }
      }).layoutWeight(1);

      // 立即购买按钮
      IBestButton({
        text: $r("app.string.modal_buy_now"),
        type: "primary",
        round: true,
        btnHeight: 38,
        disabled: this.selectedSpec === null || (this.selectedSpec?.stock ?? 0) <= 0,
        btnWidth: P100,
        onBtnClick: () => {
          this.handleBuyNow();
        }
      }).layoutWeight(1);
    }
    .width(P100);
  }

  /**
   * 数量选择器
   * @returns {void} 无返回值
   */
  @Builder
  private QuantitySelector(): void {
    RowSpaceBetweenCenter({ widthValue: P100 }) {
      Text($r("app.string.quantity"))
        .fontSize($r("app.float.body_large"))
        .fontColor($r("app.color.text_primary"));

      IBestStepper({
        value: this.quantity,
        min: 1,
        max: this.selectedSpec?.stock ?? 99,
        buttonRadius: 999,
        minusBtnBgColor: "#fff",
        minusBtnIconColor: $r("app.color.primary"),
        minusBtnBorderColor: $r("app.color.primary"),
        plusBtnBgColor: $r("app.color.primary"),
        plusBtnIconColor: "#fff",
        inputBgColor: "transparent"
      });
    }
  }

  /**
   * 网格模式的规格选择内容
   * @returns {void} 无返回值
   */
  @Builder
  private GridSpecSelectionContent(): void {
    Flex({ wrap: FlexWrap.Wrap, justifyContent: FlexAlign.SpaceBetween }) {
      ForEach(this.specList, (spec: GoodsSpec, index: number) => {
        Column() {
          // 规格图片
          NetWorkImage({
            model: spec.images?.[0] ?? this.goods?.mainPic ?? "",
            widthValue: P100,
            heightValue: 100,
            cornerRadius: $r("app.float.radius_small")
          });

          // 规格名称
          Text(spec.name)
            .fontSize($r("app.float.body_large"))
            .fontColor(this.selectedSpec?.id === spec.id ? $r("app.color.primary") : $r("app.color.text_primary"))
            .textAlign(TextAlign.Center)
            .maxLines(2)
            .textOverflow({ overflow: TextOverflow.Ellipsis })
            .width(P100)
            .height(46)
            .padding({ left: $r("app.float.space_horizontal_small"), right: $r("app.float.space_horizontal_small") });
        }
        .width('31%')
        .constraintSize({ minHeight: 130 })
        .borderRadius($r("app.float.radius_small"))
        .border({
          width: 1,
          color: this.selectedSpec?.id === spec.id ? $r("app.color.primary") : $r("app.color.border")
        })
        .backgroundColor(this.selectedSpec?.id === spec.id ? '#0D465CFF' : Color.Transparent)
        .margin({ bottom: $r("app.float.space_vertical_small") })
        .onClick(() => {
          this.onSpecSelected(spec);
        });
      });
    }
    .width(P100);
  }

  /**
   * 列表模式的规格选择内容
   * @returns {void} 无返回值
   */
  @Builder
  private ListSpecSelectionContent(): void {
    Column({ space: 12 }) {
      ForEach(this.specList, (spec: GoodsSpec, index: number) => {
        Row() {
          // 规格图片
          NetWorkImage({
            model: spec.images?.[0] ?? this.goods?.mainPic ?? "",
            widthValue: 50,
            heightValue: 50,
            cornerRadius: $r("app.float.radius_small")
          });

          // 规格信息
          Column({ space: 4 }) {
            // 规格名称
            Text(spec.name)
              .fontSize($r("app.float.body_large"))
              .fontColor(this.selectedSpec?.id === spec.id ? $r("app.color.primary") : $r("app.color.text_primary"));

            IBestPrice({
              value: spec.price
            });
          }
          .alignItems(HorizontalAlign.Start)
          .margin({ left: $r("app.float.space_horizontal_small") });
        }
        .width(P100)
        .padding($r("app.float.space_padding_small"))
        .borderRadius($r("app.float.radius_small"))
        .border({
          width: 1,
          color: this.selectedSpec?.id === spec.id ? $r("app.color.primary") : $r("app.color.border")
        })
        .backgroundColor(this.selectedSpec?.id === spec.id ? '#0D465CFF' : Color.Transparent)
        .onClick(() => {
          this.onSpecSelected(spec);
        });
      });
    }
    .width(P100);
  }

  /**
   * 自定义加载视图
   * @returns {void} 无返回值
   */
  @Builder
  private CustomLoading(): void {
    Column() {
      PageLoading();
    }
    .width(P100)
    .height(300);
  }

  /**
   * 自定义错误视图
   * @returns {void} 无返回值
   */
  @Builder
  private CustomError(): void {
    Column() {
      EmptyNetwork({
        onAction: this.onRetry
      });
    }
    .width(P100)
    .height(300);
  }

  /**
   * 处理加入购物车
   * @returns {Promise<void>} 无返回值
   */
  private async handleAddToCart(): Promise<void> {
    if (!this.selectedSpec || !this.goods) {
      return;
    }

    const selectedGoods = new SelectedGoods();
    selectedGoods.goodsId = this.goods.id;
    selectedGoods.goodsInfo = this.goods;
    selectedGoods.spec = this.selectedSpec;
    selectedGoods.count = this.quantity;

    await this.onAddToCart(selectedGoods);
    this.onDismiss();
  }

  /**
   * 处理立即购买
   * @returns {void} 无返回值
   */
  private handleBuyNow(): void {
    if (!this.selectedSpec || !this.goods) {
      return;
    }

    const selectedGoods = new SelectedGoods();
    selectedGoods.goodsId = this.goods.id;
    selectedGoods.goodsInfo = this.goods;
    selectedGoods.spec = this.selectedSpec;
    selectedGoods.count = this.quantity;

    this.onBuyNow(selectedGoods);
    this.onDismiss();
  }
}
