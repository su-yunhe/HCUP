import { BaseViewModel } from 'base';

@ObservedV2
export default class MainViewModel extends BaseViewModel {
  @Trace selectedIndex: number = 0;
  @Trace selectionEpoch: number = 1;

  // Only Swiper.onChange commits. Initialization already owns epoch 1.
  commitSelection(index: number): boolean {
    if (index < 0 || index > 3 || index === this.selectedIndex) {
      return false;
    }
    this.selectedIndex = index;
    this.selectionEpoch += 1;
    return true;
  }
}
