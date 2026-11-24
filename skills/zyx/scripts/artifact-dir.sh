#!/usr/bin/env bash
# artifact-dir.sh — 按规范创建产物目录并返回规范路径。
# 规则：产物根/<来源 Skill 子目录>/<产物 slug>[-日期后缀]/
# 用法:
#   bash artifact-dir.sh <来源: nuwa|master|cangjie|dbs|video|f2r|wiki|look> <产物名> [--date YYYYMMDD] [--create]
# 不加 --create 只返回规范路径；--create 才创建目录。
# 退出码: 0 成功；1 参数错误；2 命名不合法。

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=desktop-dir.sh
source "$SCRIPT_DIR/desktop-dir.sh"

# 来源 → 一级子目录名
declare -A SOURCE_DIR=(
  [nuwa]="nuwa"
  [master]="master"
  [cangjie]="cangjie"
  [dbs]="dbs"
  [video]="video"
  [f2r]="f2r"
  [wiki]="wiki"
  [look]="look"
)

SOURCE=""
PRODUCT=""
DATE_SUFFIX=""
CREATE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --date) DATE_SUFFIX="${2:-}"; shift 2 ;;
    --create) CREATE=1; shift ;;
    *)
      if [ -z "$SOURCE" ]; then SOURCE="$1"
      elif [ -z "$PRODUCT" ]; then PRODUCT="$1"
      else echo "多余参数: $1" >&2; exit 1; fi
      shift ;;
  esac
done

if [ -z "$SOURCE" ] || [ -z "$PRODUCT" ]; then
  echo "用法: artifact-dir.sh <来源: nuwa|master|cangjie|dbs|video|f2r|wiki|look> <产物名> [--date YYYYMMDD] [--create]" >&2
  exit 1
fi

if [ -z "${SOURCE_DIR[$SOURCE]:-}" ]; then
  echo "未知来源: $SOURCE（可选: ${!SOURCE_DIR[*]}）" >&2
  exit 1
fi

# slug 规范化：小写、空格/中文外符号转连字符，去掉非法字符
slug="$(echo "$PRODUCT" | tr '[:upper:]' '[:lower:]' | tr ' /\\' '-' | tr -c 'a-z0-9一-龥-' '-' | sed 's/-\{2,\}/-/g; s/^-//; s/-$//')"
if [ -z "$slug" ]; then
  echo "产物名无法生成合法 slug: $PRODUCT" >&2
  exit 2
fi

subdir="${SOURCE_DIR[$SOURCE]}"
if [ -n "$DATE_SUFFIX" ]; then slug="${slug}-${DATE_SUFFIX}"; fi

root="$(resolve_desktop_dir)/zyx-output"
target="$root/$subdir/$slug"

if [ "$CREATE" -eq 1 ]; then
  mkdir -p "$target/sources" "$target/evals"
fi
echo "$target"
