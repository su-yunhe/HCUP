import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { ThemeManager } from '../../manager/ThemeManager';

@Component
export struct WebDavRestoreConfirmDialog {
  @Prop colors: ColorsInterface = ThemeManager.getInstance().getColors();
  onCancel: () => void = () => {};
  onContinue: () => void = () => {};

  build() {
    Column({ space: DesignTokens.Spacing.LG }) {
      Text('⚠️ 从云端恢复')
        .id('webdav_restore_confirm_title')
        .fontSize(DesignTokens.Typography.FONT_SIZE_XL)
        .fontWeight(FontWeight.Bold)
        .fontColor(this.colors.TEXT_PRIMARY)
        .width('100%')

      Text('本地未同步的学习记录将会丢失')
        .id('webdav_restore_confirm_message')
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontColor(this.colors.TEXT_SECONDARY)
        .width('100%')

      Row({ space: DesignTokens.Spacing.MD }) {
        Button('取消')
          .id('webdav_restore_confirm_cancel')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.TEXT_SECONDARY)
          .backgroundColor(this.colors.GRAY_200)
          .onClick(() => this.onCancel())

        Button('继续')
          .id('webdav_restore_confirm_continue')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.colors.WARNING)
          .onClick(() => this.onContinue())
      }
      .width('100%')
    }
    .id('webdav_restore_confirm_dialog')
    .width('100%')
    .padding(DesignTokens.Spacing.XL)
  }
}
