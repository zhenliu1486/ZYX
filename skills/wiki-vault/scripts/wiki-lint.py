#!/usr/bin/env python3
"""wiki-lint.py — R7 wiki-vault 的知识库健康巡检（仅标准库）。

用法：
  python3 wiki-lint.py <vault-root> [--wiki-dir wiki] [--json] [--stale-days 180]

检查项：
  1. frontmatter 缺失或必填字段缺失（type / title）
  2. 断链：[[wikilink]] 指向不存在的页面
  3. 孤儿页：除 index.md / log.md 外，无任何入链
  4. 缺页：被链接指向但不存在的目标出现 ≥3 次（概念被反复提到却没有独立页）
  5. 索引覆盖：页面未出现在 wiki/index.md
  6. 废弃页仍被正常页引用（deprecated: true）
  7. 陈旧页：updated 超过 N 天未更新
  8. 内容过薄：正文少于 50 字符
  9. 矛盾标记统计（> [!contradiction]），仅作仪表盘

设计决策（按用户要求）：
  - **不设覆盖度闸门**：本脚本只输出客观统计与建议，不判定「覆盖不足禁止下结论」，也不以非零退出码阻断流程。
  - 退出码恒为 0（除非参数/路径错误），供人或 LLM 自行判断。
"""

import argparse
import datetime as dt
import json
import os
import re
import sys

WIKILINK = re.compile(r"\[\[([^\[\]]+?)\]\]")
FM_BLOCK = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)
SPECIAL_PAGES = {"index", "log", "hot", "overview"}
FOLDER_TYPE = {
    "sources": "source",
    "entities": "entity",
    "concepts": "concept",
    "comparisons": "comparison",
    "syntheses": "synthesis",
}
REQUIRED_BY_TYPE = {
    "source": ["source_file", "date_ingested"],
    "concept": ["confidence", "cluster"],
    "entity": ["entity_type"],
    "comparison": ["date"],
    "synthesis": ["date"],
}
LOG_LINE = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] (init|ingest|query|lint|sync|note) \|")


def slug_key(text):
    text = text.strip().lower()
    text = text.replace("_", "-").replace(" ", "-")
    text = re.sub(r"-{2,}", "-", text)
    return text.strip("-")


def parse_frontmatter(text):
    m = FM_BLOCK.match(text)
    if not m:
        return {}, text
    raw, body = m.group(1), text[m.end():]
    data = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        key = k.strip()
        val = v.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = [x.strip().strip("'\"") for x in inner.split(",") if x.strip()] if inner else []
        else:
            data[key] = val.strip("'\"")
    return data, body


def collect_pages(wiki_dir):
    pages = {}
    for root, _, files in os.walk(wiki_dir):
        for fn in files:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, wiki_dir)
            stem = os.path.splitext(fn)[0]
            try:
                with open(path, encoding="utf-8") as f:
                    text = f.read()
            except Exception:
                continue
            fm, body = parse_frontmatter(text)
            folder = os.path.basename(os.path.dirname(rel)) if os.path.dirname(rel) else ""
            main = slug_key(fm.get("title", "") or stem)
            pages[rel] = {
                "rel": rel,
                "stem": stem,
                "key": slug_key(stem),
                "title_key": main,
                "dir": folder,
                "frontmatter": fm,
                "body": body,
                "links": [],
                "aliases": [slug_key(a) for a in fm.get("aliases", []) if a] if isinstance(fm.get("aliases"), list) else [],
                "deprecated": str(fm.get("deprecated", "")).lower() in ("true", "1", "yes"),
                "special": stem in SPECIAL_PAGES,
            }
    return pages


def resolve_target(target, pages, by_key):
    """把 [[Target]] 解析到页面 rel；支持 target#heading 与 target|alias。"""
    t = target.split("|", 1)[0].split("#", 1)[0].strip()
    if not t:
        return None
    k = slug_key(t)
    if k in by_key:
        return by_key[k]
    # 支持路径形式 [[concepts/xxx]]
    p = t.strip().replace("\\", "/")
    for rel in pages:
        if slug_key(os.path.splitext(rel)[0]) == slug_key(os.path.splitext(p)[0]):
            return rel
    return None


