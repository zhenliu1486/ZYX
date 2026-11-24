# ZYX · Agent Skill 总调度台

一个薄壳路由入口 Skill：判断原料属于「人 / 行业 / 长内容 / 当下问题 / 内容生产 / 产物迭代」，转发给对应独立 Skill，统一收口产物。被转发的蒸馏器保持独立、各自追上游 git 更新；公共校验、质检、可信度、产物规范与 Darwin 式压测抽成 `shared/` 共享底座。

## 仓库结构

```
ZYX/
├── skills/
│   ├── zyx/                 # 第 1 层：入口路由调度台（薄壳）
│   │   ├── SKILL.md
│   │   ├── README.md         # 日常调用示例与自检/更新说明
│   │   ├── CHANGELOG.md
│   │   ├── references/       # 路由判定表、产物目录与回传规范
│   │   ├── scripts/          # 路由解析、自注册、静默更新、自检、产物目录
│   │   ├── shared/          # 第 3 层：共享底座（校验/质检/可信度/规范/压测）
│   │   └── evals/           # 路由回归用例
│   └── video-studio/         # R5 影视/短剧/漫剧制作聚合层（内部路由子技能）
├── .gitignore
└── LICENSE
```

## 路由一览

| 原料类型 | 转发到 | 上游 / 来源 |
|---|---|---|
| 人（思维方式 / 名人 OS） | 女娲 `nuwa-skill` | alchaincyf/nuwa-skill |
| 细分行业 | 大师 `master-skill` | swaylq/master-skill |
| 长内容（书/视频/播客/课程/访谈） | 仓颉 `cangjie-skill` | kangarooking/cangjie-skill |
| 当下问题（诊断/文案/决策/协作） | dbs 家族 | dontbesilent2025/dbskill |
| 影视/短剧/漫剧制作 | `video-studio` 聚合层 | 本仓库 `skills/video-studio` |
| 已有产物二次迭代 | `f2r-feedback-iteration` | 本地打磨类子技能 |

> R1–R4 为外部独立蒸馏器，需与本仓库 Skill 同机安装；R5 聚合层随本仓库提供。

## 安装

把需要的 Skill 目录复制到兼容宿主的 skills 目录：

```bash
# 以 Claude Code 为例
cp -r skills/zyx ~/.claude/skills/zyx
cp -r skills/video-studio ~/.claude/skills/video-studio
```

其他宿主：`~/.openclaw/skills`、`~/.agents/skills`，或对应 Agent 的 skills 目录。

依赖：Bash、git；仓颉本体另需 Python 3.10+ 与 PyYAML。首次调用 zyx 时会自动探测环境并注册后台周检（幂等）。

## 规范对齐

遵循开放 Agent Skills 规范（agentskills.io）：YAML frontmatter、渐进式披露（元数据 → 正文 → 按需加载 references/scripts/assets）、正文 500 行以内。模板参考 Anthropic agentskills 开放规范与 Google 官方 skills 仓库格式。

## 版本

当前 `zyx` v1.0.2，变更记录见 [skills/zyx/CHANGELOG.md](skills/zyx/CHANGELOG.md)。

## 许可

MIT，见 [LICENSE](LICENSE)。
