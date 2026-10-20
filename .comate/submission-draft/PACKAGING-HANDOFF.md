# 单题材料交接与边界

本目录是本地提交草稿，尚未上传、发邮件、创建ZIP或提交Git。团队级文件与最终打包由3-package处理。

技术快照标识：`local-snapshot-20261016T152339Z`；技术捕获时间 `2026-10-16T23:23:39.879380+08:00`。团队正式version/freeze_time等仍【待补充】。

| 本目录内容 | 3-package目标 |
| --- | --- |
| project/ | tasks/vg-spec8/project/（只复制该冻结副本） |
| build.md、trace-index.md、human-changes.md | tasks/vg-spec8/下同名文件 |
| changes/ | tasks/vg-spec8/changes/ |
| traces/、logs/、artifacts/ | tasks/vg-spec8/下同名目录，可保留一份并使用相对引用 |
| sources.fragment.md、solution.fragment.md、submission.json.fragment | 汇入团队根文件，不替代25题完整清单 |
| pending-fields.md、auto-facts.md、validation/的最终JSON/MD | 供人工补全与校验审阅；不复制临时clone/.git/缓存 |

**差异完整性口径**：冻结副本包含本工程所有真实文件、spec、hypium_tests、日志、轨迹、既有system-config以及冻结时的普通.comate材料；不是五文件补丁。仅排除本材料的递归输出子树project/、changes/、validation/，以及.git、已登记缓存/私有环境、明确跨题内容。补丁无法包含自身字节；这些派生输出独立放在project外，排除清单逐项公开。禁止后来把整个submission-draft再塞回project。

工程清单与最终diff/二进制摘要见changes/；validation/apply-check.json记录从本地官方基线clone、checkout、check、真实apply及全文件哈希比较。临时clone禁用文本/过滤器归一化，保留工程物理字节，因而补丁可能包含既有CRLF相对Git blob的字节差异；不代表材料阶段修改业务文件。

共享初始化总览含其他题，原文不提交；本题所有失败/重试保留。根输入中的人工声明与extra_sources未填，不据工具观察擅自作有利认定。构建说明仅使用PATH和包内相对路径；自动化脚本的固定ROOT限制如实披露。

冻结后产生的主会话/独立材料审核记录可能未包含在project快照中；3-package重新收尾导出并新增外置材料记录即可。若变更工程文件集、源码或项目内过程文件，须重做完整diff与apply比较，不得沿用旧校验。当前不是可直接对外提交的最终团队ZIP。
