import { navigateBack } from "navigation";
import { AppNavDestination } from "ui";
import { AddressRegionPicker } from "../component/AddressRegionPicker";
import { RegionSelection } from "../model/AddressRegion";
import AddressDetailViewModel from "../viewmodel/AddressDetailViewModel";

@ComponentV2
export struct AddressDetailPage {
  @Local private vm: AddressDetailViewModel = new AddressDetailViewModel();

  build() {
    AppNavDestination({ title: this.vm.title, hideTitleBar: true, viewModel: this.vm, onBackPressed: (): boolean => this.vm.handleBack() }) {
      Stack() {
        Column({ space: 16 }) {
          Row() {
            Button("返回").id("address_form_back").enabled(!this.vm.isSaving).onClick((): void => {
              if (!this.vm.handleBack()) {
                navigateBack();
              }
            });
            Text(this.vm.title).fontSize(22).fontWeight(FontWeight.Bold).layoutWeight(1)
              .textAlign(TextAlign.Center).id("address_form_title");
            Blank().width(64);
          }.width("100%");
          if (this.vm.isLoading) {
            Column({ space: 12 }) {
              LoadingProgress().width(36).height(36);
              Text("加载地址中");
            }.layoutWeight(1).justifyContent(FlexAlign.Center).id("address_detail_loading");
          } else if (!this.vm.isReady) {
            Column({ space: 12 }) {
              Text(this.vm.loadError).id("address_detail_error");
              Button("重试").id("address_detail_retry").onClick((): void => { this.vm.loadDetail(); });
            }.layoutWeight(1).justifyContent(FlexAlign.Center);
          } else {
            Scroll() {
              Column({ space: 16 }) {
                this.Label("联系人");
                TextInput({ text: this.vm.contact, placeholder: "请填写联系人" })
                  .id("address_contact_input").enabled(!this.vm.isSaving && !this.vm.awaitingVerification)
                  .onChange((value: string): void => { this.vm.contact = value; this.vm.clearError(); });
                this.Label("手机号");
                TextInput({ text: this.vm.phone, placeholder: "请填写手机号" }).type(InputType.Normal)
                  .id("address_phone_input").enabled(!this.vm.isSaving && !this.vm.awaitingVerification)
                  .onChange((value: string): void => { this.vm.phone = value; this.vm.clearError(); });
                this.Label("所在地区");
                Button(this.vm.regionText || "请选择所在地区", { type: ButtonType.Normal })
                  .width("100%").height(48).fontSize(16).fontColor($r("app.color.text_primary"))
                  .backgroundColor($r("app.color.bg_grey")).borderRadius(12)
                  .id("address_region_input").enabled(!this.vm.isSaving && !this.vm.awaitingVerification)
                  .onClick((): void => this.vm.openRegion());
                this.Label("详细地址");
                TextArea({ text: this.vm.address, placeholder: "街道、楼牌号等" }).height(100)
                  .id("address_detail_input").enabled(!this.vm.isSaving && !this.vm.awaitingVerification)
                  .onChange((value: string): void => { this.vm.address = value; this.vm.clearError(); });
                Row() {
                  Text("设为默认地址").fontSize(16).layoutWeight(1);
                  Toggle({ type: ToggleType.Switch, isOn: this.vm.isDefault })
                    .id("address_default_switch").enabled(!this.vm.isSaving && !this.vm.awaitingVerification)
                    .onChange((value: boolean): void => { this.vm.isDefault = value; this.vm.clearError(); });
                }.width("100%");
              }.width("100%").alignItems(HorizontalAlign.Start).padding(16)
                .backgroundColor($r("app.color.bg_white")).borderRadius(12).id("address_form_ready");
            }.width("100%").layoutWeight(1).id("address_form_scroll");
            if (this.vm.error) {
              Text(this.vm.error).width("100%").fontColor(Color.Red).id("address_form_error");
            }
            if (this.vm.isSaving) {
              LoadingProgress().width(30).height(30).id("address_save_loading");
            }
            if (this.vm.awaitingVerification) {
              Button("重试同步").width("100%").enabled(!this.vm.isSaving)
                .id("address_verify_retry").onClick((): void => { this.vm.retryVerification(); });
            }
            Button(this.vm.isEditMode ? "保存" : "保存地址")
              .id("address_save_button").width("100%").height(48)
              .enabled(!this.vm.isSaving && !this.vm.awaitingVerification)
              .onClick((): void => { this.vm.save(); });
          }
        }.width("100%").height("100%").padding(16).id("address_form_page");
        if (this.vm.pickerVisible) {
          AddressRegionPicker({
            selection: this.vm.pickerSelection,
            onConfirm: (value: RegionSelection): void => this.vm.confirmRegion(value),
            onCancel: (): void => { this.vm.pickerVisible = false; }
          });
        }
      }.width("100%").height("100%");
    }
  }

  @Builder
  private Label(value: string): void {
    Row({ space: 4 }) {
      Text(value).fontSize(16).fontColor($r("app.color.text_primary"));
      Text("*").fontSize(16).fontColor(Color.Red);
    }
  }
}
