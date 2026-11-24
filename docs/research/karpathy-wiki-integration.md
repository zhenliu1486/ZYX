# ZYX × Karpathy LLM Wiki 结合研究方案（先研究，不改代码）

> 状态：2026-11-24 决策已定稿，P1–P4 全部完成并随 v1.2.0 上线（R7 `wiki-vault`）。本文先拆清卡帕西这套 LLM 自动维护 Wiki 的流程，对照 ZYX 现有 R1–R6 与 shared 底座，给出推荐集成方案、缺口清单、分阶段计划和待拍板决策。
> 模式来源：Andrej Karpathy 2026 年 4 月提出的 LLM Wiki 思路；社区落地蓝图参考 ScrapingArt/Karpathy-LLM-Wiki-Stack（见文末来源）。**注意：ZYX 与 Karpathy 本人无关联，对外表述只能说「借鉴该模式」，不得写成 Karpathy 推荐或背书。**

## 1. 结论先行（TL;DR）

- 卡帕西 Wiki 本质是一层**长期存在、持续累积的个人/领域知识库**：原料进 `raw/`，LLM 编译成互相链接的 Markdown `wiki/`，再在 wiki 上提问、随反馈迭代；知识只编译一次并持续保鲜，而不是每次提问从原料重新检索。
- ZYX 现有六类路由都是**一次性产物**：蒸馏出一个 Skill、诊断一个问题、出一段内容、改一版产物。缺少一个「跨会话长期维护、能反复往里喂资料、能在里面查东西」的活知识库层。
- **推荐方案**：新增一条内置路由 **R7 `wiki-vault`**（与 R5 video-studio、R6 f2r 一样随仓库内置，不引外部必需依赖），负责知识库的初始化、摄入编译、库内问答、健康巡检；能复用现有 shared 底座（增量校验、三重验证、可信度分级、质检审计、产物规范），深蒸馏需求再委派回 R1/R2/R3，反馈迭代联动 R6。
- 不建议把这套塞进 R3 仓颉：仓颉是外部上游、一次性把长内容蒸馏成 Skill 包；Wiki 是长期状态层，目录、索引、巡检、跨会话引用都不一样，混在一起会让两边都变重。

## 2. Karpathy Wiki 模式拆解

### 2.1 三层结构（归属权是硬约束）

| 层 | 目录 | 归属 | 规则 |
|---|---|---|---|
| L1 原料层 | `raw/` | 人放、人维护；LLM 只读 | 永不修改，作为可回溯的事实源；文章/论文/仓库 README/转写稿/数据集/图片都放这里 |
| L2 知识层 | `wiki/` | LLM 写、LLM 维护；人只读浏览 | 摘要页、实体页、概念页、对比页、综述页，互相链接；人不手改 |
| L3 规则层 | `CLAUDE.md` / `AGENTS.md`（按宿主换文件名） | 人与 LLM 共同迭代 | 每次会话开头读：规定目录约定、页面规范、三个操作的流程；没有它，每次会话从零开始 |

### 2.2 三个核心操作

1. **Ingest（摄入编译）**：丢一份原料进 `raw/` → 读原料 → 先聊 3–5 条要点 → 生成来源摘要页 → 更新主索引 → 更新相关实体/概念页 → 新信息与旧说法矛盾时显式标注 → 必要时新建概念/实体页 → 追加活动日志。一份原料通常牵动 5–15 个 wiki 页面。
2. **Query（库内问答）**：先读主索引定位相关页 → 直接读这些页 → 带 wiki 链接引用组织答案；有价值的分析可以**回写成**对比页/综述页，并在原概念页加回链。问答本身也让知识库变厚（双向累积）。
3. **Lint（健康巡检）**：定期（建议周级）扫描：页间矛盾、孤儿页（零入链）、被反复提到 3 次以上却没有独立页的概念、被新原料推翻的陈旧结论、集群字段缺失、综述页缺回链；最后给 3–5 条下一步该查的问题/该补的来源。

### 2.3 关键文件约定

- `wiki/index.md`：全库主目录，每次摄入必更新。
- `wiki/log.md`：只追加的活动日志，条目带日期与操作类型（ingest/query/lint）。
- `wiki/hot.md`：会话热缓存（约 500 字），会话开头静默先读。
- `wiki/overview.md`：全库高层综述，大规模摄入后修订。
- 页面分类型：`sources/`（每份原料一页摘要）、`entities/`（人/公司/产品/组织）、`concepts/`（方法/技巧/理论）、`comparisons/`（对比分析）、`syntheses/`（长综述）。
- 每页带 frontmatter：类型、标题、slug、来源、关联链接、创建/更新日期、可信度、所属集群、矛盾与待解问题。

