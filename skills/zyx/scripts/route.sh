#!/usr/bin/env bash
# route.sh — 打印路由决策与被调 Skill 路径（zyx 第 1 层薄壳辅助脚本）
# 用法: route.sh <原料类型: person|industry|content|problem|production|iterate>
# 仅做路径解析与提示，不执行蒸馏、不修改任何文件。

set -euo pipefail

TARGET="${1:-}"

# 宿主 skill 探测目录（顺序即优先级）
HOST_DIRS=(
  "$HOME/.claude/skills"
  "$HOME/.openclaw/skills"
  "$HOME/.agents/skills"
  "$HOME/.doubao/agent_mode/workspace/.user_skills"
)

resolve() { # $1=目录名  $2=环境变量名
  local dir="$1" envvar="$2"
  if [ -n "${!envvar:-}" ] && [ -f "${!envvar}/SKILL.md" ]; then
    echo "${!envvar}"; return 0
  fi
  for base in "${HOST_DIRS[@]}"; do
    if [ -f "$base/$dir/SKILL.md" ]; then echo "$base/$dir"; return 0; fi
  done
  return 1
}

case "$TARGET" in
  person)
    echo "路由 → R1 女娲 nuwa-skill（蒸馏一个人的思维方式）"
    resolve nuwa-skill NUWA_SKILL_DIR || echo "未检测到 nuwa-skill，请先安装：https://github.com/alchaincyf/nuwa-skill"
    ;;
  industry)
    echo "路由 → R2 大师 master-skill（蒸馏一个细分行业）"
    resolve master-skill MASTER_SKILL_DIR || echo "未检测到 master-skill，请先安装：https://github.com/swaylq/master-skill"
    echo "衔接：Phase 3 人物 sub-skill 委派 R1 女娲"
    ;;
  content)
    echo "路由 → R3 仓颉 cangjie-skill（蒸馏长内容方法论）"
    resolve cangjie-skill CANGJIE_SKILL_DIR || echo "未检测到 cangjie-skill，请先安装：https://github.com/kangarooking/cangjie-skill"
    echo "衔接：无文字稿先走 dbs-video-extract / 本地转写；阶段 4 压测兼容 Darwin 底座"
    ;;
  problem)
    echo "路由 → R4 dbs 家族（当下问题：诊断/文案/决策/协作）"
    resolve dbs DBS_SKILL_DIR || echo "未检测到 dbs 主调度台，请先安装：https://github.com/dontbesilent2025/dbskill"
    ;;
  production)
    echo "路由 → R5 video-studio 影视制作聚合层（内部路由剧本/编剧/人物/场景/动作/表情/全流程）"
    resolve video-studio VIDEO_STUDIO_DIR || echo "未检测到 video-studio 聚合层"
    ;;
  iterate)
    echo "路由 → R6 f2r-feedback-iteration（已有产物二次迭代：负反馈显性化 + 小样本回归）"
    resolve f2r-feedback-iteration F2R_SKILL_DIR || echo "未检测到 f2r-feedback-iteration"
    ;;
  *)
    echo "用法: route.sh <person|industry|content|problem|production|iterate>"
    echo "  person     人     → 女娲"
    echo "  industry   行业   → 大师"
    echo "  content    长内容 → 仓颉"
    echo "  problem    问题   → dbs"
    echo "  production 内容生产 → video-studio"
    echo "  iterate    产物迭代 → f2r"
    exit 1
    ;;
esac
