# Changelog

本文件记录 zyx 总调度台的版本变更。版本号遵循 SemVer（MAJOR.MINOR.PATCH）。

## 1.8.0 — 2026-11-27

### 新增 · R5 导演层与镜头层
- 新增 `director-camera-composition`：中文“剧本/情绪 → 机位方案”导演层。含 12 种情绪 × 六维处方、8 种 beat × 镜头配比、情绪转换三种走法、正反打/180°/30°、竖屏 9:16、分镜表六行格式、提示词四查与重写。
- 内置 `ai-camera-shots`：MIT 镜头语法层，提供五决策、34 种镜头、运镜、转场、镜头清单与 9:16 构图；作为导演层的词典与兜底。
- `video-studio` 升级为 9 个内置子技能 + 1 个可选外部词汇包；新增“导演判断 → 镜头语法 → 词汇增强”的三步链路，动作戏仍由 `cinematic-fight-direction` 主控。
- `deps/manifest.json` 新增 `R5-shots`、`R5-director`；`zyx_version` 升至 1.8.0。
- 安装器与豆包上传包随仓库更新，内置技能数从 16 变为 18。

### 边界
- 导演层只做镜头层方案，不做灯光/调色系统、剪辑节奏与声音、具体影片判读。
- 保留 `ai-camera-shots` 与两位 MIT 上游的 `LICENSE` / `UPSTREAM.md`；不把上游 references 复制进 `video-studio`。

## 1.6.1 — 2026-11-27

### 修复 · FC-001 汇洲智能案例暴露的三类偏差
- 新增 `ashare-four-dim-decision/references/failure-cases.md`：完整记录 2026-11-23 方案（代码 002057 错位 / 漏摘帽复牌催化 / 给出一字板不可能成交的低吸价）与实际走势，含逐日数据、结果核算、六条错误与根因。
- `ashare-four-dim-decision/SKILL.md` 新增「标的资格预筛（五问）」：名称-代码-行情三向核对、30 日事件扫描、一字板可买性判定、流动性与连板位置；流程第 5 步前置该预筛。
- 闸门由 5 条扩为 7 条：第 6 条「可买性（前一日一字板 → 本轮作废）」、第 7 条「事件驱动（摘帽复牌/异常波动/连续龙虎榜 → 仓位上限 10%）」。
- 红线新增三条：代码未三向核对不得写入执行表；一字板标的不给低吸买点；闸门命中不得输出价位。
- 候选标的表新增「代码核验」「可买性」两列，闸门检查表补两行。
- `scripts/score.py` 新增 `--locked-limit-up`（本轮作废、仓位 0）与 `--event-driven`（仓位上限 10%）两个闸门开关，规则从文档变为可执行。

## 1.6.0 — 2026-11-27

### 新增 · R8 投资决策
- 新增 `ashare-four-dim-decision`（总控）与四个子技能：`ashare-sentiment-cycle`（情绪偏好周期）、`ashare-theme-wind`（市场风口研判）、`ashare-capital-flow`（资金流向追踪，含大宗与暗盘资金）、`ashare-technical-structure`（技术结构分析）。
- 面向 A 股 2–4 周波段，其建仓时点与纪律部分可用于超短线：先判市场状态（单边趋势 / 震荡结构 / 题材亢奋 / 退潮冰点 / 系统性风险）取**动态权重**，四维打分 → 一致性系数 → **一票否决闸门** → 仓位映射 → 输出精确到**日期 + 盘中时段**（09:15-09:25 / 09:30-10:00 / 10:00-11:00 / 14:30-14:50）的动作与触发条件。
- `scripts/score.py`：确定性加权与一致性校验，避免手算漂移；支持 `--trend up|range|down`、`--index-broken`、`--state`、`--json`。

### 路由与清单
- `zyx` 由七类扩为八类，新增 R8「投资 / 股票 / 波段 / 超短线」路由与触发词（投资建议、买哪只、几点买、什么时候卖、仓位、做波段、打板、复盘、暗盘资金、止损）。
- `deps/manifest.json` 登记 R8 与 4 个子技能（`source=bundled`），`zyx_version` 同步 1.6.0。
- `route.sh` 新增 `invest`；`route-selftest.py` 覆盖升至 9 项（新增路由 + 未知类型拒绝）。
- `references/routing-table.md` 补 R8 判定信号、边界与衔接段；R5 行「投资决策不归这里」改为「走 R8」。

