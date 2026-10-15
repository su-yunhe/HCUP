# 公共函数，由其他脚本 source，不单独执行。
# 执行后当前目录切换到工作区根目录。

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT" || exit 1

# 列出所有基线目录：根目录下含 .git（独立仓库为目录，worktree 为文件）的一级子目录
baselines() {
  local d
  for d in */; do
    d=${d%/}
    [ -e "$d/.git" ] && echo "$d"
  done
}

# 基线使用的团队远端名：维护者本地的独立仓库用 team（origin 仍指向原始 bundle），worktree 用 origin
remote_of() {
  if git -C "$1" remote | grep -qx team; then echo team; else echo origin; fi
}

is_dirty() {
  [ -n "$(git -C "$1" status --porcelain)" ]
}
