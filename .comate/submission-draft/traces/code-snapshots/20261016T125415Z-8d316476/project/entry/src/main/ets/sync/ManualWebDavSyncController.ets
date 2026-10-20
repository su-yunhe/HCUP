import { WebDavSettings, WebDavSyncManager, WebDavSyncResult, WebDavSyncStatus } from './WebDavSyncManager';

export class ManualWebDavSyncSnapshot {
  readonly running: boolean;
  readonly resultText: string;
  readonly toastMessage: string;

  constructor(running: boolean = false, resultText: string = '', toastMessage: string = '') {
    this.running = running;
    this.resultText = resultText;
    this.toastMessage = toastMessage;
  }
}

export type ManualWebDavSyncListener = (state: ManualWebDavSyncSnapshot) => void;

// Owns the task for this process. Pages only subscribe while they are mounted.
export class ManualWebDavSyncController {
  private static instance: ManualWebDavSyncController | null = null;
  private snapshot: ManualWebDavSyncSnapshot = new ManualWebDavSyncSnapshot();
  private listeners: Map<number, ManualWebDavSyncListener> = new Map<number, ManualWebDavSyncListener>();
  private nextToken: number = 0;
  private manager: WebDavSyncManager = WebDavSyncManager.getInstance();

  private constructor() {}

  static getInstance(): ManualWebDavSyncController {
    if (ManualWebDavSyncController.instance === null) {
      ManualWebDavSyncController.instance = new ManualWebDavSyncController();
    }
    return ManualWebDavSyncController.instance;
  }

  getSnapshot(): ManualWebDavSyncSnapshot {
    return this.snapshot;
  }

  subscribe(listener: ManualWebDavSyncListener): number {
    const token: number = this.nextToken++;
    this.listeners.set(token, listener);
    this.notifyListener(listener);
    return token;
  }

  unsubscribe(token: number): void {
    this.listeners.delete(token);
  }

  start(settings: WebDavSettings): void {
    if (this.snapshot.running) return;
    const status: WebDavSyncStatus = this.manager.getStatus();
    if (status === WebDavSyncStatus.SYNCING || status === WebDavSyncStatus.TESTING ||
      status === WebDavSyncStatus.RESTORING) {
      this.publish(new ManualWebDavSyncSnapshot(false, '⚠️ 同步操作正在进行中：请等待当前操作完成后再试'));
      return;
    }

    const frozenSettings: WebDavSettings = new WebDavSettings(settings.endpoint, settings.username, settings.password,
      settings.syncPassword, settings.remoteRoot, settings.requireRemoteRootExists);
    // Set the guard synchronously, before saving settings or awaiting any work.
    this.publish(new ManualWebDavSyncSnapshot(true, '正在同步数据...'));
    void this.run(frozenSettings);
  }

  private async run(settings: WebDavSettings): Promise<void> {
    let resultText: string = '';
    let toastMessage: string = '';
    try {
      const saved: boolean = await this.manager.setSettings(settings);
      if (!saved) {
        resultText = '⚠️ 保存设置失败，请先保存 WebDAV 设置';
        toastMessage = '保存设置失败';
        return;
      }
      // This is the actual operation: a UI timeout must never end its loading state.
      const result: WebDavSyncResult = await this.manager.syncIncremental();
      resultText = result.success ? `✅ ${result.message}` : `⚠️ ${result.message}：${result.detail}`;
      toastMessage = result.message;
    } catch (e) {
      const message: string = e instanceof Error ? e.message : String(e);
      resultText = `⚠️ WebDAV 操作异常：${message}`;
      toastMessage = 'WebDAV 操作异常';
    } finally {
      this.publish(new ManualWebDavSyncSnapshot(false, resultText, toastMessage));
    }
  }

  private publish(snapshot: ManualWebDavSyncSnapshot): void {
    this.snapshot = snapshot;
    this.listeners.forEach((listener: ManualWebDavSyncListener) => this.notifyListener(listener));
  }

  private notifyListener(listener: ManualWebDavSyncListener): void {
    try {
      listener(this.snapshot);
    } catch (e) {
      console.error('[ManualWebDavSyncController] Failed to notify subscriber:', e);
    }
  }
}
