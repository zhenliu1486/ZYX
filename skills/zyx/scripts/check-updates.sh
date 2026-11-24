#!/usr/bin/env bash
# check-updates.sh — 手动更新检查入口（兼容旧调用）。
# 只读检查：复用 updater.sh 的检查与报告逻辑；不自动覆盖本地。
# 静默自动更新由 updater.sh 经 env-registry 注册的后台任务执行。

set -uo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$SCRIPT_DIR/updater.sh" "$@"
