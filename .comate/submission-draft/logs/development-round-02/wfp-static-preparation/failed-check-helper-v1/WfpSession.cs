using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Security.Cryptography;

namespace VgSpec1.NetworkIsolation
{
    internal sealed class FilterRecord
    {
        public string id;
        public string key;
        public string layerGuid;
        public string layerName;
        public bool verified;
    }

    internal sealed class WfpSession : IDisposable
    {
        private readonly Action<string, Dictionary<string, object>> log;
        private IntPtr engine = IntPtr.Zero;
        private IntPtr appId = IntPtr.Zero;
        private byte[] appIdBytes;
        internal bool Active { get; private set; }
        internal bool EngineOpen { get { return engine != IntPtr.Zero; } }
        internal Guid SessionGuid { get; private set; }
        internal Guid SubLayerGuid { get; private set; }
        internal readonly List<FilterRecord> Filters = new List<FilterRecord>();

        internal WfpSession(Action<string, Dictionary<string, object>> logger) { log = logger; }

        internal void Block()
        {
            if (Active) return;
            NativeWfp.CheckLayout(); // Required again immediately before every engine open.
            bool transaction = false;
            SessionGuid = Guid.NewGuid();
            SubLayerGuid = Guid.NewGuid();
            IntPtr name = Marshal.StringToHGlobalUni("vg-spec1 dynamic isolation " + SessionGuid);
            try
            {
                Call("FwpmGetAppIdFromFileName0", NativeWfp.FwpmGetAppIdFromFileName0(TargetGuard.AllowedExecutable, out appId));
                appIdBytes = ReadBlob(appId);
                if (appIdBytes.Length == 0) throw new InvalidOperationException("APP_ID must not be empty.");
                NativeWfp.Session session = new NativeWfp.Session();
                session.sessionKey = SessionGuid;
                session.displayData.name = name;
                session.flags = NativeWfp.DynamicSession;
                session.txnWaitTimeoutInMSec = 5000;
                using (NativeAllocation allocation = new NativeAllocation(session))
                    Call("FwpmEngineOpen0", NativeWfp.FwpmEngineOpen0(IntPtr.Zero, NativeWfp.RpcAuthWinnt,
                        IntPtr.Zero, allocation.Pointer, out engine));
                Call("FwpmTransactionBegin0", NativeWfp.FwpmTransactionBegin0(engine, 0));
                transaction = true;
                NativeWfp.SubLayer subLayer = new NativeWfp.SubLayer();
                subLayer.subLayerKey = SubLayerGuid;
                subLayer.displayData.name = name;
                subLayer.flags = 0;
                subLayer.weight = 0x100;
                using (NativeAllocation allocation = new NativeAllocation(subLayer))
                    Call("FwpmSubLayerAdd0", NativeWfp.FwpmSubLayerAdd0(engine, allocation.Pointer, IntPtr.Zero));
                AddFilter(NativeWfp.ConnectV4, "ALE_AUTH_CONNECT_V4", name);
                AddFilter(NativeWfp.ConnectV6, "ALE_AUTH_CONNECT_V6", name);
                // No assumption/fallback: inability to read our uncommitted objects aborts.
                VerifyFilters("pre_commit");
                Call("FwpmTransactionCommit0", NativeWfp.FwpmTransactionCommit0(engine));
                transaction = false;
                VerifyFilters("post_commit");
                Active = true;
            }
            catch
            {
                if (transaction && engine != IntPtr.Zero)
                    log("native_call", Fields("function", "FwpmTransactionAbort0", "returnCode", NativeWfp.FwpmTransactionAbort0(engine)));
                Close();
                throw;
            }
            finally { Marshal.FreeHGlobal(name); }
        }

        private void AddFilter(Guid layer, string layerName, IntPtr name)
        {
            NativeWfp.FilterCondition condition = new NativeWfp.FilterCondition();
            condition.fieldKey = NativeWfp.AppIdCondition;
            condition.matchType = NativeWfp.MatchEqual;
            condition.conditionValue.type = NativeWfp.ByteBlobType;
            condition.conditionValue.pointer = appId;
            NativeWfp.Filter filter = new NativeWfp.Filter();
            filter.filterKey = Guid.NewGuid();
            filter.displayData.name = name;
            filter.flags = 0;
            filter.layerKey = layer;
            filter.subLayerKey = SubLayerGuid;
            filter.weight.type = NativeWfp.Empty;
            filter.action.type = NativeWfp.ActionBlock;
            filter.numFilterConditions = 1;
            using (NativeAllocation conditionMemory = new NativeAllocation(condition))
            {
                filter.filterCondition = conditionMemory.Pointer;
                AssertInputScope(filter, condition);
                using (NativeAllocation filterMemory = new NativeAllocation(filter))
                {
                    ulong id;
                    Call("FwpmFilterAdd0", NativeWfp.FwpmFilterAdd0(engine, filterMemory.Pointer, IntPtr.Zero, out id));
                    if (id == 0) throw new InvalidOperationException("BFE returned an empty filter ID.");
                    FilterRecord record = new FilterRecord { id = id.ToString(), key = filter.filterKey.ToString(),
                        layerGuid = layer.ToString(), layerName = layerName, verified = false };
                    Filters.Add(record);
                    log("filter_added", Fields("filter", record, "subLayerGuid", SubLayerGuid.ToString(),
                        "path", TargetGuard.AllowedExecutable, "appIdSha256", HashBytes(appIdBytes)));
                }
            }
        }

