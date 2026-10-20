"""Read-only final source/device audit and concise matrix for completed run-r4."""
from pathlib import Path
import collections
import hashlib
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "traces/verification-do-r1"
RUN = BASE / "run-r4"
def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def command(args, name):
    start = time.time()
    result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    path = ROOT / "logs" / ("verification-do-run-r4-final-" + name + ".log")
    path.write_text(result.stdout + result.stderr, encoding="utf-8")
    return {"argv": args, "started": start, "finished": time.time(), "exitCode": result.returncode,
            "rawLog": str(path.relative_to(ROOT)), "output": result.stdout + result.stderr}

summary = read(RUN / "verification-summary.json")
assert summary["complete"] and summary["AStatusCounts"] == {"pass": 44}
frozen = read(ROOT / "traces/do-implementation/source-frozen-r2.json")
expected = frozen["files_sha256"]
actual = {name: sha(ROOT / name) for name in expected}
aggregate = hashlib.sha256(json.dumps(actual, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
differences = {name: {"expected": expected[name], "actual": actual[name]} for name in expected if expected[name] != actual[name]}
assert not differences and aggregate == frozen["source_aggregate_sha256"]
hap = read(BASE / "independent-hap-run-r2.json")
assert sha(Path(hap["Path"])) == hap["SHA256"]
context = read(RUN / "run-context.json")
tests = {name: sha(ROOT / "hypium_tests" / name) for name in context["testSourceSHA256"]}
assert tests == context["testSourceSHA256"]
commands = [command(["hdc", "-t", "127.0.0.1:11245", "shell", "ls", "-l", "/data/log/faultlog/faultlogger"], "faultlogger"),
            command(["git", "diff", "--check"], "diff-check"),
            command(["git", "diff", "--name-only", "--", "**/BuildProfile.ets"], "build-profile"),
            command(["git", "status", "--short"], "git-status")]
assert all(x["exitCode"] == 0 for x in commands)
assert commands[2]["output"].strip() == ""
fault_lines = [line for line in commands[0]["output"].splitlines() if "com.joker.coolmall" in line]
frame_stats = []
for path in sorted(RUN.rglob("frame-times.json")):
    data = read(path)
    ends = [x for x in data if x["event"] == "END"]
    originals = list(path.parent.rglob("frame_*.jpeg"))
    raw_log = path.parent / "capture-raw.log"
    failed_lines = [line for line in raw_log.read_text(encoding="utf-8", errors="replace").splitlines() if "FRAME_FAIL" in line]
    frame_stats.append({"path": str(path.parent.relative_to(ROOT)), "successfulSamples": sum(x["exit"] == 0 for x in ends),
                        "failedCaptureAttempts": failed_lines, "originalFrameFiles": len(originals)})
audit = {"run": "run-r4", "recorded": time.time(), "sourceCount": len(actual), "sourceAggregateSHA256": aggregate,
         "sourceDifferences": differences, "hap": hap, "testSHA256": tests, "commands": commands,
         "faultloggerBundleEntries": fault_lines, "frameCollections": frame_stats,
         "historicalLifecycleFault": {"file": "logs/verification-do-run-r3-sysfreeze.log", "reason": "LIFECYCLE_TIMEOUT",
             "timeLocal": "2026-10-20 13:19:16", "attribution": "medium: system lifecycle/fixture interaction; root cause not fully excluded; not a production source fix"}}
(RUN / "final-audit.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
titles = {
 1:"四标签可见",2:"默认首页选中",3:"默认首页内容",4:"点击分类切页",5:"分类真实Lottie播放",6:"分类图标黑色",7:"其他图标灰色",8:"点击购物车切页",9:"购物车真实Lottie播放",
 10:"首页左滑至分类",11:"分类联动高亮",12:"左滑触发分类Lottie",13:"分类左滑至购物车",14:"点击我的切页",15:"我的真实Lottie播放",
 16:"初始化首页自动播放",17:"首页点击我的切页",18:"首页至我的触发播放",19:"离开首页首帧静止",20:"返回首页播放一次",21:"返回首页内容",22:"首页文字黑色",
 23:"下滚令领取离屏",24:"已选首页点击回顶",25:"同一领取重新可见",26:"首页持续选中",27:"回顶无切页",28:"同标签不新增播放",
 29:"通用切页与动画一致",30:"双向相邻滑动联动",31:"顶部重复点",32:"快速重复回顶",33:"点击滑动快速交错",34:"纵滑不换标签",35:"未提交横拖取消",36:"空内容导航可用",37:"本地无请求导航完成",38:"冷重启默认与自动播放",39:"播放中离开首页复位",
 40:"两端不循环",41:"非首页同点无操作",42:"暖恢复保留实例状态",43:"真实本地Lottie有限播放及离开首帧",44:"跨标签回首页保留偏移"}
matrix = []
lines = ["# run-r4 逐项实测矩阵", "", "8/8 用例完成，零失败/错误/跳过；A1–A44 全部 pass。A40–A44 是主 Agent 批准的实现策略。原始完整断言见 verification-summary.json。", "", "| 项目 | 观察点 | 状态 | 原始断言记录 |", "| --- | --- | --- | --- |"]
for item in summary["items"]:
    number = int(item["id"][1:])
    records = sorted({x["record"] for x in item["evidence"]})
    matrix.append({"id": item["id"], "title": titles[number], "status": item["status"], "kind": item["kind"], "records": records})
    refs = "; ".join("[" + Path(p).parent.name.split("_")[1] + "](D:/HCUP/cml-spec1/" + p + ")" for p in records)
    lines.append("| " + item["id"] + " | " + titles[number] + " | " + item["status"] + " | " + refs + " |")
(RUN / "a-matrix.json").write_text(json.dumps({"items": matrix, "N_A": summary["N_A"]}, ensure_ascii=False, indent=2), encoding="utf-8")
(ROOT / "workflow/verification/do-matrix-r4.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps({"sourceCount": len(actual), "aggregate": aggregate, "sourceChanges": len(differences), "scriptMatch": True,
                  "frameCollections": len(frame_stats), "successfulSamples": sum(x["successfulSamples"] for x in frame_stats),
                  "failedCaptureAttempts": sum(len(x["failedCaptureAttempts"]) for x in frame_stats),
                  "bundleFaultEntries": fault_lines, "commandsExit": [x["exitCode"] for x in commands]}, ensure_ascii=False))
