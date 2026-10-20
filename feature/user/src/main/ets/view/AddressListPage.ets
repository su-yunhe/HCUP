import { BaseNetWorkListUiState } from "base";
import { Address } from "model";
import { navigateBack } from "navigation";
import { AddressActionButton, AddressCard, AppNavDestination, RefreshLayout } from "ui";
import AddressListViewModel from "../viewmodel/AddressListViewModel";

@ComponentV2
export struct AddressListPage {
  @Local private vm: AddressListViewModel = new AddressListViewModel();
  private listScroller: Scroller = new Scroller();

  build() {
    AppNavDestination({ title: "收货地址", hideTitleBar: true, viewModel: this.vm, onBackPressed: (): boolean => this.vm.handleBack() }) {
      Stack({ alignContent: Alignment.Center }) {
        Column({ space: 12 }) {
          Row() {
            Button("返回").id("address_list_back").onClick((): void => {
              if (!this.vm.handleBack()) {
                navigateBack();
              }
            });
            Blank();
            Text("收货地址").fontSize(20).fontWeight(FontWeight.Bold);
            Blank();
            Button("刷新").enabled(!this.vm.isLoading && !this.vm.isDeleting).onClick((): void => this.vm.retryRequest());
          }.width("100%");
          if (this.vm.syncError) {
            Column({ space: 6 }) {
              Text(this.vm.syncError).id("address_list_sync_error").fontColor($r("app.color.text_subtitle"));
              Button("重试同步").id("address_list_sync_retry").enabled(!this.vm.isLoading)
                .onClick((): void => this.vm.retryRequest());
            }.width("100%");
          }
          if (this.vm.uiState === BaseNetWorkListUiState.LOADING) {
            Column({ space: 12 }) {
              LoadingProgress().width(36).height(36);
              Text("加载地址中");
            }.id("address_list_loading").layoutWeight(1).justifyContent(FlexAlign.Center);
          } else if (this.vm.uiState === BaseNetWorkListUiState.ERROR) {
            Column({ space: 12 }) {
              Text(this.vm.error).id("address_list_error");
              Button("重试").id("address_list_retry").onClick((): void => this.vm.retryRequest());
            }.layoutWeight(1).justifyContent(FlexAlign.Center);
          } else if (this.vm.uiState === BaseNetWorkListUiState.EMPTY) {
            Column({ space: 12 }) {
              Text("还没有收货地址").id("address_list_empty");
              Text("点击下方按钮新增地址").fontColor($r("app.color.text_subtitle"));
            }.layoutWeight(1).justifyContent(FlexAlign.Center);
          } else {
            Column() {
            RefreshLayout({
              loading: this.vm.isLoading, isEnableSlideUp: false, scroller: this.listScroller,
              onRefresh: (direction): void => this.vm.onRefreshDirection(direction)
            }) {
              List({ space: 12, scroller: this.listScroller }) {
                ForEach(this.vm.listData, (item: Address): void => {
                  ListItem() {
                    AddressCard({
                      address: item, cardId: `address_row_${item.id}`,
                      onTap: (): void => this.vm.onAddressClick(item),
                      actionSlot: (): void => this.Actions(item)
                    });
                  }
                }, (item: Address): string => `${item.id}:${JSON.stringify(item)}`);
              }.width("100%").height("100%").id("address_list");
            }
            }.width("100%").layoutWeight(1);
          }
          Button("新增地址")
            .id("address_add_button")
            .width("100%")
            .height(48)
            .enabled(!this.vm.navigationBusy && !this.vm.isDeleting && !this.vm.deleteTarget)
            .onClick((): void => this.vm.onAddAddress());
        }.width("100%").height("100%").padding(16).id("address_list_page");
        if (this.vm.deleteTarget) {
          this.DeleteDialog();
        }
      }.width("100%").height("100%");
    }
  }

  @Builder
  private Actions(item: Address): void {
    Row({ space: 10 }) {
      AddressActionButton({
        iconResId: $r("app.media.ic_edit_fill"), actionId: `address_edit_${item.id}`, actionLabel: "编辑地址",
        onTap: (): void => this.vm.onEditAddress(item.id)
      });
      AddressActionButton({
        iconResId: $r("app.media.ic_delete_fill"), actionId: `address_delete_${item.id}`, actionLabel: "删除地址",
        onTap: (): void => this.vm.onDeleteAddress(item.id)
      });
    }
  }

  @Builder
  private DeleteDialog(): void {
    Stack() {
      Column().width("100%").height("100%").backgroundColor("#66000000")
        .onClick((): void => this.vm.cancelDelete());
      Column({ space: 20 }) {
        Text("确认删除该地址吗？").fontSize(20).id("address_delete_message");
        if (this.vm.error) {
          Text(this.vm.error).fontColor(Color.Red);
        }
        if (this.vm.isDeleting) {
          LoadingProgress().width(32).height(32).id("address_delete_loading");
        }
        Row({ space: 20 }) {
          Button("取消").id("address_delete_cancel").enabled(!this.vm.isDeleting)
            .onClick((): void => this.vm.cancelDelete());
          Button(this.vm.deleteUncertain ? "重试同步" : "确认")
            .id("address_delete_confirm").enabled(!this.vm.isDeleting)
            .onClick((): void => {
              if (this.vm.deleteUncertain) {
                this.vm.verifyDelete();
              } else {
                this.vm.confirmDelete();
              }
            });
        }
      }.padding(24).width("85%").backgroundColor($r("app.color.bg_white")).borderRadius(16)
        .id("address_delete_dialog");
    }.width("100%").height("100%");
  }
}
