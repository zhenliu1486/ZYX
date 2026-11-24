#!/usr/bin/env python3
"""check-integrity.py — 扫描 Skill 目录内 Markdown 引用的本地文件是否存在。

用法:
  check-integrity.py <skill-dir> [skill-dir ...]

规则：
- 识别 Markdown 链接 `[text](path)` 与行内代码 `` `path` `` 里以已知子目录开头的相对路径。
- 路径相对当前文件所在目录解析；命中后若文件不存在，记为缺失引用。
- 同时校验目录内是否存在 SKILL.md（无 SKILL.md 直接报错）。
退出码：0 无缺失；1 存在缺失；2 用法/脚本错误。
"""
import os
import re
import sys

KNOWN_PREFIXES = ("references/", "shared/", "scripts/", "evals/", "templates/",
                  "rules/", "tests/", "agents/", "assets/", "refs/")

# Markdown 链接括号内路径
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
# 行内代码片段里的相对路径
CODE_RE = re.compile(r"`([^`]+)`")
PATH_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+$")

missing: list[tuple[str, str]] = []
checked_files = 0


def scan_md(md_path: str) -> None:
    global checked_files
    checked_files += 1
    try:
        text = open(md_path, encoding="utf-8").read()
    except Exception:
        return
    base = os.path.dirname(md_path)
    refs: set[str] = set()
    for m in LINK_RE.finditer(text):
        refs.add(m.group(1).strip())
    for m in CODE_RE.finditer(text):
        tok = m.group(1).strip()
        if PATH_RE.match(tok):
            refs.add(tok)
    for ref in refs:
        if ref.startswith("http://") or ref.startswith("https://") or ref.startswith("#"):
            continue
        if not any(ref.startswith(p) for p in KNOWN_PREFIXES):
            continue
        target = os.path.normpath(os.path.join(base, ref))
        if not os.path.exists(target):
            missing.append((md_path, ref))


def scan_dir(skill_dir: str) -> None:
    if not os.path.isdir(skill_dir):
        missing.append((skill_dir, "<目录不存在>"))
        return
    if not os.path.isfile(os.path.join(skill_dir, "SKILL.md")):
        missing.append((skill_dir, "SKILL.md 缺失"))
    prose_docs = {"README.md", "CHANGELOG.md", "changelog.md"}
    for root, _, files in os.walk(skill_dir):
        # 跳过运行态与版本控制目录
        if os.sep + "state" in root or os.sep + ".git" in root:
            continue
        for fn in files:
            # README/CHANGELOG 是散文文档，其中的路径提及不是可执行引用，不做悬空校验
            if fn.endswith(".md") and fn not in prose_docs:
                scan_md(os.path.join(root, fn))


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: check-integrity.py <skill-dir> [skill-dir ...]", file=sys.stderr)
        return 2
    for d in sys.argv[1:]:
        scan_dir(d)
    if missing:
        print(f"完整性检查：发现 {len(missing)} 处问题（扫描 {checked_files} 个 md 文件）")
        for src, ref in missing:
            print(f"  ❌ {os.path.relpath(src)} → {ref}")
        return 1
    print(f"完整性检查通过（扫描 {checked_files} 个 md 文件，无悬空引用）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
