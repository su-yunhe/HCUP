using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Security.Principal;
using System.Text.RegularExpressions;
using System.Threading;
using System.Web.Script.Serialization;

namespace VgSpec1.NetworkIsolation
{
    internal static class Program
    {
        private static volatile bool cancelRequested;

        private static int Main(string[] args)
        {
            try
            {
                Dictionary<string, string> options = ParseOptions(args);
                Dictionary<string, int> layout = NativeWfp.CheckLayout();
                bool serve = options.ContainsKey("--serve");
                if (!serve) return Check(options, layout);
                // No native WFP method is reachable by an unelevated caller.
                if (!IsAdministrator()) throw new UnauthorizedAccessException("Serve requires the user to launch an elevated console manually; no UAC is requested.");
                string nonce = Required(options, "--nonce");
                if (!Regex.IsMatch(nonce, "^[a-f0-9]{32}$")) throw new ArgumentException("Nonce must be exactly 32 lowercase hex characters.");
                TargetGuard target = CreateTarget(options);
                target.Validate(true);
                string runDirectory = TargetGuard.RequireLogsDirectory(Required(options, "--run-dir"));
                int lifetime = Number(options, "--max-seconds", 1200, 30, 1800);
                int blockLimit = Number(options, "--max-block-seconds", 600, 5, 900);
                bool created;
                using (Mutex single = new Mutex(true, @"Local\VgSpec1WfpIsolatedEmulator61", out created))
                {
                    if (!created) throw new InvalidOperationException("Another helper already owns the local isolated-emulator guard.");
                    try
                    {
                        using (RunFiles files = new RunFiles(runDirectory, nonce))
                        using (WfpSession session = new WfpSession(files.Log))
                        {
                            Console.CancelKeyPress += delegate(object sender, ConsoleCancelEventArgs eventArgs) { eventArgs.Cancel = true; cancelRequested = true; };
                            EventHandler onExit = delegate { session.Close(); };
                            AppDomain.CurrentDomain.ProcessExit += onExit;
                            try { return Serve(files, session, target, nonce, lifetime, blockLimit); }
                            finally { AppDomain.CurrentDomain.ProcessExit -= onExit; }
                        }
                    }
                    finally { single.ReleaseMutex(); }
                }
            }
            catch (Exception error)
            {
                Console.Error.WriteLine(new JavaScriptSerializer().Serialize(WfpSession.Fields(
                    "event", "startup_or_check_failed", "reason", error.Message, "nativeEngineOpenedByCheck", false)));
                return 2;
            }
        }

        private static int Check(Dictionary<string, string> options, Dictionary<string, int> layout)
        {
            object targetResult = "not_requested";
            if (options.ContainsKey("--target-pid"))
            {
                TargetGuard target = CreateTarget(options);
                target.Validate(true);
                targetResult = target.Snapshot();
            }
            bool exists = File.Exists(TargetGuard.AllowedExecutable);
            if (exists) TargetGuard.RejectReparsePoints(TargetGuard.AllowedExecutable);
            Dictionary<string, object> report = WfpSession.Fields("mode", "check", "nativeWfpCalls", 0,
                "engineOpen", false, "administrator", IsAdministrator(), "pointerBytes", IntPtr.Size,
                "layout", layout, "fixedExecutable", TargetGuard.AllowedExecutable, "fixedExecutableExists", exists,
                "fixedExecutableSha256", exists ? TargetGuard.HashFile(TargetGuard.AllowedExecutable) : null,
                "guids", WfpSession.Fields("connectV4", NativeWfp.ConnectV4.ToString(), "connectV6", NativeWfp.ConnectV6.ToString(),
                    "appId", NativeWfp.AppIdCondition.ToString()),
                "target", targetResult, "constants", WfpSession.Fields("dynamic", NativeWfp.DynamicSession,
                    "empty", NativeWfp.Empty, "byteBlob", NativeWfp.ByteBlobType, "equal", NativeWfp.MatchEqual,
                    "block", NativeWfp.ActionBlock, "rpcAuthWinnt", NativeWfp.RpcAuthWinnt));
            Console.WriteLine(new JavaScriptSerializer().Serialize(report));
            return 0;
        }

