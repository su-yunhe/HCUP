# vg-spec1 scoped WFP test helper

This is test infrastructure, not application code. It has been compiled and checked without administrator rights. **No filter has been enabled by the implementation role.** An elevated run, NAT failure/recovery and HDC continuity still require separate approval and independent testing. A BLOCKED acknowledgment proves filter configuration, not packet drops, guest LinkDown or R27 success.

## Fixed scope

- Only `D:\HarmonyDev\vg-spec1-isolated-emulator61\Emulator.exe` is allowed. The original installed Emulator paths are never accepted as targets.
- Exactly one readable process at that path, the specified PID and exact UTC StartTime, expected binary SHA256, command line `-start VgSpec1ManualOffline`, explicit separated `-hdcPort 11237`, and `-instancePath` equal to the specified instance root are required. This is the exact syntax observed in the official running CLI, not the earlier assumed aliases. The reviewed launch also requires `-imageRoot D:/HarmonyDev/emulator/images` and `-bootmode coldboot`. All five keys are required exactly once; unknown options, old aliases (`-instance`, `-path`, `-hvdport`), compact tokens, equals syntax, missing values and duplicate/conflicting keys are rejected.
- Instance root and run/control directory must be existing children of `D:\HCUP\vg-spec1\logs\`. Reparse points/junctions in those paths are rejected. No control message can change any target parameter.
- WFP matches the executable **APP_ID/path**, not PID. PID/StartTime/instance checks are user-mode guards. Another process at the same copied path would temporarily share the path condition until the next guard check; starting it during the experiment is prohibited. Detection closes the session and exits with an error. The original executable's other instances do not share this copied path.
- Only two outbound layers are used: ALE_AUTH_CONNECT_V4 and V6. Each filter has exactly one EQUAL/BYTE_BLOB ALE_APP_ID condition and BLOCK action, flags zero, and a new owned nonpersistent sublayer. No loopback exception, endpoint/port limitation, RECEIVE/LISTEN filter, kernel driver, Windows Firewall setting, BFE/ACL change or global audit collection is used.

## Build and read-only check (ordinary terminal)

```powershell
& 'D:/HCUP/vg-spec1/hypium_tests/network_isolation/Build-Guard.ps1'
& 'D:/HCUP/vg-spec1/hypium_tests/network_isolation/bin/VgSpec1WfpGuard.exe' --check
```

The build script loads the required Harmony environment, invokes the installed x64 .NET Framework compiler with warnings as errors, and runs only `--check`. It writes each attempt's compiler/check output under `logs/development-round-03/wfp-build/` and a source/binary SHA256 manifest under `bin/`. No downloads, NuGet packages or new compiler are needed. Rebuilding changes the executable hash; use the final reviewed manifest.

No arguments also means check. This mode only reads ABI sizes/offsets, administrator-token status, fixed file presence/hash and, if all target options are supplied, process guards. It never calls EngineOpen or any WFP API. The `nativeWfpCalls:0` field records that code path; it is not a trace of an elevated experiment. If the copied tool does not exist, basic check still succeeds and reports its absence; live target validation remains unverified.

An optional check with `--target-pid`, `--target-start-utc`, `--target-sha256`, and `--instance-root` performs the same read-only target guard. Exact StartTime should come from `(Get-Process -Id <PID>).StartTime.ToUniversalTime().ToString('o')`. No target is guessed or created by this helper.

## User's manual elevated entry (do not run during preparation)

The root/verification role first copies the complete official installed emulator tool directory into the fixed isolated directory, then starts only the reviewed task instance using an explicit task-local `-instancePath` and port. This helper does not copy or start it. A fresh run directory and 32 lowercase hexadecimal nonce must be prepared by the controller. Do not reuse a directory containing `status.json` or `helper.lock`.

The **user** opens an administrator PowerShell console and runs the reviewed entry with actual PID/time/hash/root values:

```powershell
& 'D:/HCUP/vg-spec1/hypium_tests/network_isolation/Start-GuardManually.ps1' `
  -TargetPid <ACTUAL_PID> -TargetStartUtc '<EXACT_UTC_STARTTIME>' `
  -TargetSha256 '<EXPECTED_64_LOWERCASE_HEX>' `
  -InstanceRoot 'D:/HCUP/vg-spec1/logs/<reviewed-instance-root>' `
  -RunDirectory 'D:/HCUP/vg-spec1/logs/<fresh-run-directory>' `
  -RunNonce '<32_LOWERCASE_HEX>' -MaxSeconds 1200 -MaxBlockSeconds 600
```

