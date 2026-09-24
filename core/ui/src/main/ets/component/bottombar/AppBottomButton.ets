import { ColumnBase, P100 } from "designsystem";
import { IBestButton } from "ibestui";
import { getWindowSafeAreaState, WindowSafeAreaState } from "state";

/**
 * @file 底部操作按钮组件
 * @author Joker.X
 */
@ComponentV2
export struct AppBottomButton {
  /**
   * 按钮文案
   */
  @Param
  text: ResourceStr = "";
  /**
   * 点击回调
   */
  @Param
  onTap: () => void = () => {
  };
  /**
   * 是否加载中
   */
  @Param
  loading: boolean = false;
  /**
   * 背景颜色
   */
  @Param
  bgColor: ResourceColor = $r("app.color.bg_white");
  /**
   * 是否启用底部安全区
   */
  @Param
  safeAreaEnabled: boolean = true;
  /**
   * 当前窗口安全区状态（可外部传入，默认内部获取）
   */
  @Param
  windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();

  /**
   * 构建底部操作按钮
   * @returns {void} 无返回值
   */
  build(): void {
    Column() {
      IBestButton({
        text: this.text,
        type: "primary",
        round: true,
        loading: this.loading,
        disabled: this.loading,
        btnWidth: P100,
        onBtnClick: (): void => {
          this.onTap();
        }
      });
      if (this.safeAreaEnabled && this.windowSafeAreaState.bottomInset > 0) {
        Blank().height(this.windowSafeAreaState.bottomInset);
      }
    }
    .width(P100)
    .backgroundColor(this.bgColor)
    .padding({
      left: $r("app.float.space_padding_medium"),
      right: $r("app.float.space_padding_medium"),
      top: $r("app.float.space_padding_medium"),
      bottom: this.safeAreaEnabled && this.windowSafeAreaState.bottomInset > 0
        ? 0
        : $r("app.float.space_padding_medium")
    });
  }
}
