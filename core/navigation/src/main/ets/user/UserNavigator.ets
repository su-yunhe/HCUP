import { navigateTo, navigateToForResult } from "../NavigationService";
import { RefreshResult } from "../NavigationResult";
import { UserRoutes } from "./UserRoutes";
import { UserAddressDetailParam, UserAddressListParam } from "./UserParam";
import { UserSelectAddressResult } from "./UserResult";

/**
 * @file 用户模块导航封装
 * @author Joker.X
 */
export class UserNavigator {
  /**
   * 跳转到个人中心
   * @returns {void} 无返回值
   */
  static toProfile(): void {
    navigateTo(UserRoutes.Profile);
  }

  /**
   * 跳转到收货地址列表
   * @param {boolean} isSelectMode - 是否为选择模式（默认 false）
   * @returns {Promise<UserSelectAddressResult | undefined>} 返回选中的地址结果 Promise
   */
  static toAddressList(isSelectMode: boolean = false): Promise<UserSelectAddressResult | undefined> {
    const params: UserAddressListParam = { isSelectMode };
    return navigateToForResult<UserSelectAddressResult>(UserRoutes.AddressList, params);
  }

  /**
   * 跳转到收货地址详情
   * @param {boolean} isEditMode - 是否为编辑模式（默认 false）
   * @param {number} addressId - 地址 ID（0表示新增，默认 0）
   * @returns {Promise<RefreshResult | undefined>} 返回结果 Promise
   */
  static toAddressDetail(isEditMode: boolean = false, addressId: number = 0): Promise<RefreshResult | undefined> {
    const params: UserAddressDetailParam = { isEditMode, addressId };
    return navigateToForResult<RefreshResult>(UserRoutes.AddressDetail, params);
  }

  /**
   * 跳转到用户足迹
   * @returns {void} 无返回值
   */
  static toFootprint(): void {
    navigateTo(UserRoutes.Footprint);
  }
}
