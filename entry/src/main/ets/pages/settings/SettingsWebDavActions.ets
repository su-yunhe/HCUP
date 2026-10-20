import promptAction from '@ohos.promptAction';
import { PromptAction } from '@ohos.arkui.UIContext';
import { DesignTokens } from '../../model/DesignTokens';
import { ColorsInterface } from '../../model/TokenInterfaces';
import { ThemeManager } from '../../manager/ThemeManager';
import { WebDavSyncManager, WebDavSettings, WebDavSyncResult } from '../../sync/WebDavSyncManager';
import { DataSyncManager } from '../../sync/DataSyncManager';
import { WebDavRestoreConfirmDialog } from './WebDavRestoreConfirmDialog';

interface DialogIndexResult {
  index: number;
}

enum RestorePhase {
  IDLE,
  AWAITING_CONFIRMATION,
  RUNNING
}

@Component
export struct SettingsWebDavActions {
  @Link webdavEndpoint: string;
  @Link webdavUsername: string;
  @Link webdavPassword: string;
  @Link webdavSyncPassword: string;
  @Link webdavRemoteRoot: string;
  @Prop @Watch('onPageActiveChange') pageActive: boolean = true;
  @StorageProp('ThemeRefreshToken') @Watch('onThemeChange') themeRefreshToken: number = 0;
  @State private colors: ColorsInterface = ThemeManager.getInstance().getColors();
  @State private webdavResult: string = '';
  @State private webdavBackupResult: string = '';
  @State private webdavBusy: boolean = false;
  @State private restorePhase: RestorePhase = RestorePhase.IDLE;
  private attached: boolean = false;
  private restoreTicket: number = 0;
  private restoreDialogId: number | undefined = undefined;
  private restorePrompt: PromptAction | undefined = undefined;
  private webdavManager: WebDavSyncManager = WebDavSyncManager.getInstance();
  private syncManager: DataSyncManager = DataSyncManager.getInstance();

  private onThemeChange(): void {
    this.colors = ThemeManager.getInstance().getColors();
  }

  aboutToAppear(): void {
    this.attached = true;
  }

  aboutToDisappear(): void {
    this.attached = false;
    this.cancelRestoreConfirmation(this.restoreTicket);
  }

  private onPageActiveChange(): void {
    if (!this.pageActive) this.cancelRestoreConfirmation(this.restoreTicket);
  }

  private isActionLocked(): boolean {
    return this.webdavBusy || this.restorePhase !== RestorePhase.IDLE;
  }

  private isWaitingTicket(ticket: number): boolean {
    return this.restoreTicket === ticket && this.restorePhase === RestorePhase.AWAITING_CONFIRMATION;
  }

  private closeRestoreDialog(): boolean {
    const dialogId: number | undefined = this.restoreDialogId;
    const prompt: PromptAction | undefined = this.restorePrompt;
    this.restoreDialogId = undefined;
    this.restorePrompt = undefined;
    if (dialogId === undefined || prompt === undefined) return true;
    try {
      prompt.closeCustomDialog(dialogId);
      return true;
    } catch (error) {
      console.error('[SettingsWebDavActions] Failed to close restore confirmation:', error);
      return false;
    }
  }

  private cancelRestoreConfirmation(ticket: number, closeDialog: boolean = true): void {
    if (!this.isWaitingTicket(ticket)) return;
    this.restoreTicket += 1;
    this.restorePhase = RestorePhase.IDLE;
    if (closeDialog) {
      this.closeRestoreDialog();
    } else {
      this.restoreDialogId = undefined;
      this.restorePrompt = undefined;
    }
  }

  private continueRestore(ticket: number): void {
    if (!this.attached || !this.pageActive || !this.isWaitingTicket(ticket)) return;
    this.restorePhase = RestorePhase.RUNNING;
    if (!this.closeRestoreDialog()) {
      this.restoreTicket += 1;
      this.restorePhase = RestorePhase.IDLE;
      return;
    }
    void this.runConfirmedRestore(ticket);
  }

  private async runConfirmedRestore(ticket: number): Promise<void> {
    try {
      await this.runWebDavBackupAction(async () => this.webdavRestoreWithPreview());
    } finally {
      if (this.restoreTicket === ticket && this.restorePhase === RestorePhase.RUNNING) {
        this.restorePhase = RestorePhase.IDLE;
      }
    }
  }

