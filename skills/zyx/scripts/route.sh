#!/usr/bin/env bash
# route.sh — 打印路由决策与被调 Skill 路径（zyx 第 1 层薄壳辅助脚本）
# 用法: route.sh <原料类型: persona|person|industry|content|problem|production|iterate|wiki|invest|phone>
# 仅做路径解析与提示，不执行蒸馏、不修改任何文件。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib-common.sh
source "$SCRIPT_DIR/lib-common.sh"

TARGET="${1:-}"

resolve() { # $1=目录名  $2=环境变量名
  local dir="$1" envvar="$2" p=""
  if [ -n "${!envvar:-}" ] && [ -f "${!envvar}/SKILL.md" ]; then
    p="${!envvar}"
  else
    p="$(find_local "$dir")" || return 1
  fi
  (cd "$p" && pwd)
}

case "$TARGET" in
  persona)
    echo "路由 → R1·库 zhenliu 人物库（先查库：命中读人物包，未命中转 R1 女娲造完回库）"
    p="$(resolve zhenliu ZHENLIU_DIR)" || { echo "未检测到 zhenliu 人物库，请先安装：git clone https://github.com/zhenliu1486/zhenliu && cd zhenliu && bash scripts/install.sh" >&2; exit 2; }
    echo "$p"
    echo "衔接：库里没有该人物时转 nuwa-skill 蒸馏，产物回库登记"
    ;;

  phone)
    echo "路由 → R0 手机操作 pinky（工具层；需要 Pinky App + 手机 + MCP）"
    p="$(resolve pinky PINKY_SKILL_DIR)" || { echo "未检测到 pinky 技能，请重装 ZYX 或从 https://github.com/DIYgod/pinky 安装" >&2; exit 2; }
    echo "$p"
    echo "前提：Pinky 桌面端已安装、手机已连接、宿主已接入 pinky MCP；步骤见 $p/SETUP.md"
    ;;
  person)
    echo "路由 → R1 女娲 nuwa-skill（蒸馏一个人的思维方式）"
    p="$(resolve nuwa-skill NUWA_SKILL_DIR)" || { echo "未检测到 nuwa-skill，请先安装：https://github.com/alchaincyf/nuwa-skill" >&2; exit 2; }
    echo "$p"
    ;;
  industry)
    echo "路由 → R2 大师 master-skill（蒸馏一个细分行业）"
    p="$(resolve master-skill MASTER_SKILL_DIR)" || { echo "未检测到 master-skill，请先安装：https://github.com/swaylq/master-skill" >&2; exit 2; }
    echo "$p"
    echo "衔接：Phase 3 人物 sub-skill 委派 R1 女娲"
    ;;
  content)
    echo "路由 → R3 仓颉 cangjie-skill（蒸馏长内容方法论）"
    p="$(resolve cangjie-skill CANGJIE_SKILL_DIR)" || { echo "未检测到 cangjie-skill，请先安装：https://github.com/kangarooking/cangjie-skill" >&2; exit 2; }
    echo "$p"
    echo "衔接：无文字稿先走 dbs-video-extract / 本地转写；阶段 4 压测兼容 Darwin 底座"
    ;;
  problem)
    echo "路由 → R4 dbs 家族（当下问题：诊断/文案/决策/协作）"
    p="$(resolve dbs DBS_SKILL_DIR)" || { echo "未检测到 dbs 主调度台，请先安装：https://github.com/dontbesilent2025/dbskill" >&2; exit 2; }
    echo "$p"
    ;;
  production)
    echo "路由 → R5 video-studio 影视制作聚合层（内部路由剧本/编剧/人物/场景/动作/表情/全流程）"
    p="$(resolve video-studio VIDEO_STUDIO_DIR)" || { echo "未检测到 video-studio 聚合层" >&2; exit 2; }
    echo "$p"
    ;;
  iterate)
    echo "路由 → R6 f2r-feedback-iteration（已有产物二次迭代：负反馈显性化 + 小样本回归）"
    p="$(resolve f2r-feedback-iteration F2R_SKILL_DIR)" || { echo "未检测到 f2r-feedback-iteration" >&2; exit 2; }
    echo "$p"
    ;;
  invest)
    echo "路由 → R8 ashare-four-dim-decision 投资决策总控（内部读取四个四维子技能：情绪/风口/资金/技术）"
    p="$(resolve ashare-four-dim-decision ASHARE_DECISION_DIR)" || { echo "未检测到 ashare-four-dim-decision，请重装 ZYX：https://github.com/zhenliu1486/ZYX" >&2; exit 2; }
    echo "$p"
    echo "子技能：ashare-sentiment-cycle / ashare-theme-wind / ashare-capital-flow / ashare-technical-structure（同级目录）"
    echo "衔接：打分用 scripts/score.py；方案输出到日到时段，不代下单、不承诺收益"
    ;;
  wiki)
    echo "路由 → R7 wiki-vault 长期知识库（建库/摄入编译/库内问答/健康巡检；可挂载已有 Obsidian 库）"
    p="$(resolve wiki-vault WIKI_VAULT_DIR)" || { echo "未检测到 wiki-vault" >&2; exit 2; }
    echo "$p"
    ;;
  *)
    echo "用法: route.sh <persona|person|industry|content|problem|production|iterate|wiki|invest|phone>"
    echo "  persona    人物视角/人物库 → zhenliu（命中就用，未命中转女娲）"
    echo "  person     人     → 女娲"
    echo "  industry   行业   → 大师"
    echo "  content    长内容 → 仓颉"
    echo "  problem    问题   → dbs"
    echo "  production 内容生产 → video-studio"
    echo "  iterate    产物迭代 → f2r"
    echo "  wiki       长期知识库 → wiki-vault"
    echo "  invest     投资决策（股票/波段/超短线）→ ashare-four-dim-decision"
    echo "  phone      手机操作（可选）→ pinky（需另装 Pinky App/MCP）"
    exit 1
    ;;
esac
