# harmonycup-work

一个仓库管理全部赛题基线：`main` 分支放公共资源和脚本，每道题一个同名分支，以 git worktree 的形式检出到根目录下的同名目录。所有基线同时可见、可同时编译，不需要来回 checkout。

```
harmonycup-work/          ← main：公共资源 + 脚本
├── README.md
├── common/               ← 公共资源，见 common/README.md
├── scripts/              ← 工作区管理脚本
├── cm-spec26/            ← 分支 cm-spec26（worktree）
├── jm-spec7/             ← 分支 jm-spec7（worktree）
└── ...
```

每个基线分支保留原始提交历史，并有一个 tag `base/<名称>` 指向该题的原始基线 commit。

## 首次加入

```bash
git clone -b main <团队仓库地址> harmonycup-work
cd harmonycup-work
scripts/setup.sh          # 为每个基线分支建 worktree
scripts/status.sh         # 确认所有基线都在
```

## 日常协作

1. 开工前先同步：`scripts/sync.sh`
2. 在某道题的目录里改代码，在**该目录内**提交：

   ```bash
   cd jm-spec7
   git add <文件> && git commit -m "jm-spec7: 修复xxx"
   ```

3. 改公共资源（`common/`、`scripts/`、本 README）时，在**根目录**提交到 main。
4. 收工或需要队友看到时：`scripts/sync.sh`，只同步某几题用 `scripts/sync.sh jm-spec7 vg-spec1`。

`sync.sh` 对每个目录执行 `pull --rebase` 再 `push`，有未提交改动的目录会被跳过并在最后列出。远端新增的基线会自动建 worktree。

## 协作约定

- **一题一负责人**。同一道题尽量只有一个人改，需要多人时先沟通，减少 rebase 冲突。
- **先 commit 再 sync**。不要把半成品长时间留在工作区不提交。
- **不要 force push、不要改写已推送的历史**（`commit --amend`、`rebase -i` 只用于未推送的提交）。
- **基线分支只放该题的代码**。公共资源放 `common/`，引用方式见 `common/README.md`。
- 提交信息以题目名开头，例如 `vg-spec13: 调整列表刷新逻辑`。
- `oh_modules/`、`build/`、`.hvigor/` 等构建产物已在各基线的 `.gitignore` 中忽略，不要强行提交。

## 冲突处理

`sync.sh` 报某个目录 rebase 冲突时：

```bash
cd jm-spec7
git status                 # 查看冲突文件
# 手动解决后
git add <文件> && git rebase --continue
cd .. && scripts/sync.sh jm-spec7
```

想放弃本次 rebase 回到同步前的状态：`git rebase --abort`。

## 查看改动与生成补丁

```bash
scripts/status.sh                                   # 所有基线的分支、未提交数、领先/落后、base 之后的提交数
git -C jm-spec7 diff base/jm-spec7                  # 相对原始基线的全部改动（含未提交）
git -C jm-spec7 diff base/jm-spec7 HEAD > jm-spec7.patch   # 只含已提交的改动
```

## 脚本一览

- `scripts/setup.sh`：为远端每个基线分支建 worktree，只补缺失的，可重复执行。
- `scripts/sync.sh [基线名...]`：同步 main 和基线，不带参数时同步全部。
- `scripts/status.sh`：本地状态一览，不访问网络。
- `scripts/publish.sh <团队仓库地址> [基线名...]`：仅维护者使用，把本地独立的基线仓库发布到团队远端。

## 维护者：新增一道题

维护者本地的基线是独立仓库（`origin` 指向原始 bundle，团队远端叫 `team`），其他人的是 worktree，两种形态脚本都支持。

```bash
git clone <xxx-<commit>-base.bundle> new-spec     # 在根目录下
scripts/publish.sh <团队仓库地址> new-spec         # 推分支并打 base/new-spec tag
```

队友下次运行 `scripts/sync.sh` 时会自动拿到 `new-spec`。
