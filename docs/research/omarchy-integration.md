# Omarchy × ZYX：从「技能」到「可验证能力」

> 研究对象：https://github.com/omacom/omarchy（v4.0.0.alpha，2026-11-24 拉取）。结论先说：**Omarchy 不是一个能装进 ZYX 的 skill，而是一套把操作系统变成「agent 可调用、可验证、可回滚」的工程范式。** ZYX 该借的不是它的主题和快捷键，而是它的能力契约。

## 1. 先纠正前提：Omarchy 到底是什么

Omarchy 是 DHH 做的「agentic Linux distribution」：Arch Linux + Hyprland + 一套 Quickshell 桌面，外加一层专门给 coding agent 用的运行时。

它真正特别的地方不在界面，而在四件事：

1. **把系统能力做成命令 API**：所有能力走 `omarchy <group> <action>`，每个命令带 `omarchy:summary/args/examples` 元数据，`omarchy commands --json` 可机器读。
2. **给 agent 发一套系统级技能**：仓库内置 7 个 skill——`omarchy`（改桌面）、`omarchy-make-theme`、`omarchy-make-plugin`、`omarchy-make-app`、`omarchy-make-game`、`omarchy-contribute`、`omarchy-diagnose-crash`，并按主题拆成 `hyprland.md / shell.md / theming.md / apps.md / system.md / hooks.md / capture.md` 渐进加载。
3. **把技能装进所有宿主**：`omarchy-agent-skills-link` 把自家技能链进 `~/.agents/skills`、`~/.claude/skills`、`~/.codex/skills`、`~/.pi/agent/skills`、`~/.gemini/config/skills`、`~/.hermes/skills`；个人规则统一放 `~/.agents/AGENTS.md`，再链进各家。
4. **要求 agent 先验证再宣称完成**：`omarchy agent look theme/app/plugin/page` 会把结果渲染成图并检查对比度、尺寸、可读性；仓库还有 `test/acceptance.d/` 的图形验收测试和 `oligarchy-tests/` 的 QEMU 全系统测试；系统变更走 `migrations/` 时间戳脚本，配置可 `refresh` 回默认。

一句话：**它把「skill」从一段提示词，升级成了有地址、有权限、有验收、有迁移的系统能力包。**

## 2. 用第一性原理拆：一个能力要能被 agent 安全使用，必须回答五个问题

| 最小问题 | Omarchy 的答案 | ZYX 的现状 | 差距 |
|---|---|---|---|
| 怎么调用？ | `omarchy <group> <action>`，带元数据与 JSON 列表 | `route.sh` 只打印路由决策，具体执行靠对话 | 缺每类路由的确定性入口 |
| 什么时候用？ | skill description + references 分层 | 七类路由表 + 触发词，做得比多数项目好 | 基本对齐 |
| 能碰什么？ | `/usr/share/omarchy` 只读；`~/.config` 可写；sudo/pkexec 分场景 | 文本边界 + 锁 + 脱敏清单 | 边界是「说给模型听」，不是「脚本强制」 |
| 怎么验证？ | look 预览 + 图形验收 + QEMU 全系统测试 | R7 有 34 项 selftest；其余路由靠文本质检 | 缺「产物长什么样」的验收 |
| 怎么回滚？ | migrations + refresh + 备份 + 包所有权 | 安装器有备份；没有按版本迁移状态 | 缺状态迁移与回滚契约 |

这张表说明：**ZYX 的强项是「判断该谁做」，弱项是「做完怎么证明、坏了怎么退」。** Omarchy 恰好把后两项做成了工程默认。

## 3. 四个可结合点（按新颖度 × 价值 × 成本排序）

### A. Context Card：让知识库「自己写一张技能卡」

**这是我认为最有创意、也最像第一性原理的一刀。**

现在的跨 agent 记忆有个根本矛盾：记忆存在某个宿主里，换个 agent 就失忆；写进系统提示又会膨胀、过期。Omarchy 给了一个启发：技能是宿主会自动读取的「能力声明」，那为什么不让**状态自己生成技能**？

