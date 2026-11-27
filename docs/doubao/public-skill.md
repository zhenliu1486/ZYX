---
name: zyx-installer
description: 安装 ZYX 调度台（19 个 Agent Skills 的多技能包）。当用户说「帮我安装 zyx 这个 skill」「安装 ZYX 调度台」「部署 zyx」「装一下 zyx」时使用。这是安装器，不是 ZYX 本体；它会从 GitHub 取仓库并运行 bootstrap.sh，安装路由、影视制作、产物迭代、知识库、A 股投资决策与 Pinky 手机操作技能。
license: MIT
metadata:
  author: "ZYX"
  version: "1.9.0"
  repository: "https://github.com/zhenliu1486/ZYX"
  icon: "icon.png"
  install_command: "curl -fsSL https://cdn.jsdelivr.net/gh/zhenliu1486/ZYX@main/bootstrap.sh | bash"
allowed-tools: Bash, Read, WebFetch
---

# ZYX 安装器

ZYX 是 **19 个技能的多技能包**，不是单个技能：

- 1 个路由薄壳 `zyx`；
- R5 影视制作聚合层 + 9 个子技能；
- R6 产物迭代；
- R7 长期知识库；
- R8 A 股四维投资决策 + 4 个子技能；
- R0 Pinky 手机操作（技能指南；真正用手机还需 Pinky App + MCP）。

## 执行

1. 先看当前目录有没有 `bootstrap.sh` 和 `skills/`。
2. 有则直接执行：

```bash
bash bootstrap.sh
```

3. 没有则取仓库后执行：

```bash
git clone --depth 1 https://github.com/zhenliu1486/ZYX.git "$HOME/.zyx/src"
bash "$HOME/.zyx/src/bootstrap.sh"
```

4. 只装本体、不装外部依赖：

```bash
bash bootstrap.sh --no-deps
```

5. 安装后必须跑自检；`bootstrap.sh` 会自动跑一次。看到“就绪 / 全部就绪”才能说安装完成：

```bash
bash zyx/scripts/doctor.sh --full
```

## 安装后

- 新开对话，说「用 ZYX 帮我……」或 `/zyx`。
- R0 手机操作需要另装 Pinky 桌面端、连接手机并接入 `pinky` MCP；只装技能不会自动获得手机控制。见安装后的 `pinky/SETUP.md`。

## 边界

- 不要把 19 个技能逐个复制；`bootstrap.sh` 按 `deps/manifest.json` 统一处理。
- 不要在用户未授权时 push、打 tag、发 Release。
- 不要声称“所有豆包用户只发一句话就能自动从 GitHub 装好”。豆包公开市场需要企业资质与平台审核；这个技能是安装器，不替代审核。
- 如果当前宿主不能执行 Bash 或访问 GitHub，明确说明“安装未完成”，给用户终端命令或离线包，不要编造成功。
