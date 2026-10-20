# 冻结工程与完整差异范围

官方基线为本题metadata中的`9a1d608dc89acfc301657c33ce5dd6089cbf9572`。选入范围是当前Git tracked文件、正常untracked文件和显式保存的AGENTS.md，涵盖业务及所有本题过程目录，不能只交业务补丁。

## 明确排除

1. `.git`、oh_modules、node_modules、build、.hvigor、__pycache__、虚拟环境及同类可再生缓存；构建生成BuildProfile等噪声。不排除必要manifest/lock或第三方许可。
2. `traces/analysis/baseline-runtime/emulator-instances/`中的运行中模拟器磁盘/缓存，不作为代码或测试结果提交。
3. SQLite的空`-wal`、`-shm`和临时journal sidecar。非空WAL可能含提交pages，保留为对应主DB的成套静态原始证据，不丢弃或checkpoint原件；复制前后须核hash/mtime稳定，在validation专用副本上作完整性检查。主DB及安全备份继续保留，原服务停止/完整性证据见本题cleanup。若静态性或一致性失败须停止校验，不提交仍写入的临时数据库。
4. 文件名包含`01a13fc4-2611-7761-a580-1283e0c70541`的两份旧初始化总览raw。只按名字识别、未读正文；它们包含混合准备范围，不作为本题实现参考或私有会话提交。本题16个去重相关会话完整导出保留。旧archive manifest可继续引用被排除的历史源名，排除原因以本清单为准。
5. `.comate/submission-draft/validation/`全部派生验证/临时clone；`changes/final.diff`、`changes/project-files.json`、`changes/excluded-files.json`的自引用输出；以及`traces/materials-final/`末次材料事件导出。这些仍是草案材料的一部分，但位于完整工程冻结范围之外，防止补丁包含自身、校验副本递归或导出自身。

`changes/excluded-files.json`列出本次实际排除文件及理由，`changes/project-files.json`列出全部选入文件字节摘要。二进制摘要在binary-manifest；原有截图、受控HAP备份、稳定SQLite、失败日志及本题原生记录保留，不以它们较大为由删减。

## canonical project与后续流程

本题现场是linked worktree，共享Git管理员目录不作为直接读取范围。原工程保护使用本题`git ls-files --stage -z`逻辑内容SHA与HEAD前后比对，不冒称物理index文件逐字节核验。首轮工具因边界保护在读取该目录前停止，失败原件保留。

在validation/patch-01下按实际UTC运行目录分别clone官方基线到generator和reconstructed-project，只从本地本题分支取对象，不访问应用上游。使用`--no-local --single-branch --branch cml-spec28 --depth 2 --no-tags --no-checkout`，禁用会复制共享objects的local优化；源与clone均核仅本题两个已知提交（准备HEAD b75aa21f…与官方base9a1d608d…），不枚举其他题历史。随后checkout指定base。生成器复制选入文件、处理删除，以临时index生成`--binary --full-index`补丁；另一clone先`git apply --check --binary`再实际apply，逐一比对所有非.git文件的数量与SHA-256。实际路径、命令、退出码、补丁摘要和结果在validation/patch-01/result.json及其引用输出；没有结果时不能把本说明当校验已通过。

canonical完整工程是验证后的reconstructed-project去掉其.git，严格以manifest为边界。材料冻结后的活跃workflow状态、事件、末次native导出不反写这个快照；由外部validation/trace材料记录。后续3-package拷贝canonical工程与本题材料到materials-layout约定位置，不能把增长后的现场工程与旧diff配对。

团队正式freeze_time仍为【待补充】。本次工具捕获时间是技术快照时点，不替代团队成果冻结声明。存在上述明确范围例外，不能宣称final.diff逐字节包含它自身或验证它的临时工程。
