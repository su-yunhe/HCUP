import { AppNavDestination } from 'ui';
import MainViewModel from '../viewmodel/MainViewModel';
import { HomePage } from './HomePage';
import { CategoryPage } from './CategoryPage';
import { CartPage } from './CartPage';
import { MePage } from './MePage';
import { TabLottieIcon } from '../component/TabLottieIcon';

interface MainSnapshot { selectedIndex: number; selectionEpoch: number; instanceId: string; }

@ComponentV2
export struct MainPage {
  @Local private vm: MainViewModel = new MainViewModel();
  private pager: SwiperController = new SwiperController();
  private homeScroller: Scroller = new Scroller();
  private pagerBusy: boolean = false;
  private requestInFlight: boolean = false;
  private pendingTab: number = -1;
  private instanceId: string = `main-${Date.now()}`;

  private diagnostic(): string {
    const state: MainSnapshot = { selectedIndex: this.vm.selectedIndex,
      selectionEpoch: this.vm.selectionEpoch, instanceId: this.instanceId };
    return JSON.stringify(state);
  }

  private requestTab(index: number): void {
    if (this.pagerBusy || this.requestInFlight) {
      this.pendingTab = index;
      return;
    }
    if (index === this.vm.selectedIndex) {
      if (index === 0) {
        this.homeScroller.scrollTo({ xOffset: 0, yOffset: 0,
          animation: { duration: 260, curve: Curve.EaseOut } });
      }
      return;
    }
    this.requestInFlight = true;
    this.pager.changeIndex(index, false);
  }

  private drainPending(): void {
    if (this.pagerBusy || this.requestInFlight || this.pendingTab < 0) {
      return;
    }
    const next: number = this.pendingTab;
    this.pendingTab = -1;
    this.requestTab(next);
  }

  @Builder
  private Tab(index: number, key: string, label: string) {
    Column({ space: 3 }) {
      TabLottieIcon({ tabKey: key, selected: this.vm.selectedIndex === index,
        selectionEpoch: this.vm.selectionEpoch, instanceId: this.instanceId })
      Text(label)
        .id(`main_tab_${key}_text`)
        .fontSize(12)
        .fontWeight(this.vm.selectedIndex === index ? FontWeight.Medium : FontWeight.Regular)
        .fontColor(this.vm.selectedIndex === index ? '#000000' : '#808080')
    }
    .id(`main_tab_${key}`)
    .layoutWeight(1)
    .height(60)
    .justifyContent(FlexAlign.Center)
    .accessibilityText(`${label}${this.vm.selectedIndex === index ? '，已选中' : ''}`)
    .accessibilityDescription(`{"selected":${this.vm.selectedIndex === index}}`)
    .onClick(() => this.requestTab(index))
  }

  build() {
    AppNavDestination({ viewModel: this.vm, hideTitleBar: true, pageBackgroundColor: '#F6F7F8' }) {
      Column() {
        Swiper(this.pager) {
          HomePage({ embedded: true, scroller: this.homeScroller })
          CategoryPage({ embedded: true })
          CartPage({ embedded: true })
          MePage({ embedded: true })
        }
        .id('main_content_pager')
        .width('100%')
        .layoutWeight(1)
        .index(this.vm.selectedIndex)
        .loop(false)
        .indicator(false)
        .autoPlay(false)
        .cachedCount(3)
        .vertical(false)
        .duration(260)
        .accessibilityDescription(this.diagnostic())
        .onChange((index: number) => {
          this.vm.commitSelection(index);
          this.requestInFlight = false;
          this.drainPending();
        })
        .onAnimationStart(() => { this.pagerBusy = true; })
        .onAnimationEnd(() => {
          this.pagerBusy = false;
          this.requestInFlight = false;
          this.drainPending();
        })
        Row() {
          this.Tab(0, 'home', '首页');
          this.Tab(1, 'category', '分类');
          this.Tab(2, 'cart', '购物车');
          this.Tab(3, 'me', '我的');
        }
        .id('main_tab_bar')
        .width('100%')
        .height(64)
        .backgroundColor('#FFFFFF')
        .border({ width: { top: 0.5 }, color: '#ECEDEF' })
      }
      .id('main_root')
      .width('100%')
      .height('100%')
      .accessibilityDescription(this.diagnostic())
    }
  }
}
