#!/usr/bin/env bash
# 打「豆包开放平台 · 公开上架」用的单技能安装器包。
# 产物：
#   dist/doubao-public/zyx-installer.zip          # SKILL.md 在 ZIP 根目录
#   dist/doubao-public/zyx-installer-folder.zip   # 根目录下 zyx-installer/SKILL.md
#
# 这只是一个安装器技能，不塞 19 个嵌套技能；运行时从 GitHub 取仓库。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT_DIR="$ROOT/dist/doubao-public"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$OUT_DIR" "$TMP/root" "$TMP/folder/zyx-installer"

cp "$ROOT/docs/doubao/public-skill.md" "$TMP/root/SKILL.md"
cp "$ROOT/bootstrap.sh" "$TMP/root/bootstrap.sh"
cp "$ROOT/README.md" "$TMP/root/README.md"
cp "$ROOT/LICENSE" "$TMP/root/LICENSE"
cp "$ROOT/docs/doubao/zyx-icon.png" "$TMP/root/icon.png"

cp -R "$TMP/root/." "$TMP/folder/zyx-installer/"

make_zip() { # $1=src  $2=dest
  python3 - "$1" "$2" <<'PY'
import os, sys, zipfile
src, dest = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d not in {".git", "__pycache__"}]
        for f in files:
            if f.endswith(".pyc"):
                continue
            full = os.path.join(root, f)
            rel = os.path.relpath(full, src)
            z.write(full, rel)
print(dest)
PY
}

make_zip "$TMP/root" "$OUT_DIR/zyx-installer.zip"
make_zip "$TMP/folder" "$OUT_DIR/zyx-installer-folder.zip"

python3 - "$OUT_DIR" <<'PY'
import os, sys, zipfile
for name in ("zyx-installer.zip", "zyx-installer-folder.zip"):
    p = os.path.join(sys.argv[1], name)
    with zipfile.ZipFile(p) as z:
        infos = z.infolist()
        total = sum(i.file_size for i in infos)
        print(f"{name}: {len(infos)} entries, {total} bytes uncompressed, {os.path.getsize(p)} bytes zip")
        if len(infos) > 1024 or total > 16 * 1024 * 1024:
            raise SystemExit(f"{name} exceeds Doubao limits")
        for i in infos:
            if i.file_size > 2 * 1024 * 1024:
                raise SystemExit(f"{name}: {i.filename} exceeds 2MB")
PY

echo "已生成:"
echo "  $OUT_DIR/zyx-installer.zip"
echo "  $OUT_DIR/zyx-installer-folder.zip"
echo "上传：豆包开放平台 → 技能列表 → 创建技能 → 公开上架 → 上传 zip。"