### 边界
- 投资类只产出研究性操作方案：不代下单、不承诺收益、不隐藏风险；资金量 / 交易周期 / 风险偏好不明时先问清再给方案。

## 1.5.0 — 2026-11-25

### 第一性原理审计修复
- **安装器原子化**：`scripts/install.sh` 不再先 `rm -rf` 目标目录；改为 stage 复制 → 旧目录备份 → rename 替换，替换失败自动恢复旧版。备份落在 `~/.zyx-backups/install-<时间>-<pid>/`，可用 `ZYX_INSTALL_BACKUP` 覆盖。
- **路由 fail closed**：`route.sh` 在目标蒸馏器缺失时返回退出码 2，不再“打印未检测到但返回 0”；调用方不会把未解析当成已解析。
- **Context Card 防覆盖**：`wiki.py context --install` 不只检查 `SKILL.md`，同名目录或同名文件只要不是 ZYX 托管卡就整体拒绝；`use/init/mount` 刷新旧卡失败时只警告，不回滚主操作。
- **macOS 调度**：`env-registry.sh` 在 Darwin 上优先 `launchd`，避免 cron 受 TCC/省电策略影响不执行；systemd 单元路径加引号。
- **Look Gate 能力检查**：`doctor.sh` 不再只查 `chromium`/`soffice` 二进制名，改为检查 `chromium` 或 Playwright、`libreoffice` 或 `soffice`，按能力而不是按命令名判断。
- **`sync-hosts.sh --list-hosts`**：只列候选目录，不再逐个调用安装器。

### 新增
- `scripts/route-selftest.py`：七类路由映射 + 未知类型拒绝，8 项；`doctor --full` 自动执行。
- `wiki-selftest.py` 增至 43 项：补“已有非托管同名目录”“同名文件”两类 Context 冲突用例。
- `doctor.sh` 新增第 12 段路由自测。

### 验证
- `wiki-selftest.py` 43/43；`route-selftest.py` 8/8；`look-selftest.py` 6/6；`doctor --full` 全部就绪。
- 原子安装实测：旧目录含自定义文件时被完整备份，新版本正常落位。
- launchd 分支用 fake `uname`/`launchctl` 模拟注册，plist 与 state 均生成。
- macOS 真机仍未接通（`SANDBOX_UNAVAILABLE`），Bash 3.2 与 launchd 未在真机复跑。

## 1.4.1 — 2026-11-24

### 修复
- **macOS 自带 Bash 3.2 兼容**：`scripts/install.sh` 不再用 `mapfile`（改为 `while read` 收集数组）；`artifact-dir.sh` 不再用 `declare -A`（改为 `case` 映射）。此前在 macOS 默认 shell 会直接报错。
- `deps/manifest.json` 的 `host_dirs` 补 `~/.codex/skills`，与 Context Card 的目标目录一致。

### 新增
- `scripts/sync-hosts.sh`：一条命令把内置 Skill 同步到本机所有已存在的宿主目录，复用 `install.sh` 并逐个自检；兼容 Bash 3.2。

### 验证
- Linux 上 `install.sh`、`sync-hosts.sh`（8 个宿主）、`doctor --full`、两个 selftest 均通过。
- macOS 真机尚未接通（`SANDBOX_UNAVAILABLE`），Bash 3.2 兼容写法未在真机复跑；接入后应执行 `bash scripts/sync-hosts.sh` 复验。

## 1.4.0 — 2026-11-24

### 新增
- **Context Card（状态投影技能卡）**：`wiki.py context [--install|--remove]` 把 R7 活动库投影成 `zyx-context/SKILL.md`，装进 `~/.agents/skills` 与已存在的宿主目录；`use` 切换活动库时自动刷新托管卡，换 agent 不失忆。只覆盖带 managed 标记的卡，拒绝覆盖用户同名技能。
- **Look Gate（视觉验收）**：`scripts/look.py` 把 HTML / PPTX / PDF / 视频 / 图片渲染成 `look.png` contact sheet，写 `look.json` 与 `MANIFEST.md`；`shared/quality/visual-acceptance.md` 规定“agent 亲自看图才算验收”。缺渲染工具时明确报错，不冒充已验证。
- **Omarchy 只读握手**：`scripts/omarchy-bridge.py status` 报告 Omarchy 版本、主题、默认 agent、共享 skills 目录，以及 ZYX/R7/context 卡是否就位；`--install-context` 一条命令装卡。不写系统配置、不新增 R8 路由。
- **Look 自测** `scripts/look-selftest.py`：目录拼图 / JSON / MANIFEST / unsupported / 缺失文件 6 项；`doctor --full` 调用。
- **回归用例** E19–E21：视觉产物先看后交、context 跨宿主、Omarchy 握手不抢路由。

