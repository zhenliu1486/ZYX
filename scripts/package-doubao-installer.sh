#!/usr/bin/env bash
# 打一个「豆包上传技能」可直接用的 ZYX 安装器包。
# 产物：dist/doubao/zyx-installer.zip
# 结构：根目录 SKILL.md（zyx-installer）+ bootstrap.sh + repo/（完整 ZYX 多技能仓库）
# 用途：豆包不能执行终端时，用户上传这个 zip，再说「帮我安装 zyx」。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/dist/doubao/zyx-installer.zip"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$ROOT/dist/doubao" "$TMP/repo"

# 根级安装器与仓库共用同一份 SKILL.md，避免两套文案漂移。
cp "$ROOT/SKILL.md" "$TMP/SKILL.md"
cp "$ROOT/bootstrap.sh" "$TMP/bootstrap.sh"
cp "$ROOT/INSTALL.md" "$TMP/INSTALL.md"
cp "$ROOT/README.md" "$TMP/README.md"
cp "$ROOT/llms.txt" "$TMP/llms.txt"
cp "$ROOT/LICENSE" "$TMP/LICENSE"

# 只复制运行所需内容，不带 .git / dist / docs / 依赖缓存。
# repo/ 里删掉根级 SKILL.md，避免出现两个 zyx-installer。
tar -C "$ROOT" \
  --exclude=.git --exclude=dist --exclude=docs \
  --exclude='*.pyc' --exclude='__pycache__' \
  -cf - . | tar -C "$TMP/repo" -xf -
rm -f "$TMP/repo/SKILL.md"

python3 - "$TMP" "$OUT" <<'PY'
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

echo "已生成: $OUT"
echo "安装：豆包 PC →「技能·连接器·伙伴」→「我的技能」→「上传技能」→ 拖入 zip；新开对话说「帮我安装 zyx」。"
