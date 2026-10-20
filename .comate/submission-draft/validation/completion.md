# vg-spec7 材料阶段最终校验

2-submit 单题草稿已完成，保留 README 中全部待补人工字段与记录缺口。本次未创建团队级文件／ZIP，未上传、发送或正式提交。

- 最终基线：`9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`。
- 最终工程投影：1338 文件，119499065 字节；Git tree `ed70854c4864be4d33258d9a69e13e464af7b91e`。
- final.diff：127000663 字节，SHA-256 `8b071d1ca8833f47f1d6edf1555e0876d5869cb967a20b279456d8b19b0c2666`。
- 实测：从本题本地 Git clone，checkout 官方基线，apply --check --binary、实际 apply 均退出 0；全 1338 文件 SHA 一致，0 missing、0 extra、0 hash mismatch。命令与完整 stdout/stderr 在 diff-validation.json。
- 原构建的 256 个源码／资源／配置指纹全部一致；tracked git diff --check 退出0。详见 final-production-integrity.json。
- 83 个二进制，8 个与官方基线同 blob；完整清单在 changes/binary-files.json/md，实际内容在工程投影／binary patch。
- 原生会话 15 个；工作区维度 15 个，题号索引维度 3 个；已登记本题会话无缺失。33 份日志按原字节保留。
- 原生导出截点 `2026-10-17T04:49:32.250780+00:00`；不是团队正式冻结时间。活动材料主会话在此之后的最终生成／校验／回复不在该截点快照内，后续打包须再次导出该尾部；不能以其替代原研发证据。
- 独立四角色复审已完成。independent-review.md 对前冻结1,335文件版独立核验；末次state/native刷新与三份输入副本纳入本最终1,338文件版，由主 Agent再次实际重建／比对，不把旧版独立SHA当新版SHA。
- 初始parser失败、换行校验失败、旧manifest提前校验失败及成功前冻结报告均保留在本validation目录和原生记录。未覆盖历史失败来制造成功。

project按changes/project-snapshot.json.files精确拷贝；patch、它的manifest／binary摘要和validation在project外任务材料层保留，scratch及明确跨题初始化原文不打包。若补字段、变更稳定文件或刷新native，应重新snapshot/verify，不能沿用本报告。