def main():
    ap = argparse.ArgumentParser(description="R7 wiki-vault 健康巡检")
    ap.add_argument("vault_root")
    ap.add_argument("--wiki-dir", default="wiki")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--stale-days", type=int, default=180)
    ap.add_argument("--min-body", type=int, default=50)
    ap.add_argument("--missing-threshold", type=int, default=3)
    ap.add_argument("--exit-code", action="store_true",
                    help="结构性有问题时返回 1（默认恒 0；不用于覆盖度判定）")
    args = ap.parse_args()

    wiki_dir = os.path.join(os.path.abspath(os.path.expanduser(args.vault_root)), args.wiki_dir)
    if not os.path.isdir(wiki_dir):
        print(f"wiki 目录不存在: {wiki_dir}", file=sys.stderr)
        return 1

    pages = collect_pages(wiki_dir)
    by_key = {}
    for rel, pg in pages.items():
        by_key.setdefault(pg["key"], rel)
        by_key.setdefault(pg["title_key"], rel)
        for a in pg["aliases"]:
            by_key.setdefault(a, rel)

    # 收集出链与入链
    inbound = {rel: set() for rel in pages}
    broken = []
    missing_counter = {}
    for rel, pg in pages.items():
        for raw_target in WIKILINK.findall(pg["body"]):
            tgt = raw_target.split("|", 1)[0].split("#", 1)[0].strip()
            if not tgt:
                continue
            pg["links"].append(tgt)
            resolved = resolve_target(raw_target, pages, by_key)
            if resolved:
                if resolved != rel:
                    inbound[resolved].add(rel)
            else:
                broken.append({"page": rel, "target": tgt})
                k = slug_key(tgt)
                missing_counter[k] = missing_counter.get(k, 0) + 1

    # 同一页对同一目标的重复断链只报一次（出现次数仍计入缺页统计）
    seen_pairs = set()
    unique_broken = []
    for b in broken:
        key = (b["page"], b["target"])
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        unique_broken.append(b)
    broken = unique_broken

    # frontmatter 检查（通用必填 + 按类型必填 + 目录/类型一致）
    missing_fm = []
    for rel, pg in pages.items():
        if pg["special"]:
            continue
        fm = pg["frontmatter"]
        if not fm:
            missing_fm.append({"page": rel, "issue": "无 YAML frontmatter"})
            continue
        if not fm.get("type"):
            missing_fm.append({"page": rel, "issue": "缺 type"})
        if not fm.get("title"):
            missing_fm.append({"page": rel, "issue": "缺 title"})
        ptype = str(fm.get("type", "")).strip()
        expect = FOLDER_TYPE.get(pg["dir"])
        if ptype and expect and ptype != expect:
            missing_fm.append({"page": rel, "issue": f"目录与 type 不一致（{pg['dir']} 应为 {expect}）"})
        for field in REQUIRED_BY_TYPE.get(ptype, []):
            val = fm.get(field, "")
            if not val or val in ("[]", '""'):
                missing_fm.append({"page": rel, "issue": f"缺 {field}"})

    # 孤儿页 / 仅索引引用
    # orphan：任何页面（含 index）都没有指向它 → 真正孤立
    # index_only：只有 index/log 指向它 → 需要与内容页互链
    orphans = []
    index_only = []
    for rel, pg in pages.items():
        if pg["special"]:
            continue
        all_inbound = inbound[rel]
        real_inbound = {x for x in all_inbound if os.path.basename(x) not in ("index.md", "log.md")}
        if not all_inbound:
            orphans.append(rel)
        elif not real_inbound:
            index_only.append(rel)

    # 缺页（>= 阈值）
    missing_pages = [
        {"target": k, "count": c}
        for k, c in sorted(missing_counter.items(), key=lambda x: -x[1])
        if c >= args.missing_threshold
    ]

    # 索引覆盖
    index_path = os.path.join(wiki_dir, "index.md")
    index_text = ""
    if os.path.isfile(index_path):
        with open(index_path, encoding="utf-8") as f:
            index_text = f.read()
    else:
        missing_fm.append({"page": "wiki/index.md", "issue": "主索引缺失"})
    not_in_index = []
    for rel, pg in pages.items():
        if pg["special"]:
            continue
        stem = pg["stem"]
        if stem not in index_text and pg["title_key"] not in index_text.lower():
            not_in_index.append(rel)

    # 废弃页仍被引用（仅检查本身已标 deprecated 的页）
    deprecated_linked = []
    for rel, pg in pages.items():
        if pg["special"] or not pg["deprecated"]:
            continue
        for src in inbound[rel]:
            src_pg = pages.get(src, {})
            if not src_pg.get("deprecated") and not src_pg.get("special"):
                deprecated_linked.append({"deprecated": rel, "linked_from": src})
                break

    # 陈旧页
    stale = []
    today = dt.date.today()
    for rel, pg in pages.items():
        if pg["special"]:
            continue
        upd = pg["frontmatter"].get("updated") or pg["frontmatter"].get("date_ingested") or pg["frontmatter"].get("date")
        if not upd:
            continue
        try:
            d = dt.date.fromisoformat(str(upd)[:10])
        except Exception:
            continue
        age = (today - d).days
        if age > args.stale_days:
            stale.append({"page": rel, "updated": str(upd), "age_days": age})

    # 过薄页
    thin = []
    for rel, pg in pages.items():
        if pg["special"]:
            continue
        if len(re.sub(r"\s+", "", pg["body"])) < args.min_body:
            thin.append(rel)

    # 活动日志格式
    log_issues = []
    if os.path.isfile(os.path.join(wiki_dir, "log.md")):
        with open(os.path.join(wiki_dir, "log.md"), encoding="utf-8") as f:
            for i, line in enumerate(f, 1):
                if line.startswith("## ") and not LOG_LINE.match(line.strip()):
                    log_issues.append({"line": i, "text": line.strip()[:80]})
    else:
        log_issues.append({"line": 0, "text": "wiki/log.md 缺失"})

    # 矛盾标记
    contradictions = []
    for rel, pg in pages.items():
        n = len(re.findall(r">\s*\[!contradiction\]", pg["body"], re.I))
        if n:
            contradictions.append({"page": rel, "count": n})

    result = {
        "vault": os.path.abspath(os.path.expanduser(args.vault_root)),
        "wiki_dir": wiki_dir,
        "pages": len(pages),
        "summary": {
            "broken_links": len(broken),
            "missing_pages": len(missing_pages),
            "orphans": len(orphans),
            "index_only": len(index_only),
            "frontmatter_issues": len(missing_fm),
            "not_in_index": len(not_in_index),
            "deprecated_linked": len(deprecated_linked),
            "stale": len(stale),
            "thin": len(thin),
            "contradictions": sum(c["count"] for c in contradictions),
        "log_issues": len(log_issues),
        },
        "broken_links": broken,
        "missing_pages": missing_pages,
        "orphans": orphans,
        "index_only": index_only,
        "frontmatter_issues": missing_fm,
        "not_in_index": not_in_index,
        "deprecated_linked": deprecated_linked,
        "stale": stale,
        "thin": thin,
        "contradictions": contradictions,
        "log_issues": log_issues,
        "note": "仅统计，不阻断结论（R7 不设覆盖度闸门）；由人或 LLM 决定优先修哪几项。",
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    s = result["summary"]
    print(f"# 知识库健康报告 — {dt.date.today().isoformat()}")
    print(f"\n库：{result['vault']}\n页面数：{result['pages']}")
    print("\n## 概览")
    print(f"- 断链：{s['broken_links']}")
    print(f"- 缺页（被提及 ≥{args.missing_threshold} 次）：{s['missing_pages']}")
    print(f"- 孤儿页（零入链）：{s['orphans']}")
    print(f"- 仅索引引用（缺内容页互链）：{s['index_only']}")
    print(f"- frontmatter 问题：{s['frontmatter_issues']}")
    print(f"- 未进索引：{s['not_in_index']}")
    print(f"- 废弃页仍被引用：{s['deprecated_linked']}")
    print(f"- 陈旧页（>{args.stale_days} 天）：{s['stale']}")
    print(f"- 过薄页：{s['thin']}")
    print(f"- 矛盾标记：{s['contradictions']}")
    print(f"- 日志格式问题：{s['log_issues']}")

    def section(title, items, fmt):
        if not items:
            return
        print(f"\n## {title}")
        for it in items:
            print(f"- {fmt(it)}")

    section("断链", broken, lambda x: f"`{x['page']}` → `[[{x['target']}]]`（目标不存在）")
    section("缺页（建议补独立页）", missing_pages, lambda x: f"`{x['target']}` 被提及 {x['count']} 次")
    section("孤儿页（零入链）", orphans, lambda x: f"`{x}`")
    section("仅索引引用（补内容页互链）", index_only, lambda x: f"`{x}`")
    section("frontmatter 问题", missing_fm, lambda x: f"`{x['page']}`：{x['issue']}")
    section("未进索引", not_in_index, lambda x: f"`{x}`")
    section("废弃页仍被引用", deprecated_linked, lambda x: f"`{x['deprecated']}` ← `{x['linked_from']}`")
    section("陈旧页", stale, lambda x: f"`{x['page']}`（updated {x['updated']}，{x['age_days']} 天）")
    section("过薄页", thin, lambda x: f"`{x}`")
    section("矛盾标记", contradictions, lambda x: f"`{x['page']}` × {x['count']}")
    section("日志格式问题", log_issues, lambda x: f"第 {x['line']} 行：`{x['text']}`")

    print("\n## 建议下一步")
    print("1. 先修断链与 frontmatter，保证图谱可遍历。")
    print("2. 再补「缺页」里被反复提到的概念，每页至少与 2 个已有页互链。")
    print("3. 孤儿页二选一：接到相关概念，或标记 deprecated（不删除）；仅索引引用的页补 2 条内容页互链。")
    print("4. 陈旧页按新来源复核；矛盾处保留分歧并用 `> [!contradiction]` 标注依据。")
    print("\n> 本报告只做客观统计，不判定「覆盖不足禁止下结论」；是否可用由使用者判断。")
    if args.exit_code:
        structural = (
            s["broken_links"] + s["frontmatter_issues"] + s["log_issues"]
            + s["missing_pages"] + s["orphans"] + s["deprecated_linked"]
        )
        return 1 if structural else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
