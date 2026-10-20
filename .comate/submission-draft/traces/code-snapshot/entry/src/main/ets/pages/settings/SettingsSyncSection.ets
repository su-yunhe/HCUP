import promptAction from '@ohos.promptAction';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { ThemeManager } from '../../manager/ThemeManager';
import { WebDavSyncManager, WebDavSettings, WebDavSyncResult, WebDavBackupPlainResult } from '../../sync/WebDavSyncManager';
import { DataSyncManager, ImportPreview } from '../../sync/DataSyncManager';
import { WebDavStateStore } from '../../utils/WebDavStateStore';
import { SettingsSyncView } from './SettingsSyncView';

enum RestorePhase {
  IDLE,
  FIRST_CONFIRM,
  PREPARING,
  DOWNLOADING,
  PREVIEWING,
  SECOND_CONFIRM,
  IMPORTING
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
  @State private restorePhase: RestorePhase = RestorePhase.IDLE;

  private webdavManager: WebDavSyncManager = WebDavSyncManager.getInstance();
  private webdavStateStore: WebDavStateStore = WebDavStateStore.getInstance();
  private syncManager: DataSyncManager = DataSyncManager.getInstance();

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

  private ownsRestore(): boolean {
    return this.restorePhase !== RestorePhase.IDLE;
  }

  private isRestoreWorking(): boolean {
    return this.restorePhase === RestorePhase.PREPARING || this.restorePhase === RestorePhase.DOWNLOADING ||
      this.restorePhase === RestorePhase.PREVIEWING || this.restorePhase === RestorePhase.IMPORTING;
  }

  private async saveWebDavAutoSyncSettings(): Promise<void> {
    if (this.webdavBusy || this.ownsRestore()) return;
    await this.webdavStateStore.setAutoSyncEnabled(this.webdavAutoSyncEnabled);
    const hours = WEBDAV_AUTOSYNC_INTERVAL_HOURS[this.webdavAutoSyncIntervalIndex] ?? 6;
    await this.webdavStateStore.setAutoSyncIntervalHours(hours);
    await this.webdavStateStore.setAutoSyncUploadModelEnabled(this.webdavAutoSyncUploadModelEnabled);
    await this.webdavStateStore.setAutoSyncUploadBackupEnabled(this.webdavAutoSyncUploadBackupEnabled);
  }

