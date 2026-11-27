#!/usr/bin/env bash
# install.sh — ZYX 一键安装器（仓库根目录）。
#
# 做什么：
#   1. 识别宿主 skills 目录（来自 deps/manifest.json 的 host_dirs，可被 --dir 覆盖）。
#   2. 把仓库内置（bundled）的全部 Skill 目录复制进目标目录（不含 state/、.git、日志）。
#   3. 可选 --install-deps：按清单克隆 git 依赖、执行 npx 依赖安装命令。
#   4. 装完跑 doctor.sh 自检。
#
# 用法：
#   bash install.sh                      自动选择第一个可写宿主目录安装
#   bash install.sh --dir <skills-dir>   指定目标 skills 目录
#   bash install.sh --list-hosts         只列出候选宿主目录
#   bash install.sh --install-deps       同时安装外部 git/npx 依赖
#
# 说明：内置 Skill（zyx / video-studio / R5 子技能 / f2r）随仓库复制；
#       上游蒸馏器（女娲/大师/仓颉/dbs/达尔文）需 --install-deps 或按 README 单独安装。

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_SRC="$ROOT/skills"
DEPS_PY="$SKILLS_SRC/zyx/scripts/deps.py"

LIST_HOSTS=0
INSTALL_DEPS=0
TARGET_DIR=""

while [ $# -gt 0 ]; do
  case "$1" in
    --dir) TARGET_DIR="${2:-}"; shift 2 ;;
    --list-hosts) LIST_HOSTS=1; shift ;;
    --install-deps) INSTALL_DEPS=1; shift ;;
    *) echo "未知参数: $1" >&2; exit 2 ;;
  esac
done

if [ ! -d "$SKILLS_SRC" ]; then
  echo "找不到仓库 skills 目录: $SKILLS_SRC" >&2; exit 2
fi

# 候选宿主目录（展开 $HOME）；用 while 读取，兼容 macOS 自带 Bash 3.2
HOST_DIRS=()
host_idx=0
while IFS= read -r d; do
  [ -z "$d" ] && continue
  HOST_DIRS[$host_idx]="$d"
  host_idx=$((host_idx + 1))
done < <(python3 "$DEPS_PY" host-dirs)

if [ "${#HOST_DIRS[@]}" -eq 0 ]; then
  echo "没有可用的宿主 skills 目录；请用 --dir 指定目标。" >&2
  exit 1
fi

if [ "$LIST_HOSTS" -eq 1 ]; then
  echo "候选宿主 skills 目录："
  for d in "${HOST_DIRS[@]}"; do echo "  $d"; done
  exit 0
fi

detect_target() {
  local d
  for d in "${HOST_DIRS[@]}"; do
    if [ -d "$d" ] && [ -w "$d" ]; then echo "$d"; return 0; fi
  done
  # 都不存在：取第一个 HOME 下目录并创建
  for d in "${HOST_DIRS[@]}"; do
    case "$d" in "$HOME"/*) echo "$d"; return 0 ;; esac
  done
  echo "${HOST_DIRS[0]}"
}

if [ -z "$TARGET_DIR" ]; then
  TARGET_DIR="$(detect_target)"
fi
mkdir -p "$TARGET_DIR"
if [ ! -w "$TARGET_DIR" ]; then
  echo "目标目录不可写: $TARGET_DIR" >&2; exit 1
fi
# 防止把仓库 skills 自己当成安装目标（会 mv 掉源目录）
TARGET_REAL="$(cd "$TARGET_DIR" && pwd)"
SKILLS_REAL="$(cd "$SKILLS_SRC" && pwd)"
case "$TARGET_REAL" in
  "$SKILLS_REAL"|"$SKILLS_REAL"/*)
    echo "目标目录不能是仓库 skills 目录本身或其子目录: $TARGET_REAL" >&2
    exit 1 ;;
esac

echo "===== ZYX 安装 ====="
echo "仓库根目录: $ROOT"
echo "目标 skills 目录: $TARGET_DIR"
echo

# 1. 复制内置 Skill（原子安装：先落 stage，再备份旧目录，最后 rename 替换）
echo "## 复制内置 Skill"
BACKUP_ROOT="${ZYX_INSTALL_BACKUP:-$HOME/.zyx-backups}"
STAMP="$(date +%Y%m%d-%H%M%S)-$$"
STAGE=""
cleanup_stage() { [ -n "${STAGE:-}" ] && rm -rf "$STAGE"; }
trap cleanup_stage EXIT INT TERM

for src in "$SKILLS_SRC"/*/; do
  name="$(basename "$src")"
  dest="$TARGET_DIR/$name"
  STAGE="$TARGET_DIR/.zyx-stage-$name-$$"
  rm -rf "$STAGE"
  mkdir -p "$STAGE"
  cp -R "$src/." "$STAGE/"
  rm -rf "$STAGE/state" "$STAGE/.git" "$STAGE/__pycache__"
  find "$STAGE" -name '*.pyc' -type f -delete 2>/dev/null || true

  backup_parent=""
  if [ ! -f "$STAGE/SKILL.md" ]; then
    echo "  ❌ $name 缺少 SKILL.md，跳过安装" >&2
    rm -rf "$STAGE"; STAGE=""; exit 1
  fi

  if [ -e "$dest" ]; then
    backup_parent="$BACKUP_ROOT/$STAMP"
    mkdir -p "$backup_parent"
    if ! mv "$dest" "$backup_parent/$name"; then
      echo "  ❌ $name 旧目录备份失败，未覆盖" >&2
      rm -rf "$STAGE"; STAGE=""; exit 1
    fi
    echo "  已备份旧版: $backup_parent/$name"
  fi

  if ! mv "$STAGE" "$dest"; then
    echo "  ❌ $name 安装失败，尝试恢复旧版" >&2
    if [ -n "$backup_parent" ] && [ -d "$backup_parent/$name" ]; then mv "$backup_parent/$name" "$dest"; fi
    rm -rf "$STAGE"; STAGE=""; exit 1
  fi
  STAGE=""
  echo "  ✅ $name"
done
echo

# 2. 可选：安装外部 git / npx 依赖
if [ "$INSTALL_DEPS" -eq 1 ]; then
  echo "## 安装外部依赖"
  while IFS=$'\x1f' read -r id dir source required parent url install notes; do
    [ -z "$dir" ] && continue
    if [ "$source" = "git" ]; then
      if [ -d "$TARGET_DIR/$dir" ]; then
        echo "  ℤ [$id] $dir 已存在，跳过克隆。"
      else
        echo "  ⬇ [$id] 克隆 $dir ← $url"
        git clone --depth 1 "$url" "$TARGET_DIR/$dir" || echo "  ❌ [$id] 克隆失败，请手动: $install"
      fi
    elif [ "$source" = "npx" ]; then
      if [ -d "$TARGET_DIR/$dir" ]; then
        echo "  ℤ [$id] $dir 已存在，跳过 npx。"
      else
        echo "  ⬇ [$id] 执行: $install"
        bash -c "$install" || echo "  ❌ [$id] 安装失败，请手动执行: $install"
      fi
    fi
  done < <(python3 "$DEPS_PY" deps)
  echo
fi

# 3. 自检
echo "## 安装后自检"
if [ -f "$TARGET_DIR/zyx/scripts/doctor.sh" ]; then
  bash "$TARGET_DIR/zyx/scripts/doctor.sh" || true
else
  echo "  ⚠ 未找到 zyx/scripts/doctor.sh，跳过自检。"
fi

echo
echo "安装完成。如需在其他宿主复用，把 $TARGET_DIR 下对应 Skill 目录复制过去即可。"
