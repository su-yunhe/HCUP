import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { ThemeManager } from '../../manager/ThemeManager';

@Component
export struct SettingsSyncConfigCard {
  @Link webdavEndpoint: string;
  @Link webdavUsername: string;
  @Link webdavPassword: string;
  @Link webdavSyncPassword: string;
  @Link webdavRemoteRoot: string;
  @Link showWebdavPassword: boolean;
  @Link showWebdavSyncPassword: boolean;
  @StorageProp('ThemeRefreshToken') @Watch('onThemeChange') themeRefreshToken: number = 0;
  @State private colors: ColorsInterface = ThemeManager.getInstance().getColors();

  private onThemeChange(): void {
    this.colors = ThemeManager.getInstance().getColors();
  }

  @Builder
  private buildInputField(label: string, value: string, placeholder: string, onChange: (val: string) => void, inputId: string): void {
    Column() {
      Text(label)
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.GRAY_600)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.XS })

      TextInput({ text: value, placeholder })
        .id(inputId)
        .width('100%')
        .height(44)
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .backgroundColor(this.colors.GRAY_100)
        .borderRadius(DesignTokens.BorderRadius.MD)
        .padding({ left: DesignTokens.Spacing.MD, right: DesignTokens.Spacing.MD })
        .onChange(onChange)
    }
    .width('100%')
    .margin({ bottom: DesignTokens.Spacing.MD })
  }

  @Builder
  private buildPasswordField(label: string, value: string, placeholder: string, isVisible: boolean, onChange: (val: string) => void, onToggle: () => void, inputId: string): void {
    Column() {
      Text(label)
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.GRAY_600)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.XS })

      Row() {
        TextInput({ text: value, placeholder })
          .id(inputId)
          .type(isVisible ? InputType.Normal : InputType.Password)
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .backgroundColor(this.colors.GRAY_100)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .padding({ left: DesignTokens.Spacing.MD, right: DesignTokens.Spacing.SM })
          .onChange(onChange)

        Button(isVisible ? '隐藏' : '显示')
          .margin({ left: DesignTokens.Spacing.SM })
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.colors.GRAY_700)
          .backgroundColor(this.colors.GRAY_200)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .onClick(onToggle)
      }
      .width('100%')
    }
    .width('100%')
    .margin({ bottom: DesignTokens.Spacing.MD })
  }

  build(): void {
    Column() {
      Text('基础配置')
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontWeight(DesignTokens.Typography.FONT_WEIGHT_MEDIUM)
        .fontColor(this.colors.TEXT_PRIMARY)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.MD })

      this.buildInputField('WebDAV 地址', this.webdavEndpoint, 'https://dav.example.com/dav/', (v: string): void => { this.webdavEndpoint = v; }, 'webdavEndpointInput')
      this.buildInputField('账号', this.webdavUsername, 'username', (v: string): void => { this.webdavUsername = v; }, 'webdavUsernameInput')
      this.buildPasswordField('密码', this.webdavPassword, 'password', this.showWebdavPassword, (v: string): void => { this.webdavPassword = v; }, (): void => { this.showWebdavPassword = !this.showWebdavPassword; }, 'webdavPasswordInput')
      this.buildPasswordField('同步密码（用于 AES 加密）', this.webdavSyncPassword, 'sync password', this.showWebdavSyncPassword, (v: string): void => { this.webdavSyncPassword = v; }, (): void => { this.showWebdavSyncPassword = !this.showWebdavSyncPassword; }, 'webdavSyncPasswordInput')
      this.buildInputField('远端目录', this.webdavRemoteRoot, '/weiyu_sync', (v: string): void => { this.webdavRemoteRoot = v; }, 'webdavRemoteRootInput')

      Text('提示：请先在 WebDAV 服务端创建该目录（只需一次）')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.GRAY_500)
        .width('100%')
    }
    .width('100%')
    .padding(DesignTokens.Spacing.LG)
    .backgroundColor(this.colors.SURFACE_PRIMARY)
    .borderRadius(DesignTokens.BorderRadius.LG)
  }
}

@Component
export struct SettingsSyncActionsCard {
  @Prop busy: boolean = false;
  @Prop confirmPending: boolean = false;
  @Prop result: string = '';
  @Prop backupResult: string = '';
  onSave: () => void = () => {};
  onTest: () => void = () => {};
  onSyncNow: () => void = () => {};
  onBackup: () => void = () => {};
  onRestore: () => void = () => {};
  @StorageProp('ThemeRefreshToken') @Watch('onThemeChange') themeRefreshToken: number = 0;
  @State private colors: ColorsInterface = ThemeManager.getInstance().getColors();

