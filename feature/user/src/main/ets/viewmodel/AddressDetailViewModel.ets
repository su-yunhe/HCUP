import { IBestCascaderOption, IBestFormController, IBestFormRule, IBestStringNumber } from "ibestui";
import { BaseNetWorkUiState, BaseNetWorkViewModel } from "base";
import { AddressRepository } from "data";
import { Address, NetworkResponse } from "model";
import { RefreshResult, UserAddressDetailParam, getRouteParams, navigateBackWithResult } from "navigation";
import { UserRoutes } from "navigation/src/main/ets/user/UserRoutes";
import { RequestHelper } from "result";
import { RegionData } from "../data/RegionData";

/**
 * @file 地址详情页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class AddressDetailViewModel extends BaseNetWorkViewModel<Address> {
  /**
   * 地址仓库
   */
  private readonly repository: AddressRepository = new AddressRepository();
  /**
   * 路由参数
   */
  private readonly routeParam: UserAddressDetailParam =
    getRouteParams<UserAddressDetailParam>(UserRoutes.AddressDetail) ?? {};
  /**
   * 地址 ID
   */
  private readonly addressId: number = this.routeParam.addressId ?? 0;
  /**
   * 是否编辑模式
   */
  readonly isEditMode: boolean = this.routeParam.isEditMode ?? false;
  /**
   * 表单控制器
   */
  readonly formController: IBestFormController = new IBestFormController();
  /**
   * 表单校验规则
   */
  readonly formRules: IBestFormRule = {
    contact: [
      { required: true, message: $r("app.string.please_input_contact") }
    ],
    phone: [
      { required: true, message: $r("app.string.please_input_phone") },
      { pattern: /^1[3-9]\d{9}$/, message: $r("app.string.invalid_phone_number") }
    ],
    region: [
      { required: true, message: $r("app.string.please_select_region") }
    ],
    detailAddress: [
      { required: true, message: $r("app.string.please_input_detail_address") }
    ]
  };
  /**
   * 地区选择弹窗是否可见
   */
  @Trace
  isRegionPickerVisible: boolean = false;
  /**
   * 省市区数据
   */
  readonly regionOptions: IBestCascaderOption[] = RegionData.getRegionOptions();
  /**
   * 联系人
   */
  @Trace
  contactName: string = "";
  /**
   * 手机号
   */
  @Trace
  phone: string = "";
  /**
   * 省
   */
  @Trace
  province: string = "";
  /**
   * 市
   */
  @Trace
  city: string = "";
  /**
   * 区
   */
  @Trace
  district: string = "";
  /**
   * 省市区展示文本
   */
  @Trace
  regionDisplay: string = "";
  /**
   * 省市区选择值
   */
  @Trace
  regionValue: Array<string> = [];
  /**
   * 详细地址
   */
  @Trace
  detailAddress: string = "";
  /**
   * 是否默认地址
   */
  @Trace
  isDefaultAddress: boolean = false;
  /**
   * 保存中状态
   */
  @Trace
  isSaving: boolean = false;

  /**
   * 页面出现生命周期
   * @returns {void} 无返回值
   */
  aboutToAppear(): void {
    if (this.shouldLoadAddress()) {
      this.executeRequest();
      return;
    }
    this.initCreateMode();
  }

  /**
   * 是否显示底部保存按钮
   * @returns {boolean} 是否显示
   */
  shouldShowBottomButton(): boolean {
    return this.uiState === BaseNetWorkUiState.SUCCESS;
  }

  /**
   * 请求地址详情
   * @returns {Promise<NetworkResponse<Address>>} 地址详情响应
   */
  protected requestRepository(): Promise<NetworkResponse<Address>> {
    return this.repository.getAddressInfo(this.addressId);
  }

  /**
   * 点击保存按钮
   * @returns {void} 无返回值
   */
  onSaveTap(): void {
    if (this.isSaving) {
      return;
    }
    this.formController.validate().then((result) => {
      if (!result.valid) {
        return;
      }
      this.saveAddress();
    });
  }

  /**
   * 更新联系人
   * @param {string} value - 联系人
   * @returns {void} 无返回值
   */
  updateContactName(value: string): void {
    this.contactName = value;
  }

  /**
   * 更新手机号
   * @param {string} value - 手机号
   * @returns {void} 无返回值
   */
  updatePhone(value: string): void {
    this.phone = value;
  }

  /**
   * 处理地区选择确认
   * @param {IBestCascaderOption[]} selectedOptions - 选中的地区
   * @returns {void} 无返回值
   */
  handleRegionConfirm(selectedOptions: IBestCascaderOption[]): void {
    this.isRegionPickerVisible = false;
    const labels: string[] = selectedOptions.map((item: IBestCascaderOption): string => {
      return `${item.text ?? ""}`;
    });
    const values: Array<string> = selectedOptions.map((item: IBestCascaderOption): string => {
      return `${item.value ?? ""}`;
    });
    const province: string = labels[0] ?? "";
    const city: string = labels[1] ?? "";
    const district: string = labels[2] ?? "";
    this.updateRegionWithValue(province, city, district, values);
  }

  /**
   * 点击地区选择入口
   * @returns {void} 无返回值
   */
  onRegionFieldClick(): void {
    this.isRegionPickerVisible = true;
  }

  /**
   * 更新地区选择弹窗可见状态
   * @param {boolean} visible - 是否可见
   * @returns {void} 无返回值
   */
  updateRegionPickerVisible(visible: boolean): void {
    this.isRegionPickerVisible = visible;
  }

  /**
   * 处理默认地址开关变化
   * @param {boolean | IBestStringNumber} value - 选中值
   * @returns {void} 无返回值
   */
  handleDefaultSwitchChange(value: boolean | IBestStringNumber): void {
    const isDefault: boolean = value === true || value === 1 || value === "1" || value === "on";
    this.updateIsDefaultAddress(isDefault);
  }

  /**
   * 更新省市区
   * @param {string} province - 省
   * @param {string} city - 市
   * @param {string} district - 区
   * @returns {void} 无返回值
   */
  updateRegion(province: string, city: string, district: string): void {
    this.province = province;
    this.city = city;
    this.district = district;
    this.updateRegionValue();
    this.refreshRegionDisplay();
  }

  /**
   * 更新省市区（包含选择值）
   * @param {string} province - 省
   * @param {string} city - 市
   * @param {string} district - 区
   * @param {Array<string>} valuePath - 级联值路径
   * @returns {void} 无返回值
   */
  updateRegionWithValue(province: string, city: string, district: string, valuePath: Array<string>): void {
    this.province = province;
    this.city = city;
    this.district = district;
    this.regionValue = valuePath;
    this.refreshRegionDisplay();
  }

  /**
   * 更新详细地址
   * @param {string} value - 详细地址
   * @returns {void} 无返回值
   */
  updateDetailAddress(value: string): void {
    this.detailAddress = value;
  }

  /**
   * 更新默认地址状态
   * @param {boolean} value - 是否默认
   * @returns {void} 无返回值
   */
  updateIsDefaultAddress(value: boolean): void {
    this.isDefaultAddress = value;
  }

  /**
   * 请求成功回调，回填表单数据
   * @param {Address} data - 地址数据
   * @returns {void} 无返回值
   */
  protected onRequestSuccess(data: Address): void {
    this.updateFormData(new Address(data));
    super.onRequestSuccess(data);
  }

  /**
   * 初始化新增模式数据
   * @returns {void} 无返回值
   */
  private initCreateMode(): void {
    this.updateFormData(new Address());
    this.setSuccessState();
  }

  /**
   * 是否需要请求地址详情
   * @returns {boolean} 是否请求
   */
  private shouldLoadAddress(): boolean {
    return this.isEditMode && this.addressId > 0;
  }

  /**
   * 回填表单数据
   * @param {Address} address - 地址数据
   * @returns {void} 无返回值
   */
  private updateFormData(address: Address): void {
    this.contactName = address.contact ?? "";
    this.phone = address.phone ?? "";
    this.province = address.province ?? "";
    this.city = address.city ?? "";
    this.district = address.district ?? "";
    this.detailAddress = address.address ?? "";
    this.isDefaultAddress = address.isDefault ?? false;
    this.updateRegionValue();
    this.refreshRegionDisplay();
  }

  /**
   * 刷新省市区展示文本
   * @returns {void} 无返回值
   */
  private refreshRegionDisplay(): void {
    if (this.province && this.city && this.district) {
      this.regionDisplay = `${this.province} ${this.city} ${this.district}`;
      return;
    }
    this.regionDisplay = "";
  }

  /**
   * 根据名称更新级联值路径
   * @returns {void} 无返回值
   */
  private updateRegionValue(): void {
    this.regionValue = RegionData.getRegionValuePath(this.province, this.city, this.district);
  }

  /**
   * 保存地址
   * @returns {void} 无返回值
   */
  private saveAddress(): void {
    const address: Address = new Address();
    address.id = this.isEditMode ? this.addressId : 0;
    address.contact = this.contactName;
    address.phone = this.phone;
    address.province = this.province;
    address.city = this.city;
    address.district = this.district;
    address.address = this.detailAddress;
    address.isDefault = this.isDefaultAddress;

    if (this.isEditMode) {
      this.updateAddress(address);
      return;
    }
    this.addAddress(address);
  }

  /**
   * 更新地址
   * @param {Address} address - 地址数据
   * @returns {void} 无返回值
   */
  private updateAddress(address: Address): void {
    RequestHelper.repository(this.repository.updateAddress(address))
      .start((): void => {
        this.isSaving = true;
      })
      .execute()
      .then((): void => {
        this.onSaveSuccess();
      })
      .finally((): void => {
        this.isSaving = false;
      });
  }

  /**
   * 新增地址
   * @param {Address} address - 地址数据
   * @returns {void} 无返回值
   */
  private addAddress(address: Address): void {
    RequestHelper.repository(this.repository.addAddress(address))
      .start((): void => {
        this.isSaving = true;
      })
      .execute()
      .then((): void => {
        this.onSaveSuccess();
      })
      .finally((): void => {
        this.isSaving = false;
      });
  }

  /**
   * 保存成功处理
   * @returns {void} 无返回值
   */
  private onSaveSuccess(): void {
    const result: RefreshResult = { refresh: true };
    navigateBackWithResult(result);
  }
}
