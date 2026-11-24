#!/usr/bin/env bash
# lib-common.sh — zyx 脚本共用的宿主目录探测与依赖读取（被 doctor/updater/route source）。
# 依赖清单与宿主目录统一来自 deps/manifest.json，不在脚本里重复硬编码。

# shellcheck source=deps.py
_common_deps() { python3 "$SCRIPT_DIR/deps.py" "$@"; }

# 从 manifest 读取宿主目录，追加 ZYX_EXTRA_SKILL_DIRS（冒号分隔）
_common_load_host_dirs() {
  HOST_DIRS=()
  local line
  # 优先：zyx 自身所在的同级 skills 目录（安装器把内置兄弟技能复制在 zyx 旁边）
  local self_parent
  self_parent="$(cd "$SCRIPT_DIR/.." && pwd)/.."
  HOST_DIRS+=("$self_parent")
  while IFS= read -r line; do
    [ -n "$line" ] && HOST_DIRS+=("$line")
  done < <(_common_deps host-dirs 2>/dev/null)
  if [ -n "${ZYX_EXTRA_SKILL_DIRS:-}" ]; then
    local extra
    IFS=':' read -ra extra <<< "$ZYX_EXTRA_SKILL_DIRS"
    HOST_DIRS+=("${extra[@]}")
  fi
}

# find_local <dir> → 打印第一个含 SKILL.md 的本地路径；找不到返回 1
find_local() {
  local dir="$1" base
  for base in "${HOST_DIRS[@]}"; do
    [ -f "$base/$dir/SKILL.md" ] && { echo "$base/$dir"; return 0; }
  done
  return 1
}

# find_local_git <dir> → 打印第一个含 .git 的本地路径；找不到返回 1
find_local_git() {
  local dir="$1" base
  for base in "${HOST_DIRS[@]}"; do
    [ -d "$base/$dir/.git" ] && { echo "$base/$dir"; return 0; }
  done
  return 1
}

_common_load_host_dirs
