# vg-spec13 独立自测计划

- 自测真实 CODEX_THREAD_ID：`01a143ba-f85b-7aa1-b567-2ae28bd2742e`。
- 输入 SHA256 已核对：Spec `ba156110d18109eecd2627ab66690b293da6cac504caef6650333a9a6e124677`；acceptance `14a95fcf91b40bdc268b2a0552995cf91932067e00d66e17b876de57c9e7c770`；baseline-notes `e65df210dd5cf65b66f2719ab4fbede3e6cd99dc576706c64746e9d08065c1a9`。
- 此计划创建时尚未获得最终实现和冻结授权，**全部执行状态为 not_run**。不以脚本存在、静态阅读、基线结果或 Python 语法检查替代运行验证。
- 测试入口为 `hypium_tests/test_webdav_backup.py`，继承公共 `HarnessTestCase`。WebDAV fixture 仅使用本题合成凭据，记录方法/端点/路径/认证布尔值/密文摘要和 UTC，不记录 Authorization 和明文。

| 需求/边界 | 计划用例与断言 | 初始状态 |
| --- | --- | --- |
| A01–A03、A07、A11 | 真实首页设置入口进入；输入五字段；通过稳定 id 点击原文“立即备份”；记录 t0 | not_run |
| A04–A06、A08–A10、A12 | `test_01` 对慢 PUT gate 的两个独立采样；实际 UI 树 `type=LoadingProgress`、visible、opacity、正面积及忙碌文案；截图目视复核 | not_run |
| A13–A16、D07 | 每轮隔离路径，关自动同步，不测试连接/立即同步；真实服务 received/pending/responded 同主机 UTC；两次完整 capture 位于 pending 区间 | not_run |
| D01、D05、B11/B12/B13/B27/B28 | gate 放行成功清 busy；同窗真实指针重复点击无第二上传；终结后第二次真实备份产生新 PUT；快速成功只记录时间线，不增加最短时长要求 | not_run |
| A02/A14、D06、B08/B17、U01/U08 | 未保存当前配置直接备份；A/B 两个真实端点验证采用新输入；允许备份动作复用持久化；另明确保存 C 后只输入 D、不点击动作，冷重启恢复 C；仅填写/返回重进无请求 | not_run |
| B01–B07、U03 | 空/纯空格必填字段逐例输入；短同步密码；无请求且终结收敛；空/空格远端目录沿基线默认值 | not_run |
| D02/D03、B20/B21/B22/B23 | PUT 401/403/404/409/500；实际错误凭据预检401及随后成功；连接拒绝；真实20s级网络读超时、晚响应及下一轮成功 | not_run |
| B09、取消/关闭 | 不新增备份取消；仅取消填写/离页和既有恢复首层“取消”/Back，不发生新手动请求；不拿恢复取消替代备份取消 | not_run |
| B24/B25、U07 | 在途离开后重入同一 pending 请求，busy/spinner/文案继续；完成/失败后重入再备份；冷重启恢复已保存配置 | not_run |
| B26、其它操作占用 | 测试连接 HEAD gate → 离页重入 → 输入另一端点后点备份；原 TESTING 未结束时拒绝新备份、不改旧任务配置；放行后可向新端点备份 | not_run |
| B14/B15、U09 | 无本地学习/用户词书数据、远端新目录上传；由首页0计数与真实导出 hilog 确认，无数据不能仅由密文长度推定 | not_run |
| D04、B18/B19 | 真实链路阶段日志与窗口；不能无侵入构造本地导出/加密/TaskPool异常则逐项 not_run，并登记原因 | not_run |
| U06/UI外层120s | 代码核对无120s race先释放，网络真实请求超时单独实测；需要额外可控的本地超过120s任务才可标该分支通过 | not_run |

执行前须主 Agent 确认源码冻结、设备独占窗口；先记录源码指纹与环境，再构建、安装刚构建 HAP（保存 SHA256/安装 updateTime），然后跑 Harness。每次重跑也先安装本题 HAP。每个 PowerShell 先加载 `D:/hongmengcup/Enter-HarmonyEnv.ps1`；构建/设备另加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。不占用/停止别题进程；fixture 和 rport 仅清理本轮自己创建者。

每条需求最终使用 pass/fail/blocked/not_run；skip 映射 blocked/not_run，永不算 pass。生产指纹变化使相关证据作废并重测；BuildProfile等构建生成变更单独登记，不自行改回生产文件。失败报告须包含最小复现、期望/实际、相关需求、原始日志、归因及证据强度。
