# 安装 ZYX

ZYX 是 **19 个技能的多技能包**，不是单个 `SKILL.md`。仓库根目录的 `SKILL.md`（`name: zyx-installer`）只是安装入口；真正技能在 `skills/` 下。

## 一句话安装（推荐，完整安装）

```bash
curl -fsSL https://cdn.jsdelivr.net/gh/zhenliu1486/ZYX@main/bootstrap.sh | bash
```

GitHub 原始地址备用：

```bash
curl -fsSL https://raw.githubusercontent.com/zhenliu1486/ZYX/main/bootstrap.sh | bash
```

这条命令会：

1. 把 ZYX 克隆到 `~/.zyx/src`；
2. 调仓库自带的 `scripts/install.sh --install-deps`；
3. 把 `zyx`、`pinky`、`video-studio`、R5 子技能、R6、R7、R8 等内置技能复制到本机已存在的 Agent 宿主目录；
4. 安装女娲 / 大师 / 仓颉 / dbs / 达尔文 等外部依赖；
5. 跑 `doctor.sh` 自检。

装完新开一个对话，直接说：

> 用 ZYX 帮我……

## 只装技能本体（已有外部依赖时）

```bash
curl -fsSL https://cdn.jsdelivr.net/gh/zhenliu1486/ZYX@main/bootstrap.sh | bash -s -- --no-deps
```

## 已经 clone 了仓库

```bash
bash bootstrap.sh            # 完整安装
bash bootstrap.sh --no-deps  # 只装内置
bash bootstrap.sh --dir ~/.claude/skills
```

## 用 Skills CLI / 根级 SKILL 安装

```bash
npx skills add zhenliu1486/ZYX -g -y
```

不同 Skills CLI 版本对多技能仓库的识别不一样：有的只装根级 `zyx-installer`，有的能递归 `skills/`。**无论它装了什么，最后都建议再跑一次 `bootstrap.sh`**，确保 19 个技能与外部依赖完整。

支持根级 `SKILL.md` 的宿主/上传器会看到 `zyx-installer`，它会在安装后取仓库并运行 `bootstrap.sh`。这提高了“AI 自己找到入口”的概率，但它不是豆包公开市场的替代品。

## 豆包工作 / 不能执行终端的 AI

### 路径 A：上传安装器（一次上传，之后一句话）

豆包「我的技能」只接受带根级 `SKILL.md` 的单个技能包，不会自动发现 GitHub 仓库里的 `skills/zyx/SKILL.md`。所以：

1. 下载 `ZYX-豆包安装器-v1.9.0.zip`（Release asset，或仓库 `dist/doubao/zyx-installer.zip`）；
2. 豆包 PC →「技能 · 连接器 · 伙伴」→「我的技能」→「上传技能」→ 拖入 zip；
3. 新开对话，说「帮我安装 zyx」。

这个 zip 是安装器，不是 ZYX 本体；它会读取包内的 `repo/` 离线安装 19 个技能。若豆包不允许执行 shell，就只能在有终端的环境跑上面的一行命令，或让管理员把 ZYX 上架到企业技能库。

### 路径 B：公开上架（所有豆包用户可见）

豆包开放平台「公开上架」需要：

- 企业资质认证；
- ZIP ≤ 16 MB、≤1024 条目、单文件 ≤2 MB；
- 平台运营审核，通常 3 个工作日；
- 上架后出现在「豆包推荐」，用户搜到后一键安装。

材料与包见 [docs/doubao/public-listing.md](docs/doubao/public-listing.md)，打包命令：

```bash
bash scripts/package-doubao-public.sh
```

**这不是“聊天里自动搜 GitHub”**，而是商店安装。公开上架需要企业账号提交，ZYX 仓库本身不能替用户完成审核。

### 路径 C：本地技能自动读取

用户先在有终端的环境跑一行安装，ZYX 落到本地 `agents.skill` / `~/.claude/skills` 等目录；豆包桌面端会自动读取本地技能。之后在豆包里可以直接调用 ZYX，但“安装”这一步仍然是终端命令，不是聊天一句话。

> 云电脑和本地电脑的技能列表不共用：本地装了，云电脑还要再装一次。

## 为什么以前“找不到”

- ZYX 是 19 个技能的多技能仓库，旧版根目录没有 `SKILL.md`；
- 旧 README 只写了 `bash scripts/install.sh`，前提是已经 clone；
- 豆包技能安装器只认根级 `SKILL.md` 的单个技能包，不会递归找 `skills/`；
- GitHub 搜索 “zyx” 会撞上大量同名项目，仓库没有安装入口关键词。

现在根目录有 `zyx-installer` 安装器，同时保留 `bootstrap.sh` / `llms.txt` / `INSTALL.md` 三个固定入口；AI 不需要自己“找”，按固定 URL 执行即可。

## Pinky（R0 手机操作）

`pinky` 技能随仓库内置，但它只是 Agent 指南；真正操控手机还需要：

- 安装 Pinky 桌面端（macOS / Windows / Linux）；
- 连接 iPhone / Android；
- 在宿主接入 `pinkyctl mcp` 或 HTTP MCP。

步骤见 [skills/pinky/SETUP.md](skills/pinky/SETUP.md)。没有 MCP 工具时，ZYX 只输出安装指引，不会假装已经操控手机。

## 卸载 / 重装

安装器会把旧版备份到 `~/.zyx-backups/`，不会直接删除。重跑同一条命令即可覆盖更新。

## 安全边界

- 不在用户未授权时 push、打 tag、发 Release；安装只写本地。
- 不把密钥、手机屏幕、验证码、账号、金额、聊天内容写进仓库或公开 issue。
- Pinky 的付款/下单/发送/删除等动作由手机端人工批准；Agent 不能代批。
