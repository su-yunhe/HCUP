import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { ThemeManager } from '../../manager/ThemeManager';
import { SelectOption } from './SettingsCommon';

const WEBDAV_AUTOSYNC_INTERVAL_OPTIONS: SelectOption[] = [
  { value: '每1小时' },
  { value: '每3小时' },
  { value: '每6小时（默认）' },
  { value: '每12小时' },
  { value: '每24小时' }
];

@Component
export struct SettingsSyncView {
  @Link webdavEndpoint: string;
  @Link webdavUsername: string;
  @Link webdavPassword: string;
  @Link webdavSyncPassword: string;
  @Link webdavRemoteRoot: string;
  @Link showWebdavPassword: boolean;
  @Link showWebdavSyncPassword: boolean;
  @Link webdavAutoSyncEnabled: boolean;
  @Link webdavAutoSyncIntervalIndex: number;
  @Link webdavAutoSyncUploadModelEnabled: boolean;
  @Link webdavAutoSyncUploadBackupEnabled: boolean;
  @Link webdavAutoSyncLastSuccessMs: number;
  @Link webdavAutoSyncLastError: string;
  @Prop colors: ColorsInterface = ThemeManager.getInstance().getColors();
  @Prop webdavResult: string = '';
  @Prop webdavBackupResult: string = '';
  @Prop actionsBusy: boolean = false;
  @Prop actionsDisabled: boolean = false;
  @Prop restoreWorking: boolean = false;
  onSave: () => void = () => {};
  onTest: () => void = () => {};
  onSync: () => void = () => {};
  onBackup: () => void = () => {};
  onRestore: () => void = () => {};
  onAutoSyncChange: () => void = () => {};

  private formatWebDavAutoSyncLastSuccess(): string {
    const ms = this.webdavAutoSyncLastSuccessMs;
    if (ms <= 0) {
      return '从未';
    }
    try {
      return new Date(ms).toLocaleString();
    } catch {
      return String(ms);
    }
  }

