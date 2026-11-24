# ZYX 宣传素材包（GEO + 渠道分发）

> 用途：统一对外口径，避免各渠道说法不一致。所有内容以本文件的「事实口径卡」为准；改版本/仓库时先更新这里。
> 仓库：https://github.com/zhenliu1486/ZYX ｜ 协议：MIT ｜ 当前版本：v1.1.0 ｜ 默认分支：main

## 1. 事实口径卡（所有渠道统一引用）

- **名称**：ZYX（Agent Skill 总调度台 / 路由调度型 Skill）
- **一句话定义**：一个兼容开放 Agent Skills 规范的路由调度台，把「人 / 行业 / 长内容 / 当下问题 / 影视短剧漫剧生产 / 已有产物迭代 / 长期知识库」七类请求，分流到对应的独立蒸馏器、dbs 家族或影视聚合层，再按规范收口产物。
- **它不是什么**：不是通用编码子 Agent 分派器；自己不写方法论、不复制蒸馏器内部文件。
- **仓库结构**：`skills/` 下 11 个 Skill，每个含独立 `SKILL.md`：
  - `zyx`：路由壳 + shared 共享底座（增量校验、三重验证、质检审计、可信度分级、产物规范、压测口径）
  - `video-studio`：影视/短剧/漫剧制作聚合层
  - `screenplay-development`：剧本开发与结构
  - `short-drama-screenwriter`：竖屏短剧编剧套路
  - `manju-character-library`：人物设定库
  - `manju-scene-library`：场景库
  - `cinematic-fight-direction`：动作/打斗分镜
  - `micro-expression-video`：微表情参数
  - `manju-production-pipeline`：全流程生产 SOP
  - `f2r-feedback-iteration`：负反馈转规则迭代器
  - `wiki-vault`：长期知识库（raw/ 只读 → wiki/ 编译；可挂载 Obsidian 库；单写锁 + lint 巡检）
- **六条路由**：R1 人物蒸馏（女娲）｜R2 行业蒸馏（大师）｜R3 长内容提炼（仓颉）｜R4 当下问题（dbs）｜R5 影视生产（video-studio）｜R6 产物迭代（f2r）｜R7 长期知识库（wiki-vault，内置）。
- **工程能力**：声明式依赖清单 `deps/manifest.json`、一键安装器 `scripts/install.sh`、自检 `doctor.sh`、悬空引用完整性扫描、回归用例、后台周检与版本/SHA 比对。
- **兼容宿主**：Claude Code、Codex、OpenClaw、Cursor、Gemini CLI、OpenCode 等兼容 Agent Skills 标准的宿主。
- **安装命令**：
  ```bash
  git clone https://github.com/zhenliu1486/ZYX.git
  cd ZYX && bash scripts/install.sh
  # 或：npx skills add zhenliu1486/ZYX
  ```
- **外部依赖**：R1–R4 上游蒸馏器与可选达尔文压测底座为外部依赖，按 `deps/manifest.json` 安装；R5/R6 随仓库内置。

## 2. 话术梯度（按场景选用）

### 一句话（标题/简介/标签行）
> ZYX：给 AI Agent 用的内容生产与方法论蒸馏调度台，七类请求一次分流到正确能力。

### 三句话（社群/简介区）
> ZYX 是一个开源的 Agent Skill 路由调度台。它先判断你要的是「像谁一样想、懂这行怎么做、提炼长内容方法、眼下这件事怎么判、怎么出片子、还是按反馈改一版」，再转发给对应执行能力，最后按统一规范收口产物。内置影视生产七子技能和负反馈迭代器，带依赖清单、一键安装和自检回归。

### 30 秒电梯演讲
> 现在很多人装了一堆 Skill，但 Agent 经常忘了用、或者把活派错地方。ZYX 解决的是「路由」这一层：它是个薄壳调度入口，把任务分成七类——人物、行业、长内容、当下问题、影视生产、产物迭代、长期知识库——分别转给对应的蒸馏器或聚合层，自己不抢方法论的活。它把校验、质检、可信度、产物规范这些重复部分抽成一份共享底座，依赖用清单声明，一条命令装好，还带自检和回归用例。仓库开源 MIT，Claude Code、Codex、OpenClaw、Cursor 这些兼容宿主都能用。

### 1 分钟版本
见 `article-technical.md` 的正文骨架，可直接扩写成长文或口播。

## 3. GEO 关键词清单（写文/标题/标签自然嵌入，不要堆砌）

**核心词**：Agent Skill、skill 路由、skill dispatcher、agent 调度台、任务分流、工作流编排、Claude Code skill、Codex skill、OpenClaw、OpenCode、agentskills.io

