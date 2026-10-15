#!/usr/bin/env bash
# 同步 main（公共资源）和基线：先 pull --rebase 再 push。不带参数时同步全部，并补齐远端新增的基线。
# 有未提交改动的目录会跳过，先 commit 再同步。
# 用法: common/scripts/sync.sh [基线名...]
set -u
. "$(dirname "$0")/lib.sh"

failed=""

if [ $# -eq 0 ]; then
  echo "== main"
  if is_dirty .; then
    echo "  有未提交改动，跳过"; failed="$failed main"
  else
    { git pull -q --rebase origin main && git push -q origin main; } || failed="$failed main"
  fi
  "$ROOT/common/scripts/setup.sh" || failed="$failed setup"
  set -- $(baselines)
fi

for d in "$@"; do
  echo "== $d"
  if [ ! -e "$d/.git" ]; then
    echo "  不是基线目录，跳过"; failed="$failed $d"; continue
  fi
  if is_dirty "$d"; then
    echo "  有未提交改动，跳过"; failed="$failed $d"; continue
  fi
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
