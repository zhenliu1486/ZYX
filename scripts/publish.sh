#!/usr/bin/env bash
# publish.sh — 登录后把本仓库发布到 GitHub（ZYX）。
# 用法:
#   bash scripts/publish.sh [private|public] [tag]
# 前置: 先完成 GitHub 登录（gh auth login 或 gh auth login --with-token）。
# 说明: 本脚本只做建仓/提交/打 tag/推送；不改动 skills 内部方法论。

set -euo pipefail

REPO_NAME="ZYX"
VISIBILITY="${1:-public}"
TAG="${2:-v1.5.0}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# 1. 校验登录状态
if ! gh auth status >/dev/null 2>&1; then
  echo "❌ 尚未登录 GitHub。请先执行其一："
  echo "   gh auth login                       # 设备码 / 浏览器授权"
  echo "   gh auth login --with-token <token>  # 粘贴带 repo 权限的 PAT"
  exit 1
fi

# 2. 取 GitHub 身份并写本地 git 配置（不污染全局）
LOGIN="$(gh api user --jq .login 2>/dev/null || echo "")"
GUNAME="$(gh api user --jq .name 2>/dev/null || true)"
GUEMAIL="$(gh api user --jq .email 2>/dev/null || true)"
[ -z "${GUNAME:-}" ] && GUNAME="$LOGIN"
[ -z "${GUEMAIL:-}" ] && GUEMAIL="${LOGIN}@users.noreply.github.com"

git init -q 2>/dev/null || true
git config user.name "$GUNAME"
git config user.email "$GUEMAIL"
echo "✓ git 身份: $GUNAME <$GUEMAIL>"

# 3. 提交本地改动
git add -A
if git diff --cached --quiet; then
  echo "ℹ 无待提交改动。"
else
  git commit -m "chore: release $TAG — zyx 调度台 + video-studio 聚合层 + 内置 R5/R6 子技能"
fi

# 4. 建仓并推送（远端已存在则只推送）
if ! git remote get-url origin >/dev/null 2>&1; then
  gh repo create "$REPO_NAME" "--$VISIBILITY" --source=. --remote=origin --push
else
  echo "ℹ origin 已存在，直接推送。"
  git push -u origin "$(git branch --show-current 2>/dev/null || echo main)"
fi

# 5. 打 tag 并推送
git tag "$TAG" 2>/dev/null || echo "ℹ tag $TAG 已存在。"
git push origin "$TAG" || true

echo "✓ 发布完成: https://github.com/$LOGIN/$REPO_NAME  (tag: $TAG, 可见性: $VISIBILITY)"
