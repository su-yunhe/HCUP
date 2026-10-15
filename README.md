# harmonycup-work

2026 AI 辅助研发创新大赛（鸿蒙杯）团队工作区。一个仓库 26 个分支：

- `main`：公共资源，即根目录本身（README、`common/`）。
- 25 个赛题分支：每道题一个，分支名就是题目 ID，以 git worktree 的形式检出到根目录下的同名目录。

所有题目同时可见、可同时编译，不需要来回 checkout。题目需求（Spec）、元数据和官方工具在赛题包 [SWE-OpenHarmony](https://gitcode.com/SMAT/SWE-OpenHarmony) 里，不在本仓库。

**路径约定**：赛题包放在与本仓库同级的 `SWE-OpenHarmony/`。任务书、测试和文档里一律用相对路径：在题目目录里，公共资源是 `../common/`，赛题包是 `../../SWE-OpenHarmony/`。不要写本机绝对路径。

```
harmonycup-work/          ← 分支 main
├── README.md
├── common/               ← 公共资源，见 common/README.md
│   └── scripts/          ← 工作区管理脚本
├── cm-spec26/            ← 分支 cm-spec26（worktree）
├── jm-spec7/             ← 分支 jm-spec7（worktree）
└── ...                   ← 其余 23 个赛题
```

## 分支一览

每个赛题分支保留原始提交历史，并有一个 tag `base/<题目ID>` 指向官方 metadata 指定的基线 commit。

| 分支 / 目录 | 来源工程 | 赛题 |
| --- | --- | --- |
| `main` | - | 公共资源与管理脚本 |
| `cm-spec26` | coolmallarkts | 商品详情新增买家评价与详情长图 |
| `cml-combo-search` | coolmallarkts | 商品搜索功能（搜索框/历史记录/推荐关键词/搜索结果跳转/清空历史确认） |
| `cml-spec1` | coolmallarkts | 底部导航栏（首页/分类/购物车/我的） |
| `cml-spec17` | coolmallarkts | 创建订单功能（表单校验/提交下单/跳转支付） |
| `cml-spec24` | coolmallarkts | 商品分类页面完整功能（搜索/筛选/排序/布局切换/分页加载） |
| `cml-spec28` | coolmallarkts | 收货地址列表/新增/编辑功能 |
| `cml-spec7` | coolmallarkts | 登录主页面与手机号登录入口 |
| `cmu-spec1` | cloudmusic-harmonyosnex | API 服务配置页面优化 |
| `cmu-spec102` | cloudmusic-harmonyosnex | 底部播放控制栏与播放页关联 |
| `cmu-spec114` | cloudmusic-harmonyosnex | 0.9.3 版本信息、应用内隐私页与搜索提示统一 |
| `cmu-spec34` | cloudmusic-harmonyosnex | 私人FM 功能 |
| `cmu-spec9` | cloudmusic-harmonyosnex | 悬浮歌词设置选项扩展 |
| `cmu-spec99` | cloudmusic-harmonyosnex | 搜索结果支持手动分页加载 |
| `jm-spec35` | jingmo-for-harmonyos | 关于页面展示应用图标和版本号 |
| `jm-spec7` | jingmo-for-harmonyos | 完善收藏夹支持更多内容类型 |
| `jm-spec71` | jingmo-for-harmonyos | 完成成语模块首屏随机展示功能 |
| `jm-spec75` | jingmo-for-harmonyos | 实现诗文名句模块首屏功能及路由跳转 |
| `sym-combo-customize` | symbolu_next | 符号自定义完整功能（颜色选择器、渲染策略切换、信息栏水平滚动） |
| `vg-spec1` | vignette | WebDAV 还原确认对话框 |
| `vg-spec7` | vignette | WebDAV 恢复操作须在确认后发起网络请求 |
| `vg-spec8` | vignette | WebDAV 恢复取消状态 |
| `vg-spec9` | vignette | WebDAV 手动同步加载反馈 |
| `vg-spec13` | vignette | WebDAV 备份进度提示与实际操作保持一致 |
| `vg-spec14` | vignette | WebDAV 同步进度提示与实际操作保持一致 |
| `vg-spec15` | vignette | WebDAV 恢复进度提示与实际操作保持一致 |

同一来源工程的不同题目基线 commit 不同，代码不能互相合并或拷贝。

## 首次加入

```bash
git clone -b main git@github.com:su-yunhe/HCUP.git harmonycup-work   # 与 SWE-OpenHarmony/ 同级
cd harmonycup-work
common/scripts/setup.sh          # 为 25 个赛题分支建 worktree
common/scripts/status.sh         # 确认 25 个目录都在
```

每道题开工前，按赛题包 README 运行一次 `tools/prepare_baseline.py --task <题目ID> --project <本仓库>/<题目ID>`。

自测用的 Python 环境 `common/.venv` 不进仓库，每台机器按 `common/test-harness/README.md` 建一次。

## 日常协作

1. 开工前先同步：`common/scripts/sync.sh`
2. 在某道题的目录里改代码，在**该目录内**提交，提交只会进该题的分支：

   ```bash
   cd jm-spec7
   git add <文件> && git commit -m "jm-spec7: 修复xxx"
   ```

3. 改公共资源（`common/`、本 README）时，在**根目录**提交，进 `main`。
4. 收工或需要队友看到时：`common/scripts/sync.sh`，只同步某几题用 `common/scripts/sync.sh jm-spec7 vg-spec1`。

`sync.sh` 对 main 和每个赛题目录执行 `pull --rebase` 再 `push`，有未提交改动的目录会跳过并在最后列出。远端新增的赛题会自动建 worktree。

## 协作约定

- **一题一负责人**。同一道题尽量只有一个人改，需要多人时先沟通，减少 rebase 冲突。
- **Agent 只在单题目录里运行**。比赛规则禁止作答时访问其他赛题的基线：在 `jm-spec7/` 里启动 Agent，不要在根目录启动，也不要把其他题目录提供给它。
- **先 commit 再 sync**。不要把半成品长时间留在工作区不提交。
- **不要 force push、不要改写已推送的历史**（`commit --amend`、`rebase -i` 只用于未推送的提交）。
- **赛题分支只放该题的代码**。公共资源放 `common/`，引用方式见 `common/README.md`。
- 提交信息以题目 ID 开头，例如 `vg-spec13: 调整列表刷新逻辑`。
- `oh_modules/`、`build/`、`.hvigor/` 等构建产物已在各题的 `.gitignore` 中忽略，不要强行提交。

## 冲突处理

`sync.sh` 报某个目录 rebase 冲突时：

```bash
cd jm-spec7
git status                 # 查看冲突文件
# 手动解决后
git add <文件> && git rebase --continue
cd .. && common/scripts/sync.sh jm-spec7
```

想放弃本次 rebase 回到同步前的状态：`git rebase --abort`。

## 查看改动与生成补丁

```bash
common/scripts/status.sh                                   # 各题的分支、未提交数、领先/落后、base 之后的提交数
git -C jm-spec7 diff base/jm-spec7                         # 相对官方基线的全部改动（含未提交）
git -C jm-spec7 diff base/jm-spec7 HEAD > jm-spec7.patch   # 只含已提交的改动
```

## 脚本一览（common/scripts/）

- `setup.sh`：为远端每个赛题分支建 worktree，只补缺失的，可重复执行。
- `sync.sh [题目ID...]`：同步 main 和赛题分支，不带参数时同步全部。
- `status.sh`：本地状态一览，不访问网络。
- `publish.sh <团队仓库地址> [题目ID...]`：仅维护者使用，把本地独立的基线仓库发布到团队远端。
- `lib.sh`：公共函数，被其他脚本引用。

## 维护者：新增一道题

维护者本地的赛题目录是独立仓库（`origin` 指向原始 bundle，团队远端叫 `team`），其他人的是 worktree，两种形态脚本都支持。

```bash
# 在根目录下，按赛题包 metadata 克隆
git clone --branch base <赛题包>/repo_bundles/<xxx>-base.bundle new-spec
git -C new-spec checkout --detach <base_commit>
common/scripts/publish.sh git@github.com:su-yunhe/HCUP.git new-spec   # 推分支并打 base/new-spec tag
```

队友下次运行 `common/scripts/sync.sh` 时会自动拿到 `new-spec`。新增后记得更新上面的分支一览。
