---
name: wiki-vault
description: 长期知识库（个人/领域 Wiki）维护入口。承接「建一个关于 X 的知识库」「把这篇/这本书/这段转写加进我的 X 库」「我库里关于 X 都有什么结论」「体检一下我的库」这类需要跨会话累积、反复摄入、库内检索的请求：管理 raw/ 只读原料层与 wiki/ 编译知识层，产出互为链接的 Obsidian Markdown（摘要页/实体页/概念页/对比页/综述页），维护主索引、活动日志与会话热缓存，并提供库健康巡检。已建好的 Obsidian 库可直接挂载，不搬动不重构。不替代一次性拆书（R3）、人物/行业深蒸馏（R1/R2）、当下问题诊断（R4）与产物迭代（R6）。
license: MIT
compatibility: 兼容 Claude Code / Codex / OpenClaw / Cursor / Gemini CLI / OpenCode 等 Agent Skills 标准宿主；仅依赖 Python 3 标准库与 Bash，无外部必需依赖；Obsidian 为可选阅读前端，不内置插件配置。
metadata:
  author: "ZYX"
  version: "1.0.0"
  layer: "2-capability"
  schema: "agentskills.io"
allowed-tools: Read, Write, Edit, Bash
---

# wiki-vault · 长期知识库（R7）

> 借鉴 Andrej Karpathy 2026 年提出的 LLM Wiki 模式（原料只读 → LLM 增量编译成互相链接的 Markdown 知识层 → 在库内问答并回写），按 ZYX 的产物规范与共享底座落地。**与 Karpathy 本人无隶属或背书关系，仅模式借鉴。**

## 1. 做什么 / 不做什么

**做**：一个库的完整生命周期——建库、摄入编译、库内问答、健康巡检；把一次性的资料沉淀成可累积、可回溯、可反复查询的知识资产。

**不做**：

- 不写 HTML、不内置 Obsidian 插件配置，只产 Obsidian Markdown（`[[wikilink]]` + frontmatter + callout）。
- 不改写、不删除 `raw/` 里的原始材料。
- 不替代一次性任务：拆书成 Skill 包走 R3，人物/行业深蒸馏走 R1/R2，眼下判断走 R4，产物改版走 R6。
- 不做无授权的远端同步；git 同步接口只预留，未启用。

## 2. 两个库形态

| 形态 | 命令 | 说明 |
|---|---|---|
| 受管库（新建） | `python3 scripts/wiki.py init <slug> [--topic "主题"]` | 默认落 `<桌面>/zyx-output/wiki/<slug>/`，生成 `raw/`、`wiki/` 与种子文件 |
| 挂载库（已有 Obsidian 库） | `python3 scripts/wiki.py mount <slug> <库路径> [--provision]` | **不搬动、不改名、不重构**用户既有目录；默认只检测，缺结构不擅自补，同意后才 `--provision` |

用户的库若把知识放别的目录名，用 `--wiki-dir` / `--raw-dir` 指过去，不要改用户的目录名。

## 3. 四个操作

| 操作 | 触发信号 | 动作 | 产物 |
|---|---|---|---|
| `init` | 「建一个关于 X 的知识库」 | 建骨架、写 schema、登记注册表 | 空库 + `index/log/hot/overview` |
| `ingest` | 「把这篇文章/这本书加进我的库里」 | 先验记录 → 读原料 → 摘要页 → 更新相关页 → 矛盾标注 → 补新页 → 更新索引 → 写日志 | 一页摘要 + 牵动 5–15 页 |
| `query` | 「我库里关于 X 有什么结论」 | 读索引定位 → 读命中页 → 带 wikilink 作答 → 有价值则归档 | 答案（可选归档为对比/综述页） |
| `lint` | 「体检一下我的库」 | 跑巡检脚本 → 按优先级修 → 记日志 | 健康报告 + 修复清单 |

详细步骤见 `references/operations.md`；目录与 frontmatter 规范见 `references/vault-layout.md`。

## 4. 六条硬约束

