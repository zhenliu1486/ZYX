#!/usr/bin/env bash
# sync-hosts.sh — 把本仓库内置 Skill 同步到本机所有已存在的宿主 skills 目录。
# 兼容 macOS 自带 Bash 3.2；每个宿主复用 install.sh，装完由 install.sh 跑自检。
# 用法: bash scripts/sync-hosts.sh [--install-deps]

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPS_PY="$ROOT/skills/zyx/scripts/deps.py"
INSTALL="$ROOT/scripts/install.sh"
if [ "$#" -gt 0 ]; then EXTRA=("$@"); else EXTRA=(); fi

if [ ! -f "$DEPS_PY" ] || [ ! -f "$INSTALL" ]; then
  echo "找不到安装器：$ROOT" >&2
  exit 2
fi
if ! command -v python3 >/dev/null 2>&1; then
  echo "需要 python3 读取宿主目录清单" >&2
  exit 2
fi

HOSTS=()
i=0
while IFS= read -r d; do
  [ -z "$d" ] && continue
  [ -d "$d" ] || continue
  HOSTS[$i]="$d"
  i=$((i + 1))
done < <(python3 "$DEPS_PY" host-dirs)

# 通用落点：即使宿主目录还没建，也保证 ~/.agents/skills 有一份
AGENTS="$HOME/.agents/skills"
already=0
for d in "${HOSTS[@]}"; do
  [ "$d" = "$AGENTS" ] && already=1
done
if [ "$already" -eq 0 ]; then
  HOSTS[$i]="$AGENTS"
  i=$((i + 1))
fi

if [ "$i" -eq 0 ]; then
  echo "没有发现已存在的宿主 skills 目录；先建一个，或用 install.sh --dir 指定。" >&2
  exit 1
fi

echo "===== 同步 ZYX 到 $i 个宿主 ====="
for d in "${HOSTS[@]}"; do
  echo
  echo "## → $d"
  if [ "${#EXTRA[@]}" -gt 0 ]; then
    bash "$INSTALL" --dir "$d" "${EXTRA[@]}" || exit 1
  else
    bash "$INSTALL" --dir "$d" || exit 1
  fi
done

echo
echo "===== 同步完成：$i 个宿主 ====="
