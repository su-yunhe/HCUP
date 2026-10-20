# vg-spec1 单题材料交付说明

8类材料已在本目录准备：changes/final.diff、build.md、trace-index.md、sources.fragment.md、solution.fragment.md、submission.json.fragment、traces/、logs/。另附人工操作索引、二进制清单、待补清单、事实出处和audit/工具，以便3-package复核。尚未生成团队级solution/sources/README、system-config汇总、ZIP或对外上传。

差异已在从本题仓库clone的临时目录checkout到`9cbcf7292c8cc46955dc3b522ddbda41c66a61d9`后，先git apply --check --binary，再实际git apply --binary，均退出0。逐项比对交付清单4175文件SHA，0差异/0额外文件/0采集期间变化。diff为571193656字节，SHA256 `0af67292ff56ecb45d8455ecadb0335cc9b3a99f314414002b6650bca12f084d`。保留原始CRLF字节造成apply whitespace警告，原始输出在audit/diff-validation.json，未静默修复内容。

**完整性边界**：本地工程含2GB左右模拟器运行磁盘/缓存及初始化跨题混合会话。官方清单不要求提交运行缓存/无关会话，因此本次明确形成project-manifest交付投影，排除84个此类文件（含6个pyc、14份混合会话原文、64个模拟器运行文件）及本次派生submission-draft目录。所有其余源码、资源、配置、spec、hypium_tests、logs、traces、workflow、system-config、已有其他.comate过程文件都覆盖。没有删除原工程任何文件。**3-package必须按manifest复制project，不能对原目录无过滤递归复制，更不能把含final.diff的draft再嵌入project。** 如果范围改变，必须重新生成并验证diff；不宣称已满足“未经筛选本机目录逐字节全量打包”。

logs为原logs的逐字节副本，排除的只有上述模拟器运行文件/缓存；复制校验见audit/log-copy-manifest.json。所需构建与自测日志齐备，无需为材料再跑构建/设备；官方缺失报告和旧诊断字段不能通过新日志补造。全量日志和原有本题阶段轨迹均保留失败重试。

3-package搬运：build/trace-index/human-changes/changes/logs/pending-fields/auto-filled-facts/delivery-notes/audit/tools放tasks/vg-spec1相应位置；本traces放包根traces/vg-spec1；两个fragment分别汇入根文件，JSON片段合入25题清单；工程仅按project-manifest；validation/为本机临时校验checkout，不进成果包。相对链接在搬运后解释。build.md不依赖本机私有绝对路径；既有自动化脚本含私有路径的限制如实披露。

团队及本题空字段见pending-fields.md。正式成果冻结时间仍【待补充】，当前记录是材料草稿快照。Comate原生资料不存在时已用真实Codex资料说明，未编造双ID/版本。当前活跃材料会话仅采集到traces/sessions.json各自截点，3-package最终冻结时应更新；不得声称当前副本包含未来消息。原生可见副本的内部推理删节、无关检索元数据排除和初始化混合会话排除均有清单；尚未全量敏感信息扫描，本阶段没有对外发送。
