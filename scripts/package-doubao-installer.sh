#!/usr/bin/env bash
# 打一个「豆包上传技能」可直接用的 ZYX 安装器包。
# 产物：dist/doubao/zyx-installer.zip
# 结构：根目录 SKILL.md + bootstrap.sh + repo/（完整 ZYX 多技能仓库）
# 用途：豆包不能执行终端时，用户上传这个 zip，再说「帮我安装 zyx」。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/dist/doubao/zyx-installer.zip"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

mkdir -p "$ROOT/dist/doubao" "$TMP/repo"

cat > "$TMP/SKILL.md" <<'EOF'
---
name: zyx-installer
description: 当用户说「帮我安装 zyx 这个 skill」「安装 ZYX 调度台」「部署 zyx」「装一下 zyx」时使用。这个技能是 ZYX 的安装器，不是 ZYX 本体；它把本包内的完整 ZYX 多技能仓库安装到当前设备，不执行具体业务任务。
metadata:
  version: "1.0.0"
---

# ZYX Installer

ZYX 是 18 个技能的多技能包，根目录故意没有单个 `SKILL.md`。不要把它当作一个普通技能安装，也不要去 GitHub 搜索“zyx skill”。

## 执行

1. 先确认本技能目录里有 `repo/skills/` 和 `bootstrap.sh`。
2. 在本技能目录执行：

```bash
bash bootstrap.sh
```

不传参数会自动探测宿主 skills 目录，并安装内置技能与外部依赖。只想装技能本体：

```bash
bash bootstrap.sh --no-deps
```

指定目录：

```bash
bash bootstrap.sh --dir ~/.claude/skills
```

3. 安装完成后运行：

```bash
bash repo/skills/zyx/scripts/doctor.sh --full
```

看到「全部就绪」即完成。新开一个对话，直接说「用 ZYX 帮我……」。
EOF

cp "$ROOT/bootstrap.sh" "$TMP/bootstrap.sh"
cp "$ROOT/INSTALL.md" "$TMP/INSTALL.md"
cp "$ROOT/LICENSE" "$TMP/LICENSE"

# 只复制运行所需内容，不带 .git / dist / 依赖缓存
tar -C "$ROOT" \
  --exclude=.git --exclude=dist --exclude=docs \
  --exclude='*.pyc' --exclude='__pycache__' \
  -cf - . | tar -C "$TMP/repo" -xf -

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
