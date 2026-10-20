from hypium import UiDriver, BY
from datetime import datetime, timezone
from pathlib import Path
import subprocess, shutil
ROOT = Path(__file__).resolve().parent
hdc = shutil.which('hdc')
def shell(*args):
    p = subprocess.run([hdc, '-t', '127.0.0.1:5555', *args], text=True, capture_output=True, encoding='utf8')
    print(datetime.now(timezone.utc).isoformat(), args, 'exit=', p.returncode, p.stdout, p.stderr, flush=True)
    if p.returncode: raise RuntimeError(args)
def snapshot(name):
    for ext, cmd in [('json','dumpLayout'),('png','screenCap')]:
        remote = '/data/local/tmp/vg13-' + name + '.' + ext
        shell('shell','uitest',cmd,'-p',remote)
        shell('file','recv',remote,str(ROOT/(name+'.'+ext)))
driver = UiDriver.connect(device_sn='127.0.0.1:5555')
driver.set_implicit_wait_time(2)
for hint, value in [('https://dav.example.com/dav/', 'http://127.0.0.1:18173'), ('username','vg13-fixture'), ('password','fixture-pass'), ('sync password','fixture-sync-pass'), ('/weiyu_sync','/vg13-baseline')]:
    print(datetime.now(timezone.utc).isoformat(), 'input', hint, flush=True)
    driver.input_text(BY.type('TextInput').hint(hint), value)
    shell('shell','uitest','uiInput','keyEvent','Back')
snapshot('04-configured-unsaved')
driver.click(BY.text('保存设置'))
snapshot('05-config-saved')
shell('shell','uitest','uiInput','swipe','650','2450','650','1100','2000')
snapshot('06-before-backup')
