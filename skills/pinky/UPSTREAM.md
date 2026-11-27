# Pinky 上游记录

- 上游仓库：<https://github.com/DIYgod/pinky>
- License：Apache-2.0（见同目录 `LICENSE`）
- 引入文件：上游 `docs/SKILL.md`，仅补充 `license`、`metadata` 与中文触发词，正文保持原样。
- 引入版本：`2026.1127.5`
- 引入 commit：`6933257372e354ee32ceaae8f83049f5759a5015`
- 同步方式：`git -C pinky fetch && git checkout <tag>` 后重新复制 `docs/SKILL.md`；不要手改正文。
- 注意：Pinky App 在 Settings › Agents 连接 Agent 时会安装并维护自己的 `pinky/SKILL.md`；如果 App 已安装更新版本，以 App 的副本为准，本目录副本只用于 ZYX 开箱携带与离线阅读。
- Pinky 是桌面 App + MCP server，不是单文件技能；完整安装步骤见 `SETUP.md`。