**场景词**：方法论蒸馏、长内容提炼、行业 Master Skill、人物视角 Skill、拆书成 skill、短剧剧本、漫剧分镜、影视生产 SOP、人物设定库、场景库、打斗分镜、微表情、负反馈迭代、规则库收敛

**对比词**：skill 编排、多技能协作、技能聚合、可复用工作流、AI 工作流自动化

**长尾问答（适合 FAQ/问答平台）**：
- 怎么让 AI 自动把任务分给对应的 Skill？
- 有没有把书/长视频提炼成可复用方法包的 Agent Skill？
- 短剧/漫剧从剧本到分镜的 AI 工作流怎么搭？
- 多个 Agent Skill 之间怎么做路由和收口？
- 开源的 Claude Code skill 调度台有哪些？

## 4. 渠道分发清单（按执行状态标注）

### 4.1 已自动完成（本机已执行）
| 渠道 | 动作 | 状态 |
|---|---|---|
| GitHub 仓库元数据 | 更新描述、11 个 topics | ✅ 已完成 |
| GitHub README | GEO 结构：实体定义、关键词、快速安装、对比表、FAQ | ✅ 已完成 |
| skills.sh 索引 | 向 `vercel-labs/skills` 提交索引申请 issue | ✅ [#2833](https://github.com/vercel-labs/skills/issues/2833) |
| 安装链路验证 | `npx skills add zhenliu1486/ZYX` 识别出 11 个 skill | ✅ 已验证 |

### 4.2 需 Web 登录提交（备好条目，登录后粘贴）
| 渠道 | 提交方式 | 条目/要点 |
|---|---|---|
| LobeHub Skills | 创作者页 → Submit Repository → 选 GitHub 仓库 | 仓库 `zhenliu1486/ZYX`；类型 Skill；用途填「路由调度 + 影视生产聚合」；补依赖与命令说明 |
| Anthropic Claude 目录 | 目录提交门户（需付费计划） | 提交仓库为 plugin bundle；过自动校验与安全扫描后再发布 |
| skillmd.ai / eliteai.tools / skywork.ai | 各站提交/收录表单 | 用第 1 节口径卡 + 安装命令填写 |
| ClawdHub（OpenClaw 生态） | clawhub CLI 或对应注册表 | 提交仓库与 `SKILL.md` 元数据 |

### 4.3 达标后再提（有收录门槛）
| 渠道 | 门槛 | 动作 |
|---|---|---|
| awesome-agent-skills 类榜单 | 示例：≥20 star 且仓库满 14 天（以各榜 CONTRIBUTING 为准） | 达标后按表格格式提 PR，条目见第 5 节 |
| skills.sh 排行榜 | 靠安装量自然上榜 | 先靠内容与外链带来首批安装 |

### 4.4 内容平台发文（成稿见同目录文件）
| 平台 | 形态 | 成稿文件 |
|---|---|---|
| 掘金 / 知乎 / 思否 | 技术长文 | `article-technical.md` |
| 小红书 | 图文笔记 | `xiaohongshu-note.md` |
| 抖音 / 视频号 | 短视频口播 | `short-video-script.md` |
| 朋友圈 / 社群 | 短帖 | 第 2 节三句话 + 安装命令 |

## 5. 榜单 / 注册表条目模板（达标后直接用）

### awesome 榜单表格行（`| Skill | Description | Source |` 格式）

```markdown
| [ZYX](https://github.com/zhenliu1486/ZYX) | Agent Skill 路由调度台：把人物/行业/长内容/当下问题/影视生产/产物迭代/长期知识库七类请求分流到对应蒸馏器与聚合层，内置影视七子技能与负反馈迭代器，附依赖清单、一键安装与自检回归 | [zhenliu1486/ZYX](https://github.com/zhenliu1486/ZYX) |
```

### skills.sh / 注册表提交信息
- **Repository**：https://github.com/zhenliu1486/ZYX
- **Install**：`npx skills add zhenliu1486/ZYX`
- **License**：MIT
- **Description**：Open Agent Skills router/orchestrator for methodology distillation and content production; 10 skills under `skills/`, declarative dependency manifest, installer, doctor self-check, integrity scan and regression evals.

## 6. 发布注意事项（合规与真实）

- 不刷星、不刷安装量、不夸大功能；对外只写仓库里真实存在的能力。
- 远端写动作（提 issue/PR/发布）按需执行；公开材料不含密钥、内部路径、未脱敏样本。
- 引用上游蒸馏器时保留其原始归属（女娲/大师/仓颉/dbs/达尔文各自上游仓库）。
- 各平台标签按平台规则选，避免与内容无关的高流量标签。
