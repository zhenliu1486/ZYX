---
name: zyx
description: zyx 总调度台（薄壳路由入口）。当用户要把人、行业、长内容（书/长视频/播客/课程/访谈）蒸馏成 Skill，要处理当下的商业/文案/决策问题，要做影视/短剧/漫剧内容生产，或要对已有产物二次迭代时使用。只判断原料属于哪一类，转发给女娲 nuwa-skill、大师 master-skill、仓颉 cangjie-skill、dbs 家族、video-studio 聚合层或 f2r 迭代器，不自行产出方法论；产物按「生成它的 Skill 名分目录」落到桌面产物目录，再由 zyx 统一回传。触发词：zyx、调度、路由、造 skill、蒸馏、拆书、做个 X 的 master、我是 X 行业、诊断我的生意、这篇文案行不行、写短剧剧本、出分镜、改这版产物。
license: MIT
compatibility: 兼容 Claude Code / Codex / OpenClaw / Hermes / Kiro / Cline 等 Agent Skills 标准宿主；引用外部蒸馏器路径，需与它们同机安装。
metadata:
  author: "ZYX"
  version: "1.0.2"
  layer: "1-router"
  schema: "agentskills.io"
allowed-tools: Read, Write, Edit, Bash, WebSearch, WebFetch
---

# zyx · 总调度台（第 1 层 · 路由薄壳）

> 本 skill **只做路由与收口**，不含任何蒸馏方法论。方法论分别驻留在三个独立蒸馏器和 dbs 家族；公共校验、质检、可信度、产物规范与压测用例放在第 3 层 `shared/`，被各蒸馏器引用。

## 1. 三层结构总览

```
zyx/                                  # 第 1 层：入口路由（本目录，薄壳）
├── SKILL.md                          #   判断原料类型 → 转发 → 收口产物
├── references/
│   ├── routing-table.md               #   四类原料的判定信号与分流规则
│   └── artifact-layout.md            #   产物目录命名与回传规范（与 shared/artifacts 对齐）
├── scripts/
│   ├── route.sh                       #   打印当前路由决策与被调 Skill 路径
│   ├── env-registry.sh                #   首次触发探测环境并注册后台更新任务（幂等）
│   ├── updater.sh                      #   后台静默更新器：快进更新 + 备份回滚 + 失败计数 + drift 报告 + 自身版本检查
│   ├── check-updates.sh              #   手动检查入口（复用 updater 检查逻辑，只读报告）
│   ├── desktop-dir.sh                #   桌面目录跨平台探测与回退顺序
│   ├── artifact-dir.sh                #   给定来源+产物名+日期，返回/创建规范产物目录
│   └── doctor.sh                      #   自检：就绪状态、缺什么、怎么补
├── evals/                             #   路由回归用例（人/行业/内容/问题/生产/迭代）
├── state/                             #   注册状态、更新日志、备份 HEAD（本机运行态，不发布）
├── shared/                            # 第 3 层：共享底座（抽自三方重复部分）
│   ├── verification/                  #   增量认知校验 + 三重交叉验证
│   ├── quality/                       #   质检与审计清单
│   ├── credibility/                   #   来源可信度标注口径
│   ├── artifacts/                      #   产物目录规范与模板
│   └── darwin/                         #   Darwin 式压测用例（兼容达尔文 skill）
└── assets/
```

第 2 层是三个**保持独立、各自追上游 git 更新**的蒸馏器，zyx 只引用它们的安装路径，不复制、不内嵌其方法论：

| 编号 | 蒸馏器 | 上游仓库 | 角色 |
|---|---|---|---|
| R1 | 女娲 `nuwa-skill` | alchaincyf/nuwa-skill | 蒸馏**一个人**的思维方式 / 名人 OS |
| R2 | 大师 `master-skill` | swaylq/master-skill | 蒸馏**一个细分行业**的 Master OS（Phase 3 内部调女娲出人物 sub-skill） |
| R3 | 仓颉 `cangjie-skill` | kangarooking/cangjie-skill | 蒸馏**长内容**（书/长视频/播客/课程/访谈）的方法论为 Skill 包 |
| R4 | dbs 家族 | dontbesilent2025/dbskill | 处理**当下问题**：商业诊断、文案、决策复盘、协作派单（不产出新 Skill） |
| R5 | `video-studio` 聚合层 | 本地聚合（子技能见其 SKILL.md） | **影视/短剧/漫剧内容生产**：内部路由剧本、编剧、人物、场景、动作分镜、表情参数、全流程 SOP |
| R6 | `f2r-feedback-iteration` | 本地打磨类子技能 | **已有产物二次迭代**：按反馈显性化为规则，小样本迭代 + 回归测试 |

## 2. 工作流程（首次自注册 → 路由 → 转发 → 收口）

### Step 0 · 首次触发：环境探测与后台自注册（幂等）
每次 zyx 被调用时，先检查 `state/registry.json` 是否已存在：
- **未注册过**：运行 `bash scripts/env-registry.sh`，自动探测本机可用调度器（cron / launchd / systemd；云端 Agent 则降级为提示在定时任务中心建任务），注册一条每周日 18:00 的后台静默更新任务；注册结果写入 `state/registry.json`。
- **已注册**：跳过，不重复注册。
- 注册动作只写本机调度配置，不访问远端、不推送内容；调度器不可用时不中断主流程，只记录降级提示。

