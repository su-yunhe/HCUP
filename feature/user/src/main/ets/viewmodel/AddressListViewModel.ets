import { BaseNetWorkListUiState, BaseNetWorkListViewModel } from "base";
import { AddressRepository } from "data";
import { Address, Ids, NetworkPageData, NetworkResponse, PageRequest } from "model";
import {
  RefreshResult,
  UserAddressListParam,
  UserNavigator,
  UserSelectAddressResult,
  getRouteParams,
  navigateBackWithResult
} from "navigation";
import { UserRoutes } from "navigation/src/main/ets/user/UserRoutes";
import { RequestHelper } from "result";

/**
 * @file 地址列表页面 ViewModel
 * @author Joker.X
 */
@ObservedV2
export default class AddressListViewModel extends BaseNetWorkListViewModel<Address> {
  /**
   * 地址仓库
   */
  private repository: AddressRepository = new AddressRepository();
  /**
   * 路由参数
   */
  private readonly routeParam: UserAddressListParam =
    getRouteParams<UserAddressListParam>(UserRoutes.AddressList) ?? {};
  /**
   * 是否为选择模式
   */
  readonly isSelectMode: boolean = this.routeParam.isSelectMode ?? false;
  /**
   * 是否显示删除确认弹窗
   */
  @Trace
  isDeleteDialogVisible: boolean = false;
  /**
   * 当前待删除的地址 ID
   */
  @Trace
  deleteId: number | null = null;

  /**
   * 请求地址分页数据
   * @returns {Promise<NetworkResponse<NetworkPageData<Address>>>} 网络请求 Promise
   */
  protected requestListData(): Promise<NetworkResponse<NetworkPageData<Address>>> {
    const request: PageRequest = new PageRequest();
    request.page = this.currentPage;
    request.size = this.pageSize;
    return this.repository.getAddressPage(request);
  }

  /**
   * 地址卡片点击回调
   * 根据当前模式决定是编辑地址还是选择地址
   * @param {Address} address - 点击的地址
   * @returns {void} 无返回值
   */
  onAddressClick(address: Address): void {
    if (this.isSelectMode) {
      const result: UserSelectAddressResult = { address };
      navigateBackWithResult(result);
      return;
    }
    this.onEditAddress(address.id);
  }

  /**
   * 点击新增地址
   * @returns {void} 无返回值
   */
  onAddAddress(): void {
    UserNavigator.toAddressDetail().then((result?: RefreshResult): void => {
      if (result?.refresh) {
        this.onRefresh();
      }
    });
  }

  /**
   * 点击编辑地址
   * @param {number} addressId - 地址 ID
   * @returns {void} 无返回值
   */
  onEditAddress(addressId: number): void {
    UserNavigator.toAddressDetail(true, addressId).then((result?: RefreshResult): void => {
      if (result?.refresh) {
        this.onRefresh();
      }
    });
  }

  /**
   * 点击删除地址
   * @param {number} addressId - 地址 ID
   * @returns {void} 无返回值
   */
  onDeleteAddress(addressId: number): void {
    this.showDeleteDialog(addressId);
  }

  /**
   * 显示删除确认弹窗，并记录待删除的地址 ID
   * @param {number} addressId - 待删除的地址 ID
   * @returns {void} 无返回值
   */
  showDeleteDialog(addressId: number): void {
    this.deleteId = addressId;
    this.isDeleteDialogVisible = true;
  }

  /**
   * 隐藏删除确认弹窗，并清空待删除 ID
   * @returns {void} 无返回值
   */
  hideDeleteDialog(): void {
    this.isDeleteDialogVisible = false;
    this.deleteId = null;
  }

  /**
   * 执行删除操作，成功后刷新列表并关闭弹窗
   * @returns {void} 无返回值
   */
  deleteAddress(): void {
    const id: number | null = this.deleteId;
    if (id === null) {
      return;
    }
    RequestHelper.repository(this.repository.deleteAddress(new Ids([id])))
      .execute()
      .then((): void => {
        this.onRefresh();
        this.hideDeleteDialog();
      });
  }

  /**
   * 是否显示底部操作按钮
   * @returns {boolean} 是否显示
   */
  shouldShowBottomButton(): boolean {
    return this.uiState !== BaseNetWorkListUiState.LOADING
      && this.uiState !== BaseNetWorkListUiState.ERROR;
  }
}
