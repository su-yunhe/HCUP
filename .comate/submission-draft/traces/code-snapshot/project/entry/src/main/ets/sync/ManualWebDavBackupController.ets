import { WebDavSettings, WebDavSyncManager, WebDavSyncResult, WebDavSyncStatus } from './WebDavSyncManager';

export class ManualWebDavBackupState {
  runId: number;
  busy: boolean;
  resultText: string;

  constructor(runId: number = 0, busy: boolean = false, resultText: string = '') {
    this.runId = runId;
    this.busy = busy;
    this.resultText = resultText;
  }
}

export type ManualWebDavBackupListener = (state: ManualWebDavBackupState) => void;

// The task belongs to the process; settings pages only observe its state.
export class ManualWebDavBackupController {
  private static instance: ManualWebDavBackupController | null = null;
  private state: ManualWebDavBackupState = new ManualWebDavBackupState();
  private listeners: ManualWebDavBackupListener[] = [];
  private manager: WebDavSyncManager = WebDavSyncManager.getInstance();

  private constructor() {}

  static getInstance(): ManualWebDavBackupController {
    if (ManualWebDavBackupController.instance === null) {
      ManualWebDavBackupController.instance = new ManualWebDavBackupController();
    }
    return ManualWebDavBackupController.instance;
  }

  getState(): ManualWebDavBackupState {
    return new ManualWebDavBackupState(this.state.runId, this.state.busy, this.state.resultText);
  }

  subscribe(listener: ManualWebDavBackupListener): void {
    if (this.listeners.indexOf(listener) < 0) {
      this.listeners.push(listener);
    }
    this.notify(listener);
  }

  unsubscribe(listener: ManualWebDavBackupListener): void {
    this.listeners = this.listeners.filter((item: ManualWebDavBackupListener) => item !== listener);
  }

  private notify(listener: ManualWebDavBackupListener): void {
    try {
      listener(this.getState());
    } catch (error) {
      console.error('[ManualWebDavBackupController] Observer failed:', error);
    }
  }

  private publish(): void {
    for (const listener of this.listeners.slice()) {
      this.notify(listener);
    }
  }

  private validate(settings: WebDavSettings): string {
    if (settings.endpoint.trim().length === 0) return 'WebDAV 地址不能为空';
    if (settings.username.trim().length === 0) return '账号不能为空';
    if (settings.password.trim().length === 0) return '密码不能为空';
    if (settings.syncPassword.trim().length < 4) return '同步密码至少需要4位';
    return '';
  }

  async start(settings: WebDavSettings): Promise<void> {
    if (this.state.busy) return;
    const snapshot: WebDavSettings = new WebDavSettings(
      settings.endpoint.trim(), settings.username.trim(), settings.password, settings.syncPassword,
      settings.remoteRoot.trim().length > 0 ? settings.remoteRoot.trim() : '/weiyu_sync',
      settings.requireRemoteRootExists
    );
    const runId: number = this.state.runId + 1;
    this.state = new ManualWebDavBackupState(runId, true, '正在备份到云端...');
    this.publish();

    let resultText: string = '';
    try {
      const missing: string = this.validate(snapshot);
      if (missing.length > 0) {
        resultText = `⚠️ 配置不完整：${missing}`;
        return;
      }
      const managerStatus: WebDavSyncStatus = this.manager.getStatus();
      if (managerStatus !== WebDavSyncStatus.IDLE && managerStatus !== WebDavSyncStatus.ERROR) {
        resultText = '⚠️ 同步操作正在进行中：请等待当前同步完成后再试';
        return;
      }
      const saved: boolean = await this.manager.setSettings(snapshot);
      if (!saved) {
        resultText = '⚠️ WebDAV 设置保存失败';
        return;
      }
      // Allow the pending state to render without imposing a minimum busy duration.
      await new Promise<void>((resolve) => setTimeout(resolve, 0));
      const result: WebDavSyncResult = await this.manager.backupToCloudInBackground();
      resultText = result.success ? `✅ ${result.message}` : `⚠️ ${result.message}：${result.detail}`;
    } catch (error) {
      const message: string = error instanceof Error ? error.message : String(error);
      resultText = `⚠️ WebDAV 操作异常：${message}`;
    } finally {
      this.state = new ManualWebDavBackupState(runId, false, resultText);
      this.publish();
    }
  }
}
