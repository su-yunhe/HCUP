# 实施交接 01

- 角色 `/root/implementation_do`，CODEX_THREAD_ID `01a158d7-59c4-7df2-95f7-995b90d6bbee`；唯一生产源码写者，未操作设备或测试文件。首次改码前确认 `logs/prepare-baseline-exit-code.txt=0`、HEAD `75fd0066a7fc0c1e8cedb6218df081f86d307f45`。仅本题基线与指定输入，未读其他题或上游实现。
- 实施批准方案01：登录页120 Logo、精确双按钮与四条既有路由、等宽三方图标/标签、三方缺配置反馈、独立主题色协议链接、可滚动底部文案；窗口断点100%/70%/60%，`auth_login_content`为无业务横padding的安全区内分母；Main/Me真实id与局部去重；两目标页身份；两份原创本地长正文。三图标复制本题core/ui基线，使用专用资源名。
- 修改14个生产文件：auth的LoginPage/LoginViewModel、SmsLoginPage、AccountLoginPage、base string资源、三个ic_login_*.svg；main的MainPage/MePage/MeViewModel；common两协议页和base string资源。逐文件SHA256与聚合值见 `source-fingerprint-01.json`。
- 对应 A1–A15、B1–B8、B12–B19、C1–C7 的实现路径已具备；这不是独立验收通过结论。B9–B11仅完成入口/反馈/恢复，真实三方授权仍缺平台身份及后端契约，见 `third-party-setup.md`。
- 原创正文：`feature/common/src/main/resources/base/element/string.json` 的 `local_user_agreement_body`/`local_privacy_policy_body`，本地1.0/2026-10-20。依据本题EntryAbility/权限声明、NetworkClient、UserState/AccountStore与本轮未调用认证事实；不声称上游官方文本，不虚构主体、联系信息或已集成SDK。由需求角色独立复核。

检查：两份JSON解析、`git diff --check`均通过。构建先加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`，运行用户命令 `hvigorw assembleHap --mode module -p product=default -p buildMode=debug --no-daemon`；首次成功，exit0，23s20ms。完整输出 `logs/implementation/build-01.log` 与退出码文件。HAP `entry/build/default/outputs/default/entry-default-unsigned.hap` SHA256 `fda27f350d9fe1f54ac3b8ba48b8ef35168ccfcd75ffacee7b5a7ded4730a849`。无BuildProfile等tracked构建噪声。

告警比较 `logs/implementation/warning-diff-01.json`：本次增量构建发出185条ArkTS位置/消息，均在完整基线207条清单中；资源冲突170次与基线相同。未出现新增位置/消息，不把增量未发出的22条当作已消除。14文件聚合源码SHA256为 `d27a5af240231e94f25502c78cc337bb462f925c509d5c164002bc973236d84d`。

没有执行独立安装、Hypium或视觉/几何验收；生产代码现已冻结，交验证角色安装上述产物验证真实入口、id、页脚、38项路径、三类实际窗口及返回/连点。无真实请求，不添加网络loading或认证/存储调用。没有新增依赖。

技术参考：读取三项指定ArkTS技能，本地官方迁移参考 `arkts-syntax-assistant/references/en/typescript-to-arkts-migration-guide.md`；knowledge-retriever脚本因缺 `references/doc_index.json`失败，改读已打包linter摘要（不是官方规范全文）和本题现用模式，未宣称轻量lint通过。实际编译由上述hvigor执行。