        private void AssertInputScope(NativeWfp.Filter filter, NativeWfp.FilterCondition condition)
        {
            if (filter.flags != 0 || filter.subLayerKey != SubLayerGuid || SubLayerGuid == Guid.Empty ||
                (filter.layerKey != NativeWfp.ConnectV4 && filter.layerKey != NativeWfp.ConnectV6) ||
                filter.action.type != NativeWfp.ActionBlock || filter.numFilterConditions != 1 ||
                filter.filterCondition == IntPtr.Zero || condition.fieldKey != NativeWfp.AppIdCondition ||
                condition.matchType != NativeWfp.MatchEqual || condition.conditionValue.type != NativeWfp.ByteBlobType ||
                condition.conditionValue.pointer == IntPtr.Zero || appIdBytes == null || appIdBytes.Length == 0)
                throw new InvalidOperationException("Refusing a filter outside the exact APP_ID/layer scope.");
        }

        private void VerifyFilters(string phase)
        {
            if (Filters.Count != 2) throw new InvalidOperationException("Exactly two filters are required.");
            foreach (FilterRecord expected in Filters)
            {
                IntPtr returned = IntPtr.Zero;
                try
                {
                    Call("FwpmFilterGetById0", NativeWfp.FwpmFilterGetById0(engine, UInt64.Parse(expected.id), out returned));
                    if (returned == IntPtr.Zero) throw new InvalidOperationException("BFE returned a null filter.");
                    NativeWfp.Filter actual = (NativeWfp.Filter)Marshal.PtrToStructure(returned, typeof(NativeWfp.Filter));
                    if (actual.numFilterConditions != 1 || actual.filterCondition == IntPtr.Zero)
                        throw new InvalidOperationException("BFE filter does not have exactly one condition.");
                    NativeWfp.FilterCondition condition = (NativeWfp.FilterCondition)Marshal.PtrToStructure(
                        actual.filterCondition, typeof(NativeWfp.FilterCondition));
                    AssertInputScope(actual, condition);
                    if (actual.filterKey != new Guid(expected.key) || actual.filterId.ToString() != expected.id ||
                        actual.layerKey != new Guid(expected.layerGuid) || !EqualBytes(ReadBlob(condition.conditionValue.pointer), appIdBytes))
                        throw new InvalidOperationException("Filter readback identity/APP_ID mismatch.");
                    expected.verified = true;
                    log("filter_verified", Fields("phase", phase, "filter", expected, "flags", actual.flags,
                        "action", actual.action.type, "numConditions", actual.numFilterConditions,
                        "conditionKey", condition.fieldKey.ToString(), "matchType", condition.matchType,
                        "conditionType", condition.conditionValue.type, "appIdBytes", appIdBytes.Length,
                        "appIdSha256", HashBytes(appIdBytes), "subLayerGuid", actual.subLayerKey.ToString()));
                }
                finally { if (returned != IntPtr.Zero) NativeWfp.FwpmFreeMemory0(ref returned); }
            }
        }

        internal bool Close()
        {
            uint code = 0;
            bool engineWasOpen = engine != IntPtr.Zero;
            if (engine != IntPtr.Zero)
            {
                code = NativeWfp.FwpmEngineClose0(engine);
                if (code != 0)
                {
                    try { log("native_call", Fields("function", "FwpmEngineClose0", "returnCode", code)); }
                    catch (Exception) { Console.Error.WriteLine("NativeClose failed and logging also failed."); }
                    return false;
                }
                engine = IntPtr.Zero;
            }
            Active = false;
            Filters.Clear();
            if (appId != IntPtr.Zero) NativeWfp.FwpmFreeMemory0(ref appId);
            appIdBytes = null;
            // Logging failure must never prevent the successful native cleanup above.
            try { if (engineWasOpen) log("session_closed", Fields("function", "FwpmEngineClose0", "returnCode", code)); }
            catch (Exception) { Console.Error.WriteLine("Session closed; logging failed."); }
            return true;
        }

        public void Dispose() { Close(); }

        private void Call(string function, uint code)
        {
            log("native_call", Fields("function", function, "returnCode", code));
            if (code != 0) throw new InvalidOperationException(function + " failed: 0x" + code.ToString("x8"));
        }
        private static byte[] ReadBlob(IntPtr pointer)
        {
            if (pointer == IntPtr.Zero) throw new InvalidOperationException("Null APP_ID blob.");
            NativeWfp.ByteBlob blob = (NativeWfp.ByteBlob)Marshal.PtrToStructure(pointer, typeof(NativeWfp.ByteBlob));
            if (blob.size == 0 || blob.size > 65536 || blob.data == IntPtr.Zero)
                throw new InvalidOperationException("Invalid APP_ID blob size/data.");
            byte[] bytes = new byte[blob.size];
            Marshal.Copy(blob.data, bytes, 0, bytes.Length);
            return bytes;
        }
        private static bool EqualBytes(byte[] left, byte[] right)
        {
            if (left.Length != right.Length) return false;
            for (int index = 0; index < left.Length; index++) if (left[index] != right[index]) return false;
            return true;
        }
        private static string HashBytes(byte[] bytes)
        {
            using (SHA256 hash = SHA256.Create())
                return BitConverter.ToString(hash.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }
        internal static Dictionary<string, object> Fields(params object[] pairs)
        {
            Dictionary<string, object> fields = new Dictionary<string, object>();
            for (int index = 0; index < pairs.Length; index += 2) fields.Add((string)pairs[index], pairs[index + 1]);
            return fields;
        }
    }
}
