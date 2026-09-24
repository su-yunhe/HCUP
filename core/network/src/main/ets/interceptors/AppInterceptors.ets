import { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig, AxiosError } from "@ohos/axios";

import { setupLogInterceptor } from "./LogInterceptor";

/**
 * @file 全局网络拦截器注册
 * @author Joker.X
 */

/**
 * 配置全局网络拦截器
 * @param {AxiosInstance} axiosInstance - Axios 实例
 * @returns {void} 无返回值
 */
export function setupInterceptors(axiosInstance: AxiosInstance): void {
  setupLogInterceptor(axiosInstance);

  // 请求拦截器
  axiosInstance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
      return config;
    },
    (error: AxiosError) => {
      return Promise.reject(error);
    }
  );

  // 响应拦截器
  axiosInstance.interceptors.response.use(
    (response: AxiosResponse) => {
      return response;
    },
    (error: AxiosError) => {
      return Promise.reject(error);
    }
  );
}
