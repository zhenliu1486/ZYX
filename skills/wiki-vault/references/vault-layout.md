# 库布局与 Obsidian Markdown 约定

> 本文件规定 R7 `wiki-vault` 管什么、目录怎么放、页面长什么样。只做 Obsidian Markdown，不产出 HTML，不内置插件配置。

## 1. 两种库形态

| 形态 | 场景 | 命令 | 规则 |
|---|---|---|---|
| **受管库** `managed` | 从零建一个知识库 | `wiki.py init <slug> [--topic T]` | 默认建在 `<桌面>/zyx-output/wiki/<slug>/`，自动生成 `raw/`、`wiki/` 与四个种子文件 |
| **挂载库** `mounted` | 用户已有 Obsidian 库，直接接进来 | `wiki.py mount <slug> <路径> [--provision]` | **不搬动、不重命名、不重构**用户既有目录；只登记路径并检测结构 |

挂载已有 Obsidian 库时：

1. 先只读检测：`.obsidian/` 是否存在、`raw/` 与 `wiki/index.md` 是否已具备。
2. 结构齐全 → 直接可用，不改任何文件。
3. 结构不全 → 默认**不写**，报告缺什么；用户同意后才加 `--provision`，且只补建缺失的目录与种子文件，不触碰已有文件。
4. 用户的库若用别的目录名（如 `notes/` 存知识、`inbox/` 存原料），用 `--wiki-dir` / `--raw-dir` 指向既有目录，不要改名。

## 2. 目录结构（受管库默认）

```
<vault>/
├── raw/                        # L1 原料层：只读，永不修改
│   ├── articles/               #   网页剪藏（Obsidian Web Clipper）
│   ├── papers/                 #   论文、PDF 笔记
│   ├── transcripts/            #   播客/视频/会议转写
│   ├── data/                   #   CSV/JSON/评测结果
│   └── assets/                 #   图片等附件（Obsidian 附件目录）
├── wiki/                       # L2 知识层：LLM 写，人只读
│   ├── index.md                #   主索引，每次摄入必更
│   ├── log.md                  #   活动日志，只追加
│   ├── hot.md                  #   会话热缓存（≤500 字），会话开头先读
│   ├── overview.md             #   全库综述，重大变更后修订
│   ├── sources/                #   每份原料一页摘要
│   ├── entities/               #   人/公司/产品/组织
│   ├── concepts/               #   方法/技巧/理论
│   ├── comparisons/            #   对比页（可从问答归档）
│   └── syntheses/              #   长综述（可从问答归档）
├── schema.md                   # L3 规则层（可与人不短迭代；换宿主可复制为 CLAUDE.md/AGENTS.md）
└── MANIFEST.md                 # 可选：库清单与验证记录（按需生成）
```

运行态（库注册表、写锁）不在库目录内，统一放 `zyx/state/`，不污染 Obsidian 图谱。

## 3. 页面 frontmatter 规范

所有页面必须有 YAML frontmatter；`type` 与 `title` 为必填。按类型补齐：

### 3.1 来源摘要页 `wiki/sources/summary-<slug>.md`

```yaml
---
type: source
title: "文章/论文标题"
slug: summary-<slug>
source_file: raw/articles/<文件名>
author: ""
date_published: ""
date_ingested: 2026-11-24
key_claims: []
related: []
confidence: low
---
```

### 3.2 概念页 `wiki/concepts/<slug>.md`

```yaml
---
type: concept
title: "概念名"
aliases: []
sources: []
related: []
created: 2026-11-24
updated: 2026-11-24
confidence: low
cluster: ""
cluster_role: member   # hub | member；hub 页须有「本集群包含」段
---
```

### 3.3 实体页 `wiki/entities/<slug>.md`

```yaml
---
type: entity
entity_type: person   # person | company | product | org
title: "实体名"
sources: []
related: []
created: 2026-11-24
updated: 2026-11-24
cluster: ""
contradictions: []
open_questions: []
---
```

### 3.4 对比页 `wiki/comparisons/<slug>.md`

```yaml
---
type: comparison
title: "A vs B"
sources: []
related: []
filed_from_query: true
date: 2026-11-24
---
```

### 3.5 综述页 `wiki/syntheses/<slug>.md`

```yaml
---
type: synthesis
title: "综述标题"
sources: []
related: []
filed_from_query: true
date: 2026-11-24
---
```

> `confidence` 取 `high | medium | low`；没把握一律 `low`，不冒充确定结论。来源级别（一手/二手/推断）写在 `sources/` 页与正文引用里，口径沿用 `../../zyx/shared/credibility/source-grading.md`。

## 4. Obsidian Markdown 写法

- **页内链接一律用 wikilink**：`[[concepts/xxx]]` 或 `[[xxx]]`；不用 Markdown 相对链接，保证图谱和反向链接可用。
- **别名**写 `aliases`，方便 `[[缩写]]` 也能解析。
- **矛盾**用 callout 显式标注，不悄悄改掉旧结论：

```markdown
> [!contradiction] 与 [[concepts/xxx]] 冲突
> 旧说法：……（来源：[[summary-a]]）
> 新证据：……（来源：[[summary-b]]）
> 处置：保留双方，标 confidence: low，待补充来源。
```

- **待补问题**用 `> [!question]`；**风险/限制**用 `> [!warning]`。
- **图片**放 `raw/assets/`，页面内用 `![[assets/xxx.png]]` 引用；远程图片容易失效，能本地化就本地化。
- **标签**用行内 `#tag` 或 frontmatter `tags`，不要为流量堆无关标签。
- 不写 HTML 块、不改 `.obsidian/` 配置、不装插件；Obsidian 只作为阅读前端。

## 5. 命名规则

- 页面文件名用小写英文连字符或中文短名，不含空格与特殊字符；`concepts/` 下同义概念只留一页，其余用 `aliases`。
- 同一主题重写不覆盖：加日期后缀或另立新页并标 deprecated，具体见下条。
- 废弃页**不删除**：frontmatter 加 `deprecated: true`，正文顶部写清替代页 `[[...]]`。
- 不用 agent id、会话 id、临时文件名做页名。

## 6. 主索引 / 日志 / 热缓存

- `index.md`：按集群分节，每行一页；每次摄入、建页、归档后更新。孤儿页多半是漏了这一步。
- `log.md`：只追加，格式固定 `## [YYYY-MM-DD] ingest|query|lint|init|sync|note | 标题`；不删旧条目。
- `hot.md`：≤500 字，只放当前最相关的上下文、未决问题、最近动作；每次摄入后重写。
- `overview.md`：全库层面的综述；集群增删或大规模摄入后修订。

## 7. 与同步（预留）

库默认只落本机。`git` 同步接口仅预留设计，未启用；契约见 `sync-interface.md`。开启前必须先脱敏并单独授权。
