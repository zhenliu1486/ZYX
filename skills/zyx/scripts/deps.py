#!/usr/bin/env python3
"""deps.py — 读取 deps/manifest.json，供 doctor / updater / install 脚本共用。

子命令：
  host-dirs                打印展开后的宿主 skills 目录（每行一个，$HOME 已展开）
  deps                     打印依赖行：id\x1fdir\x1fsource\x1frequired\x1fparent\x1furl\x1finstall\x1fnotes
  git-repos                仅打印 source=git 的依赖：id\tdir\turl
  get-dir <dir> <field>    按目录名取字段（url/install/source/required/parent/notes）

脚本不在 shell 里硬编码依赖清单；新增/调整依赖只改 manifest.json。
"""
import json
import os
import sys

ZYX_DIR = os.environ.get("ZYX_DIR") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.environ.get("ZYX_MANIFEST") or os.path.join(ZYX_DIR, "deps", "manifest.json")


def load():
    with open(MANIFEST, encoding="utf-8") as f:
        return json.load(f)


def expand(path: str) -> str:
    return path.replace("$HOME", os.path.expanduser("~"))


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "deps"
    data = load()

    if cmd == "host-dirs":
        for d in data.get("host_dirs", []):
            print(expand(d))
        return 0

    if cmd == "git-repos":
        for dep in data["dependencies"]:
            if dep["source"] == "git":
                print("\t".join([dep["id"], dep["dir"], dep["url"] or ""]))
        return 0

    if cmd == "get-dir":
        target = sys.argv[2]
        field = sys.argv[3]
        for dep in data["dependencies"]:
            if dep["dir"] == target:
                v = dep.get(field)
                print("" if v is None else v)
                return 0
        print("", end="")
        return 1

    # deps
    for dep in data["dependencies"]:
        row = [
            dep["id"],
            dep["dir"],
            dep["source"],
            "1" if dep.get("required") else "0",
            dep.get("parent") or "",
            dep.get("url") or "",
            dep.get("install") or "",
            dep.get("notes") or "",
        ]
        print("\x1f".join(row))
    return 0


if __name__ == "__main__":
    sys.exit(main())