        private static int Serve(RunFiles files, WfpSession session, TargetGuard target, string nonce, int lifetime, int blockLimit)
        {
            Stopwatch clock = Stopwatch.StartNew();
            DateTime startUtc = DateTime.UtcNow;
            DateTime totalDeadline = startUtc.AddSeconds(lifetime);
            DateTime requestExpires = startUtc.AddSeconds(45);
            DateTime? acceptedUtc = null;
            DateTime? blockDeadline = null;
            double leaseUntil = Math.Min(45, lifetime);
            double blockUntil = Double.PositiveInfinity;
            double nextHash = 10;
            long sequence = 0;
            string state = "IDLE_UNBLOCKED";
            string reason = null;
            int exitCode = 0;
            SafetyWatchdog watchdog = new SafetyWatchdog(clock, lifetime);
            files.Log("ready", WfpSession.Fields("state", state, "active", false, "helperPid", Process.GetCurrentProcess().Id,
                "target", target.Snapshot(), "totalDeadlineUtc", totalDeadline.ToString("o"), "tickMilliseconds", 1000,
                "proof", "No filters exist until a valid block request; ACK is configuration evidence, not traffic-drop proof."));
            try
            {
                while (true)
                {
                    if (cancelRequested) { reason = "console_cancel"; state = "EXITED_UNBLOCKED"; break; }
                    if (clock.Elapsed.TotalSeconds >= lifetime) throw new InvalidOperationException("total_deadline_expired");
                    if (clock.Elapsed.TotalSeconds >= leaseUntil) throw new InvalidOperationException("controller_lease_expired");
                    if (session.Active && clock.Elapsed.TotalSeconds >= blockUntil) throw new InvalidOperationException("absolute_block_deadline_expired");
                    bool hash = clock.Elapsed.TotalSeconds >= nextHash;
                    target.Validate(hash);
                    if (hash) nextHash = clock.Elapsed.TotalSeconds + 10;
                    ControlRequest request = files.ReadRequest(sequence);
                    if (request != null)
                    {
                        sequence = request.Sequence;
                        acceptedUtc = DateTime.UtcNow;
                        requestExpires = request.ExpiresUtc;
                        leaseUntil = clock.Elapsed.TotalSeconds + Math.Min(15, (requestExpires - acceptedUtc.Value).TotalSeconds);
                        watchdog.SetLease(leaseUntil);
                        if (request.Operation == "block")
                        {
                            target.Validate(true);
                            if (!session.Active)
                            {
                                blockUntil = Math.Min(lifetime, clock.Elapsed.TotalSeconds + blockLimit);
                                blockDeadline = startUtc.AddSeconds(blockUntil);
                                watchdog.SetBlock(blockUntil);
                                session.Block();
                                target.Validate(false);
                                if (clock.Elapsed.TotalSeconds >= leaseUntil || clock.Elapsed.TotalSeconds >= blockUntil)
                                    throw new InvalidOperationException("lease_or_block_deadline_expired_during_activation");
                                files.Log("armed", WfpSession.Fields("filters", session.Filters, "target", target.Snapshot(),
                                    "sessionGuid", session.SessionGuid.ToString(), "subLayerGuid", session.SubLayerGuid.ToString(),
                                    "blockDeadlineUtc", blockDeadline.Value.ToString("o"), "proof", "filter_configuration_only"));
                            }
                            state = "BLOCKED";
                        }
                        else
                        {
                            if (!session.Close()) throw new InvalidOperationException("native_close_failed");
                            state = request.Operation == "exit" ? "EXITED_UNBLOCKED" : "IDLE_UNBLOCKED";
                            blockUntil = Double.PositiveInfinity;
                            blockDeadline = null;
                            watchdog.SetBlock(Double.PositiveInfinity);
                        }
                        files.Log("control_accepted", WfpSession.Fields("sequence", sequence, "operation", request.Operation,
                            "state", state, "active", session.Active, "filters", session.Filters));
                        if (request.Operation == "exit") { reason = "exit_request"; break; }
                    }
                    WriteStatus(files, session, target, nonce, state, reason, sequence, acceptedUtc, requestExpires, totalDeadline, blockDeadline);
                    Thread.Sleep(1000);
                }
            }
            catch (Exception error)
            {
                reason = error.Message;
                state = "ERROR_UNBLOCKED";
                exitCode = 3;
                files.Log("fail_safe", WfpSession.Fields("reason", reason));
            }
            finally
            {
                if (!session.Close()) { state = "ERROR_CLEANUP_UNCONFIRMED"; reason = "native_close_failed_process_exit_required"; exitCode = 4; }
                WriteStatus(files, session, target, nonce, state, reason, sequence, acceptedUtc, requestExpires, totalDeadline, null);
                files.Log("finished", WfpSession.Fields("state", state, "reason", reason, "exitCode", exitCode,
                    "active", session.Active, "nativeEngineOpen", session.EngineOpen));
                watchdog.Dispose();
            }
            return exitCode;
        }

