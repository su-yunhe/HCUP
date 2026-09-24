import { BaseNetWorkListUiState, BaseNetWorkListViewModel } from "base";
import { AddressRepository } from "data";
import { Address, NetworkPageData, NetworkResponse, PageRequest } from "model";
import { UserNavigator } from "navigation";

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
   * @param {Address} address - 点击的地址
   * @returns {void} 无返回值
   */
  onAddressClick(address: Address): void {
  }

  /**
   * 点击编辑地址
   * @param {number} addressId - 地址 ID
   * @returns {void} 无返回值
   */
  onEditAddress(addressId: number): void {
    UserNavigator.toAddressDetail(true, addressId);
  }

  /**
   * 点击删除地址
   * @param {number} addressId - 地址 ID
   * @returns {void} 无返回值
   */
  onDeleteAddress(addressId: number): void {
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
