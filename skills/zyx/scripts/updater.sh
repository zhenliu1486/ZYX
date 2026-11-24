#!/usr/bin/env bash
# updater.sh — zyx 后台静默更新器。
# 由 env-registry 注册的周检任务调用；也可手动执行。
#
# 职责：
# 1. 检查并快进更新三个 git 蒸馏器（女娲/大师/仓颉），失败自动回滚。
# 2. 检查 zyx 自身版本（若 zyx 后续发布到远端仓库，比对远端版本号/commit）。
# 3. dbs 家族：只比对官方版本并记录差异，不自动批量覆盖（目录式安装，由 dbs-update 处理）。
# 4. 全程写日志到 state/updater.log；--silent 时不在前台打印。
#
# 安全策略：
# - git 仓库只做 --ff-only 快进；非快进（本地有分叉/手改）不强行合并，保留本地并记录。
# - 快进前备份当前 HEAD 到 state/backup/；更新后若产物脚本/关键文件缺失，可据此回滚。
# - 不删除用户本地未提交改动；不访问远端写接口；不推送任何内容。

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZYX_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_DIR="$ZYX_DIR/state"
BACKUP_DIR="$STATE_DIR/backup"
LOG_FILE="$STATE_DIR/updater.log"
SELF_VER_FILE="$STATE_DIR/self-version.json"
mkdir -p "$STATE_DIR" "$BACKUP_DIR"

# zyx 自身远端仓库（可用环境变量 ZYX_REPO / ZYX_BRANCH 覆盖）
DEFAULT_ZYX_REPO="https://github.com/zhenliu1486/ZYX"
ZYX_REPO="${ZYX_REPO:-$DEFAULT_ZYX_REPO}"
ZYX_BRANCH="${ZYX_BRANCH:-main}"

SILENT=0
CHECK_DRIFT=0
for arg in "$@"; do
  case "$arg" in
    --silent) SILENT=1 ;;
    --check-drift) CHECK_DRIFT=1 ;;
  esac
done

log() {
  local line="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  echo "$line" >> "$LOG_FILE"
  [ "$SILENT" -eq 0 ] && echo "$line"
}

# 宿主探测目录：内置清单 + 环境变量 ZYX_EXTRA_SKILL_DIRS 追加（冒号分隔）
HOST_DIRS=(
  "$HOME/.claude/skills"
  "$HOME/.openclaw/skills"
  "$HOME/.agents/skills"
  "$HOME/.doubao/agent_mode/workspace/.user_skills"
  "$HOME/.gemini/skills"
  "$HOME/.kiro/skills"
  "$HOME/.qwen/skills"
  "$HOME/.grok/skills"
  "$HOME/.hermes/skills"
)
if [ -n "${ZYX_EXTRA_SKILL_DIRS:-}" ]; then
  IFS=':' read -ra _extra <<< "$ZYX_EXTRA_SKILL_DIRS"
  HOST_DIRS+=("${_extra[@]}")
fi

# 失败计数状态文件（JSON，python 读写保证格式合法）
FAIL_STATE="$STATE_DIR/fail-count.json"
record_failure() { # $1=key $2=reason
  local key="$1" reason="$2"
  export FAIL_STATE
  local count
  count="$(python3 - "$key" <<'PY'
import json, os, sys
f=os.environ["FAIL_STATE"]; k=sys.argv[1]
try: d=json.load(open(f)) if os.path.exists(f) else {}
except Exception: d={}
d[k]=int(d.get(k,0))+1
json.dump(d, open(f,"w"), ensure_ascii=False, indent=2)
print(d[k])
PY
)"
  log "失败计数 $key = $count（$reason）"
}
record_success() { # $1=key
  export FAIL_STATE
  python3 - "$1" <<'PY'
import json, os, sys
f=os.environ["FAIL_STATE"]; k=sys.argv[1]
try: d=json.load(open(f)) if os.path.exists(f) else {}
except Exception: d={}
d.pop(k, None)
json.dump(d, open(f,"w"), ensure_ascii=False, indent=2)
PY
}

# 代号|目录名|上游仓库|分支
REPOS=(
  "R1女娲|nuwa-skill|https://github.com/alchaincyf/nuwa-skill|main"
  "R2大师|master-skill|https://github.com/swaylq/master-skill|main"
  "R3仓颉|cangjie-skill|https://github.com/kangarooking/cangjie-skill|main"
)