### 2.4 必须守住的规则（参考实现里的硬约束）

- `raw/` 绝不写入；出错可回溯源料纠正。
- 不删除 wiki 页，废弃只在 frontmatter 标 `deprecated`。
- 每次操作都要更新 `index.md` 和 `log.md`。
- 结论没把握时可信度标低；新页面至少与 2 个已有页面交叉链接。
- **准备度门槛（10-source 测试）**：覆盖度不够的 wiki 会用高置信的缺口误导人；在攒到有意义的覆盖量之前，不拿 wiki 做决策依据。
- **单写规则**：同一时刻默认单会话顺序写；并行会话只能操作互不相交的文件集，防止静默写坏。
- 知识是「编译一次、持续保鲜」，不是每次提问从原料重新拼。

## 3. ZYX 现状对照：哪些已有，哪些缺

### 3.1 已经能复用的部分

| Wiki 环节 | ZYX 现有底座/路由 | 复用方式 |
|---|---|---|
| 摄入前先区分「已知常识 vs 增量」 | `shared/verification/incremental-check.md`（推翻/加深/新增） | 摄入编译前置步骤沿用先验记录与增量标注 |
| 页面结论入库前的闸门 | `shared/verification/triple-verification.md`（来源充分性/可执行性/任务增益） | 候选概念/实体页进 wiki 前过三道闸门 |
| 来源分级与可信度标注 | `shared/credibility/source-grading.md`（一手/二手/推断） | 映射到页面 frontmatter 的来源级别与 confidence |
| 入库前质检、脱敏、审计留痕 | `shared/quality/qa-audit.md` | 综述/对比页回写前过质检门；沿用脱敏清单 |
| 目录结构、命名、MANIFEST 清单 | `shared/artifacts/convention.md` | 每个 vault 一份 MANIFEST，sources/ 留痕 |
| 被驳回初稿、按反馈改规则 | R6 `f2r-feedback-iteration` | wiki 页面被否/要改版时联动 R6，把反馈沉淀成规则 |
| 深度蒸馏成可复用 Skill | R1 女娲 / R2 大师 / R3 仓颉 | 某份原料不只是进 wiki，而要晋级成独立 Skill 时委派过去 |
| 后台周检机制 | `scripts/updater.sh` / env-registry 状态闭环 | lint 可挂到同一套周检调度，不另造定时器 |
| 断链/悬空引用扫描 | `scripts/check-integrity.py` | 扩展到扫描 wiki 内链接、孤儿页、缺字段 |

### 3.2 现有缺口（ZYX 目前没有的）

1. **跨会话的持久状态**：现有产物是一次性输出目录，用完即止；wiki 需要按 slug 记住「这个库在哪、里面有什么」，下次会话直接找到。需要一个 vault 注册表（类似现有 `state/registry.json` 的运行态）。
2. **结构化编译产物**：摘要页、实体页、概念页、反向链接、主索引、日志、热缓存、综述页——现有组件不产出这种互相链接的 Markdown 图谱。
3. **周期健康巡检**：现有 qa-audit 是「交付前一次性质检」，没有针对活库的递归 lint（孤儿、缺页、矛盾、陈旧结论、缺回链）。
4. **库内问答流程**：现有 R4 是基于对话已有事实做当下诊断，没有「先查我的持久知识库再作答」的操作路径。
5. **回写累积闭环**：现有 R6 是围绕一份已有产物按反馈迭代；wiki 的问答答案回写成新页、并给原页加回链，是另一种累积动作。
6. **准备度门槛与并发约束**：现有流程没有「覆盖度不足不下结论」的闸门，也没有多会话写同一目录的并发约定。

## 4. 推荐集成方案：R7 `wiki-vault`（内置路由）

### 4.1 定位与边界

- **做什么**：管理一个长期维护的 Markdown 知识库：建库、往里喂资料并编译入库、在库内提问、定期巡检健康；页面结论过现有验证与质检底座。
- **不做什么**：不自己写行业方法论（深蒸馏走 R1/R2/R3）；不替代 R4 的当下问题诊断；不把整本书/长段原文存进库（版权安全，只留摘要 + 最短摘录 + 元数据）；默认只落本机，远端同步沿用现有授权边界。

