import {
  P100, RowSpaceBetweenCenter, RowStartCenter, SpaceHorizontalSmall
} from "designsystem";
import { IBestButton, IBestCheckbox, IBestPrice } from "ibestui";
import { getWindowSafeAreaState, WindowSafeAreaState } from "state";

/**
 * @file 购物车底部操作栏组件
 * @author Joker.X
 */
@ComponentV2
export struct CartBottomBar {
  /**
   * 是否全选
   */
  @Param
  isAllSelected: boolean = false;
  /**
   * 是否处于编辑模式
   */
  @Param
  isEditing: boolean = false;
  /**
   * 已选商品数量
   */
  @Param
  selectedCount: number = 0;
  /**
   * 已选商品总金额（单位：分）
   */
  @Param
  totalAmount: number = 0;
  /**
   * 全选状态变更回调
   */
  @Param
  onToggleSelectAll: () => void = () => {
  };
  /**
   * 删除按钮点击回调
   */
  @Param
  onDeleteClick: () => void = () => {
  };
  /**
   * 结算按钮点击回调
   */
  @Param
  onSettleClick: () => void = () => {
  };
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
   * 构建购物车底部操作栏
   * @returns {void} 无返回值
   */
  build(): void {
    Column() {
      RowSpaceBetweenCenter({
        widthValue: P100,
        paddingValue: {
          left: $r("app.float.space_horizontal_medium"),
          right: $r("app.float.space_horizontal_medium"),
          top: $r("app.float.space_vertical_medium"),
          bottom: this.safeAreaEnabled && this.windowSafeAreaState.bottomInset > 0
            ? 0
            : $r("app.float.space_vertical_medium")
        }
      }) {
        // 左侧：全选复选框
        RowStartCenter() {
          IBestCheckbox({
            value: this.isAllSelected,
            shape: "round",
            onChange: (): void => {
              this.onToggleSelectAll();
            }
          });

          SpaceHorizontalSmall();

          Text($r("app.string.select_all"))
            .fontSize($r("app.float.body_large"))
            .fontColor($r("app.color.text_primary"));
        }

        // 右侧：合计 + 结算按钮 或 删除按钮
        if (this.isEditing) {
          // 编辑模式：删除按钮
          IBestButton({
            text: this.selectedCount === 0
              ? $r("app.string.delete")
              : $r("app.string.delete_count", this.selectedCount),
            type: "danger",
            round: true,
            disabled: this.selectedCount === 0,
            btnWidth: 90,
            btnHeight: 34,
            onBtnClick: (): void => this.onDeleteClick()
          });
        } else {
          // 非编辑模式：合计 + 结算按钮
          RowStartCenter() {
            Text($r("app.string.total"))
              .fontSize($r("app.float.body_large"))
              .fontColor($r("app.color.text_primary"));

            SpaceHorizontalSmall();

            IBestPrice({ value: this.totalAmount });

            SpaceHorizontalSmall();

            IBestButton({
              text: this.selectedCount === 0
                ? $r("app.string.settle_account")
                : $r("app.string.settle_account_count", this.selectedCount),
              type: "primary",
              round: true,
              disabled: this.selectedCount === 0,
              btnWidth: 90,
              btnHeight: 34,
              onBtnClick: (): void => this.onSettleClick()
            });
          }
        }
      }

      if (this.safeAreaEnabled && this.windowSafeAreaState.bottomInset > 0) {
        Blank().height(this.windowSafeAreaState.bottomInset);
      }
    }
    .width(P100)
    .backgroundColor($r("app.color.bg_white"))
    .border({
      width: { top: 1 },
      color: $r("app.color.border")
    });
  }
}
