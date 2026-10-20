"""Render the final auditable result without replacing raw case counts."""
from collections import Counter
import hashlib
import json
from pathlib import Path
from cml_evidence import ROOT, production_fingerprint, write_json

data = json.loads((ROOT / "logs/verification-final-03.json").read_text(encoding="utf-8"))
assert data["requirement_counts"] == {"pass": 38, "blocked": 3}, "Unexpected result: do not publish an assumed success count"
closeout = json.loads((ROOT / "logs/verification-closeout-03/closeout.json").read_text(encoding="utf-8"))
assert closeout["own_layout_stopped"] and closeout["shared_main_alive"] and closeout["shared_instance_config_unchanged"]
final_source = production_fingerprint()
assert final_source["sha256"] == data["source_sha256"]
hap = ROOT / "entry/build/default/outputs/default/entry-default-unsigned.hap"
assert hashlib.sha256(hap.read_bytes()).hexdigest() == data["hap_sha256"]
test_final = json.loads((ROOT / "logs/verification-large-geometry-03/test-code-fingerprint-after.json").read_text(encoding="utf-8"))
assert all(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest for name, digest in test_final.items()), "Runtime scripts changed since final round"
lines = [
    "# cml-spec7 独立自测最终报告 03", "",
    "结论：41项明文原子中 **38 pass、3 blocked、0 fail、0 not_run**。blocked仅B9/B10/B11真实第三方登录；没有平台签发的合法配置/账号条件，不能把不可用提示冒充授权启动。此为本地验收，不是隐藏测试或官方成绩。", "",
    "自测角色 `/root/verification_do`，CODEX_THREAD_ID `01a158d3-1977-7490-b337-d28df9f59e73`；只写本题测试/验证记录，不改生产、Spec或全局state。", "",
    f"生产输入SHA256：`{data['source_sha256']}`。锁定独立全量构建HAP SHA256：`{data['hap_sha256']}`。每一轮均重新安装此产物，并分别验证生产/测试助手首尾指纹一致；测试源码副本和SHA保存在各round的 `test-code/` 和 `test-code-fingerprint-before/after.json`。", "",
    "## 原始运行统计", "",
    "下表是实际脚本case数量，不能与41项合并矩阵混淆；未选用例见各子集selection.json，不记为pass。", "",
    "| round | 实际执行/选择 | pass | fail/error | skip |", "| --- | ---: | ---: | ---: | ---: |",
]
for name in ["verification-navigation-smoke-03", "verification-phone-suite-03", "verification-documents-03", "verification-phone-rotation-03", "verification-tablet-subset-03", "verification-large-subset-03", "verification-large-geometry-03"]:
    report = json.loads((ROOT / "logs" / name / "selftest.json").read_text(encoding="utf-8"))
    counts = Counter(case["outcome"] for case in report["cases"])
    lines.append(f"| [{name}](../../logs/{name}/selftest.json) | {len(report['cases'])} | {counts['pass']} | {counts['fail'] + counts['error']} | {counts['skip']} |")
lines += ["", "手机48case的唯一error是测试助手将Hypium滑动方向写成小写up；原始异常完整保留。结束该轮后仅修为官方API要求的UP/DOWN，重新安装同HAP，正文专项3/3及手机短横屏1/1通过；没有删除正文/滚动断言，也没有重跑无关普通case。手机8skip为B9–B11外部条件、C2–C5当前尺寸不适用、D5未派旋转；后者已由单独真实短横屏轮补齐。", "",
          "名为verification-large-subset-03的22case轮实际仍是800vp平板窗口：首启权限设置将提前设置的横屏恢复竖屏，C4/C5按实际MD明确skip。该轮原始结果保留，绝不按目录名算大屏。结束后把请求方向应用时机改到权限处理、稳定登录页之后，新装同HAP仅补C4/C5/C6/C7；verification-large-geometry-03四项均在真实1200vp通过。", "",
          "## 三类真实窗口", "", "| 类别 | WMS窗口/Density | content宽px | region宽px | 比例/中心 | 证据 |", "| --- | --- | ---: | ---: | --- | --- |"]
for folder, case, title in [("verification-phone-suite-03", "test_C01", "手机"), ("verification-tablet-subset-03", "test_C02", "平板窗口"), ("verification-large-geometry-03", "test_C04", "大屏窗口")]:
    obs = json.loads((ROOT / "logs" / folder / (case + ".observations.json")).read_text(encoding="utf-8"))
    content, region = (obs["bounds_px"][key] for key in ("auth_login_content", "auth_login_button_region"))
    cw, rw = content[2] - content[0], region[2] - region[0]
    lines.append(f"| {title} | {obs['window_xywh_px'][2]}px / {obs['density']} = {obs['width_vp']:.3f}vp | {cw} | {rw} | {rw/cw:.0%}；中心一致（≤1物理px舍入） | [{case}](../../logs/{folder}/{case}.observations.json) |")
lines += ["", "U1按真实WMS窗口逻辑宽分类；U3比例与Logo中心固定以扣安全区、业务padding前的auth_login_content为基准，同时保留window/page/content/region原始边界。Logo三类窗口120×120vp均由实际边界与DMS密度换算；图标间距/包含关系C6/C7只在三类各有pass后合并。没有注入bp或用设备名称替代窗口。", "",
          "临时CmlSpec7_Layout采用当前官方Phone/API23镜像的独立任务配置，实际1600×2400/Density2（800vp），真实旋转为2400×1600（1200vp）；不是冒称另一官方平板机型。手机另有373.714→822.857vp短横屏，UP滚动至完整页脚、70%比例/图标间距通过，方向恢复证据及像素review齐全。未额外测拖拽resize或600/840vp等值边界；不宣称这些派生边界已执行。", "",
          "## 41项逐项结果", "", "| 原子项 | 状态 | 主要证据 |", "| --- | --- | --- |"]