  @Builder
  private buildRestoreConfirmation(ticket: number) {
    WebDavRestoreConfirmDialog({
      colors: this.colors,
      onCancel: () => this.cancelRestoreConfirmation(ticket),
      onContinue: () => this.continueRestore(ticket)
    })
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
    if (this.isActionLocked()) return;
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
    if (this.webdavBusy || this.restorePhase === RestorePhase.AWAITING_CONFIRMATION) return;
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
    if (this.isActionLocked()) return;
    await this.runWebDavBackupAction(async () => this.webdavManager.backupToCloudInBackground());
  }

  private async webdavRestore(): Promise<void> {
    if (!this.attached || !this.pageActive || this.isActionLocked()) return;
    const ticket: number = ++this.restoreTicket;
    this.restorePhase = RestorePhase.AWAITING_CONFIRMATION;
    try {
      const prompt: PromptAction = this.getUIContext().getPromptAction();
      const dialogId: number = await prompt.openCustomDialog({
        builder: () => { this.buildRestoreConfirmation(ticket); },
        autoCancel: true,
        isModal: true,
        showInSubWindow: false,
        alignment: DialogAlignment.Center,
        width: '90%',
        backgroundColor: this.colors.SURFACE_PRIMARY,
        cornerRadius: DesignTokens.BorderRadius.LG,
        onWillDismiss: (action) => {
          this.cancelRestoreConfirmation(ticket, false);
          action.dismiss();
        },
        onDidDisappear: () => this.cancelRestoreConfirmation(ticket, false)
      });
      if (!this.attached || !this.pageActive || !this.isWaitingTicket(ticket)) {
        prompt.closeCustomDialog(dialogId);
        return;
      }
      this.restoreDialogId = dialogId;
      this.restorePrompt = prompt;
    } catch (error) {
      this.cancelRestoreConfirmation(ticket);
      console.error('[SettingsWebDavActions] Failed to open restore confirmation:', error);
    }
  }

  private async webdavSyncNow(): Promise<void> {
    if (this.isActionLocked()) return;
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
          .enabled(!this.isActionLocked())
          .onClick(async () => { if (!this.isActionLocked()) await this.saveWebDavSettings(); })

        Button(this.webdavBusy ? '处理中...' : '测试连接')
          .id('webdav_test_button')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.webdavBusy ? this.colors.GRAY_400 : this.colors.PRIMARY)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.isActionLocked())
          .margin({ left: DesignTokens.Spacing.SM })
          .onClick(async () => { await this.webdavTest(); })
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG })

      if (this.webdavResult.length > 0) {
        Text(this.webdavResult)
          .id('webdav_sync_result')
          .fontSize(DesignTokens.Typography.FONT_SIZE_SM)
          .fontColor(this.webdavResult.includes('✅') ? this.colors.SUCCESS : this.colors.GRAY_600)
          .margin({ top: DesignTokens.Spacing.SM })
          .textAlign(TextAlign.Center)
      }

      Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Row() {
        Button(this.webdavBusy ? '处理中...' : '立即同步')
          .id('webdav_sync_button')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.webdavBusy ? this.colors.GRAY_400 : this.colors.PRIMARY)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.isActionLocked())
          .onClick(async () => { await this.webdavSyncNow(); })
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Divider().color(this.colors.GRAY_200).margin({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      Row() {
        Button(this.webdavBusy ? '处理中...' : '立即备份')
          .id('webdav_backup_button')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.webdavBusy ? this.colors.GRAY_400 : this.colors.SUCCESS)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.isActionLocked())
          .onClick(async () => { await this.webdavBackup(); })

        Button(this.webdavBusy ? '处理中...' : '从云端恢复')
          .id('webdav_restore_button')
          .layoutWeight(1)
          .height(44)
          .fontSize(DesignTokens.Typography.FONT_SIZE_BASE)
          .fontColor(this.colors.WHITE)
          .backgroundColor(this.webdavBusy ? this.colors.GRAY_400 : this.colors.WARNING)
          .borderRadius(DesignTokens.BorderRadius.MD)
          .enabled(!this.isActionLocked())
          .margin({ left: DesignTokens.Spacing.SM })
          .onClick(async () => { await this.webdavRestore(); })
      }
      .width('100%')
      .padding({ left: DesignTokens.Spacing.LG, right: DesignTokens.Spacing.LG, top: DesignTokens.Spacing.MD })

      if (this.webdavBackupResult.length > 0) {
        Text(this.webdavBackupResult)
          .id('webdav_backup_result')
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
    this.buildActionButtonsCard()
  }
}
