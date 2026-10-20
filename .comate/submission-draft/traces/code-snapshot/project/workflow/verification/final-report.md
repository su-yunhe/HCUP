# vg-spec13 独立验证最终报告

自测真实 CODEX_THREAD_ID：`01a143ba-f85b-7aa1-b567-2ae28bd2742e`。仅使用本题 Spec、批准复审/方案、本题实现及公共 Harness；未读取其他赛题或上游同功能修复。未修改生产代码、Spec、需求或全局 workflow 状态。

同一 v2 冻结源码的最新实际结果：**17 个独立用例 pass，0 fail / error / skip**。这是 `run02` 已通过的 test00–13 与 `run04` test14–16 合并，**不是单次17/17全套**。canonical 为 [logs/selftest.json](../../logs/selftest.json)，逐用例原始运行见 [summary.md](summary.md)。没有官方测试、隐藏输入或官方成绩推断。

## 运行、构建与原始失败

| 运行 | 构建/安装/测试退出码 | 实际结果与处置 |
| --- | --- | --- |
| run01 | 0 / 0 / -1 | 自测工具原生 CLI swipe 约10秒，首例输入阶段主动中断；not_run，未形成产品结论。 |
| run02 | 0 / 0 / 1 | 独立 clean 构建；15例实际14 pass、1 fail；原始 [selftest.json](../../logs/implementation-verification/run02/selftest.json) 与失败栈完整保留。 |
| run03 | 0 / 0 / -1 | 同v2独立 clean 构建；收到等待 oracle 复审指令后在首例输入阶段停止；interrupted/not_run。 |
| run04 | 复用已核对的run03构建 / 0 / 0 | 先逐源码hash和HAP SHA核对一致，再重新install-r；定向test14复测+test15/test16补充共3 pass。 |

每个 PowerShell 先加载 `D:/hongmengcup/Enter-HarmonyEnv.ps1`，构建/设备另加载本题 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。准确参数和UTC在各运行 `commands.log`；构建命令为 `hvigorw.bat --mode module -p module=entry@default -p product=default -p buildMode=debug clean assembleHap --no-daemon`。Harness主运行从logs目录执行 `python -m harness.runner`，补充运行复用相同 `HarnessTestCase`、环境校验和RecordingResult，只选择14–16。每次实际执行均先安装本题HAP，保存 `installed-bundle.log`、HAP SHA和安装输出。

run02唯一失败的最小复现：有效配置点击测试连接，受控HEAD保持pending；离页重入后尝试立即备份。期望：拒绝新备份，原TESTING继续；实际按钮已恢复、无spinner，显示“⚠️ 同步操作正在进行中：请等待当前同步完成后再试”。旧测试把任何“正在”均判为本轮未结束，失败点仅为该词断言。归因：**测试oracle过度，强证据**（原始属性、截图、失败栈；[批准复审](../requirements/test14-oracle-review-v1.md)）。精准例外仅用于已确认其它占用的警告拒绝，要求明确占用/请等待，并禁止“正在备份”“处理中”；其它终态判据保留，spinner缺失/按钮恢复/无新上传/旧HEAD仍pending均保留。run04实际重跑通过，未改记run02原失败。

## 环境、产物与指纹

