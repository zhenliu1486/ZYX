# ZYX · Agent Skill 总调度台

一个薄壳路由入口 Skill：判断原料属于「人 / 行业 / 长内容 / 当下问题 / 内容生产 / 产物迭代 / 长期知识库 / 投资决策」，转发给对应独立 Skill，统一收口产物。被转发的蒸馏器保持独立、各自追上游 git 更新；公共校验、质检、可信度、产物规范与 Darwin 式压测抽成 `shared/` 共享底座。

## 一句话安装

把下面整行复制给任何能执行终端的 AI，或直接贴进终端：

```bash
curl -fsSL https://cdn.jsdelivr.net/gh/zhenliu1486/ZYX@main/bootstrap.sh | bash
```

GitHub 备用地址：

```bash
curl -fsSL https://raw.githubusercontent.com/zhenliu1486/ZYX/main/bootstrap.sh | bash
```

只装技能本体、不装外部依赖：

```bash
curl -fsSL https://cdn.jsdelivr.net/gh/zhenliu1486/ZYX@main/bootstrap.sh | bash -s -- --no-deps
```

> **为什么 AI 会说“没找到”**：ZYX 是 18 个技能的多技能包，根目录故意没有单个 `SKILL.md`；豆包技能安装器只认根级 `SKILL.md`，不会递归找 `skills/`。给 AI 固定 URL，不要让它自己搜 GitHub。豆包上传包与详细说明见 [INSTALL.md](INSTALL.md)。

## 仓库结构

```
ZYX/
├── skills/
│   ├── zyx/                 # 第 1 层：入口路由调度台（薄壳）
│   │   ├── SKILL.md
│   │   ├── README.md         # 日常调用示例与自检/更新说明
│   │   ├── CHANGELOG.md
│   │   ├── references/       # 路由判定表、产物目录与回传规范
│   │   ├── scripts/          # 路由解析、自注册、静默更新、自检、look.py、omarchy-bridge.py
│   │   ├── shared/          # 第 3 层：共享底座（校验/质检/可信度/规范/压测）
│   │   └── evals/           # 路由回归用例
│   ├── video-studio/         # R5 影视/短剧/漫剧制作聚合层（内部路由 9 个子技能）
│   ├── director-camera-composition/ # R5 导演运镜/机位/构图（内置）
│   ├── ai-camera-shots/      # R5 镜头语言/分镜/转场（内置，MIT 上游）
│   ├── wiki-vault/           # R7 长期知识库（raw/ 只读 → wiki/ 编译）
│   └── ashare-four-dim-decision/  # R8 投资决策总控（附 4 个四维子技能）
├── docs/
│   ├── doubao/              # 豆包 personal agent 人设卡
│   ├── research/            # 设计与决策记录
│   └── promo/               # 对外素材
├── bootstrap.sh             # 一行安装入口（curl | bash）
├── INSTALL.md               # 安装说明（含豆包上传包）
├── scripts/install.sh        # 一键安装（含内置技能）
├── scripts/sync-hosts.sh     # 同步到本机所有已存在的宿主
├── scripts/package-doubao.sh # 打成豆包「上传技能」可用的 zip
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
| 影视/短剧/漫剧/镜头设计 | `video-studio` 聚合层（含导演/镜头层） | 本仓库 `skills/video-studio` / `director-camera-composition` / `ai-camera-shots` |
| 已有产物二次迭代 | `f2r-feedback-iteration` | 本地打磨类子技能 |
| 长期知识库（个人/领域 Wiki） | `wiki-vault` | 本仓库 `skills/wiki-vault` |
| 投资 / 股票 / 波段 / 超短线 | `ashare-four-dim-decision`（+ 情绪/风口/资金/技术四子技能） | 本仓库 `skills/ashare-*` |

> R1–R4 为外部独立蒸馏器，需与本仓库 Skill 同机安装；R5 / R7 / R8 随本仓库提供。

## 安装

推荐一键安装（含内置技能；外部蒸馏器另加 `--install-deps`）：

```bash
bash scripts/install.sh --dir ~/.claude/skills

