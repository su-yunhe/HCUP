import os, subprocess, tempfile, json
from pathlib import Path
root=Path(__file__).resolve().parents[3]
out=root/'.comate/submission-draft'
base=json.loads((root/'spec/metadata.json').read_text())['base_commit']
files=['entry/src/main/ets/pages/settings/SettingsSyncSection.ets','entry/src/main/ets/pages/settings/SettingsSyncView.ets','spec/requirement.md','spec-harness/2-submit.md']
with tempfile.TemporaryDirectory(prefix='apply-probe-',dir=out) as td:
 t=Path(td); env=os.environ.copy();env['GIT_INDEX_FILE']=str(t/'index')
 def git(*args,**kw): return subprocess.run(['git',*args],check=True,capture_output=True,**kw)
 git('read-tree',base,cwd=root,env=env)
 for f in files:
  oid=git('hash-object','-w','--no-filters','--',f,cwd=root).stdout.decode().strip()
  git('update-index','--add','--cacheinfo','100644',oid,f,cwd=root,env=env)
 diff=git('diff','--cached','--binary',base,cwd=root,env=env).stdout
 (t/'test.diff').write_bytes(diff)
 git('clone','--no-hardlinks','--no-checkout',str(root),str(t/'clone'),cwd=root)
 git('-c','core.autocrlf=true','checkout','--detach',base,cwd=t/'clone')
 git('-c','core.autocrlf=input','apply','--check','--binary',str(t/'test.diff'),cwd=t/'clone')
 git('-c','core.autocrlf=input','apply','--binary',str(t/'test.diff'),cwd=t/'clone')
 print(json.dumps([{'path':f,'equal':(root/f).read_bytes()==(t/'clone'/f).read_bytes(),'src_crlf':(root/f).read_bytes().count(b'\r\n'),'applied_crlf':(t/'clone'/f).read_bytes().count(b'\r\n')} for f in files]))