- 设备 `127.0.0.1:5555`；镜像 `emulator 6.1.0.115(SP11DEVC00E115R4P11)`，API `23`；截图/DisplayManager确认 `1308×2880`、虚拟密度/VirtualPixelRatio `3.5`。`const.product.model/name` 均返回 `emulator`；物理DPI报告461.433/468.923，**不能据此宣称已独立确认Pura 90 Pro Max机型及全部官方屏幕规格**。公共环境检查只校验镜像/分辨率，本轮warnings=[]；原始额外信息在 `logs/implementation-verification/device-*.log`。
- Python 3.12环境，Hypium `6.1.0.210`，uitest `6.0.2.3`、代理1.1.9。后续启动均 `PYTHONDONTWRITEBYTECODE=1`；公共Harness只读，主Agent另核对公共缓存时间未被本轮刷新。
- 最终安装HAP：`entry/build/default/outputs/default/entry-default-unsigned.hap`，SHA256 **`40971677431e7da2238dcff28e814dbe0ed81b889c093ee249be638fb34fd341`**，与run03构建、run04安装记录和清理时实物一致。
- v2完整冻结参考 SHA256 **`e463b2682fed306471dc9068eadf9666cc9928c02a297363a334bf70ff7b30d3`**。run02开始全参考匹配；run02/run04生产前后指纹 unchanged=true；最终299个参考文件逐项无差异，完整actual map见 [final-source-fingerprint-comparison.json](../../logs/implementation-verification/final-source-fingerprint-comparison.json)。没有用测试期间变更后的源码支持旧证据。
- 独立clean告警 **759→756**，按文件+消息多重集新增0，仅 `SettingsSyncSection` 的showToast废弃×2和may-throw×1减少。旧LoadingAnimations两个@Prop告警仍存在；未把增量未编译造成的漏报算修复。run02/run03 `warnings-summary.json`、完整diagnostics和原始构建日志保存。已有 `ESObject`、废弃API等告警仍未全部消除。

## 核心时间证据和截图核实

受控fixture为本题本机18173/18174，合成Basic凭据；不写Authorization或明文数据，只记录认证布尔、method/path/Host、UTC、长度及密文SHA。关闭自动同步；每轮路径隔离，不点击连接/同步替代主正例。时间关联全部用同一主机UTC，不混用设备hilog墙钟。

run02核心：PUT `/run02/00/unsaved/backup.json.enc`，565字节、认证正确，**08:30:55.751313 received/pending → 08:30:58.836705 201**。两次完整RPC属性与JPEG采样都在pending内；类型为原生 `LoadingProgress`，opacity=1、84×84正面积且在屏幕内，专属Text为“正在备份到云端...”。第二次真实连续点击两次未新增PUT；放行后spinner节点消失、按钮enabled=true、成功结果可见。精确采样区间在 [core-proof.json](../../logs/implementation-verification/run02/core-proof.json)。

自测通过view_image检查：核心busy-1、busy-2-after-repeat、settled三图；test12退出设置重入pending及在途终止后重启图；test14原拒绝终态图。核心两图圆环角度不同、文字可读，终态无圆环且动作恢复。截图由工具观察，未声称人类手动验收。

RPC `getAllProperties` 保留真实hierarchy、type、opacity、bounds等原生属性；该API本轮未返回visible字段，不能伪造visible=true。可见性联合正屏幕bounds、opacity与上述真实截图判定。JSON明确标注RPC属性来源，未伪称完整native dumpLayout；原始CLI和RPC工具方式有记录。

## 明文A01–A16逐项结论

下表 C00=run02 test00；C01…C13=run02对应编号；C14…C16=run04对应编号。每例原始属性/截图、点击时间及fixture日志均在其运行目录。

| 条目 | 状态 | 实际证据 |
| --- | --- | --- |
| A01 | pass | C00真实首页⚙→设置→WebDAV入口，稳定容器及按钮可达。 |
| A02 | pass | C00五字段真实输入可访问合成配置；C02当前未保存B直接备份。 |
| A03 | pass | C00按原文“立即备份”点击并记t0。 |
| A04 | pass | C00同轮禁用按钮、原生spinner和专属文案。 |
| A05 | pass | C00两次 `type=LoadingProgress`，属性+JPEG核实。 |
| A06 | pass | C00两采样完整处在真实PUT pending内。 |
| A07 | pass | C00单次备份点击，文案时间与t0关联。 |
| A08 | pass | C00同一轮busy及文字窗口。 |
| A09 | pass | C00可读Text“正在备份到云端...”。 |
| A10 | pass | C00第二采样仍为相同进行文字，PUT尚未响应。 |
| A11 | pass | C00独立路径和t0，旧日志/其它动作不能替代。 |
| A12 | pass | C00本轮实际加载状态与请求同窗。 |
| A13 | pass | fixture收到本轮真实HEAD/备份PUT。 |
| A14 | pass | C02预存A后输入B直备份，仅B端口18174收到该轮请求。 |
| A15 | pass | 请求存在作为独立硬断言；若缺上传将失败，未以spinner抵消网络。 |
| A16 | pass | C00两次同窗pending+spinner+文案；服务Host/路径归属正确。 |

