import { BaseViewModel } from "base";
import { CartRepository } from "data";
import { Cart } from "model";
import { getNavPathStack, OrderNavigator } from "navigation";

@ObservedV2
export default class CartViewModel extends BaseViewModel {
  @Trace carts: Cart[] = [];
  @Trace isLoading: boolean = false;
  @Trace error: string = "";
  @Trace navigationBusy: boolean = false;
  private repository: CartRepository;
  private disposed: boolean = false;

  constructor(repository: CartRepository = new CartRepository()) {
    super();
    this.repository = repository;
  }

  aboutToAppear(): void {
    this.load();
  }

  async load(): Promise<void> {
    if (this.isLoading || this.disposed) {
      return;
    }
    this.isLoading = true;
    this.error = "";
    try {
      const result: Cart[] = await this.repository.getAllCarts();
      if (!this.disposed) {
        this.carts = result;
      }
    } catch (error) {
      if (!this.disposed) {
        this.error = "购物车加载失败，请重试";
      }
    } finally {
      if (!this.disposed) {
        this.isLoading = false;
      }
    }
  }

  confirmOrder(): void {
    if (this.navigationBusy || this.disposed) {
      return;
    }
    const names: string[] = getNavPathStack()?.getAllPathName() ?? [];
    const current: string = names[names.length - 1] ?? "";
    if (names.length > 0 && current !== "main/main" && current !== "main/cart") {
      return;
    }
    this.navigationBusy = true;
    OrderNavigator.toConfirm();
    setTimeout((): void => {
      if (!this.disposed) {
        this.navigationBusy = false;
      }
    }, 0);
  }

  onShown(reason: VisibilityChangeReason): void {
    this.navigationBusy = false;
    this.load();
  }

  aboutToDisappear(): void {
    this.disposed = true;
  }
}
