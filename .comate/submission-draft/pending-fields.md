# 仍需补充的字段与记录缺口

下面10个用户输入叶字段原样为空，均保留【待补充】；本阶段不会推测或回写输入。

| 来源 | 字段 | 状态 |
| --- | --- | --- |
| ../common/spec-harness/team.yaml | version | 【待补充】成果包版本 |
| 同上 | contact | 【待补充】联系人及联系方式 |
| 同上 | freeze_time | 【待补充】正式冻结北京时间，精确到分 |
| 同上 | members[0].name | 【待补充】实际成员姓名 |
| 同上 | members[0].work | 【待补充】实际分工 |
| 同上 | source_guard | 【待补充】实际来源保护配置声明 |
| spec/submit-input.yaml | human_edits | 【待补充】不能推断无人工改码；若有，需当时证据 |
| 同上 | known_issues | 【待补充】用户未完成项/已知问题声明，客观未测范围另保留 |
| 同上 | extra_sources | 【待补充】用户额外来源声明；已观察到的来源已自动列出 |
| 同上 | md_export_dir | 【待补充】IDE侧边栏Markdown导出目录；现有为机械阅读副本 |

记录层面的缺口：题包指定 reports/build-baselines/vg-spec14.log 不存在，保留本题 logs/prepare-baseline.log 等替代证据但不冒充原件；脚本确切版本与原执行起止未核实。子会话没有独立IDE侧边栏条目，原生payload.session_id与已保存的主侧边栏索引逐一对应；未提供独立条目不冒充缺失原生记录。Comate sessionUuid和客户端扩展不适用于本题Codex运行器，不能造两个ID。服务端模型内部快照版本未公开，历史JDK/Hvigor精确版本及部分第三方指南原版本【待补充】；当前补跑版本命令不能伪装恢复历史事实。所有已登记本题原生会话已查找，实际缺失列表以 traces/manifest.json 为准。

本题已有构建、安装、启动和必要自测日志，无需为本阶段重新构建/跑设备。缺失历史基线报告不能通过新命令恢复原记录。若以后需要新的复现日志，执行 build.md 的 ohpm install、hvigorw.bat clean assembleHap、hdc安装启动与Hypium命令，并标为新复现证据。

submitted_tasks、attempted_not_submitted、zip_out仅在3-package要求，本阶段不补填、不扩展到其他题。