1. **`raw/` 只读**：永不写入、不删除、不改名；出错可回溯源料纠正。
2. **不删页面**：废弃只加 `deprecated: true`，正文写明替代页。
3. **每次写入都更新** `wiki/index.md` 与 `wiki/log.md`；新页至少与 2 个已有页互链。
4. **单写、禁并行**：同一库同一时刻只允许一个写会话，写前取锁、写完释放；多会话必须写同一个活动库，禁止并行写同一库。
5. **只写 Obsidian Markdown**：wikilink、YAML frontmatter、`> [!contradiction]` 等 callout；不写 HTML、不动 `.obsidian/`。
6. **不设覆盖度闸门**：巡检只出客观统计与建议，不判定「覆盖不足禁止下结论」；库能否用于判断由使用者决定。

## 5. 脚本

```bash
# 建库 / 挂载已有 Obsidian 库
python3 scripts/wiki.py init <slug> --topic "主题"
python3 scripts/wiki.py mount <slug> "/path/to/obsidian-vault" --provision

# 库与锁
python3 scripts/wiki.py list            # 列出库（--plain 只出 slug；--json 机器读）
python3 scripts/wiki.py resolve [<slug>] # 打印库根
python3 scripts/wiki.py use <slug>       # 切换活动库（多会话统一写同一个库）
python3 scripts/wiki.py status           # 活动库与持锁状态
python3 scripts/wiki.py lock <slug>      # 取写锁（--force 接管陈旧锁）
python3 scripts/wiki.py unlock <slug>

# 写页面 / 日志（未持锁会被拒绝，退出码 5）
python3 scripts/wiki.py new-page concept "增量认知校验" --title "增量认知校验"
python3 scripts/wiki.py log ingest "《xxx》摄入" --detail "新增 3 页，更新 5 页，1 处矛盾"

# 健康巡检（只读，退出码恒 0）
python3 scripts/wiki-lint.py "$(python3 scripts/wiki.py resolve)" [--json]

# 同步（预留，未实现，返回提示）
python3 scripts/wiki.py sync --status
```

规则与退出码：锁被占 → 3；页面已存在（不覆盖）→ 4；未持锁写入 → 5；参数/路径错误 → 1。

## 6. 路径与状态

- 库注册表：`../zyx/state/vaults.json`（`ZYX_STATE_DIR` 可覆盖），**不进发布包**。
- 写锁：`../zyx/state/locks/<slug>.lock`，默认 12 小时视为陈旧（`WIKI_LOCK_TTL_HOURS` 可调）。
- 库目录本身可被 Obsidian 直接打开；运行态文件不在库内，不污染图谱。

## 7. 复用 ZYX 共享底座

| 环节 | 引用 |
|---|---|
| 摄入前先验与增量标注 | `../zyx/shared/verification/incremental-check.md` |
| 新建概念/实体页前的三道闸门 | `../zyx/shared/verification/triple-verification.md` |
| 来源分级（一手/二手/推断） | `../zyx/shared/credibility/source-grading.md` |
| 归档页交付前质检与脱敏 | `../zyx/shared/quality/qa-audit.md` |
| 目录/命名/MANIFEST | `../zyx/shared/artifacts/convention.md` |

## 8. 与其他路由的衔接

- **晋级到 R3**：某份原料在库里沉淀出独立复用价值，且过三重验证（来源充分 / 可执行 / 任务增益）+ 具备独立复用价值，才委派仓颉打包成 Skill。
- **深挖走 R1/R2**：人物视角、行业打法不在库里造，wiki 只留摘要与 wikilink。
- **改版走 R6**：页面被否或要按反馈迭代时，先由 f2r 把反馈显性化为规则，再回写。
- **当下问题走 R4**：只要判断、不要求进长期库的请求不进 R7。

## 9. 边界与失败模式

- 挂载用户库时误建目录、误改结构 → 默认不写，`--provision` 才补缺失骨架。
- 并发写坏库 → 单写锁强制拦截；陈旧锁可 `--force` 但需先核对上次写入。
- 过早信任库内结论 → 不设闸门不等于无条件采信；每条结论标 `confidence` 与来源级别，缺口写进 `hot.md`。
- 库变大后上下文膨胀 → 靠 `hot.md` 热缓存 + 按需只读命中页；不整库塞进对话。
- 版权与隐私 → 不存长段原文，只留摘要 + 最短引用；入库前脱敏。

## 10. 决策记录

- 2026-11-24：确认为独立 R7 路由（不并入 R3）；支持挂载已有 Obsidian 库；只做 Obsidian Markdown；**不设覆盖度闸门**；显式单写、禁并行、多会话写同一库；预留 git 同步接口；页面晋级 Skill 复用三重验证 + 独立复用价值。
