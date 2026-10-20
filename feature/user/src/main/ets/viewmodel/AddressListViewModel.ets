import { BaseNetWorkListUiState, BaseViewModel } from "base";
import { AddressRepository } from "data";
import { Address, Ids, NetworkResponse } from "model";
import {
  AddressSaveOperation, getNavPathStack, getRouteParams, navigateBackWithResult,
  UserAddressListParam, UserAddressSaveResult, UserAddressSelectionResult, UserNavigator
} from "navigation";
import { addressError, isAddress } from "../model/AddressResponse";

@ObservedV2
export default class AddressListViewModel extends BaseViewModel {
  @Trace uiState: BaseNetWorkListUiState = BaseNetWorkListUiState.LOADING;
  @Trace listData: Address[] = [];
  @Trace isLoading: boolean = false;
  @Trace isEnableSlideUp: boolean = false;
  @Trace isSelectMode: boolean = false;
  @Trace error: string = "";
  @Trace syncError: string = "";
  @Trace deleteTarget: Address | null = null;
  @Trace isDeleting: boolean = false;
  @Trace deleteUncertain: boolean = false;
  @Trace navigationBusy: boolean = false;
  private repository: AddressRepository;
  private hasSnapshot: boolean = false;
  private hasCompleteSnapshot: boolean = false;
  private disposed: boolean = false;
  private epoch: number = 0;
  private hasReturned: boolean = false;
  private resumeRead: boolean = false;

  constructor(repository: AddressRepository = new AddressRepository()) {
    super();
    this.repository = repository;
  }

  aboutToAppear(): void {
    const params: UserAddressListParam | undefined = getRouteParams<UserAddressListParam | undefined>("user/address-list");
    this.isSelectMode = params?.isSelectMode === true;
    this.reload();
  }

  async reload(): Promise<void> {
    if (this.isLoading || this.disposed) {
      return;
    }
    const requestEpoch: number = ++this.epoch;
    this.isLoading = true;
    this.error = "";
    this.syncError = "";
    if (!this.hasSnapshot) {
      this.uiState = BaseNetWorkListUiState.LOADING;
    }
    try {
      const response: NetworkResponse<Address[]> = await this.repository.getAddressList();
      if (!this.current(requestEpoch)) {
        return;
      }
      if (response?.code !== 1000 || !Array.isArray(response.data) || !response.data.every((item: Address): boolean => isAddress(item))) {
        this.readFailed(response?.message || "地址列表加载失败，请重试");
        return;
      }
      const seen: Set<number> = new Set<number>();
      const rows: Address[] = [];
      response.data.forEach((item: Address): void => {
        if (!seen.has(item.id)) {
          seen.add(item.id);
          rows.push(new Address(item));
        }
      });
      this.listData = rows;
      this.hasSnapshot = true;
      this.hasCompleteSnapshot = true;
      this.updateState();
    } catch (error) {
      if (this.current(requestEpoch)) {
        this.readFailed(addressError(error));
      }
    } finally {
      if (this.current(requestEpoch)) {
        this.isLoading = false;
      }
    }
  }

  private readFailed(message: string): void {
    if (this.hasSnapshot) {
      this.syncError = `列表待同步：${message}`;
      this.updateState();
    } else {
      this.error = message;
      this.uiState = BaseNetWorkListUiState.ERROR;
    }
  }

  private updateState(): void {
    this.uiState = this.listData.length > 0 ? BaseNetWorkListUiState.SUCCESS : BaseNetWorkListUiState.EMPTY;
  }

  private invalidateRead(): void {
    this.epoch++;
    this.isLoading = false;
  }

  retryRequest(): void {
    this.reload();
  }

  onRefreshDirection(direction: "pull" | "slideUp"): void {
    if (direction === "pull" && !this.isDeleting) {
      this.reload();
    }
  }

  onAddressClick(address: Address): void {
    if (!this.isSelectMode || this.navigationBusy || this.deleteTarget || this.isDeleting || this.hasReturned || this.disposed || !isAddress(address)) {
      return;
    }
    this.hasReturned = true;
    navigateBackWithResult(new UserAddressSelectionResult(address));
  }

  onEditAddress(addressId: number): void {
    if (!this.canNavigate()) {
      return;
    }
    this.beginNavigation();
    UserNavigator.editAddress(addressId).then((result: UserAddressSaveResult | undefined): void => this.acceptSaveResult(result));
    this.releaseFailedNavigation();
  }

  onAddAddress(): void {
    if (!this.canNavigate()) {
      return;
    }
    this.beginNavigation();
    UserNavigator.addAddress(this.listData.map((item: Address): number => item.id), this.hasCompleteSnapshot && !this.isLoading)
      .then((result: UserAddressSaveResult | undefined): void => this.acceptSaveResult(result));
    this.releaseFailedNavigation();
  }

