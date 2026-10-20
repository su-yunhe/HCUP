import { BaseViewModel } from "base";
import { AddressRepository } from "data";
import { Address, Id, NetworkResponse } from "model";
import {
  AddressSaveOperation, getRouteParams, navigateBackWithResult,
  UserAddressDetailParam, UserAddressSaveResult
} from "navigation";
import { ValidationUtil } from "util";
import { addressError, isAddress, sameAddressFields } from "../model/AddressResponse";
import { findRegion, RegionSelection, resolveRegion } from "../model/AddressRegion";

@ObservedV2
export default class AddressDetailViewModel extends BaseViewModel {
  @Trace contact: string = "";
  @Trace phone: string = "";
  @Trace province: string = "";
  @Trace city: string = "";
  @Trace district: string = "";
  @Trace address: string = "";
  @Trace isDefault: boolean = false;
  @Trace isEditMode: boolean = false;
  @Trace isLoading: boolean = false;
  @Trace isReady: boolean = false;
  @Trace isSaving: boolean = false;
  @Trace loadError: string = "";
  @Trace error: string = "";
  @Trace pickerVisible: boolean = false;
  @Trace awaitingVerification: boolean = false;
  private repository: AddressRepository;
  private originalAddress: Address | null = null;
  private regionSelection: RegionSelection = new RegionSelection();
  private addressId: number = 0;
  private knownIds: number[] = [];
  private hasCompleteSnapshot: boolean = false;
  private pendingPayload: Address | null = null;
  private disposed: boolean = false;
  private generation: number = 0;
  private hasReturned: boolean = false;

  constructor(repository: AddressRepository = new AddressRepository()) {
    super();
    this.repository = repository;
  }

  aboutToAppear(): void {
    const params: UserAddressDetailParam | undefined = getRouteParams<UserAddressDetailParam | undefined>("user/address-detail");
    this.initialize(params);
  }

  initialize(params?: UserAddressDetailParam): void {
    this.isEditMode = params?.isEditMode === true;
    this.addressId = params?.addressId ?? 0;
    this.knownIds = params?.knownAddressIds?.slice() ?? [];
    this.hasCompleteSnapshot = params?.hasCompleteAddressSnapshot === true;
    if (this.isEditMode) {
      if (!Number.isInteger(this.addressId) || this.addressId <= 0) {
        this.loadError = "地址参数无效，请返回列表重试";
        return;
      }
      this.loadDetail();
    } else {
      this.isReady = true;
    }
  }

  async loadDetail(): Promise<void> {
    if (this.isLoading || this.isSaving || this.disposed || !this.isEditMode || this.addressId <= 0) {
      return;
    }
    const epoch: number = ++this.generation;
    this.isLoading = true;
    this.loadError = "";
    try {
      const response: NetworkResponse<Address> = await this.repository.getAddressInfo(this.addressId);
      if (!this.isCurrent(epoch)) {
        return;
      }
      if (response?.code !== 1000 || !isAddress(response.data) || response.data?.id !== this.addressId) {
        this.loadError = response?.message || "地址详情加载失败，请重试";
        return;
      }
      const saved: Address = new Address(response.data);
      this.originalAddress = new Address(saved);
      this.contact = saved.contact;
      this.phone = saved.phone;
      this.province = saved.province;
      this.city = saved.city;
      this.district = saved.district;
      this.address = saved.address;
      this.isDefault = saved.isDefault;
      this.regionSelection = findRegion(saved.province, saved.city, saved.district);
      this.isReady = true;
    } catch (error) {
      if (this.isCurrent(epoch)) {
        this.loadError = addressError(error);
      }
    } finally {
      if (this.isCurrent(epoch)) {
        this.isLoading = false;
      }
    }
  }

  get title(): string {
    return this.isEditMode ? "编辑地址" : "新增地址";
  }

  get regionText(): string {
    return [this.province, this.city, this.district].filter((value: string): boolean => value.length > 0).join(" ");
  }

  get pickerSelection(): RegionSelection {
    return findRegion(this.province, this.city, this.district);
  }

  openRegion(): void {
    if (this.isReady && !this.isSaving && !this.awaitingVerification) {
      this.pickerVisible = true;
    }
  }

  confirmRegion(selection: RegionSelection): void {
    const valid: RegionSelection | null = resolveRegion(selection.provinceCode, selection.cityCode, selection.districtCode);
    if (!valid || this.isSaving) {
      return;
    }
    this.regionSelection = valid;
    this.province = valid.province;
    this.city = valid.city;
    this.district = valid.district;
    this.pickerVisible = false;
    this.clearError();
  }

  clearError(): void {
    if (!this.awaitingVerification) {
      this.error = "";
    }
  }

  handleBack(): boolean {
    if (this.isSaving) {
      return true;
    }
    if (this.pickerVisible) {
      this.pickerVisible = false;
      return true;
    }
    return false;
  }

