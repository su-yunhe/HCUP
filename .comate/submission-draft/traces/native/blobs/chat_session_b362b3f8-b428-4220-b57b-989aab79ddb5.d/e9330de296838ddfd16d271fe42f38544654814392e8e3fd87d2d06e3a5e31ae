---
name: Local build/device environment for cml-combo-search
description: Non-obvious CLI build prerequisites and emulator quirks on this Mac for the HarmonyOS cml-combo-search task
type: reference
---

- CLI `hvigorw` build fails at PackageHap ("Unable to locate a Java Runtime") unless `JAVA_HOME=/Applications/DevEco-Studio.app/Contents/jbr/Contents/Home`; also set `DEVECO_SDK_HOME=$D/sdk` and add `$D/tools/{hvigor,node,ohpm}/bin` + `$D/sdk/default/openharmony/toolchains` (hdc) to PATH. None are on PATH by default.
- Emulator `127.0.0.1:5555` is arm64-v8a (matches official spec per harness env_check), so the payment-SDK x86_64 install issue from the contest FAQ does not apply; unsigned HAP installs fine.
- Emulator DNS (114.114.114.114 / 8.8.8.8) is flaky on this network: first app launch may show "网络连接失败"; retry/relaunch before judging network-dependent tests. Observed 2026-10-20: emulator ping RTT ~30 s while host curl was fine.
- Hypium `start_app("com.joker.coolmall")` fails ("Fail to get main ability"); must pass ability `"EntryAbility"` explicitly. The common harness `restart_app` helper therefore doesn't work for this bundle.
- Keyboard visibility can be checked via `hidumper -s WindowManagerService -a '-a'`: a `softKeyboard*` row appears in the visible-window section only while the IME is shown.

**How to apply:** use these env vars for every build/self-test run in later stages (1-do / 2-submit); precheck home page loads before running network-dependent Hypium cases.
