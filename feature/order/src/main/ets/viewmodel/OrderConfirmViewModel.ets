import { BaseViewModel } from "base";
import { AddressRepository, CartRepository } from "data";
import { Address, Cart, NetworkResponse } from "model";
import { getNavPathStack, UserAddressSelectionResult, UserNavigator } from "navigation";

@ObservedV2
export default class OrderConfirmViewModel extends BaseViewModel {
  @Trace selectedAddress: Address | null = null;
  @Trace addressLoading: boolean = false;
  @Trace addressError: string = "";
  @Trace navigationBusy: boolean = false;
  @Trace carts: Cart[] = [];
  @Trace cartError: string = "";
  private repository: AddressRepository;
  private cartRepository: CartRepository;
  private addressRevision: number = 0;
  private disposed: boolean = false;

  constructor(repository: AddressRepository = new AddressRepository(), cartRepository: CartRepository = new CartRepository()) {
    super();
    this.repository = repository;
    this.cartRepository = cartRepository;
  }

  aboutToAppear(): void {
    this.loadDefault();
    this.loadCarts();
  }

  async loadCarts(): Promise<void> {
    try {
      const carts: Cart[] = await this.cartRepository.getAllCarts();
      if (!this.disposed) {
        this.carts = carts;
        this.cartError = "";
      }
    } catch (error) {
      if (!this.disposed) {
        this.cartError = "商品摘要加载失败";
      }
    }
  }

  async loadDefault(): Promise<void> {
    if (this.disposed || this.addressLoading) {
      return;
    }
    const revision: number = ++this.addressRevision;
    this.addressLoading = true;
    this.addressError = "";
    try {
      const response: NetworkResponse<Address | null> = await this.repository.getDefaultAddress();
      if (!this.current(revision)) {
        return;
      }
      if (response?.code !== 1000) {
        this.addressError = response?.message || "地址加载失败，请重试";
      } else if (response.data === null) {
        this.selectedAddress = null;
      } else if (this.validAddress(response.data)) {
        this.selectedAddress = new Address(response.data);
      } else {
        this.addressError = "地址数据无效，请重试";
      }
    } catch (error) {
      if (this.current(revision)) {
        this.addressError = error instanceof Error ? error.message : "地址加载失败，请重试";
      }
    } finally {
      if (this.current(revision)) {
        this.addressLoading = false;
      }
    }
  }

  selectAddress(): void {
    if (this.navigationBusy || this.disposed) {
      return;
    }
    this.navigationBusy = true;
    this.addressRevision++;
    this.addressLoading = false;
    UserNavigator.selectAddress().then((result: UserAddressSelectionResult | undefined): void => {
      if (this.disposed) {
        return;
      }
      this.navigationBusy = false;
      if (result && this.validAddress(result.address)) {
        this.addressRevision++;
        this.selectedAddress = new Address(result.address);
        this.addressError = "";
      } else {
        this.revalidate();
      }
    });
    setTimeout((): void => {
      const names: string[] = getNavPathStack()?.getAllPathName() ?? [];
      if (!this.disposed && names[names.length - 1] === "order/confirm") {
        this.navigationBusy = false;
      }
    }, 0);
  }

  async revalidate(): Promise<void> {
    if (this.disposed || this.addressLoading) {
      return;
    }
    if (!this.selectedAddress) {
      await this.loadDefault();
      return;
    }
    const currentId: number = this.selectedAddress.id;
    const revision: number = ++this.addressRevision;
    this.addressLoading = true;
    try {
      const response: NetworkResponse<Address[]> = await this.repository.getAddressList();
      if (!this.current(revision)) {
        return;
      }
      if (response?.code === 1000 && Array.isArray(response.data) &&
        response.data.every((item: Address): boolean => this.validAddress(item))) {
        const selected: Address | undefined = response.data.find((item: Address): boolean => item.id === currentId);
        const defaultAddress: Address | undefined = response.data.find((item: Address): boolean => item.isDefault);
        this.selectedAddress = selected ? new Address(selected) : defaultAddress ? new Address(defaultAddress) : null;
        this.addressError = "";
      } else {
        this.addressError = "地址待核实，请重试同步";
      }
    } catch (error) {
      if (this.current(revision)) {
        this.addressError = "地址待核实，请重试同步";
      }
    } finally {
      if (this.current(revision)) {
        this.addressLoading = false;
      }
    }
  }

  private validAddress(value: Address | null | undefined): boolean {
    return !!value && Number.isInteger(value.id) && value.id > 0 && typeof value.contact === "string" &&
      typeof value.phone === "string" && typeof value.province === "string" && typeof value.city === "string" &&
      typeof value.district === "string" && typeof value.address === "string" && typeof value.isDefault === "boolean";
  }

  private current(revision: number): boolean {
    return !this.disposed && this.addressRevision === revision;
  }

  onShown(reason: VisibilityChangeReason): void {
    this.navigationBusy = false;
  }

  aboutToDisappear(): void {
    this.disposed = true;
    this.addressRevision++;
  }

  aboutToBeDeleted(): void {
    this.disposed = true;
    this.addressRevision++;
  }
}