做法：

- R7 的活动库状态（slug / root / topic / 最近日志）生成一张 8–12 行的 `SKILL.md`：
  - `name: zyx-<slug>-context`
  - `description:` 用户说「我的知识库 / 我库里 / 接着上次的库」时先用
  - 正文只写三件事：库在哪、先跑 `wiki.py brief --vault <slug>`、回答必须带页名、不许整库贴入。
- 安装到各宿主的 skills 目录；`wiki.py use` 切换活动库时重新生成；`--remove` 只删带 managed 标记的卡。
- Omarchy 的 `~/.agents/skills` 是共同落点，但要注意：它只把**自家**技能链进 Claude/Codex 等目录，用户技能不会自动分发。所以 ZYX 的安装器要像现在同步 `zyx/wiki-vault` 一样，把这张卡一起同步到四个宿主；Omarchy 负责让 `~/.agents/skills` 成为公共十字路口，不负责替你分发。

**为什么这是新东西**：技能不再是静态文档，而是**活状态的一个视图**。每建一个库，就自动多一个「懂这个库」的技能；换宿主、换模型、换会话，记忆都跟着走，而且不依赖任何云端 API。

**风险**：技能卡描述写不好会误触发；路径写死会过期；多库会互相抢触发。控制方式：一张卡只指向一个活动库，描述里带库的主题词，`doctor` 检查卡与注册表是否一致。

### B. Look Gate：先看后交，而不是先交后改

Omarchy 最值得抄的一个小动作是 `omarchy agent look theme`：它不把主题直接套到你的桌面，而是先画一张「桌面长什么样」的预览图，打印缺色、对比度不足、壁纸太小等问题；agent 看完再决定是否应用。

ZYX 的 `qa-audit.md` 是文本清单，能查「有没有脱敏、有没有来源」，但查不出「这页 PPT 标题压到图上了」「封面字在手机上糊了」「分镜顺序读不懂」。对内容生意来说，后者才是退货原因。

建议加一个 `zyx look` 验收原语：

- HTML → 无头 Chromium 截全页；
- PPTX → LibreOffice 转 PDF → 逐页 PNG → 拼 contact sheet；
- 视频/分镜 → ffmpeg 抽 4 帧拼图；
- 图片 → 统一尺寸拼图；
- agent 必须 `Read` 这张图，修完溢出/对比度/层级问题，才允许交付；`look.png` 进 `MANIFEST.md`。

这不是新路由，是给现有 R5/R6 和所有视觉产物加一道**看得见的质检门**。

### C. Skill Contract：把七类路由做成「能力包」

Omarchy 的每个命令都有元数据、测试、迁移；ZYX 的每个路由目前只有文档和边界。

可以给每类路由加一份 `contract.json`：

```json
{
  "route": "R7",
  "entry": "wiki.py",
  "state": "state/vaults.json",
  "acceptance": "wiki-selftest.py",
  "rollback": "wiki.py archive",
  "migration": "migrations/",
  "version": "1.4.0"
}
```

再加三个命令：`zyx verify <route>`（跑验收）、`zyx status --json`（机器读）、`zyx migrate`（状态迁移）。

这会把 ZYX 从「一堆提示词文件夹」变成「判断力的包管理器」。代价是 R1–R4 是外部技能，只能做适配层，不能强制它们改；所以这是 v2.0 级工程，不是一次迭代。

### D. Skin Bridge：主题即品牌

Omarchy 的主题就是一个 `colors.toml`，所有应用的颜色由它生成。ZYX 的 HTML/PPT/封面如果能读这份色板，就能让桌面、文档、视频字幕共用一套视觉身份。

```bash
python3 scripts/theme-palette.py --format css
# --accent #89b4fa --bg #1e1e2e --fg #cdd6f4 ...
```

有意思，但战略价值低于 A/B；适合作为「给内容创业者的彩蛋」，不适合当主线。

