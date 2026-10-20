import promptAction from '@ohos.promptAction';
import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { ThemeManager } from '../../manager/ThemeManager';
import { WebDavSyncManager, WebDavSettings, WebDavSyncResult } from '../../sync/WebDavSyncManager';
import { DataSyncManager } from '../../sync/DataSyncManager';
import { WebDavStateStore } from '../../utils/WebDavStateStore';
import { SelectOption } from './SettingsCommon';
import { SettingsSyncConfigCard, SettingsSyncActionsCard } from './SettingsSyncCards';

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

  @State webdavResult: string = '';
  @State webdavBackupResult: string = '';
  @State webdavBusy: boolean = false;
  @State private restoreConfirmPending: boolean = false;

  private restoreRound: number = 0;
  private restoreViewActive: boolean = false;
  private webdavManager: WebDavSyncManager = WebDavSyncManager.getInstance();
  private webdavStateStore: WebDavStateStore = WebDavStateStore.getInstance();
  private syncManager: DataSyncManager = DataSyncManager.getInstance();

  private onThemeChange(): void {
    this.colors = ThemeManager.getInstance().getColors();
  }

  aboutToAppear(): void {
    this.restoreViewActive = true;
    this.restoreRound += 1;
    void this.loadAutoSyncSettings();
  }

  aboutToDisappear(): void {
    this.restoreViewActive = false;
    this.restoreRound += 1;
    this.restoreConfirmPending = false;
  }

  private isCurrentRestoreRound(round: number): boolean {
    return this.restoreViewActive && this.restoreRound === round;
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

  private async saveWebDavSettings(): Promise<boolean> {
    if (this.restoreConfirmPending) return false;
    const s = new WebDavSettings(
      this.webdavEndpoint.trim(),
      this.webdavUsername.trim(),
      this.webdavPassword,
      this.webdavSyncPassword,
      this.webdavRemoteRoot.trim().length > 0 ? this.webdavRemoteRoot.trim() : '/weiyu_sync',
      true
    );
    const saved = await this.webdavManager.setSettings(s);
    this.webdavResult = saved ? '✅ WebDAV 设置已保存' : '⚠️ WebDAV 设置保存失败';
    return saved;
  }

  private readonly OPERATION_TIMEOUT = 120000; // 120秒超时

  private async runWithTimeout<T>(operation: () => Promise<T>, timeoutMs: number): Promise<T> {
    return Promise.race([
      operation(),
      new Promise<T>((_, reject) => {
        setTimeout(() => reject(new Error('操作超时，请检查网络连接')), timeoutMs);
      })
    ]);
  }

  private async runWebDavAction(fn: () => Promise<WebDavSyncResult>): Promise<void> {
    if (this.webdavBusy || this.restoreConfirmPending) return;
    this.webdavBusy = true;
    try {
      const res = await this.runWithTimeout(fn, this.OPERATION_TIMEOUT);
      this.webdavResult = res.success ? `✅ ${res.message}` : `⚠️ ${res.message}：${res.detail}`;
      promptAction.showToast({ message: res.message, duration: 1200 });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      this.webdavResult = `⚠️ WebDAV 操作异常：${msg}`;
      promptAction.showToast({ message: 'WebDAV 操作异常', duration: 1200 });
    } finally {
      this.webdavBusy = false;
    }
  }

  private async runWebDavBackupAction(fn: () => Promise<WebDavSyncResult>): Promise<void> {
    if (this.webdavBusy || this.restoreConfirmPending) return;
    this.webdavBusy = true;
    this.webdavBackupResult = '正在处理...';

    await new Promise<void>((resolve) => setTimeout(resolve, 50));

    try {
      const res = await this.runWithTimeout(fn, this.OPERATION_TIMEOUT);
      this.webdavBackupResult = res.success ? `✅ ${res.message}` : `⚠️ ${res.message}：${res.detail}`;
      promptAction.showToast({ message: res.message, duration: 1200 });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      this.webdavBackupResult = `⚠️ WebDAV 操作异常：${msg}`;
      promptAction.showToast({ message: 'WebDAV 操作异常', duration: 1200 });
    } finally {
      this.webdavBusy = false;
    }
  }

  private async webdavBackup(): Promise<void> {
    await this.runWebDavBackupAction(async () => this.webdavManager.backupToCloudInBackground());
  }

  private async webdavRestore(): Promise<void> {
    if (this.webdavBusy || this.restoreConfirmPending || !this.restoreViewActive) return;
    this.restoreConfirmPending = true;
    const round: number = ++this.restoreRound;
    try {
      const dialogResult: promptAction.ShowDialogSuccessResponse =
        await this.getUIContext().getPromptAction().showDialog({
          title: '恢复确认',
          message: '继续后将连接 WebDAV 并下载云端备份。下载完成后可预览数据，再确认是否覆盖本地数据。',
          buttons: [
            { text: '取消', color: String(this.colors.TEXT_SECONDARY) },
            { text: '继续', color: String(this.colors.WARNING) }
          ]
        });
      if (dialogResult.index !== 1 || !this.isCurrentRestoreRound(round) || !this.restoreConfirmPending) return;
      this.restoreConfirmPending = false;
      await this.runWebDavBackupAction(async (): Promise<WebDavSyncResult> => this.webdavRestoreWithPreview(round));
    } catch {
      // 取消、关闭或弹窗异常均不授予恢复权限。
    } finally {
      if (this.restoreRound === round) {
        this.restoreConfirmPending = false;
        this.restoreRound += 1;
      }
    }
  }

  private async webdavSyncNow(): Promise<void> {
    if (this.webdavBusy || this.restoreConfirmPending) return;
    this.webdavBusy = true;
    this.webdavResult = '正在同步...';

    // 使用更长的延迟确保 UI 更新
    await new Promise<void>((resolve) => setTimeout(resolve, 100));

    try {
      const saved = await this.saveWebDavSettings();
      if (!saved) {
        this.webdavResult = '⚠️ 保存设置失败，请先保存 WebDAV 设置';
        promptAction.showToast({ message: '保存设置失败', duration: 1200 });
        return;
      }

      // 给 UI 线程时间响应
      await new Promise<void>((resolve) => setTimeout(resolve, 50));

      const res = await this.runWithTimeout(() => this.webdavManager.syncIncremental(), this.OPERATION_TIMEOUT);
      this.webdavResult = res.success ? `✅ ${res.message}` : `⚠️ ${res.message}：${res.detail}`;
      promptAction.showToast({ message: res.message, duration: 1200 });
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      this.webdavResult = `⚠️ WebDAV 操作异常：${msg}`;
      promptAction.showToast({ message: 'WebDAV 操作异常', duration: 1200 });
    } finally {
      this.webdavBusy = false;
    }
  }

  private async webdavRestoreWithPreview(round: number): Promise<WebDavSyncResult> {
    if (!this.isCurrentRestoreRound(round)) return WebDavSyncResult.ok('已取消恢复');
    const download = await this.webdavManager.downloadBackupPlain(false);
    if (!this.isCurrentRestoreRound(round)) return WebDavSyncResult.ok('已取消恢复');
    if (!download.result.success) return download.result;
    if (download.plain.length === 0) {
      return WebDavSyncResult.fail('云端无备份', download.result.message || '未找到可用的备份文件');
    }

    const preview = await this.syncManager.previewImport(download.plain);
    if (!this.isCurrentRestoreRound(round)) return WebDavSyncResult.ok('已取消恢复');
    if (preview.errors.length > 0) {
      return WebDavSyncResult.fail('预览失败', preview.errors.join('; '));
    }

    const sample = preview.sampleUpdatedWords.length > 0 ? `\n示例：${preview.sampleUpdatedWords.join('、')}` : '';
    const msg = `⚠️ 警告：此操作将覆盖本地数据！\n\n将覆盖更新 ${preview.updated} 词，新增 ${preview.imported} 词，共 ${preview.total} 词。${sample}\n\n本地未同步的学习记录将丢失，请确认是否继续？`;

    try {
      const dialogResult: promptAction.ShowDialogSuccessResponse = await this.getUIContext().getPromptAction().showDialog({
        title: '⚠️ 恢复确认',
        message: msg,
        buttons: [
          { text: '取消', color: String(this.colors.TEXT_SECONDARY) },
          { text: '确认恢复', color: String(this.colors.ERROR) }
        ]
      });

      if (dialogResult.index !== 1 || !this.isCurrentRestoreRound(round)) {
        return WebDavSyncResult.ok('已取消恢复');
      }
      return await this.webdavManager.importPlainBackup(download.plain);
    } catch (e) {
      return WebDavSyncResult.ok('已取消恢复');
    }
  }

  private async webdavTest(): Promise<void> {
    await this.runWebDavAction(async () => {
      const settings = new WebDavSettings(
        this.webdavEndpoint.trim(),
        this.webdavUsername.trim(),
        this.webdavPassword,
        this.webdavSyncPassword,
        this.webdavRemoteRoot.trim().length > 0 ? this.webdavRemoteRoot.trim() : '/weiyu_sync',
        true
      );
      const missing = this.validateSettings(settings);
      if (missing.length > 0) {
        return WebDavSyncResult.fail('配置不完整', missing);
      }
      this.webdavManager.setSettings(settings);
      return this.webdavManager.testConnection();
    });
  }

  private validateSettings(settings: WebDavSettings): string {
    if (settings.endpoint.length === 0) return 'WebDAV 地址不能为空';
    if (settings.username.length === 0) return '账号不能为空';
    if (settings.password.length === 0) return '密码不能为空';
    if (settings.syncPassword.length < 4) return '同步密码至少需要4位';
    return '';
  }

  @Builder
  private buildToggleRow(title: string, subtitle: string, isOn: boolean, onChange: (val: boolean) => void, toggleId: string): void {
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
  private buildAutoSyncCard(): void {
    Column() {
      Text('自动同步')
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontWeight(DesignTokens.Typography.FONT_WEIGHT_MEDIUM)
        .fontColor(this.colors.TEXT_PRIMARY)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.MD })

      this.buildToggleRow('启用自动同步', '进入前台时按间隔自动同步', this.webdavAutoSyncEnabled, (isOn) => {
        this.webdavAutoSyncEnabled = isOn;
        this.saveWebDavAutoSyncSettings();
      }, 'webdavAutoSyncToggle')

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

        this.buildToggleRow('自动上传模型', '用于多端算法同步', this.webdavAutoSyncUploadModelEnabled, (isOn) => {
          this.webdavAutoSyncUploadModelEnabled = isOn;
          this.saveWebDavAutoSyncSettings();
        }, 'webdavAutoSyncUploadModelToggle')

        Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

        this.buildToggleRow('自动上传全量备份', '只上传，不自动恢复覆盖本地', this.webdavAutoSyncUploadBackupEnabled, (isOn) => {
          this.webdavAutoSyncUploadBackupEnabled = isOn;
          this.saveWebDavAutoSyncSettings();
        }, 'webdavAutoSyncUploadBackupToggle')

        Text(`上次自动同步：${this.formatWebDavAutoSyncLastSuccess()}${this.webdavAutoSyncLastError.length > 0 ? `\n最近错误：${this.webdavAutoSyncLastError}` : ''}`)
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.webdavAutoSyncLastError.length > 0 ? this.colors.WARNING : this.colors.GRAY_500)
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

  build(): void {
    Column() {
      SettingsSyncConfigCard({
        webdavEndpoint: $webdavEndpoint, webdavUsername: $webdavUsername,
        webdavPassword: $webdavPassword, webdavSyncPassword: $webdavSyncPassword,
        webdavRemoteRoot: $webdavRemoteRoot, showWebdavPassword: $showWebdavPassword,
        showWebdavSyncPassword: $showWebdavSyncPassword
      })
      this.buildAutoSyncCard()
      SettingsSyncActionsCard({
        busy: this.webdavBusy, confirmPending: this.restoreConfirmPending,
        result: this.webdavResult, backupResult: this.webdavBackupResult,
        onSave: (): void => { void this.saveWebDavSettings(); },
        onTest: (): void => { void this.webdavTest(); },
        onSyncNow: (): void => { void this.webdavSyncNow(); },
        onBackup: (): void => { void this.webdavBackup(); },
        onRestore: (): void => { void this.webdavRestore(); }
      })
    }
    .width('100%')
    .padding(DesignTokens.Spacing.MD)
    .id('webdavConfigSection')
  }
}
