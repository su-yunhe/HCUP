# common

所有基线共用的资源：文档、prompt、AGENTS 模板、检查脚本、测试数据等。这个目录属于 main 分支，跟着 `scripts/sync.sh` 同步。

- 不要把这里的文件提交进任何基线分支，否则会混进该题的补丁。
- 基线里需要用到时，优先用相对路径 `../common/xxx` 引用。
- 必须出现在基线目录里的（比如构建时要读的配置），用软链接，并加到本地排除列表，不提交：

  ```bash
  cd jm-spec7
  ln -s ../common/xxx xxx
  echo "/xxx" >> "$(git rev-parse --git-common-dir)/info/exclude"
  ```

  队友环境下所有 worktree 共用一个 exclude 文件，写一次即可。
