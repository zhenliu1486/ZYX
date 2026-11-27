# 安装 ZYX

> 给 AI 的硬指令：不要再去 GitHub 搜“zyx skill”，也不要尝试把整个仓库当成一个 `SKILL.md` 安装。ZYX 是多技能包，按下面这一行执行。

## 一句话安装（推荐，完整安装）

```bash
curl -fsSL https://cdn.jsdelivr.net/gh/zhenliu1486/ZYX@main/bootstrap.sh | bash
```

如果 `cdn.jsdelivr.net` 访问不了，用 GitHub 原始地址：

```bash
curl -fsSL https://raw.githubusercontent.com/zhenliu1486/ZYX/main/bootstrap.sh | bash
```

这条命令会：

1. 把 ZYX 克隆到 `~/.zyx/src`；
2. 调仓库自带的 `scripts/install.sh --install-deps`；
3. 把 `zyx`、`video-studio`、R5 子技能、R6、R7 等内置技能复制到本机已存在的 Agent 宿主目录；
4. 安装女娲 / 大师 / 仓颉 / dbs / R8 等外部依赖；
5. 跑 `doctor.sh` 自检。

装完新开一个对话，直接说：

> 用 ZYX 帮我……

## 只装技能本体（已有外部依赖时）

```bash
curl -fsSL https://cdn.jsdelivr.net/gh/zhenliu1486/ZYX@main/bootstrap.sh | bash -s -- --no-deps
```

## 用 Skills CLI 安装（只支持 `SKILL.md` 的 Agent）

```bash
npx skills add zhenliu1486/ZYX --all -g -y
```

这条只复制 18 个技能，不会安装女娲 / 大师 / 仓颉 / dbs / R8。装完用 `bootstrap.sh` 或 `bash ~/.claude/skills/zyx/scripts/doctor.sh` 补齐外部依赖。

## 豆包工作 / 不能执行终端的 AI

豆包「我的技能」只接受带根级 `SKILL.md` 的单个技能包，不会自动发现 GitHub 仓库里的 `skills/zyx/SKILL.md`。所以：

1. 下载 [dist/doubao/zyx-installer.zip](https://github.com/zhenliu1486/ZYX/raw/main/dist/doubao/zyx-installer.zip)（或让发送者给你）；
2. 豆包 PC →「技能·连接器·伙伴」→「我的技能」→「上传技能」→ 拖入 zip；
3. 新开对话，说「帮我安装 zyx」。

这个 zip 是安装器，不是 ZYX 本体；它会读取包内的 `repo/` 离线安装 ZYX。若你的豆包不允许执行 shell，就只能在终端执行上面的一行命令，或让管理员把 ZYX 上架到企业技能库。

## 为什么以前“找不到”

- ZYX 是 18 个技能的多技能仓库，根目录没有 `SKILL.md`；
- 旧 README 只写了 `bash scripts/install.sh`，前提是已经 clone；
- 豆包技能安装器只认根级 `SKILL.md` 的单个技能包，不会递归找 `skills/`；
- GitHub 搜索 “zyx” 会撞上大量同名项目，仓库没有安装入口关键词。

现在用上面的 `bootstrap.sh` 或 Skills CLI，AI 不需要自己“找”，只要执行固定 URL。

## 卸载 / 重装

安装器会把旧版备份到 `~/.zyx-backups/`，不会直接删除。重跑同一条命令即可覆盖更新。
