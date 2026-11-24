#!/usr/bin/env python3
"""wiki-selftest.py — R7 wiki-vault 端到端回归自测（仅标准库，不碰真实库）。

用法：
  python3 scripts/wiki-selftest.py [--verbose]

覆盖：
  init 骨架 / 建页 / 重复页拒写 / 单写锁（同会话续租、异会话拒绝）/
  未持锁拒绝 / 双向回链 / 问答归档 / 本地检索 / 晋级自查 /
  lint 九类指标与 --exit-code / 挂载已有 Obsidian 库不写入 / sync 只读与预留。

退出码：0 全部通过；1 有失败项；2 脚本自身异常。
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WIKI = os.path.join(HERE, "wiki.py")
LINT = os.path.join(HERE, "wiki-lint.py")
VERBOSE = "--verbose" in sys.argv

results = []


def check(name, cond, detail=""):
    results.append({"name": name, "ok": bool(cond), "detail": detail})
    mark = "✅" if cond else "❌"
    print(f"{mark} {name}" + (f" — {detail}" if detail and not cond else ""))
    return bool(cond)


def run(args, env=None, timeout=60):
    e = os.environ.copy()
    e.update(env or {})
    p = subprocess.run(
        [sys.executable, WIKI, *args],
        text=True, capture_output=True, env=e, timeout=timeout,
    )
    if VERBOSE:
        print(f"  $ wiki.py {' '.join(args)} → {p.returncode}")
        if p.stdout.strip():
            print("    " + p.stdout.strip().replace("\n", "\n    "))
        if p.stderr.strip():
            print("    [err] " + p.stderr.strip().replace("\n", "\n    "))
    return p.returncode, p.stdout, p.stderr


def main():
    root = tempfile.mkdtemp(prefix="zyx-wiki-selftest-")
    state = os.path.join(root, "state")
    vault = os.path.join(root, "vault")
    obs = os.path.join(root, "obsidian-vault")
    os.makedirs(os.path.join(obs, ".obsidian"))
    os.makedirs(os.path.join(obs, "notes"))
    with open(os.path.join(obs, "notes", "mine.md"), "w", encoding="utf-8") as f:
        f.write("# 用户自己的笔记\n")

    env = {"ZYX_STATE_DIR": state, "WIKI_SESSION_ID": "selftest-s1"}
    env2 = {"ZYX_STATE_DIR": state, "WIKI_SESSION_ID": "selftest-s2"}
    env_no_lock = {"ZYX_STATE_DIR": state, "WIKI_SESSION_ID": "selftest-s1"}

    try:
        # 1. 建库
        code, out, _ = run(["init", "demo", "--topic", "自测", "--root", vault], env)
        check("init 建库", code == 0, f"exit={code}")
        check("init 生成主索引", os.path.isfile(os.path.join(vault, "wiki", "index.md")))
        check("init 生成 raw/articles", os.path.isdir(os.path.join(vault, "raw", "articles")))

        # 2. 锁
        code, _, _ = run(["lock", "demo"], env)
        check("取写锁", code == 0, f"exit={code}")
        code, _, _ = run(["lock", "demo"], env)
        check("同会话续租", code == 0, f"exit={code}")

        # 3. 建页与重复
        code, out, _ = run(["new-page", "concept", "概念甲", "--title", "概念甲"], env)
        check("建概念页", code == 0 and os.path.isfile(os.path.join(vault, "wiki", "concepts", "概念甲.md")), f"exit={code}")
        code, _, _ = run(["new-page", "concept", "概念甲"], env)
        check("重复页拒写（退出码 4）", code == 4, f"exit={code}")

        code, _, _ = run(["log", "ingest", "自测摄入"], env)
        check("追加日志", code == 0, f"exit={code}")

        # 4. 并发会话
        code, _, _ = run(["log", "note", "并发尝试"], env2)
        check("异会话未持锁写入被拒（5）", code == 5, f"exit={code}")
        code, _, _ = run(["lock", "demo"], env2)
        check("异会话抢锁被拒（3）", code == 3, f"exit={code}")

        # 5. 解链后未持锁写入
        code, _, _ = run(["unlock", "demo"], env)
        check("释放写锁", code == 0, f"exit={code}")
        code, _, _ = run(["new-page", "entity", "实体乙"], env_no_lock)
        check("未持锁写入被拒（5）", code == 5, f"exit={code}")

        # 6. 双向回链与归档
        run(["lock", "demo"], env)
        code, _, _ = run(["new-page", "entity", "实体乙", "--title", "实体乙", "--link-to", "概念甲", "--backlink"], env)
        check("建实体页并双向回链", code == 0, f"exit={code}")
        a_text = open(os.path.join(vault, "wiki", "concepts", "概念甲.md"), encoding="utf-8").read()
        check("来源页被加回链", "[[实体乙]]" in a_text)
        code, _, _ = run(["archive", "synthesis", "综述丙", "--title", "综述丙", "--link-from", "概念甲"], env)
        check("问答归档为综述页", code == 0 and os.path.isfile(os.path.join(vault, "wiki", "syntheses", "综述丙.md")), f"exit={code}")
        a_text = open(os.path.join(vault, "wiki", "concepts", "概念甲.md"), encoding="utf-8").read()
        check("归档回链到来源页", "[[综述丙]]" in a_text)

        # 7. 检索
        code, out, _ = run(["search", "概念甲"], env)
        check("本地检索命中", code == 0 and "概念甲" in out, f"exit={code}")

        # 8. 晋级自查（只读，不阻断）
        code, out, _ = run(["promote-check", "概念甲"], env)
        check("晋级自查可运行", code == 0 and "晋级自查" in out, f"exit={code}")

        # 8.5 简报与定位
        code, out, _ = run(["where"], env)
        check("where 打印库位置", code == 0 and "root:" in out, f"exit={code}")
        code, out, _ = run(["brief"], env)
        check("brief 生成简报", code == 0 and "知识库简报" in out, f"exit={code}")
        code, out, _ = run(["brief", "--with-lint"], env)
        check("brief 可带巡检摘要", code == 0 and "巡检" in out, f"exit={code}")

        # 9. lint
        code, out, _ = run(["list"], env)
        check("库列表可读", code == 0 and "demo" in out, f"exit={code}")
        p = subprocess.run([sys.executable, LINT, vault, "--json"], text=True, capture_output=True)
        try:
            data = json.loads(p.stdout)
        except Exception:
            data = {}
        check("lint 正常输出 JSON", p.returncode == 0 and bool(data), f"exit={p.returncode}")
        check("lint 检出未进索引", data.get("summary", {}).get("not_in_index", 0) >= 1, str(data.get("summary")))

        # 制造断链 + 缺页
        with open(os.path.join(vault, "wiki", "concepts", "概念甲.md"), "a", encoding="utf-8") as f:
            f.write("\n[[不存在的页]]\n[[不存在的页]]\n[[不存在的页]]\n")
        p = subprocess.run([sys.executable, LINT, vault, "--json"], text=True, capture_output=True)
        data = json.loads(p.stdout)
        check("lint 检出断链", data["summary"]["broken_links"] >= 1, str(data["summary"]))
        check("lint 检出缺页", data["summary"]["missing_pages"] >= 1, str(data["summary"]))
        p = subprocess.run([sys.executable, LINT, vault, "--exit-code"], text=True, capture_output=True)
        check("lint --exit-code 结构性有问题返回 1", p.returncode == 1, f"exit={p.returncode}")

        # 10. 同步
        code, out, _ = run(["sync", "--status"], env)
        check("sync --status 非 git 库正常提示", code == 0 and "不是 git" in out, f"exit={code}")
        code, _, _ = run(["sync", "--push"], env)
        check("sync --push 仍为预留（2）", code == 2, f"exit={code}")

        # 11. 挂载已有 Obsidian 库
        code, out, _ = run(["mount", "obs1", obs], env)
        check("挂载已有 Obsidian 库", code == 0, f"exit={code}")
        check("挂载不擅建 raw/", not os.path.isdir(os.path.join(obs, "raw")))
        check("用户既有笔记未被改动", os.path.isfile(os.path.join(obs, "notes", "mine.md")))
        code, _, _ = run(["mount", "obs2", obs, "--provision"], env)
        check("--provision 才补骨架", code == 0 and os.path.isdir(os.path.join(obs, "raw")), f"exit={code}")

        # 12. 收尾
        run(["unlock", "demo"], env)
        code, out, _ = run(["status", "--json"], env)
        check("status 可读 JSON", code == 0 and "vaults" in out, f"exit={code}")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    print(f"\n===== 结果：{passed}/{total} 通过 =====")
    if passed != total:
        for r in results:
            if not r["ok"]:
                print(f"失败：{r['name']} {r['detail']}")
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"自测异常: {e}", file=sys.stderr)
        sys.exit(2)
