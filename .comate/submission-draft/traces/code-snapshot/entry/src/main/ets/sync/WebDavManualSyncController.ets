import promptAction from '@ohos.promptAction';
import { WebDavSettings, WebDavSyncManager, WebDavSyncResult, WebDavSyncStatus } from './WebDavSyncManager';

export class ManualWebDavSyncSnapshot {
  operationId: number;
  busy: boolean;
  result: string;

  constructor(operationId: number = 0, busy: boolean = false, result: string = '') {
    this.operationId = operationId;
    this.busy = busy;
    this.result = result;
  }
}

type ManualSyncListener = (snapshot: ManualWebDavSyncSnapshot) => void;

// Owns the operation independently of the settings page and its UI subscriptions.
export class WebDavManualSyncController {
  private static instance: WebDavManualSyncController | null = null;
  private snapshot: ManualWebDavSyncSnapshot = new ManualWebDavSyncSnapshot();
  private listeners: Map<number, ManualSyncListener> = new Map<number, ManualSyncListener>();
  private nextSubscriptionId: number = 1;
  private activeOperation: Promise<void> | null = null;
  private manager: WebDavSyncManager = WebDavSyncManager.getInstance();

  private constructor() {}

  static getInstance(): WebDavManualSyncController {
    if (WebDavManualSyncController.instance === null) {
      WebDavManualSyncController.instance = new WebDavManualSyncController();
    }
    return WebDavManualSyncController.instance;
  }

  getSnapshot(): ManualWebDavSyncSnapshot {
    return new ManualWebDavSyncSnapshot(this.snapshot.operationId, this.snapshot.busy, this.snapshot.result);
  }

  subscribe(listener: ManualSyncListener): number {
    const subscriptionId: number = this.nextSubscriptionId++;
    this.listeners.set(subscriptionId, listener);
    listener(this.getSnapshot());
    console.info(`[WebDavManualSync] subscribe=${subscriptionId} op=${this.snapshot.operationId}`);
    return subscriptionId;
  }

  unsubscribe(subscriptionId: number): void {
    this.listeners.delete(subscriptionId);
    console.info(`[WebDavManualSync] unsubscribe=${subscriptionId}`);
  }

  start(settings: WebDavSettings, prepareVisibleFrame: () => Promise<void>): boolean {
    if (this.snapshot.busy || this.activeOperation !== null) {
      console.info(`[WebDavManualSync] rejected while op=${this.snapshot.operationId} is busy`);
      return false;
    }
    if (this.manager.getStatus() === WebDavSyncStatus.SYNCING) {
      this.showToast('同步操作正在进行中');
      return false;
    }
    const operationId: number = this.snapshot.operationId + 1;
    const settingsCopy: WebDavSettings = new WebDavSettings(settings.endpoint, settings.username,
      settings.password, settings.syncPassword, settings.remoteRoot, settings.requireRemoteRootExists);
    this.snapshot = new ManualWebDavSyncSnapshot(operationId, true, '正在同步数据...');
    this.publish();
    console.info(`[WebDavManualSync] accepted op=${operationId} time=${Date.now()}`);
    try {
      // Invoke immediately; the controller keeps only the returned Promise, never the UI callback.
      const frameReady: Promise<void> = prepareVisibleFrame();
      this.activeOperation = this.run(operationId, settingsCopy, frameReady);
    } catch (error) {
      this.finish(operationId, this.exceptionResult(error instanceof Error ? error.message : String(error)));
    }
    return true;
  }

  private async run(operationId: number, settings: WebDavSettings, frameReady: Promise<void>): Promise<void> {
    let result: string = '';
    try {
      await frameReady;
      console.info(`[WebDavManualSync] visible frame ready op=${operationId} time=${Date.now()}`);
      if (this.manager.getStatus() === WebDavSyncStatus.SYNCING) {
        result = '⚠️ 同步操作正在进行中：请等待当前同步完成后再试';
        this.showToast('同步操作正在进行中');
        return;
      }
      const saved: boolean = await this.manager.setSettings(settings);
      if (!saved) {
        result = '⚠️ 保存设置失败，请先保存 WebDAV 设置';
        this.showToast('保存设置失败');
        return;
      }
      // Busy belongs to this real Promise, including every request and all intermediate work.
      const response: WebDavSyncResult = await this.manager.syncIncremental();
      result = response.success ? `✅ ${response.message}` : `⚠️ ${response.message}：${response.detail}`;
      this.showToast(response.message);
    } catch (error) {
      result = this.exceptionResult(error instanceof Error ? error.message : String(error));
    } finally {
      this.finish(operationId, result);
    }
  }

  private exceptionResult(message: string): string {
    console.error(`[WebDavManualSync] operation failed: ${message}`);
    this.showToast('WebDAV 操作异常');
    return `⚠️ WebDAV 操作异常：${message}`;
  }

  private finish(operationId: number, result: string): void {
    if (this.snapshot.operationId !== operationId) {
      return;
    }
    this.activeOperation = null;
    this.snapshot = new ManualWebDavSyncSnapshot(operationId, false, result);
    console.info(`[WebDavManualSync] settled op=${operationId} time=${Date.now()}`);
    this.publish();
  }

  private publish(): void {
    this.listeners.forEach((listener: ManualSyncListener) => {
      try {
        listener(this.getSnapshot());
      } catch (error) {
        console.error('[WebDavManualSync] UI subscriber failed');
      }
    });
  }

  private showToast(message: string): void {
    try {
      promptAction.showToast({ message, duration: 1200 });
    } catch (error) {
      console.warn('[WebDavManualSync] Toast unavailable');
    }
  }
}
