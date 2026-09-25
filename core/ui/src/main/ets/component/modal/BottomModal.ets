import { WindowSafeAreaState, getWindowSafeAreaState } from "state";

/**
 * @file 底部弹出层 Modal 组件
 *
 * 基于鸿蒙官方 bindSheet API 实现的半模态弹窗组件。
 * 提供统一的样式和行为，支持自定义背景色、圆角、内边距等。
 *
 * @param visible 是否显示弹窗
 * @param title 标题文本（可选）
 * @param onDismiss 关闭回调
 * @param detents 高度档位，默认 [SheetSize.FIT_CONTENT, SheetSize.FIT_CONTENT]
 * @param dragBar 是否显示拖动条，默认 true
 * @param showClose 是否显示关闭按钮，默认 true
 * @param containerColor 容器背景色，默认白色
 * @param sheetBorderRadius 容器圆角，默认顶部 16vp 圆角
 * @param horizontalPadding 水平内边距，默认 16vp
 * @param content 内容构建器
 * @author Joker.X
 */
@ComponentV2
export struct BottomModal {
  /**
   * 是否显示弹窗
   */
  @Param
  @Require
  visible: boolean = false;
  /**
   * 标题
   */
  @Param
  title?: string | Resource = undefined;
  /**
   * 关闭回调
   */
  @Param
  onDismiss: () => void = () => {
  };
  /**
   * 高度档位
   */
  @Param
  detents: [SheetSize | Length, (SheetSize | Length)?, (SheetSize | Length)?] =
    [SheetSize.FIT_CONTENT, SheetSize.FIT_CONTENT];
  /**
   * 是否显示拖动条
   */
  @Param
  dragBar: boolean = true;
  /**
   * 是否显示关闭按钮
   */
  @Param
  showClose: boolean = true;
  /**
   * 容器背景色
   */
  @Param
  containerColor: ResourceColor = $r("app.color.bg_white");
  /**
   * 容器圆角
   */
  @Param
  sheetBorderRadius: BorderRadiuses = {
    topLeft: $r("app.float.radius_large"),
    topRight: $r("app.float.radius_large")
  };
  /**
   * 水平内边距
   */
  @Param
  horizontalPadding: number | Resource = $r("app.float.space_padding_large");
  /**
   * 当前窗口安全区状态（可外部传入，默认内部获取）
   */
  @Param
  windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();
  /**
   * 内容构建器
   */
  @BuilderParam
  @Require
  content: () => void;

  /**
   * 构建底部弹窗
   * @returns {void} 无返回值
   */
  build() {
    Column()
      .width(0)
      .height(0)
      .bindSheet($$this.visible, this.sheetBuilder, {
        detents: this.detents,
        dragBar: this.dragBar,
        showClose: this.showClose,
        backgroundColor: this.containerColor,
        radius: this.sheetBorderRadius,
        title: this.title ? { title: this.title } : undefined,
        onDisappear: () => {
          this.onDismiss();
        }
      })
  }

  /**
   * Sheet 内容构建器
   * @returns {void} 无返回值
   */
  @Builder
  sheetBuilder() {
    Column() {
      this.content();
    }
    .padding({
      left: this.horizontalPadding,
      right: this.horizontalPadding,
      bottom: this.windowSafeAreaState.bottomInset
    })
  }
}
