# common

所有赛题共用的资源，属于 `main` 分支，跟着 `common/scripts/sync.sh` 同步。

- `scripts/`：工作区管理脚本，用法见根目录 README。
- 其他：文档、prompt、AGENTS 模板、检查脚本、测试数据等，按需新建子目录。

使用约定：

- 不要把这里的文件提交进任何赛题分支，否则会混进该题的补丁。
- 赛题里需要用到时，优先用相对路径 `../common/xxx` 引用。
- 必须出现在赛题目录里的（比如构建时要读的配置），用软链接，并加到本地排除列表，不提交：

  ```bash
  cd jm-spec7
  ln -s ../common/xxx xxx
  echo "/xxx" >> "$(git rev-parse --git-common-dir)/info/exclude"
  ```

  队友环境下所有 worktree 共用一个 exclude 文件，写一次即可。

## 已有内容

| 目录 | 用途 |
| --- | --- |
| `scripts/` | 工作区管理脚本，用法见根目录 README |
| `spec-harness/` | 通用四阶段任务书（分析 / 开发 / 单题材料 / 阶段打包）与团队级信息 `team.yaml`，见其 `README.md` |
| `test-harness/` | Hypium 自测框架，各题 `hypium_tests/` 继承其 `HarnessTestCase`，见其 `README.md` |
| `skills/` | HarmonyOS / ArkTS 相关 Agent Skills（3 个），安装方式、来源与许可说明见其 `README.md` |
| `.venv/` | 自测用 Python 3.13 环境，已装 `hypium==6.1.0.210`；本机生成，已在 `common/.gitignore` 中排除，不进仓库 |

各赛题 Agent 对本目录**只读**，不得修改；本目录**不得放入任何题目专属内容**（某题的分析、代码、会话信息等），
否则会通过任务书把一道题的信息带进另一道题的 Agent。