This script requires an already elevated console and checks the built EXE and source hashes. It never invokes UAC/RunAs. Do not substitute paths or omit independent review. `--serve` refuses unelevated callers before any WFP call. It starts **IDLE_UNBLOCKED**, with no engine open and no filters. Only an accepted block request opens the dynamic engine and adds objects.

Total runtime defaults to 1200 seconds, hard range 30–1800. Each continuous block defaults to 600 seconds, hard range 5–900, and can never extend past the total deadline. A successful repeated block is idempotent and cannot extend its absolute block deadline. Monotonic time enforces these limits. The watchdog checks target/lease/deadlines once per second; target binary size/mtime is checked each tick and full SHA256 is forced every ten seconds and immediately before blocking. A changed/unreadable target, second same-path process, stale controller or deadline causes cleanup, an explicit error status and exit. Startup allows at most 45 seconds for the first fresh request.

An independent background watchdog checks the same monotonic total/lease/block deadlines every 250 ms. If a synchronous BFE/WMI call prevents the normal close/error path for more than three seconds past a deadline, it terminates the management process with FailFast so Windows dynamic-session/RPC cleanup can run. That abnormal exit and any stale status must fail the facility gate; it cannot be treated as a normal acknowledgment. No global audit policy is changed. Actual crash/rundown recovery is still an elevated validation item.

## Control protocol (ordinary controller, no privileges)

The only input is `<RunDirectory>/request.json`, strict UTF-8 JSON, at most 4096 bytes, with exactly these five fields:

```json
{"nonce":"0123456789abcdef0123456789abcdef","sequence":1,"operation":"unblock","createdUtc":"2026-10-17T10:00:00.0000000Z","expiresUtc":"2026-10-17T10:00:10.0000000Z"}
```

Use the actual nonce and current UTC times. Allowed operations are exactly `block`, `unblock`, `exit`. Sequence is a strictly increasing positive integer. Creation can be at most two seconds in the future or fifteen seconds old; expiration must be later than creation/current time and at most fifteen seconds after creation. Wrong nonce/sequence/fields/operation/expired messages are rejected and do not renew the lease. The old unchanged file never renews it. Emit a new atomic replacement every three seconds with a ten-second lease while the test is active, including while unblocked. On lost lease the helper closes and exits **ERROR_UNBLOCKED**, code 3; that must fail the facility gate, never silently become a passing cancellation case. A new nonce cannot be adopted by the existing helper.

For individual requests, the supplied ordinary-user writer performs atomic replacement:

```powershell
& 'D:/HCUP/vg-spec1/hypium_tests/network_isolation/Send-GuardRequest.ps1' `
  -RunDirectory '<SAME_RUN_DIRECTORY>' -RunNonce '<SAME_NONCE>' `
  -Sequence 1 -Operation unblock -LeaseSeconds 10
```

The controller's next request uses sequence 2, and so forth. A writer's output is not a helper acknowledgment. Wait for matching nonce/accepted sequence and the required state in `status.json`; keep auditing that heartbeat and the unchanged deadline/filter IDs.

`status.json` is replaced atomically once per tick and after termination:

- `schemaVersion`, `task`, `nonce`, `state`, `active` (boolean), `helperPid`, `timestampUtc`.
- `lastAcceptedSequence`, nullable `lastAcceptedUtc`, `requestExpiresUtc`, `totalDeadlineUtc`, nullable `blockDeadlineUtc`.
- `target`: fixed `path`, `pid`, exact `startTimeUtc`, `sha256`, fixed `instance`, `instanceRoot`, `hdcPort` (string `11237`), `guardOk` and `lastGuardUtc` (last successful guard).
- `filters`: empty before/after block; while BLOCKED exactly two objects with `id` (decimal string), `key`, `layerGuid`, `layerName`, `verified:true`.
- `nativeEngineOpen`, `cleanupUnconfirmed` (boolean), `sessionGuid`, `subLayerGuid`, nullable `terminationReason`, `auditMode:not_enabled`, `proof:filter_configuration_only`.