## 批准R01–R10逐项结论

| 条目 | 状态 | 实际证据与限度 |
| --- | --- | --- |
| R01 | pass | C00/C01入口、输入、滚动到手动操作。 |
| R02 | pass | C02 A/B当前输入；C04非法当前输入不回退旧配置；C13预检pending时输入和冲突动作禁用，本轮只投A。 |
| R03 | pass | C00 t0→busy；C16真实double_click+click仅一轮。 |
| R04 | pass | C00两次真实LoadingProgress；C03/C12重入恢复。 |
| R05 | pass | C00进行文案/终态；C06–09失败恢复；C14其它任务拒绝按批准oracle区分。 |
| R06 | pass | C00真实原上传链、C02端点对照、C11空数据上传；没有另发无关探针伪造。 |
| R07 | pass | 可执行的成功、HTTP/鉴权/连接拒绝/读超时终结均清busy；C13预检和C00上传pending保持busy。不可安全注入的本地异常见D03/B18/B19，未宣称穷尽所有throw。 |
| R08 | pass | C00在途重复；C16快速连点；C03完成后新一轮；C14 TESTING占用拒绝且不改旧任务。 |
| R09 | pass | C01仅填写离开无请求；C05取消无请求；C15连接/同步与备份分开归因；本轮自动同步关闭。 |
| R10 | pass | C03分区返回；C12系统返回退出设置、后台、在途终止再冷启；C02显式保存C/只输入D后重启恢复C；不自动重放。 |

## D01–D07逐项结论

| 条目 | 状态 | 实际证据与未覆盖 |
| --- | --- | --- |
| D01 | pass | C00放行201后无spinner、文案终态、按钮恢复。 |
| D02 | pass | C06五种HTTP失败、C07鉴权、C08读超时、C09连接拒绝均恢复。 |
| D03 | not_run | 网络失败终结收敛已测；控制器/经理非预期直接throw、导出或TaskPool抛错未安全注入，不能以静态finally冒充运行通过。 |
| D04 | pass | C13受控预检、C00上传前后加载，原始hilog有真实导出/加密/上传阶段。毫秒级本地阶段未逐帧采样，未伪造阶段延迟。 |
| D05 | pass | C03终结后下一次点击新增PUT，C07/C08故障恢复后新轮。 |
| D06 | pass | C01仅进入/填/离开无本次请求；C05取消无请求；C15不把其它动作busy当备份spinner。 |
| D07 | pass | t0、原生属性/JPEG采样、同主机服务pending/responded和终态逐轮对应。 |

## B01–B28逐项结论

