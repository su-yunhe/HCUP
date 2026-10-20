# cml-spec7 / 自测角色 / 基线第 1 轮

范围：仅分析阶段，独立构建、安装、启动并操作未修改的当前基线，记录真实证据，不实现或修复业务代码。执行原生 harmony_verification 角色，不派生子 Agent，不读其他题目录、题包、上游实现/历史、初始化总览会话。允许本题 `D:/HCUP/cml-spec7` 和 `D:/HCUP/common` 只读公共资源。你不是唯一在工作的 Agent，不撤销他人改动。

输入版本：HEAD `75fd0066a7fc0c1e8cedb6218df081f86d307f45`；Spec `spec/requirement.md` SHA256 `d4600d3b744f8d5cd11d2c5e09e2148798a439b5206c03ffbf3c8c70a411fed9`。需求矩阵尚在拆分，不要把基线表现当作规范。

每个构建/设备命令的 PowerShell 进程先加载 `D:/HCUP/.hcup-local/Enter-HarmonyEnv.ps1`。使用构建技能 `C:/Users/22580/.codex/skills/hmos-arkts-syntax-checker/SKILL.md` 的检查流程，但禁止自动修复源码。本题已准备工具链和依赖，根目录就是工程，不创建 project 子目录。读取本题 `test-harness/README.md` 以及必要 harness API，优先用本地 Hypium、hdc 验证。模拟器操作由你独占，先确认设备及当前前台应用；若明显有其他题正在运行，先回报主 Agent 协调，不抢占。不得访问其他题工程。

可写范围：`workflow/verification/`、`logs/analysis-baseline/`、`traces/analysis-baseline/` 内的脚本、报告、日志、截图；构建工具自动生成输出需记录。不写生产代码、spec、全局 workflow/state/events。首尾核对 tracked 文件和参与构建的新文件指纹。不要更改签名配置或绕过校验；安装失败先留证据再调查可逆环境手段。

需要独立重跑基线构建并完整收集警告；记录命令、退出码、HAP 哈希、环境/设备、安装和启动结果。若成功，实际按首页→我的→登录操作，观察目标页、手机号/账号密码入口、第三方图标、微信点击和协议/隐私入口，可行时返回重进及重启重进。以证据标注 pass/fail/blocked/not_run，不冒充隐藏测试；手机/平板/更宽尺寸如未实测必须明确未验证。保留页面树或截图及原始日志。遇登录、凭证或第三方缺失可如实阻断，继续可完成的本地项。

产出 `workflow/verification/baseline-evidence-01.md`，用于主 Agent 编制 `spec/baseline-notes.md`。必须先尝试构建安装操作后再形成结论。返回路径、阻断、真实观测与下一步，并提供原生会话 UUID（如可获得）。
