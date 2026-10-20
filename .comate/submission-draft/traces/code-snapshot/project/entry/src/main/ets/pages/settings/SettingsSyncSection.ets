import promptAction from '@ohos.promptAction';
import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { ThemeManager } from '../../manager/ThemeManager';
import { WebDavSyncManager, WebDavSettings, WebDavSyncResult, WebDavBackupPlainResult } from '../../sync/WebDavSyncManager';
import { DataSyncManager } from '../../sync/DataSyncManager';
import { WebDavStateStore } from '../../utils/WebDavStateStore';
import { WebDavBasicConfigCard, WebDavAutoSyncCard, WebDavActionButtonsCard } from './SettingsWebDavBuilders';
import { ManualWebDavBackupController, ManualWebDavBackupListener, ManualWebDavBackupState } from '../../sync/ManualWebDavBackupController';

interface DialogIndexResult {
  index: number;
}

const WEBDAV_AUTOSYNC_INTERVAL_HOURS: number[] = [1, 3, 6, 12, 24];
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
  @State manualBackupBusy: boolean = false;
  @State restoreDialogShowing: boolean = false; // Bug fix: 防止重复弹出恢复确认对话框

  private webdavManager: WebDavSyncManager = WebDavSyncManager.getInstance();
  private webdavStateStore: WebDavStateStore = WebDavStateStore.getInstance();
  private syncManager: DataSyncManager = DataSyncManager.getInstance();
  private backupController: ManualWebDavBackupController = ManualWebDavBackupController.getInstance();
  private mounted: boolean = false;
  private backupListener: ManualWebDavBackupListener = (state: ManualWebDavBackupState): void => {
    if (!this.mounted) return;
    this.manualBackupBusy = state.busy;
    if (state.runId > 0) {
      this.webdavBackupResult = state.resultText;
    }
  };

  private isWebDavBusy(): boolean {
    return this.webdavBusy || this.manualBackupBusy || this.backupController.getState().busy;
  }

  private onThemeChange(): void {
    this.colors = ThemeManager.getInstance().getColors();
  }

  aboutToAppear(): void {
    this.mounted = true;
    this.backupController.subscribe(this.backupListener);
    void this.loadAutoSyncSettings();
  }

  aboutToDisappear(): void {
    this.mounted = false;
    this.backupController.unsubscribe(this.backupListener);
  }

  private async loadAutoSyncSettings(): Promise<void> {
    try {
      const enabled = await this.webdavStateStore.getAutoSyncEnabled();
      const hours = await this.webdavStateStore.getAutoSyncIntervalHours();
      const uploadModel = await this.webdavStateStore.getAutoSyncUploadModelEnabled();
      const uploadBackup = await this.webdavStateStore.getAutoSyncUploadBackupEnabled();
      const lastSuccess = await this.webdavStateStore.getAutoSyncLastSuccessMs();
      const lastError = await this.webdavStateStore.getAutoSyncLastError();

      if (!this.mounted) return;

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
    if (this.backupController.getState().busy) return false;
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
    if (this.isWebDavBusy()) return;
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

  private webdavBackup(): void {
    if (this.isWebDavBusy() || this.restoreDialogShowing) return;
    const settings: WebDavSettings = new WebDavSettings(
      this.webdavEndpoint, this.webdavUsername, this.webdavPassword,
      this.webdavSyncPassword, this.webdavRemoteRoot, true
    );
    void this.backupController.start(settings);
  }

  private async webdavRestore(): Promise<void> {
    // Bug fix: 检查是否已经在处理中，防止重复触发
    if (this.isWebDavBusy()) {
      return;
    }

    // Bug fix: 防止重复弹出恢复确认对话框
    if (this.restoreDialogShowing) {
      console.warn('[SettingsSyncSection] Restore dialog already showing, skipping duplicate call');
      return;
    }

    // 第一层确认：点击按钮后立即弹出，防止误触
    try {
      const firstConfirm = await promptAction.showDialog({
        title: '从云端恢复',
        message: '⚠️ 警告：此操作将从云端下载备份并覆盖本地数据，本地未同步的学习记录将丢失。\n\n确定要继续吗？',
        buttons: [
          { text: '取消', color: String(this.colors.TEXT_SECONDARY) },
          { text: '继续', color: String(this.colors.WARNING) }
        ]
      });
      const clicked = firstConfirm as DialogIndexResult;
      if (clicked.index === 0) {
        return; // 用户取消，不执行任何操作
      }
    } catch (e) {
      return; // 对话框被关闭，视为取消
    }

    if (this.isWebDavBusy()) return;
    // 开始下载和解析流程，手动管理状态
    this.webdavBusy = true;
    this.restoreDialogShowing = true;
    this.webdavBackupResult = '正在下载云端备份...';
    
    // Yield to UI thread to show download message
    await new Promise<void>((resolve) => setTimeout(resolve, 0));

    let download: WebDavBackupPlainResult | null = null;
    
    try {
      // Step 1: Download backup from cloud
      download = await this.runWithTimeout(() => this.webdavManager.downloadBackupPlain(false), this.OPERATION_TIMEOUT);
      
      if (!download.result.success) {
        this.webdavBackupResult = `⚠️ ${download.result.message}：${download.result.detail}`;
        promptAction.showToast({ message: download.result.message, duration: 1200 });
        this.webdavBusy = false;
        this.restoreDialogShowing = false;
        return;
      }
      
      if (download.plain.length === 0) {
        this.webdavBackupResult = '⚠️ 云端无备份：未找到可用的备份文件';
        promptAction.showToast({ message: '云端无备份', duration: 1200 });
        this.webdavBusy = false;
        this.restoreDialogShowing = false;
        return;
      }

      // Step 2: Parse and preview backup data
      this.webdavBackupResult = '正在解析备份数据...';
      await new Promise<void>((resolve) => setTimeout(resolve, 0));
      
      const preview = await this.syncManager.previewImport(download.plain);
      if (preview.errors.length > 0) {
        this.webdavBackupResult = `⚠️ 预览失败：${preview.errors.join('; ')}`;
        promptAction.showToast({ message: '预览失败', duration: 1200 });
        this.webdavBusy = false;
        this.restoreDialogShowing = false;
        return;
      }

      // Release busy state while waiting for user confirmation
      this.webdavBusy = false;
      this.webdavBackupResult = ''; // Clear loading message before showing dialog

      // Step 3: Show second confirmation dialog with preview data
      const sample = preview.sampleUpdatedWords.length > 0 ? `\n示例：${preview.sampleUpdatedWords.join('、')}` : '';
      const msg = `⚠️ 警告：此操作将覆盖本地数据！\n\n将覆盖更新 ${preview.updated} 词，新增 ${preview.imported} 词，共 ${preview.total} 词。${sample}\n\n本地未同步的学习记录将丢失，请确认是否继续？`;

      let userConfirmed = false;
      try {
        const dialogResult = await promptAction.showDialog({
          title: '⚠️ 恢复确认',
          message: msg,
          buttons: [
            { text: '取消', color: String(this.colors.TEXT_SECONDARY) },
            { text: '确认恢复', color: String(this.colors.ERROR) }
          ]
        });

        const clickedSecond = dialogResult as DialogIndexResult;
        userConfirmed = clickedSecond.index === 1;
      } catch (e) {
        userConfirmed = false;
      }

      if (!userConfirmed) {
        this.webdavBackupResult = '✅ 已取消恢复';
        promptAction.showToast({ message: '已取消恢复', duration: 1200 });
        this.restoreDialogShowing = false;
        return;
      }

      // Step 4: User confirmed, proceed with restore
      this.webdavBusy = true;
      this.webdavBackupResult = '正在恢复数据...';
      await new Promise<void>((resolve) => setTimeout(resolve, 0));

      const importResult = await this.runWithTimeout(() => this.webdavManager.importPlainBackup(download!.plain), this.OPERATION_TIMEOUT);
      this.webdavBackupResult = importResult.success ? `✅ ${importResult.message}` : `⚠️ ${importResult.message}：${importResult.detail}`;
      promptAction.showToast({ message: importResult.message, duration: 1200 });

    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      this.webdavBackupResult = `⚠️ WebDAV 操作异常：${msg}`;
      promptAction.showToast({ message: 'WebDAV 操作异常', duration: 1200 });
    } finally {
      this.webdavBusy = false;
      this.restoreDialogShowing = false;
    }
  }

  private async webdavSyncNow(): Promise<void> {
    if (this.isWebDavBusy()) return;
    this.webdavBusy = true;
    this.webdavResult = '正在同步数据...';

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

  build() {
    Column() {
      WebDavBasicConfigCard({
        colors: this.colors, disabled: this.isWebDavBusy(),
        endpoint: this.webdavEndpoint, username: this.webdavUsername, password: this.webdavPassword,
        syncPassword: this.webdavSyncPassword, remoteRoot: this.webdavRemoteRoot,
        showPassword: this.showWebdavPassword, showSyncPassword: this.showWebdavSyncPassword,
        onEndpointChange: (value: string): void => { if (!this.isWebDavBusy()) this.webdavEndpoint = value; },
        onUsernameChange: (value: string): void => { if (!this.isWebDavBusy()) this.webdavUsername = value; },
        onPasswordChange: (value: string): void => { if (!this.isWebDavBusy()) this.webdavPassword = value; },
        onSyncPasswordChange: (value: string): void => { if (!this.isWebDavBusy()) this.webdavSyncPassword = value; },
        onRemoteRootChange: (value: string): void => { if (!this.isWebDavBusy()) this.webdavRemoteRoot = value; },
        onTogglePassword: (): void => { if (!this.isWebDavBusy()) this.showWebdavPassword = !this.showWebdavPassword; },
        onToggleSyncPassword: (): void => { if (!this.isWebDavBusy()) this.showWebdavSyncPassword = !this.showWebdavSyncPassword; }
      })
      WebDavAutoSyncCard({
        colors: this.colors, enabled: this.webdavAutoSyncEnabled, intervalIndex: this.webdavAutoSyncIntervalIndex,
        uploadModel: this.webdavAutoSyncUploadModelEnabled, uploadBackup: this.webdavAutoSyncUploadBackupEnabled,
        lastSuccessText: this.formatWebDavAutoSyncLastSuccess(), lastError: this.webdavAutoSyncLastError,
        onEnabledChange: (value: boolean): void => {
          this.webdavAutoSyncEnabled = value;
          void this.saveWebDavAutoSyncSettings();
        },
        onIntervalChange: (value: number): void => {
          this.webdavAutoSyncIntervalIndex = value;
          void this.saveWebDavAutoSyncSettings();
        },
        onUploadModelChange: (value: boolean): void => {
          this.webdavAutoSyncUploadModelEnabled = value;
          void this.saveWebDavAutoSyncSettings();
        },
        onUploadBackupChange: (value: boolean): void => {
          this.webdavAutoSyncUploadBackupEnabled = value;
          void this.saveWebDavAutoSyncSettings();
        }
      })
      WebDavActionButtonsCard({
        colors: this.colors, busy: this.isWebDavBusy(), backupBusy: this.manualBackupBusy,
        configResult: this.webdavResult, backupResult: this.webdavBackupResult,
        onSave: (): void => { if (!this.isWebDavBusy()) void this.saveWebDavSettings(); },
        onTest: (): void => { void this.webdavTest(); },
        onSync: (): void => { void this.webdavSyncNow(); },
        onBackup: (): void => { this.webdavBackup(); },
        onRestore: (): void => { void this.webdavRestore(); }
      })
    }
    .id('webdav_settings_section')
    .width('100%')
    .padding(DesignTokens.Spacing.MD)
  }
}
