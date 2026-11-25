#!/usr/bin/env python3
"""wiki.py — R7 wiki-vault 的库注册表、单写锁、骨架生成与日志工具（仅标准库）。

子命令：
  init <slug> [--topic T] [--root PATH] [--provision]
      新建一个受管库（豆包环境默认 ~/Doubao/wiki/<slug>，其他宿主 <桌面>/zyx-output/wiki/<slug>），生成 raw/ 与 wiki/ 骨架。
  mount <slug> <path> [--topic T] [--provision]
      挂载一个已存在的 Obsidian 库目录（不搬动、不重构用户既有目录）。
  list [--plain|--json]
  resolve [<slug>]
  use <slug>
  status [--json]
  lock <slug> [--force]
  unlock <slug>
  new-page <type> <slug> [--title T] [--vault SLUG] [--force]
  log <op> <title> [--vault SLUG] [--date YYYY-MM-DD] [--detail TEXT] [--force]
  context [--install|--remove] [--dir D] [--json]
      把活动库状态投影成 zyx-context 技能卡，安装/移除到宿主 skills 目录。

约定：
- 一个库 = 一个目录（通常是 Obsidian vault）；库内结构见 references/vault-layout.md。
- 运行态注册表落在 zyx/state/vaults.json（不进发布包）；可用 ZYX_STATE_DIR 覆盖。
- 单写规则：同一库同一时刻只允许一个写会话；lock 以原子 mkdir 互斥，默认 12 小时视为陈旧锁。
- 只写 Obsidian Markdown；不生成 HTML、不内置插件配置。
"""

import argparse
import datetime as dt
import getpass
import json
import os
import re
import shlex
import shutil
import socket
import subprocess
import sys
import time

LOCK_TTL_HOURS = float(os.environ.get("WIKI_LOCK_TTL_HOURS", "12"))

RAW_SUBDIRS = ["articles", "papers", "transcripts", "data", "assets"]
WIKI_SUBDIRS = ["sources", "entities", "concepts", "comparisons", "syntheses"]
TYPE_DIR = {
    "source": "sources",
    "entity": "entities",
    "concept": "concepts",
    "comparison": "comparisons",
    "synthesis": "syntheses",
}
LOG_OPS = {"init", "ingest", "query", "lint", "sync", "note"}


# ---------------------------------------------------------------- 基础路径

def skill_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def zyx_dir():
    """返回同机 zyx 目录；找不到返回 None。"""
    env = os.environ.get("ZYX_SKILL_DIR")
    if env and os.path.isfile(os.path.join(env, "SKILL.md")):
        return env
    cand = os.path.normpath(os.path.join(skill_dir(), "..", "zyx"))
    if os.path.isfile(os.path.join(cand, "SKILL.md")):
        return cand
    return None


def state_dir():
    env = os.environ.get("ZYX_STATE_DIR")
    if env:
        return os.path.abspath(env)
    z = zyx_dir()
    if z:
        return os.path.join(z, "state")
    return os.path.join(os.path.expanduser("~"), ".zyx", "state")


def registry_path():
    return os.path.join(state_dir(), "vaults.json")


def lock_root():
    return os.path.join(state_dir(), "locks")


def is_doubao_env():
    """是否运行在豆包 Agent 环境（云端工作区）。"""
    if any(os.environ.get(k) for k in ("DOUBAO_SANDBOX_TYPE", "DOUBAO_OFFICE_AGENT_NAME", "DOUBAO_VERSION")):
        return True
    return os.path.isdir(os.path.expanduser("~/Doubao"))


def default_wiki_home():
    """默认库根：显式 ZYX_WIKI_HOME > 豆包 ~/Doubao/wiki > 桌面 zyx-output/wiki。"""
    env = os.environ.get("ZYX_WIKI_HOME")
    if env:
        return os.path.abspath(os.path.expanduser(env))
    if is_doubao_env():
        return os.path.expanduser("~/Doubao/wiki")
    return os.path.join(desktop_output_root(), "wiki")


def desktop_output_root():
    z = zyx_dir()
    if z:
        script = os.path.join(z, "scripts", "desktop-dir.sh")
        if os.path.isfile(script):
            try:
                out = subprocess.check_output(["bash", script], text=True).strip()
                if out:
                    return out
            except Exception:
                pass
    home = os.path.expanduser("~")
    for cand in (os.path.join(home, "Desktop"), os.path.join(home, "Documents"), home):
        if os.path.isdir(cand):
            return os.path.join(cand, "zyx-output")
    return os.path.join(home, "zyx-output")


