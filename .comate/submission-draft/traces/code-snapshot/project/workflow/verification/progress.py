import json
from pathlib import Path
import re
import sys

folder = Path(sys.argv[1])
events = [json.loads(line) for line in (folder / 'observations.jsonl').read_text(encoding='utf-8').splitlines()]
raw = (folder / 'selftest-raw.log').read_text(encoding='utf-8-sig', errors='replace')
finished = re.findall(r'^test_\d+.*?\.\.\. (ok|FAIL|ERROR|skipped[^\r\n]*)', raw, re.M)
print(json.dumps({'case_results':finished, 'latest_case':events[-1]['case'], 'latest_event':events[-1]['event'], 'utc':events[-1]['utc'], 'snapshot_count':sum(e['event']=='snapshot' for e in events)}, ensure_ascii=True))