### 变更
- `wiki-selftest.py` 由 34 项扩为 41 项（context 预览/安装/幂等/防覆盖/移除/换库刷新）。
- `artifact-dir.sh` 白名单加 `look`；`qa-audit.md` 加视觉验收必过项。
- `wiki-vault` metadata 版本 1.2.0；`zyx` 版本 1.4.0。

### 边界
- Look Gate 依赖 chromium/playwright、libreoffice、pdftoppm、ffmpeg、Pillow/ImageMagick；缺工具时在 MANIFEST 标“未做视觉验收”，不得宣称已验证。
- Omarchy 只做握手；`/usr/share/omarchy` 只读，`~/.agents/AGENTS.md` 不自动写。

## 1.3.0 — 2026-11-24

### 新增
- **豆包 personal agent 适配**：`wiki.py where`（库名/根/主题，`--json` 机器读）与 `wiki.py brief`（≤600 字简报：规模/最近日志/热缓存，`--with-lint` 带巡检摘要），供豆包侧记忆注入与会话开头加载。
- **豆包环境默认库根**：检测 `DOUBAO_*` 运行时或 `~/Doubao` 存在时，`wiki init` 默认落 `~/Doubao/wiki/<slug>`；`ZYX_WIKI_HOME` 可覆盖，其他宿主维持桌面 `zyx-output/wiki`。
- **技能上传打包脚本** `scripts/package-doubao.sh`：把技能目录打成 `SKILL.md` 位于 zip 根目录的包，供豆包 PC「我的技能 → 上传技能」直接拖入；打包时校验 YAML name/description，排除 `state/`、`__pycache__`。
- **「知识库管家」人设卡** `docs/doubao/personal-agent-profile.md`：可直接粘贴的人设指令、开场白、快捷指令与挂载验证步骤。
- **结合说明** `skills/wiki-vault/references/personal-agent.md`：技能/记忆/定时任务/分发四层落地、安装步骤、移动端回复规范、隐私与边界。
- **回归用例** E17–E18：豆包侧会话开头 `brief`、库位置记忆与默认路径。

### 变更
- `wiki-selftest.py` 由 31 项扩为 34 项（新增 `where`、`brief`、`brief --with-lint`）；`wiki-vault` metadata 版本 1.1.0。
- R7 文档补豆包小节；README 补安装与用法；`wiki-vault` SKILL 增加 `where/brief` 命令。

## 1.2.0 — 2026-11-24

### 新增
- **R7 长期知识库路由** `wiki-vault`（随仓库内置）：借鉴 Karpathy LLM Wiki 模式，`raw/` 只读原料层 → `wiki/` 增量编译成互为链接的 Obsidian Markdown（摘要/实体/概念/对比/综述页），维护主索引、活动日志、会话热缓存与全库综述；承接建库、摄入编译、库内问答、健康巡检四类操作。
- **挂载已有 Obsidian 库**：`wiki.py mount <slug> <路径>` 只登记路径并检测结构，不搬动、不重命名、不重构用户既有目录；缺结构默认不写，用户同意后才 `--provision` 补缺失骨架；知识放别的目录名时可用 `--wiki-dir` / `--raw-dir` 指向既有目录。
- **单写锁与禁并行**：写操作前必须 `lock`，脚本对未持锁写入（退出码 5）与他人持锁（退出码 3）直接拒绝；锁为会话租约（`WIKI_SESSION_ID` 区分会话），默认 12 小时视为陈旧，可 `--force` 接管。
- **健康巡检** `wiki-lint.py`：扫描断链、缺页（被提及 ≥3 次却无独立页）、孤儿页、仅索引引用、frontmatter 问题、索引覆盖、废弃页仍被引用、陈旧页、过薄页与矛盾标记；只读、退出码恒 0。
- **库注册表** `state/vaults.json` 与活动库切换 `use`：多会话统一写同一个库；运行态不进发布包、不污染 Obsidian 图谱。
- **检索与归档闭环**：`wiki.py search` 库内全文检索（可按类型过滤）、`backlink` 幂等回链、`new-page --link-to/--backlink` 建页即互链、`archive` 把问答结果归档为对比/综述页并自动回链与写日志。
- **晋级自查** `promote-check`：只读检查来源/可信度/关联/可执行步骤/边界五项，作为交 R3 前的候选筛查，不阻断流程。
- **lint 增强**：补按类型必填字段（source_file/date_ingested/entity_type/confidence/cluster/date）、目录与 type 一致性、活动日志格式检查；新增可选 `--exit-code` 供批处理，默认仍恒 0。
- **可选模板** `assets/templates/`：五类页面模板（纯 Markdown，不内置插件配置）。
- **端到端自测** `scripts/wiki-selftest.py`：31 项覆盖建库/锁/并发/重复/回链/归档/检索/lint/挂载/sync；`doctor.sh --full` 自动调用。
- **回归用例** E11–E16：R7 路由判别（vs R3/R1/R2）、挂载不重构、单写并发拒绝、巡检不设覆盖度闸门、检索归档、晋级自查。