  validate(): boolean {
    const original: Address | null = this.originalAddress;
    if (!this.contact.trim().length) {
      this.error = "请填写联系人";
    } else if ((!this.isEditMode || this.phone !== original?.phone) && !this.phone.trim().length) {
      this.error = "请填写手机号";
    } else if ((!this.isEditMode || this.phone !== original?.phone) && !ValidationUtil.isValidPhone(this.phone)) {
      this.error = "手机号格式不正确";
    } else if (!this.regionIsUnchanged() && !resolveRegion(this.regionSelection.provinceCode, this.regionSelection.cityCode, this.regionSelection.districtCode)) {
      this.error = "请选择完整的所在地区";
    } else if ((!this.isEditMode || this.address !== original?.address) && !this.address.trim().length) {
      this.error = "请填写详细地址";
    } else {
      this.error = "";
      return true;
    }
    return false;
  }

  private regionIsUnchanged(): boolean {
    const original: Address | null = this.originalAddress;
    return this.isEditMode && original !== null && this.province === original.province &&
      this.city === original.city && this.district === original.district;
  }

  private payload(): Address {
    const result: Address = this.originalAddress ? new Address(this.originalAddress) : new Address();
    result.contact = this.contact;
    result.phone = this.phone;
    result.province = this.province;
    result.city = this.city;
    result.district = this.district;
    result.address = this.address;
    result.isDefault = this.isDefault;
    return result;
  }

  async save(): Promise<void> {
    if (!this.isReady || this.isSaving || this.awaitingVerification || this.hasReturned || this.disposed || !this.validate()) {
      return;
    }
    const payload: Address = this.payload();
    const epoch: number = ++this.generation;
    this.pendingPayload = new Address(payload);
    this.isSaving = true;
    try {
      if (this.isEditMode) {
        const response: NetworkResponse<void> = await this.repository.updateAddress(payload);
        if (!this.isCurrent(epoch)) {
          return;
        }
        if (response?.code === 1000) {
          this.finish(payload);
        } else {
          this.error = response?.message || "保存失败，请重试";
        }
      } else {
        const response: NetworkResponse<Id> = await this.repository.addAddress(payload);
        if (!this.isCurrent(epoch)) {
          return;
        }
        if (response?.code !== 1000) {
          this.error = response?.message || "保存失败，请重试";
        } else if (response.data && Number.isInteger(response.data.id) && response.data.id > 0) {
          payload.id = response.data.id;
          this.finish(payload);
        } else {
          this.awaitingVerification = true;
          await this.verifyPending(epoch);
        }
      }
    } catch (error) {
      if (this.isCurrent(epoch)) {
        // A lost response can follow a committed write. Read before another write.
        this.awaitingVerification = true;
        this.error = `${addressError(error)}；保存结果待核实，请重试同步`;
      }
    } finally {
      if (this.isCurrent(epoch)) {
        this.isSaving = false;
      }
    }
  }

  async retryVerification(): Promise<void> {
    if (!this.awaitingVerification || this.isSaving || this.disposed || this.hasReturned) {
      return;
    }
    const epoch: number = ++this.generation;
    this.isSaving = true;
    try {
      await this.verifyPending(epoch);
    } finally {
      if (this.isCurrent(epoch)) {
        this.isSaving = false;
      }
    }
  }

  private async verifyPending(epoch: number): Promise<void> {
    const payload: Address | null = this.pendingPayload;
    if (!payload) {
      return;
    }
    try {
      if (this.isEditMode) {
        const response: NetworkResponse<Address> = await this.repository.getAddressInfo(this.addressId);
        if (!this.isCurrent(epoch)) {
          return;
        }
        if (response?.code === 1000 && isAddress(response.data) && response.data?.id === this.addressId && sameAddressFields(response.data, payload)) {
          this.finish(new Address(response.data));
          return;
        }
      } else if (this.hasCompleteSnapshot) {
        const response: NetworkResponse<Address[]> = await this.repository.getAddressList();
        if (!this.isCurrent(epoch)) {
          return;
        }
        if (response?.code === 1000 && Array.isArray(response.data)) {
          const matches: Address[] = response.data.filter((item: Address): boolean =>
            isAddress(item) && !this.knownIds.includes(item.id) && sameAddressFields(item, payload));
          if (matches.length === 1) {
            this.finish(new Address(matches[0]));
            return;
          }
        }
      }
      this.error = "保存已提交，结果待同步。请重试同步，或返回列表核实";
    } catch (error) {
      if (this.isCurrent(epoch)) {
        this.error = `${addressError(error)}；保存结果待同步`;
      }
    }
  }

  private finish(address: Address): void {
    if (this.disposed || this.hasReturned || !isAddress(address)) {
      return;
    }
    this.hasReturned = true;
    this.awaitingVerification = false;
    navigateBackWithResult(new UserAddressSaveResult(this.isEditMode ? AddressSaveOperation.UPDATE : AddressSaveOperation.ADD, address));
  }

  private isCurrent(epoch: number): boolean {
    return !this.disposed && epoch === this.generation;
  }

  aboutToDisappear(): void {
    this.dispose();
  }

  aboutToBeDeleted(): void {
    this.dispose();
  }

  private dispose(): void {
    this.disposed = true;
    this.generation++;
    this.pickerVisible = false;
  }
}
