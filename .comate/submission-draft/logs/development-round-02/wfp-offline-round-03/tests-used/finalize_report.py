"""Archive observable verification evidence; does not drive the device or edit production."""
import json
import re
import shutil
from pathlib import Path

from hypium_tests.evidence import ROOT, digest, utc, write_json

OUT = ROOT / "logs/development-round-01"
FULL = OUT / "formal-round-02"
SUP = OUT / "formal-supplement-01"


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def relative(path):
    return path.relative_to(ROOT).as_posix()


def main():
    primary, supplement = load(FULL / "selftest.json"), load(SUP / "selftest.json")
    assert len(primary["cases"]) == 13 and all(c["outcome"] == "pass" for c in primary["cases"])
    assert len(supplement["cases"]) == 2 and all(c["outcome"] == "pass" for c in supplement["cases"])
    manifests = [load(p / "installed-hap-manifest.json") for p in (FULL, SUP)]
    assert manifests[0]["source"] == manifests[1]["source"]
    assert manifests[0]["hap_sha256"] == manifests[1]["hap_sha256"]
    checks = []
    cases = {int(p.name[5:7]): p for p in FULL.iterdir() if p.is_dir() and p.name.startswith("test_")}
    for n in (1, 2, 3):
        checks.append((cases[n], FULL / "webdav" / ("window-" + cases[n].name + ".json")))
    for n, modes in ((10, ("failure", "delay", "unavailable-endpoint")),
                     (12, ("button", "gesture", "outside"))):
        for mode in modes:
            checks.append((SUP / cases[n].name / mode,
                           SUP / "webdav" / ("window-" + cases[n].name + "-" + mode + ".json")))
    verified = []
    for directory, window in checks:
        before = load(directory / "data-before/semantic.json")
        after = load(directory / "data-after/semantic.json")
        ui0, ui1 = load(directory / "before-ui-state.json"), load(directory / "after-ui-state.json")
        net = load(window)
        assert before["tables"] == after["tables"] and ui0 == ui1
        assert before["integrity_check"] == after["integrity_check"] == "ok"
        assert net["total"] == net["downloads"] == 0
        prefs_equal = (directory / "data-before/webdav_state_store.xml").read_bytes() == (directory / "data-after/webdav_state_store.xml").read_bytes()
        assert prefs_equal
        verified.append({"directory": relative(directory), "data_equal_all_9_tables": True,
                         "preferences_byte_equal": prefs_equal, "ui0_equal": True,
                         "business_sha256": before["business_sha256"], "window": relative(window),
                         "window_started_at": net["started_at"], "window_finished_at": net["finished_at"],
                         "actual_requests_at_controlled_receiver": 0, "downloads_at_controlled_receiver": 0,
                         "request_counter_scope": "127.0.0.1:28762 receiver; unavailable-endpoint points to port1, whose socket attempts are not instrumented" if directory.name == "unavailable-endpoint" else "Configured controlled WebDAV receiver 127.0.0.1:28762"})
    write_json(OUT / "final-audit/data-ui-request-equality.json", verified)
    hilog = (OUT / "final-audit/hilog-dump.log").read_text(encoding="utf8")
    write_json(OUT / "final-audit/crash-check.json", {
        "at": utc(), "current_app_pid": 25748,
        "faultlogger_listing": "total 0", "raw_listing": "logs/development-round-01/final-audit/commands.jsonl",
        "hilog_crash_marker_matches": [line for line in hilog.splitlines() if re.search(r"JSCRASH|CPPCRASH|Fatal signal|AppFreeze", line, re.I)],
        "current_app_pid_hilog": "logs/development-round-01/final-audit/app-current-pid-hilog.log",
        "scope": "No crash markers in retained final hilog dump and empty faultlogger; app remains foreground. Ring-buffer scope, not unlimited historical absence. Intentional force-stops are test actions."})
    for target in (OUT / "selftest.json", ROOT / "logs/selftest.json"):
        shutil.copyfile(FULL / "selftest.json", target)
    write_json(OUT / "selftest-provenance.json", {"primary": relative(FULL / "selftest.json"),
        "primary_tests": 13, "supplement": relative(SUP / "selftest.json"), "supplement_tests": 2,
        "all_executed_outcome": "pass", "skip": 0, "requirement_status": "27 pass, R27 blocked for actual system offline"})

    descriptions = [
        "既有设置/WebDAV恢复入口可达并可操作", "点击后的首个稳定状态为第一层，未先请求/校验", "标题精确匹配 ⚠️ 从云端恢复",
        "正文可见本地未同步学习记录丢失风险", "取消按钮文字及真实关闭", "继续按钮文字及真实交接",
        "未选择时三个观察周期保持第一层", "等待期间实际下载为零", "等待期间九业务表逐字段不变",
        "取消按钮关闭第一层", "非按钮关闭进入取消终态", "真实物理边缘返回手势关闭", "当次边界外实际点击关闭",
        "三取消路径UI/数据/请求终态等价", "关闭后观察及重开无迟到恢复", "三路径独立零实际下载",
        "三路径独立本地独有/冲突字段不变", "五输入和两结果保持UI0，含已有非空结果", "五操作按钮enabled且可重新开启",
        "第一层等待/取消全部实际WebDAV请求为零", "无busy/loading或新取消结果残留", "真实恢复双击安全且无堆叠/迟到",
        "三取消后主动重开正常且旧轮不发请求", "取消后返回首页再重进不续跑", "取消后和未确认强停重启均不续跑",
        "首次空本地/预置空云端、空配置、纯空白配置先确认并安全取消", "失败/延迟/拒绝连接已测；真实系统断网受环境阻断",
        "快速继续仅一次下载交接，保留既有预览第二层"]
    mapping = {
        1:[0,1],2:[0,1,8,9,10],3:[1],4:[1],5:[1],6:[11],7:[1,2,3],8:[1,2,3],9:[1,2,3],
        10:[1],11:[2,3],12:[2],13:[3],14:[1,2,3,12],15:[1,2,3,12],16:[1,2,3,12],17:[1,2,3,12],
        18:[1,2,3,12],19:[1,2,3,12],20:[1,2,3,10,12],21:[1,2,3,12],22:[4],23:[1,2,3,12],
        24:[5],25:[6,7],26:[0,8,9],27:[10],28:[11,12]}
    explicit = set(range(1,8)) | set(range(10,20))
    requirements = []
    for n, description in enumerate(descriptions, 1):
        evidence = []
        for t in mapping[n]:
            base = SUP if t in (10,12) else FULL
            evidence.append(relative(base / cases[t].name))
        if n == 27:
            evidence += ["logs/development-round-01/network-research/commands.jsonl",
                         "logs/development-round-01/network-ui-probe/result.json"]
        requirements.append({"id": f"R{n:02}", "source_level": "SPEC_EXPLICIT" if n in explicit else "REASONABLE_DERIVATION",
                             "status": "blocked" if n == 27 else "pass", "observable": description, "evidence": evidence})
    requirements[26]["subconditions"] = {"server_503_preset": "pass", "server_delay_preset": "pass",
        "refused_connection_endpoint": "pass", "actual_system_offline": "blocked"}
    report = {"task": "vg-spec1", "at": utc(), "native_session_uuid": "01a148da-ba96-71c0-ba89-6c2b452a9225",
        "conclusion": "27 requirements pass; R27 actual system offline blocked; zero observed product failures; local acceptance remains incomplete",
        "counts": {"pass":27,"fail":0,"blocked":1,"not_run":0}, "requirements":requirements,
        "full_run": {"path":relative(FULL),"tests":13,"pass":13,"fail":0,"skip":0,"seconds":673.156,"process_exit":0},
        "supplement": {"path":relative(SUP),"tests":2,"pass":2,"fail":0,"skip":0,"seconds":178.330,"process_exit":0,
            "reason":"T10/T12 original fixed evidence filenames overwrote preceding subscenarios. Supplement uniquely scopes each mode; assertions unchanged.",
            "diff":"logs/development-round-01/formal-round-02-to-supplement-test.diff"},
        "source_main_ets_files":193,"source_main_ets_sha256":"17493881420eeb97d206c463c2b82f1176b9d3870ec8e1f4af08bab2b7cf2f5e",
        "hap_sha256":manifests[0]["hap_sha256"],"install_times":[m["installed_at"] for m in manifests],
        "source_and_hap_final_audit":load(OUT / "final-audit/fingerprint-check.json"),
        "warnings":load(FULL / "warning-comparison.json"),
        "environment":{"device":"127.0.0.1:11235","os":"OpenHarmony 6.1.0.115 API23 x86_64","display":"Pura 90 Pro 1256x2760 560dpi",
            "official_display":"Pura 90 Pro Max 1308x2880; not tested on exact resolution", "app_api":"target/compatible22 unchanged",
            "hypium":"6.1.0.210","uitest":"6.0.2.3; agent1.1.9","auto_sync":"UI checked=false and persisted webdav_autosync_enabled=0 per case"},
        "data_proof":"Actual DB/WAL raw copies, integrity_check=ok, nine tables with full sorted rows. Nonempty REVIEW local-only and conflict fields/tags/definitions and user book. Imported history/review_events empty/default, not claimed nonempty.",
        "network_proof":"Host loopback28762 controlled server via assigned-device rport. All methods arriving at this receiver counted, no Authorization logged. Core R20 uses matching configured endpoint. T10 unavailable port1 is UI/data robustness only: its socket attempts are not instrumented by the port28762 receiver. T11 HEAD directory + HEAD backup + GET2001324bytes proves live observation path; second preview canceled without data change.",
        "offline_limitation":"Airplane mode left Ethernet/route/NetConn IsAvailable=1; restored OFF. Official target-only hdc smode explicitly refused undebuggable version; uid2000 retained. No supported emulator link control or service setter established. No permission bypass or host network changes.",
        "prior_failed_run":{"path":"logs/development-round-01/formal-round-01","tests":13,"raw_unittest_failures":3,"seconds":1002.767,
            "cases":["T02 x=1 Hypium ratio scaling changed physical coordinates","T04 second real tap lands outside newly opened dialog and legally cancels","T12 reused T02 gesture"],
            "resolution":"facility-corrections-01.md; x=2 physical calibrated; approved rapid-tap-review-01.md and recorded control geometry; full rerun passes. Original report raw failure preserved, not relabeled.",
            "report_caveat":"Common RecordingResult lacks addSubTest; original JSON 10pass/2fail/1skip differs from raw unittest3fail. Final runs both0skip."},
        "cleanup":load(OUT / "final-audit/cleanup.json"),
        "crash_check":relative(OUT / "final-audit/crash-check.json"),
        "generated_files":"final-audit/entry-build-generated-files.json and hvigor-generated-files.json; __pycache__/pyc ignored locally, no recursive delete; no tracked BuildProfile/lock noise in git status",
        "scope_limitations":["Full final successful import not executed; outside added first-confirmation scope. Real encrypted download, original second confirmation and second cancel covered.","No hidden tests or official score claimed."],
        "reproduce":"pwsh -File hypium_tests/run_verification.ps1 -SourceFrozen -RunName (\"selftest-\" + (Get-Date -Format yyyyMMdd-HHmmss))"}
    target = ROOT / "workflow/verification/round-01.json"
    write_json(target, report)
    lines = ["# vg-spec1 独立验证 round-01", "", f"记录时间：{report['at']}；原生会话 `{report['native_session_uuid']}`。",
        "", "27 项 R 通过，R27 的真实系统断网子项 blocked；0 产品失败。完整 13 项与补跑 2 项均 0 fail / 0 skip。由于该环境缺口，不能宣布本地验收全部完成。",
        "", "## 执行与版本", "",
        f"- 第二轮独立 clean assembleHap 成功（44.107s），安装刚构建 HAP 后冷启动测试：13/13，673.156s，进程 exit0。见 [完整报告](../../{relative(FULL / 'selftest.json')})、[原始日志](../../{relative(FULL / 'hypium.log')})。",
        f"- 证据补跑重新 `hdc -t 127.0.0.1:11235 install -r` 同 HAP：2/2，178.330s，exit0。见 [补跑报告](../../{relative(SUP / 'selftest.json')})。",
        f"- HAP SHA256：`{report['hap_sha256']}`。安装时间 UTC：`{manifests[0]['installed_at']}`、`{manifests[1]['installed_at']}`。",
        f"- 冻结 main/ets 193 文件聚合 `{report['source_main_ets_sha256']}`。逐文件与批准实现一致；构建前/测试后/补跑后全部源码与构建输入一致，最终 HAP 相同。见 [冻结核对](../../{relative(FULL / 'freeze-comparison.json')})、[最终指纹](../../{relative(OUT / 'final-audit/fingerprint-check.json')})。",
        "- 实际设备：专用 `127.0.0.1:11235`，OpenHarmony6.1.0.115/API23 x86_64，Pura90Pro 1256×2760/560dpi；与官方 ProMax1308×2880 分辨率有差异，未声称目标分辨率布局已测。应用API22配置未改。Hypium6.1.0.210，uitest6.0.2.3/agent1.1.9。",
        "", "## 证据有效性及设施修正", "",
        "第一轮完整保留在 `logs/development-round-01/formal-round-01/`：13tests/1002.767s，原始 unittest 3fail，归因是T02的x=1被Hypium当比例缩放、T12复用同手势，以及T04将合法蒙层取消误判为失败。公共report未实现addSubTest，故旧JSON显示10pass/2fail/1skip；未将旧轮改报通过。",
        "",
        "手势改为x=2绝对物理坐标，并用普通HDC物理swipe对照实证关闭；正式T02再次执行真实边缘手势。连点按已批准 `workflow/requirements/rapid-tap-review-01.md` 同时接受一次首层或第二tap框外已取消两种合法终态，保留单击后首层bounds、同点第二tap对照、真实双击、无迟到/堆叠、D0/UI0/0请求。恢复按钮点[879,1821]位于按钮[656,1744][1102,1898]内，而首层[63,1112][1193,1649]外。详见 [设施归因](facility-corrections-01.md) 和正式T04原始树/坐标。生产未改。",
        "",
        "T10/T12在formal02中复用固定before/data-before/after与窗口名，先前子场景文件被后者覆盖；不声称这些旧文件可证明全部子项。修改前脚本已归档formal02/tests-used及SHA。补跑仅增加evidence_scope，T10按failure/delay/unavailable-endpoint、T12按button/gesture/outside保存目录和窗口；全部安全断言保留。另加选择性runner/重装脚本仅负责执行两项和公共report，未改测试行为。",
        "",
        "[精确测试差异](../../logs/development-round-01/formal-round-02-to-supplement-test.diff)；补跑版本见formal-supplement-01/tests-used及SHA。主证据采用完整formal02 + 分目录补跑组合，两个版本同生产指纹/同HAP。",
        "", "## 数据与请求", "",
        "每项先核实真实自动同步checked=false及持久化0。使用合成账号和本地受控WebDAV服务；窗口从恢复点击前开始，覆盖等待/取消和关闭后观察，不在关闭后才清零。核心三路径在实际配置的受控端点均请求0/GET0；六补跑窗口接收计数亦为0。九组UI0逐字段相同；真实DB/WAL读回后九表全行语义比较一致、integrity_check=ok，Preferences原始字节也相同。见 [九组数据/UI/请求核对](../../logs/development-round-01/final-audit/data-ui-request-equality.json)。不可达端点子项配置为端口1，该28762接收器没有监测端口1的socket尝试；该子项仅宣称首层开关/UI0/D0及不等待失败通过，不单凭接收器零值宣称端口1无尝试。核心R20采用有效端点三路径和T12三路径及T11正对照。",
        "",
        "本地含REVIEW学习状态的独有词vgspec1_localonly、冲突词vgspec1_conflict及LOCAL_CONFLICT_VALUE释义/标签和本地用户词书；云端同词为KNOWN/CLOUD_CONFLICT_VALUE。经既有JSON导入UI置备；既有导入会将FSRS/history归一化，review_events为空，未声称有非空历史。原始数据库、WAL/SHM、全字段JSON和截图均保留，不用条数替代字段证据。没有新增生产后门或直接热写数据库。",
        "",
        "T11正对照：双击继续后目录HEAD200、备份HEAD200各一次，GET200一次1324字节，实际解密到既有 `⚠️ 恢复确认` / `确认恢复` 第二层。继续前零请求；第二层前及取消后数据不变，按钮恢复。后续完整成功导入未执行，属于新增规格之外回归范围。T12先真实继续获得503失败结果，再三路径取消保留原有同步和备份非空结果。",
        "", "## 逐需求结论", "", "| 编号 | 状态 | 实测结论 | 主要原始目录 |", "| --- | --- | --- | --- |"]
    for row in requirements:
        links = "、".join(f"[{Path(p).name}](../../{p})" for p in row["evidence"])
        lines.append(f"| {row['id']} | {row['status']} | {row['observable']} | {links} |")
    lines += ["", "17项SPEC_EXPLICIT全部pass；11项REASONABLE_DERIVATION中10pass、R27 blocked。U01-U05按已批准方案处理，不是阻断项；未增加毫秒性能要求。",
        "", "## R27 环境阻断及恢复", "",
        "补跑已分别预置503、延迟服务、拒绝连接端点，第一层开关不等待网络，D0/UI0相同；请求计数范围见上文。真实系统offline没有可执行证据：飞行模式确实打开，但eth0和默认路由仍在、NetConn IsAvailable=1；故未冒称断网。官方目标设备hdc smode明确拒绝 `Cannot set root run mode in undebuggable version`，随后仍uid2000；未绕过拒绝。该实例CLI/界面和服务help未提供已确认的link/策略断网写接口，不猜内部参数、不改宿主网络。",
        "",
        "证据在 `network-research/commands.jsonl`、`network-ui-probe/`（飞行模式前/打开/恢复树与截图、网卡/路由/NetConn原文）及facility-corrections-01.md。已恢复飞行模式OFF，最终eth0 UP/10.0.2.15、默认路由10.0.2.2、shell uid2000；主Agent已采纳blocked限制，本次不等待可选设备信息。",
        "", "## 构建、崩溃与清理", "",
        "两轮独立clean均764条ArkTS告警+既有签名告警；按路径/诊断正文/次数比较基线，忽略搬迁行列并显式映射提取组件，新增0、缺失0。未通过隐藏告警或只看构建成功判整题通过。见formal-round-02/warning-comparison.json及build-diagnostics.csv。",
        "",
        "最终app PID25748处前台，faultlogger目录total0，保留的最终hilog dump无JSCRASH/CPPCRASH/Fatal signal/AppFreeze匹配；当前PID日志三条I级预设503记录，没有崩溃证据。此结论限保留环形日志与faultlogger范围，强停为主动测试动作。见final-audit/commands.jsonl、hilog-dump.log、crash-check.json。",
        "",
        "受控服务已停止，28762端口关闭，rport已结束；仅移除本题Hypium日志可证明属于该设备的9915/9916/9918/9921/9922→8012转发，最终fport为空。见final-audit/cleanup.json。构建生成文件分别登记entry-build-generated-files.json、hvigor-generated-files.json；测试pycache/pyc用局部.gitignore忽略，无递归删除。git状态无BuildProfile/锁文件噪声；生产改动均属冻结实现，没有验证角色生产编辑。",
        "", "## 复跑", "", "在本题专用合成数据模拟器、源码冻结且独占设备时，从工程根执行：", "", "```powershell", report["reproduce"], "```", "",
        "该命令独立clean→安装刚构建HAP→设置manifest→标准spec-harness runner，缺manifest明确报错，0skip门禁。README有相同入口；使用新时间戳RunName保留原日志。最终logs/selftest.json及logs/development-round-01/selftest.json均为完整13项原报告副本，补跑2项独立引用，未把15项拼作一个虚构运行。未声称隐藏测试或官方成绩。", ""]
    (ROOT / "workflow/verification/round-01.md").write_text("\n".join(lines), encoding="utf8")
    print(report["conclusion"])


if __name__ == "__main__":
    main()