### 4.2 建议目录布局（落在现有产物根目录下）

```
<桌面>/zyx-output/wiki/<vault-slug>/
├── raw/                        # L1 原料，只读；articles/ papers/ transcripts/ data/ assets/
├── wiki/
│   ├── index.md                # 主目录，每次摄入必更
│   ├── log.md                  # 只追加活动日志
│   ├── hot.md                  # 会话热缓存（约 500 字）
│   ├── overview.md             # 全库高层综述
│   ├── sources/                # 每份原料一页摘要
│   ├── entities/               # 人/公司/产品/组织
│   ├── concepts/               # 方法/技巧/理论
│   ├── comparisons/             # 对比页
│   └── syntheses/              # 长综述页
├── MANIFEST.md                 # 库清单：来源、版本、验证记录、边界、修改记录
└── schema.md                   # L3 规则层（本库目录约定与操作口径；按宿主可复制为 CLAUDE.md/AGENTS.md）
```

> vault slug 用小写英文连字符或中文短名，规则与现有产物命名一致；vault 注册表放运行态 `state/`，不进发布包。

### 4.3 四个操作（对应 skill 内指令分层）

| 操作 | 触发信号 | 动作要点 | 复用底座 |
|---|---|---|---|
| `init` | 「给我建一个关于 X 的知识库/资料库」 | 建目录骨架、写 schema.md、生成空 index/log/overview、登记 vault 注册表 | artifacts 规范 |
| `ingest` | 「把这篇/这本书/这个视频加进我的 X 库」 | 先验记录 → 读原料 → 摘要页 → 更新索引与相关页 → 矛盾标注 → 新建页 → 写日志；增量标注 + 三重验证 + 来源分级 | incremental-check / triple-verification / source-grading |
| `query` | 「我库里关于 X 都有什么结论」 | 读 index 定位 → 读相关页 → 带链接引用作答；有价值的分析提议回写为 comparison/synthesis 并加回链 | triple-verification / qa-audit |
| `lint` | 「体检一下我的库 / 巡检」 | 扫矛盾、孤儿、缺页、陈旧结论、缺集群字段、缺回链；给下一步补查建议；写日志 | check-integrity 扩展 + qa-audit |

### 4.4 与其他路由的衔接

- **晋级委派**：某份原料在 wiki 里沉淀出独立复用价值（过三重验证闸门 C + 可独立复用），才升级交给 R3 仓颉编译成 Skill；人物深挖走 R1，行业打法走 R2。wiki 是原料和概念的蓄水池，不是 Skill 打包器。
- **反馈联动**：用户对某页结论不满意、要改版，走 R6 f2r 把反馈显性化成规则，迭代后回写 wiki。
- **当下问题分流**：如果用户只是眼下要一个判断、并不要求进长期库，仍归 R4，不新建 vault。

### 4.5 路由信号与相邻边界（拟补进路由表）

| 归 R7 的信号 | 容易误分到哪 | 裁决 |
|---|---|---|
| 「攒一个关于 X 的知识库」「持续往这个库里喂资料」「在我笔记库里查 X」 | R3 仓颉 | 要长期累积、反复摄入、库内查询 → R7；只要一次性拆成一个 Skill 包 → R3 |
| 「把这篇文章存进我的资料库并整理成条目」 | R4 dbs | 要落进持久库、可回溯链接 → R7；只要当下给个看法/诊断 → R4 |
| 「上次库里那个结论再改一版」 | R6 f2r | 改的是活库里的一页，反馈规则沉淀后回写 R7；R6 负责迭代方法与规则记录 |

## 5. 工程落地清单（编码阶段照此拆）

