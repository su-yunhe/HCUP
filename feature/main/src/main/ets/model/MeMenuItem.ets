/**
 * @file 我的页面菜单项模型
 * @author Joker.X
 */
export interface MeMenuItem {
  /**
   * 菜单标题
   */
  title: ResourceStr;

  /**
   * 菜单图标
   */
  icon: Resource;

  /**
   * 图标颜色
   */
  iconColor: ResourceColor;

  /**
   * 点击回调
   */
  onClick: () => void;

  /**
   * 是否显示分割线
   */
  showDivider: boolean;
}