  private async saveWebDavSettings(): Promise<boolean> {
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

  private async webdavSave(): Promise<void> {
    if (this.webdavBusy || this.ownsRestore()) return;
    this.webdavBusy = true;
    try {
      await this.saveWebDavSettings();
    } catch (e) {
      const msg: string = e instanceof Error ? e.message : String(e);
      this.webdavResult = `⚠️ WebDAV 操作异常：${msg}`;
    } finally {
      this.webdavBusy = false;
    }
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
    if (this.webdavBusy || this.ownsRestore()) return;
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

  private async runWebDavBackupAction(fn: () => Promise<WebDavSyncResult>, loadingMessage: string = '正在处理...'): Promise<void> {
    if (this.webdavBusy || this.ownsRestore()) return;
    this.webdavBusy = true;
    this.webdavBackupResult = loadingMessage;

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
    await this.runWebDavBackupAction(async () => this.webdavManager.backupToCloudInBackground(), '正在备份到云端...');
  }

  private async webdavRestore(): Promise<void> {
    if (this.webdavBusy || this.ownsRestore()) return;
    this.restorePhase = RestorePhase.FIRST_CONFIRM;
    try {
      try {
        const firstConfirm: promptAction.ShowDialogSuccessResponse = await promptAction.showDialog({
          title: '从云端恢复',
          message: '⚠️ 警告：此操作将从云端下载备份并覆盖本地数据，本地未同步的学习记录将丢失。\n\n确定要继续吗？',
          buttons: [
            { text: '取消', color: String(this.colors.TEXT_SECONDARY) },
            { text: '继续', color: String(this.colors.WARNING) }
          ]
        });
        if (firstConfirm.index !== 1) return;
      } catch {
        return;
      }

      this.restorePhase = RestorePhase.PREPARING;
      this.webdavBackupResult = '正在准备云端恢复...';
      await new Promise<void>((resolve) => setTimeout(resolve, 0));
      const saved: boolean = await this.saveWebDavSettings();
      if (!saved) {
        this.webdavBackupResult = '⚠️ 保存设置失败，请先保存 WebDAV 设置';
        return;
      }

      this.restorePhase = RestorePhase.DOWNLOADING;
      this.webdavBackupResult = '正在下载云端备份...';
      const download: WebDavBackupPlainResult = await this.webdavManager.downloadBackupPlain(false);
      if (!download.result.success) {
        this.webdavBackupResult = `⚠️ ${download.result.message}：${download.result.detail}`;
        promptAction.showToast({ message: download.result.message, duration: 1200 });
        return;
      }
      if (download.plain.length === 0) {
        this.webdavBackupResult = '⚠️ 云端无备份：未找到可用的备份文件';
        promptAction.showToast({ message: '云端无备份', duration: 1200 });
        return;
      }

      this.restorePhase = RestorePhase.PREVIEWING;
      this.webdavBackupResult = '正在解析备份数据...';
      await new Promise<void>((resolve) => setTimeout(resolve, 0));
      const preview: ImportPreview = await this.syncManager.previewImport(download.plain);
      if (preview.errors.length > 0) {
        this.webdavBackupResult = `⚠️ 预览失败：${preview.errors.join('; ')}`;
        promptAction.showToast({ message: '预览失败', duration: 1200 });
        return;
      }

      this.restorePhase = RestorePhase.SECOND_CONFIRM;
      this.webdavBackupResult = '';
      const sample: string = preview.sampleUpdatedWords.length > 0 ? `\n示例：${preview.sampleUpdatedWords.join('、')}` : '';
      const msg: string = `⚠️ 警告：此操作将覆盖本地数据！\n\n将覆盖更新 ${preview.updated} 词，新增 ${preview.imported} 词，共 ${preview.total} 词。${sample}\n\n本地未同步的学习记录将丢失，请确认是否继续？`;
      let userConfirmed: boolean = false;
      try {
        const secondConfirm: promptAction.ShowDialogSuccessResponse = await promptAction.showDialog({
          title: '⚠️ 恢复确认',
          message: msg,
          buttons: [
            { text: '取消', color: String(this.colors.TEXT_SECONDARY) },
            { text: '确认恢复', color: String(this.colors.ERROR) }
          ]
        });
        userConfirmed = secondConfirm.index === 1;
      } catch {
        userConfirmed = false;
      }
      if (!userConfirmed) {
        this.webdavBackupResult = '✅ 已取消恢复';
        promptAction.showToast({ message: '已取消恢复', duration: 1200 });
        return;
      }

      this.restorePhase = RestorePhase.IMPORTING;
      this.webdavBackupResult = '正在恢复数据...';
      await new Promise<void>((resolve) => setTimeout(resolve, 0));
      const importResult: WebDavSyncResult = await this.webdavManager.importPlainBackup(download.plain);
      this.webdavBackupResult = importResult.success ? `✅ ${importResult.message}` : `⚠️ ${importResult.message}：${importResult.detail}`;
      promptAction.showToast({ message: importResult.message, duration: 1200 });
    } catch (e) {
      const msg: string = e instanceof Error ? e.message : String(e);
      this.webdavBackupResult = `⚠️ WebDAV 操作异常：${msg}`;
      promptAction.showToast({ message: 'WebDAV 操作异常', duration: 1200 });
    } finally {
      this.restorePhase = RestorePhase.IDLE;
    }
  }

  private async webdavSyncNow(): Promise<void> {
    if (this.webdavBusy || this.ownsRestore()) return;
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
    SettingsSyncView({
      webdavEndpoint: $webdavEndpoint,
      webdavUsername: $webdavUsername,
      webdavPassword: $webdavPassword,
      webdavSyncPassword: $webdavSyncPassword,
      webdavRemoteRoot: $webdavRemoteRoot,
      showWebdavPassword: $showWebdavPassword,
      showWebdavSyncPassword: $showWebdavSyncPassword,
      webdavAutoSyncEnabled: $webdavAutoSyncEnabled,
      webdavAutoSyncIntervalIndex: $webdavAutoSyncIntervalIndex,
      webdavAutoSyncUploadModelEnabled: $webdavAutoSyncUploadModelEnabled,
      webdavAutoSyncUploadBackupEnabled: $webdavAutoSyncUploadBackupEnabled,
      webdavAutoSyncLastSuccessMs: $webdavAutoSyncLastSuccessMs,
      webdavAutoSyncLastError: $webdavAutoSyncLastError,
      colors: this.colors,
      webdavResult: this.webdavResult,
      webdavBackupResult: this.webdavBackupResult,
      actionsBusy: this.webdavBusy || this.isRestoreWorking(),
      actionsDisabled: this.webdavBusy || this.ownsRestore(),
      restoreWorking: this.isRestoreWorking(),
      onSave: () => { void this.webdavSave(); },
      onTest: () => { void this.webdavTest(); },
      onSync: () => { void this.webdavSyncNow(); },
      onBackup: () => { void this.webdavBackup(); },
      onRestore: () => { void this.webdavRestore(); },
      onAutoSyncChange: () => { void this.saveWebDavAutoSyncSettings(); }
    })
  }
}