| 边界 | 状态 | 实际证据／不适用或未执行部分 |
| --- | --- | --- |
| B01 | pass | C04单独空地址、已有旧合法配置时无请求。 |
| B02 | pass | C04单独空账号无请求。 |
| B03 | pass | C04真正清空密码；未以遮蔽字符猜有值。 |
| B04 | pass | C04同步密码0/1/3拒绝，4位abcd真实成功；4空格拒绝。 |
| B05 | pass | C10空白目录trim为空后实际请求默认`/weiyu_sync`；字面空字符串未单列重复。 |
| B06 | pass | C04各必填项四空格独立拒绝，C10空白目录默认。 |
| B07 | pass | C04全空、仅地址及逐字段缺失；未清真实库创建全新安装前置。 |
| B08 | pass | C01只输入不备份，离开重进无该轮请求。 |
| B09 | not_run | 不适用：批准不新增备份取消，原流程无该入口；不拿恢复取消当备份取消。 |
| B10 | pass | C12分别离页、后台、在途进程终止；原任务/新请求归属分开。 |
| B11 | pass | C03完成后第二轮新PUT。 |
| B12 | pass | C00 pending中真实再点两次仍一个上传。 |
| B13 | pass | C16原生double_click+click，从空闲快速触发，只有一个真实上传。 |
| B14 | pass | C11 fresh hilog `Exporting 0 words`、`Fetched 0 word books`，真实上传，无清库。 |
| B15 | pass | 每轮fixture新路径无旧备份，首次上传成功；不外推完整服务商WebDAV兼容。 |
| B16 | not_run | 不适用：配置表单无分页；滚动可达性另由R01通过。 |
| B17 | pass | C02仅填B直备份；C03保存后备份；C15连接成功/同步完成后各自新备份，独立记录请求窗。 |
| B18 | not_run | 预检HTTP/鉴权失败已测；本地导出失败及预检直接throw未安全注入。 |
| B19 | not_run | 加密/TaskPool异常无法无侵入稳定注入，未改业务代码制造故障。 |
| B20 | pass | C06上传返回五种非2xx，各自记录真实PUT及失败终态。 |
| B21 | pass | C09连接拒绝、C08真实读超时已测；离线开关/DNS失败未额外切换。 |
| B22 | pass | C06 401/403/404/409/500上传，C07错误实际凭据预检/探针401。 |
| B23 | pass | C08真实HTTP read timeout、晚响应后UI不回到busy、下一轮成功；旧UI120秒race已从手动链移除，该旧分支不再适用。 |
| B24 | pass | C03成功后重进；C15 500终态后退出整个设置再进入并新备份。 |
| B25 | pass | C03/C12分区及路由在途返回，C02终态冷启，C12在途终止后冷启不重放且可新备份。 |
| B26 | pass | C13输入/冲突按钮锁；C14其它TESTING占用；C15其它动作请求分离。自动同步占用分支未主动开启，均以关闭状态隔离。 |
| B27 | pass | C00两次真实pending采样，放行后收敛。 |
| B28 | pass | C10即时服务真实请求并收敛；未增固定最短展示时长，也未把漏帧当失败。 |

## 清理、噪声和限制

各轮fixture服务已退出，18173/18174/18175主机监听0，本题runner0。reverse18173/18174以及本题新建forward9982/9919/9931删除均退出0；原先9923 forward保留，未抢占或停止别题进程。run01误用rport清理命令及第一次带引号taskstring清理失败有原始记录，随后正确fport rm清理成功，不计业务失败。设备保留最后合成配置、自动同步关闭、空闲；未清业务库或卸载本题应用。见 [final-cleanup.log](../../logs/implementation-verification/final-cleanup.log)。

构建生成列表已按轮保存；最终git状态无BuildProfile等新增tracked构建噪声，生产修改保持冻结。两处本题Python缓存仍在 `hypium_tests/__pycache__`（3个pyc）和 `workflow/verification/__pycache__`（2个pyc）。root已在各缓存目录新增仅含`*`的本地.gitignore并核实5个pyc及忽略文件自身均被忽略，**无需用户再清理缓存**；公共缓存未删除，共享Git元数据未改。自动审批拒绝了含递归缓存删除的组合命令，仅返回 `blocked by policy`，整条未执行；改做不含文件删除的安全清理后forward/fixture均已收尾，未绕过删除阻断。

本机fixture实现本题所需HEAD/GET/PUT/DELETE/MKCOL等最小应答和可控等待，不证明外网、TLS、真实服务商权限/目录语义、恢复内容完整性或所有WebDAV协议兼容。服务收到密文上传不等于已验证解密恢复。没有大规模非空用户库性能测试、未预期本地throw注入、长于120秒本地任务或隐藏测试。上述未执行项未记为通过。
