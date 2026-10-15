#!/usr/bin/env bash
# 仅维护者执行：把根目录 main 和本地的独立基线仓库发布到团队远端。可重复执行。
# 每个基线：推到同名分支，并打上 tag base/<名称>（取自 origin bundle 文件名里的 commit）。
# 有未提交改动的仓库会跳过。
# 用法: scripts/publish.sh <团队仓库地址> [基线名...]
set -u
. "$(dirname "$0")/lib.sh"

REMOTE=${1:?用法: scripts/publish.sh <团队仓库地址> [基线名...]}
shift
[ $# -gt 0 ] || set -- $(baselines)

skipped=""

echo "== main"
git remote get-url origin >/dev/null 2>&1 || git remote add origin "$REMOTE"
git push -q -u origin main || skipped="$skipped main"

for d in "$@"; do
  echo "== $d"
  if [ -f "$d/.git" ]; then
    echo "  已是 worktree，用 sync.sh 同步"; continue
  fi
  if [ ! -d "$d/.git" ]; then
    echo "  不是基线目录，跳过"; skipped="$skipped $d"; continue
  fi
  if is_dirty "$d"; then
    echo "  有未提交改动，跳过"; skipped="$skipped $d"; continue
  fi

  git -C "$d" remote get-url team >/dev/null 2>&1 || git -C "$d" remote add team "$REMOTE"
  # 游离 HEAD 时建一个同名分支，便于之后 pull/push
  git -C "$d" symbolic-ref -q HEAD >/dev/null || git -C "$d" switch -q -c "$d"

  base=$(basename "$(git -C "$d" remote get-url origin 2>/dev/null)" | sed -nE 's/.*-([0-9a-f]{7,40})-base\.bundle$/\1/p')
  if [ -n "$base" ] && ! git -C "$d" rev-parse -q --verify "refs/tags/base/$d" >/dev/null; then
    git -C "$d" tag "base/$d" "$base" || base=""
  fi

  git -C "$d" push -q -u team "HEAD:refs/heads/$d" || { skipped="$skipped $d"; continue; }
  if git -C "$d" rev-parse -q --verify "refs/tags/base/$d" >/dev/null; then
    git -C "$d" push -q team "refs/tags/base/$d" || skipped="$skipped $d"
  else
    echo "  未找到 base commit，没有打 tag"
  fi
done

if [ -n "$skipped" ]; then
  echo
  echo "未发布:$skipped"
  exit 1
fi
echo
echo "全部发布完成"
