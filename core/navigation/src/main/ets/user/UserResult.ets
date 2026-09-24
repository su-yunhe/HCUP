import { Address } from "model";

/**
 * @file 用户模块导航结果定义
 * @author Joker.X
 */

/**
 * 选择收货地址返回结果
 */
export interface UserSelectAddressResult {
  /**
   * 选择的地址
   */
  address: Address;
}
