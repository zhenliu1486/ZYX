#!/usr/bin/env python3
"""omarchy-bridge.py — ZYX 与 Omarchy 的只读握手（不写系统配置）。

用法：
  python3 scripts/omarchy-bridge.py status [--json]
  python3 scripts/omarchy-bridge.py status --install-context

只检测：Omarchy 版本/路径、当前主题、默认 agent、共享 skills 目录、
ZYX / wiki-vault / zyx-context 是否已安装。除 --install-context 外不改任何文件。
"""

import argparse
import json
import os
import subprocess
import sys


def read_first(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.readline().strip()
    except Exception:
        return ""


def find_omarchy():
    candidates = []
    env = os.environ.get("OMARCHY_PATH")
    if env:
        candidates.append(env)
    candidates += ["/usr/share/omarchy", os.path.join(os.path.expanduser("~"), ".local/share/omarchy")]
    for path in candidates:
        if path and os.path.isfile(os.path.join(path, "version")):
            return path, read_first(os.path.join(path, "version"))
    return "", ""


def skill_state(root, name):
    return os.path.isfile(os.path.join(root, name, "SKILL.md"))


def host_dirs():
    home = os.path.expanduser("~")
    dirs = [
        os.path.join(home, ".agents", "skills"),
        os.path.join(home, ".claude", "skills"),
        os.path.join(home, ".openclaw", "skills"),
        os.path.join(home, ".codex", "skills"),
        os.path.join(home, ".doubao", "agent_mode", "workspace", ".user_skills"),
        os.path.join(home, ".gemini", "skills"),
        os.path.join(home, ".kiro", "skills"),
        os.path.join(home, ".qwen", "skills"),
        os.path.join(home, ".grok", "skills"),
        os.path.join(home, ".hermes", "skills"),
    ]
    seen, out = set(), []
    for d in dirs:
        rp = os.path.realpath(d)
        if rp in seen:
            continue
        seen.add(rp)
        out.append(d)
    return out


def status():
    path, version = find_omarchy()
    installing = bool(path) or bool(os.environ.get("OMARCHY_PATH"))
    theme = read_first(os.path.join(os.path.expanduser("~"), ".local/state/omarchy/current/theme.name"))
    agent = read_first(os.path.join(os.path.expanduser("~"), ".config/omarchy/defaults/agent"))
    shared = os.path.join(os.path.expanduser("~"), ".agents", "skills")
    installed_dirs = [d for d in host_dirs() if skill_state(d, "zyx")]
    context_dirs = [d for d in host_dirs() if skill_state(d, "zyx-context")]
    data = {
        "installed": installing,
        "version": version or "unknown",
        "path": path,
        "theme": theme or "unknown",
        "agent": agent or "unknown",
        "shared_skills": shared,
        "shared_skills_exists": os.path.isdir(shared),
        "zyx_installed": bool(installed_dirs),
        "zyx_dirs": installed_dirs,
        "wiki_vault_installed": any(skill_state(d, "wiki-vault") for d in host_dirs()),
        "context_card_installed": bool(context_dirs),
        "context_dirs": context_dirs,
        "ready": bool(installing and installed_dirs and any(skill_state(d, "wiki-vault") for d in host_dirs())),
    }
    return data


def main():
    ap = argparse.ArgumentParser(description="ZYX × Omarchy 只读握手")
    ap.add_argument("command", nargs="?", default="status", choices=["status"])
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--install-context", action="store_true", help="调用 wiki.py context --install")
    args = ap.parse_args()

    if args.install_context:
        here = os.path.dirname(os.path.abspath(__file__))
        wiki = os.path.normpath(os.path.join(here, "..", "..", "wiki-vault", "scripts", "wiki.py"))
        if not os.path.isfile(wiki):
            print(f"找不到 wiki.py: {wiki}", file=sys.stderr)
            return 1
        return subprocess.call([sys.executable, wiki, "context", "--install"])

    d = status()
    if args.json:
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return 0

    if not d["installed"]:
        print("Omarchy: 未检测到（可选；ZYX 仍可独立使用）")
    else:
        print(f"Omarchy: {d['version']} ({d['path']})")
    print(f"Theme: {d['theme']}")
    print(f"Default agent: {d['agent']}")
    print(f"Shared skills: {d['shared_skills']}（{'存在' if d['shared_skills_exists'] else '不存在'}）")
    print(f"ZYX: {'已安装 ' + str(len(d['zyx_dirs'])) + ' 处' if d['zyx_installed'] else '未安装'}")
    print(f"R7 wiki-vault: {'已安装' if d['wiki_vault_installed'] else '未安装'}")
    print(f"Context card: {'已安装 ' + str(len(d['context_dirs'])) + ' 处' if d['context_card_installed'] else '未安装'}")
    print(f"握手: {'ready' if d['ready'] else ('partial' if d['installed'] else 'not-detected')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
