---
name: zyx
description: zyx 总调度台（薄壳路由入口）。当用户要把人、行业、长内容（书/长视频/播客/课程/访谈）蒸馏成 Skill，处理当下商业/文案/决策问题，做影视/短剧/漫剧内容生产，对已有产物二次迭代，或维护一个长期累积的个人/领域知识库时使用。只判断原料属于哪一类并转发给对应蒸馏器/聚合层，不自行产出方法论；产物按生成它的 Skill 名分目录落盘后统一回传。生产类触发词：zyx、调度、路由、造 skill、蒸馏、拆书、做个 X 的 master、我是 X 行业、诊断我的生意、这篇文案行不行、写短剧剧本、出分镜、改这版产物、建个知识库、把这篇加进我的库、我库里关于 X、体检我的库、把库带到别的 agent、看这版 PPT 或封面。投资类触发词：投资建议、股票、买哪只、几点买、什么时候买、什么时候卖、仓位怎么分、做波段、超短线、打板、复盘、暗盘资金、止损、该不该割、四维决策。
license: MIT
compatibility: 兼容 Claude Code / Codex / OpenClaw / Hermes / Kiro / Cline 等 Agent Skills 标准宿主；引用外部蒸馏器路径，需与它们同机安装。
metadata:
  author: "ZYX"
  version: "1.6.1"
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
│   ├── routing-table.md               #   八类原料的判定信号与分流规则
│   └── artifact-layout.md            #   产物目录命名与回传规范（与 shared/artifacts 对齐）
├── deps/
│   └── manifest.json                 #   依赖声明清单（来源/安装命令/必需可选/子技能归属），doctor/updater/install 共用
├── scripts/
│   ├── route.sh                       #   打印当前路由决策与被调 Skill 路径
│   ├── lib-common.sh                  #   共用：宿主目录探测、清单读取（被各脚本 source）
│   ├── deps.py                        #   manifest.json 读取器（宿主目录/依赖行/git 仓库）
│   ├── check-integrity.py             #   扫描 Markdown 悬空引用与缺失文件
│   ├── env-registry.sh                #   首次触发探测环境并注册后台更新任务（幂等）
│   ├── updater.sh                      #   后台静默更新器：快进更新 + 备份回滚 + 失败计数 + drift 报告 + 自身版本/SHA 检查
│   ├── check-updates.sh              #   手动检查入口（复用 updater 检查逻辑，只读报告）
│   ├── desktop-dir.sh                #   桌面目录跨平台探测与回退顺序
│   ├── artifact-dir.sh                #   给定来源+产物名+日期，返回/创建规范产物目录
│   └── doctor.sh                      #   自检：就绪状态、依赖状态、文件完整性、缺什么、怎么补
├── evals/                             #   路由回归用例（人/行业/内容/问题/生产/迭代/降级/版本/脱敏）
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
| R5 | `video-studio` 聚合层 | 随仓库内置（子技能随仓库内置） | **影视/短剧/漫剧内容生产**：内部路由剧本、编剧、人物、场景、动作分镜、表情参数、全流程 SOP |
| R6 | `f2r-feedback-iteration` | 随仓库内置 | **已有产物二次迭代**：按反馈显性化为规则，小样本迭代 + 回归测试 |
| R7 | `wiki-vault` | 随仓库内置 | **长期知识库（个人/领域 Wiki）**：`raw/` 只读原料 → `wiki/` 编译成互链 Obsidian Markdown；支持挂载已有 Obsidian 库；单写锁 + lint 巡检 |
| R8 | `ashare-four-dim-decision` + 4 子技能 | 随仓库内置 | **投资决策（A 股波段 / 超短线）**：情绪偏好 · 市场风口 · 资金流向（含暗盘）· 技术面四维加权，动态权重 + 一票否决闸门 → 到日到时段的具体操作方案 |
| 可选 | `darwin-skill` | alchaincyf/darwin-skill | Darwin 式压测本体；`shared/darwin/` 只引用口径，不内嵌本体 |

> 依赖的来源、安装命令、必需/可选与子技能归属，统一登记在 `deps/manifest.json`；新增或调整依赖只改这一份清单。

## 2. 工作流程（首次自注册 → 路由 → 转发 → 收口）

### Step 0 · 首次触发：环境探测与后台自注册（幂等）
每次 zyx 被调用时，先检查 `state/registry.json` 是否已存在：
- **未注册过**：运行 `bash scripts/env-registry.sh`，自动探测本机可用调度器（cron / launchd / systemd；云端 Agent 则降级为提示在定时任务中心建任务），注册一条每周日 18:00 的后台静默更新任务；注册结果写入 `state/registry.json`。
- **已注册**：跳过，不重复注册。
- 注册动作只写本机调度配置，不访问远端、不推送内容；调度器不可用时不中断主流程，只记录降级提示。