## 4. 不建议做的三件事

1. **不要加一个 R8「Omarchy 路由」。** 七类路由分的是「原料类型」，Omarchy 是「运行环境」；硬塞会把内容路由和系统操作混在一起。正确姿势是**握手，不是路由**：`doctor` 检测到 Omarchy 就报告版本/主题/默认 agent，需要时再由 agent 调 `omarchy` 技能。
2. **不要合并仓库、复制它的 7 个 skill。** 许可证、上游更新、系统路径都会打架；ZYX 只借模式，不借实现。
3. **不要自动写 `~/.agents/AGENTS.md`。** 那是用户的个人规则文件，不是 ZYX 的公告栏；要做也只做 opt-in 的 managed block，默认只写独立技能卡。

## 5. 如果只做一件事

**先做 A 的 `wiki.py context --install`。**

它满足三个条件：一周内能做完、不依赖 Omarchy 安装、直接解决「换个 agent 就忘了我的库」这个真问题。做完之后，每建一个库就自动多一个跨宿主技能；这是复利，不是一次性功能。

验收标准：

- 干净宿主上装完，Claude/Codex/OpenClaw/豆包四个入口都能看到 `zyx-<slug>-context`；
- 用户只说「我库里关于 X 有什么」，不报路径，agent 也会先跑 `brief`；
- 删库/换库后，旧卡不残留，新卡指向正确；
- `doctor` 能查出卡与注册表不一致。

## 6. 落地路线

| 版本 | 内容 | 风险 |
|---|---|---|
| v1.4 | Context Card + Look Gate + `omarchy-bridge status` 握手 | 低；不改七类路由 |
| v1.5 | 把 Look Gate 接入 R5/R6 交付门，补视觉验收用例 | 中；依赖渲染工具 |
| v2.0 | Skill Contract + `verify/status/migrate` | 高；涉及外部技能适配与状态迁移 |

## 7. 已落地（v1.4.0，2026-11-24）

按上面的建议，先落地了 A + B + 只读握手，没有新增 R8，也没有动七类路由：

| 落地项 | 实现 | 验收 |
|---|---|---|
| Context Card | `wiki.py context --install/--remove`；`use` 切换自动刷新托管卡；只覆盖 managed 卡 | R7 自测 41/41（含预览/安装/幂等/防覆盖/移除/换库刷新） |
| Look Gate | `scripts/look.py` 渲染 HTML/PPTX/PDF/视频/图片成 `look.png`，写 `look.json` + `MANIFEST.md`；`shared/quality/visual-acceptance.md` 规定必须亲自看图 | Look 自测 6/6；实测 HTML/PPTX/图片均出图 |
| Omarchy 握手 | `scripts/omarchy-bridge.py status` 只读报告版本/主题/默认 agent/共享目录/ZYX 状态；`--install-context` 一条命令装卡 | 用 fake Omarchy 目录验证版本/主题/agent 可读；未装时正常降级 |
| 医生检查 | `doctor.sh` 新增第 9/10/11 段：Look Gate、Omarchy 握手、Context Card | `doctor --full` 全绿 |

**仍留到后续**：Skill Contract（v2.0）、主题色板 Skin Bridge（彩蛋）、把 Look Gate 接进 R5/R6 的强制交付门（当前是共享质检清单里的必过项）。

## 8. 事实来源

- 仓库与版本：https://github.com/omacom/omarchy（`version` = `4.0.0.alpha`）
- Agent 与技能说明：`manual/17-ai.md`（7 个技能、共享 `~/.agents`、look、crash diagnosis）
- 技能链接实现：`bin/omarchy-agent-skills-link`
- 个人规则链接：`bin/omarchy-agent-instructions`
- 命令元数据：`bin/omarchy`、`bin/omarchy-theme-set` 头部注释
- 验收与迁移：`test/acceptance.d/`、`oligarchy-tests/`、`migrations/`
- 主题色板：`themes/*/colors.toml`
