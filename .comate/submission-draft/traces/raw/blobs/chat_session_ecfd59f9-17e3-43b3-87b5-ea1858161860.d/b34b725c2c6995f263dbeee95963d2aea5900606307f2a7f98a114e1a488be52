---
name: cmu-spec1 local build/test environment
description: How to build/run cmu-spec1 on this Mac (toolchain env vars, emulator serial, local NeteaseCloudMusicApi docker) — check before building or self-testing
type: reference
---

- Toolchain is not on PATH. hvigorw needs JAVA_HOME=/Applications/DevEco-Studio.app/Contents/jbr/Contents/Home (else "Unable to locate a Java Runtime" at packaging) and DEVECO_SDK_HOME=/Applications/DevEco-Studio.app/Contents/sdk; hdc lives in sdk/default/openharmony/toolchains. Full commands recorded in spec/baseline-notes.md section 2.
- Emulator serial 127.0.0.1:5555 (API 23, aarch64, matches official spec). Unsigned HAP installs fine.
- Local compatible API server: docker container `netease_cloud_music_api` on host port 3000; emulator reaches it at http://10.0.2.2:3000. `docker logs netease_cloud_music_api` shows every request path — use it to verify real network calls.
- Device has no audio files by default; push test mp3 to /storage/media/100/local/files/Docs/Download/ via `hdc file send`.
- Do not pipe hvigorw through `| head` — SIGPIPE kills the build mid-way; redirect to a log file instead.
