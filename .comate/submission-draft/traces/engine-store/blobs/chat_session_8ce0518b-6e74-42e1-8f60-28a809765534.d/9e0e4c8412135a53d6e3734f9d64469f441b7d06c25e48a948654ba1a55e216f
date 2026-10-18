import { ThemeConst } from 'constants';

/**
 * 页面底部自建工具栏的一项（图标 + 文字），文字可见且可通过 itemId 定位
 */
@ComponentV2
export struct ToolbarItem {
  @Param @Require itemId: string;
  @Param @Require icon: Resource;
  @Param @Require label: string;
  @Param selected: boolean = false;
  @Event action: () => void = () => {
  };

  build() {
    Column({ space: 4 }) {
      Image(this.icon)
        .width(24)
        .height(24)
      Text(this.label)
        .fontSize(12)
    }
    .id(this.itemId)
    .width('100%')
    .padding({ top: 8, bottom: 8 })
    .accessibilitySelected(this.selected)
    .stateStyles({
      normal: {
        .backgroundColor(ThemeConst.BackGroundColor_Normal)
      },
      clicked: {
        .backgroundColor(ThemeConst.BackGroundColor_Clicked)
      }
    })
    .onClick(() => {
      this.action()
    })
  }
}
