#!/usr/bin/env bash
# 一览所有基线的状态，不访问网络（想看最新的远端情况先跑 sync.sh 或 git fetch）。
#   DIRTY       未提交的文件数
#   AHEAD/BEHIND 相对团队远端同名分支领先/落后的提交数，"-" 表示尚未发布
#   SINCE-BASE  基线 tag base/<名称> 之后的提交数
# 用法: common/scripts/status.sh
set -u
. "$(dirname "$0")/lib.sh"

printf "%-22s %-20s %6s %13s %11s\n" NAME BRANCH DIRTY AHEAD/BEHIND SINCE-BASE
for d in $(baselines); do
  r=$(remote_of "$d")
  br=$(git -C "$d" symbolic-ref -q --short HEAD || echo "(detached)")
  n=$(git -C "$d" status --porcelain | wc -l | tr -d ' ')
  ab=$(git -C "$d" rev-list --left-right --count "HEAD...$r/$d" 2>/dev/null | awk '{print "+"$1"/-"$2}')
  nb=$(git -C "$d" rev-list --count "base/$d..HEAD" 2>/dev/null)
  printf "%-22s %-20s %6s %13s %11s\n" "$d" "$br" "$n" "${ab:--}" "${nb:--}"
done
