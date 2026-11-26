#!/usr/bin/env python3
"""route-selftest.py — 验证 route.sh 的八类路由映射与路径解析。

用临时目录伪造每个蒸馏器的 SKILL.md，通过环境变量覆盖路径，逐条断言：
- 返回码为 0；
- 输出包含被路由的 Skill 绝对路径；
- 未知类型返回非零。
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROUTE = HERE / "route.sh"

CASES = [
    ("person", "nuwa-skill", "NUWA_SKILL_DIR"),
    ("industry", "master-skill", "MASTER_SKILL_DIR"),
    ("content", "cangjie-skill", "CANGJIE_SKILL_DIR"),
    ("problem", "dbs", "DBS_SKILL_DIR"),
    ("production", "video-studio", "VIDEO_STUDIO_DIR"),
    ("iterate", "f2r-feedback-iteration", "F2R_SKILL_DIR"),
    ("wiki", "wiki-vault", "WIKI_VAULT_DIR"),
    ("invest", "ashare-four-dim-decision", "ASHARE_DECISION_DIR"),
]


def main() -> int:
    passed = 0
    failed = []
    with tempfile.TemporaryDirectory(prefix="zyx-route-") as tmp:
        root = Path(tmp)
        for route, skill_dir, env_name in CASES:
            target = root / env_name / skill_dir
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("# fake\n", encoding="utf-8")
            env = os.environ.copy()
            env[env_name] = str(target)
            p = subprocess.run(
                ["bash", str(ROUTE), route],
                capture_output=True, text=True, env=env, timeout=20,
            )
            if p.returncode == 0 and str(target) in p.stdout:
                passed += 1
                print(f"✅ {route:10s} → {skill_dir}")
            else:
                failed.append(f"{route}: rc={p.returncode} out={p.stdout!r} err={p.stderr!r}")
        p = subprocess.run(["bash", str(ROUTE), "not-a-route"],
                           capture_output=True, text=True, timeout=20)
        if p.returncode != 0:
            passed += 1
            print("✅ 未知类型被拒绝")
        else:
            failed.append("未知类型没有返回非零")

    total = len(CASES) + 1
    if failed:
        print(f"\n❌ route 自测失败：{passed}/{total}", file=sys.stderr)
        for item in failed:
            print(f"  - {item}", file=sys.stderr)
        return 1
    print(f"\n✅ route 自测：{passed}/{total} 通过")
    return 0


if __name__ == "__main__":
    sys.exit(main())