### 变更
- zyx 路由从六类扩为七类；路由表、产物布局（`wiki/<slug>/`）、`artifact-dir.sh`（白名单加 `wiki`）、`route.sh`（`wiki` 分支）、doctor 自检（知识库段）同步更新。
- README 补 R7 定位、布局、调用示例与 FAQ；研究方案 `docs/research/karpathy-wiki-integration.md` 记录决策。

### 预留（未实现）
- **知识库 git 同步写接口**：契约见 `skills/wiki-vault/references/sync-interface.md`；只同步 `wiki/`、`schema.md`，不同步 `raw/`；默认 dry-run、冲突不自动合并、推送前强制脱敏与单独授权。`sync --status` 已实现为只读本地检查；`--pull` / `--push` 仍返回「未实现」（退出码 2），不产生任何远端动作。

## 1.1.0 — 2026-11-24

### 新增
- **声明式依赖清单** `deps/manifest.json`：统一登记 R1–R6 与可选达尔文的来源类型（git/npx/bundled）、安装命令、必需/可选、子技能归属；doctor / updater / install 脚本共用这一份事实源，不再在脚本里硬编码依赖数组。
- **一键安装器** `scripts/install.sh`：识别宿主 skills 目录（`--dir` 指定、`--list-hosts` 列出、`--install-deps` 同时装外部 git/npx 依赖），复制全部内置 Skill 后自动跑 doctor 自检。
- **内置 R5 七子技能与 R6 迭代器**：`screenplay-development`、`short-drama-screenwriter`、`manju-character-library`、`manju-scene-library`、`cinematic-fight-direction`、`micro-expression-video`、`manju-production-pipeline`、`f2r-feedback-iteration` 随仓库打包，外部宿主可复现 R5/R6 能力。
- **完整性校验** `check-integrity.py`：扫描 Skill 内 Markdown 链接与行内代码引用的本地文件，报悬空引用与缺失 SKILL.md；纳入 doctor 自检。
- **清单读取器** `deps.py` 与共用库 `lib-common.sh`：宿主目录探测、依赖行、git 仓库清单统一从 manifest 读取；内置兄弟技能优先在 zyx 同级目录解析。
- **回归用例补充**：依赖缺失降级（E7）、版本 behind/ahead 与远端不可达（E8）、产物命名与脱敏（E9）、模糊信号裁决（E10）。

### 优化
- **doctor 自检覆盖**：按清单逐项检查必需/可选依赖；补 R5 子技能检查（消除假阳性）；新增文件完整性段；`--online` 可选做上游网络可达性检查。
- **updater 健壮性**：git 依赖从清单读取；连续失败阈值改为 `ZYX_FAIL_THRESHOLD` 可配置（默认 3）；自身版本比对补远端 HEAD SHA 记录（版本号 + SHA 双口径）。
- **文档对齐**：README 安装段对齐 `skills/` 实际布局，补 Doubao 用户技能目录路径；SKILL.md 描述分层为生产路由触发与运维指令；路由表/产物规范指向 manifest 与预留远端接口说明。

### 预留（未实现）
- zyx 自身远端**自动快进覆盖**：版本号 + SHA 比对已接入；自动覆盖运行中的 zyx 目录仍需人工确认，未启用。
- 远端产物 fetch/commit 接口：待有远端产物仓库后补，推送前强制脱敏与质检清单。

## 1.0.2 — 2026-11-24

