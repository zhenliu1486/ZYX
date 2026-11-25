# ZYX · Agent Skill 总调度台（路由 / 蒸馏 / 内容生产聚合）

> **ZYX 是什么**：一个兼容开放 Agent Skills 规范（agentskills.io）的**路由调度型 Skill**。接到任务后先判断属于「人 / 行业 / 长内容 / 当下问题 / 影视短剧漫剧生产 / 已有产物迭代 / 长期知识库」七类中的哪一类，再转发给对应的独立蒸馏器、dbs 家族或影视聚合层，最后按规范收口产物。上游蒸馏器保持独立、各自追上游 git 更新；公共校验、质检、可信度、产物规范与压测口径抽成 `shared/` 共享底座。

**适用宿主**：Claude Code、Codex、OpenClaw、Cursor、Gemini CLI、OpenCode 等兼容 Agent Skills 标准的宿主；脚本依赖 Bash / git / curl，仓颉本体另需 Python 3.10+ 与 PyYAML。

**一句话定位**：不是又一个通用编码路由，而是面向**方法论蒸馏 + 内容生产**的垂直调度台——把「像谁一样想 / 懂这行怎么做 / 提炼长内容方法 / 眼下这件事怎么判 / 怎么出片子 / 怎么按反馈迭代 / 怎么把资料攒成能用一辈子的知识库」七类请求，一次分流到正确的执行能力上。

**快速安装**

```bash
git clone https://github.com/zhenliu1486/ZYX.git
cd ZYX
bash scripts/install.sh            # 自动选择宿主目录并自检
# 可选：同时安装外部上游蒸馏器（女娲/大师/仓颉/dbs/达尔文）
bash scripts/install.sh --install-deps
# 或用 skills CLI：npx skills add zhenliu1486/ZYX
```

**关键词**：Agent Skill、skill 路由、skill dispatcher、agent 调度台、任务分流、方法论蒸馏、长内容提炼、行业 Master Skill、人物视角 Skill、短剧 / 漫剧 / 影视分镜、负反馈迭代、Claude Code skill、可复用工作流。

## 仓库布局

```
ZYX/
├── scripts/install.sh              # 一键安装器（识别宿主 → 复制内置 Skill → 自检）
├── scripts/sync-hosts.sh           # 同步到本机所有已存在的宿主目录
└── skills/
    ├── zyx/                        # 第 1 层：入口路由薄壳（本目录）
    │   ├── deps/manifest.json     #   依赖声明清单：来源/安装命令/必需可选/子技能归属
    │   ├── references/            #   路由判定表、产物目录与回传规范
    │   ├── scripts/               #   路由解析 / 自注册 / 静默更新 / 自检 / 目录探测
    │   ├── shared/                #   第 3 层：共享底座（三方重复部分抽公共）
    │   └── evals/                 #   路由与降级/版本/脱敏回归用例
    ├── video-studio/              # 第 2 层：影视制作聚合入口
    ├── screenplay-development/    # R5 剧本开发（内置）
    ├── short-drama-screenwriter/  # R5 竖屏短剧编剧（内置）
    ├── manju-character-library/   # R5 人物设定库（内置）
    ├── manju-scene-library/        # R5 场景库（内置）
    ├── cinematic-fight-direction/ # R5 动作/打斗分镜（内置）
    ├── micro-expression-video/    # R5 微表情参数（内置）
    ├── manju-production-pipeline/  # R5 全流程 SOP（内置）
    ├── f2r-feedback-iteration/    # R6 负反馈迭代器（内置）
    └── wiki-vault/                # R7 长期知识库（内置：注册表/单写锁/lint 巡检）
```

## 路由表

| 原料类型 | 转发到 | 来源类型 | 产物 |
|---|---|---|---|
| 人（思维方式 / 名人 OS） | R1 女娲 `nuwa-skill` | git（必需，外部上游） | 人物视角 Skill |
| 细分行业 | R2 大师 `master-skill` | git（必需，外部上游） | 行业 Master Skill（Phase 3 调女娲出人物 sub-skill） |
| 长内容（书/视频/播客/课程/访谈） | R3 仓颉 `cangjie-skill` | git（必需，外部上游） | 原子能力卡 + Skill 包 |
| 当下问题（诊断/文案/决策/协作） | R4 dbs 家族 | npx（必需，外部上游） | 报告 / 成稿 / 决策记录 |
| 影视/短剧/漫剧制作 | R5 `video-studio` 聚合层 | 内置，7 个子技能随仓库 | 剧本 / 设定 / 分镜 / 参数 / 流程方案 |
| 已有产物二次打磨 | R6 `f2r-feedback-iteration` | 内置 | 迭代后的产物 + 反馈规则记录 |
| 长期知识库（个人/领域 Wiki） | R7 `wiki-vault` | 内置 | 持续累积的 Obsidian Markdown 知识库（摘要/实体/概念/对比/综述页 + 索引/日志/热缓存） |
| Darwin 式压测底座（可选） | `darwin-skill` | git（可选，外部上游） | 压测行为验证本体 |