### Step 1 · 读取原料，判定类型
先读用户原话、附件和对话已有事实，不要求用户重复背景。按 `references/routing-table.md` 的判定信号，把原料归入六类之一（R1 人 / R2 行业 / R3 长内容 / R4 当下问题 / R5 内容生产 / R6 产物迭代）；信号冲突或模糊时，**一次问清**属于哪类，不要猜着分流。

### Step 2 · 解析目标蒸馏器的绝对路径
按 `references/routing-table.md` 末尾的「路径解析」找到对应蒸馏器在本机的安装目录。路径解析顺序：环境变量覆盖 → 本机各宿主 skill 目录探测 → 报错并提示安装。**禁止把蒸馏器方法论复制进 zyx 目录**，zyx 只引用路径。

### Step 3 · 转发并委派
把任务连同原料、约束、产物目录位置交给对应蒸馏器执行：
- **R1 女娲**：明确人名 → 直接蒸馏；只有模糊困惑 → 先走女娲的诊断推荐再蒸馏。
- **R2 大师**：输入细分行业；其 Phase 3 调女娲生成 top3 人物 sub-skill 时，按女娲路径衔接（见 `references/routing-table.md` 衔接段）。
- **R3 仓颉**：长内容需先有文字稿/字幕转写；**无文字稿时先走 `dbs-video-extract` 或本地转写**，拿到文字稿后再进 RIA-TV++ 流水线，压测兼容达尔文（见 `shared/darwin/`）。
- **R4 dbs**：当下问题，按 dbs 主调度台路由到具体子 skill；dbs 不生成可安装 Skill。
- **R5 video-studio**：影视/短剧/漫剧制作，先到聚合层，由其内部路由到剧本/编剧/人物/场景/动作/表情/全流程对应子技能。
- **R6 f2r**：已有产物（Skill / MD 文档）二次修改迭代，指向 f2r 负反馈迭代；需要诊断共鸣断点联动 dbs-resonate，查 AI 味联动 dbs-ai-check。

### Step 4 · 套用共享底座（第 3 层）
委派执行时，要求被调蒸馏器按 `shared/` 下的公共口径工作，避免三方各造一套：
- 增量认知校验：先写下已有认知，再专找反例与增量（`shared/verification/incremental-check.md`）。
- 三重交叉验证：来源充分性 / 可执行性 / 任务增益（`shared/verification/triple-verification.md`）。
- 质检与审计：发布前过清单，留审计痕迹（`shared/quality/qa-audit.md`）。
- 来源可信度标注：一手 / 二手 / 推断分级（`shared/credibility/source-grading.md`）。
- 产物规范与压测：目录结构、命名、Darwin 式用例（`shared/artifacts/`、`shared/darwin/`）。

### Step 5 · 收口产物并回传桌面
产物先落到本机桌面产物根目录，**按生成它的 Skill 名分一级子目录**（规则见 `references/artifact-layout.md` 与 `shared/artifacts/convention.md`）。全部产物就位后，zyx 统一汇总路径清单回传给用户：每个产物标注来源蒸馏器、版本、校验状态与所在目录。回传前按 `shared/quality/qa-audit.md` 做一次交付前核对。

## 3. 边界（zyx 不做什么）

- 不自己调研、不自己提炼方法论、不写蒸馏正文——这些归 R1/R2/R3。
- 不复制、不内嵌、不改写三个蒸馏器的内部文件；它们独立追上游更新。
- 不做无确认的远端动作（建仓、push、tag、Release 单独授权，见 `references/routing-table.md` 发布段）。
- 不把书摘、读后感、作者人设扮演交给仓颉（那是女娲的活）；路由表已写明边界。

## 4. 后台静默更新机制

- **首次自注册**：首次调用 zyx 时 `env-registry.sh` 探测环境并注册周检任务，之后在后台持续运行；注册状态在 `state/registry.json`，重复调用幂等不重复注册。
- **静默更新器** `updater.sh`：每周日 18:00（或手动）执行：
  1. 对女娲/大师/仓颉三个 git 蒸馏器做 `--ff-only` 快进更新；本地有未提交改动或分叉时不强行覆盖，保留本地并记录；更新前备份 HEAD 到 `state/backup/`。
  2. 检查 **zyx 自身版本**：拉取远端 `skills/zyx/SKILL.md` 版本号与本地比对，输出最新/落后/超前；落后时提示人工确认更新，自身快进覆盖仍预留不自动执行。仓库与分支可用 `ZYX_REPO` / `ZYX_BRANCH` 环境变量覆盖。
  3. dbs 家族只比对官方版本并记录差异，不批量自动覆盖（目录式安装，由 dbs-update 处理）。
  4. 失败计数写入 `state/fail-count.json`；连续失败达阈值在下次对话提示；`--check-drift` 输出 drift 报告。
- **日志**：更新过程写入 `state/updater.log`；`--silent` 模式不在前台打印。
- **安全边界**：只快进本地已有仓库，不删除未提交改动、不访问远端写接口、不推送内容；非快进失败自动保留现状。手动只读检查可运行 `bash scripts/check-updates.sh`；环境就绪/缺项可运行 `bash scripts/doctor.sh`。