### Step 1 · 读取原料，判定类型
先读用户原话、附件和对话已有事实，不要求用户重复背景。按 `references/routing-table.md` 的判定信号，把原料归入八类之一（R1 人 / R2 行业 / R3 长内容 / R4 当下问题 / R5 内容生产 / R6 产物迭代 / R7 长期知识库 / R8 投资决策）；信号冲突或模糊时，**一次问清**属于哪类，不要猜着分流。

### Step 2 · 解析目标蒸馏器的绝对路径
按 `references/routing-table.md` 末尾的「路径解析」找到对应蒸馏器在本机的安装目录。路径解析顺序：环境变量覆盖 → 本机各宿主 skill 目录探测 → 报错并提示安装。**禁止把蒸馏器方法论复制进 zyx 目录**，zyx 只引用路径。

### Step 3 · 转发并委派
把任务连同原料、约束、产物目录位置交给对应蒸馏器执行：
- **R1 女娲**：明确人名 → 直接蒸馏；只有模糊困惑 → 先走女娲的诊断推荐再蒸馏。
- **R2 大师**：输入细分行业；其 Phase 3 调女娲生成 top3 人物 sub-skill 时，按女娲路径衔接（见 `references/routing-table.md` 衔接段）。
- **R3 仓颉**：长内容需先有文字稿/字幕转写；**无文字稿时先走 `dbs-video-extract` 或本地转写**，拿到文字稿后再进 RIA-TV++ 流水线，压测兼容达尔文（见 `shared/darwin/`）。
- **R4 dbs**：当下问题，按 dbs 主调度台路由到具体子 skill；dbs 不生成可安装 Skill。
- **R5 video-studio**：影视/短剧/漫剧制作，先到聚合层，由其内部路由到剧本/编剧/人物/场景/动作/表情/全流程对应子技能。
- **R8 投资决策**：A 股个股/组合的买卖判断与执行方案。先判市场状态取动态权重（单边趋势 / 震荡结构 / 题材亢奋 / 退潮冰点 / 系统性风险），四维打分后过一票否决闸门，再映射仓位，最后给出精确到日期与盘中时段（09:15-09:25 / 09:30-10:00 / 14:30-14:50）的动作与触发条件。只做研究框架输出，不下单、不承诺收益。
- **R7 wiki-vault**：长期知识库建库/摄入编译/库内问答/巡检。已有 Obsidian 库用 `mount` 挂载、不重构；写操作先取单写锁，未持锁脚本拒绝；不设覆盖度闸门；库内页晋级成 Skill 需过三重验证 + 具备独立复用价值。
- **R6 f2r**：已有产物（Skill / MD 文档）二次修改迭代，指向 f2r 负反馈迭代；需要诊断共鸣断点联动 dbs-resonate，查 AI 味联动 dbs-ai-check。

### Step 4 · 套用共享底座（第 3 层）
委派执行时，要求被调蒸馏器按 `shared/` 下的公共口径工作，避免三方各造一套：
- 增量认知校验：先写下已有认知，再专找反例与增量（`shared/verification/incremental-check.md`）。
- 三重交叉验证：来源充分性 / 可执行性 / 任务增益（`shared/verification/triple-verification.md`）。
- 质检与审计：发布前过清单，留审计痕迹（`shared/quality/qa-audit.md`）。
- 视觉验收：PPT/HTML/PDF/封面/分镜等会被人看见的产物，交付前先渲染成图并由 agent 亲自看（`shared/quality/visual-acceptance.md`）。
- 来源可信度标注：一手 / 二手 / 推断分级（`shared/credibility/source-grading.md`）。
- 产物规范与压测：目录结构、命名、Darwin 式用例（`shared/artifacts/`、`shared/darwin/`）。

### Step 5 · 收口产物并回传桌面
产物先落到本机桌面产物根目录，**按生成它的 Skill 名分一级子目录**（知识库落 `wiki/<slug>/`，库内自带 raw/ 与 wiki/）（规则见 `references/artifact-layout.md` 与 `shared/artifacts/convention.md`）。全部产物就位后，zyx 统一汇总路径清单回传给用户：每个产物标注来源蒸馏器、版本、校验状态与所在目录。回传前按 `shared/quality/qa-audit.md` 做一次交付前核对；视觉产物还要跑 `look.py` 并 Read `look.png`，没有看过的图不算验收通过。

