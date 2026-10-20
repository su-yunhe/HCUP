# cml-spec7 材料草案交接

这是2-submit单题材料草案，不是正式成果包。功能本地验收为38pass/3blocked（B9–B11），未全完成；原始失败/重试和限制未删除，完整事实见 `solution.fragment.md`。team未选择submitted题目，当前JSON保守not_completed；三个非空路径仅为3-package拟定映射。

## 文件与后续映射

| 当前草案相对路径 | 3-package拟定包内路径/用途 |
| --- | --- |
| `traces/code-snapshot/project/` | `tasks/cml-spec7/project/`，精确复制这一文件树 |
| `build.md` / `trace-index.md` / `human-changes.md` | `tasks/cml-spec7/`下同名文件 |
| `changes/`、`traces/`、`logs/`及取证JSON | 本题材料目录内保留相对关联；原生文件只保留本题 |
| `sources.fragment.md` / `solution.fragment.md` | 3-package汇总到团队根sources/solution；当前不改团队根文件 |
| `submission.json.fragment` | 仅本题task对象，合并团队总任务清单，最终status由真实提交选择决定 |
| `missing-fields.md` / `auto-filled-facts.md` | 人工待补与自动事实两份清单 |

`.comate/submission-draft/`是材料派生输出，不能再整个塞回project。否则final.diff包含自身、代码快照再包含快照，无法有限冻结。除了该输出及逐项识别缓存，实际Spec、inputs、Hypium、workflow、系统配置副本、原始记录等仍按 `project-manifest.json` 清单交付。`project-exclusions.json`列明缓存/生成磁盘排除，不删除原文件；`logs-copy-manifest.json`逐项保存日志副本hash和排除原因。项目/补丁输出本身位于清单外，避免摘要包含自身。

## 版本与补丁核对

官方基线 `75fd0066a7fc0c1e8cedb6218df081f86d307f45`。完整交付版本/文件数量/哈希、snapshot git tree与本次快照时刻取 `project-manifest.json`；快照时刻明确不是团队正式freeze_time。源码完整生产输入SHA为 `26307326248e8e874d1e2d8c3a4abf10e14008d5fd386b91682357a928f6f78e`；历史HAP为 `17068002` bytes、SHA256 `8aaa5de48b5664b92210fad7ffcddf9abbcebbb92e52faf7f5359bbeb3611863`。Git HEAD仍停在基线，不能只用普通git diff漏掉未跟踪材料。

主调度负责生成 `changes/final.diff`（`--binary`、新增/修改/删除全量），并保留临时基线clone的原始命令、输出和校验记录；先 `git apply --check --binary` 后真实apply，每个交付文件SHA、额外文件与删除项、生产漂移和BuildProfile噪声均在 `patch-validation.json`。**当前读取的校验状态：已通过；完整命令、退出码、逐文件比较与当前摘要见 `patch-validation.json`（`passed=true`）。** 不以diff语法通过代替完整应用/全树一致性。临时 `.validation-work/`、`validation/independent-baseline/` 当前均在本地保留，按 `assembly-plan.json` 及最终 `artifact-manifest.json` 的排除规则不随包。主调度安全清理 `.validation-work/` 的操作被自动审批以 `blocked by policy` 拒绝，未执行，也未换机制删除；原始拒绝记录见 `temporary-clone-cleanup-rejected.json`。该拒绝不改变已完成的补丁应用和逐文件校验结果，不以临时clone目录代替原始校验记录。

当前快照树不含构建依赖缓存或HAP编译产物；`facts.json`保存历史验证HAP摘要，使用 `build.md`从完整工程重建。二进制与资源单列 `changes/binary-files.json`、`changes/resource-files.json`；每项路径、bytes、SHA及基线同源关系可查，文本SVG也在diff与资源清单内。最终以真实生成清单为准，不在正文硬编码会持续变化的数量。

## 原生记录、失败和缺口

会话选择由工程路径与题号两维核对，真实ID、父子关系、源路径、导出hash/bytes、模型与累计token口径见 `traces/session-metadata.json`；`traces/discovery.json` / `native-discovery-search.json`记录过滤过程。`traces/native/*.jsonl`为可独立读取的原生副本；`traces/markdown/*.md`是机械副本，不是IDE导出。导出截止后的事件和3-package活动须后续收录，不用当前材料快照冒充未来完整轨迹。混含其他题的初始化总览排除，不作为本题功能证据。

官方本题基线报告缺失，本地prepare log与setup登记如实分别引用；初始化hdc stdout捕获缺口、手机原轮测试error及定向补测、800vp旧轮/1200vp新轮、02b失效、清理拒绝均保留。详见 `trace-index.md`、`missing-fields.md`。本阶段没有补跑命令来冒充历史原始输出。

## 仍需人工补充与正式打包条件

见 `missing-fields.md`：human_edits、known_issues、extra_sources、md_export_dir，以及团队version/contact/freeze_time/members/source_guard均为 **【待补充】**。已自动取事实与出处独列 `auto-filled-facts.md`。不能根据空字段写“无人工修改/无额外来源”，不能把材料时间代填正式冻结时间。

主调度还需将最终材料会话刷新进原生切片，重跑本文档生成器以同步机器元数据和补丁状态，并由独立验证角色核对官方逐字段、路径/文件存在、完整patch/快照与便携说明。正式3-package在真实冻结/选择后再生成团队根文件及ZIP。本角色仅撰写被授权文档，无业务、资源、配置或测试改动。

## 补充取证位置与字节范围

原始人工输入与官方逐字段模板的包内只读副本为 `evidence-inputs/team.yaml`、`evidence-inputs/submit-input.yaml`、`evidence-inputs/templates/`。本材料阶段实际读取的工作流Skill及四角色配置副本/hash在 `evidence-inputs/current-config/manifest.json`；它是本题材料附件，不改团队根system-config。原始公共输入路径用于来源说明，离线核对可直接读取这些随包副本。

`changes/line-ending-only.json`另列既有Windows CRLF与基线LF造成的纯行尾差异；这些既有字节差异纳入exact-bytes补丁，但不计为本材料阶段业务改动。主调度在临时基线clone中设置 `core.autocrlf=false`，以清单内真实字节生成和应用补丁，不改原工程行尾。文件数、清单hash与比较结果以最终机器JSON为准。

本材料阶段沿用同一生产源码的历史构建/设备结论：`current-production-fingerprint.json`与最终03验收完整生产输入SHA一致，没有通过重跑构建制造新证据；根调度的 `git diff --check` 退出0，记录见本次原生会话及材料验证报告。
