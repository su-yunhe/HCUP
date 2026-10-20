# vg-spec9 来源片段

S-vg9-1：官方随包基线 `metadata.base_commit=a22f32b07bf81c6dde4367e2543ebac29186cbc1`；bundle 标识 `repo_bundles/vignette-a22f32b07b-base.bundle`。仅从本工程 `spec/metadata.json`、`workflow/baseline-provenance.json` 和本地 Git 取证，没有在材料阶段访问题包受限目录或下载来源项目历史。基线资源的路径/字节摘要及同源判断见 `changes/binary-files.json`；原样保留的官方基线二进制不当作额外自制素材。

S-vg9-2：本题 `spec/requirement.md` 与 `inputs/Spec.md`，SHA-256=`c6236994e253c6de9f6decd99d7c0637620027ac16ce3699154796cba7a5edbf`。本题元数据 SHA-256=`496950d171e032fe6f10cf76fd485341f4f293b6f162857d60a46bd98756f660`。

S-vg9-3：只读公共任务书和测试框架；本题保留 `spec-harness/`、`test-harness/`、`system-config/initial-20261016T113216Z/`，任务书版本见 `taskbook-version.md`。Python `hypium==6.1.0.210`、ArkTS `@ohos/hypium=1.0.24`、`@ohos/hamock=1.0.0`，由需求/锁文件与实际环境记录支持。没有新增业务第三方依赖。

S-vg9-4：已安装的 ArkTS 技能及其本地参考文档。实际读取路径和原始返回在本题需求/方案/编码/验证会话中；编码交接明确记录检索索引缺失，改读 Basic-Syntax/functions.md 的 Function Types、classes.md 的 Static Members、error-handling.md 的 finally/async 说明。不能把安装包中的整理文档自动声明为逐条核验过的当前华为官方网页。本次原生工具检索未发现 `web.run` / `web__run` 调用；这只是工具记录观察，不替代用户的完整来源声明。

用户额外来源声明：【待补充】。输入为空，不能写“无额外来源”或断言历史从未访问受保护修复内容。团队实际来源保护措施声明：【待补充】；已观察到的本题 AGENTS/Skill 约束可列为配置证据，不能替代用户对实际措施的确认。

本阶段只提供本题片段，不写根 `sources.md`。
