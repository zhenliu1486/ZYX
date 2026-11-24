# 同步接口（预留，未实现）

> 状态：**契约设计，未启用**。当前库只落本机，不自动访问远端、不自动 push。启用前必须单独授权。

## 1. 设计目标

让知识库能像代码一样被版本管理，同时不把隐私和版权风险带出去：

- 只同步知识层（`wiki/`、`schema.md`、`MANIFEST.md`），**不同步 `raw/`**（原始素材可能含隐私、版权内容与大文件）。
- 默认 dry-run：先报告将要发生什么，用户确认后才真正执行。
- 远端写动作（push/建仓/tag）沿用 zyx 现有边界：当轮明确授权。

## 2. 计划中的子命令（占位，当前返回「未实现」）

```bash
python3 scripts/wiki.py sync --status        # 只读：本地改动、领先/落后、冲突预检
python3 scripts/wiki.py sync --pull          # 拉取（ff-only，冲突则停）
python3 scripts/wiki.py sync --push --dry-run # 默认；只报告将提交什么
python3 scripts/wiki.py sync --push          # 需显式确认 + 远端授权
```

## 3. 契约要点

| 项 | 约定 |
|---|---|
| 同步范围 | `wiki/**/*.md`、`wiki/index.md`、`wiki/log.md`、`schema.md`；排除 `raw/`、`.obsidian/`、`.trash/`、`*.canvas` |
| 分支 | 默认 `main`；可用 `WIKI_SYNC_BRANCH` 覆盖 |
| 冲突策略 | **不自动合并**。检测到分叉即停，列出冲突文件，交人工处理；禁止 `--force-push` |
| 提交信息 | `wiki(<slug>): ingest <title> / lint / query archive`，与 `log.md` 条目对应 |
| 凭据 | 不写入库、不写入 registry；复用宿主已有 git 凭据，摸不到就不推 |
| 脱敏 | push 前强制过 `../../zyx/shared/quality/qa-audit.md`；未过则拒绝推送 |
| 锁 | 同步期间必须持写锁；与写页面共用单写规则，避免拉取覆盖正在写的内容 |
| 失败 | 只读检查失败不阻断本地使用；push 失败保留本地提交，提示手工处理 |

## 4. 启用前要补的代码

1. `sync.py`：状态检测（git status/rev-list）、范围过滤、dry-run 报告。
2. 冲突检测与人工介入流程；禁止自动 merge。
3. 远端授权校验：读注册表 `sync_remote` 字段，未授权直接拒绝。
4. 回归用例：分叉拒绝、raw 不外传、未脱敏拒推、dry-run 不改远端。

## 5. 当前行为

- 调用 `wiki.py sync` 会明确返回「预留接口，未实现」并退出非零，不产生任何远端动作。
- 需要备份时，用户可自行 `git init` 在库目录并本地提交，ZYX 不代管。
