# cml-spec7 来源片段（供3-package汇总）

本片段仅报告本题已有可读证据，人工输入 `spec/submit-input.yaml.extra_sources` 仍为 **【待补充】**；不代填“无额外来源”。团队来源保护声明 `source_guard` 仍为 **【待补充】**。

| 来源类别 | 事实 | 证据与使用范围 |
| --- | --- | --- |
| 随包官方基线 | `75fd0066a7fc0c1e8cedb6218df081f86d307f45` | `spec/metadata.json`、`inputs/`、`workflow/baseline-provenance.json`；本题当前基线，不读取来源项目修复历史 |
| 基线已有组件/资源 | Logo、主题、断点、路由、ViewModel、现有三方图标 | `workflow/implementation/implementation-handoff-01.md`、`workflow/design/implementation-plan-01.md`；三份专用 `ic_login_*.svg` 复制自本题 `core/ui` 基线资源，详见资源清单 |
| 原创本地协议正文 | 本地1.0 / 2026-10-20 | `feature/common/src/main/resources/base/element/string.json`；按用户授权由AI编写，需求角色复核，见 `workflow/implementation/implementation-handoff-01.md` 及原生会话；不是上游官方协议 |
| Harmony/ArkTS参考与工具 | 实际读取版本和hash见配置快照 | `system-config/analysis-20261020T095248Z/manifest.json`、实际Skill副本和原生工具read记录；文件存在不单独证明使用 |
| 公共本地测试框架 | Python hypium==6.1.0.210 | 随包 `test-harness/`、`test-harness/requirements.txt`；本题 `hypium_tests/` 继承框架，非官方评测器 |

## 三方通用SDK研究：读取成功、下载与失败分别记录

以下均为既有 `workflow/provider-research-01.md` 的研究事实；本材料阶段未重新联网核验，未把下载包写入生产依赖。

- QQ官方通用说明实际读取：[环境搭建](https://wiki.connect.qq.com/harmonyos_sdk%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA)、[接口说明](https://wiki.connect.qq.com/harmonyos_sdk%E6%8E%A5%E5%8F%A3%E8%AF%B4%E6%98%8E)、[应用注册说明](https://wiki.connect.qq.com/__trashed-2)。读取范围、authCode与旧后端契约差异见该研究记录。
- 官方OHPM元数据及发行包实际获取：[@tencent/wechat_open_sdk 1.0.23](https://ohpm.openharmony.cn/ohpm/@tencent/wechat_open_sdk/-/wechat_open_sdk-1.0.23.har)、[@tencent/qq-open-sdk 1.0.4](https://ohpm.openharmony.cn/ohpm/@tencent/qq-open-sdk/-/qq-open-sdk-1.0.4.har)。实际读取README/声明，下载物和命令输出在 `logs/provider-research-01/`，完整摘要见 `changes/binary-files.json`。
- 微信开发者接入页打开失败；支付宝开放文档超时，没有据此声称读到具体实现。`ohpm info`字段尝试失败、一次多字段失败、猜测名称`@alipay/apay`返回404均保留；404不表示平台不支持鸿蒙登录。准确失败URL及输出索引见研究记录和原生会话。

根/模块OHPM依赖的名称、精确版本、resolved URL与integrity，以各 `oh-package-lock.json5` 为准，摘要表见 `build.md`。本题没有添加真实三方授权SDK/凭据，B9–B11仍未完成。

## 来源、修改和素材追溯

总体差异为 `changes/final.diff`；二进制文件及每项bytes/SHA-256、基线同源判定在 `changes/binary-files.json`；资源另外列于 `changes/resource-files.json`，含新增的文本SVG。基线复制资源需结合原生工具调用确认原路径，不能因换名被当作外部素材。

当前适用访问边界由本题 `AGENTS.md`、角色提示和既有 `system-config/` 副本记录：本题inputs/工程/记录、只读公共资源与允许的官方模板/本题基线报告；禁止其他题工程和来源项目相关修复提交/PR/Issue/补丁及副本。初始化总览因混含其他题准备被排除，不作为本题功能研发证据。该配置和本片段不替代尚未提供的人工 `extra_sources` / `source_guard` 声明。
