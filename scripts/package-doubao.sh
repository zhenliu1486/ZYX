#!/usr/bin/env bash
# 把技能目录打成豆包「上传技能」可直接用的 zip。
# 用法：bash scripts/package-doubao.sh [--out DIR] [--only name1,name2]
# 产物：dist/doubao/<skill>.zip（内含 <skill>/SKILL.md）
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/dist/doubao"
ONLY=""

while [ $# -gt 0 ]; do
  case "$1" in
    --out) OUT="$2"; shift 2 ;;
    --only) ONLY="$2"; shift 2 ;;
    -h|--help) sed -n '1,6p' "$0"; exit 0 ;;
    *) echo "未知参数: $1" >&2; exit 2 ;;
  esac
done

mkdir -p "$OUT"
packed=0; skipped=0

for src in "$ROOT"/skills/*/; do
  [ -f "${src}SKILL.md" ] || continue
  name="$(basename "$src")"
  if [ -n "$ONLY" ]; then
    case ",$ONLY," in *",$name,"*) ;; *) skipped=$((skipped+1)); continue ;; esac
  fi
  # 校验 frontmatter 必填项
  if ! head -20 "${src}SKILL.md" | grep -qE '^name:\s*\S' || ! head -40 "${src}SKILL.md" | grep -qE '^description:\s*\S'; then
    echo "跳过 $name：SKILL.md 缺少 YAML name/description" >&2
    skipped=$((skipped+1)); continue
  fi
  python3 - "$src" "$OUT/$name.zip" "$name" <<'PY'
import os, sys, zipfile
src, dest, name = sys.argv[1], sys.argv[2], sys.argv[3]
skip_dirs = {"state", "__pycache__", ".git", "node_modules", "cycles"}
skip_files = {".DS_Store"}
with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
    for root_dir, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        rel = os.path.relpath(root_dir, src)
        for f in files:
            if f in skip_files or f.endswith(".pyc"):
                continue
            full = os.path.join(root_dir, f)
            arc = os.path.join(name, "" if rel == "." else rel, f)
            z.write(full, arc)
print(dest)
PY
  echo "✅ $name.zip"
  packed=$((packed+1))
done

echo
echo "已打包 $packed 个技能，跳过 $skipped 个；输出目录：$OUT"
echo "安装：豆包 PC →「技能·连接器·伙伴」→「我的技能」→ 上传技能 → 拖入 zip。"
[ "$packed" -gt 0 ]
