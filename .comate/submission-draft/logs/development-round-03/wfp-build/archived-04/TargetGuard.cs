using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Management;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text.RegularExpressions;

namespace VgSpec1.NetworkIsolation
{
    internal sealed class TargetGuard
    {
        internal const string AllowedExecutable = @"D:\HarmonyDev\vg-spec1-isolated-emulator61\Emulator.exe";
        internal const string AllowedLogs = @"D:\HCUP\vg-spec1\logs\";
        internal const string InstanceName = "VgSpec1ManualOffline";
        internal const string HdcPort = "11237";
        internal readonly int Pid;
        internal readonly DateTime StartTimeUtc;
        internal readonly string ExpectedSha256;
        internal readonly string InstanceRoot;
        internal bool GuardOk { get; private set; }
        internal DateTime LastGuardUtc { get; private set; }
        private long checkedLength;
        private DateTime checkedWriteTime;

        internal TargetGuard(int pid, DateTime startUtc, string sha256, string instanceRoot)
        {
            if (pid <= 0) throw new ArgumentException("A positive target PID is required.");
            if (!Regex.IsMatch(sha256, "^[a-f0-9]{64}$")) throw new ArgumentException("Expected SHA256 must be lowercase hex.");
            Pid = pid;
            StartTimeUtc = startUtc;
            ExpectedSha256 = sha256;
            InstanceRoot = RequireLogsDirectory(instanceRoot);
        }

        internal static string RequireLogsDirectory(string directory)
        {
            string path = Path.GetFullPath(directory).TrimEnd(Path.DirectorySeparatorChar);
            if (!path.StartsWith(AllowedLogs, StringComparison.OrdinalIgnoreCase))
                throw new ArgumentException("Directory must be a child of this task's logs directory.");
            if (!Directory.Exists(path)) throw new DirectoryNotFoundException(path);
            RejectReparsePoints(path);
            return path;
        }

        internal static void RejectReparsePoints(string path)
        {
            string current = Path.GetFullPath(path);
            while (!String.IsNullOrEmpty(current))
            {
                if ((File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0)
                    throw new InvalidOperationException("Reparse-point paths are not accepted: " + current);
                current = Path.GetDirectoryName(current);
            }
        }

        internal void Validate(bool hashFile)
        {
            GuardOk = false;
            RejectReparsePoints(AllowedExecutable);
            RequireLogsDirectory(InstanceRoot);
            using (Process target = Process.GetProcessById(Pid))
            {
                if (target.HasExited || target.StartTime.ToUniversalTime().Ticks != StartTimeUtc.Ticks)
                    throw new InvalidOperationException("Target PID exited or its StartTime changed.");
                string actualPath = Path.GetFullPath(target.MainModule.FileName);
                if (!String.Equals(actualPath, AllowedExecutable, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("Target executable path is outside the fixed scope.");
            }
            string query = "SELECT ProcessId,CommandLine FROM Win32_Process WHERE ExecutablePath='" +
                AllowedExecutable.Replace("\\", "\\\\") + "'";
            string commandLine = null;
            int count = 0;
            using (ManagementObjectSearcher searcher = new ManagementObjectSearcher(query))
            using (ManagementObjectCollection matches = searcher.Get())
            {
                foreach (ManagementObject process in matches)
                {
                    using (process)
                    {
                        count++;
                        if (Convert.ToInt32(process["ProcessId"], CultureInfo.InvariantCulture) != Pid)
                            throw new InvalidOperationException("Another process uses the isolated executable path.");
                        commandLine = process["CommandLine"] as string;
                    }
                }
            }
            if (count != 1 || String.IsNullOrEmpty(commandLine))
                throw new InvalidOperationException("Cannot prove exactly one readable process at the isolated path.");
            string[] arguments = ParseCommandLine(commandLine);
            if (!String.Equals(FindArgument(arguments, "-instance"), InstanceName, StringComparison.Ordinal))
                throw new InvalidOperationException("Unexpected emulator instance.");
            if (!String.Equals(FindArgument(arguments, "-hvdport"), HdcPort, StringComparison.Ordinal))
                throw new InvalidOperationException("Expected explicit HDC port 11237.");
            string actualRoot = RequireLogsDirectory(FindArgument(arguments, "-path"));
            if (!String.Equals(actualRoot, InstanceRoot, StringComparison.OrdinalIgnoreCase))
                throw new InvalidOperationException("Instance root differs from the fixed startup scope.");
            FileInfo binary = new FileInfo(AllowedExecutable);
            if (hashFile || binary.Length != checkedLength || binary.LastWriteTimeUtc != checkedWriteTime)
            {
                string actualHash = HashFile(AllowedExecutable);
                if (!String.Equals(actualHash, ExpectedSha256, StringComparison.Ordinal))
                    throw new InvalidOperationException("Target binary SHA256 changed.");
                checkedLength = binary.Length;
                checkedWriteTime = binary.LastWriteTimeUtc;
            }
            GuardOk = true;
            LastGuardUtc = DateTime.UtcNow;
        }

        internal Dictionary<string, object> Snapshot()
        {
            return new Dictionary<string, object> {
                {"path", AllowedExecutable}, {"pid", Pid}, {"startTimeUtc", StartTimeUtc.ToString("o")},
                {"sha256", ExpectedSha256}, {"instance", InstanceName}, {"instanceRoot", InstanceRoot},
                {"hdcPort", HdcPort}, {"guardOk", GuardOk}, {"lastGuardUtc", LastGuardUtc.ToString("o")}
            };
        }

        internal static string HashFile(string path)
        {
            using (SHA256 sha = SHA256.Create())
            using (FileStream file = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
                return BitConverter.ToString(sha.ComputeHash(file)).Replace("-", "").ToLowerInvariant();
        }

        private static string FindArgument(string[] arguments, string key)
        {
            string value = null;
            for (int index = 1; index < arguments.Length; index++)
            {
                string candidate = null;
                if (String.Equals(arguments[index], key, StringComparison.OrdinalIgnoreCase))
                {
                    if (++index >= arguments.Length) throw new ArgumentException("Missing argument value: " + key);
                    candidate = arguments[index];
                }
                else if (arguments[index].StartsWith(key + "=", StringComparison.OrdinalIgnoreCase))
                    candidate = arguments[index].Substring(key.Length + 1);
                if (candidate != null)
                {
                    if (value != null) throw new ArgumentException("Duplicate target argument: " + key);
                    value = candidate;
                }
            }
            if (String.IsNullOrEmpty(value)) throw new ArgumentException("Missing target argument: " + key);
            return value;
        }

        private static string[] ParseCommandLine(string commandLine)
        {
            int count;
            IntPtr pointer = CommandLineToArgvW(commandLine, out count);
            if (pointer == IntPtr.Zero) throw new InvalidOperationException("Cannot parse target command line.");
            try
            {
                string[] result = new string[count];
                for (int index = 0; index < count; index++)
                    result[index] = Marshal.PtrToStringUni(Marshal.ReadIntPtr(pointer, index * IntPtr.Size));
                return result;
            }
            finally { LocalFree(pointer); }
        }
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        [DllImport("shell32.dll", ExactSpelling = true, CharSet = CharSet.Unicode)]
        private static extern IntPtr CommandLineToArgvW(string commandLine, out int count);
        [DefaultDllImportSearchPaths(DllImportSearchPath.System32)]
        [DllImport("kernel32.dll", ExactSpelling = true)]
        private static extern IntPtr LocalFree(IntPtr memory);
    }
}
