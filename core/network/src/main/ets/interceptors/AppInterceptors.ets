import { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig, AxiosError } from '@ohos/axios';

/**
 * 配置全局网络拦截器
 * @param axiosInstance Axios 实例
 * @author Joker.X
 */
export function setupInterceptors(axiosInstance: AxiosInstance): void {
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
