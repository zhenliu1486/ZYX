#!/usr/bin/env bash
# ZYX 一行安装器：把 ZYX 多技能包装到本机，并跑 doctor 自检。
#
# 用法：
#   curl -fsSL https://cdn.jsdelivr.net/gh/zhenliu1486/ZYX@main/bootstrap.sh | bash
#   curl -fsSL https://raw.githubusercontent.com/zhenliu1486/ZYX/main/bootstrap.sh | bash
#   bash bootstrap.sh --dir ~/.claude/skills --no-deps
#
# 参数：
#   --dir <dir>       指定宿主 skills 目录（不传则自动探测）
#   --no-deps         只装随仓库内置技能，不装女娲/大师/仓颉/dbs/R8 等外部依赖
#   --ref <ref>       分支或 tag，默认 main
#   --repo <owner/repo> GitHub 仓库，默认 zhenliu1486/ZYX
#   --src <dir>       源码缓存目录，默认 ~/.zyx/src
#   --local <dir>     直接使用本地仓库（离线安装包会用到）
#   -h, --help        显示帮助
#
# 设计原则：这是“多技能包”的安装器，不是单个 SKILL.md。它先拿到完整仓库，
# 再调用仓库自带的 scripts/install.sh，保证内置技能和外部依赖都按清单处理。

set -euo pipefail

REPO="${ZYX_REPO:-zhenliu1486/ZYX}"
REF="${ZYX_REF:-main}"
ZYX_HOME="${ZYX_HOME:-${HOME:-$PWD}/.zyx}"
SRC="${ZYX_SRC:-$ZYX_HOME/src}"
SKILLS_DIR="${ZYX_SKILLS_DIR:-}"
INSTALL_DEPS=1
LOCAL_REPO="${ZYX_LOCAL_REPO:-}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  sed -n '3,19p' "$0"
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dir) SKILLS_DIR="${2:-}"; shift 2 ;;
    --no-deps) INSTALL_DEPS=0; shift ;;
    --ref) REF="${2:-}"; shift 2 ;;
    --repo) REPO="${2:-}"; shift 2 ;;
    --src) SRC="${2:-}"; shift 2 ;;
    --local) LOCAL_REPO="${2:-}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "未知参数: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [ -z "$SRC" ]; then
  echo "源码目录不能为空" >&2
  exit 2
fi

# 离线安装包：bootstrap.sh 旁边如果有 repo/skills，就直接用本地仓库，不再访问 GitHub。
if [ -z "$LOCAL_REPO" ] && [ -d "$SCRIPT_DIR/repo/skills" ]; then
  LOCAL_REPO="$SCRIPT_DIR/repo"
fi

if [ -n "$LOCAL_REPO" ]; then
  if [ ! -f "$LOCAL_REPO/scripts/install.sh" ]; then
    echo "本地仓库不完整：$LOCAL_REPO/scripts/install.sh 不存在" >&2
    exit 2
  fi
  SRC="$LOCAL_REPO"
  echo "== 使用本地仓库：$SRC =="
else
  if ! command -v git >/dev/null 2>&1; then
    echo "缺少 git。请先安装 git，或下载离线包后运行 bash bootstrap.sh --local <解压目录>。" >&2
    exit 2
  fi

  mkdir -p "$(dirname "$SRC")"
  if [ -d "$SRC/.git" ]; then
    echo "== 更新 ZYX 源码缓存：$SRC =="
    git -C "$SRC" fetch --depth 1 origin "$REF"
    git -C "$SRC" reset --hard FETCH_HEAD
  else
    echo "== 克隆 ZYX：$REPO@$REF =="
    git clone --depth 1 --branch "$REF" "https://github.com/$REPO.git" "$SRC"
  fi
fi

if [ ! -f "$SRC/scripts/install.sh" ]; then
  echo "找不到 $SRC/scripts/install.sh；仓库结构可能已变化。" >&2
  exit 2
fi

cd "$SRC"

args=()
[ -n "$SKILLS_DIR" ] && args+=(--dir "$SKILLS_DIR")
[ "$INSTALL_DEPS" -eq 1 ] && args+=(--install-deps)

echo
echo "== 开始安装 =="
bash scripts/install.sh "${args[@]}"

echo
echo "== 完成 =="
cat <<'MSG'
ZYX 已安装。新开一个对话，直接说：

  用 ZYX 帮我……

如果自检提示缺外部依赖，重跑：
  curl -fsSL https://cdn.jsdelivr.net/gh/zhenliu1486/ZYX@main/bootstrap.sh | bash

不要只从 GitHub 搜索“zyx skill”：ZYX 是 16 个技能的多技能包，仓库根目录故意没有单个 SKILL.md。
MSG
