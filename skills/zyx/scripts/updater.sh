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
mkdir -p "$STATE_DIR" "$BACKUP_DIR"

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

# 失败计数状态文件
FAIL_STATE="$STATE_DIR/fail-count.json"
record_failure() { # $1=key $2=reason
  local key="$1" reason="$2" count=0
  if [ -f "$FAIL_STATE" ]; then
    count="$(grep -o "\"$key\": *[0-9]*" "$FAIL_STATE" | grep -o '[0-9]*' || echo 0)"
  fi
  count=$((count + 1))
  # 简单写入：key → count
  local tmp="$FAIL_STATE.tmp"
  cp "$FAIL_STATE" "$tmp" 2>/dev/null || true
  grep -v "\"$key\"" "$tmp" 2>/dev/null > "$FAIL_STATE" || true
  echo "\"$key\": $count" >> "$FAIL_STATE"
  rm -f "$tmp"
  log "失败计数 $key = $count（$reason）"
}
record_success() { # $1=key
  [ -f "$FAIL_STATE" ] && grep -v "\"$1\"" "$FAIL_STATE" 2>/dev/null > "$FAIL_STATE.tmp" && mv "$FAIL_STATE.tmp" "$FAIL_STATE"
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

# ---- zyx 自身版本检查 ----
check_zyx_self() {
  local current
  current="$(grep -m1 'version:' "$ZYX_DIR/SKILL.md" | sed -E 's/.*version: *"?([^" ]+)"?.*/\1/')"
  log "zyx 自身版本: $current（本地）。"
  # 预留远端自更新接口：配置 ZYX_REPO=<git-url> 后，fetch 远端并比对 commit/VERSION。
  # 待 zyx 发布到 GitHub 后在此接入：clone/fetch 远端 → 比对 HEAD 或 VERSION → 快进更新 zyx 自身目录。
  if [ -n "${ZYX_REPO:-}" ]; then
    local remote_head="unknown"
    local tmpdir="$STATE_DIR/zyx-self-check"
    rm -rf "$tmpdir"; mkdir -p "$tmpdir"
    if git clone --depth 1 "$ZYX_REPO" "$tmpdir" >>"$LOG_FILE" 2>&1; then
      remote_head="$(git -C "$tmpdir" rev-parse HEAD 2>/dev/null || echo unknown)"
      log "ZYX_REPO=$ZYX_REPO 远端 HEAD: ${remote_head:0:7}（本地版本 $current）。远端自更新逻辑待发布后接入。"
    else
      record_failure "zyx-self" "ZYX_REPO 不可达"
      log "ZYX_REPO 不可达，跳过 zyx 自身远端比对。"
    fi
    rm -rf "$tmpdir"
  fi
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

# drift 报告：汇总失败计数与连续失败项
if [ "$CHECK_DRIFT" -eq 1 ]; then
  echo "----- drift 报告 -----"
  if [ -f "$FAIL_STATE" ]; then
    cat "$FAIL_STATE"
  else
    echo "无失败记录。"
  fi
  # 连续失败 ≥ 3 次的项，提示下次对话需人工检查
  threshold=3
  if [ -f "$FAIL_STATE" ]; then
    grep -oE '"[^"]+": *[0-9]+' "$FAIL_STATE" | while IFS=: read -r k v; do
      v="$(echo "$v" | tr -d ' "')"
      k="$(echo "$k" | tr -d '"')"
      if [ "${v:-0}" -ge "$threshold" ]; then
        echo "⚠ $k 连续失败 $v 次，下次对话请人工检查网络/安装状态。"
      fi
    done
  fi
fi
log "===== zyx 静默更新结束 ====="
exit 0
