# vg-spec1 来源片段

随包基线由 `tasks/vg-spec1/project/spec/metadata.json` 声明：提交 `9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`，bundle标识 `repo_bundles/vignette-9cbcf7292c-base.bundle`。`tasks/vg-spec1/project/workflow/baseline-provenance.json` 保存准备时核对的题包提交 `4ea7779175fc185ed70e8dc515249ec77cd55563` 和bundle SHA256 `c54ce90f52f80624b7d146db2d7c31561d3eeca0d3b1fe337baad423c43f80c2`。本次未重访问题包metadata/specs/bundle或来源项目历史。既有服务、资源、恢复/导入链继承基线；二进制清单 `tasks/vg-spec1/changes/binary-files.json` 按内容摘要标出基线字节同源项，不将它们冒充新增外部素材。

本地prepare记录 `tasks/vg-spec1/logs/prepare-baseline.log` 为profile=harmony-cup-build-v1、dry_run=false、changes=[]；准备完成时间见 `tasks/vg-spec1/project/workflow/setup-result.json`。任务书指定的题包 `reports/build-baselines/vg-spec1.log` 不存在；未核对到官方原报告或脚本内容哈希，不能编造脚本精确版本及执行时间。

已登记技术资料及用途如下。这里整理历史记录，不代表本阶段重新联网查证。

| 来源 | 用途与本题证据 |
| --- | --- |
| 本机HarmonyOS API23 SDK声明、ArkTS知识库与Skill资料 | Dialog签名、关闭原因、ArkTS限制；`tasks/vg-spec1/project/workflow/design/round-01.md` §7及`tasks/vg-spec1/project/system-config/`。 |
| 华为官方ArkUI弹框指南与FAQ | 弹框生命周期与返回手势；同上。部分正文抓取超时，仅用官方搜索摘要辅助，最终签名按SDK与实测。 |
| 华为官方模拟器网络、CLI、屏幕配置、下载页、公开JS及SDK元数据 | 旧版Ethernet行为、替代工具预检；`tasks/vg-spec1/project/workflow/design/offline-validation-02.md`、`after-wifi-negative-04.md`，`tasks/vg-spec1/project/workflow/implementation/emulator-tool-preflight-02.md`、`public-tool-metadata-03.md`。Emulator26路线未取得可核验下载文件/大小/SHA，不声称下载成功。 |
| Microsoft Learn/WFP、Microsoft维护的通用WinSDK声明 | WFP动态会话、APP_ID/ABI、权限、原生回读及精确清理；`tasks/vg-spec1/project/workflow/design/after-wifi-negative-04.md`、`wfp-helper-review-05.md`、`wfp-readback-failure-06.md`。不是本题来源应用的修复代码。 |
| Python/CPython/.NET/Microsoft文件API官方文档和参考源 | 单调时钟、文件共享、异常、IPC重试；`tasks/vg-spec1/project/workflow/design/wfp-file-ipc-review-07.md`。 |
| 自研Python Hypium框架、C# WFP辅助工具、合成测试fixture | 工程`test-harness/`、`hypium_tests/`与logs保留实际版本/生成过程；3-package归档共用框架，不把本地工具目录当作可移植构建依赖。 |

精确URL与使用限制保留在表列报告及原生工具记录，不因技能目录内静态链接存在就声称全部已访问。新增二进制主要为本题合成测试快照/截图；其大小SHA逐项列出，具体来源声明仍需结合本题记录及用户extra_sources核对。

用户额外来源完整声明：**【待补充】**（`spec/submit-input.yaml:extra_sources`为空，不得填“无”）。团队来源保护完整声明：**【待补充】**。既有交付报告声明未访问其他题或来源项目相关实现历史；本阶段未把该声明升级为全量原生轨迹的合规审计结论。初始化混合总览不使用、不导出为本题研发记录。
