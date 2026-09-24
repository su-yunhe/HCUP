import { ColumnStart, P100, RowCenter, SpaceHorizontalSmall, SpaceVerticalXXLarge } from "designsystem";

/**
 * @file 底部导航行组件
 * @author Joker.X
 */
@ComponentV2
export struct BottomNavigationRow {
  /**
   * 提示文案
   */
  @Param
  messageText: ResourceStr = "";
  /**
   * 操作文案
   */
  @Param
  actionText: ResourceStr = "";
  /**
   * 左侧点击回调
   */
  @Param
  onCancelClick: () => void = () => {
  };
  /**
   * 右侧点击回调
   */
  @Param
  onActionClick: () => void = () => {
  };
  /**
   * 是否显示分隔符
   */
  @Param
  divider: boolean = false;

  /**
   * 构建底部导航行
   * @returns {void} 无返回值
   */
  build(): void {
    ColumnStart({ widthValue: P100 }) {
      SpaceVerticalXXLarge();

      RowCenter({ widthValue: P100 }) {
        if (!this.divider) {
          Text(this.messageText)
            .fontSize($r("app.float.body_medium"))
            .fontColor($r("app.color.text_tertiary"));
        } else {
          Text(this.messageText)
            .fontSize($r("app.float.body_medium"))
            .fontColor($r("app.color.text_tertiary"))
            .onClick((): void => {
              this.onCancelClick();
            });
        }

        if (this.divider) {
          SpaceHorizontalSmall();

          Text("|")
            .fontSize($r("app.float.body_medium"))
            .fontColor($r("app.color.text_tertiary"));

          SpaceHorizontalSmall();
        }

        Text(this.actionText)
          .fontSize($r("app.float.body_medium"))
          .fontColor($r("app.color.primary"))
          .onClick((): void => {
            this.onActionClick();
          });
      }
    }
  }
}
