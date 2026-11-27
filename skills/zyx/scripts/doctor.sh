#!/usr/bin/env bash
# doctor.sh — zyx 安装就绪自检。
# 装完或排障时跑一遍：运行依赖、依赖安装状态、文件完整性、调度环境、产物目录可写性、自身版本，
# 输出「就绪 / 缺什么 / 怎么补」。只读检查，不改动任何文件。
# 退出码: 0 全部就绪；1 存在缺失项；2 脚本本身出错。
#
# 选项:
#   --online   额外做上游网络可达性检查（默认离线，避免自检被网络拖慢）。
#   --full     额外跑 R7 知识库端到端自测与 Look Gate 自测（临时目录，不碰真实产物）。

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZYX_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
# shellcheck source=lib-common.sh
source "$SCRIPT_DIR/lib-common.sh"

ONLINE=0
FULL=0
for arg in "$@"; do
  case "$arg" in
    --online) ONLINE=1 ;;
    --full) FULL=1 ;;
  esac
done

warn=0
fail=0

check_cmd() { # $1=命令 $2=用途
  if command -v "$1" >/dev/null 2>&1; then
    echo "  ✅ $1 可用（$2）"
  else
    echo "  ⚠ 缺少 $1（$2）"
    warn=1
  fi
}

echo "===== zyx 就绪自检 $(date '+%Y-%m-%d %H:%M') ====="
echo "zyx 目录: $ZYX_DIR"
echo

echo "## 1. 运行依赖"
check_cmd bash "脚本执行"
check_cmd git "蒸馏器版本检测与更新"
check_cmd curl "远端版本/网络可达性检查"
command -v python3 >/dev/null 2>&1 && echo "  ✅ python3 $(python3 --version 2>/dev/null | awk '{print $2}')" || echo "  ℹ 未装 python3（仓颉脚本/PY 依赖需要时再补）"
echo

echo "## 2. 依赖安装状态（清单: deps/manifest.json）"
# 读取清单行：id|dir|source|required|parent|url|install|notes
while IFS=$'\x1f' read -r id dir source required parent url install notes; do
  [ -z "$dir" ] && continue
  p="$(find_local "$dir" || true)"
  if [ -n "$p" ]; then
    echo "  ✅ [$id] $dir → $p"
  else
    if [ "$required" = "1" ]; then
      echo "  ❌ [$id] $dir 未安装（必需）。安装: $install"
      fail=1
    else
      echo "  ⚠ [$id] $dir 未安装（可选）。$install"
      warn=1
    fi
  fi
done < <(python3 "$SCRIPT_DIR/deps.py" deps)
echo

echo "## 3. 文件完整性（自身 + 已安装的内置技能）"
INTEGRITY_TARGETS=("$ZYX_DIR")
while IFS=$'\x1f' read -r id dir source required parent url install notes; do
  [ -z "$dir" ] && continue
  [ "$source" != "bundled" ] && continue
  p="$(find_local "$dir" || true)"
  [ -n "$p" ] && INTEGRITY_TARGETS+=("$p")
done < <(python3 "$SCRIPT_DIR/deps.py" deps)
python3 "$SCRIPT_DIR/check-integrity.py" "${INTEGRITY_TARGETS[@]}" || fail=1
echo

if [ "$ONLINE" -eq 1 ]; then
  echo "## 4. 上游网络可达性"
  while IFS=$'\x1f' read -r id dir source required parent url install notes; do
    [ -z "$url" ] && continue
    if curl -fsSI --max-time 8 "$url" >/dev/null 2>&1; then
      echo "  ✅ [$id] $url 可达"
    else
      echo "  ⚠ [$id] $url 不可达（可能是网络/限流，不影响本地已装版本）"
      warn=1
    fi
  done < <(python3 "$SCRIPT_DIR/deps.py" deps)
  echo
fi

echo "## 5. 调度环境（后台自动更新）"
if command -v crontab >/dev/null 2>&1; then echo "  ✅ crontab 可用"; else echo "  ⚠ 无 crontab"; fi
if command -v launchctl >/dev/null 2>&1; then echo "  ✅ launchctl 可用（macOS）"; fi
if command -v systemctl >/dev/null 2>&1; then echo "  ✅ systemd 可用（Linux）"; fi
if [ ! -f "$ZYX_DIR/state/registry.json" ]; then
  echo "  ℹ 尚未注册后台更新任务；首次调用 zyx 时 env-registry.sh 会自动注册。"
