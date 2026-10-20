# 三方接入来源核查 01

本记录由主调度在本题实施会话中形成，只检索与赛题来源项目无关的官方通用 SDK 文档和发行包。未读取上游应用实现、修复或其他题目录。

用户已授权主动提供缺失内容与本地配置。可自动取得通用 SDK，但应用身份、平台审核和真实授权条件仍不能由本地生成替代。

| 来源 | 实际结果 |
| --- | --- |
| https://wiki.connect.qq.com/harmonyos_sdk%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA | 已读取。官方依赖 @tencent/qq-open-sdk；应用使用真实 appId 建实例，接收 qqopenapi 对应 host 回调。SDK返回一次性 authCode；服务端用应用密钥换取 Token，密钥不能放客户端。 |
| https://wiki.connect.qq.com/harmonyos_sdk%E6%8E%A5%E5%8F%A3%E8%AF%B4%E6%98%8E | 已读取。存在成功/取消/错误结果和登录参数；具体函数签名需以所用发行包声明为准，页面示例与最新声明有差别。 |
| https://wiki.connect.qq.com/__trashed-2 | 已读取。应用需要注册申请取得 appId/appKey，并提交审核；用户授予本机权限不能替代平台签发。 |
| https://developers.weixin.qq.com/doc/oplatform/Mobile_App/Access_Guide/ohos.html | 浏览工具无法打开；未假称读取内容。 |
| https://ohpm.openharmony.cn/ohpm/@tencent/wechat_open_sdk | 官方仓元数据查询成功，latest=1.0.23。已下载发行包至 logs/provider-research-01/，读取 README、Index.d.ets、WXAPIFactory/SendAuth/Base声明。具备 SendAuthReq 与 Want 回调 API。 |
| https://ohpm.openharmony.cn/ohpm/@tencent/qq-open-sdk | 官方仓元数据查询成功，latest=1.0.4。已下载发行包并读取声明/README；实际登录签名以该包为准。 |
| https://opendocs.alipay.com/open/218/sxc60m | 浏览工具超时，未假称核验具体接入代码。通用搜索结果不作为实现依据。 |

发行包确切 URL：

- https://ohpm.openharmony.cn/ohpm/@tencent/wechat_open_sdk/-/wechat_open_sdk-1.0.23.har
- https://ohpm.openharmony.cn/ohpm/@tencent/qq-open-sdk/-/qq-open-sdk-1.0.4.har

本次还保留以下失败事实：ohpm info 的 version 字段不被支持；一次尝试多字段参数也失败，随后改为只读官方元数据查询。对猜测名称 @alipay/apay 的元数据查询返回404，不能据此推断支付宝不支持鸿蒙登录。未安装该猜测包，未从第三方应用复制实现。

基线 QQ 后端契约需要 accessToken/openId，不能把新 SDK 返回的 authCode 直接冒充这两项。基线微信参数仅泛型字典，不能猜凭据字段；支付宝只有支付接口，不能当认证接口。平台真实 appId/签名回调登记、认证换票接口仍需合法配置后才能端到端验证 B9–B11。无这些配置时必须不发空凭据认证 POST、不写登录态、不声称真实授权成功。
