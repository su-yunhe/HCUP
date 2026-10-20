using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace VgSpec1.NetworkIsolation
{
    // ABI and constants: Microsoft win32metadata WinSDK headers / Microsoft Learn.
    internal static class NativeWfp
    {
        internal const uint DynamicSession = 1;
        internal const uint Empty = 0;
        internal const uint ByteBlobType = 12;
        internal const uint MatchEqual = 0;
        internal const uint ActionBlock = 0x1001;
        internal const uint RpcAuthWinnt = 10;
        internal const uint ReadOnlyTransaction = 1;
        internal const uint FilterNotFound = 0x80320003;
        internal const uint SubLayerNotFound = 0x80320007;
        internal const uint FilterIndexed = 0x00000040;
        internal static readonly Guid ConnectV4 = new Guid("c38d57d1-05a7-4c33-904f-7fbceee60e82");
        internal static readonly Guid ConnectV6 = new Guid("4a72393b-319f-44bc-84c3-ba54dcb3b6b4");
        internal static readonly Guid AppIdCondition = new Guid("d78e1e87-8644-4ea5-9437-d809ecefc971");

        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        [DllImport("fwpuclnt.dll", ExactSpelling = true)]
        internal static extern uint FwpmEngineOpen0(IntPtr serverName, uint authnService,
            IntPtr authIdentity, IntPtr session, out IntPtr engineHandle);
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        [DllImport("fwpuclnt.dll", ExactSpelling = true, CharSet = CharSet.Unicode)]
        internal static extern uint FwpmGetAppIdFromFileName0(string fileName, out IntPtr appId);
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        [DllImport("fwpuclnt.dll", ExactSpelling = true)]
        internal static extern uint FwpmTransactionBegin0(IntPtr engineHandle, uint flags);
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        [DllImport("fwpuclnt.dll", ExactSpelling = true)]
        internal static extern uint FwpmSubLayerAdd0(IntPtr engineHandle, IntPtr subLayer, IntPtr securityDescriptor);
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        [DllImport("fwpuclnt.dll", ExactSpelling = true)]
        internal static extern uint FwpmFilterAdd0(IntPtr engineHandle, IntPtr filter,
            IntPtr securityDescriptor, out ulong filterId);
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        [DllImport("fwpuclnt.dll", ExactSpelling = true)]
        internal static extern uint FwpmFilterGetById0(IntPtr engineHandle, ulong filterId, out IntPtr filter);
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        [DllImport("fwpuclnt.dll", ExactSpelling = true)]
        internal static extern uint FwpmSubLayerGetByKey0(IntPtr engineHandle, ref Guid key, out IntPtr subLayer);
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        [DllImport("fwpuclnt.dll", ExactSpelling = true)]
        internal static extern uint FwpmTransactionCommit0(IntPtr engineHandle);
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        [DllImport("fwpuclnt.dll", ExactSpelling = true)]
        internal static extern uint FwpmTransactionAbort0(IntPtr engineHandle);
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        [DllImport("fwpuclnt.dll", ExactSpelling = true)]
        internal static extern uint FwpmEngineClose0(IntPtr engineHandle);
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        [DllImport("fwpuclnt.dll", ExactSpelling = true)]
        internal static extern void FwpmFreeMemory0(ref IntPtr memory);

        internal static Dictionary<string, int> CheckLayout()
        {
            if (IntPtr.Size != 8) throw new InvalidOperationException("Only an x64 process is supported.");
            Dictionary<string, int> result = new Dictionary<string, int>();
            CheckSize<DisplayData>(16, result);
            CheckSize<ByteBlob>(16, result);
            CheckSize<Value>(16, result);
            CheckSize<Session>(72, result);
            CheckSize<SubLayer>(72, result);
            CheckSize<FilterCondition>(40, result);
            CheckSize<Action>(20, result);
            CheckSize<ContextUnion>(16, result);
            CheckSize<Filter>(200, result);
            CheckOffset<DisplayData>("description", 8, result);
            CheckOffset<ByteBlob>("data", 8, result);
            CheckOffset<Value>("pointer", 8, result);
            CheckOffset<Session>("flags", 32, result);
            CheckOffset<Session>("txnWaitTimeoutInMSec", 36, result);
            CheckOffset<Session>("processId", 40, result);
            CheckOffset<Session>("sid", 48, result);
            CheckOffset<Session>("username", 56, result);
            CheckOffset<Session>("kernelMode", 64, result);
            CheckOffset<SubLayer>("weight", 64, result);
            CheckOffset<FilterCondition>("matchType", 16, result);
            CheckOffset<FilterCondition>("conditionValue", 24, result);
            CheckOffset<Action>("filterType", 4, result);
            CheckOffset<Filter>("flags", 32, result);
            CheckOffset<Filter>("providerKey", 40, result);
            CheckOffset<Filter>("providerData", 48, result);
            CheckOffset<Filter>("layerKey", 64, result);
            CheckOffset<Filter>("subLayerKey", 80, result);
            CheckOffset<Filter>("weight", 96, result);
            CheckOffset<Filter>("numFilterConditions", 112, result);
            CheckOffset<Filter>("filterCondition", 120, result);
            CheckOffset<Filter>("action", 128, result);
            CheckOffset<Filter>("context", 152, result);
            CheckOffset<Filter>("reserved", 168, result);
            CheckOffset<Filter>("filterId", 176, result);
            CheckOffset<Filter>("effectiveWeight", 184, result);
            return result;
        }

        private static void CheckSize<T>(int expected, Dictionary<string, int> result)
        {
            int actual = Marshal.SizeOf(typeof(T));
            result.Add(typeof(T).Name + ".size", actual);
            if (actual != expected) throw new InvalidOperationException(typeof(T).Name + " size mismatch.");
        }

        private static void CheckOffset<T>(string field, int expected, Dictionary<string, int> result)
        {
            int actual = Marshal.OffsetOf(typeof(T), field).ToInt32();
            result.Add(typeof(T).Name + "." + field, actual);
            if (actual != expected) throw new InvalidOperationException(typeof(T).Name + "." + field + " offset mismatch.");
        }

        [StructLayout(LayoutKind.Sequential)]
        internal struct DisplayData { internal IntPtr name; internal IntPtr description; }
        [StructLayout(LayoutKind.Sequential)]
        internal struct ByteBlob { internal uint size; internal IntPtr data; }
        [StructLayout(LayoutKind.Explicit, Size = 16)]
        internal struct Value
        {
            [FieldOffset(0)] internal uint type;
            [FieldOffset(8)] internal IntPtr pointer;
        }
        [StructLayout(LayoutKind.Sequential)]
        internal struct Session
        {
            internal Guid sessionKey;
            internal DisplayData displayData;
            internal uint flags;
            internal uint txnWaitTimeoutInMSec;
            internal uint processId; // BFE's management-client PID, never a target condition.
            internal IntPtr sid;
            internal IntPtr username;
            internal int kernelMode;
        }
        [StructLayout(LayoutKind.Sequential)]
        internal struct SubLayer
        {
            internal Guid subLayerKey;
            internal DisplayData displayData;
            internal uint flags;
            internal IntPtr providerKey;
            internal ByteBlob providerData;
            internal ushort weight;
        }
        [StructLayout(LayoutKind.Sequential)]
        internal struct FilterCondition
        {
            internal Guid fieldKey;
            internal uint matchType;
            internal Value conditionValue;
        }
        [StructLayout(LayoutKind.Sequential)]
        internal struct Action { internal uint type; internal Guid filterType; }
        [StructLayout(LayoutKind.Explicit, Size = 16)]
        internal struct ContextUnion
        {
            [FieldOffset(0)] internal ulong rawContext;
            [FieldOffset(0)] internal Guid providerContextKey;
        }
        [StructLayout(LayoutKind.Sequential)]
        internal struct Filter
        {
            internal Guid filterKey;
            internal DisplayData displayData;
            internal uint flags;
            internal IntPtr providerKey;
            internal ByteBlob providerData;
            internal Guid layerKey;
            internal Guid subLayerKey;
            internal Value weight;
            internal uint numFilterConditions;
            internal IntPtr filterCondition;
            internal Action action;
            internal ContextUnion context;
            internal IntPtr reserved;
            internal ulong filterId;
            internal Value effectiveWeight;
        }
    }

    internal sealed class NativeAllocation : IDisposable
    {
        internal IntPtr Pointer { get; private set; }
        internal NativeAllocation(object value)
        {
            Pointer = Marshal.AllocHGlobal(Marshal.SizeOf(value));
            Marshal.StructureToPtr(value, Pointer, false);
        }
        public void Dispose()
        {
            if (Pointer != IntPtr.Zero) Marshal.FreeHGlobal(Pointer);
            Pointer = IntPtr.Zero;
        }
    }
}