## 3. 边界（zyx 不做什么）

- 不自己调研、不自己提炼方法论、不写蒸馏正文——这些归 R1/R2/R3。
- 不复制、不内嵌、不改写三个蒸馏器的内部文件；它们独立追上游更新。
- 投资类只产出研究性操作方案：不代下单、不承诺收益、不隐藏风险；资金量、交易周期、风险偏好不明时先问清再给方案。
- 不做无确认的远端动作（建仓、push、tag、Release 单独授权，见 `references/routing-table.md` 发布段）。
- 不把书摘、读后感、作者人设扮演交给仓颉（那是女娲的活）；路由表已写明边界。
- 知识库层不写 HTML、不装 Obsidian 插件、不改用户既有 Obsidian 库结构；同步接口仅预留。
- 本机环境/桌面（Omarchy/Hyprland）操作不属于 R1–R8 任一类：只做只读握手，执行交给 Omarchy 自己的 skill，不新增 R9。

## 4. 与 Omarchy 的握手（可选，不改 R1–R8 路由）

如果本机是 Omarchy（DHH 的 agentic Linux 发行版），ZYX 不新增 R9 路由，只做三件事：

- `omarchy-bridge.py status`：只读报告 Omarchy 版本、主题、默认 agent、共享 skills 目录，以及 ZYX/R7/context 卡是否就位。
- Context Card：把 R7 活动库投影成 `zyx-context` 技能卡，装进 `~/.agents/skills` 与已存在的宿主 skills 目录；换库自动刷新。
- Look Gate：视觉产物先渲染再交付（见 `shared/quality/visual-acceptance.md`）。

边界：不改 `/usr/share/omarchy`、不自动建任务、不写 `~/.agents/AGENTS.md`；环境操作交给 Omarchy 自己的 skill。

## 5. 后台静默更新机制

- **首次自注册**：首次调用 zyx 时 `env-registry.sh` 探测环境并注册周检任务，之后在后台持续运行；注册状态在 `state/registry.json`，重复调用幂等不重复注册。
- **静默更新器** `updater.sh`：每周日 18:00（或手动）执行：
  1. 对清单内 `source=git` 的蒸馏器（女娲/大师/仓颉；达尔文可选）做 `--ff-only` 快进更新；本地有未提交改动或分叉时不强行覆盖，保留本地并记录；更新前备份 HEAD 到 `state/backup/`。
  2. 检查 **zyx 自身版本**：拉取远端版本号与 HEAD SHA 同本地比对，输出最新/落后/超前；落后时提示人工确认更新，自身快进覆盖仍预留不自动执行。仓库与分支可用 `ZYX_REPO` / `ZYX_BRANCH` 环境变量覆盖。
  3. dbs 家族只比对官方版本并记录差异，不批量自动覆盖（目录式安装，由 dbs-update 处理）。
  4. 失败计数写入 `state/fail-count.json`；连续失败达阈值（`ZYX_FAIL_THRESHOLD`，默认 3）在下次对话提示；`--check-drift` 输出 drift 报告。
- **日志**：更新过程写入 `state/updater.log`；`--silent` 模式不在前台打印。
- **安全边界**：只快进本地已有仓库，不删除未提交改动、不访问远端写接口、不推送内容；非快进失败自动保留现状。手动只读检查可运行 `bash scripts/check-updates.sh`；环境就绪/缺项/完整性可运行 `bash scripts/doctor.sh [--online]`。

## 6. 运维指令（管理类，不参与生产路由触发）

以下命令属于安装、自检、更新等管理动作，与上面的生产路由分开，不在生产触发词里混用：

- 安装到当前宿主：在仓库根目录运行 `bash scripts/install.sh`（`--dir <目录>` 指定目标；`--install-deps` 同时装外部 git/npx 依赖；`--list-hosts` 列出候选目录）。
- 自检：`bash scripts/doctor.sh`（加 `--online` 额外检查上游网络可达性）。
- 视觉验收：`python3 scripts/look.py <产物> --out <目录>/look`；自测 `python3 scripts/look-selftest.py`。
- Omarchy 握手：`python3 scripts/omarchy-bridge.py status [--json]`；安装 context 卡 `python3 scripts/omarchy-bridge.py status --install-context`。
- 手动检查更新：`bash scripts/check-updates.sh`。
- 查看/注销后台注册：`bash scripts/env-registry.sh --status` / `--unregister`。
- 云端 Agent 没有本机调度器时，env-registry 会降级提示：在定时任务中心建一条每周日 18:00 的任务，命令为 `bash <zyx目录>/scripts/updater.sh --silent`。
