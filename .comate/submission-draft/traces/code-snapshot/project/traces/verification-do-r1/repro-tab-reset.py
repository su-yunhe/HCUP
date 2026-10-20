"""Native single-click reproduction; only the explicitly question-owned device."""
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from hypium_tests.evidence import flatten_tree, rectangle, save_json, source_manifest

OUT = Path(__file__).resolve().parent / "repro-tab-reset-r1"
OUT.mkdir(exist_ok=True)
SERIAL = "127.0.0.1:11245"
records = []
before = source_manifest()
save_json(OUT / "source-before.json", before)


def command(label, *args):
    argv = ["hdc", "-t", SERIAL, *map(str, args)]
    start = time.time()
    result = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            encoding="utf-8", errors="replace", timeout=40)
    records.append({"label": label, "argv": argv, "start": start, "end": time.time(),
                    "exit": result.returncode, "output": result.stdout})
    save_json(OUT / "commands.json", records)
    if result.returncode or "[Fail]" in result.stdout:
        raise RuntimeError(result.stdout)
    return result.stdout


def capture(label):
    base = f"/data/local/tmp/cml_spec1_repro_{label}"
    command(label + "-tree", "shell", "uitest", "dumpLayout", "-a", "-p", base + ".json")
    command(label + "-tree-recv", "file", "recv", base + ".json", OUT / (label + ".json"))
    command(label + "-image", "shell", "uitest", "screenCap", "-p", base + ".png")
    command(label + "-image-recv", "file", "recv", base + ".png", OUT / (label + ".png"))
    nodes = flatten_tree(json.loads((OUT / (label + ".json")).read_text(encoding="utf-8-sig")))
    summary = {k: [{"bounds": n["attributes"]["bounds"], "description": n["attributes"].get("description"),
                    "text": n["attributes"].get("text")} for n in nodes.get(k, [])]
               for k in ("main_root", "main_content_pager", "main_tab_home", "main_tab_category", "main_tab_cart", "main_tab_me")}
    save_json(OUT / (label + "-summary.json"), summary)
    print(label, json.dumps(summary, ensure_ascii=False), flush=True)
    return nodes


command("stop", "shell", "aa", "force-stop", "com.joker.coolmall")
command("start", "shell", "aa", "start", "-a", "EntryAbility", "-b", "com.joker.coolmall")
time.sleep(2)
nodes = capture("before")
box = rectangle(nodes["main_tab_category"][0]["attributes"]["bounds"])
command("single-click-category", "shell", "uitest", "uiInput", "click", (box[0] + box[2]) // 2, (box[1] + box[3]) // 2)
time.sleep(.5)
capture("after")
after = source_manifest()
save_json(OUT / "source-after.json", after)
assert before == after, "Source changed; reproduction invalid"
