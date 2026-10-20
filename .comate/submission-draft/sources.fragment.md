# cml-spec28 来源片段

整理日期2026-10-19。工程内路径相对本题完整project；团队汇总到根sources.md时应加最终工程前缀。本文件依据本题已留记录，不在材料阶段重新访问应用上游、其他赛题或重新下载依赖。

## 需要人工补充的申报

`spec/submit-input.yaml` 的 `extra_sources` 为空：**【待补充】**。不能替用户填“无”；下表单列本题记录可证明的实际来源，不代表用户已确认没有其他来源。human_edits等其他空字段仍由总材料标【待补充】，不从代码推定作者。

## 随题基线及准备记录

- 本题ID cml-spec28；`spec/metadata.json`指定base_commit=`9a1d608dc89acfc301657c33ce5dd6089cbf9572`，随包基线标识=`repo_bundles/coolmallarkts-9a1d608dc8-base.bundle`。以上只读取本题metadata/已留provenance，未在本阶段访问题包repo_bundles目录。`workflow/baseline-provenance.json`登记该bundle摘要a534a04e…、题包记录提交4ea77791…及输入核验；这是已有记录，不声称本轮重新取回题包验证。
- 基线原 `LICENSE` 为MIT，Copyright(c)2025 Joker.X；完整原LICENSE随工程保留。现有依赖分别受其manifest/lock和各自许可约束，不能将全部第三方统一称MIT。
- `logs/prepare-baseline.log`记录profile harmony-cup-build-v1固定ibest-ui-v2@1.1.3并重建失效锁；`workflow/setup-result.json`、`baseline-provenance.json`记录准备后b75aa21f…仅采用等价依赖配置。该准备标识不是最终功能源版本；最终正式10由827文件清单及3eaa1310…聚合标识。
- 官方 `reports/build-baselines/cml-spec28.log` 在本轮批准的主位置及指定备用同名精确位置均缺失，标**官方基线日志【待补充】**。本题上述prepare/setup/provenance及logs/baseline-build.log是替代证据，不能冒称缺失的官方原日志；未扩展检索其他题目记录。

## 新增地区数据来源与许可

|字段|实际来源/处理|
|---|---|
|通用数据|ibestservices的 `@ibestservices/area-data@0.0.6`；[OHPM registry](https://ohpm.openharmony.cn/ohpm/@ibestservices/area-data)、[同版HAR](https://ohpm.openharmony.cn/ohpm/@ibestservices/area-data/-/area-data-0.0.6.har)。属于通用中国地区数据包，不是本应用同功能实现。|
|原件摘要|HAR SHA256 `ca85c6c34537371024e4a3199922b8cd22ca359d5931ff2d4c6b48cc66cb248d`；原AreaData.ets `220a240d5412206e66d271c3bfb3693fc528fa3d23d972c902e4bb78e0c5dc82`。registry sha512登记在 `workflow/design/development-sources.json`。|
|许可证|Apache-2.0，完整原LICENSE及署名/修改说明在 `third_party/area-data-0.0.6/`；LICENSE SHA256 `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`。已留包检查记录为无NOTICE，不编造NOTICE。|
|纳入本题的内容|`feature/user/src/main/ets/model/AddressRegionData.ets`：完整text/value/children地区树与显式类型，仅改变存储表示。没有纳入原HAR资源、formatter/UI组件、GeoJSON和其他导出。初次引HAR新增资源冲突后改为本地静态数据，原失败及方案修订保留。|
|等价证据|34省/369市/3477区、3880节点；完整名称/代码/顺序/父子路径与原树规范UTF-8逐字节等价，SHA256 `565f7e754dfca6640fabcdc71423a7b307ece4aa96f6a9def486ac01e327552b`。不是仅比总数，也不宣称行政区划为当前年度最新。|
|过程记录|`workflow/implementation/development-export-region-data.py`、`development-region-export-06.json`、`workflow/design/region-warning-revision.md`、`traces/development/verification/round1/region-data-canonical.json`及round2同名原件。当前manifest/lock已移除area-data HAR依赖；构建使用随包静态数据，不需再次导出。|

依赖下载记录另有基线已用的axios2.2.6、ibest-orm2.0.2、ibest-ui-v2 1.1.3、lottie2.0.25、lottie_component_v2 1.0.1（`logs/ohpm-install.log`及各模块lock）；这些不是本次从来源应用借来的修复。完整依赖与许可信息以保留的manifest/lock/包许可为准，本片段不冒充全部传递依赖许可证审计。

## 本题实际使用的技术资料

|资料|用途及可追溯记录|
|---|---|
|本地ArkTS知识检索/语法技能中的接口、可选参数、显式类型/空值及迁移指南|用于命名接口、DTO、空config检查等语言约束。见 `workflow/design/development-sources.json`、`boundary-log-error-revision-01.md`；已归档技能配置在system-config，通用技能包可由只读common/skills提供。检索器doc_index缺失有记录，直接读已授权指南，未伪造检索成功。|
|SDK23的component/common.d.ts、enums.d.ts、for_each.d.ts通用声明|用于hitTestBehavior/HitTestMode、ClickEvent成员和ForEach签名。`workflow/design/fixture-icon-revision.md`保留撤回错误stopPropagation建议及真实编译失败；`fixture-list-refresh-revision.md`登记SDK与运行证据。只引用通用API，未复制应用修复。SDK本体由工具链提供，不是假称已归档全部SDK。|
|[OpenHarmony官方ForEach说明](https://raw.githubusercontent.com/openharmony/docs/master/zh-cn/application-dev/ui/rendering-control/arkts-rendering-control-foreach.md)|2026-10-18读取键值/非首次渲染规则，支持同id快照的局部内容key修订；记录 `workflow/design/fixture-list-refresh-revision.md`。没有沿文档访问示例应用、PR或Issue。|
|[OpenHarmony官方TextInput说明](https://raw.githubusercontent.com/openharmony/docs/master/zh-cn/application-dev/reference/apis-arkui/arkui-ts/ts-basic-components-textinput.md)|2026-10-18读取type/InputType/inputFilter，用于解释PhoneNumber过滤及Normal保真权衡；记录 `workflow/design/boundary-phone-revision-01.md`及原生轨迹。华为同组件文档获取超时，未从失败响应推导技术事实。|
|本题已安装通用axios2.2.6源/类型|核对请求拦截逆序、error/response config声明与日志链，见 `fixture-isolation-review.md`、`boundary-log-error-revision-01.md`；读取范围是本题依赖，不涉及本应用上游修复历史。|
|本题及common/test-harness、Hypium6.1.0.210|用于统一本地测试与设备/报告封装；工程已有test-harness副本，8个harness模块与本轮只读common字节一致。框架不是官方评测器，fixture/源码状态回归不等于正式鉴权或官方通过。|

网页查询无结果、请求失败、错误建议和修订均按原轨迹/文档保留。实际官方API网页是资料查阅；地区树是唯一在本片段明确登记的新第三方数据表示转换，不以“无额外来源”掩盖其复用。

## 记录边界

本题沿本工程Spec/基线及授权通用资料研发，派工禁止其他题工程、应用上游相关提交/Issue/PR/补丁及总览会话作为功能参考。材料中的setup/provenance只用于基线准备事实，不把初始化总览当本题功能开发证据。正式AUTH继续blocked；真实有限fixture通过、失败重试和版本08/09/10分别保留，来源声明不把它们改写成官方验收通过。