  @Builder
  private buildInputField(id: string, label: string, getValue: () => string, placeholder: string, onChange: (val: string) => void) {
    Column() {
      Text(label)
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.GRAY_600)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.XS })

      TextInput({ text: getValue(), placeholder })
        .id(id)
        .enabled(!this.actionsDisabled)
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
  private buildPasswordField(id: string, toggleId: string, label: string, getValue: () => string, placeholder: string, getVisible: () => boolean, onChange: (val: string) => void, onToggle: () => void) {
    Column() {
      Text(label)
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.GRAY_600)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.XS })

      Row() {
        TextInput({ text: getValue(), placeholder })
          .id(id)
          .enabled(!this.actionsDisabled)
          .type(getVisible() ? InputType.Normal : InputType.Password)
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .backgroundColor(this.colors.GRAY_100)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .padding({ left: DesignTokens.Spacing.MD, right: DesignTokens.Spacing.SM })
          .onChange(onChange)

        Button(getVisible() ? '隐藏' : '显示')
          .id(toggleId)
          .enabled(!this.actionsDisabled)
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

  @Builder
  private buildToggleRow(id: string, title: string, subtitle: string, getIsOn: () => boolean, onChange: (val: boolean) => void) {
    Row() {
      Column() {
        Text(title)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.GRAY_700)
        Text(subtitle)
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.colors.GRAY_600)
      }
      .alignItems(HorizontalAlign.Start)

      Blank()

      Toggle({ type: ToggleType.Switch, isOn: getIsOn() })
        .id(id)
        .enabled(!this.actionsDisabled)
        .selectedColor(this.colors.PRIMARY)
        .switchPointColor(this.colors.WHITE)
        .onChange(onChange)
    }
    .width('100%')
    .height(64)
    .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })
  }

  @Builder
  private buildBasicConfigCard() {
    Column() {
      Text('基础配置')
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontWeight(DesignTokens.Typography.FONT_WEIGHT_MEDIUM)
        .fontColor(this.colors.TEXT_PRIMARY)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.MD })

      this.buildInputField('webdav_endpoint', 'WebDAV 地址', () => this.webdavEndpoint, 'https://dav.example.com/dav/', (v) => this.webdavEndpoint = v)
      this.buildInputField('webdav_username', '账号', () => this.webdavUsername, 'username', (v) => this.webdavUsername = v)
      this.buildPasswordField('webdav_password', 'webdav_password_toggle', '密码', () => this.webdavPassword, 'password', () => this.showWebdavPassword, (v) => this.webdavPassword = v, () => this.showWebdavPassword = !this.showWebdavPassword)
      this.buildPasswordField('webdav_sync_password', 'webdav_sync_password_toggle', '同步密码（用于 AES 加密）', () => this.webdavSyncPassword, 'sync password', () => this.showWebdavSyncPassword, (v) => this.webdavSyncPassword = v, () => this.showWebdavSyncPassword = !this.showWebdavSyncPassword)
      this.buildInputField('webdav_remote_root', '远端目录', () => this.webdavRemoteRoot, '/weiyu_sync', (v) => this.webdavRemoteRoot = v)

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

  @Builder
  private buildAutoSyncCard() {
    Column() {
      Text('自动同步')
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontWeight(DesignTokens.Typography.FONT_WEIGHT_MEDIUM)
        .fontColor(this.colors.TEXT_PRIMARY)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.MD })

      this.buildToggleRow('webdav_auto_sync_enabled', '启用自动同步', '进入前台时按间隔自动同步', () => this.webdavAutoSyncEnabled, (isOn) => {
        this.webdavAutoSyncEnabled = isOn;
        this.onAutoSyncChange();
      })

      if (this.webdavAutoSyncEnabled) {
        Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

        Row() {
          Text('同步间隔')
            .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
            .fontColor(this.colors.GRAY_700)
          Blank()
          Select(WEBDAV_AUTOSYNC_INTERVAL_OPTIONS)
            .enabled(!this.actionsDisabled)
            .selected(this.webdavAutoSyncIntervalIndex)
            .value(WEBDAV_AUTOSYNC_INTERVAL_OPTIONS[this.webdavAutoSyncIntervalIndex].value)
            .font({ size: DesignTokens.Typography.FONT_SIZE_BASE })
            .fontColor(this.colors.GRAY_700)
            .onSelect((index: number) => {
              this.webdavAutoSyncIntervalIndex = index;
              this.onAutoSyncChange();
            })
        }
        .width('100%')
        .height(56)
        .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

        Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

        this.buildToggleRow('webdav_auto_upload_model', '自动上传模型', '用于多端算法同步', () => this.webdavAutoSyncUploadModelEnabled, (isOn) => {
          this.webdavAutoSyncUploadModelEnabled = isOn;
          this.onAutoSyncChange();
        })

        Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

        this.buildToggleRow('webdav_auto_upload_backup', '自动上传全量备份', '只上传，不自动恢复覆盖本地', () => this.webdavAutoSyncUploadBackupEnabled, (isOn) => {
          this.webdavAutoSyncUploadBackupEnabled = isOn;
          this.onAutoSyncChange();
        })

        Column() {
          Text(`上次自动同步：${this.formatWebDavAutoSyncLastSuccess()}`)
            .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
            .fontColor(this.colors.GRAY_500)
            .width('100%')

          if (this.webdavAutoSyncLastError.length > 0) {
            Text(`最近错误：${this.webdavAutoSyncLastError}`)
              .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
              .fontColor(this.colors.ERROR)
              .width('100%')
              .margin({ top: DesignTokens.Spacing.XS })
          }
        }
        .width('100%')
        .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.SM })
      }
    }
    .width('100%')
    .padding({ top: DesignTokens.Spacing.LG, bottom: DesignTokens.Spacing.LG })
    .backgroundColor(this.colors.SURFACE_PRIMARY)
    .borderRadius(DesignTokens.BorderRadius.LG)
    .margin({ top: DesignTokens.Spacing.MD })
  }

  @Builder
  private buildActionButtonsCard() {
    Column() {
      Text('手动操作')
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontWeight(DesignTokens.Typography.FONT_WEIGHT_MEDIUM)
        .fontColor(this.colors.TEXT_PRIMARY)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.MD })

      Row() {
        Button(this.actionsBusy ? '处理中...' : '保存设置')
          .id('webdav_save_settings')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.actionsBusy ? this.colors.GRAY_400 : this.colors.GRAY_600)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.actionsDisabled)
          .onClick(() => this.onSave())

        Button(this.actionsBusy ? '处理中...' : '测试连接')
          .id('webdav_test_connection')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.actionsBusy ? this.colors.GRAY_400 : this.colors.PRIMARY)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.actionsDisabled)
          .margin({ left: DesignTokens.Spacing.SM })
          .onClick(() => this.onTest())
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

      if (this.webdavResult.length > 0) {
        Text(this.webdavResult)
          .id('webdav_action_status')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.webdavResult.includes('✅') ? this.colors.SUCCESS : this.colors.GRAY_600)
          .margin({ top: DesignTokens.Spacing.SM })
          .textAlign(TextAlign.Center)
      }

      Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Row() {
        Button(this.actionsBusy ? '处理中...' : '立即同步')
          .id('webdav_sync_now')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.actionsBusy ? this.colors.GRAY_400 : this.colors.PRIMARY)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.actionsDisabled)
          .onClick(() => this.onSync())
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Row() {
        Button(this.actionsBusy ? '处理中...' : '立即备份')
          .id('webdav_backup_now')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.actionsBusy ? this.colors.GRAY_400 : this.colors.SUCCESS)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.actionsDisabled)
          .onClick(() => this.onBackup())

        Button(this.actionsBusy ? '处理中...' : '从云端恢复')
          .id('webdav_restore_from_cloud')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.actionsBusy ? this.colors.GRAY_400 : this.colors.ERROR)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.actionsDisabled)
          .margin({ left: DesignTokens.Spacing.SM })
          .onClick(() => this.onRestore())
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Row({ space: DesignTokens.Spacing.SM }) {
        LoadingProgress()
          .id('webdav_restore_loading')
          .width(24)
          .height(24)
          .color(this.colors.PRIMARY)
          .enableLoading(this.restoreWorking)
          .visibility(this.restoreWorking ? Visibility.Visible : Visibility.None)
        Text(this.webdavBackupResult)
          .id('webdav_restore_status')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.webdavBackupResult.includes('✅') ? this.colors.SUCCESS : this.colors.GRAY_600)
          .layoutWeight(1)
          .textAlign(TextAlign.Center)
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })
      .margin({ top: DesignTokens.Spacing.SM })
      .visibility(this.webdavBackupResult.length > 0 ? Visibility.Visible : Visibility.None)

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

  build() {
    Column() {
      this.buildBasicConfigCard()
      this.buildAutoSyncCard()
      this.buildActionButtonsCard()
    }
    .width('100%')
    .padding(DesignTokens.Spacing.MD)
  }
}