### 新增
- **zyx 自身远端版本比对**：拉取远端 `skills/zyx/SKILL.md` 版本号与本地比对，输出最新 / 落后 / 超前；结果落盘 `state/self-version.json`，纳入 drift 报告与 doctor 自检。自身快进覆盖仍预留，落后时提示人工确认。
- **doctor.sh 补全**：探测目录与 updater 对齐并支持 `ZYX_EXTRA_SKILL_DIRS`；跨宿主探测 dbs；新增 R5 video-studio、R6 f2r 可选依赖检查；新增「zyx 自身版本」自检段。
- **远端分支回退**：自身版本抓取按 `ZYX_BRANCH`（默认 main）→ master 顺序回退，避免过渡期 404 误判。

### 优化
- 失败计数改用 Python 读写 JSON，保证状态文件格式合法；drift 报告同步改为 JSON 解析。
- `route.sh` 探测目录与 updater 对齐并支持环境变量追加。
- 清理 updater 中的死代码；README 补充 `ZYX_REPO` / `ZYX_BRANCH` / `ZYX_EXTRA_SKILL_DIRS` 环境变量说明。

## 1.0.1 — 2026-11-24

### 新增
- **R5 内容生产路由**：新增 `video-studio` 影视制作聚合层，内部路由到剧本开发、竖屏短剧编剧、人物设定库、场景库、动作/打斗分镜、微表情视频参数、全流程生产 SOP 七个子技能。
- **R6 产物迭代路由**：已有产物（Skill / MD 文档）二次修改迭代指向 `f2r-feedback-iteration`，可联动 `dbs-resonate` / `dbs-ai-check`。
- **自检脚本** `scripts/doctor.sh`：输出就绪状态、缺什么、怎么补（同仓颉 doctor 思路）。
- **桌面目录跨平台探测** `scripts/desktop-dir.sh`：按「系统桌面 → 文档目录 → `$HOME/zyx-output`」回退，路径不写死宿主。
- **规范产物目录脚本** `scripts/artifact-dir.sh`：给定来源 + 产物名 + 可选日期，返回规范目录并可创建，统一命名与 slug 化。
- **evals/ 回归用例**：人 / 行业 / 长内容 / 当下问题 / 内容生产 / 产物迭代各一条路由裁决用例。
- **CHANGELOG.md**：建立版本变更记录。

### 变更
- **R3 衔接段**：无文字稿时先走 `dbs-video-extract` 或本地转写，拿到文字稿后再进仓颉。
- **updater.sh 扩充**：探测目录清单扩充并支持 `ZYX_EXTRA_SKILL_DIRS` 环境变量追加；新增失败计数、连续 N 次失败下次对话提示、`--check-drift` drift 报告；zyx 自身版本检查预留 `ZYX_REPO` 远端比对接口。
- **shared 底座标注**：六个 shared 文件头部补「引用方与挂载阶段」。
- **产物规范**：补 `video/`、`f2r/` 来源子目录；补隐私与脱敏边界。
- **README**：补人物蒸馏、行业蒸馏、拆书诊断、生意诊断、直接生成编导脚本五类日常调用示例；更新三层结构与自检/更新说明。

### 安全 / 质检
- `quality/qa-audit.md` 把「发布前脱敏」列为必过项：脱敏未过禁止发布/外发。

### 预留（未实现）
- zyx 自身远端**自动快进覆盖**：版本比对已在 1.0.2 接入；自动覆盖运行中的 zyx 目录仍需人工确认，未启用。
- 远端产物 fetch/commit 接口：待有远端产物仓库后补。

## 1.0.0 — 2026-11-23

### 新增
- **zyx 入口薄壳**：`SKILL.md` 路由流程 + `references/routing-table.md` 判定表，把人 / 行业 / 长内容 / 当下问题分别转发 R1 女娲、R2 大师、R3 仓颉、R4 dbs。
- **三层软融合**：第 1 层 zyx 入口；第 2 层三个独立蒸馏器 + dbs 家族；第 3 层 `shared/` 共享底座。
- **共享底座**：增量认知校验、三重交叉验证、质检与审计清单、来源可信度分级、产物目录规范、Darwin 式压测口径。
- **脚本**：`route.sh` 路由解析；`env-registry.sh` 首次触发环境探测与后台周检注册（cron / launchd / systemd，幂等）；`updater.sh` 静默快进更新（ff-only + 浅克隆兜底 + 旧 HEAD 备份，dbs 只比对不覆盖）；`check-updates.sh` 兼容封装。
- **定时周检**：每周日 18:00 云端触发上游更新检查。
- **产物规范**：`references/artifact-layout.md` 目录结构、命名与收口回传清单格式。
- 达尔文 `darwin-skill` 作为第 3 层压测底座依赖装入各宿主。