fi
echo

echo "## 6. 产物目录可写性"
# shellcheck source=desktop-dir.sh
source "$SCRIPT_DIR/desktop-dir.sh"
desktop="$(resolve_desktop_dir)"
out="$desktop/zyx-output"
if mkdir -p "$out/.write-test" 2>/dev/null; then
  rmdir "$out/.write-test" 2>/dev/null
  echo "  ✅ 产物目录可写: $out"
else
  echo "  ❌ 产物目录不可写: $out"
  fail=1
fi
echo

echo "## 7. zyx 自身版本"
SELF_VER="$ZYX_DIR/state/self-version.json"
if [ -f "$SELF_VER" ]; then
  SELF_VER="$SELF_VER" python3 <<'PY'
import json, os
try:
    d=json.load(open(os.environ["SELF_VER"]))
    msg={"equal":"已是最新","behind":"⚠ 本地落后远端，建议更新","ahead":"本地超前远端（未发布）","unknown":"版本号无法比对"}
    extra=""
    if d.get("remote_sha"): extra=f"（远端 {d['remote_sha'][:7]}）"
    print(f"  本地 {d['local']} / 远端 {d['remote']} — {msg.get(d['status'], d['status'])}{extra}（{d['checked_at']}）")
except Exception:
    print("  ⚠ 自身版本记录损坏，可跑 updater.sh 重新比对。")
PY
else
  echo "  ℹ 尚未做过远端版本比对；运行 bash $SCRIPT_DIR/updater.sh --check-drift 后生成。"
fi
echo

echo "## 8. 知识库（R7）"
WV="$(find_local wiki-vault || true)"; [ -n "$WV" ] && WV="$(cd "$WV" && pwd)"
if [ -n "$WV" ] && [ -f "$WV/scripts/wiki.py" ]; then
  n="$(python3 "$WV/scripts/wiki.py" list --plain 2>/dev/null | grep -c . || true)"
  echo "  ✅ wiki-vault 可用 → $WV"
  echo "  ℹ 已注册库: ${n:-0} 个；注册表: $ZYX_DIR/state/vaults.json"
  if [ -f "$ZYX_DIR/state/vaults.json" ]; then
    python3 - "$ZYX_DIR/state/vaults.json" <<'PYW'
import json, sys
try:
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    for v in d.get("vaults", []):
        mark = "*" if v.get("slug") == d.get("active") else " "
        ready = "就绪" if v.get("layout_ready") else "未对齐"
        print(f"    {mark} {v.get('slug')} [{ready}] {v.get('root')}")
except Exception:
    print("    ⚠ 注册表损坏，可删除后重新 init/mount。")
PYW
  fi
else
  echo "  ⚠ 未检测到 wiki-vault（R7 可选；随仓库内置，重装 install.sh 可补）"
  warn=1
fi
if [ "$FULL" -eq 1 ] && [ -n "$WV" ] && [ -f "$WV/scripts/wiki-selftest.py" ]; then
  echo
  echo "  ## R7 端到端自测（--full）"
  python3 "$WV/scripts/wiki-selftest.py" || { echo "  ❌ R7 自测存在失败项"; warn=1; }
fi
echo

echo "## 9. 视觉验收（Look Gate）"
if [ -f "$SCRIPT_DIR/look.py" ]; then
  echo "  ✅ look.py 可用 → $SCRIPT_DIR/look.py"
else
  echo "  ⚠ 缺少 look.py（视觉产物验收不可用；重装 install.sh 可补）"
  warn=1
fi
if command -v chromium >/dev/null 2>&1 || command -v chromium-browser >/dev/null 2>&1 || command -v google-chrome >/dev/null 2>&1; then
  echo "  ✅ HTML 渲染器：chromium 可用"
elif python3 -c 'import playwright' >/dev/null 2>&1; then
  echo "  ✅ HTML 渲染器：playwright 可用"
else
  echo "  ⚠ 缺少 HTML 渲染器（chromium / playwright；HTML 无法渲染）"
  warn=1
fi
if command -v soffice >/dev/null 2>&1 || command -v libreoffice >/dev/null 2>&1; then
  echo "  ✅ PPTX/PDF 渲染器：libreoffice/soffice 可用"