State literals are `IDLE_UNBLOCKED`, `BLOCKED`, `EXITED_UNBLOCKED`, `ERROR_UNBLOCKED`, and exceptional `ERROR_CLEANUP_UNCONFIRMED`. The last state means NativeClose or the fresh removal observer failed: never claim recovery from that snapshot; the process exits with code 4, followed by independent recovery verification. `cleanupUnconfirmed:true` and `terminationReason:cleanup_removal_unconfirmed` identify the observer failure; the retained filters are historical IDs whose absence could not be confirmed. A later no-op Close cannot erase that failure. The normal error exit code is 3. `terminationReason` is null while running and records exit_request/console_cancel or the specific failed guard/deadline/lease/API cause at termination. Deliberately stopping heartbeat should produce `controller_lease_expired`, then successful Close/removal verification, `ERROR_UNBLOCKED` and exit 3; any missing verification must fail the facility gate.

`helper.jsonl` records ready, armed, control accepted/rejected, each DWORD-returning native call result, filter ID/layer/key, exact target path/hash, APP_ID blob hash, session/sublayer GUID and cleanup. Pre-commit and post-commit GetById verify identity, owned sublayer, flags, exact single APP_ID condition/type/match/blob and BLOCK action. If same-transaction GetById cannot read newly added filters, the transaction is aborted and the engine closed: there is no fallback that skips this verification. That visibility and all API behavior remain untested until an approved elevated run. No WFP net-event/drop audit has been enabled or claimed.

After a real main-engine Close succeeds, `session_closed` records the native return separately with `removalVerified:false/verificationPending:true`. Before clearing the actual owned IDs/key, a fresh observer engine opens a `FWPM_TXN_READ_ONLY=1` transaction. `cleanup_filter_query` records each actual filter ID/key/layer, returnCode and expectedReturnCode `0x80320003` (FWP_E_FILTER_NOT_FOUND); `cleanup_sublayer_query` records the owned GUID and expected `0x80320007` (FWP_E_SUBLAYER_NOT_FOUND). Return 0 (still present), access errors, open/transaction/log failures or any other error do not prove removal. `cleanup_observer_call` logs open, readonly begin, abort and observer close; all exit paths attempt Close even if query/abort/log fails. `cleanup_verification` summarizes `success`, original `filters`, `subLayerGuid`, `readOnlyTransaction:true`, `observerClosed` and expected return codes. Only strict NOT_FOUND results plus successful observer cleanup/evidence yield success. Idle Close opens no observer. There is no external inspect mode, no guessed ID input and no Add or policy mutation in this observer; `--check` never reaches it.

## Recovery

1. Send a current nonce/sequence `unblock`, then check matching `IDLE_UNBLOCKED`, active false, engine false, empty filters, `cleanup_verification.success:true` for the actual IDs/key, and the real NAT recovery control.
2. Send current `exit`, or press Ctrl+C in the manually opened helper console. Both close the dynamic session and terminate.
3. If the controller/HDC is unavailable, use the helper console's Ctrl+C. As a last local recovery, the user may terminate only the recorded helper PID after checking its executable path/StartTime. Terminating this management process ends the dynamic WFP session; do not kill unrelated Emulator or HDC processes.
4. Unexpected process death also ends the dynamic session by the official WFP lifecycle contract. A stale status file is not a live acknowledgment; independently confirm restored same-endpoint HEAD/GET. There are no persistent/boot-time rules to restore, no global defaults were changed, and no broad cleanup rule should be run.

The independent sequence remains online positive control → scoped block plus same-endpoint failure/zero arrivals and host-service liveness → three cancellation cases with full evidence → unblock/exit and same-endpoint recovery. Check HDC heartbeat and lawful reconnection throughout. A guest may still report eth0/NetConn available: this helper targets transmission isolation, not the guest network-manager state. Do not report R27 passed until the root agent reviews the independent evidence and this boundary.

