---
name: zyx-installer
description: 安装 ZYX 调度台（zhenliu1486/ZYX）多技能包。当用户说「帮我安装 zyx 这个 skill」「安装 ZYX」「部署 zyx 到本地」「把 zyx 装进豆包 / Claude Code / Codex」时使用。这是安装器，不是 ZYX 本体；它会取仓库并安装 19 个技能（18 个内置技能 + R0 Pinky 手机操作）。
license: MIT
metadata:
  author: "ZYX"
  version: "1.9.0"
  repository: "https://github.com/zhenliu1486/ZYX"
  install_command: "curl -fsSL https://raw.githubusercontent.com/zhenliu1486/ZYX/main/bootstrap.sh | bash"
allowed-tools: Bash, Read, WebFetch
---

# ZYX Installer · 一句话安装入口

ZYX 不是单个技能，而是 **19 个技能的多技能包**：1 个路由薄壳 `zyx` + R5 影视制作 10 个技能（聚合层 + 9 个子技能）+ R6 迭代器 + R7 知识库 + R8 投资决策 5 个技能 + R0 Pinky 手机操作。根目录这个 `SKILL.md` 只是安装入口，不是 ZYX 本体。

## 先判断：当前有没有仓库

### 情况 A：当前目录已经有 `bootstrap.sh` 和 `skills/`

说明仓库已经拿到（用户 clone 了仓库，或这是豆包离线包里的 `repo/`）。直接运行：

```bash
bash bootstrap.sh
```

默认会安装内置技能并安装外部依赖（女娲 / 大师 / 仓颉 / dbs / 达尔文）。如果用户只想装本体：

```bash
bash bootstrap.sh --no-deps
```

指定宿主目录：

```bash
bash bootstrap.sh --dir ~/.claude/skills
```

### 情况 B：只有这个 `SKILL.md`，没有仓库

先把仓库取到本机缓存，再运行：

```bash
git clone --depth 1 https://github.com/zhenliu1486/ZYX.git "$HOME/.zyx/src"
bash "$HOME/.zyx/src/bootstrap.sh"
```

只想装本体：

```bash
bash "$HOME/.zyx/src/bootstrap.sh" --no-deps
```

### 情况 C：当前宿主不能执行 Bash

不要假装安装成功。告诉用户：

- 有终端：复制这一行执行：
  ```bash
  curl -fsSL https://raw.githubusercontent.com/zhenliu1486/ZYX/main/bootstrap.sh | bash
  ```
- 豆包工作 / 不能执行终端的桌面端：先下载 `zyx-installer.zip`，在「技能 · 连接器 · 伙伴 → 我的技能 → 上传技能」上传，再对新对话说「帮我安装 zyx」。
- 只能浏览网页的 Agent：把 `INSTALL.md` 和 `llms.txt` 的内容读完，按里面的命令交给用户执行；不要编造一个“已经装好”的结果。

## 安装后必须验证

`bootstrap.sh` 最后会跑 `doctor.sh`。只有看到“就绪 / 全部就绪”才能说安装完成；如果出现缺失项，原样报告缺什么、补什么，不要用“应该可以了”代替。

需要复跑自检时，在安装目标目录执行：

```bash
bash zyx/scripts/doctor.sh --full
```

常见安装目标：`~/.agents/skills/zyx`、`~/.claude/skills/zyx`、`~/.doubao/agent_mode/workspace/.user_skills/zyx`。不确定时先运行：

```bash
bash "$HOME/.zyx/src/skills/zyx/scripts/doctor.sh" --full
```

## 安装后怎么用

- 新开一个对话，直接说「用 ZYX 帮我……」或输入 `/zyx`。
- 路由表：R1 人 / R2 行业 / R3 长内容 / R4 当下问题 / R5 影视制作 / R6 产物迭代 / R7 知识库 / R8 投资决策；R0 是手机操作（Pinky，可选）。
- R0 需要另装 Pinky 桌面端、连接手机并在宿主接入 `pinky` MCP；只装技能不会自动获得手机控制。步骤见安装后的 `pinky/SETUP.md`。

## 边界

- 不要把这 19 个技能逐个复制；`bootstrap.sh` 会按 `skills/zyx/deps/manifest.json` 统一处理。
- 不要在用户没有授权时 push、打 tag、发 Release；安装只需要本地写。
- 不要声称“豆包聊天里一句话就能自动从 GitHub 安装所有用户”。豆包官方自定义技能走「上传根级 `SKILL.md` 的包/文件夹」；公开上架需企业资质与平台审核。这个根级 `SKILL.md` 是为了让支持根级技能的宿主/上传器能找到入口，不改变豆包的审核规则。
