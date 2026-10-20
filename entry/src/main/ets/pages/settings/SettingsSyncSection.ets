import promptAction from '@ohos.promptAction';
import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { ThemeManager } from '../../manager/ThemeManager';
import { WebDavSyncManager, WebDavSettings, WebDavSyncResult } from '../../sync/WebDavSyncManager';
import { DataSyncManager } from '../../sync/DataSyncManager';
import { SettingsWebDavConfigPanel } from './SettingsWebDavConfigPanel';
import { WebDavRestoreConfirmDialog } from './WebDavRestoreConfirmDialog';

interface DialogIndexResult {
  index: number;
}

enum WebDavRestorePhase {
  READY,
  CONFIRM,
  AUTHORIZED,
  BUSY
}

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
  @State private restorePhase: WebDavRestorePhase = WebDavRestorePhase.READY;
  private restoreDialogClosing: boolean = false;
  private isActive: boolean = false;
  private restoreDialogController: CustomDialogController = new CustomDialogController({
    builder: WebDavRestoreConfirmDialog({
      colors: $colors,
      onCancel: () => this.dismissRestoreConfirmation(false),
      onContinue: () => this.dismissRestoreConfirmation(true)
    }),
    cancel: () => this.onRestoreDialogCancelled(),
    onDidDisappear: () => this.onRestoreDialogClosed(),
    alignment: DialogAlignment.Center,
    autoCancel: true,
    isModal: true,
    showInSubWindow: false
  });

  private webdavManager: WebDavSyncManager = WebDavSyncManager.getInstance();
  private syncManager: DataSyncManager = DataSyncManager.getInstance();

  private onThemeChange(): void {
    this.colors = ThemeManager.getInstance().getColors();
  }

  aboutToAppear(): void {
    this.isActive = true;
  }

  aboutToDisappear(): void {
    this.isActive = false;
    if (this.restorePhase === WebDavRestorePhase.CONFIRM || this.restorePhase === WebDavRestorePhase.AUTHORIZED) {
      this.restorePhase = WebDavRestorePhase.CONFIRM;
      this.restoreDialogClosing = true;
      this.closeRestoreDialog();
    }
  }

  private openRestoreConfirmation(): void {
    if (!this.isActive || this.webdavBusy || this.restorePhase !== WebDavRestorePhase.READY) return;
    this.restorePhase = WebDavRestorePhase.CONFIRM;
    this.restoreDialogClosing = false;
    try {
      this.restoreDialogController.open();
    } catch (e) {
      this.restorePhase = WebDavRestorePhase.READY;
      console.error('[SettingsSyncSection] Failed to open restore confirmation:', e);
    }
  }

  private dismissRestoreConfirmation(authorized: boolean): void {
    if (this.restorePhase !== WebDavRestorePhase.CONFIRM || this.restoreDialogClosing) return;
    if (authorized && (!this.isActive || this.webdavBusy)) return;
    this.restoreDialogClosing = true;
    if (authorized) this.restorePhase = WebDavRestorePhase.AUTHORIZED;
    this.closeRestoreDialog();
  }

  private closeRestoreDialog(): void {
    try {
      this.restoreDialogController.close();
    } catch (e) {
      this.restorePhase = WebDavRestorePhase.CONFIRM;
      this.restoreDialogClosing = false;
      console.error('[SettingsSyncSection] Failed to close restore confirmation:', e);
    }
  }

  private onRestoreDialogCancelled(): void {
    if (this.restorePhase !== WebDavRestorePhase.CONFIRM || this.restoreDialogClosing) return;
    this.restoreDialogClosing = true;
  }

  private onRestoreDialogClosed(): void {
    if (this.restorePhase !== WebDavRestorePhase.CONFIRM && this.restorePhase !== WebDavRestorePhase.AUTHORIZED) return;
    const authorized: boolean = this.restorePhase === WebDavRestorePhase.AUTHORIZED;
    this.restoreDialogClosing = false;
    if (!authorized || !this.isActive || this.webdavBusy) {
      this.restorePhase = WebDavRestorePhase.READY;
      return;
    }
    this.restorePhase = WebDavRestorePhase.BUSY;
    void this.runAuthorizedRestore();
  }

  private async runAuthorizedRestore(): Promise<void> {
    try {
      await this.runWebDavBackupAction(async () => this.webdavRestoreWithPreview());
    } finally {
      this.restorePhase = WebDavRestorePhase.READY;
    }
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
    if (this.webdavBusy) return;
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
    if (this.webdavBusy) return;
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

  private async webdavSyncNow(): Promise<void> {
    if (this.webdavBusy) return;
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

  private async webdavRestoreWithPreview(): Promise<WebDavSyncResult> {
    const download = await this.webdavManager.downloadBackupPlain(false);
    if (!download.result.success) return download.result;
    if (download.plain.length === 0) {
      return WebDavSyncResult.fail('云端无备份', download.result.message || '未找到可用的备份文件');
    }

    const preview = await this.syncManager.previewImport(download.plain);
    if (preview.errors.length > 0) {
      return WebDavSyncResult.fail('预览失败', preview.errors.join('; '));
    }

    const sample = preview.sampleUpdatedWords.length > 0 ? `\n示例：${preview.sampleUpdatedWords.join('、')}` : '';
    const msg = `⚠️ 警告：此操作将覆盖本地数据！\n\n将覆盖更新 ${preview.updated} 词，新增 ${preview.imported} 词，共 ${preview.total} 词。${sample}\n\n本地未同步的学习记录将丢失，请确认是否继续？`;

    try {
      const dialogResult = await promptAction.showDialog({
        title: '⚠️ 恢复确认',
        message: msg,
        buttons: [
          { text: '取消', color: String(this.colors.TEXT_SECONDARY) },
          { text: '确认恢复', color: String(this.colors.ERROR) }
        ]
      });

      const clicked = dialogResult as DialogIndexResult;
      if (clicked.index === 0) {
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
  private buildActionButtonsCard() {
    Column() {
      Text('手动操作')
        .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
        .fontWeight(DesignTokens.Typography.FONT_WEIGHT_MEDIUM)
        .fontColor(this.colors.TEXT_PRIMARY)
        .width('100%')
        .margin({ bottom: DesignTokens.Spacing.MD })

      Row() {
        Button(this.webdavBusy ? '处理中...' : '保存设置')
          .id('webdav_save_button')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.webdavBusy ? this.colors.GRAY_400 : this.colors.GRAY_600)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.webdavBusy)
          .onClick(async () => { await this.saveWebDavSettings(); })

        Button(this.webdavBusy ? '处理中...' : '测试连接')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.webdavBusy ? this.colors.GRAY_400 : this.colors.PRIMARY)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.webdavBusy)
          .margin({ left: DesignTokens.Spacing.SM })
          .onClick(async () => { await this.webdavTest(); })
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

      if (this.webdavResult.length > 0) {
        Text(this.webdavResult)
          .id('webdav_config_result')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.webdavResult.includes('✅') ? this.colors.SUCCESS : this.colors.GRAY_600)
          .margin({ top: DesignTokens.Spacing.SM })
          .textAlign(TextAlign.Center)
      }

      Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Row() {
        Button(this.webdavBusy ? '处理中...' : '立即同步')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.webdavBusy ? this.colors.GRAY_400 : this.colors.PRIMARY)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.webdavBusy)
          .onClick(async () => { await this.webdavSyncNow(); })
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Row() {
        Button(this.webdavBusy ? '处理中...' : '立即备份')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.webdavBusy ? this.colors.GRAY_400 : this.colors.SUCCESS)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.webdavBusy)
          .onClick(async () => { await this.webdavBackup(); })

        Button(this.webdavBusy ? '处理中...' : '从云端恢复')
          .id('webdav_restore_button')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.webdavBusy ? this.colors.GRAY_400 : this.colors.WARNING)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.webdavBusy && this.restorePhase === WebDavRestorePhase.READY)
          .margin({ left: DesignTokens.Spacing.SM })
          .onClick(() => this.openRestoreConfirmation())
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      if (this.webdavBackupResult.length > 0) {
        Text(this.webdavBackupResult)
          .id(this.restorePhase === WebDavRestorePhase.BUSY && this.webdavBusy ? 'webdav_restore_request_loading' : 'webdav_restore_result')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.webdavBackupResult.includes('✅') ? this.colors.SUCCESS : this.colors.GRAY_600)
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

  build() {
    Column() {
      SettingsWebDavConfigPanel({
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
        colors: $colors
      })
      this.buildActionButtonsCard()
    }
    .width('100%')
    .padding(DesignTokens.Spacing.MD)
    .id('webdav_config_panel')
  }
}
