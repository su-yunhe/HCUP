# common/skills：HarmonyOS / ArkTS 相关 Agent Skills

从本机全局目录 `~/.agents/skills/` 整理而来，共 3 个，用于团队内共享。内容是通用参考，不含任何题目专属信息。
整理时去掉了 `node_modules/` 和 `linter-cache/`（机器相关、可再生，约 45MB），已写入 `common/.gitignore`。

## 清单

| Skill | 用途 | 上游 | 许可 |
| --- | --- | --- | --- |
| `arkts-syntax-assistant` | ArkTS 语法、TS 迁移、性能优化、编译错误、状态管理参考 | [summerkaze/skill-arkts-syntax-assistant](https://github.com/summerkaze/skill-arkts-syntax-assistant) | MIT，见目录内 `LICENSE.txt` |
| `hmos-arkts-knowledge-retriever` | 基于本地 ArkTS 语言指南 / API 参考 / linter 规则库做检索，自带轻量 lint 工具 `linter-cli/` | [iskenkenya/skills](https://github.com/iskenkenya/skills)（转载） | 未声明，见下 |
| `hmos-arkts-syntax-checker` | ArkTS 语法检查、自动修复，循环构建到成功 | [weikangzeng07-ops/dsh-hmos-skills](https://github.com/weikangzeng07-ops/dsh-hmos-skills)（转载） | 未声明，见下 |

## 安装

重启 Agent（Comate）后才会加载新 skill。

方式一：从本目录复制，适合团队内。

```bash
mkdir -p ~/.agents/skills
cp -R common/skills/arkts-syntax-assistant \
      common/skills/hmos-arkts-knowledge-retriever \
      common/skills/hmos-arkts-syntax-checker \
      ~/.agents/skills/
```

方式二：从上游安装，需要 Node.js，适合对团队外分享。以下命令是整理者实际用过的：

```bash
npx skills add summerkaze/skill-arkts-syntax-assistant@arkts-syntax-assistant -g -y -a universal
npx skills add iskenkenya/skills@hmos-arkts-knowledge-retriever -g -y -a universal
npx skills add weikangzeng07-ops/dsh-hmos-skills@hmos-arkts-syntax-checker -g -y -a universal
```

## 使用前提

- `hmos-arkts-syntax-checker`：需要本机有 DevEco Studio，设置 `DEVECO_SDK_HOME`，工程根目录有 `hvigorw`（上游 README 的说明）。
- `hmos-arkts-knowledge-retriever`：
  - `docs/` 是 Markdown / ets 文档，检索由 `scripts/search_docs.py` 完成，不需要 Node。
  - `linter-cli/` 需要先装依赖（见该 skill 的 `SKILL.md` 和 `linter-cli/README.md`）：
    `cd linter-cli && npm install && npm run install-runtime-deps`。后一步会从 gitcode 克隆 OpenHarmony 定制的 TypeScript，需要联网。
  - `linter-cli/package.json` 声明了 `cpu: x64`。在 Apple Silicon 上能否运行，**整理者没有验证过**。

## 来源与许可

- `arkts-syntax-assistant`：MIT。
- 两个 `hmos-*` skill 本质上是华为 / OpenHarmony 社区官方 skill 的第三方转载。`dsh-hmos-skills` 的 README 写明
  “Copyright remains with the original authors”，其 MIT 许可只覆盖该仓库自己的插件代码，不覆盖 skill 内容；
  `iskenkenya/skills` 的授权说明我没能查到。因此这两个 skill 的再分发授权**不明确**。
  团队内部使用问题不大；向团队外分享时，建议只发上面的“方式二”安装命令，不要直接转发这里的文件。

## 状态

整理者尚未在任何赛题工作中实际调用过这三个 skill，效果未评估。
