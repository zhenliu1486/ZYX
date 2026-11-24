# Changelog

本文件记录 zyx 总调度台的版本变更。版本号遵循 SemVer（MAJOR.MINOR.PATCH）。

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