> 依赖的完整字段（安装命令、归属、备注）以 `skills/zyx/deps/manifest.json` 为准；新增/调整依赖只改这一份清单。

## 安装

### 方式一：一键安装器（推荐）

在仓库根目录执行：

```bash
# 自动选择第一个可写的宿主 skills 目录，复制全部内置 Skill 并跑自检
bash scripts/install.sh

# 指定目标 skills 目录
bash scripts/install.sh --dir ~/.claude/skills

# 同时安装外部 git/npx 上游依赖（女娲/大师/仓颉/dbs/达尔文）
bash scripts/install.sh --install-deps

# 只列出候选宿主目录
bash scripts/install.sh --list-hosts

# 同步到本机所有已存在的宿主目录（macOS 自带 Bash 3.2 兼容）
bash scripts/sync-hosts.sh
```

`install.sh` 会先把宿主里的旧版备份到 `~/.zyx-backups/install-<时间>-<pid>/`，再用 stage 目录原子替换；替换失败自动恢复旧版。可用 `ZYX_INSTALL_BACKUP` 改备份根目录。

### 方式二：手工复制

把 `skills/` 下需要的 Skill 目录复制到任一宿主的 skills 目录：

```bash
# Claude Code
cp -r skills/zyx skills/video-studio ~/.claude/skills/
# OpenClaw
cp -r skills/zyx skills/video-studio ~/.openclaw/skills/
# Agents
cp -r skills/zyx skills/video-studio ~/.agents/skills/
# 豆包 Doubao 用户技能目录
cp -r skills/zyx skills/video-studio ~/.doubao/agent_mode/workspace/.user_skills/
```

内置的 R5 子技能与 R6 迭代器随 `skills/` 一起复制即可；外部上游蒸馏器按上表来源单独安装。

### 运行环境

- 脚本运行需要 Bash、git、curl；仓颉本体另需 Python 3.10+ 与 PyYAML。
- 宿主目录探测顺序见 `deps/manifest.json` 的 `host_dirs`；可用 `ZYX_EXTRA_SKILL_DIRS`（冒号分隔）追加额外探测目录。

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

### 6. 长期知识库（R7 wiki-vault）
> 「帮我建一个关于 AI 基础设施的知识库，以后我看到文章就往里加，能随时问库里的结论。」

入口判定：要长期累积、反复摄入、库内检索 → 路由 R7 wiki-vault；产物落到 `zyx-output/wiki/<slug>/`（内含 `raw/` 只读原料与 `wiki/` 编译知识层）。已有 Obsidian 库直接 `mount` 挂载，不搬动、不重构；写操作先取单写锁，禁止并行写同一库。库内可用 `search` 检索、`archive` 把问答归档成对比/综述页并回链、`promote-check` 自查是否够格晋级 R3。

## 自检与更新

- **自检**：`bash skills/zyx/scripts/doctor.sh`（加 `--online` 额外检查上游网络可达性，`--full` 额外跑 R7 知识库端到端自测）。检查运行依赖、依赖安装状态、文件完整性与悬空引用、调度环境、产物目录可写性、自身版本；并检查 Look Gate 渲染工具、Omarchy 握手与 Context Card。
- **首次触发自注册**：`scripts/env-registry.sh` 探测 cron / launchd / systemd 并幂等注册后台周检；`--status` 查看状态，`--unregister` 卸载。纯云端无调度器环境会降级提示在定时任务中心建任务。
- **静默更新**：`scripts/updater.sh` 对清单内 git 依赖做 ff-only 快进 + 浅克隆兜底重置（旧 HEAD 备份），dbs 只比对不覆盖；失败计数、连续失败提示与 drift 报告（`--check-drift`）。zyx 自身拉取远端版本号与 HEAD SHA 同本地比对，落后/超前/最新写入 `state/self-version.json`；自身快进覆盖仍需人工确认，不自动执行。
- **环境变量**：`ZYX_REPO` 覆盖自身远端仓库，`ZYX_BRANCH` 覆盖远端分支（默认 `main`），`ZYX_FAIL_THRESHOLD` 覆盖连续失败阈值（默认 3），`ZYX_EXTRA_SKILL_DIRS` 追加额外 Skill 探测目录。

## 发布与认证（开发者）

- 发布到远端仓库用 `scripts/publish.sh`（默认 public，可传 `private` 与 tag）；建仓 / push / tag / Release 属远端写动作，需当轮明确授权。
- 换机器或首次推送需重新完成 GitHub 登录（`gh auth login` 或 `gh auth login --with-token <token>`）；旧版 gh 凭证助手不吐账号时，用带 `repo` 权限的 PAT 走 token 方式。
- 发布前按 `shared/quality/qa-audit.md` 脱敏：不提交密钥、内部路径、本机配置、未脱敏样本与运行记录。

## 与通用编码路由 Skill 的区别

