"""Finalize only after every required local method has valid passing evidence."""
import ast
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[2]
folder = root / "logs/do-validation"
latest = int(sys.argv[1]) if len(sys.argv) > 1 else 11
cases = {}
for run, prefixes in ((7, ("test_01_", "test_02_", "test_03_")),
                      (8, ("test_04_", "test_05_", "test_06_", "test_07_", "test_08_"))):
    log = (folder / f"runner-v{run}.log").read_text(encoding="utf-8-sig")
    for name in re.findall(r"^(test_\w+) \(.*?\.\.\. ok$", log, re.M):
        if name.startswith(prefixes):
            cases[int(name[5:7])] = {"name": name, "status": "pass", "batch": run,
                                     "evidence": f"logs/do-validation/runner-v{run}.log"}
for run, allowed in ((10, (10, 11)), (latest, (9,))):
    batch = json.loads((folder / f"runner-v{run}.json").read_text(encoding="utf-8"))
    for case in batch["cases"]:
        name = case["name"].split(" ")[0]
        number = int(name[5:7])
        if number in allowed:
            cases[number] = {"name": name, "status": case["outcome"], "batch": run,
                             "evidence": f"logs/do-validation/runner-v{run}.json"}
assert set(cases) == set(range(1, 12)), cases
assert all(case["status"] == "pass" for case in cases.values()), cases
input_events = [json.loads(line) for line in (folder / f"device-run-v{latest}/ui-events.jsonl").read_text(encoding="utf-8").splitlines()]
assert sum(row["event"] == "invalid_result" for row in input_events) == 11
integrity = json.loads((folder / "freeze-integrity-final.json").read_text(encoding="utf-8"))
assert integrity["unchanged"]
cleanup = json.loads((folder / "cleanup.json").read_text(encoding="utf-8"))
assert cleanup["fixture_stopped"] and cleanup["own_forwards_removed"]
mapping = {
    "A01": [1], "A02": [1, 8], "A03": [1], "A04": [1], "A05": [1], "A06": [2, 6, 11],
    "B01": [1], "B02": [1], "B03": [1, 8], "B04": [8], "B05": [2, 10], "B06": [1, 10],
    "D01": [1, 2, 7], "D02": [2, 3, 4, 11], "D03": [1], "D04": [1],
    "E01": [9], "E02": [9], "E04": [6], "E05": [5], "E06": [5], "E07": [1],
    "E08": [2, 3, 4, 11], "E09": [2], "E10": [2, 10, 11], "E11": [3, 6, 7],
    "E12": [7], "E14": [8, 9], "E15": [1, 10],
}
rows = []
for prefix, count in (("A", 6), ("B", 6), ("D", 4), ("E", 15)):
    for number in range(1, count + 1):
        identifier = f"{prefix}{number:02}"
        if identifier in ("E03", "E13"):
            reason = "Spec has no explicit cancellation entry; selected U05 continues on navigation" if identifier == "E03" else "Spec has no pagination or next-page operation"
            rows.append({"id": identifier, "status": "not_run", "applicable": False,
                         "disposition": "not_applicable", "reason": reason,
                         "evidence": ["workflow/requirements/do-test-scope-v1.md#3"]})
        else:
            numbers = mapping[identifier]
            rows.append({"id": identifier, "status": "pass", "applicable": True,
                         "methods": [cases[n]["name"] for n in numbers],
                         "evidence": sorted({cases[n]["evidence"] for n in numbers} |
                                            {f"logs/do-validation/device-run-v{cases[n]['batch']}/{artifact}" for n in numbers
                                             for artifact in ("operation-timelines.json", "ui-events.jsonl", "server.jsonl")}),
                         "limits": "Only the concrete local samples described in the report; no hidden-test claim"})

timelines = json.loads((folder / "device-run-v10/operation-timelines.json").read_text(encoding="utf-8"))
result = {"utc": datetime.now(timezone.utc).isoformat(), "role": "harmony_verification",
          "CODEX_THREAD_ID": "01a142c5-5844-70b0-92f9-f941525030f0", "phase": "complete",
          "source_sha256": integrity["frozen_source_sha256"], "valid_batches": [7, 8, 10, latest],
          "single_full_run_claim": False, "cases": [cases[number] for number in sorted(cases)], "items": rows,
          "optional": [{"id": "pressure_over_120s", "status": "not_run", "required": False,
                        "reason": "Optional pressure sample per do-test-scope-v1; no duration added to Spec"}],
          "official_score": None}
