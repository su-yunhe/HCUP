import { BaseNetWorkListUiState } from "base";
import { ColumnBase, ColumnStart, P100 } from "designsystem";
import { Address } from "model";
import { UserNavigator } from "navigation";
import { getWindowSafeAreaState, WindowSafeAreaState } from "state";
import {
  AddressActionButton,
  AddressCard,
  AppBottomButton,
  AppNavDestination,
  BaseNetWorkListView,
  RefreshLayout
} from "ui";
import AddressListViewModel from "../viewmodel/AddressListViewModel";

/**
 * @file 地址列表页面视图
 * @author Joker.X
 */
@ComponentV2
export struct AddressListPage {
  /**
   * 地址列表页面 ViewModel
   */
  @Local
  private vm: AddressListViewModel = new AddressListViewModel();
  /**
   * 列表滚动控制器，用于刷新同步
   */
  private listScroller: Scroller = new Scroller();
  /**
   * 当前窗口安全区状态
   */
  @Param
  windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();

  /**
   * 构建地址列表页面
   * @returns {void} 无返回值
   */
  build() {
    AppNavDestination({
      title: $r("app.string.address_list_title"),
      viewModel: this.vm,
      paddingValue: {
        top: this.windowSafeAreaState.topInset,
        left: this.windowSafeAreaState.leftInset,
        right: this.windowSafeAreaState.rightInset,
      }
    }) {
      ColumnStart({ fillMaxSize: true }) {
        BaseNetWorkListView({
          uiState: this.vm.uiState,
          onRetry: (): void => this.vm.retryRequest(),
          content: (): void => this.AddressListContent()
        }).layoutWeight(1);

        if (this.vm.shouldShowBottomButton()) {
          AppBottomButton({
            text: $r("app.string.address_add_new"),
            onTap: (): void => UserNavigator.toAddressDetail()
          });
        }
      }
    }
  }

  /**
   * 地址列表页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private AddressListContent() {
    RefreshLayout({
      loading: this.vm.isLoading,
      isEnableSlideUp: this.vm.isEnableSlideUp,
      scroller: this.listScroller,
      onRefresh: (direction): void => this.vm.onRefreshDirection(direction),
    }) {
      List({ space: 12, scroller: this.listScroller }) {
        ForEach(this.vm.listData, (item: Address): void => {
          ListItem() {
            this.AddressListItem(item);
          }
        }, (item: Address): string => `${item.id}`);
      }
      .width(P100)
      .height(P100)
      .padding($r("app.float.space_padding_medium"));
    }
  }

  /**
   * 渲染地址列表项
   * @param {Address} item - 地址数据
   * @returns {void} 无返回值
   */
  @Builder
  private AddressListItem(item: Address): void {
    AddressCard({
      address: item,
      onTap: (): void => this.vm.onAddressClick(item),
      actionSlot: (): void => this.AddressActionSlot(item)
    });
  }

  /**
   * 渲染地址操作区域
   * @param {Address} item - 地址数据
   * @returns {void} 无返回值
   */
  @Builder
  private AddressActionSlot(item: Address): void {
    Row({ space: 8 }) {
      AddressActionButton({
        iconResId: $r("app.media.ic_edit_fill"),
        onTap: (): void => this.vm.onEditAddress(item.id)
      });

      AddressActionButton({
        iconResId: $r("app.media.ic_delete_fill"),
        onTap: (): void => this.vm.onDeleteAddress(item.id)
      });
    }
  }
}