| 维度 | 通用编码 / 任务路由 Skill | ZYX 调度台 |
|---|---|---|
| 目标任务 | 代码、通用多步任务的子 Agent 分派 | 方法论蒸馏 + 内容生产 + 长期知识库七类请求分流 |
| 路由对象 | 子 Agent 类型（Explore / Plan / Researcher 等） | 独立蒸馏器、影视聚合层、R5 子技能、R6 迭代器、R7 知识库 |
| 依赖管理 | 多靠提示词判断，缺依赖时提示 | 声明式 `manifest.json` 清单 + 一键安装器 + 逐项自检 |
| 产物收口 | 较少涉及 | 规范目录 / 命名 / 脱敏 / 统一回传清单 |
| 更新闭环 | 通常无 | 后台周检、版本号 + HEAD SHA 比对、失败计数与 drift 报告 |
| 共享底座 | 各自重复实现 | 校验 / 质检 / 可信度 / 产物规范 / 压测口径抽成一份 shared |

## 常见问题（FAQ）

**Q：ZYX 自己会蒸馏方法论、写剧本吗？**
不会。ZYX 是薄壳路由入口，只判断类型、转发委派、收口产物；方法论分别驻留在对应蒸馏器与子技能里，ZYX 不复制、不内嵌其内部文件。

**Q：装好 ZYX 就能直接出蒸馏产物 / 影视脚本吗？**
R5 影视七子技能与 R6 迭代器随仓库内置；R1–R4 上游蒸馏器（女娲 / 大师 / 仓颉 / dbs）是外部依赖，用 `bash scripts/install.sh --install-deps` 或按 `deps/manifest.json` 单独安装；可选达尔文压测底座同理。

**Q：支持哪些 Agent 宿主？**
兼容开放 Agent Skills 规范的宿主：Claude Code、Codex、OpenClaw、Cursor、Gemini CLI、OpenCode 等；探测目录见 `deps/manifest.json`，可用 `ZYX_EXTRA_SKILL_DIRS` 追加。

**Q：产物和隐私怎么处理？**
产物默认只落本机桌面 `zyx-output/`，不自动推送远端；发布前强制过脱敏清单，手机号 / 身份证 / 内部账号 / 未公开客户名等一律占位符替代。

**Q：怎么更新 ZYX 和上游依赖？**
后台周检自动快进 git 上游（有手改或分叉不强行覆盖）；手动跑 `bash scripts/check-updates.sh` 看 drift 报告；ZYX 自身版本落后时提示人工确认，不自动覆盖运行中的 Skill。

**Q：R7 知识库和 R3 拆书有什么区别？**
R3 是一次性把书/长视频蒸馏成可安装 Skill 包；R7 是长期活着的库，反复往里喂资料、编译成互链页面、随时库内提问与巡检。库里的某份材料沉淀出独立复用价值（过三重验证 + 具备独立复用价值）后，才晋级交给 R3 打包。

**Q：知识库会不会因为资料太少给出错误结论？**
R7 不设覆盖度闸门，巡检只报客观统计（断链/缺页/孤儿/索引覆盖/陈旧/矛盾），不下「覆盖不足禁止下结论」的判断；每条结论标 `confidence` 与来源级别，是否采信由你决定。

**Q：开源协议？**
MIT，可自由使用、修改与再分发。

## 设计原则

- **入口只做路由与收口**：zyx 不调研、不提炼方法论、不复制蒸馏器内部文件。
- **蒸馏器独立演进**：女娲 / 大师 / 仓颉各自追上游 git 更新，zyx 只引用安装路径。
- **共享底座去重**：增量校验、三重验证、质检审计、可信度标注、产物规范、压测用例只维护一份，三方引用。
- **产物按来源名分目录**：产物落到桌面 `zyx-output/<来源 Skill>/<产物>/`，由 zyx 统一回传路径清单；桌面目录按「桌面 → 文档 → HOME/zyx-output」跨平台回退探测。
- **知识库是一层活资产**：R7 把原料编译成互链 Markdown 并持续保鲜，不每次提问重造；库只落本机，同步接口预留未启用。

## 规范对齐

本 Skill 遵循开放 Agent Skills 规范（agentskills.io）：YAML frontmatter（`name` / `description` / `license` / `compatibility` / `metadata` / `allowed-tools`）、渐进式披露（元数据 → 正文 → 按需加载 references/scripts/assets）、正文 500 行以内。模板与标准参考 Anthropic agentskills 开放规范与 Google 官方 skills 仓库格式。

## 许可

MIT，见 [LICENSE](LICENSE)。变更记录见 [CHANGELOG.md](CHANGELOG.md)。

## 分享与推广素材

对外口径、各平台成稿与渠道跟踪清单见 [`docs/promo/`](../../docs/promo/)：`marketing-kit.md`（事实口径与话术）、`article-technical.md`（技术长文）、`xiaohongshu-note.md`（图文笔记）、`short-video-script.md`（短视频口播）、`channel-checklist.md`（渠道执行跟踪）。
