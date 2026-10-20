// Executes the actual frozen restore method with controlled dependencies.
// This is source-level behavioral evidence, not ArkUI/device/import evidence.
import fs from 'node:fs';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const ts = require('D:/HarmonyDev/sdk/api23/default/openharmony/ets/build-tools/ets-loader/node_modules/typescript');
const path = 'entry/src/main/ets/pages/settings/SettingsSyncSection.ets';
const source = fs.readFileSync(path, 'utf8');
const method = source.slice(source.indexOf('  private async webdavRestore()'), source.indexOf('  private async webdavSyncNow()'));
const enumText = source.slice(source.indexOf('enum RestorePhase'), source.indexOf('const WEBDAV_AUTOSYNC_INTERVAL_HOURS'));
const helpers = source.slice(source.indexOf('  private ownsRestore()'), source.indexOf('  private async saveWebDavAutoSyncSettings()'));
assert(method.includes('await this.webdavManager.downloadBackupPlain(false)'));
assert(method.includes('await this.webdavManager.importPlainBackup(download.plain)'));
assert(!/runWithTimeout|Promise\.race/.test(method));
const js = ts.transpileModule(`${enumText}\nclass Probe { ${helpers}\n${method}\n}`, { compilerOptions: {target: ts.ScriptTarget.ES2020} }).outputText;
const results = [];
const tick = () => new Promise(resolve => setTimeout(resolve, 3));
function deferred() { let resolve, reject; const promise = new Promise((a,b) => {resolve=a; reject=b}); return {promise,resolve,reject}; }
function setup({dialogs=[1,1], save=true, download, preview, imported}={}) {
  const calls = {dialog:0,save:0,download:0,preview:0,import:0};
  const prompt = {showDialog: async () => {const value=dialogs[calls.dialog++]; if(value instanceof Error) throw value; if(value?.promise) return value.promise; return {index:value};}, showToast:()=>{}};
  const {Probe,RestorePhase:P} = new Function('promptAction',`${js}\nreturn {Probe, RestorePhase};`)(prompt);
  const p = new Probe();
  p.webdavBusy=false; p.restorePhase=P.IDLE; p.colors={TEXT_SECONDARY:'gray',WARNING:'orange',ERROR:'red'};
  p.saveWebDavSettings=async()=>{calls.save++; if(save instanceof Error) throw save; return save;};
  p.webdavManager={downloadBackupPlain:async()=>{calls.download++; if(download instanceof Error) throw download; return download?.promise??download??{result:{success:true},plain:'REAL_METHOD_TEST_PLAIN'};},
    importPlainBackup:async plain=>{calls.import++; assert.equal(plain,'REAL_METHOD_TEST_PLAIN'); if(imported instanceof Error) throw imported; return imported?.promise??imported??{success:true,message:'restored'};}};
  p.syncManager={previewImport:async plain=>{calls.preview++; assert.equal(plain,'REAL_METHOD_TEST_PLAIN'); if(preview instanceof Error) throw preview; return preview?.promise??preview??{errors:[],sampleUpdatedWords:[],updated:0,imported:1,total:1};}};
  return {p,P,calls};
}
async function check(name, fn) {await fn(); results.push({name,status:'pass',evidence_level:'actual extracted method with controlled dependencies'});}
await check('first cancel and rejected native dialog have no settings/network/import side effects',async()=>{for(const choice of [0,new Error('native closed')]) {const {p,P,calls}=setup({dialogs:[choice]}); await p.webdavRestore(); assert.equal(p.restorePhase,P.IDLE); assert.equal(calls.save+calls.download+calls.import,0);}});
await check('settings false or rejection ends before network',async()=>{for(const save of [false,new Error('store rejected')]) {const {p,P,calls}=setup({save}); await p.webdavRestore(); assert.equal(p.restorePhase,P.IDLE); assert.equal(calls.download,0);}});
await check('download failure object and rejection clean actual busy',async()=>{for(const download of [{result:{success:false,message:'network failed',detail:'controlled'}},new Error('network rejected')]) {const {p,P,calls}=setup({download}); await p.webdavRestore(); assert.equal(p.restorePhase,P.IDLE); assert.equal(calls.preview+calls.import,0);}});
await check('empty plaintext and preview failure/rejection never import',async()=>{for(const args of [{download:{result:{success:true},plain:''}},{preview:{errors:['preview failed']}},{preview:new Error('preview rejected')}]) {const {p,P,calls}=setup(args); await p.webdavRestore(); assert.equal(p.restorePhase,P.IDLE); assert.equal(calls.import,0);}});
await check('real dependency pending ownership through download preview confirmation and import; repeat guarded',async()=>{
  const download=deferred(), preview=deferred(), confirm=deferred(), imported=deferred();
  const {p,P,calls}=setup({download,preview,dialogs:[1,confirm],imported}); const flow=p.webdavRestore();
  await tick(); assert.equal(p.restorePhase,P.DOWNLOADING); assert(p.isRestoreWorking()); await p.webdavRestore(); assert.equal(calls.download,1);
  download.resolve({result:{success:true},plain:'REAL_METHOD_TEST_PLAIN'}); await tick(); assert.equal(p.restorePhase,P.PREVIEWING); assert(p.isRestoreWorking());
  preview.resolve({errors:[],sampleUpdatedWords:[],updated:0,imported:1,total:1}); await tick(); assert.equal(p.restorePhase,P.SECOND_CONFIRM); assert(!p.isRestoreWorking()); assert(p.ownsRestore()); await p.webdavRestore(); assert.equal(calls.dialog,2); assert.equal(calls.import,0);
  confirm.resolve({index:1}); await tick(); assert.equal(p.restorePhase,P.IMPORTING); assert(p.isRestoreWorking()); await p.webdavRestore(); assert.equal(calls.import,1);
  imported.resolve({success:true,message:'restored'}); await flow; assert.equal(p.restorePhase,P.IDLE); assert(!p.isRestoreWorking()); assert.equal(p.webdavBackupResult,'✅ restored');
});
await check('second cancel retains authorization boundary',async()=>{const {p,P,calls}=setup({dialogs:[1,0]}); await p.webdavRestore(); assert.equal(p.restorePhase,P.IDLE); assert.equal(calls.import,0);});
await check('import failure object and rejection release ownership with actual error',async()=>{for(const imported of [{success:false,message:'import failed',detail:'controlled'},new Error('import rejected')]) {const {p,P,calls}=setup({imported}); await p.webdavRestore(); assert.equal(p.restorePhase,P.IDLE); assert.equal(calls.import,1); assert.match(p.webdavBackupResult,/failed|rejected/);}});
const report={time:new Date().toISOString(),source:path,source_sha256:crypto.createHash('sha256').update(source).digest('hex'),
  method_sha256:crypto.createHash('sha256').update(method).digest('hex'),limitations:'Node transpilation and controlled dependencies; not actual ArkTS VM, ArkUI rendering, network, or business storage evidence.',results};
fs.writeFileSync(`logs/implementation-validation/dependency-results-${report.source_sha256.slice(0,12)}.json`,JSON.stringify(report,null,2));
console.log(JSON.stringify(report,null,2));
