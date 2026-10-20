using System;
using System.Collections.Generic;

namespace VgSpec1.NetworkIsolation
{
    // Only WfpSession.Close supplies its own recorded IDs/key; no external query input.
    internal static class RemovalObserver
    {
        internal static bool Verify(List<FilterRecord> filters, Guid subLayer,
            Action<string, Dictionary<string, object>> log)
        {
            IntPtr observer = IntPtr.Zero;
            bool transaction = false;
            bool success = false;
            bool evidenceLogged = true;
            bool observerClosed = true;
            try
            {
                NativeWfp.CheckLayout();
                if (subLayer == Guid.Empty || filters.Count > 2)
                    throw new InvalidOperationException("Invalid owned cleanup scope.");
                uint code = NativeWfp.FwpmEngineOpen0(IntPtr.Zero, NativeWfp.RpcAuthWinnt,
                    IntPtr.Zero, IntPtr.Zero, out observer);
                evidenceLogged &= Record(log, "cleanup_observer_call", WfpSession.Fields(
                    "function", "FwpmEngineOpen0", "returnCode", code));
                if (code != 0 || observer == IntPtr.Zero) throw new InvalidOperationException("cleanup_observer_open_failed");
                code = NativeWfp.FwpmTransactionBegin0(observer, NativeWfp.ReadOnlyTransaction);
                evidenceLogged &= Record(log, "cleanup_observer_call", WfpSession.Fields(
                    "function", "FwpmTransactionBegin0", "flags", NativeWfp.ReadOnlyTransaction, "returnCode", code));
                if (code != 0) throw new InvalidOperationException("cleanup_observer_read_transaction_failed");
                transaction = true;
                success = true;
                foreach (FilterRecord filter in filters)
                {
                    IntPtr returned = IntPtr.Zero;
                    bool removed;
                    try
                    {
                        code = NativeWfp.FwpmFilterGetById0(observer, UInt64.Parse(filter.id), out returned);
                        removed = code == NativeWfp.FilterNotFound && returned == IntPtr.Zero;
                        success &= removed;
                        evidenceLogged &= Record(log, "cleanup_filter_query", WfpSession.Fields(
                            "function", "FwpmFilterGetById0", "filter", filter, "returnCode", code,
                            "expectedReturnCode", NativeWfp.FilterNotFound, "removed", removed));
                    }
                    finally { if (returned != IntPtr.Zero) NativeWfp.FwpmFreeMemory0(ref returned); }
                }
                IntPtr returnedSubLayer = IntPtr.Zero;
                try
                {
                    code = NativeWfp.FwpmSubLayerGetByKey0(observer, ref subLayer, out returnedSubLayer);
                    bool removed = code == NativeWfp.SubLayerNotFound && returnedSubLayer == IntPtr.Zero;
                    success &= removed;
                    evidenceLogged &= Record(log, "cleanup_sublayer_query", WfpSession.Fields(
                        "function", "FwpmSubLayerGetByKey0", "subLayerGuid", subLayer.ToString(),
                        "returnCode", code, "expectedReturnCode", NativeWfp.SubLayerNotFound, "removed", removed));
                }
                finally { if (returnedSubLayer != IntPtr.Zero) NativeWfp.FwpmFreeMemory0(ref returnedSubLayer); }
            }
            catch (Exception error)
            {
                success = false;
                evidenceLogged &= Record(log, "cleanup_observer_failed", WfpSession.Fields("reason", error.Message));
            }
            finally
            {
                // Abort/log failures cannot skip closing the independent observer handle.
                try
                {
                    if (transaction)
                    {
                        uint code = NativeWfp.FwpmTransactionAbort0(observer);
                        success &= code == 0;
                        evidenceLogged &= Record(log, "cleanup_observer_call", WfpSession.Fields(
                            "function", "FwpmTransactionAbort0", "returnCode", code));
                    }
                }
                catch (Exception error)
                {
                    success = false;
                    evidenceLogged &= Record(log, "cleanup_observer_failed", WfpSession.Fields("reason", error.Message));
                }
                finally
                {
                    if (observer != IntPtr.Zero)
                    {
                        try
                        {
                            uint code = NativeWfp.FwpmEngineClose0(observer);
                            observerClosed = code == 0;
                            success &= observerClosed;
                            evidenceLogged &= Record(log, "cleanup_observer_call", WfpSession.Fields(
                                "function", "FwpmEngineClose0", "returnCode", code));
                        }
                        catch (Exception error)
                        {
                            success = false;
                            observerClosed = false;
                            evidenceLogged &= Record(log, "cleanup_observer_failed", WfpSession.Fields("reason", error.Message));
                        }
                    }
                }
            }
            success &= evidenceLogged;
            return Record(log, "cleanup_verification", WfpSession.Fields("success", success,
                "filters", filters, "subLayerGuid", subLayer.ToString(), "readOnlyTransaction", true,
                "observerClosed", observerClosed, "expectedFilterReturnCode", NativeWfp.FilterNotFound,
                "expectedSubLayerReturnCode", NativeWfp.SubLayerNotFound)) && success;
        }

        private static bool Record(Action<string, Dictionary<string, object>> log, string eventName,
            Dictionary<string, object> fields)
        {
            try { log(eventName, fields); return true; }
            catch (Exception) { Console.Error.WriteLine("Cleanup observer logging failed; removal cannot be confirmed."); return false; }
        }
    }
}