1. **新内置技能目录**：`skills/wiki-vault/`，含 `SKILL.md`、`references/`（vault 布局、页面 frontmatter 规范、lint 口径）、`scripts/`（vault 注册表、索引/日志辅助、lint 扫描）。
2. **依赖清单**：`deps/manifest.json` 加 R7 条目，`source: bundled`、`required: false`、无外部必需依赖；可选前端（Obsidian CLI / qmd）列为可选增强。
3. **路由表/产物布局**：`routing-table.md` 补 R7 信号、裁决与路径解析；`artifact-layout.md` 补 `wiki/` 一级子目录与落点规则；白名单加 `wiki`。
4. **shared 复用**：不新造校验口径；在 wiki 操作节点挂现有 verification/credibility/quality/artifacts 文件。
5. **状态注册表**：`state/vaults.json`（slug → 路径 → 主题 → 最近摄入时间），与现有 registry 一样幂等、不进发布包。
6. **回归用例**：补 R7 路由判别（vs R3/R4/R6）、lint 四类问题识别、准备度门槛提示、raw/ 只读约束、脱敏与断链扫描。
7. **自检**：`doctor.sh` 增加 vault 健康概览（库数量、最近活动、缺字段/孤儿数量）。
8. **文档与话术**：README、CHANGELOG、promo 素材包补 R7 定位与安装说明。

## 6. 分阶段计划

- **P0（本次）**：研究与方案确认，本文档定稿。
- **P1 骨架**：R7 skill 目录、schema 与四个操作口径、vault 注册表、manifest/路由表/产物布局/eval 用例补齐；先跑通 init → ingest → query 手工流程。
- **P2 脚本化**：index/log 更新校验、frontmatter 校验、lint 扫描（孤儿/缺页/矛盾/陈旧/缺回链），复用并扩展 check-integrity。
- **P3 闭环**：问答回写归档、R6 反馈联动、R1/R2/R3 晋级委派、可选 Obsidian 模板与本地搜索增强。
- **P4 回归与发布**：扩充 evals、doctor 覆盖、README 与话术更新，过脱敏与质检门后再发版本。

## 7. 决策点（已定稿，见第 10 节）

1. **路由形态**：是否同意新增独立 R7 `wiki-vault`，而不是并入 R3？（推荐独立）
2. **库落点**：默认放 `<桌面>/zyx-output/wiki/<slug>/`；要不要支持直接挂载一个已有 Obsidian vault 目录作为库根？
3. **前端绑定**：ZYX 层只产 Markdown 与索引（Obsidian 作为可选前端），还是要内置一套 Obsidian 模板/插件配置？（推荐先只做 Markdown，前端留可选）
4. **准备度门槛**：是否把「10-source / 覆盖度不足不下决策结论」写成正式闸门？阈值按经验先定多少。
5. **并发约定**：默认单会话顺序写；是否需要在规则层显式禁止并行会话写同一 vault。
6. **远端同步**：vault 是否预留后续 git 同步接口（默认只落本机、推送单独授权，沿用现有边界）？
7. **晋级标准**：wiki 页升级成独立 Skill 的判据，是否直接复用三重验证闸门 + 独立复用价值，还是另定一档门槛？

## 8. 风险与失败模式

- **过早信任缺口**：覆盖度不够的库会用高置信错误误导人 → 准备度门槛 + 低置信标注。
- **并发写坏**：多会话同时改同一文件导致内容丢失/乱码 → 单写规则，并行限定 disjoint 文件集。
- **溯源断裂**：raw/ 被改后无法回查 → 只读硬约束 + sources 元数据留痕。
- **链接腐烂、孤儿堆积**：长期不巡检图谱退化 → lint 挂周检，定期出孤儿/缺页清单。
- **版权风险**：长段原文入库 → 沿用现有红线：只存摘要、最短摘录、元数据。
- **上下文膨胀**：库变大后规则层/全库内容撑爆会话 → hot.md 热缓存 + 模块化 schema（规则按层拆分），大库再接本地搜索。
- **概念混淆**：wiki 页和 Skill 产物界限不清 → 靠 4.5 路由边界和晋级标准守住。

## 9. 参考来源

- Karpathy LLM Wiki 原始思路（2026-04 gist）：LLM 增量构建并维护持久化、互相链接的 Markdown wiki，知识编译一次持续保鲜，而非每次提问重新检索。
- 社区落地蓝图：`ScrapingArt/Karpathy-LLM-Wiki-Stack`（三层目录、CLAUDE.md 主 schema、ingest/query/lint 操作、frontmatter 规范、lint 报告格式、准备度与单写规则）。
- 其他跟风模板：`KHOAAI-HILL/llm-wiki-template`、`kytmanov/obsidian-llm-wiki-local`（本地 Ollama 版）。

## 10. 决策定稿（2026-11-24）