        private static void WriteStatus(RunFiles files, WfpSession session, TargetGuard target, string nonce, string state,
            string reason, long sequence, DateTime? acceptedUtc, DateTime expires, DateTime totalDeadline, DateTime? blockDeadline)
        {
            files.WriteStatus(WfpSession.Fields("schemaVersion", 1, "task", "vg-spec1", "nonce", nonce,
                "state", state, "active", session.Active, "helperPid", Process.GetCurrentProcess().Id,
                "timestampUtc", DateTime.UtcNow.ToString("o"), "lastAcceptedSequence", sequence,
                "lastAcceptedUtc", acceptedUtc.HasValue ? acceptedUtc.Value.ToString("o") : null,
                "requestExpiresUtc", expires.ToString("o"), "totalDeadlineUtc", totalDeadline.ToString("o"),
                "blockDeadlineUtc", blockDeadline.HasValue ? blockDeadline.Value.ToString("o") : null,
                "target", target.Snapshot(), "filters", session.Filters, "nativeEngineOpen", session.EngineOpen,
                "sessionGuid", session.SessionGuid.ToString(), "subLayerGuid", session.SubLayerGuid.ToString(),
                "terminationReason", reason, "auditMode", "not_enabled", "proof", "filter_configuration_only"));
        }

        private static TargetGuard CreateTarget(Dictionary<string, string> options)
        {
            return new TargetGuard(Int32.Parse(Required(options, "--target-pid"), CultureInfo.InvariantCulture),
                RunFiles.ParseUtc(Required(options, "--target-start-utc")), Required(options, "--target-sha256"),
                Required(options, "--instance-root"));
        }
        private static bool IsAdministrator()
        {
            using (WindowsIdentity identity = WindowsIdentity.GetCurrent())
                return new WindowsPrincipal(identity).IsInRole(WindowsBuiltInRole.Administrator);
        }
        private static Dictionary<string, string> ParseOptions(string[] args)
        {
            HashSet<string> values = new HashSet<string>(new[] { "--run-dir", "--nonce", "--target-pid", "--target-start-utc",
                "--target-sha256", "--instance-root", "--max-seconds", "--max-block-seconds" }, StringComparer.Ordinal);
            Dictionary<string, string> result = new Dictionary<string, string>(StringComparer.Ordinal);
            foreach (string key in args) if (key == null) throw new ArgumentException("Null argument.");
            for (int index = 0; index < args.Length; index++)
            {
                string key = args[index];
                if (result.ContainsKey(key)) throw new ArgumentException("Duplicate option: " + key);
                if (key == "--check" || key == "--serve") result.Add(key, "true");
                else if (values.Contains(key) && index + 1 < args.Length) result.Add(key, args[++index]);
                else throw new ArgumentException("Unknown/incomplete option: " + key);
            }
            if (result.ContainsKey("--check") && result.ContainsKey("--serve")) throw new ArgumentException("Choose check or serve.");
            return result;
        }
        private static string Required(Dictionary<string, string> options, string key)
        {
            string value;
            if (!options.TryGetValue(key, out value) || String.IsNullOrEmpty(value)) throw new ArgumentException("Missing " + key);
            return value;
        }
        private static int Number(Dictionary<string, string> options, string key, int fallback, int minimum, int maximum)
        {
            string text;
            int result = options.TryGetValue(key, out text) ? Int32.Parse(text, CultureInfo.InvariantCulture) : fallback;
            if (result < minimum || result > maximum) throw new ArgumentException(key + " is outside the bounded range.");
            return result;
        }
    }
}