## Primary references

Native types/constants/GUIDs are based on Microsoft's [WinSDK fwpmtypes.h](https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/shared/fwpmtypes.h), [fwptypes.h](https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/shared/fwptypes.h), [fwpmu.h](https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/um/fwpmu.h) and [rpcdce.h](https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/shared/rpcdce.h). Relevant APIs: [EngineOpen](https://learn.microsoft.com/en-us/windows/win32/api/fwpmu/nf-fwpmu-fwpmengineopen0), [FilterAdd](https://learn.microsoft.com/en-us/windows/win32/api/fwpmu/nf-fwpmu-fwpmfilteradd0), [FilterGetById](https://learn.microsoft.com/en-us/windows/win32/api/fwpmu/nf-fwpmu-fwpmfiltergetbyid0), [SubLayerAdd](https://learn.microsoft.com/en-us/windows/win32/api/fwpmu/nf-fwpmu-fwpmsublayeradd0), [Object Management](https://learn.microsoft.com/en-us/windows/win32/fwp/object-management). The implementation report records actual compiler/layout evidence separately from these API contracts.

The removal observer additionally follows [TransactionBegin/read-only transaction](https://learn.microsoft.com/en-us/windows/win32/api/fwpmu/nf-fwpmu-fwpmtransactionbegin0), [SubLayerGetByKey](https://learn.microsoft.com/en-us/windows/win32/api/fwpmu/nf-fwpmu-fwpmsublayergetbykey0) and Microsoft's [WFP error codes](https://learn.microsoft.com/en-us/windows/win32/fwp/wfp-error-codes). The raw WinSDK fwpmu.h defines FWPM_TXN_READ_ONLY as 0x00000001. The implementation role has not executed any observer/WFP call.

## Version 06 diagnostic gate

The first actual version-05 administrator preflight stopped before Commit at an exact-scope assertion. Abort/Close and strict removal observation succeeded. That run did not record the fields before the generic assertion, so its cause remains undetermined. Root approved a limited compatibility policy based on Microsoft's INDEXED lookup-acceleration semantics: Add flags remain exactly zero; pre/post-commit readback accepts exactly zero or INDEXED (0x40) alone, rejecting every other single bit and every mixture. This is a compatibility design choice, not evidence that BFE added INDEXED in that failed run. All other scope/identity/blob gates and pre/post-commit validation remain required.

`filter_add_input` records the outgoing fields before Add assertions. `filter_readback_raw` records decoded BFE fields before scope/identity assertions: stage, validationPolicy=`add0_readback0_or_indexed_v06`, expectedFilter, actual filterKey/filterId/flags/flagsHex/layerKey/subLayerKey/ownedSubLayerKey/actionType/actionTypeHex/actionFilterType/numConditions, pointer-presence booleans, conditionDecoded/key/matchType/type, provider/weight metadata and expected APP_ID size/hash. Only if there is exactly one non-null condition with BYTE_BLOB type is its blob interpreted; actual declared size/data presence/size/hash or appIdReadError are included. It never logs blob content or the application path blob itself. A wrong type is recorded and rejected without interpreting its union as a blob.

`scope_assertion_failed` includes stage, validationPolicy, and `failures:[{field,actual,expected}]`. The error reason is `scope_assertion_failed:<stage>:<comma-separated-fields>`. Persistent, boot-time, disabled, provider-context, action-right, unknown bits and INDEXED combined with any other bit are rejected. The [official FILTER0 reference](https://learn.microsoft.com/en-us/windows/win32/api/fwpmtypes/ns-fwpmtypes-fwpm_filter0) describes INDEXED as a classification lookup optimization; [WinSDK fwpmtypes.h](https://github.com/microsoft/win32metadata/blob/main/generation/WinSDK/RecompiledIdlHeaders/shared/fwpmtypes.h) defines it as 0x00000040. Those sources do not identify the previous failure's actual flags. The complete v05 failure, cleanup and prior source/EXE remain archived for review.
