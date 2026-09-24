import { navigateTo } from "../NavigationService";
import { UserRoutes } from "./UserRoutes";
import { UserAddressDetailParam, UserAddressListParam } from "./UserParam";

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
   * @param {boolean} [isSelectMode] - 是否为选择模式
   * @returns {void} 无返回值
   */
  static toAddressList(isSelectMode?: boolean): void {
    if (isSelectMode !== undefined) {
      const params: UserAddressListParam = { isSelectMode };
      navigateTo(UserRoutes.AddressList, params);
      return;
    }
    navigateTo(UserRoutes.AddressList);
  }

  /**
   * 跳转到收货地址详情
   * @param {boolean} [isEditMode] - 是否为编辑模式
   * @param {number} [addressId] - 地址 ID（0表示新增）
   * @returns {void} 无返回值
   */
  static toAddressDetail(isEditMode?: boolean, addressId?: number): void {
    if (isEditMode !== undefined || addressId !== undefined) {
      const params: UserAddressDetailParam = { isEditMode, addressId };
      navigateTo(UserRoutes.AddressDetail, params);
      return;
    }
    navigateTo(UserRoutes.AddressDetail);
  }

  /**
   * 跳转到用户足迹
   * @returns {void} 无返回值
   */
  static toFootprint(): void {
    navigateTo(UserRoutes.Footprint);
  }
}