# 或一次性同步到本机所有已存在的宿主目录（macOS 自带 Bash 3.2 也可用）
bash scripts/sync-hosts.sh
```

也可以手动复制：

```bash
cp -r skills/zyx ~/.claude/skills/zyx
cp -r skills/video-studio ~/.claude/skills/video-studio
```

其他宿主：`~/.openclaw/skills`、`~/.agents/skills`、`~/.codex/skills`，或对应 Agent 的 skills 目录。macOS 自带的 Bash 3.2 已做兼容；同步脚本见 `scripts/sync-hosts.sh`。安装器先备份旧版到 `~/.zyx-backups/` 再原子替换，不会把宿主里的旧 Skill 直接删掉。

依赖：Bash、git；仓颉本体另需 Python 3.10+ 与 PyYAML。首次调用 zyx 时会自动探测环境并注册后台周检（幂等）。

## 在豆包 personal agent 里用

豆包侧没有公开的个人 Agent API，能接的是三层：**技能上传 + 记忆注入 + 定时巡检**。

```bash
# 打成豆包「上传技能」可直接拖入的 zip
bash scripts/package-doubao.sh --only wiki-vault
```

安装：豆包 PC →「技能·连接器·伙伴」→「我的技能」→ 上传技能 → 拖入 `dist/doubao/wiki-vault.zip`。
在豆包环境里，知识库默认建在 `~/Doubao/wiki/<slug>`（`ZYX_WIKI_HOME` 可覆盖）；让 Agent 记住 `wiki.py where` 的库名与路径，会话开头跑 `wiki.py brief`，每周任务跑 `wiki-lint.py`。
「知识库管家」人设卡见 [docs/doubao/personal-agent-profile.md](docs/doubao/personal-agent-profile.md)，机制与边界见 [skills/wiki-vault/references/personal-agent.md](skills/wiki-vault/references/personal-agent.md)。

## Omarchy 握手、Context Card 与 Look Gate

不新增 R9 路由；只借 Omarchy 的三个工程默认，补 ZYX 的“可验证能力”：

```bash
# 1. 只读握手：Omarchy 版本/主题/默认 agent + ZYX/R7/context 卡状态
python3 skills/zyx/scripts/omarchy-bridge.py status

# 2. 把 R7 活动库投影成跨宿主技能卡（换库自动刷新）
python3 skills/wiki-vault/scripts/wiki.py context --install

# 3. 视觉产物先渲染成图，agent 亲自看过再交付
python3 skills/zyx/scripts/look.py deck.pptx --out ./look
```

- Context 卡名为 `zyx-context`，装进 `~/.agents/skills` 与已存在的宿主目录；只覆盖带 managed 标记的卡。
- Look Gate 支持 HTML / PPTX / PDF / 视频 / 图片，输出 `look.png`、`look.json`、`MANIFEST.md`；缺渲染工具时明确报错，不冒充已验证。
- 规则见 `skills/zyx/shared/quality/visual-acceptance.md`；背景与取舍见 `docs/research/omarchy-integration.md`。

## 规范对齐

遵循开放 Agent Skills 规范（agentskills.io）：YAML frontmatter、渐进式披露（元数据 → 正文 → 按需加载 references/scripts/assets）、正文 500 行以内。模板参考 Anthropic agentskills 开放规范与 Google 官方 skills 仓库格式。

## 版本

当前 `zyx` v1.6.1，变更记录见 [skills/zyx/CHANGELOG.md](skills/zyx/CHANGELOG.md)；第一性原理审计见 [docs/research/zyx-first-principles-audit.md](docs/research/zyx-first-principles-audit.md)。

## 许可

MIT，见 [LICENSE](LICENSE)。