def slugify(text):
    s = text.strip().lower()
    s = re.sub(r"[\s/\\]+", "-", s)
    s = re.sub(r"[^a-z0-9\u4e00-\u9fff-]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s


def today():
    return dt.date.today().isoformat()


def now_iso():
    return dt.datetime.now().replace(microsecond=0).isoformat()


# ---------------------------------------------------------------- 注册表

def load_registry():
    p = registry_path()
    if not os.path.isfile(p):
        return {"schema_version": 1, "active": None, "vaults": []}
    try:
        with open(p, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        print(f"注册表损坏，无法解析: {p}", file=sys.stderr)
        sys.exit(2)
    data.setdefault("vaults", [])
    data.setdefault("active", None)
    return data


def save_registry(data):
    p = registry_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, p)


def find_vault(data, slug):
    for v in data["vaults"]:
        if v["slug"] == slug:
            return v
    return None


def active_vault(data, slug=None):
    if slug:
        v = find_vault(data, slug)
        if not v:
            print(f"未注册的库: {slug}（先 init 或 mount）", file=sys.stderr)
            sys.exit(1)
        return v
    cur = data.get("active")
    if cur:
        v = find_vault(data, cur)
        if v:
            return v
    if len(data["vaults"]) == 1:
        return data["vaults"][0]
    print("没有活动库：先用 `use <slug>` 指定，或显式传 --vault <slug>。", file=sys.stderr)
    sys.exit(1)


def touch(vault):
    vault["last_used_at"] = now_iso()


# ---------------------------------------------------------------- 骨架

INDEX_TEMPLATE = """# 知识库索引

> 主目录：每次摄入、新建页面或归档后更新本文件。按集群分节列出页面，一行一页。

## 集群：未分类

| 页面 | 类型 | 一句话说明 |
|---|---|---|
"""

LOG_TEMPLATE = """# 活动日志

> 只追加，不删改。每条格式：`## [YYYY-MM-DD] ingest|query|lint|init|sync|note | 标题`

"""

HOT_TEMPLATE = """# 会话热缓存

> 约 500 字以内。每次会话开始先读这里；每次摄入后重写，只保留当前最相关的上下文与未决问题。

"""

OVERVIEW_TEMPLATE = """# 全库综述

> 全库层面的高层综合。大规模摄入或集群调整后修订。

"""

SCHEMA_TEMPLATE = """# 本库约定（schema）

> 本文件由 ZYX R7 wiki-vault 生成，可与人共同迭代；换宿主时复制为 CLAUDE.md / AGENTS.md 即可生效。

## 结构

- `raw/`：原始材料，只读，任何人不得修改或删除。
- `wiki/`：知识层，LLM 负责写入与维护，人只读浏览。
- `wiki/index.md` 主索引：每次摄入必须更新。
- `wiki/log.md` 活动日志：只追加。
- `wiki/hot.md` 会话热缓存：会话开始先读。
- `wiki/overview.md` 全库综述：重大变更后修订。

## 硬约束

1. 永不写入或删除 `raw/`。
2. 不删除 wiki 页；废弃只在 frontmatter 标 `deprecated: true`。
3. 每次写入都更新 `index.md` 与 `log.md`。
4. 新页面至少与 2 个已有页面互相链接。
5. 同一时刻只有一个写会话；写前取锁，写完释放。
6. 只在库内使用 Obsidian Markdown：`[[wikilink]]`、YAML frontmatter、`> [!note]` 类 callout。
"""

PAGE_BODY = {
    "source": """
## 摘要

## 关键要点

## 与已有知识的增量

- 推翻：
- 加深：
- 新增：

## 矛盾与待核查

## 引用与元数据
""",
    "entity": """
## 是什么

## 与知识库的关系

## 关联概念

## 待解问题
""",
    "concept": """
## 定义

## 怎么做（可执行步骤）

## 适用条件与反例

## 与其他概念的关系
""",
    "comparison": """
## 对比对象

## 维度对照

| 维度 | A | B |
|---|---|---|
|  |  |  |

## 结论与适用场景

## 回链
""",
    "synthesis": """
## 问题

## 综合结论

## 证据链

## 边界与未决
""",
}


def page_frontmatter(ptype, title, slug):
    d = today()
    if ptype == "source":
        return (
            "---\n"
            "type: source\n"
            f'title: "{title}"\n'
            f"slug: summary-{slug}\n"
            "source_file: raw/articles/<文件名>\n"
            'author: ""\n'
            'date_published: ""\n'
            f"date_ingested: {d}\n"
            "key_claims: []\n"
            "related: []\n"
            "confidence: low\n"
            "---\n"
        )
    if ptype == "entity":
        return (
            "---\n"
            "type: entity\n"
            "entity_type: person\n"
            f'title: "{title}"\n'
            "sources: []\n"
            "related: []\n"
            f"created: {d}\n"
            f"updated: {d}\n"
            'cluster: ""\n'
            "contradictions: []\n"
            "open_questions: []\n"
            "---\n"
        )
    if ptype == "concept":
        return (
            "---\n"
            "type: concept\n"
            f'title: "{title}"\n'
            "aliases: []\n"
            "sources: []\n"
            "related: []\n"
            f"created: {d}\n"
            f"updated: {d}\n"
            "confidence: low\n"
            'cluster: ""\n'
            "cluster_role: member\n"
            "---\n"
        )
    if ptype == "comparison":
        return (
            "---\n"
            "type: comparison\n"
            f'title: "{title}"\n'
            "sources: []\n"
            "related: []\n"
            "filed_from_query: true\n"
            f"date: {d}\n"
            "---\n"
        )
    return (
        "---\n"
        "type: synthesis\n"
        f'title: "{title}"\n'
        "sources: []\n"
        "related: []\n"
        "filed_from_query: true\n"
        f"date: {d}\n"
        "---\n"
    )


def provision(root, raw_name="raw", wiki_name="wiki"):
    raw = os.path.join(root, raw_name)
    wiki = os.path.join(root, wiki_name)
    created = []
    for sub in RAW_SUBDIRS:
        p = os.path.join(raw, sub)
        if not os.path.isdir(p):
            os.makedirs(p, exist_ok=True)
            created.append(os.path.relpath(p, root))
    for sub in WIKI_SUBDIRS:
        p = os.path.join(wiki, sub)
        if not os.path.isdir(p):
            os.makedirs(p, exist_ok=True)
            created.append(os.path.relpath(p, root))
    seeds = {
        os.path.join(wiki, "index.md"): INDEX_TEMPLATE,
        os.path.join(wiki, "log.md"): LOG_TEMPLATE,
        os.path.join(wiki, "hot.md"): HOT_TEMPLATE,
        os.path.join(wiki, "overview.md"): OVERVIEW_TEMPLATE,
        os.path.join(root, "schema.md"): SCHEMA_TEMPLATE,
    }
    for path, text in seeds.items():
        if not os.path.isfile(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(text.lstrip("\n"))
            created.append(os.path.relpath(path, root))
    return created


def inspect_root(root, raw_name="raw", wiki_name="wiki"):
    return {
        "obsidian": os.path.isdir(os.path.join(root, ".obsidian")),
        "raw": os.path.isdir(os.path.join(root, raw_name)),
        "wiki": os.path.isdir(os.path.join(root, wiki_name)),
        "layout_ready": os.path.isdir(os.path.join(root, raw_name))
        and os.path.isfile(os.path.join(root, wiki_name, "index.md")),
    }


# ---------------------------------------------------------------- 锁

def lock_dir(slug):
    return os.path.join(lock_root(), f"{slug}.lock")


def read_lock(slug):
    d = lock_dir(slug)
    if not os.path.isdir(d):
        return None
    info = {"path": d, "age_hours": None}
    f = os.path.join(d, "owner.json")
    if os.path.isfile(f):
        try:
            with open(f, encoding="utf-8") as fh:
                info.update(json.load(fh))
        except Exception:
            pass
    try:
        info["age_hours"] = round((time.time() - os.path.getmtime(d)) / 3600, 2)
    except Exception:
        pass
    return info


def owner_token():
    """写锁持有者标识：默认「用户@主机」，多会话并行时用 WIKI_SESSION_ID 区分。

    锁是会话租约（session lease）而不是进程互斥：一次 lock 之后，同一会话的多次
    命令（new-page / log / 手写页面）都可写入；不同会话会拿到不同的 token。
    """
    env = os.environ.get("WIKI_SESSION_ID")
    if env:
        return env.strip()
    try:
        user = getpass.getuser()
    except Exception:
        user = "user"
    return f"{user}@{socket.gethostname()}"


def require_lock(vault, force=False):
    """写操作前检查单写锁；未取得锁或锁属其他会话则拒绝（禁止并发写同一库）。"""
    if force or os.environ.get("WIKI_ALLOW_UNLOCKED") == "1":
        return
    info = read_lock(vault["slug"])
    if not info:
        print(
            f"未取得写锁：先执行 `python3 scripts/wiki.py lock {vault['slug']}`，"
            f"写完 `unlock {vault['slug']}`。单库同一时刻只允许一个写会话。",
            file=sys.stderr,
        )
        sys.exit(5)
    owner = info.get("owner")
    if owner and owner != owner_token():
        print(
            f"库 {vault['slug']} 已被其他会话持锁（owner={owner}，pid={info.get('pid')}）。"
            f"禁止并行写，等对方释放或确认陈旧后 --force 接管。",
            file=sys.stderr,
        )
        sys.exit(5)


# ---------------------------------------------------------------- 命令

def cmd_init(args):
    slug = slugify(args.slug)
    if not slug:
        print("slug 不合法", file=sys.stderr)
        return 1
    data = load_registry()
    if find_vault(data, slug):
        print(f"库已存在: {slug}", file=sys.stderr)
        return 1
    root = os.path.abspath(args.root) if args.root else os.path.join(
        default_wiki_home(), slug
    )
    os.makedirs(root, exist_ok=True)
    created = provision(root, args.raw_dir, args.wiki_dir)
    info = inspect_root(root, args.raw_dir, args.wiki_dir)
    entry = {
        "slug": slug,
        "root": root,
        "topic": args.topic or "",
        "mode": "managed",
        "obsidian": info["obsidian"],
        "raw_dir": args.raw_dir,
        "wiki_dir": args.wiki_dir,
        "layout_ready": info["layout_ready"],
        "created_at": now_iso(),
        "last_used_at": now_iso(),
    }
    data["vaults"].append(entry)
    if not data.get("active"):
        data["active"] = slug
    save_registry(data)
    refresh_context_cards(data, data.get("active") or slug)
    print(f"已建库: {slug}")
    print(f"根目录: {root}")
    print(f"活动库: {data.get('active')}")
    if created:
        print("已创建: " + ", ".join(created))
    return 0


def cmd_mount(args):
    slug = slugify(args.slug)
    if not slug:
        print("slug 不合法", file=sys.stderr)
        return 1
    root = os.path.abspath(os.path.expanduser(args.path))
    if not os.path.isdir(root):
        print(f"目录不存在: {root}", file=sys.stderr)
        return 1
    data = load_registry()
    if find_vault(data, slug):
        print(f"库已存在: {slug}；如需换路径先手动从注册表移除。", file=sys.stderr)
        return 1
    created = []
    if args.provision:
        created = provision(root, args.raw_dir, args.wiki_dir)
    info = inspect_root(root, args.raw_dir, args.wiki_dir)
    entry = {
        "slug": slug,
        "root": root,
        "topic": args.topic or "",
        "mode": "mounted",
        "obsidian": info["obsidian"],
        "raw_dir": args.raw_dir,
        "wiki_dir": args.wiki_dir,
        "layout_ready": info["layout_ready"],
        "created_at": now_iso(),
        "last_used_at": now_iso(),
    }
    data["vaults"].append(entry)
    if not data.get("active"):
        data["active"] = slug
    save_registry(data)
    refresh_context_cards(data, data.get("active") or slug)
    print(f"已挂载: {slug} → {root}")
    print(f"Obsidian 库: {'是' if info['obsidian'] else '否（普通 Markdown 目录也可用）'}")
    print(f"raw/: {'有' if info['raw'] else '无'}｜wiki/: {'有' if info['wiki'] else '无'}")
    if not info["layout_ready"]:
        print("⚠ 现有目录尚未满足 raw/ + wiki/index.md 约定；不要挪动用户既有文件，"
              "可加 --provision 只补建缺失骨架，或按 references/vault-layout.md 手动对齐。")
    if created:
        print("已补建: " + ", ".join(created))
    return 0


def cmd_list(args):
    data = load_registry()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    if args.plain:
        for v in data["vaults"]:
            print(v["slug"])
        return 0
    if not data["vaults"]:
        print("尚未注册任何库。用 init <slug> 新建，或 mount <slug> <已有Obsidian库路径>。")
        return 0
    print(f"活动库: {data.get('active') or '（未设置）'}")
    for v in data["vaults"]:
        mark = "*" if v["slug"] == data.get("active") else " "
        obs = "obsidian" if v.get("obsidian") else "markdown"
        ready = "ready" if v.get("layout_ready") else "未对齐"
        print(f"{mark} {v['slug']}\t{v['mode']}\t{obs}\t{ready}\t{v['root']}")
    return 0


def cmd_resolve(args):
    data = load_registry()
    v = active_vault(data, args.slug)
    print(v["root"])
    return 0


def cmd_use(args):
    data = load_registry()
    v = find_vault(data, slugify(args.slug))
    if not v:
        print(f"未注册的库: {args.slug}", file=sys.stderr)
        return 1
    data["active"] = v["slug"]
    touch(v)
    save_registry(data)
    refreshed = refresh_context_cards(data, v["slug"])
    print(f"活动库已切换: {v['slug']} → {v['root']}")
    if refreshed:
        print(f"已同步 context 卡: {len(refreshed)} 处")
    return 0


def cmd_status(args):
    data = load_registry()
    items = []
    for v in data["vaults"]:
        info = read_lock(v["slug"])
        item = {
            "slug": v["slug"],
            "root": v["root"],
            "active": v["slug"] == data.get("active"),
            "layout_ready": v.get("layout_ready"),
            "lock": None,
        }
        if info:
            item["lock"] = {
                "pid": info.get("pid"),
                "host": info.get("host"),
                "started_at": info.get("started_at"),
                "age_hours": info.get("age_hours"),
                "stale": (info.get("age_hours") or 0) > LOCK_TTL_HOURS,
            }
        items.append(item)
    if args.json:
        print(json.dumps({"active": data.get("active"), "vaults": items}, ensure_ascii=False, indent=2))
        return 0
    if not items:
        print("尚未注册任何库。")
        return 0
    for it in items:
        mark = "*" if it["active"] else " "
        lock = "解锁" if not it["lock"] else f"持锁 pid={it['lock'].get('pid')} 已 {it['lock'].get('age_hours')}h"
        if it["lock"] and it["lock"]["stale"]:
            lock += "（陈旧，可 --force 接管）"
        print(f"{mark} {it['slug']}\t{lock}\t{it['root']}")
    return 0


def cmd_lock(args):
    slug = slugify(args.slug)
    d = lock_dir(slug)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    existing = read_lock(slug)
    if existing:
        same = existing.get("owner") == owner_token()
        if not same and not args.force:
            print(
                f"库 {slug} 已被其他会话持锁（owner={existing.get('owner')}，pid={existing.get('pid')}，"
                f"{existing.get('age_hours')}h）。禁止并行写；确认陈旧后用 --force 接管。",
                file=sys.stderr,
            )
            return 3
        if same and not args.force:
            # 同一会话续租：刷新时间戳，避免长任务被误判陈旧
            with open(os.path.join(d, "owner.json"), "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "owner": owner_token(),
                        "pid": os.getpid(),
                        "host": socket.gethostname(),
                        "started_at": existing.get("started_at") or now_iso(),
                        "renewed_at": now_iso(),
                        "note": args.note or existing.get("note", ""),
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )
            os.utime(d, None)
            print(f"已续租写锁: {slug}（owner={owner_token()}，pid={os.getpid()}）。")
            return 0
        if args.force:
            shutil.rmtree(d, ignore_errors=True)
    try:
        os.mkdir(d)
    except FileExistsError:
        print(f"抢锁失败（并发竞争）: {slug}", file=sys.stderr)
        return 3
    with open(os.path.join(d, "owner.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "owner": owner_token(),
                "pid": os.getpid(),
                "host": socket.gethostname(),
                "started_at": now_iso(),
                "note": args.note or "",
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"已取得写锁: {slug}（owner={owner_token()}，pid={os.getpid()}）。写完请 unlock。")
    return 0


def cmd_unlock(args):
    slug = slugify(args.slug)
    d = lock_dir(slug)
    if not os.path.isdir(d):
        print(f"库 {slug} 当前无锁。")
        return 0
    shutil.rmtree(d, ignore_errors=True)
    print(f"已释放写锁: {slug}")
    return 0


def cmd_new_page(args):
    ptype = args.type
    if ptype not in TYPE_DIR:
        print(f"未知页面类型: {ptype}（可选: {', '.join(TYPE_DIR)}）", file=sys.stderr)
        return 1
    data = load_registry()
    v = active_vault(data, args.vault)
    require_lock(v, args.force)
    slug = slugify(args.slug)
    if not slug:
        print("slug 不合法", file=sys.stderr)
        return 1
    title = args.title or slug
    path = write_new_page(v, ptype, slug, title)
    if not path:
        print(f"页面已存在，按「不删除、不覆盖」约定拒绝写入: {slug}", file=sys.stderr)
        return 4
    linked = []
    for target in getattr(args, "link_to", None) or []:
        tp = find_page(v, target)
        if tp:
            add_see_also(path, os.path.splitext(os.path.basename(tp))[0])
            linked.append(os.path.splitext(os.path.basename(tp))[0])
    if getattr(args, "backlink", False):
        for name in linked:
            tp = find_page(v, name)
            if tp:
                add_see_also(tp, slug)
    touch(v)
    save_registry(data)
    print(f"已建页: {path}")
    if linked:
        print("已建立链接: " + ", ".join(f"[[{x}]]" for x in linked) + ("（含双向回链）" if args.backlink else ""))
    print("下一步：补 frontmatter 字段与正文，并把该页链接进 index.md 和至少 2 个相关页面。")
    return 0


def cmd_log(args):
    if args.op not in LOG_OPS:
        print(f"未知操作类型: {args.op}（可选: {', '.join(sorted(LOG_OPS))}）", file=sys.stderr)
        return 1
    data = load_registry()
    v = active_vault(data, args.vault)
    require_lock(v, args.force)
    wiki = os.path.join(v["root"], v.get("wiki_dir", "wiki"))
    os.makedirs(wiki, exist_ok=True)
    log = os.path.join(wiki, "log.md")
    if not os.path.isfile(log):
        with open(log, "w", encoding="utf-8") as f:
            f.write(LOG_TEMPLATE.lstrip("\n"))
    entry = f"\n## [{args.date or today()}] {args.op} | {args.title}\n"
    if args.detail:
        entry += f"{args.detail.rstrip()}\n"
    with open(log, "a", encoding="utf-8") as f:
        f.write(entry)
    touch(v)
    save_registry(data)
    print(f"已追加日志: {log}")
    return 0


def read_front_matter(path):
    """极简 frontmatter 读取：只取标量与方括号列表，用于简报统计。"""
    try:
        text = open(path, encoding="utf-8").read()
    except Exception:
        return {}, ""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip().strip("'\"")
    return fm, text[m.end():]


def cmd_where(args):
    data = load_registry()
    v = active_vault(data, args.vault)
    if args.json:
        print(json.dumps({k: v.get(k) for k in ("slug", "root", "topic", "mode", "obsidian", "wiki_dir")}, ensure_ascii=False, indent=2))
        return 0
    print(f"slug: {v['slug']}")
    print(f"root: {v['root']}")
    print(f"topic: {v.get('topic') or '（未设置）'}")
    print(f"mode: {v.get('mode')}｜wiki_dir: {v.get('wiki_dir', 'wiki')}")
    return 0


def cmd_brief(args):
    data = load_registry()
    v = active_vault(data, args.vault)
    counts = {}
    for path in iter_pages(v):
        if os.path.basename(path) in ("index.md", "log.md", "hot.md", "overview.md"):
            continue
        fm, _ = read_front_matter(path)
        t = fm.get("type") or "unknown"
        counts[t] = counts.get(t, 0) + 1
    total = sum(counts.values())
    labels = [("concept", "概念"), ("entity", "实体"), ("source", "来源"), ("comparison", "对比"), ("synthesis", "综述")]
    parts = [f"{cn}{counts.get(en, 0)}" for en, cn in labels if counts.get(en, 0)]
    if counts.get("unknown"):
        parts.append(f"未标类型{counts['unknown']}")
    log_path = os.path.join(wiki_root(v), "log.md")
    recent = []
    if os.path.isfile(log_path):
        for line in open(log_path, encoding="utf-8"):
            if line.startswith("## ["):
                recent.append(line.strip().lstrip("# ").strip())
    hot_path = os.path.join(wiki_root(v), "hot.md")
    hot = ""
    if os.path.isfile(hot_path):
        for line in open(hot_path, encoding="utf-8"):
            t = line.strip()
            if t and not t.startswith("#") and not t.startswith(">"):
                hot = t
                break
    lines = [
        f"# 知识库简报 · {v['slug']}",
        f"主题：{v.get('topic') or '未设置'}",
        f"页面：{total}" + (f"（{'｜'.join(parts)}）" if parts else ""),
    ]
    if recent:
        lines.append("最近：" + "；".join(recent[-2:]))
    if hot:
        lines.append("热缓存：" + hot[:160])
    if args.with_lint:
        try:
            out = subprocess.check_output(
                [sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "wiki-lint.py"), v["root"], "--json"],
                text=True, stderr=subprocess.DEVNULL, timeout=30,
            )
            sm = json.loads(out).get("summary", {})
            lines.append(
                f"巡检：断链 {sm.get('broken_links', 0)}｜缺页 {sm.get('missing_pages', 0)}"
                f"｜孤儿 {sm.get('orphans', 0)}｜未进索引 {sm.get('not_in_index', 0)}"
            )
        except Exception:
            lines.append("巡检：暂时不可用")
    lines.append(f"位置：{v['root']}")
    text = "\n".join(lines)
    if args.json:
        print(json.dumps({"slug": v["slug"], "root": v["root"], "topic": v.get("topic", ""), "counts": counts,
                          "recent": recent[-2:], "hot": hot[:160], "text": text}, ensure_ascii=False, indent=2))
        return 0
    print(text[: args.max_chars])
    return 0


CONTEXT_SKILL_NAME = "zyx-context"
CONTEXT_MARKER = "<!-- zyx-context-card: managed"


def context_host_dirs(explicit=None):
    """Context 卡的目标目录：--dir > ZYX_CONTEXT_DIRS > ~/.agents/skills + 已存在的宿主 skills 目录。"""
    home = os.path.expanduser("~")
    dirs = []
    if explicit:
        dirs.extend(os.path.expanduser(d) for d in explicit)
    else:
        env = os.environ.get("ZYX_CONTEXT_DIRS")
        if env:
            dirs.extend(d for d in env.split(os.pathsep) if d)
        else:
            dirs.append(os.path.join(home, ".agents", "skills"))
            for rel in (
                ".claude/skills",
                ".openclaw/skills",
                ".codex/skills",
                ".doubao/agent_mode/workspace/.user_skills",
                ".gemini/skills",
                ".kiro/skills",
                ".qwen/skills",
                ".grok/skills",
                ".hermes/skills",
            ):
                p = os.path.join(home, rel)
                if os.path.isdir(p):
                    dirs.append(p)
    out, seen = [], set()
    for d in dirs:
        if not d:
            continue
        d = os.path.abspath(d)
        rp = os.path.realpath(d)
        if rp in seen:
            continue
        seen.add(rp)
        out.append(d)
    return out


def context_card(v, generated=None):
    """把活动库的状态投影成一张 8–12 行的宿主技能卡。"""
    topic = (v.get("topic") or v["slug"]).replace("|", "\\|")
    root = str(v.get("root") or "").replace("|", "\\|")
    desc = re.sub(r"\s+", " ", f"读取「{topic}」长期知识库（{v['slug']}）的简报；用户提到「我的知识库 / 我库里 / 接着上次的库 / 我的 wiki」或需要长期背景时先用。")
    qpy = shlex.quote(os.path.abspath(__file__))
    qslug = shlex.quote(v["slug"])
    generated = generated or dt.date.today().isoformat()
    return f"""---
name: {CONTEXT_SKILL_NAME}
description: >
  {desc}
---
# 知识库上下文 · {topic}

这是我在本机的个人长期知识库。先读简报，再决定是否检索页面。

| 项 | 值 |
|---|---|
| 库名 | `{v['slug']}` |
| 位置 | `{root}` |
| 主题 | {topic} |
| 生成时间 | {generated} |

## 先读简报

```bash
python3 {qpy} brief --vault {qslug} --with-lint
```

只想知道规模时去掉 `--with-lint`。

## 再检索

```bash
python3 {qpy} search "<关键词>" --vault {qslug}
```

## 规则

- 先简报，后检索；回答带页面标题或 `[[页面名]]`。
- 只读命中的 1–3 页，不把整库贴进上下文。
- 写入前先 `lock`，写完 `unlock`；不并行写。
- 库里没有就说「库里还没有」，不要用常识补。

<!-- zyx-context-card: managed; slug={v['slug']}; regenerate: python3 {qpy} context --install -->
"""


def context_card_path(target):
    return os.path.join(target, CONTEXT_SKILL_NAME, "SKILL.md")


def read_text(path):
    try:
        return open(path, encoding="utf-8").read()
    except Exception:
        return ""


def is_managed_card(path):
    return CONTEXT_MARKER in read_text(path)


def context_conflict(target):
    """目标已有 zyx-context 目录/文件但不是托管卡 → 返回冲突路径，否则空串。"""
    path = context_card_path(target)
    skill_dir = os.path.dirname(path)
    if os.path.isdir(skill_dir):
        if not os.path.isfile(path) or not is_managed_card(path):
            return path
    elif os.path.exists(skill_dir):
        # 同名位置是个文件/symlink 到文件，不是目录
        return skill_dir
    return ""


def write_context_card(target, content):
    path = context_card_path(target)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(content)
    os.replace(tmp, path)
    return path


def refresh_context_cards(data, slug):
    """只刷新已存在的托管卡，不新装；切换活动库后避免旧卡指向旧库。"""
    v = find_vault(data, slug)
    if not v:
        return []
    content = context_card(v)
    written = []
    for target in context_host_dirs(None):
        path = context_card_path(target)
        if os.path.isfile(path) and is_managed_card(path):
            try:
                write_context_card(target, content)
                written.append(path)
            except Exception as e:
                print(f"⚠ context 卡刷新失败（{path}）：{e}", file=sys.stderr)
    return written


def cmd_context(args):
    if args.install and args.remove:
        print("--install 与 --remove 不能同时用", file=sys.stderr)
        return 2
    data = load_registry()
    targets = context_host_dirs(args.dir or None)
    if not targets:
        print("没有可用的宿主 skills 目录；用 --dir 指定一个", file=sys.stderr)
        return 1

    if args.remove:
        removed, skipped = [], []
        for target in targets:
            path = context_card_path(target)
            if not os.path.isfile(path):
                continue
            if not is_managed_card(path):
                skipped.append(path)
                continue
            os.remove(path)
            parent = os.path.dirname(path)
            try:
                os.rmdir(parent)
            except OSError:
                pass
            removed.append(path)
        if args.json:
            print(json.dumps({"action": "remove", "removed": removed, "skipped": skipped}, ensure_ascii=False, indent=2))
        else:
            for p in removed:
                print(f"已删除: {p}")
            for p in skipped:
                print(f"跳过（非 ZYX 托管，未删除）: {p}")
            if not removed and not skipped:
                print("没有已安装的 context 卡。")
        return 0

    v = active_vault(data, args.vault)
    content = context_card(v)
    if args.install:
        conflicts = [p for p in (context_conflict(t) for t in targets) if p]
        if conflicts:
            print("目标位置已有非 ZYX 托管的同名技能，未覆盖：", file=sys.stderr)
            for p in conflicts:
                print(f"  {p}", file=sys.stderr)
            print("先手动移走该目录，或改用 --dir 指定其他目录。", file=sys.stderr)
            return 1
        paths = []
        for t in targets:
            try:
                paths.append(write_context_card(t, content))
            except Exception as e:
                print(f"安装 context 卡失败（{t}）：{e}", file=sys.stderr)
                return 1
        if args.json:
            print(json.dumps({"action": "install", "name": CONTEXT_SKILL_NAME, "slug": v["slug"],
                              "root": v["root"], "paths": paths}, ensure_ascii=False, indent=2))
        else:
            print(f"已安装 context 卡: {CONTEXT_SKILL_NAME}（{v['slug']}）")
            for p in paths:
                print(f"  → {p}")
        return 0

    if args.json:
        print(json.dumps({"action": "preview", "name": CONTEXT_SKILL_NAME, "slug": v["slug"],
                          "root": v["root"], "targets": targets, "content": content}, ensure_ascii=False, indent=2))
    else:
        print(content)
    return 0


# ---------------------------------------------------------------- 页面级操作

SEE_ALSO_HEADING = "## 关联（自动回链）"


def wiki_root(vault):
    return os.path.join(vault["root"], vault.get("wiki_dir", "wiki"))


def iter_pages(vault):
    root = wiki_root(vault)
    for cur, _, files in os.walk(root):
        for fn in files:
            if fn.endswith(".md"):
                yield os.path.join(cur, fn)


def find_page(vault, target):
    """按 stem 或 title 在库内定位页面；target 可带类型前缀 `concepts/xxx`。"""
    t = target.strip().split("#", 1)[0]
    want = slugify(os.path.splitext(t)[0] if "/" in t else t)
    want_path = slugify(os.path.splitext(t)[0]) if "/" in t else None
    for path in iter_pages(vault):
        stem = os.path.splitext(os.path.basename(path))[0]
        rel = os.path.relpath(path, wiki_root(vault))
        if slugify(stem) == want:
            return path
        if want_path and slugify(os.path.splitext(rel)[0]) == want_path:
            return path
    return None


def add_see_also(path, target_link):
    """在页面末尾追加 `- see also: [[target]]`；已存在则跳过（幂等）。"""
    try:
        text = open(path, encoding="utf-8").read()
    except Exception:
        return False
    if re.search(r"\[\[" + re.escape(target_link) + r"(\||\]\])", text):
        return False
    if SEE_ALSO_HEADING not in text:
        text = text.rstrip() + "\n\n" + SEE_ALSO_HEADING + "\n"
    text = text.rstrip() + f"\n- see also: [[{target_link}]]\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return True


def write_new_page(vault, ptype, slug, title):
    folder = os.path.join(wiki_root(vault), TYPE_DIR[ptype])
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{slug}.md")
    if os.path.exists(path):
        return None
    text = page_frontmatter(ptype, title, slug) + PAGE_BODY[ptype].rstrip() + "\n"
    with open(path, "x", encoding="utf-8") as f:
        f.write(text)
    return path


def cmd_backlink(args):
    data = load_registry()
    v = active_vault(data, args.vault)
    require_lock(v, args.force)
    src = find_page(v, args.from_page)
    dst = find_page(v, args.to_page)
    if not src or not dst:
        print(f"未找到页面：{'from' if not src else ''}{' ' if not src and not dst else ''}{'to' if not dst else ''}", file=sys.stderr)
        return 1
    src_stem = os.path.splitext(os.path.basename(src))[0]
    if add_see_also(dst, src_stem):
        touch(v); save_registry(data)
        print(f"已加回链: {os.path.relpath(dst, v['root'])} → [[{src_stem}]]")
    else:
        print("回链已存在，跳过（幂等）。")
    return 0


def cmd_search(args):
    data = load_registry()
    v = active_vault(data, args.vault)
    root = wiki_root(v)
    q = args.query.lower()
    hits = 0
    for path in iter_pages(v):
        rel = os.path.relpath(path, root)
        if args.type and not rel.startswith(TYPE_DIR.get(args.type, args.type) + os.sep):
            continue
        try:
            lines = open(path, encoding="utf-8").read().splitlines()
        except Exception:
            continue
        for i, line in enumerate(lines, 1):
            if q in line.lower():
                hits += 1
                print(f"{rel}:{i}: {line.strip()}")
                if hits >= args.limit:
                    print(f"（已到上限 {args.limit} 条，可用 --limit 放宽）")
                    return 0
    if hits == 0:
        print("未命中。可换关键词，或用 lint 看缺页建议。")
        return 1
    return 0


def cmd_archive(args):
    if args.type not in ("comparison", "synthesis"):
        print("归档只支持 comparison / synthesis", file=sys.stderr)
        return 1
    data = load_registry()
    v = active_vault(data, args.vault)
    require_lock(v, args.force)
    slug = slugify(args.slug)
    path = write_new_page(v, args.type, slug, args.title or slug)
    if not path:
        print(f"页面已存在，拒绝覆盖: {slug}", file=sys.stderr)
        return 4
    linked = []
    for target in args.link_from or []:
        tp = find_page(v, target)
        if tp and add_see_also(tp, slug):
            linked.append(os.path.splitext(os.path.basename(tp))[0])
    log_path = os.path.join(wiki_root(v), "log.md")
    entry = f"\n## [{today()}] query | 归档 {args.type}: {args.title or slug}\n"
    if linked:
        entry += "回链: " + ", ".join(f"[[{x}]]" for x in linked) + "\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(entry)
    touch(v); save_registry(data)
    print(f"已归档: {path}")
    print(f"回链 {len(linked)} 个页面；日志已写入 log.md")
    if not linked:
        print("提示：用 --link-from 指定来源概念页，归档才会接进图谱。")
    return 0


def cmd_promote_check(args):
    data = load_registry()
    v = active_vault(data, args.vault)
    path = find_page(v, args.page)
    if not path:
        print(f"未找到页面: {args.page}", file=sys.stderr)
        return 1
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
    fm = {}
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, val = line.split(":", 1)
                fm[k.strip()] = val.strip()
    body = text[m.end():] if m else text
    stem = os.path.splitext(os.path.basename(path))[0]
    inbound = 0
    for other in iter_pages(v):
        if other == path:
            continue
        if os.path.basename(other) in ("index.md", "log.md", "hot.md", "overview.md"):
            continue
        try:
            t = open(other, encoding="utf-8").read()
        except Exception:
            continue
        if f"[[{stem}]]" in t:
            inbound += 1
    checks = [
        ("来源可追溯（sources 非空）", bool(fm.get("sources") and fm.get("sources") not in ("[]", ""))),
        ("可信度已标（confidence 为 high/medium/low）", fm.get("confidence", "").strip("'\"") in ("high", "medium", "low")),
        ("关联 ≥2 页（related 或回链）", (fm.get("related", "[]").count("[[") >= 2) or inbound >= 2),
        ("有可执行步骤（正文含 怎么做/步骤/流程）", any(k in body for k in ("## 怎么做", "## 步骤", "## 流程", "可执行"))),
        ("有边界与反例（正文含 适用条件/反例/失效）", any(k in body for k in ("## 适用条件", "反例", "失效"))),
    ]
    print(f"# 晋级自查 — {stem}")
    print("\n| 项 | 结果 |")
    print("|---|---|")
    for name, ok in checks:
        print(f"| {name} | {'✅' if ok else '⬜ 待补'} |")
    passed = sum(1 for _, ok in checks if ok)
    print(f"\n通过 {passed}/{len(checks)}；晋级判据：三重验证（来源/可执行/增益）+ 独立复用价值。本检查仅作候选筛查，不替代 R3 评估，也不阻断任何流程。")
    return 0


def cmd_sync(args):
    data = load_registry()
    v = active_vault(data, args.vault)
    root = v["root"]
    if args.pull or args.push:
        print("R7 同步写接口（pull/push）为预留设计，尚未实现（见 references/sync-interface.md）。")
        print("当前不产生任何远端动作；如需备份可在库目录自行 git init 并本地提交。")
        return 2
    if not os.path.isdir(os.path.join(root, ".git")):
        print(f"库 {v['slug']} 不是 git 仓库：未启用同步（本地使用不受影响）。")
        print("如需版本管理，可在库目录执行 git init；ZYX 不代管远端。")
        return 0
    def git(*cmd):
        try:
            return subprocess.check_output(["git", "-C", root, *cmd], text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return None
    branch = git("branch", "--show-current") or "（detached）"
    dirty = git("status", "--porcelain") or ""
    ahead = git("rev-list", "--count", "@{u}..HEAD")
    behind = git("rev-list", "--count", "HEAD..@{u}")
    remote = git("remote", "get-url", "origin")
    print(f"# 同步状态（只读）— {v['slug']}")
    print(f"- 分支: {branch}")
    print(f"- 未提交改动: {len([x for x in dirty.splitlines() if x.strip()])} 项")
    print(f"- 领先上游: {ahead if ahead is not None else '无上游'}")
    print(f"- 落后上游: {behind if behind is not None else '无上游'}")
    print(f"- 远端: {remote or '未配置（纯本地）'}")
    print("\n只读检查，不联网写；pull/push 仍未实现。")
    return 0


# ---------------------------------------------------------------- 参数

def build_parser():
    p = argparse.ArgumentParser(description="R7 wiki-vault 库注册与骨架工具")
    sub = p.add_subparsers(dest="cmd", required=True)

    def common(sp, topic=True):
        sp.add_argument("--raw-dir", default="raw")
        sp.add_argument("--wiki-dir", default="wiki")
        if topic:
            sp.add_argument("--topic", default="")

    sp = sub.add_parser("init", help="新建受管库")
    sp.add_argument("slug")
    sp.add_argument("--root")
    sp.add_argument("--provision", action="store_true")
    common(sp)
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("mount", help="挂载已有 Obsidian 库")
    sp.add_argument("slug")
    sp.add_argument("path")
    sp.add_argument("--provision", action="store_true")
    common(sp)
    sp.set_defaults(func=cmd_mount)

    sp = sub.add_parser("list", help="列出库")
    sp.add_argument("--plain", action="store_true")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("resolve", help="打印库根目录")
    sp.add_argument("slug", nargs="?")
    sp.set_defaults(func=cmd_resolve)

    sp = sub.add_parser("use", help="切换活动库")
    sp.add_argument("slug")
    sp.set_defaults(func=cmd_use)

    sp = sub.add_parser("status", help="活动库与锁状态")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("lock", help="取得单写锁")
    sp.add_argument("slug")
    sp.add_argument("--force", action="store_true")
    sp.add_argument("--note", default="")
    sp.set_defaults(func=cmd_lock)

    sp = sub.add_parser("unlock", help="释放单写锁")
    sp.add_argument("slug")
    sp.set_defaults(func=cmd_unlock)

    sp = sub.add_parser("new-page", help="按类型建页（带 frontmatter）")
    sp.add_argument("type", choices=sorted(TYPE_DIR))
    sp.add_argument("slug")
    sp.add_argument("--title", default="")
    sp.add_argument("--vault", default=None)
    sp.add_argument("--link-to", action="append", default=[], help="新页链接到已有页（可重复）")
    sp.add_argument("--backlink", action="store_true", help="同时给对方页加回链")
    sp.add_argument("--force", action="store_true", help="跳过单写锁检查")
    sp.set_defaults(func=cmd_new_page)

    sp = sub.add_parser("log", help="追加活动日志")
    sp.add_argument("op", choices=sorted(LOG_OPS))
    sp.add_argument("title")
    sp.add_argument("--vault", default=None)
    sp.add_argument("--date", default="")
    sp.add_argument("--detail", default="")
    sp.add_argument("--force", action="store_true", help="跳过单写锁检查")
    sp.set_defaults(func=cmd_log)

    sp = sub.add_parser("sync", help="同步接口（status 只读；pull/push 预留未实现）")
    sp.add_argument("--status", action="store_true")
    sp.add_argument("--pull", action="store_true")
    sp.add_argument("--push", action="store_true")
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--vault", default=None)
    sp.set_defaults(func=cmd_sync)

    sp = sub.add_parser("backlink", help="给已有页加回链")
    sp.add_argument("from_page")
    sp.add_argument("to_page")
    sp.add_argument("--vault", default=None)
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_backlink)

    sp = sub.add_parser("search", help="库内本地检索")
    sp.add_argument("query")
    sp.add_argument("--type", choices=sorted(TYPE_DIR))
    sp.add_argument("--vault", default=None)
    sp.add_argument("--limit", type=int, default=20)
    sp.set_defaults(func=cmd_search)

    sp = sub.add_parser("archive", help="把问答结果归档为对比/综述页并回链")
    sp.add_argument("type", choices=["comparison", "synthesis"])
    sp.add_argument("slug")
    sp.add_argument("--title", default="")
    sp.add_argument("--link-from", action="append", default=[], help="来源页（可重复）")
    sp.add_argument("--vault", default=None)
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_archive)

    sp = sub.add_parser("where", help="打印活动库位置（供 personal agent 记忆）")
    sp.add_argument("--vault", default=None)
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_where)

    sp = sub.add_parser("context", help="生成/安装跨宿主知识库技能卡")
    sp.add_argument("--vault", default=None)
    sp.add_argument("--install", action="store_true")
    sp.add_argument("--remove", action="store_true")
    sp.add_argument("--dir", action="append", default=[], help="目标 skills 目录（可重复）")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_context)

    sp = sub.add_parser("brief", help="生成 ≤600 字知识库简报（会话开头读）")
    sp.add_argument("--vault", default=None)
    sp.add_argument("--with-lint", action="store_true")
    sp.add_argument("--max-chars", type=int, default=600)
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_brief)

    sp = sub.add_parser("promote-check", help="晋级 Skill 前的候选自查（只读，不阻断）")
    sp.add_argument("page")
    sp.add_argument("--vault", default=None)
    sp.set_defaults(func=cmd_promote_check)
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
