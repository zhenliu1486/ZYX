#!/usr/bin/env bash
# env-registry.sh — 首次执行 zyx 时自动探测环境并注册后台更新任务。
# 幂等：重复执行不会重复注册；已注册则跳过。
#
# 设计原则：
# - 只注册「静默更新」任务，不改动任何 Skill 方法论文件。
# - 探测到哪种调度器就用哪种；都不支持时给出降级提示，不报错中断主流程。
# - 注册动作只写本机调度配置，不访问远端、不推送任何内容。
#
# 用法:
#   bash env-registry.sh                # 自动探测并注册
#   bash env-registry.sh --status       # 查看注册状态
#   bash env-registry.sh --unregister   # 移除已注册的调度项（不删 Skill 文件）

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ZYX_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
STATE_DIR="$ZYX_DIR/state"
STATE_FILE="$STATE_DIR/registry.json"
UPDATER="$SCRIPT_DIR/updater.sh"
CRON_MARKER="# zyx-autoupdate"
WEEKLY_MIN="0"   # 周日 18:00
WEEKLY_HOUR="18"

mkdir -p "$STATE_DIR"

log() { echo "[env-registry] $*"; }

# 解析 updater 绝对路径（兼容含空格路径）
UPDATER_ESC="$(printf '%q' "$UPDATER")"

detect_scheduler() {
  # 依次判断本机可用的调度器，输出名称
  if command -v crontab >/dev/null 2>&1 && [ -d "$HOME" ]; then echo "cron"; return 0; fi
  if command -v launchctl >/dev/null 2>&1; then echo "launchd"; return 0; fi
  if command -v systemctl >/dev/null 2>&1 && [ -d "$HOME/.config/systemd/user" ]; then echo "systemd"; return 0; fi
  echo "none"
}

write_state() { # $1=scheduler $2=entry
  local scheduler="$1" entry="$2"
  cat > "$STATE_FILE" <<EOF
{
  "registered_at": "$(date -Iseconds 2>/dev/null || date)",
  "scheduler": "$scheduler",
  "entry": "$entry"
}
EOF
}

register_cron() {
  local line="$CRON_MARKER"
  local job="$WEEKLY_MIN $WEEKLY_HOUR * * 0 $UPDATER_ESC --silent >> \"$STATE_DIR/updater.log\" 2>&1 $line"
  # 去重：先删旧的 zyx 条目
  local current; current="$(crontab -l 2>/dev/null | grep -v "$CRON_MARKER" || true)"
  ( [ -n "$current" ] && echo "$current"; echo "$job" ) | crontab -
  write_state "cron" "$job"
  log "已通过 crontab 注册周检任务（每周日 $WEEKLY_HOUR:00）。"
}

register_launchd() {
  local label="com.zyx.autoupdate"
  local plist="$HOME/Library/LaunchAgents/$label.plist"
  mkdir -p "$HOME/Library/LaunchAgents"
  cat > "$plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$label</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>$UPDATER</string>
    <string>--silent</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key><integer>0</integer>
    <key>Hour</key><integer>$WEEKLY_HOUR</integer>
    <key>Minute</key><integer>$WEEKLY_MIN</integer>
  </dict>
  <key>StandardOutPath</key><string>$STATE_DIR/updater.log</string>
  <key>StandardErrorPath</key><string>$STATE_DIR/updater.log</string>
</dict>
</plist>
EOF
  launchctl unload "$plist" 2>/dev/null || true
  launchctl load "$plist" 2>/dev/null || true
  write_state "launchd" "$plist"
  log "已通过 launchd 注册周检任务（每周日 $WEEKLY_HOUR:00）。"
}

register_systemd() {
  local unit="zyx-autoupdate.service"
  local timer="zyx-autoupdate.timer"
  local dir="$HOME/.config/systemd/user"
  mkdir -p "$dir"
  cat > "$dir/$unit" <<EOF
[Unit]
Description=zyx silent updater

[Service]
Type=oneshot
ExecStart=/bin/bash $UPDATER --silent
EOF
  cat > "$dir/$timer" <<EOF
[Unit]
Description=zyx weekly update timer

[Timer]
OnCalendar=Sun *-*-* $WEEKLY_HOUR:$WEEKLY_MIN:00
Persistent=true

[Install]
WantedBy=timers.target
EOF
  systemctl --user daemon-reload 2>/dev/null || true
  systemctl --user enable --now "$timer" 2>/dev/null || true
  write_state "systemd" "$dir/$timer"
  log "已通过 systemd user timer 注册周检任务（每周日 $WEEKLY_HOUR:00）。"
}

cmd_status() {
  if [ -f "$STATE_FILE" ]; then
    log "注册状态："
    cat "$STATE_FILE"
  else
    log "尚未注册。"
  fi
}

cmd_unregister() {
  if command -v crontab >/dev/null 2>&1; then
    local current; current="$(crontab -l 2>/dev/null | grep -v "$CRON_MARKER" || true)"
    echo "$current" | crontab -
  fi
  launchctl unload "$HOME/Library/LaunchAgents/com.zyx.autoupdate.plist" 2>/dev/null || true
  rm -f "$HOME/Library/LaunchAgents/com.zyx.autoupdate.plist" 2>/dev/null || true
  systemctl --user disable --now zyx-autoupdate.timer 2>/dev/null || true
  rm -f "$HOME/.config/systemd/user/zyx-autoupdate."{service,timer} 2>/dev/null || true
  rm -f "$STATE_FILE"
  log "已移除已注册的调度项（Skill 文件保留）。"
}

case "${1:-}" in
  --status) cmd_status; exit 0 ;;
  --unregister) cmd_unregister; exit 0 ;;
  "") ;;
  *) echo "未知参数: $1"; exit 2 ;;
esac

# 已注册则幂等跳过
if [ -f "$STATE_FILE" ]; then
  log "已注册过，跳过重复注册。"
  cmd_status
  exit 0
fi

scheduler="$(detect_scheduler)"
case "$scheduler" in
  cron) register_cron ;;
  launchd) register_launchd ;;
  systemd) register_systemd ;;
  none)
    log "未检测到可用调度器（cron/launchd/systemd 均不可用）。"
    log "降级方案：在当前 Agent 对话框的定时任务中心，手动注册一条每周日 $WEEKLY_HOUR:00 的任务，命令：bash $UPDATER --silent"
    exit 0
    ;;
esac
