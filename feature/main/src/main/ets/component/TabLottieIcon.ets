import lottie, { AnimationItem, AnimationConfigWithData } from '@ohos/lottie';
import { util } from '@kit.ArkTS';

interface IconSnapshot {
  ready: boolean;
  frame: number;
  paused: boolean;
  consumedEpoch: number;
  observedPlaySeq: number;
  completeSeq: number;
  instanceId: string;
  error: string;
}

@ComponentV2
export struct TabLottieIcon {
  @Param tabKey: string = '';
  @Param selected: boolean = false;
  @Param selectionEpoch: number = 0;
  @Param instanceId: string = '';
  @Local private description: string = '';
  private context2d: CanvasRenderingContext2D =
    new CanvasRenderingContext2D(new RenderingContextSettings(true));
  private item: AnimationItem | null = null;
  private ready: boolean = false;
  private generation: number = 0;
  private consumedEpoch: number = 0;
  private observedEpoch: number = 0;
  private completedEpoch: number = 0;
  private observedPlaySeq: number = 0;
  private completeSeq: number = 0;
  private failure: string = '';
  private removeListeners: Array<() => void> = [];

  @Monitor('selected', 'selectionEpoch')
  private onSelectionChanged(): void {
    this.reconcile();
  }

  private name(): string {
    return `${this.instanceId}-${this.tabKey}`;
  }

  private snapshot(event: string = ''): void {
    const animation: AnimationItem | null = this.item;
    const state: IconSnapshot = {
      ready: this.ready,
      frame: animation === null ? 0 : animation.currentFrame,
      paused: animation === null ? true : animation.isPaused,
      consumedEpoch: this.consumedEpoch,
      observedPlaySeq: this.observedPlaySeq,
      completeSeq: this.completeSeq,
      instanceId: this.name(),
      error: this.failure
    };
    this.description = JSON.stringify(state);
    if (event.length > 0) {
      console.info(`MainTabsLottie ${this.tabKey} ${event} ${this.description}`);
    }
  }

  private observeFrame(): void {
    const animation: AnimationItem | null = this.item;
    // Count only actual engine frame progression for the current selection.
    if (animation !== null && this.selected && animation.currentFrame > 0 &&
      this.consumedEpoch === this.selectionEpoch && this.observedEpoch !== this.consumedEpoch) {
      this.observedEpoch = this.consumedEpoch;
      this.observedPlaySeq += 1;
      this.snapshot('observedPlay');
    } else {
      this.snapshot();
    }
  }

  private reconcile(): void {
    const animation: AnimationItem | null = this.item;
    if (!this.ready || animation === null) {
      return;
    }
    try {
      if (!this.selected) {
        animation.changeColor([128, 128, 128, 1]);
        animation.goToAndStop(0, true);
        this.snapshot('reset');
      } else if (this.consumedEpoch !== this.selectionEpoch) {
        animation.changeColor([0, 0, 0, 1]);
        animation.loop = false;
        this.consumedEpoch = this.selectionEpoch;
        animation.goToAndPlay(0, true);
        this.snapshot('playRequested');
      }
    } catch (error) {
      this.failure = `control: ${String(error)}`;
      this.snapshot('error');
    }
  }

  private onLoaded(generation: number): void {
    if (generation !== this.generation || this.ready) {
      return;
    }
    this.ready = true;
    this.snapshot('DOMLoaded');
    this.reconcile();
  }

  private async load(): Promise<void> {
    if (this.item !== null) {
      this.item.resize();
      return;
    }
    const generation: number = ++this.generation;
    try {
      const host = this.getUIContext().getHostContext();
      if (host === undefined) {
        throw new Error('Missing resource context');
      }
      const bytes: Uint8Array = await host.resourceManager.getRawFileContent(`lottie/tab_${this.tabKey}.json`);
      if (generation !== this.generation) {
        return;
      }
      const data: Record<string, Object> = JSON.parse(util.TextDecoder.create('utf-8').decodeToString(bytes));
      const config: AnimationConfigWithData = {
        container: this.context2d, renderer: 'canvas', animationData: data,
        autoplay: false, loop: false, name: this.name(), contentMode: 'Contain'
      };
      const animation: AnimationItem = lottie.loadAnimation(config);
      this.item = animation;
      this.removeListeners.push(animation.addEventListener('DOMLoaded', () => this.onLoaded(generation)));
      this.removeListeners.push(animation.addEventListener('drawnFrame', () => {
        if (generation === this.generation) { this.observeFrame(); }
      }));
      this.removeListeners.push(animation.addEventListener('enterFrame', () => {
        if (generation === this.generation) { this.observeFrame(); }
      }));
      this.removeListeners.push(animation.addEventListener('complete', () => {
        if (generation !== this.generation) { return; }
        if (this.selected && this.consumedEpoch === this.selectionEpoch &&
          this.completedEpoch !== this.consumedEpoch) {
          this.completedEpoch = this.consumedEpoch;
          this.completeSeq += 1;
        }
        this.snapshot('complete');
      }));
      this.removeListeners.push(animation.addEventListener('data_failed', () => {
        if (generation === this.generation) {
          this.failure = 'data_failed';
          this.snapshot('error');
        }
      }));
      this.removeListeners.push(animation.addEventListener('error', () => {
        if (generation === this.generation) {
          this.failure = 'engine_error';
          this.snapshot('error');
        }
      }));
      if (animation.isLoaded) { this.onLoaded(generation); }
    } catch (error) {
      if (generation === this.generation) {
        this.failure = `load: ${String(error)}`;
        this.snapshot('error');
      }
    }
  }

  aboutToDisappear(): void {
    this.generation += 1;
    this.removeListeners.forEach((remove: () => void) => remove());
    this.removeListeners = [];
    if (this.item !== null) {
      lottie.destroy(this.name());
      this.item = null;
    }
    this.ready = false;
  }

  build() {
    Canvas(this.context2d)
      .id(`main_tab_${this.tabKey}_icon`)
      .width(32).height(32)
      .accessibilityDescription(this.description)
      .onReady(() => { this.load(); })
  }
}