(root / "workflow/verification/do-results-v1.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
warnings = json.loads((folder / "warning-comparison.json").read_text(encoding="utf-8"))
table = "\n".join(f"| {identifier} | pass | {', '.join(str(n).zfill(2) for n in numbers)} |" for identifier, numbers in mapping.items())
timeout = timelines["timeout_evidence"]
fast = timelines["fast_order_results"]
report = f"""# vg-spec14 独立自测 v1

结论：冻结实现的 **11 个唯一本地 Hypium 方法分批通过**，无 skip；A01–A06、B01–B06、D01–D04 及适用 E 项通过。E03 显式取消、E13 分页有依据不适用（JSON 为 not_run + applicable=false）。不是单轮 11/11，不推断官方 F-point 或成绩。

角色 `harmony_verification`，真实 `CODEX_THREAD_ID=01a142c5-5844-70b0-92f9-f941525030f0`。仅使用本题资料/源码/记录与只读公共框架；未改生产代码、Spec、state.json，未派生 Agent。

## 环境、构建与对象核对

设备 `127.0.0.1:5555`，HarmonyOS/OpenHarmony 6.1 API23，1308×2880 / 560dpi；公共 runner 环境检查无告警。PowerShell 每进程加载 `D:/hongmengcup/Enter-HarmonyEnv.ps1`，构建/设备进程另加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。使用 common Python/Hypium 6.1.0.210，从本题 logs/ 运行。

独立 clean assembleHap 退出0，原始命令/日志 `logs/do-validation/build-command.txt`、`build.log`、`build-exit-code.txt`。HAP SHA256 `a8c2b0cd7f00f13cdded0bbbb51e17b183e7236c949f14ea97ca15fbd4634b17`。每批 runner 前重新安装同一个刚构建的本题 unsigned HAP，设备实际接受安装；逐批 bm updateTime 与 SHA256 见 `install-integrity-summary.json`，安装原始输出和命令见 device-commands.jsonl。

冻结源聚合 `{integrity['frozen_source_sha256']}`；批准 manifest SHA256 `2e92cfc7f940c1da6ede778d66d4fed2e69730bc0a6044b467f9de30bbdd48c8`。构建前、分批间及全部验证结束的文件散列一致，见 freeze-integrity-*.json；runner 也逐方法核对生产指纹，v{latest} 有 source-before/source-after。脚本副本/散列分别保存在各批 test-scripts/ 与 test-inputs.json。

源码告警 {warnings['current_source_warnings']}（基线759），原位724、迁移/辅助方法抽取32、减少3、0新增，既有空签名配置告警1。全量 warnings.csv 与 warning-comparison.json 按消息和对应语句/调用归属匹配，包含手动 showToast 抽取的人工核对依据。6个触及生产文件分别499/296/466/78/143/138行，均未超过500；新设置总览使用 LazyForEach。

## 执行批次与测量修正

有效主证据：v7 已完成01–03，主 Agent 同意结束批次以调整后续忙碌重进测量；04片段不使用。v8 已完成04–08，主 Agent 同意结束批次以优化定位；09片段不算方法通过。v7/v8均主动中断退出1，完成行见batch-v7-completed.json / batch-v8-completed.json。v10 的09因测试键盘前置失败，整批退出1；其独立10/11均通过并保留公共runner原生JSON。随后v{latest}重装同HAP仅运行完整09，一项通过退出0、覆盖11组。首次干净用户数据/空远端另有v5的01单方法通过（退出0）。最终按01–11唯一方法汇总，不冒称单轮11/11。

保留设施问题：v1 11项均在自动发现主 Ability 时失败，改为 module 中的 EntryAbility；v2/v3 首次异步隐私弹窗、v4 使用引导遮挡入口，及时中断并保存 setup-failed 原树/JPEG，完成本地测试安装的同意/跳过后仍沿首页齿轮→设置→WebDAV原入口；v6 输入模式 import 路径错误已修正。上述均未用于产品通过证据，也未改生产规避。

Hypium Scroll.scrollSearch 在新页面滚到屏外 S09 约需25秒。忙碌重进改为先采可见固定页头 S10、S03 与原服务请求存活，释放后才滚 S09 检查最终恢复；原始忙碌按钮禁用另由开始和连点样本检查。三种重进采样时请求年龄1.625/4.047/3.36秒，均远早于现有20秒读超时，避免自然超时误判。

最后批次定位helper在原稳定ID未找到时，先调用文档化driver.swipe(UP/DOWN,80%,0.3s)，再按相同ID查找，保留原scrollSearch兜底；没有减少字段组合或修改断言/网络行为。v9首组未能有效执行，原树/截图显示回到首页：clear_text未必唤起键盘，随后的Back可能退出SettingsPage；该轮及时停止，不计09通过。v10尝试显式点击后Back仍有同样问题，09首错终止；独立10/11正常输入路径通过。最终清空分支仅clear_text，不发Back或额外点击，非空输入保留已验证流程，每字段后立即断言S03；随后09从头完整通过。01–08及10/11未受该清空交互修正影响且保留各批原脚本。所有runner设置PYTHONDONTWRITEBYTECODE=1，未写入/清理公共目录缓存。

## 逐需求映射

| 编号 | 状态 | 对应方法编号 |
| --- | --- | --- |
{table}
| E03 | N/A，JSON not_run | 原文无取消，本轮离页继续 |
| E13 | N/A，JSON not_run | 原文无分页 |

详细动作、前置、UI/网络与返回映射见 do-test-plan-v1.md 和 do-results-v1.json。服务只保存内存对象和方法/路径/时间/状态/字节数/认证存在，不记录密码或载荷。测试关闭自动同步，不先点测试连接；每次点击前记录请求序号，用新路径或本次序号区间区分真实手动请求。

## 关键运行证据

- 原生 LoadingProgress 的类型、visible=true、非零 bounds、屏幕交集和实际 JPEG 都已核对；首次/无改动、多阶段、受控401/403/500、断连、连点、正常返回/失败返回/运行中返回、首页重进、前后台、正常重启和在途强停后新进程均形成实际 UI+请求证据。重进截图已目视复核。
- 部分阶段失败：先成功完成预检，后续实际请求500，保持该阶段可见 loading，真实流程 settle 后恢复并能重试；不强制错误文案，也不把服务器第一条响应当同步完成。
- 快路径：点击前启动独立原树采样，服务器立即响应，无人为产品/服务延迟；严格以完整 dump 的完成单调时间作为可见性观测上界，早于同次至少一条后续真实请求收到时间才通过。结果：`{json.dumps(fast, ensure_ascii=False)}`。原始 fast-*.json、UI事件与 server.jsonl 同机时间关联；帧回调日志仅辅助。
- 实际 HTTP timeout：首请求不响应，服务端记录客户端先关闭连接，没有提前发响应，后续回退受控500；真实失败结束后加载消失、按钮恢复、重试有新请求。结果：`{json.dumps(timeout, ensure_ascii=False)}`。UI等待截图、server client_closed、hilog-stream 的网络错误与 controller settle 可交叉核对。独立夹具 peer-close 自检仅证明测量设施，不替代本条设备证据。
- U07 可达调用链已核对：S09→SettingsSyncActions.webdavSyncNow→controller.start/run→帧Promise→setSettings→await syncIncremental→finally finish；手动路径无旧 UI Promise.race 或固定清 busy timer。运行结果以真实多阶段及超时样本补证，未只靠静态阅读判通过。

operation-timelines.json 给出每次点击、服务收到/响应、可见组件采样和最终 idle；v7仅使用01–03、v8仅使用04–08、v10仅使用10/11、v{latest}使用09。09逐组输入/结果还见原始ui-events.jsonl。完整命令、退出码、UI树、JPEG、请求日志、构建日志和源码指纹均在 logs/do-validation/。

决定请求前可见关系的UI/服务日志使用同一主机单调时钟。设备Hilog墙钟与主机存在秒级偏差，clock-calibration.json保留秒分辨率校准；Hilog仅作同设备内部接受/超时/settle顺序辅助，不用未经校准的墙钟与主机日志直接比较毫秒。

## 范围限制与清理

累计超过旧120秒阈值的真实同步为可选压力样本，按 do-test-scope-v1.md 明确 not_run；未运行系统返回手势/其他 section 的每一种组合、远程生产服务认证/证书互操作性和复杂业务冲突。A/B 用同一本机服务器的不同 URL 前缀区分。只声称上述具体样本，不声称每一帧、全部 WebDAV 服务或隐藏输入全覆盖。

临时WebDAV服务已停止，连续日志采集已停止，只移除本 Agent 建立的转发，模拟器保留；见 cleanup.json。构建生成目录/工具临时文件和 git 状态单独登记，未擅自清理其他角色文件或用户改动。无未解决的本题产品失败；设施失败及测量修正均保留原始证据。
"""
(root / "workflow/verification/do-validation-v1.md").write_text(report, encoding="utf-8")
print(json.dumps({"unique_methods_pass": len(cases), "requirement_rows_pass": len(mapping),
                  "not_applicable": 2, "source_unchanged": True}))
