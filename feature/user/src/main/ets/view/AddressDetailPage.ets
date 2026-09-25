import {
  IBestCascader,
  IBestCascaderOption,
  IBestCell,
  IBestCellGroup,
  IBestField,
  IBestFieldValueType,
  IBestForm,
  IBestStringNumber,
  IBestSwitch
} from "ibestui";
import {
  ColumnStart, MediumPaddingVerticalScroll, P100, SpaceVerticalMedium,
} from "designsystem";
import { getWindowSafeAreaState, WindowSafeAreaState } from "state";
import { AppBottomButton, AppNavDestination, BaseNetWorkView } from "ui";
import AddressDetailViewModel from "../viewmodel/AddressDetailViewModel";

/**
 * @file 地址详情页面视图
 * @author Joker.X
 */
@ComponentV2
export struct AddressDetailPage {
  /**
   * 地址详情页面 ViewModel
   */
  @Local
  private vm: AddressDetailViewModel = new AddressDetailViewModel();
  /**
   * 表单 ID
   */
  private formId: string = "address-detail-form";
  /**
   * 当前窗口安全区状态
   */
  @Param
  windowSafeAreaState: WindowSafeAreaState = getWindowSafeAreaState();

  /**
   * 构建地址详情页面
   * @returns {void} 无返回值
   */
  build(): void {
    AppNavDestination({
      title: this.vm.isEditMode
        ? $r("app.string.edit_address")
        : $r("app.string.add_address"),
      viewModel: this.vm,
      paddingValue: {
        top: this.windowSafeAreaState.topInset,
        left: this.windowSafeAreaState.leftInset,
        right: this.windowSafeAreaState.rightInset
      }
    }) {
      ColumnStart({ fillMaxSize: true }) {
        BaseNetWorkView({
          uiState: this.vm.uiState,
          onRetry: (): void => this.vm.retryRequest(),
          content: (): void => this.AddressDetailContent()
        }).layoutWeight(1);

        if (this.vm.shouldShowBottomButton()) {
          AppBottomButton({
            text: $r("app.string.save_address"),
            loading: this.vm.isSaving,
            onTap: (): void => this.vm.onSaveTap()
          });
        }
      }
    }
  }

  /**
   * 地址详情页面内容视图
   * @returns {void} 无返回值
   */
  @Builder
  private AddressDetailContent(): void {
    MediumPaddingVerticalScroll({ fillMaxSize: true }) {
      Column() {
        this.buildFormCard();
        SpaceVerticalMedium();
        this.buildDefaultAddressCard();
      }
      .width(P100)
      .constraintSize({ minHeight: P100 });
    }
  }

  /**
   * 构建基础信息表单
   * @returns {void} 无返回值
   */
  @Builder
  private buildFormCard(): void {
    IBestForm({
      formId: this.formId,
      controller: this.vm.formController,
      rules: this.vm.formRules
    }) {
      IBestCellGroup({
        inset: true,
        radius: $r("app.float.radius_medium"),
        outerMargin: 0
      }) {
        IBestField({
          formId: this.formId,
          prop: "contact",
          value: this.vm.contactName,
          label: $r("app.string.contact_person"),
          placeholder: $r("app.string.please_input_contact"),
          fieldPadding: $r("app.float.space_padding_large"),
          onChange: (value: IBestFieldValueType): void => {
            this.vm.updateContactName(`${value ?? ""}`);
          }
        });

        IBestField({
          formId: this.formId,
          prop: "phone",
          value: this.vm.phone,
          label: $r("app.string.phone_number"),
          placeholder: $r("app.string.please_input_phone"),
          type: "phone",
          fieldPadding: $r("app.float.space_padding_large"),
          onChange: (value: IBestFieldValueType): void => {
            this.vm.updatePhone(`${value ?? ""}`);
          }
        });

        IBestField({
          formId: this.formId,
          prop: "region",
          value: this.vm.regionValue,
          showValue: this.vm.regionDisplay,
          label: $r("app.string.region"),
          placeholder: $r("app.string.please_select_region"),
          isLink: true,
          fieldPadding: $r("app.float.space_padding_large"),
          onFieldClick: (): void => {
            this.vm.onRegionFieldClick();
          }
        });

        IBestField({
          formId: this.formId,
          prop: "detailAddress",
          value: this.vm.detailAddress,
          label: $r("app.string.detail_address"),
          placeholder: $r("app.string.street_number_etc"),
          hasBorder: false,
          autosize: true,
          rows: 4,
          fieldPadding: $r("app.float.space_padding_large"),
          onChange: (value: IBestFieldValueType): void => {
            this.vm.updateDetailAddress(`${value ?? ""}`);
          }
        });
      }
    }

    IBestCascader({
      visible: this.vm.isRegionPickerVisible,
      options: this.vm.regionOptions,
      value: this.vm.regionValue,
      $visible: (visible: boolean): void => {
        this.vm.updateRegionPickerVisible(visible);
      },
      onConfirm: (value: IBestCascaderOption[]): void => {
        this.vm.handleRegionConfirm(value);
      }
    });
  }

  /**
   * 构建默认地址开关卡片
   * @returns {void} 无返回值
   */
  @Builder
  private buildDefaultAddressCard(): void {
    IBestCellGroup({
      inset: true,
      radius: $r("app.float.radius_medium"),
      outerMargin: 0
    }) {
      IBestCell({
        title: $r("app.string.set_default_address"),
        label: $r("app.string.default_address_tip"),
        center: true,
        hasBorder: false,
        cellPadding: $r("app.float.space_padding_large"),
        valueBuilder: (): void => this.buildDefaultAddressSwitch()
      });
    }
  }

  /**
   * 构建默认地址开关
   * @returns {void} 无返回值
   */
  @Builder
  private buildDefaultAddressSwitch(): void {
    IBestSwitch({
      value: this.vm.isDefaultAddress,
      onChange: (value: boolean | IBestStringNumber): void => {
        this.vm.handleDefaultSwitchChange(value);
      }
    });
  }
}
