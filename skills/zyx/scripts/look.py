#!/usr/bin/env python3
"""look.py — 视觉产物验收渲染器（ZYX Look Gate）。

把 HTML / PPTX / PDF / 视频 / 图片渲染成一张可被 agent 直接 Read 的 contact sheet，
并在同目录写 look.json 与 MANIFEST.md 供交付审计。只读源文件，不改原产物。

用法：
  python3 scripts/look.py <文件或图片目录> [--out DIR] [--pages 8] [--width 1280] [--json]

退出码：0 已生成；2 不支持的格式；3 缺少渲染工具；1 参数/路径错误。
依赖（按格式取用）：chromium 或 playwright（HTML）、libreoffice + pdftoppm（PPTX/PDF）、
ffmpeg（视频）、Pillow 或 ImageMagick（拼图）。缺工具时明确报错，不假装成功。
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".svg"}
VIDEO_EXT = {".mp4", ".mov", ".webm", ".m4v", ".mkv", ".avi"}
HTML_EXT = {".html", ".htm"}
PDF_EXT = {".pdf"}
PPT_EXT = {".pptx", ".ppt", ".odp"}


def which(name):
    return shutil.which(name)


def run(cmd, timeout=120):
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)


def slugify(text):
    s = re.sub(r"[\s/\\]+", "-", text.strip().lower())
    s = re.sub(r"[^a-z0-9._-]+", "-", s)
    return re.sub(r"-{2,}", "-", s).strip("-") or "look"


def desktop_output():
    here = os.path.dirname(os.path.abspath(__file__))
    desktop_script = os.path.join(here, "desktop-dir.sh")
    if os.path.isfile(desktop_script):
        try:
            out = subprocess.check_output(["bash", desktop_script], text=True).strip()
            if out:
                return out
        except Exception:
            pass
    return os.path.join(os.path.expanduser("~"), "zyx-output")


def render_html(src, workdir, width):
    warnings = []
    out = os.path.join(workdir, "page.png")
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
        with sync_playwright() as p:
            kwargs = {}
            chromium = which("chromium") or which("chromium-browser") or which("google-chrome")
            if chromium:
                kwargs["executable_path"] = chromium
            browser = p.chromium.launch(args=["--no-sandbox"], **kwargs)
            page = browser.new_page(viewport={"width": width, "height": 900})
            from pathlib import Path
            page.goto(Path(src).resolve().as_uri(), wait_until="load")
            page.wait_for_timeout(600)
            page.screenshot(path=out, full_page=True)
            browser.close()
        return [out], ["playwright full_page"], warnings
    except Exception as e:
        warnings.append(f"playwright 不可用，改用 chromium 视口截图：{e}")
    chromium = which("chromium") or which("chromium-browser") or which("google-chrome")
    if not chromium:
        raise RuntimeError("缺少 chromium / playwright，无法渲染 HTML")
    p = run([chromium, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
             f"--screenshot={out}", f"--window-size={width},2000", "file://" + os.path.abspath(src)], timeout=60)
    if p.returncode != 0 or not os.path.isfile(out):
        raise RuntimeError(f"chromium 截图失败：{p.stderr[-400:]}")
    warnings.append("chromium 视口截图（可能截不到超长页面底部）")
    return [out], ["chromium viewport"], warnings


def pdf_to_images(pdf, workdir, pages):
    pdftoppm = which("pdftoppm")
    if not pdftoppm:
        raise RuntimeError("缺少 pdftoppm（poppler），无法把 PDF 转图")
    prefix = os.path.join(workdir, "page")
    p = run([pdftoppm, "-png", "-r", "110", "-f", "1", "-l", str(pages), pdf, prefix], timeout=180)
    if p.returncode != 0:
        raise RuntimeError(f"pdftoppm 失败：{p.stderr[-400:]}")
    images = sorted(
        [os.path.join(workdir, f) for f in os.listdir(workdir) if re.match(r"page-\d+\.png$", f)],
        key=lambda x: int(re.search(r"page-(\d+)", x).group(1)),
    )
    if not images:
        raise RuntimeError("PDF 没有渲染出任何页面")
    return images


def render_office(src, workdir, pages):
    warnings = []
    if src.lower().endswith(".pdf"):
        pdf = src
        tools = ["pdftoppm"]
    else:
        soffice = which("soffice") or which("libreoffice")
        if not soffice:
            raise RuntimeError("缺少 libreoffice / soffice，无法渲染 PPTX")
        p = run([soffice, "--headless", "--norestore", "--convert-to", "pdf", "--outdir", workdir, src], timeout=180)
        if p.returncode != 0:
            raise RuntimeError(f"libreoffice 转 PDF 失败：{p.stderr[-400:]}")
        pdf = os.path.join(workdir, os.path.splitext(os.path.basename(src))[0] + ".pdf")
        if not os.path.isfile(pdf):
            raise RuntimeError("libreoffice 未产出 PDF")
        tools = ["libreoffice+pdftoppm"]
    images = pdf_to_images(pdf, workdir, pages)
    if len(images) >= pages:
        warnings.append(f"只渲染了前 {pages} 页；完整验收请加 --pages")
    return images, tools, warnings


def video_duration(src):
    if not which("ffprobe"):
        return None
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", src], timeout=30)
    try:
        return float(p.stdout.strip())
    except Exception:
        return None


def render_video(src, workdir, width):
    ffmpeg = which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("缺少 ffmpeg，无法抽视频帧")
    duration = video_duration(src)
    if duration and duration > 0:
        times = [duration * f for f in (0.15, 0.38, 0.62, 0.85)]
    else:
        times = [1, 3, 5, 7]
    images = []
    for i, t in enumerate(times, 1):
        out = os.path.join(workdir, f"frame-{i}.png")
        p = run([ffmpeg, "-y", "-ss", f"{t:.2f}", "-i", src, "-frames:v", "1",
                 "-vf", f"scale={width}:-1", out], timeout=60)
        if p.returncode == 0 and os.path.isfile(out):
            images.append(out)
    if not images:
        raise RuntimeError("ffmpeg 没有抽出任何帧")
    return images, ["ffmpeg"], []


def collect_images(src, workdir):
    if os.path.isdir(src):
        files = []
        for name in sorted(os.listdir(src)):
            p = os.path.join(src, name)
            if os.path.isfile(p) and os.path.splitext(name)[1].lower() in IMAGE_EXT:
                files.append(p)
        if not files:
            raise RuntimeError("目录里没有可渲染的图片")
        return files
    if os.path.splitext(src)[1].lower() == ".svg":
        convert = which("convert")
        if not convert:
            raise RuntimeError("缺少 ImageMagick convert，无法栅格化 SVG")
        out = os.path.join(workdir, "svg.png")
        p = run([convert, src, out], timeout=60)
        if p.returncode != 0:
            raise RuntimeError(f"SVG 栅格化失败：{p.stderr[-400:]}")
        return [out]
    if os.path.splitext(src)[1].lower() not in IMAGE_EXT:
        raise RuntimeError("不是图片格式")
    return [src]


def compose(images, out, width):
    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore
    except Exception:
        montage = which("montage")
        if not montage:
            raise RuntimeError("缺少 Pillow 或 ImageMagick montage，无法拼 contact sheet；可 pip3 install pillow")
        if len(images) == 1:
            p = run([montage, images[0], "-resize", f"{width}x", out], timeout=60)
        else:
            p = run([montage, "-label", "%f", "-tile", "3x", "-geometry", f"{width // 3}x+6+6", *images, out], timeout=120)
        if p.returncode != 0 or not os.path.isfile(out):
            raise RuntimeError(f"montage 失败：{p.stderr[-400:]}")
        return out, []

    n = len(images)
    cols = 1 if n == 1 else (2 if n == 2 else 3)
    gap, label_h, pad = 10, 22, 14
    cell_w = max(200, (width - pad * 2 - gap * (cols - 1)) // cols)
    cell_h = int(cell_w * 0.62)
    rows = (n + cols - 1) // cols
    canvas = Image.new("RGB", (pad * 2 + cols * cell_w + (cols - 1) * gap,
                              pad * 2 + rows * (cell_h + label_h) + (rows - 1) * gap), "white")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    warnings = []
    for i, path in enumerate(images):
        try:
            img = Image.open(path).convert("RGB")
        except Exception as e:
            warnings.append(f"跳过无法读取的图 {os.path.basename(path)}：{e}")
            continue
        orig_w, orig_h = img.size
        img.thumbnail((cell_w, cell_h))
        col, row = i % cols, i // cols
        x = pad + col * (cell_w + gap)
        y = pad + row * (cell_h + label_h + gap)
        draw.text((x + 2, y + 4), f"p{i + 1}", fill="#333333", font=font)
        canvas.paste(img, (x + (cell_w - img.width) // 2, y + label_h + (cell_h - img.height) // 2))
        if orig_w < 640 or orig_h < 360:
            warnings.append(f"p{i + 1} 分辨率偏低（{orig_w}x{orig_h}）")
        gray = img.convert("L")
        ink = gray.point(lambda px: 255 if px < 240 else 0)
        if ink.getbbox() is None:
            warnings.append(f"p{i + 1} 近似空白，检查是否渲染失败")
    canvas.save(out, "PNG", optimize=True)
    return out, warnings


def main():
    ap = argparse.ArgumentParser(description="把视觉产物渲染成 agent 可读的 contact sheet")
    ap.add_argument("source", help="HTML/PPTX/PDF/视频/图片/图片目录")
    ap.add_argument("--out", default="", help="输出目录（默认 ~/zyx-output/look/<slug>-<stamp>）")
    ap.add_argument("--pages", type=int, default=8, help="PPTX/PDF 最多渲染页数")
    ap.add_argument("--width", type=int, default=1280, help="输出图宽度")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.pages < 1:
        print("--pages 必须 ≥ 1", file=sys.stderr)
        return 1
    src = os.path.abspath(os.path.expanduser(args.source))
    if not os.path.exists(src):
        print(f"文件不存在: {src}", file=sys.stderr)
        return 1
    base = slugify(os.path.basename(src.rstrip("/")) or "look")
    outdir = os.path.abspath(args.out) if args.out else os.path.join(
        desktop_output(), "look", f"{base}-{time.strftime('%Y%m%d-%H%M%S')}")
    os.makedirs(outdir, exist_ok=True)

    ext = os.path.splitext(src)[1].lower()
    tools, warnings = [], []
    images = []
    try:
        with tempfile.TemporaryDirectory(prefix="zyx-look-") as tmp:
            if ext in HTML_EXT:
                images, t, warnings = render_html(src, tmp, args.width)
            elif ext in PPT_EXT or ext in PDF_EXT:
                images, t, warnings = render_office(src, tmp, args.pages)
            elif ext in VIDEO_EXT:
                images, t, warnings = render_video(src, tmp, args.width)
            elif ext in IMAGE_EXT or os.path.isdir(src):
                images, t, warnings = collect_images(src, tmp), ["source"], []
            else:
                print(f"不支持的格式: {ext or '目录'}（支持 HTML/PPTX/PDF/视频/图片）", file=sys.stderr)
                return 2

            if len(images) > 12:
                warnings.append(f"图片 {len(images)} 张，只拼前 12 张")
                images = images[:12]
            sheet = os.path.join(outdir, "look.png")
            _, compose_warnings = compose(images, sheet, args.width)
            warnings.extend(compose_warnings)
            tools = t
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        return 3
    except Exception as e:
        print(f"渲染失败: {e}", file=sys.stderr)
        return 1

    meta = {
        "source": src,
        "output": sheet,
        "pages": len(images),
        "width": args.width,
        "tools": tools,
        "warnings": warnings,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    with open(os.path.join(outdir, "look.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    with open(os.path.join(outdir, "MANIFEST.md"), "w", encoding="utf-8") as f:
        f.write("# look · 视觉验收\n\n")
        f.write(f"- 源文件: `{src}`\n- 输出: `look.png`（{meta['pages']} 张，宽 {args.width}）\n")
        f.write(f"- 渲染: {', '.join(tools) or 'unknown'}\n- 生成: {meta['generated_at']}\n")
        if warnings:
            f.write("- 警告:\n" + "".join(f"  - {w}\n" for w in warnings))
        f.write("\n> 交付前必须由 agent 亲自 Read `look.png`，修完溢出/对比度/层级问题；未看不得宣称已验证。\n")

    if args.json:
        print(json.dumps(meta, ensure_ascii=False, indent=2))
    else:
        print(sheet)
        for w in warnings:
            print(f"⚠ {w}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