else
  echo "  ⚠ 缺少 libreoffice/soffice（PPTX 无法渲染）"
  warn=1
fi
for c in pdftoppm ffmpeg; do
  if command -v "$c" >/dev/null 2>&1; then
    echo "  ✅ $c 可用"
  else
    echo "  ⚠ 缺少 $c（对应格式无法渲染；按需安装）"
    warn=1
  fi
done
if python3 - <<'PY' 2>/dev/null
import importlib.util
raise SystemExit(0 if importlib.util.find_spec("PIL") else 1)
PY
then
  echo "  ✅ Pillow 可用（contact sheet）"
elif command -v montage >/dev/null 2>&1; then
  echo "  ✅ ImageMagick montage 可用（contact sheet 回退）"
else
  echo "  ⚠ 缺少 Pillow/ImageMagick（contact sheet 不可用）"
  warn=1
fi
if [ "$FULL" -eq 1 ] && [ -f "$SCRIPT_DIR/look-selftest.py" ]; then
  echo
  echo "  ## Look Gate 自测（--full）"
  python3 "$SCRIPT_DIR/look-selftest.py"
  rc=$?
  if [ "$rc" -eq 2 ]; then
    echo "  ℹ 跳过拼图（宿主缺 Pillow/ImageMagick）"
  elif [ "$rc" -ne 0 ]; then
    echo "  ❌ Look Gate 自测失败"
    warn=1
  fi
fi
echo

echo "## 10. Omarchy 握手（可选）"
if [ -f "$SCRIPT_DIR/omarchy-bridge.py" ]; then
  bridge_out="$(python3 "$SCRIPT_DIR/omarchy-bridge.py" status 2>&1 || true)"
  echo "$bridge_out" | sed 's/^/  /'
  if echo "$bridge_out" | grep -q '^握手: partial'; then
    echo "  ⚠ Omarchy 已检测到，但 ZYX/R7 未完整安装；先跑 install.sh。"
    warn=1
  fi
else
  echo "  ℹ 未带 Omarchy 握手脚本（可选）"
fi
echo

echo "## 11. Context Card（跨宿主记忆）"
if [ -n "$WV" ] && [ -f "$WV/scripts/wiki.py" ]; then
  if python3 "$WV/scripts/wiki.py" list --plain 2>/dev/null | grep -q .; then
    ctx_json="$(python3 "$WV/scripts/wiki.py" context --json 2>/dev/null || true)"
    ctx_slug="$(printf '%s' "$ctx_json" | python3 -c 'import json,sys;print(json.load(sys.stdin).get("slug",""))' 2>/dev/null || true)"
    installed=0
    for base in "${HOST_DIRS[@]}"; do
      card="$base/zyx-context/SKILL.md"
      if [ -f "$card" ] && grep -q "slug=$ctx_slug" "$card" 2>/dev/null; then
        installed=$((installed+1))
      fi
    done
    if (( installed > 0 )); then
      echo "  ✅ 活动库 $ctx_slug 的 context 卡已安装 $installed 处"
    else
      echo "  ℹ 活动库 $ctx_slug 尚未安装 context 卡；需要时说「安装知识库上下文卡」，或跑 wiki.py context --install"
    fi
  else
    echo "  ℹ 尚无知识库；建库后可安装 context 卡"
  fi
else
  echo "  ℹ 未检测到 wiki-vault"
fi
echo

echo "## 12. 路由自测（--full）"
if [ "$FULL" -eq 1 ] && [ -f "$SCRIPT_DIR/route-selftest.py" ]; then
  python3 "$SCRIPT_DIR/route-selftest.py"
  rc=$?
  if [ "$rc" -ne 0 ]; then
    echo "  ❌ route 自测失败"
    warn=1
  fi
else
  echo "  ℹ 跳过（仅 --full 运行）"
fi
echo

echo "## 结论"
if [ "$fail" -eq 1 ]; then
  echo "存在必须补齐的缺失项（见 ❌），补齐后重跑 doctor。"
  exit 1
elif [ "$warn" -eq 1 ]; then
  echo "基本就绪，有可选缺失项（见 ⚠），不影响核心路由。"
else
  echo "全部就绪。"
fi
exit 0
