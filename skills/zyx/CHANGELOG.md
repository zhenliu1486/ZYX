# Changelog

本文件记录 zyx 总调度台的版本变更。版本号遵循 SemVer（MAJOR.MINOR.PATCH）。

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