for item in data["requirements"]:
    links = [row["observation"] for row in item["evidence"] if row["outcome"] == "pass" and row["observation"]]
    if item["requirement"] in ("C6", "C7"):
        chosen = []
        for group in ("phone", "tablet", "large"):
            chosen += [row["observation"] for row in item["evidence"] if row["outcome"] == "pass" and row["actual_layout"] == group][:1]
        links = chosen
    evidence = "；".join(f"[{Path(name).parent.name}](../../{name})" for name in links[:3]) if links else "外部接入条件缺失；原始脚本明确skip，合并记blocked"
    lines.append(f"| {item['requirement']} | {item['status']} | {evidence} |")
lines += ["", "## 像素、恢复与限制", "",
          "Root分别直接查看phone/tablet/large新source/HAP截图，11项图案、顶部归属、实心/空心圆角、底部文案/主题色有独立review：root-visual-review-*-03.json。正文B14/B15另由需求角色批准本地原创资源；真实链接、正文片段、滚动、返回后重进均实测，两份完整结束标记由验证角色和Root分别view确认，见root-document-end-review-03.json。", "",
          "正常/头像连点、同入口三连点、两按钮交错连点、目标页未提交返回/重进、三方缺配置可恢复、无账号冷启动均保留真实观察。缺配置提示不算B9–B11通过；没有伪Token/凭据/授权成功。空输入/纯空格不适用：登录主页无输入字段；分页最后一页不适用，协议长文滚动已实际执行。认证HTTP次数/Token写入没有独立网络抓包证据，不把静态无调用当实测网络pass。", "",
          "独立project clean与entry全量clean assembleHap退出均0；207条ArkTS诊断按文件+消息+次数（忽略行列偏移）对基线新增0，资源冲突170，duplicate/sourceMapsPath/signing各1，原始stdout/stderr及语义比对保留。构建未产生生产输入变化（build-generated-input-changes=[]）；entry/build为工具产物单独登记。", "",
          "旧标题/状态栏重叠和Me入口返回后持久锁均已退回主调度修复并形成新冻结回归；旧A01过渡帧假阳性作废，诊断02b因父调度并发改源而末尾指纹失败，不作为新版本通过依据。详见safety-regression-01.md、navigation-regression-02.md，原始失败没有删除。", "",
          "收尾：两设备方向0、仅停止本角色创建的CmlSpec7_Layout（原PID35092）及主实例30856/5555仍Connected，见[closeout.json](../../logs/verification-closeout-03/closeout.json)。官方-stop退出0并明确successfully，进程已消失；hdc保留5557 Offline条目，首次收尾助手误将该条目当仍连接，原始日志保留后修正为核对Connected状态和进程，不重复stop。共享实例3份微型配置SHA与测试前一致，临时实例大文件保留待主调度决定清理。", "",
          "## 复现命令", "", "每个新PowerShell先加载D:/hongmengcup/Enter-HarmonyEnv.ps1和D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1；Python使用common/.venv，工作目录/报告位于本题logs。首个独立构建轮：", "", "```powershell", 
          "./workflow/verification/run-verified-round.ps1 -RoundName <new-name> -ExpectedSourceSha256 26307326248e8e874d1e2d8c3a4abf10e14008d5fd386b91682357a928f6f78e -Device 127.0.0.1:5555 -Mode suite -SuiteKind smoke", 
          "```", "", "后续每轮加 `-BuiltManifest logs/verification-navigation-smoke-03/install-manifest.json` 复用锁定产物并强制新装；full手机/ documents正文/rotation短横屏/layout宽窗选择与确切命令，均以各round的hypium-runner.json、install.json、selection.json和归档PS/Python为准。临时实例已停止时由主调度按保留配置重启，不能直接测试模拟器上来源不明的同bundle应用。", ""]
lines += ["## 最后一轮运行时测试代码指纹", "", "每轮各自的归档SHA已独立保留；以下是最后4case轮及收尾时仍一致的文件。", "", "| 文件 | SHA256 |", "| --- | --- |"]
for name, digest in test_final.items():
    lines.append(f"| {name} | `{digest}` |")
lines += ["", "Root对最终C04实际1200vp截图另有[root-final-large-geometry-review-03.json](root-final-large-geometry-review-03.json)独立像素补证。最终生产/测试/Spec/报告指纹见[final-evidence-fingerprint-03.json](final-evidence-fingerprint-03.json)。", ""]
report_path = ROOT / "workflow/verification/final-verification-03.md"
report_path.write_text("\n".join(lines), encoding="utf-8")
write_json(ROOT / "workflow/verification/final-evidence-fingerprint-03.json", {
    "production": final_source, "hap_sha256": data["hap_sha256"], "final_runtime_test_files": test_final,
    "verification_files": {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in [
        "spec/requirement.md", "spec/acceptance.md", "logs/verification-final-03.json",
        "logs/verification-closeout-03/closeout.json", "workflow/verification/final-verification-03.md",
        "workflow/verification/collect_results.py", "workflow/verification/write_final_report.py", "workflow/verification/closeout_03.py"]},
    "requirement_counts": data["requirement_counts"], "device_control_released": True,
    "note": "No official score or hidden tests claimed. Original failed/helper-error rounds retained; each round has its own immutable test-code archive."
})
print("final-verification-03.md saved")
