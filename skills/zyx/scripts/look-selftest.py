#!/usr/bin/env python3
"""look-selftest.py — ZYX Look Gate 的离线自测（仅标准库生成 PNG）。

验证：目录拼图、JSON 元数据、MANIFEST、 unsupported 退出码、缺失文件退出码。
如果宿主缺少 Pillow/ImageMagick，返回 2（跳过），由 doctor 记为可选缺失。
"""

import json
import os
import struct
import subprocess
import sys
import tempfile
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
LOOK = os.path.join(HERE, "look.py")


def png(path, w, h, rgb):
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))

    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    data += chunk(b"IDAT", zlib.compress(raw, 9))
    data += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)


def run(args, env=None):
    e = os.environ.copy()
    e.update(env or {})
    return subprocess.run([sys.executable, LOOK, *args], text=True, capture_output=True, env=e, timeout=120)


def main():
    tmp = tempfile.mkdtemp(prefix="zyx-look-selftest-")
    try:
        imgs = os.path.join(tmp, "imgs")
        os.makedirs(imgs)
        png(os.path.join(imgs, "a.png"), 640, 360, (30, 30, 46))
        png(os.path.join(imgs, "b.png"), 640, 360, (137, 180, 250))
        out = os.path.join(tmp, "out")
        p = run([imgs, "--out", out, "--json"])
        if p.returncode == 3:
            print("⚠ 跳过：宿主缺少 Pillow/ImageMagick，无法拼 contact sheet")
            return 2
        data = json.loads(p.stdout) if p.returncode == 0 else {}
        assert p.returncode == 0, p.stderr[-300:]
        assert os.path.isfile(os.path.join(out, "look.png")), "缺少 look.png"
        assert os.path.isfile(os.path.join(out, "look.json")), "缺少 look.json"
        assert os.path.isfile(os.path.join(out, "MANIFEST.md")), "缺少 MANIFEST.md"
        assert data.get("pages") == 2, data
        txt = os.path.join(tmp, "x.txt")
        open(txt, "w").write("not visual")
        assert run([txt]).returncode == 2, "unsupported 格式应返回 2"
        assert run([os.path.join(tmp, "missing.png")]).returncode == 1, "缺失文件应返回 1"
        print("✅ look 自测：6/6 通过")
        return 0
    except AssertionError as e:
        print(f"❌ look 自测失败: {e}", file=sys.stderr)
        return 1
    finally:
        import shutil
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
