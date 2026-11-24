#!/usr/bin/env bash
# desktop-dir.sh — 跨平台探测可用的产物桌面根目录。
# 回退顺序写死：桌面 → 文档 → HOME 下 zyx-output。
# 用法: source 本文件后调用 resolve_desktop_dir；或直接 bash desktop-dir.sh 打印路径。

set -uo pipefail

resolve_desktop_dir() {
  local candidates=()
  case "$(uname -s)" in
    Darwin)
      # macOS：中英文桌面都试
      candidates=("$HOME/Desktop" "$HOME/Desktop/桌面" "$HOME/Documents" "$HOME")
      ;;
    Linux)
      # Linux 桌面（XDG 或中文目录），容器常无桌面目录
      candidates=("$HOME/Desktop" "$HOME/桌面" "${XDG_DOCUMENTS_DIR:-$HOME/Documents}" "$HOME/Documents" "$HOME")
      ;;
    MINGW*|MSYS*|CYGWIN*)
      candidates=("$USERPROFILE/Desktop" "$USERPROFILE/Documents" "$USERPROFILE")
      ;;
    *)
      candidates=("$HOME/Desktop" "$HOME/Documents" "$HOME")
      ;;
  esac

  local d
  for d in "${candidates[@]}"; do
    [ -n "$d" ] && [ -d "$d" ] && { echo "$d"; return 0; }
  done
  # 兜底：HOME 必然存在
  echo "$HOME"
  return 0
}

# 直接执行时打印最终产物根目录（桌面/文档下的 zyx-output）
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
  base="$(resolve_desktop_dir)"
  echo "$base/zyx-output"
fi