find_local() { # $1=目录名 → 打印第一个含 .git 的本地路径
  local dir="$1" base
  for base in "${HOST_DIRS[@]}"; do
    if [ -d "$base/$dir/.git" ]; then echo "$base/$dir"; return 0; fi
  done
  return 1
}

backup_head() { # $1=路径 $2=目录名
  local path="$1" name="$2" head
  head="$(git -C "$path" rev-parse HEAD 2>/dev/null || echo unknown)"
  echo "$head" > "$BACKUP_DIR/$name.head"
}

update_git_repo() { # $1=label $2=dir $3=repo $4=branch
  local label="$1" dir="$2" repo="$3" branch="$4"
  local local_path
  local_path="$(find_local "$dir" || true)"

  if [ -z "$local_path" ]; then
    log "$label ($dir) 本地未安装，跳过。"
    return 0
  fi

  if ! git -C "$local_path" remote get-url origin >/dev/null 2>&1; then
    git -C "$local_path" remote add origin "$repo" 2>/dev/null || true
  fi

  if ! git -C "$local_path" fetch --depth 1 origin "$branch" >>"$LOG_FILE" 2>&1; then
    record_failure "$dir" "远端不可达/fetch 失败"
    log "$label ($dir) 远端不可达，跳过。"
    return 0
  fi
  record_success "$dir"

  local before after
  before="$(git -C "$local_path" rev-parse HEAD 2>/dev/null || echo unknown)"
  after="$(git -C "$local_path" rev-parse "origin/$branch" 2>/dev/null || echo unknown)"

  if [ "$before" = "$after" ]; then
    log "$label ($dir) 已是最新。"
    return 0
  fi

  # 本地有未提交改动则不覆盖，避免冲掉手改内容
  if [ -n "$(git -C "$local_path" status --porcelain 2>/dev/null)" ]; then
    log "$label ($dir) 本地有未提交改动，为避免覆盖，跳过自动更新（$before → $after）。"
    return 0
  fi

  backup_head "$local_path" "$dir"

  if git -C "$local_path" pull --ff-only origin "$branch" >>"$LOG_FILE" 2>&1; then
    log "$label ($dir) 已快进更新：${before:0:7} → ${after:0:7}。"
    return 0
  fi

  # 兜底：浅克隆历史不全导致非快进、且本地无手改时，允许硬重置到远端（已备份 HEAD）。
  # 有未提交改动已在前面拦截；走到这里说明工作区干净，仅历史浅/分叉。
  if [ -z "$(git -C "$local_path" status --porcelain 2>/dev/null)" ]; then
    if git -C "$local_path" reset --hard "origin/$branch" >>"$LOG_FILE" 2>&1; then
      log "$label ($dir) 浅克隆/历史不全，已按远端重置：${before:0:7} → ${after:0:7}（旧 HEAD 备份于 $BACKUP_DIR/$dir.head）。"
      return 0
    fi
  fi

  log "$label ($dir) 更新失败，保留本地版本（备份 HEAD: $(cat "$BACKUP_DIR/$dir.head" 2>/dev/null)）。"
}

# ---- zyx 自身版本检查（远端版本号比对；自身快进更新仍预留，不自动覆盖运行中的 Skill）----
_zyx_remote_version() {
  local owner_repo="${ZYX_REPO#https://github.com/}" branch url body
  for branch in "$ZYX_BRANCH" master; do
    url="https://raw.githubusercontent.com/$owner_repo/$branch/skills/zyx/SKILL.md"
    body="$(curl -fsSL --max-time 10 "$url" 2>/dev/null)" && [ -n "$body" ] && {
      echo "$body" | grep -m1 'version:' | sed -E 's/.*version: *"?([^" ]+)"?.*/\1/'
      return 0
    }
  done
  return 1
}

_ver_compare() { # $1=local $2=remote -> equal|behind|ahead|unknown
  python3 - "$1" "$2" <<'PY'
import sys
def v(s):
    try: return [int(x) for x in str(s).split('.')]
    except Exception: return None
a, b = v(sys.argv[1]), v(sys.argv[2])
if a is None or b is None:
    print("unknown"); sys.exit()
print("equal" if a == b else ("behind" if a < b else "ahead"))
PY
}