  private canNavigate(): boolean {
    return !this.navigationBusy && !this.deleteTarget && !this.isDeleting && !this.disposed && !this.hasReturned;
  }

  private beginNavigation(): void {
    this.navigationBusy = true;
    this.resumeRead = true;
  }

  private releaseFailedNavigation(): void {
    setTimeout((): void => {
      const names: string[] = getNavPathStack()?.getAllPathName() ?? [];
      if (!this.disposed && names[names.length - 1] === "user/address-list") {
        this.navigationBusy = false;
      }
    }, 0);
  }

  acceptSaveResult(result?: UserAddressSaveResult): void {
    if (this.disposed) {
      return;
    }
    this.navigationBusy = false;
    if (!result || !isAddress(result.savedAddress) ||
      (result.operation !== AddressSaveOperation.ADD && result.operation !== AddressSaveOperation.UPDATE)) {
      return;
    }
    this.invalidateRead();
    const saved: Address = new Address(result.savedAddress);
    const index: number = this.listData.findIndex((item: Address): boolean => item.id === saved.id);
    const rows: Address[] = this.listData.slice();
    if (index >= 0) {
      rows[index] = saved;
    } else {
      rows.push(saved);
    }
    this.listData = rows;
    this.hasSnapshot = true;
    this.updateState();
    this.resumeRead = false;
    this.reload();
  }

  onDeleteAddress(addressId: number): void {
    if (!this.canNavigate()) {
      return;
    }
    const target: Address | undefined = this.listData.find((item: Address): boolean => item.id === addressId);
    if (target) {
      this.deleteTarget = new Address(target);
      this.deleteUncertain = false;
      this.error = "";
    }
  }

  cancelDelete(): void {
    if (!this.isDeleting) {
      this.deleteTarget = null;
      this.deleteUncertain = false;
      this.error = "";
    }
  }

  async confirmDelete(): Promise<void> {
    if (!this.deleteTarget || this.isDeleting || this.disposed || this.deleteUncertain) {
      return;
    }
    const target: Address = new Address(this.deleteTarget);
    this.isDeleting = true;
    this.error = "";
    try {
      const response: NetworkResponse<void> = await this.repository.deleteAddress(new Ids([target.id]));
      if (this.disposed) {
        return;
      }
      if (response?.code === 1000) {
        this.completeDelete(target.id);
      } else {
        this.error = response?.message || "删除失败，请重试";
      }
    } catch (error) {
      if (!this.disposed) {
        this.deleteUncertain = true;
        this.error = `${addressError(error)}；删除结果待核实，请重试同步`;
      }
    } finally {
      if (!this.disposed) {
        this.isDeleting = false;
      }
    }
  }

  async verifyDelete(): Promise<void> {
    if (!this.deleteTarget || this.isDeleting || !this.deleteUncertain || this.disposed) {
      return;
    }
    const targetId: number = this.deleteTarget.id;
    this.isDeleting = true;
    try {
      const response: NetworkResponse<Address[]> = await this.repository.getAddressList();
      if (this.disposed) {
        return;
      }
      if (response?.code === 1000 && Array.isArray(response.data) && response.data.every((item: Address): boolean => isAddress(item))) {
        if (!response.data.some((item: Address): boolean => item.id === targetId)) {
          this.completeDelete(targetId);
          return;
        }
        this.error = "该地址仍存在，可取消后重新确认删除";
      } else {
        this.error = response?.message || "删除结果待核实，请重试同步";
      }
    } catch (error) {
      if (!this.disposed) {
        this.error = addressError(error);
      }
    } finally {
      if (!this.disposed) {
        this.isDeleting = false;
      }
    }
  }

  private completeDelete(id: number): void {
    this.invalidateRead();
    this.listData = this.listData.filter((item: Address): boolean => item.id !== id);
    this.deleteTarget = null;
    this.deleteUncertain = false;
    this.hasSnapshot = true;
    this.updateState();
    this.reload();
  }

  handleBack(): boolean {
    if (this.isDeleting) {
      return true;
    }
    if (this.deleteTarget) {
      this.cancelDelete();
      return true;
    }
    return false;
  }

  onHidden(reason: VisibilityChangeReason): void {
    if (this.isLoading) {
      this.resumeRead = true;
      this.invalidateRead();
    }
  }

  onShown(reason: VisibilityChangeReason): void {
    this.navigationBusy = false;
    if (this.resumeRead) {
      this.resumeRead = false;
      this.reload();
    }
  }

  private current(epoch: number): boolean {
    return !this.disposed && epoch === this.epoch;
  }

  aboutToDisappear(): void {
    this.disposed = true;
    this.invalidateRead();
  }

  aboutToBeDeleted(): void {
    this.disposed = true;
    this.invalidateRead();
  }
}