| 决策点 | 定稿 |
|---|---|
| 路由形态 | **独立 R7 `wiki-vault`**，不并入 R3 |
| 库落点 | 桌面宿主默认 `<桌面>/zyx-output/wiki/<slug>/`；豆包环境默认 `~/Doubao/wiki/<slug>/`（`ZYX_WIKI_HOME` 可覆盖）；**支持挂载已有 Obsidian 库目录**，只登记不重构，缺结构需同意后才补 |
| 前端绑定 | **只做 Obsidian Markdown**（wikilink/frontmatter/callout），不内置插件配置、不产 HTML |
| 覆盖度门槛 | **不设闸门**：lint 只出客观统计与建议，不判定「覆盖不足禁止下结论」 |
| 并发 | **显式单写、禁止并行**；多会话写同一个活动库；锁为会话租约，陈旧可接管 |
| 远端同步 | **预留 git 同步接口**（`sync-interface.md` 契约），当前未实现、无任何远端动作 |
| 晋级判据 | **复用三重验证（来源/可执行/增益）+ 具备独立复用价值** |

### 已完成（P1–P4）
- `skills/wiki-vault/`：`SKILL.md`、三份 references、`assets/templates/` 五类模板。
- `scripts/wiki.py`：注册表、单写锁（会话租约）、骨架、建页（支持 `--link-to/--backlink`）、日志、`search`、`backlink`、`archive`、`promote-check`、`sync --status`（只读）。
- `scripts/wiki-lint.py`：断链/缺页/孤儿/仅索引/索引覆盖/废弃/陈旧/过薄/矛盾 + 按类型必填字段、目录与 type 一致性、日志格式；可选 `--exit-code`。
- `scripts/wiki-selftest.py`：31 项端到端回归；`doctor.sh --full` 调用。
- zyx 接入：manifest 加 R7、路由表七类、产物布局 `wiki/`、`artifact-dir.sh` 与 `route.sh` 白名单、doctor 知识库段、回归用例 E11–E14、版本 1.2.0。
- 实测：建库 → 取锁 → 建页 → 重复覆盖被拒（4）→ 日志 → 他人持锁被拒（3/5）→ 巡检九类指标 → 挂载已有 Obsidian 库不写入。

### 已知边界（不阻塞上线）
- `sync --pull/--push` 仍为预留（写接口需单独授权后实现）；R6 反馈联动目前靠既有原语（`new-page` + `backlink` + `log`）编排，未做成独立命令；库特别大时的搜索性能后续可接外部索引。

## 11. 与豆包 personal agent 结合（2026-11-24）

### 事实边界
- 豆包技能是 Agent 的正式能力单元，PC 端「技能·连接器·伙伴 → 我的技能 → 上传技能」可拖入含 `SKILL.md` 的文件夹或压缩包；豆包工作另有可挂技能的「工作伙伴」。
- 面向个人的「小豆」处于邀请制公测，主打主动服务、记忆与后台任务，**无公开 API**。
- 因此不做私有接口对接，只做「技能 + 记忆 + 定时任务」三层适配。

### 落地
- **技能**：`scripts/package-doubao.sh` 打包（含 frontmatter 校验、排除 `state/`），产物 `dist/doubao/<skill>.zip`；上传路径写入 `references/personal-agent.md`。
- **记忆**：`wiki.py where` 给出 `slug/root/topic` 作为稳定事实；`wiki.py brief` 输出 ≤600 字简报（规模/最近日志/热缓存，`--with-lint` 带巡检），会话开头读它而非整库。
- **主动**：每周任务跑 `wiki-lint.py` + `brief --with-lint`，只推缺口与下一步；R7 不自动建任务，指令由用户确认后创建。
- **落点**：豆包环境默认 `~/Doubao/wiki/<slug>`，与手机/PC 同一账号的会话共用；`ZYX_WIKI_HOME` 可覆盖。
- **人设**：`docs/doubao/personal-agent-profile.md` 提供可粘贴的「知识库管家」指令、开场白与快捷指令。

### 验证
- `wiki-selftest.py` 34/34（新增 `where`、`brief`、`brief --with-lint`）。
- 实测豆包环境默认建库落 `~/Doubao/wiki/briefdemo`，`where` 与 `brief` 输出正常，`brief --with-lint` 附带巡检统计。

### 未做
- 小豆私有能力、自动建任务、自动外发；`sync --push` 仍预留。
