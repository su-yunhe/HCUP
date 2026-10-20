using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Text;
using System.Web.Script.Serialization;

namespace VgSpec1.NetworkIsolation
{
    internal sealed class ControlRequest
    {
        internal long Sequence;
        internal string Operation;
        internal DateTime CreatedUtc;
        internal DateTime ExpiresUtc;
    }

    internal sealed class RunFiles : IDisposable
    {
        private readonly string directory;
        private readonly string nonce;
        private readonly FileStream runLock;
        private readonly StreamWriter logWriter;
        private readonly JavaScriptSerializer serializer = new JavaScriptSerializer { MaxJsonLength = 65536, RecursionLimit = 16 };
        private string lastReadText;

        internal RunFiles(string runDirectory, string runNonce)
        {
            directory = TargetGuard.RequireLogsDirectory(runDirectory);
            nonce = runNonce;
            if (File.Exists(Path.Combine(directory, "status.json")))
                throw new InvalidOperationException("A fresh run directory without status.json is required.");
            runLock = new FileStream(Path.Combine(directory, "helper.lock"), FileMode.CreateNew, FileAccess.Write, FileShare.Read);
            logWriter = new StreamWriter(new FileStream(Path.Combine(directory, "helper.jsonl"), FileMode.CreateNew,
                FileAccess.Write, FileShare.Read), new UTF8Encoding(false));
            logWriter.AutoFlush = true;
        }

        internal void Log(string eventName, Dictionary<string, object> fields)
        {
            lock (serializer)
            {
                fields["event"] = eventName;
                fields["timestampUtc"] = DateTime.UtcNow.ToString("o");
                fields["nonce"] = nonce;
                string text = serializer.Serialize(fields);
                logWriter.WriteLine(text);
                Console.WriteLine(text);
            }
        }

        internal void WriteStatus(Dictionary<string, object> status)
        {
            TargetGuard.RequireLogsDirectory(directory);
            string path = Path.Combine(directory, "status.json");
            if (File.Exists(path)) TargetGuard.RejectReparsePoints(path);
            string temporary = Path.Combine(directory, "status." + Guid.NewGuid().ToString("N") + ".tmp");
            string text;
            lock (serializer) { text = serializer.Serialize(status); }
            try
            {
                File.WriteAllText(temporary, text, new UTF8Encoding(false));
                if (File.Exists(path)) File.Replace(temporary, path, null);
                else File.Move(temporary, path);
            }
            finally { if (File.Exists(temporary)) File.Delete(temporary); }
        }

        internal ControlRequest ReadRequest(long lastSequence)
        {
            string path = Path.Combine(directory, "request.json");
            if (!File.Exists(path)) return null;
            TargetGuard.RejectReparsePoints(path);
            FileInfo info = new FileInfo(path);
            if (info.Length > 4096) throw new InvalidOperationException("Control request exceeds 4096 bytes.");
            string text;
            using (FileStream stream = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete))
            using (StreamReader reader = new StreamReader(stream, new UTF8Encoding(false, true), true))
            {
                char[] buffer = new char[4097];
                int length = reader.ReadBlock(buffer, 0, buffer.Length);
                if (length > 4096) throw new InvalidOperationException("Oversized control request.");
                text = new string(buffer, 0, length);
            }
            if (text == lastReadText) return null; // An old file never extends the lease.
            lastReadText = text;
            try
            {
                Dictionary<string, object> fields = serializer.DeserializeObject(text) as Dictionary<string, object>;
                string[] required = { "nonce", "sequence", "operation", "createdUtc", "expiresUtc" };
                if (fields == null || fields.Count != required.Length) throw new ArgumentException("Unexpected control schema.");
                foreach (string key in required) if (!fields.ContainsKey(key)) throw new ArgumentException("Missing field: " + key);
                if (!String.Equals(fields["nonce"] as string, nonce, StringComparison.Ordinal))
                    throw new ArgumentException("Wrong run nonce.");
                object sequenceObject = fields["sequence"];
                if (!(sequenceObject is int) && !(sequenceObject is long)) throw new ArgumentException("Sequence must be an integer.");
                long sequence = Convert.ToInt64(sequenceObject, CultureInfo.InvariantCulture);
                if (sequence <= lastSequence) throw new ArgumentException("Stale/non-increasing sequence.");
                string operation = fields["operation"] as string;
                if (operation != "block" && operation != "unblock" && operation != "exit")
                    throw new ArgumentException("Operation must be block, unblock or exit.");
                DateTime created = ParseUtc(fields["createdUtc"] as string);
                DateTime expires = ParseUtc(fields["expiresUtc"] as string);
                DateTime now = DateTime.UtcNow;
                if (created > now.AddSeconds(2) || created < now.AddSeconds(-15) || expires <= now ||
                    expires <= created || expires > created.AddSeconds(15))
                    throw new ArgumentException("Expired, future or overlong control lease.");
                return new ControlRequest { Sequence = sequence, Operation = operation, CreatedUtc = created, ExpiresUtc = expires };
            }
            catch (Exception error)
            {
                Log("request_rejected", WfpSession.Fields("reason", error.Message));
                return null;
            }
        }

        internal static DateTime ParseUtc(string text)
        {
            DateTimeOffset parsed;
            if (String.IsNullOrEmpty(text) || (!text.EndsWith("Z", StringComparison.OrdinalIgnoreCase) &&
                !text.EndsWith("+00:00", StringComparison.Ordinal)) ||
                !DateTimeOffset.TryParse(text, CultureInfo.InvariantCulture, DateTimeStyles.None, out parsed) ||
                parsed.Offset != TimeSpan.Zero) throw new ArgumentException("An ISO8601 UTC timestamp is required.");
            return parsed.UtcDateTime;
        }

        public void Dispose()
        {
            logWriter.Dispose();
            runLock.Dispose();
        }
    }
}
