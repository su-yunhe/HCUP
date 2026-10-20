# 测试连接静态复核 01

2026-10-20；角色 `/root/design_do`；CODEX_THREAD_ID `01a158d2-9ec4-7050-87ff-875ea468f5ce`。仅只读本题快照脚本及 `D:/HCUP/common/.venv/Lib/site-packages` 已安装库；未导入执行驱动、操作设备或修改库/生产/测试/state。

- 已安装Hypium为6.1.0.210（`hypium-6.1.0.210.dist-info/METADATA`）。`hypium/action/device/uidriver.py:113` 的签名为 `UiDriver.connect(cls, connector="hdc", **kwargs)`；指定 `device_sn` 后经 `device_connector.py:69–100` 的DeviceSelector选设备，进程内EnvPool复用不是强制将设备改成首台。
- **未发现固定宿主端口自动重映射事实。** `ohos/proxy/ui_proxy.py:26` 的8012是设备RPC端口；`:191–231` 将分配的宿主端口转发到设备tcp:8012或localabstract:uitest_socket。`:35–36` 每个UIProxy实例单独保存forward_ports_ui，重建/清理删除自身记录的转发。
- `devicetest/utils/util.py:153–172` 的 `get_forward_port(self, host=None, port=None, filter_ports=None)` 从 `9999-secrets.randbelow(99)` 开始选宿主端口，排除已有fport列表和监听端口。此静态实现不支持“5557预览必然重映射5555固定端口”假设；并发端口分配竞态不能仅凭静态读码彻底排除，但没有当前故障证据，不继续扩展。
- 本题 `workflow/verification/cml_evidence.py:60–80` 的snapshot依次执行外部 `hdc -t DEVICE shell uitest dumpLayout -p ...`、接收布局、截图与显示/窗口元数据。未显式reset/kill驱动，不能由此断言CLI取树必然破坏RPC。
- 已提供公共接口：`driver.UiTree.dump_to_file(file_path, **kwargs) -> str`（`hypium/uidriver/uitree/uitree.py:1231`）、`dump_to_dir(dir_path="", **kwargs) -> str`（:1246）、`dump_page_info(dir_path="", screenshot=True, layout=True) -> Page`（:1274）；UiTree由 `hypium/action/device/plugin_mix_in.py:15–19` 挂到driver。可用bundle_name/window_id等UiTreeDumpConfig参数。
- **这些接口不是纯RPC取树替代。** `uitree.py:1131–1145,1178–1210` 内部仍执行设备shell `uitest dumpLayout`，再pull/load；因此单换接口不能声称消除了dump干扰。在已读ArkUiDriver前端未发现独立的全树RPC导出接口。库自身使用该CLI也说明不能把“活跃会话调用dump必然失败”当已确认规则；原生CLI与daemon具体相互影响仍需设备证据。
- 主Agent随后报告的独立复现：已结束旧driver、新进程只连5555、未dump前点可见me_login_entry，仍停在我的页，且距首次返回已数分钟；证据位于 `logs/verification-phone-suite-02/reentry-after-interruption.jpeg`、`.ui.json`、`-action.json`。本角色未重做设备实验。结合MeViewModel持久bool锁，当前应转入口恢复修订，停止以传输假设阻塞验证；见implementation-plan-03。