  private onThemeChange(): void {
    this.colors = ThemeManager.getInstance().getColors();
  }

  build(): void {
    Column() {
      Text('手动操作')
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontWeight(DesignTokens.Typography.FONT_WEIGHT_MEDIUM)
        .fontColor(this.colors.TEXT_PRIMARY)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.MD })

      Row() {
        Button(this.busy ? '处理中...' : '保存设置')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.busy ? this.colors.GRAY_400 : this.colors.GRAY_600)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!(this.busy || this.confirmPending))
          .id('webdavSaveSettingsButton')
          .onClick(this.onSave)

        Button(this.busy ? '处理中...' : '测试连接')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.busy ? this.colors.GRAY_400 : this.colors.PRIMARY)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!(this.busy || this.confirmPending))
          .margin({ left: DesignTokens.Spacing.SM })
          .id('webdavTestConnectionButton')
          .onClick(this.onTest)
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

      if (this.result.length > 0) {
        Text(this.result)
          .id('webdavSettingsStatus')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.result.includes('✅') ? this.colors.SUCCESS : this.colors.GRAY_600)
          .margin({ top: DesignTokens.Spacing.SM })
          .textAlign(TextAlign.Center)
      }

      Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Row() {
        Button(this.busy ? '处理中...' : '立即同步')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.busy ? this.colors.GRAY_400 : this.colors.PRIMARY)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!(this.busy || this.confirmPending))
          .id('webdavSyncNowButton')
          .onClick(this.onSyncNow)
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Row() {
        Button(this.busy ? '处理中...' : '立即备份')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.busy ? this.colors.GRAY_400 : this.colors.SUCCESS)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!(this.busy || this.confirmPending))
          .id('webdavBackupButton')
          .onClick(this.onBackup)

        Button(this.busy ? '处理中...' : '从云端恢复')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.busy ? this.colors.GRAY_400 : this.colors.WARNING)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!(this.busy || this.confirmPending))
          .margin({ left: DesignTokens.Spacing.SM })
          .id('webdavRestoreButton')
          .onClick(this.onRestore)
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      if (this.backupResult.length > 0) {
        Text(this.backupResult)
          .id('webdavRestoreStatus')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.backupResult.includes('✅') ? this.colors.SUCCESS : this.colors.GRAY_600)
          .margin({ top: DesignTokens.Spacing.SM })
          .textAlign(TextAlign.Center)
      }

      Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Text('使用说明')
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.TEXT_SECONDARY)
        .margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Column() {
        Text('【立即同步】日常多端同步，只同步变更数据')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.colors.TEXT_SECONDARY)
          .width('100%')
        Text('• 同步学习过的单词、复习记录、用户词书')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.colors.GRAY_500)
          .width('100%')
          .margin({ left: DesignTokens.Spacing.SM })
        Text('• 未学习的单词不会同步，节省流量')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.colors.GRAY_500)
          .width('100%')
          .margin({ left: DesignTokens.Spacing.SM })
        Text('【立即备份】完整备份所有数据到云端')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.colors.TEXT_SECONDARY)
          .width('100%')
          .margin({ top: DesignTokens.Spacing.SM })
        Text('• 适合换设备前、定期备份使用')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.colors.GRAY_500)
          .width('100%')
          .margin({ left: DesignTokens.Spacing.SM })
        Text('【从云端恢复】下载云端数据覆盖本地')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.colors.TEXT_SECONDARY)
          .width('100%')
          .margin({ top: DesignTokens.Spacing.SM })
        Text('• ⚠️ 会覆盖本地数据，新设备首次使用')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.colors.GRAY_500)
          .width('100%')
          .margin({ left: DesignTokens.Spacing.SM })
        Text('• 本地未同步的学习记录将丢失')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.colors.GRAY_500)
          .width('100%')
          .margin({ left: DesignTokens.Spacing.SM })
      }
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.SM })
      .width('100%')
    }
    .width('100%')
    .padding({ top: DesignTokens.Spacing.LG, bottom: DesignTokens.Spacing.LG })
    .backgroundColor(this.colors.SURFACE_PRIMARY)
    .borderRadius(DesignTokens.BorderRadius.LG)
    .margin({ top: DesignTokens.Spacing.MD })
  }
}
