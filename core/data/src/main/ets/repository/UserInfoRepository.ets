import { UserInfoNetworkDataSource, UserInfoNetworkDataSourceImpl } from "network";
import { NetworkResponse, Unknown, User } from "model";

/**
 * @file 用户信息仓库，封装用户信息相关请求
 * @author Joker.X
 */
export class UserInfoRepository {
  /**
   * 用户信息网络数据源
   */
  private networkDataSource: UserInfoNetworkDataSource;

  /**
   * 构造函数
   * @param {UserInfoNetworkDataSource} networkDataSource - 可选的用户信息数据源实例
   */
  constructor(networkDataSource?: UserInfoNetworkDataSource) {
    this.networkDataSource = networkDataSource ?? new UserInfoNetworkDataSourceImpl();
  }

  /**
   * 更新用户个人信息
   * @param {Record<string, Unknown>} params - 更新参数
   * @returns {Promise<NetworkResponse<Unknown>>} 更新结果
   */
  async updatePersonInfo(params: Record<string, Unknown>): Promise<NetworkResponse<Unknown>> {
    return this.networkDataSource.updatePersonInfo(params);
  }

  /**
   * 更新用户密码
   * @param {Record<string, string>} params - 修改密码参数
   * @returns {Promise<NetworkResponse<Unknown>>} 更新结果
   */
  async updatePassword(params: Record<string, string>): Promise<NetworkResponse<Unknown>> {
    return this.networkDataSource.updatePassword(params);
  }

  /**
   * 注销账号
   * @param {Record<string, Unknown>} params - 注销参数
   * @returns {Promise<NetworkResponse<Unknown>>} 注销结果
   */
  async logoff(params: Record<string, Unknown>): Promise<NetworkResponse<Unknown>> {
    return this.networkDataSource.logoff(params);
  }

  /**
   * 绑定手机号
   * @param {Record<string, string>} params - 绑定参数
   * @returns {Promise<NetworkResponse<Unknown>>} 绑定结果
   */
  async bindPhone(params: Record<string, string>): Promise<NetworkResponse<Unknown>> {
    return this.networkDataSource.bindPhone(params);
  }

  /**
   * 获取用户个人信息
   * @returns {Promise<NetworkResponse<User>>} 用户信息响应
   */
  async getPersonInfo(): Promise<NetworkResponse<User>> {
    return this.networkDataSource.getPersonInfo();
  }
}
