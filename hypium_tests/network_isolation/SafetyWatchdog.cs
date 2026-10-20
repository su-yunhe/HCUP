using System;
using System.Diagnostics;
using System.Threading;

namespace VgSpec1.NetworkIsolation
{
    // Independent of synchronous BFE/WMI calls in the main loop. In normal operation
    // the main loop closes and records ERROR first; this is the hung-call backstop.
    internal sealed class SafetyWatchdog : IDisposable
    {
        private readonly Stopwatch clock;
        private readonly double totalSeconds;
        private readonly Thread thread;
        private long leaseDeadlineMilliseconds;
        private long blockDeadlineMilliseconds = Int64.MaxValue;
        private volatile bool stopped;

        internal SafetyWatchdog(Stopwatch runtimeClock, double lifetime)
        {
            clock = runtimeClock;
            totalSeconds = lifetime;
            SetLease(Math.Min(45, lifetime));
            thread = new Thread(Watch) { IsBackground = true, Name = "vg-spec1-dynamic-session-safety" };
            thread.Start();
        }
        internal void SetLease(double elapsedDeadlineSeconds)
        {
            Interlocked.Exchange(ref leaseDeadlineMilliseconds, (long)(elapsedDeadlineSeconds * 1000));
        }
        internal void SetBlock(double elapsedDeadlineSeconds)
        {
            Interlocked.Exchange(ref blockDeadlineMilliseconds, Double.IsPositiveInfinity(elapsedDeadlineSeconds)
                ? Int64.MaxValue : (long)(elapsedDeadlineSeconds * 1000));
        }
        private void Watch()
        {
            while (!stopped)
            {
                long deadline = Math.Min((long)(totalSeconds * 1000),
                    Math.Min(Interlocked.Read(ref leaseDeadlineMilliseconds), Interlocked.Read(ref blockDeadlineMilliseconds)));
                if (clock.ElapsedMilliseconds > deadline + 3000 && !stopped)
                {
                    // Do not wait on a logger/native lock that may be hung. WFP's
                    // process/RPC rundown deletes this dynamic session's objects.
                    Environment.FailFast("vg-spec1 WFP helper safety deadline exceeded during a hung operation; dynamic-session process cleanup required.");
                }
                Thread.Sleep(250);
            }
        }
        public void Dispose()
        {
            stopped = true;
            thread.Join(1000);
        }
    }
}
