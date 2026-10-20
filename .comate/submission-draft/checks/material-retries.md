# Material verification retry history

1. First patch-check attempt failed before delivery: Windows native text checkout used CRLF even with core.autocrlf=false, whereas baseline Git blobs use LF. The original worktree was not modified. Failed temporary clone and full native tool error are retained under checks/work/ and this material session.
2. Corrective action: explicitly configure core.eol=lf as well as core.autocrlf=false in isolated temporary clones, and preserve source bytes when staging. A fresh clone/check is required; failure is never counted as passed.

3. Independent review found that the snapshot identifier used WindowsPath case-insensitive order while the stated canonical algorithm required relative-path string ordering. File contents and patch reconstruction were correct; the identifier declaration was inconsistent. The generator now sorts pure relative-path strings explicitly, and verification independently recomputes the identifier. Final outputs must be regenerated; the earlier e68d identifier is a superseded material checkpoint, not the final version.
