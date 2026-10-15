#!/usr/bin/env bash
# 为远端的每个基线分支在根目录下建一个同名 worktree。
# 队友 clone main 后执行一次；之后 sync.sh 会自动调用它来补齐新增的基线。可重复执行。
# 用法: common/scripts/setup.sh
set -u
. "$(dirname "$0")/lib.sh"

git fetch -q --prune origin || exit 1

for b in $(git for-each-ref --format='%(refname:lstrip=3)' refs/remotes/origin); do
  case "$b" in main|HEAD) continue ;; esac
  [ -e "$b" ] && continue
  echo "+ $b"
  if git show-ref -q --verify "refs/heads/$b"; then
    git worktree add -q "$b" "$b"
  else
    git worktree add -q --track -b "$b" "$b" "origin/$b"
  fi
done
