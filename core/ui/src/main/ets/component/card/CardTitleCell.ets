import { IBestCell, IBestCellGroup } from "@ibestservices/ibest-ui-v2";

/**
 * @file 卡片标题单元格组件
 * @author Joker.X
 */
type BorderSizeType = "full" | "center" | "right";

@ComponentV2
export struct CardTitleCell {
  /**
   * 左侧图标
   */
  @Param
  @Require
  leftIcon: ResourceStr = "";
  /**
   * 左侧图标颜色
   */
  @Param
  leftIconColor: ResourceColor | undefined = undefined;
  /**
   * 标题文本
   */
  @Param
  @Require
  title: ResourceStr = "";
  /**
   * 右侧文案
   */
  @Param
  @Require
  value: ResourceStr = "";
  /**
   * 是否显示右侧箭头
   */
  @Param
  isLink: boolean = true;
  /**
   * 是否显示分割线
   */
  @Param
  hasBorder: boolean = true;
  /**
   * 分割线类型
   */
  @Param
  borderSizeType: BorderSizeType = "full";
  /**
   * 点击回调
   */
  @Param
  onTap: () => void = () => {
  };

  /**
   * 构建卡片标题单元格
   * @returns {void} 无返回值
   */
  build(): void {
    IBestCellGroup({
      inset: true,
      radius: $r("app.float.radius_medium"),
      outerMargin: 0
    }) {
      IBestCell({
        leftIcon: this.leftIcon,
        leftIconColor: this.leftIconColor,
        title: this.title,
        value: this.value,
        isLink: this.isLink,
        hasBorder: this.hasBorder,
        borderSizeType: this.borderSizeType,
        onCellClick: (): void => this.onTap()
      });
    }
  }
}
