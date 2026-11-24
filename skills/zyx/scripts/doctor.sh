#!/usr/bin/env bash
# doctor.sh — zyx 安装就绪自检（与仓颉 doctor 同思路）。
# 装完或排障时跑一遍：检查运行依赖、蒸馏器安装状态、调度环境、产物目录可写性，
# 输出「就绪 / 缺什么 / 怎么补」的结论。只读检查，不改动任何文件。
# 退出码: 0 全部就绪；1 存在缺失项；2 脚本本身出错。

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZYX_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

HOST_DIRS=(
  "$HOME/.claude/skills"
  "$HOME/.openclaw/skills"
  "$HOME/.agents/skills"
  "$HOME/.doubao/agent_mode/workspace/.user_skills"
)

# 代号|目录名|上游仓库
DEPS=(
  "R1女娲|nuwa-skill|https://github.com/alchaincyf/nuwa-skill"
  "R2大师|master-skill|https://github.com/swaylq/master-skill"
  "R3仓颉|cangjie-skill|https://github.com/kangarooking/cangjie-skill"
)

warn=0
fail=0

find_local() { # $1=目录名
  local dir="$1" base
  for base in "${HOST_DIRS[@]}"; do
    [ -f "$base/$dir/SKILL.md" ] && { echo "$base/$dir"; return 0; }
  done
  return 1
}

check_cmd() { # $1=命令 $2=用途
  if command -v "$1" >/dev/null 2>&1; then
    echo "  ✅ $1 可用（$2）"
  else
    echo "  ⚠ 缺少 $1（$2）"
    warn=1
  fi
}

echo "===== zyx 就绪自检 $(date '+%Y-%m-%d %H:%M') ====="
echo "zyx 目录: $ZYX_DIR"
echo

echo "## 1. 运行依赖"
check_cmd bash "脚本执行"
check_cmd git "蒸馏器版本检测与更新"
check_cmd curl "远端版本/网络可达性检查"
command -v python3 >/dev/null 2>&1 && echo "  ✅ python3 $(python3 --version 2>/dev/null | awk '{print $2}')" || echo "  ℹ 未装 python3（仓颉脚本/PY 依赖需要时再补）"
echo

echo "## 2. 蒸馏器安装状态"
for entry in "${DEPS[@]}"; do
  IFS='|' read -r label dir repo <<< "$entry"
  p="$(find_local "$dir" || true)"
  if [ -n "$p" ]; then
    echo "  ✅ $label → $p"
  else
    echo "  ❌ $label 未安装（$dir）。安装: git clone $repo"
    fail=1
  fi
done
# dbs 主调度台
if [ -f "$HOME/.doubao/agent_mode/workspace/.user_skills/dbs/SKILL.md" ] || [ -f "$HOME/.agents/skills/dbs/SKILL.md" ]; then
  echo "  ✅ dbs 主调度台已安装"
else
  echo "  ⚠ dbs 主调度台未检测到；当下问题诊断/文案能力不可用。安装: npx -y skills add dontbesilent2025/dbskill -g --all"
  warn=1
fi
echo

echo "## 3. 调度环境（后台自动更新）"
if command -v crontab >/dev/null 2>&1; then echo "  ✅ crontab 可用"; else echo "  ⚠ 无 crontab"; fi
if command -v launchctl >/dev/null 2>&1; then echo "  ✅ launchctl 可用（macOS）"; fi
if command -v systemctl >/dev/null 2>&1; then echo "  ✅ systemd 可用（Linux）"; fi
if [ ! -f "$ZYX_DIR/state/registry.json" ]; then
  echo "  ℹ 尚未注册后台更新任务；首次调用 zyx 时 env-registry.sh 会自动注册。"
fi
echo

echo "## 4. 产物目录可写性"
# shellcheck source=desktop-dir.sh
source "$SCRIPT_DIR/desktop-dir.sh"
desktop="$(resolve_desktop_dir)"
out="$desktop/zyx-output"
if mkdir -p "$out/.write-test" 2>/dev/null; then
  rmdir "$out/.write-test" 2>/dev/null
  echo "  ✅ 产物目录可写: $out"
else
  echo "  ❌ 产物目录不可写: $out"
  fail=1
fi
echo

echo "## 结论"
if [ "$fail" -eq 1 ]; then
  echo "存在必须补齐的缺失项（见 ❌），补齐后重跑 doctor。"
  exit 1
elif [ "$warn" -eq 1 ]; then
  echo "基本就绪，有可选缺失项（见 ⚠），不影响核心路由。"
else
  echo "全部就绪。"
fi
exit 0
