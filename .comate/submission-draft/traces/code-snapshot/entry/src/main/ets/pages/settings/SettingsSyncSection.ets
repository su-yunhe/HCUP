import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { ThemeManager } from '../../manager/ThemeManager';
import { WebDavStateStore } from '../../utils/WebDavStateStore';
import { SelectOption } from './SettingsCommon';

import { SettingsSyncActions } from './SettingsSyncActions';

const WEBDAV_AUTOSYNC_INTERVAL_HOURS: number[] = [1, 3, 6, 12, 24];
const WEBDAV_AUTOSYNC_INTERVAL_OPTIONS: SelectOption[] = [
  { value: '每1小时' },
  { value: '每3小时' },
  { value: '每6小时（默认）' },
  { value: '每12小时' },
  { value: '每24小时' }
];

@Component
export struct SettingsSyncSection {
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
  @StorageProp('ThemeRefreshToken') @Watch('onThemeChange') themeRefreshToken: number = 0;
  @State private colors: ColorsInterface = ThemeManager.getInstance().getColors();

  @Prop manualBusy: boolean = false;
  @Prop manualResult: string = '';
  private webdavStateStore: WebDavStateStore = WebDavStateStore.getInstance();

  private onThemeChange(): void {
    this.colors = ThemeManager.getInstance().getColors();
  }

  aboutToAppear(): void {
    void this.loadAutoSyncSettings();
  }

  private async loadAutoSyncSettings(): Promise<void> {
    try {
      const enabled = await this.webdavStateStore.getAutoSyncEnabled();
      const hours = await this.webdavStateStore.getAutoSyncIntervalHours();
      const uploadModel = await this.webdavStateStore.getAutoSyncUploadModelEnabled();
      const uploadBackup = await this.webdavStateStore.getAutoSyncUploadBackupEnabled();
      const lastSuccess = await this.webdavStateStore.getAutoSyncLastSuccessMs();
      const lastError = await this.webdavStateStore.getAutoSyncLastError();

      this.webdavAutoSyncEnabled = enabled;
      this.webdavAutoSyncUploadModelEnabled = uploadModel;
      this.webdavAutoSyncUploadBackupEnabled = uploadBackup;
      this.webdavAutoSyncLastSuccessMs = lastSuccess;
      this.webdavAutoSyncLastError = lastError;

      const index = WEBDAV_AUTOSYNC_INTERVAL_HOURS.indexOf(hours);
      this.webdavAutoSyncIntervalIndex = index >= 0 ? index : 2;
    } catch (e) {
      console.error('[SettingsSyncSection] Failed to load auto sync settings:', e);
    }
  }

  private async saveWebDavAutoSyncSettings(): Promise<void> {
    await this.webdavStateStore.setAutoSyncEnabled(this.webdavAutoSyncEnabled);
    const hours = WEBDAV_AUTOSYNC_INTERVAL_HOURS[this.webdavAutoSyncIntervalIndex] ?? 6;
    await this.webdavStateStore.setAutoSyncIntervalHours(hours);
    await this.webdavStateStore.setAutoSyncUploadModelEnabled(this.webdavAutoSyncUploadModelEnabled);
    await this.webdavStateStore.setAutoSyncUploadBackupEnabled(this.webdavAutoSyncUploadBackupEnabled);
  }

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
  private buildInputField(fieldId: string, label: string, value: string, placeholder: string, onChange: (val: string) => void) {
    Column() {
      Text(label)
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.GRAY_600)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.XS })

      TextInput({ text: value, placeholder })
        .id(fieldId)
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
  private buildPasswordField(fieldId: string, label: string, value: string, placeholder: string, isVisible: boolean, onChange: (val: string) => void, onToggle: () => void) {
    Column() {
      Text(label)
        .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
        .fontColor(this.colors.GRAY_600)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.XS })

      Row() {
        TextInput({ text: value, placeholder })
        .id(fieldId)
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

  @Builder
  private buildToggleRow(toggleId: string, title: string, subtitle: string, isOn: boolean, onChange: (val: boolean) => void) {
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

      Toggle({ type: ToggleType.Switch, isOn })
        .id(toggleId)
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

      this.buildInputField('webdav_endpoint_input', 'WebDAV 地址', this.webdavEndpoint, 'https://dav.example.com/dav/', (v) => this.webdavEndpoint = v)
      this.buildInputField('webdav_username_input', '账号', this.webdavUsername, 'username', (v) => this.webdavUsername = v)
      this.buildPasswordField('webdav_password_input', '密码', this.webdavPassword, 'password', this.showWebdavPassword, (v) => this.webdavPassword = v, () => this.showWebdavPassword = !this.showWebdavPassword)
      this.buildPasswordField('webdav_sync_password_input', '同步密码（用于 AES 加密）', this.webdavSyncPassword, 'sync password', this.showWebdavSyncPassword, (v) => this.webdavSyncPassword = v, () => this.showWebdavSyncPassword = !this.showWebdavSyncPassword)
      this.buildInputField('webdav_remote_root_input', '远端目录', this.webdavRemoteRoot, '/weiyu_sync', (v) => this.webdavRemoteRoot = v)

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

      this.buildToggleRow('webdav_auto_sync_toggle', '启用自动同步', '进入前台时按间隔自动同步', this.webdavAutoSyncEnabled, (isOn) => {
        this.webdavAutoSyncEnabled = isOn;
        this.saveWebDavAutoSyncSettings();
      })

      if (this.webdavAutoSyncEnabled) {
        Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

        Row() {
          Text('同步间隔')
            .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
            .fontColor(this.colors.GRAY_700)
          Blank()
          Select(WEBDAV_AUTOSYNC_INTERVAL_OPTIONS)
            .selected(this.webdavAutoSyncIntervalIndex)
            .value(WEBDAV_AUTOSYNC_INTERVAL_OPTIONS[this.webdavAutoSyncIntervalIndex].value)
            .font({ size: DesignTokens.Typography.FONT_SIZE_BASE })
            .fontColor(this.colors.GRAY_700)
            .onSelect((index: number) => {
              this.webdavAutoSyncIntervalIndex = index;
              this.saveWebDavAutoSyncSettings();
            })
        }
        .width('100%')
        .height(56)
        .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

        Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

        this.buildToggleRow('webdav_auto_upload_model_toggle', '自动上传模型', '用于多端算法同步', this.webdavAutoSyncUploadModelEnabled, (isOn) => {
          this.webdavAutoSyncUploadModelEnabled = isOn;
          this.saveWebDavAutoSyncSettings();
        })

        Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

        this.buildToggleRow('webdav_auto_upload_backup_toggle', '自动上传全量备份', '只上传，不自动恢复覆盖本地', this.webdavAutoSyncUploadBackupEnabled, (isOn) => {
          this.webdavAutoSyncUploadBackupEnabled = isOn;
          this.saveWebDavAutoSyncSettings();
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

  build() {
    Column() {
      this.buildBasicConfigCard()
      this.buildAutoSyncCard()
      SettingsSyncActions({
        webdavEndpoint: $webdavEndpoint,
        webdavUsername: $webdavUsername,
        webdavPassword: $webdavPassword,
        webdavSyncPassword: $webdavSyncPassword,
        webdavRemoteRoot: $webdavRemoteRoot,
        manualBusy: this.manualBusy,
        manualResult: this.manualResult
      })
    }
    .width('100%')
    .padding(DesignTokens.Spacing.MD)
    .id('webdav_config_page')
  }
}