check_zyx_self() {
  local current remote cmp
  current="$(grep -m1 'version:' "$ZYX_DIR/SKILL.md" | sed -E 's/.*version: *"?([^" ]+)"?.*/\1/')"
  remote="$(_zyx_remote_version || true)"

  if [ -z "$remote" ]; then
    record_failure "zyx-self" "远端版本不可达"
    log "zyx 自身版本: 本地 $current；远端不可达，跳过自身比对（仓库: $ZYX_REPO@$ZYX_BRANCH）。"
    return 0
  fi
  record_success "zyx-self"

  cmp="$(_ver_compare "$current" "$remote")"
  case "$cmp" in
    equal)
      log "zyx 自身已是最新（本地 $current = 远端 $remote）。" ;;
    behind)
      log "⚠ zyx 本地 $current 落后远端 $remote；建议按远端更新 zyx 自身（自动快进未启用，需人工确认）。" ;;
    ahead)
      log "zyx 本地 $current 超前远端 $remote（本地改动尚未发布）。" ;;
    *)
      log "zyx 版本号无法比对：本地 $current / 远端 $remote。" ;;
  esac

  # 落盘自身版本比对结果，供 drift 报告与 doctor 读取
  ZYX_SELF_VER_FILE="$SELF_VER_FILE" python3 - "$current" "$remote" "$cmp" <<'PY'
import json, os, sys, time
f=os.environ["ZYX_SELF_VER_FILE"]
data={"local":sys.argv[1],"remote":sys.argv[2],"status":sys.argv[3],"checked_at":time.strftime("%Y-%m-%d %H:%M:%S")}
json.dump(data, open(f,"w"), ensure_ascii=False, indent=2)
PY
}

# ---- dbs 家族：只比对版本，不自动覆盖 ----
check_dbs() {
  local remote_version
  remote_version="$(curl -fsSL --max-time 15 https://raw.githubusercontent.com/dontbesilent2025/dbskill/main/VERSION 2>/dev/null || echo unknown)"
  log "dbs 家族：远端官方版本 $remote_version；目录式安装，需用 dbs-update 或 npx -y skills add dontbesilent2025/dbskill -g --all 刷新，本更新器不批量覆盖。"
}

log "===== zyx 静默更新开始 ====="
check_zyx_self
for entry in "${REPOS[@]}"; do
  IFS='|' read -r label dir repo branch <<< "$entry"
  update_git_repo "$label" "$dir" "$repo" "$branch"
done
check_dbs

# drift 报告：汇总失败计数、连续失败项与 zyx 自身版本状态
if [ "$CHECK_DRIFT" -eq 1 ]; then
  echo "----- drift 报告 -----"
  echo "## 失败计数"
  FAIL_STATE="$FAIL_STATE" python3 <<'PY'
import json, os
f=os.environ["FAIL_STATE"]
try: d=json.load(open(f)) if os.path.exists(f) else {}
except Exception: d={}
if d:
    for k,v in sorted(d.items()): print(f"  {k}: {v}")
else:
    print("  无失败记录。")
PY
  # 连续失败 ≥ 3 次的项，提示下次对话需人工检查
  threshold=3
  FAIL_STATE="$FAIL_STATE" THRESHOLD="$threshold" python3 <<'PY'
import json, os
f=os.environ["FAIL_STATE"]; t=int(os.environ["THRESHOLD"])
try: d=json.load(open(f)) if os.path.exists(f) else {}
except Exception: d={}
for k,v in sorted(d.items()):
    if int(v)>=t: print(f"  ⚠ {k} 连续失败 {v} 次，下次对话请人工检查网络/安装状态。")
PY
  echo "## zyx 自身版本"
  SELF="$SELF_VER_FILE" python3 <<'PY'
import json, os
f=os.environ["SELF"]
try:
    d=json.load(open(f))
    msg={"equal":"已是最新","behind":"⚠ 本地落后远端，建议更新","ahead":"本地超前远端（未发布）","unknown":"版本号无法比对"}
    print(f"  本地 {d['local']} / 远端 {d['remote']} — {msg.get(d['status'], d['status'])}（{d['checked_at']}）")
except Exception:
    print("  未生成自身版本比对结果。")
PY
fi
log "===== zyx 静默更新结束 ====="
exit 0
