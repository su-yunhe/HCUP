# 三方登录接入条件

本题当前版本只实现三方入口、缺配置反馈、连点合并和恢复，**没有集成授权 SDK，也没有配置真实 appId**。B9–B11 尚未完成。下载官方 SDK 不代表本应用已获授权。

- 应用包名：`com.joker.coolmall`（AppScope/app.json5）。当前 signingConfigs 为空；测试 unsigned HAP 的安装结果不能代替平台要求的发布签名身份。不得随意填造 appId、签名摘要或回调。
- 微信官方仓发行版：`@tencent/wechat_open_sdk` 1.0.23；下载件 `logs/provider-research-01/wechat_open_sdk-1.0.23.har`。官方仓地址为 https://ohpm.openharmony.cn/ohpm/@tencent/wechat_open_sdk 。实际接入需平台登记应用身份、该 SDK 要求的应用配置和 Want 回调，并核实平台当前的审核要求。主调度尚未成功读取微信接入网页，不能据此文档虚构细节。
- QQ官方仓发行版：`@tencent/qq-open-sdk` 1.0.4；下载件 `logs/provider-research-01/qq-open-sdk-1.0.4.har`。官方[环境搭建](https://wiki.connect.qq.com/harmonyos_sdk%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA)与[应用申请](https://wiki.connect.qq.com/__trashed-2)由主调度核验：需要真实 appId、登记回调及平台审核；应用密钥应留在服务端。最新 SDK 返回一次性 authCode，不能填入本题旧接口所需 accessToken/openId。
- 支付宝：本题现有 `order/pay/alipayAppPay` 是支付接口。当前没有核验可用的支付宝登录 SDK、合法应用配置及认证服务契约，不能拿支付当登录或以普通网页充当授权。

服务端仍需确认：微信 `user/login/wxApp` 的准确凭据字段与授权码换取约定；QQ authCode 到现有 `QQLoginRequest.accessToken/openId` 的安全交换接口；支付宝独立认证契约。当前页面不调用这三个候选认证/支付接口、不发送空凭据、不写 Token、没有假 HTTP loading。

取得真实配置后须补接入方案再实施：SDK拉起与回调 → 用户取消/拒绝/失败/未安装处理 → 有效凭据 → 已确认业务认证接口 → 成功状态。须验证离页失效、重入、重复/晚回调，以及真实设备/平台账号环境。不能把本文件或不可用提示视为授权流程已通过。
