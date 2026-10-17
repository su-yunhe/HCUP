#!/usr/bin/env bash
# 同步 main（公共资源）和基线：先 rebase 到远端再 push。不带参数时同步全部，并补齐远端新增的基线。
# 只 fetch 一次拿到所有分支的远端状态，与远端一致的目录直接跳过，只有真正有差异的才访问网络。
# 有未提交改动的目录会跳过，先 commit 再同步。
# 用法: common/scripts/sync.sh [基线名...]
set -u
. "$(dirname "$0")/lib.sh"

failed=""

git fetch -q --prune origin || exit 1

if [ $# -eq 0 ]; then
  echo "== main"
  if is_dirty .; then
    echo "  有未提交改动，跳过"; failed="$failed main"
  elif ! git rebase -q origin/main; then
    failed="$failed main"
  elif [ "$(git rev-list --count origin/main..HEAD)" -gt 0 ]; then
    git push -q origin main || failed="$failed main"
  fi
  "$ROOT/common/scripts/setup.sh" --no-fetch || failed="$failed setup"
  set -- $(baselines)
fi

for d in "$@"; do
  if [ ! -e "$d/.git" ]; then
    echo "== $d: 不是基线目录，跳过"; failed="$failed $d"; continue
  fi
  if is_dirty "$d"; then
    echo "== $d: 有未提交改动，跳过"; failed="$failed $d"; continue
  fi
  # 与根仓库刚 fetch 到的远端同名分支一致，说明无需同步
  [ "$(git -C "$d" rev-parse HEAD)" = "$(git rev-parse -q --verify "refs/remotes/origin/$d")" ] && continue
  echo "== $d"
  r=$(remote_of "$d")
  { git -C "$d" pull -q --rebase "$r" "$d" && git -C "$d" push -q "$r" "HEAD:refs/heads/$d"; } || failed="$failed $d"
done

if [ -n "$failed" ]; then
  echo
  echo "未完成:$failed"
  echo "rebase 冲突时：进入目录解决冲突 -> git add -> git rebase --continue，再重跑本脚本。"
  exit 1
fi
echo
echo "全部同步完成"
