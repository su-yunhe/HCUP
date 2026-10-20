import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';

@CustomDialog
export struct WebDavRestoreConfirmDialog {
  controller?: CustomDialogController;
  @Link colors: ColorsInterface;
  onCancel: () => void = () => {};
  onContinue: () => void = () => {};

  build() {
    Column({ space: DesignTokens.Spacing.LG }) {
      Text('从云端恢复')
        .fontSize(DesignTokens.Typography.FONT_SIZE_XL)
        .fontWeight(DesignTokens.Typography.FONT_WEIGHT_BOLD)
        .fontColor(this.colors.TEXT_PRIMARY)
        .width('100%')

      Text('继续后将下载云端备份并预览恢复内容，确认恢复后会覆盖本地数据。是否继续？')
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontColor(this.colors.TEXT_SECONDARY)
        .width('100%')

      Row({ space: DesignTokens.Spacing.SM }) {
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
    .padding(DesignTokens.Spacing.LG)
    .backgroundColor(this.colors.SURFACE_PRIMARY)
    .borderRadius(DesignTokens.BorderRadius.LG)
  }
}
