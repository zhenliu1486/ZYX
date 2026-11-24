# zyx · 总调度台

> 一个薄壳路由入口 Skill：判断原料是「人 / 行业 / 长内容 / 当下问题 / 内容生产 / 产物迭代」，转发给对应的独立蒸馏器、dbs 家族或聚合层，统一收口产物。三个蒸馏器保持独立、各自追上游 git 更新；公共校验、质检、可信度、产物规范与 Darwin 式压测抽成 `shared/` 共享底座。

## 三层结构

```
zyx/
├── SKILL.md                  # 第 1 层：入口路由（薄壳，不含方法论）
├── references/               # 路由判定表、产物目录与回传规范
├── scripts/                  # route.sh 路由解析；env-registry.sh 自注册；updater.sh 静默更新；
│                             #   doctor.sh 自检；desktop-dir.sh 桌面探测；artifact-dir.sh 规范产物目录
├── shared/                   # 第 3 层：共享底座（三方重复部分抽公共）
│   ├── verification/         #   增量认知校验 + 三重交叉验证
│   ├── quality/              #   质检与审计清单（含发布前脱敏必过项）
│   ├── credibility/          #   来源可信度分级
│   ├── artifacts/            #   产物目录规范与 MANIFEST 模板
│   └── darwin/               #   Darwin 式压测用例口径（兼容达尔文 skill）
├── evals/                    # 路由回归用例（人/行业/内容/问题/生产/迭代各一条）
└── assets/
```

## 路由表

| 原料类型 | 转发到 | 上游仓库 / 来源 | 产物 |
|---|---|---|---|
| 人（思维方式 / 名人 OS） | R1 女娲 `nuwa-skill` | alchaincyf/nuwa-skill | 人物视角 Skill |
| 细分行业 | R2 大师 `master-skill` | swaylq/master-skill | 行业 Master Skill（Phase 3 调女娲出人物 sub-skill） |
| 长内容（书/视频/播客/课程/访谈） | R3 仓颉 `cangjie-skill` | kangarooking/cangjie-skill | 原子能力卡 + Skill 包 |
| 当下问题（诊断/文案/决策/协作） | R4 dbs 家族 | dontbesilent2025/dbskill | 报告 / 成稿 / 决策记录 |
| 影视/短剧/漫剧制作 | R5 `video-studio` 聚合层 | 本地聚合，内部路由子技能 | 剧本 / 设定 / 分镜 / 参数 / 流程方案 |
| 已有产物二次打磨 | R6 `f2r-feedback-iteration` | 本地打磨类子技能 | 迭代后的产物 + 反馈规则记录 |

## 日常调用示例

> 最常见用法：直接把 zyx 发到对话框，再描述你的情况；入口先判断原料类型，再路由。

### 1. 人物蒸馏（R1 女娲）
> 「帮我把查理·芒格的思维方式蒸馏成一个可复用的人物视角 Skill，以后遇到决策先按他的视角想一遍。」

入口判定：原料是「人」→ 路由 R1 女娲；产物落到 `zyx-output/nuwa/`。

### 2. 行业蒸馏（R2 大师）
> 「我想做跨境电商这行，帮我把这行的大佬打法、工具地图、工作流和信息源整理成一个行业 Master Skill。」

入口判定：原料是「行业」→ 路由 R2 大师；Phase 3 出 top3 人物 sub-skill 时内部委派 R1 女娲；产物落到 `zyx-output/master/`。

### 3. 拆书 / 长内容诊断（R3 仓颉）
> 「这是《穷查理宝典》的摘录，帮我提炼成可复用的方法包，压测通过后入库。」

入口判定：原料是「长内容」→ 路由 R3 仓颉；无文字稿时先走 dbs-video-extract / 本地转写，再进仓颉；产物落到 `zyx-output/cangjie/`。

### 4. 生意 / 当下问题诊断（R4 dbs）
> 「我这门小生意现在获客成本越来越高，帮我诊断一下问题出在哪、先改哪一步。」

入口判定：原料是「当下问题」→ 路由 R4 dbs 主调度台，由 dbs 内部再分发；产物落到 `zyx-output/dbs/`。

### 5. 直接生成编导 / 影视脚本（R5 video-studio）
> 「帮我构思一个竖屏复仇短剧的开头三集，人物和场景先定下来，再出打斗戏分镜。」

入口判定：原料是「内容生产」→ 路由 R5 video-studio 聚合层，内部依次路由短剧编剧、人物/场景库、动作分镜子技能；产物落到 `zyx-output/video/`。

## 设计原则

- **入口只做路由与收口**：zyx 不调研、不提炼方法论、不复制蒸馏器内部文件。
- **蒸馏器独立演进**：女娲 / 大师 / 仓颉各自追上游 git 更新，zyx 只引用安装路径。
- **共享底座去重**：增量校验、三重验证、质检审计、可信度标注、产物规范、压测用例只维护一份，三方引用。
- **产物按来源名分目录**：产物落到桌面 `zyx-output/<来源 Skill>/<产物>/`，由 zyx 统一回传路径清单；桌面目录按「桌面 → 文档 → HOME/zyx-output」跨平台回退探测。

## 自检与更新

- **首次触发自注册**：`scripts/env-registry.sh` 探测 cron / launchd / systemd 并幂等注册后台周检；`--status` 查看状态，`--unregister` 卸载。
- **静默更新**：`scripts/updater.sh` 对 R1/R2/R3 做 ff-only 快进 + 浅克隆兜底重置（旧 HEAD 备份），dbs 只比对不覆盖；失败计数、连续失败提示与 drift 报告（`--check-drift`）。zyx 自身版本检查预留 `ZYX_REPO` 接口，发布到远端后接入。
- **自检**：`bash scripts/doctor.sh` 输出就绪状态、缺什么、怎么补。
- **定时周检**：每周日 18:00 触发上游更新检查；纯云端无调度器环境会降级提示。

## 规范对齐

本 Skill 遵循开放 Agent Skills 规范（agentskills.io）：YAML frontmatter（`name` / `description` / `license` / `compatibility` / `metadata` / `allowed-tools`）、渐进式披露（元数据 → 正文 → 按需加载 references/scripts/assets）、正文 500 行以内。模板与标准参考 Anthropic agentskills 开放规范与 Google 官方 skills 仓库格式。

## 安装

把 `zyx/` 目录放到任一宿主的 skill 目录即可，例如：

```bash
# Claude Code
cp -r zyx ~/.claude/skills/zyx
# OpenClaw
cp -r zyx ~/.openclaw/skills/zyx
# 或其他兼容宿主的 skills 目录
```

依赖：被转发的蒸馏器需与本 Skill 同机安装；脚本用 Bash 与 git；仓颉本体另需 Python 3.10+ 与 PyYAML。

## 许可

MIT，见 [LICENSE](LICENSE)。变更记录见 [CHANGELOG.md](CHANGELOG.md)。
