# 渠道执行跟踪清单

> 状态：✅ 已完成 ｜ 🟡 待登录提交 ｜ ⏳ 达标后再做 ｜ 📝 成稿已备

## 一、已自动完成（本机已执行）

- [x] ✅ GitHub 仓库描述更新（含定位与关键词）
- [x] ✅ GitHub topics：agent-skills / claude-code / skill-router / agent-router / workflow-orchestration / content-production / ai-agents / skills-sh / openagent-skills / video-production / skill-dispatcher
- [x] ✅ README GEO 重构：实体定义、适用宿主、快速安装、关键词、对比表、FAQ
- [x] ✅ skills.sh 索引申请 issue：https://github.com/vercel-labs/skills/issues/2833
- [x] ✅ 安装链路验证：`npx skills add zhenliu1486/ZYX` 识别 10 个 skill
- [x] ✅ 宣传素材包与各平台成稿（见 `docs/promo/`）

## 二、待登录提交（需在 Web 端操作）

- [ ] 🟡 **LobeHub**：创作者页 → Submit Repository → 选 `zhenliu1486/ZYX`；类型 Skill，用途填「路由调度 + 影视生产聚合」
- [ ] 🟡 **Anthropic Claude 目录门户**：付费计划可用时提交 plugin bundle，过自动校验与安全扫描后发布
- [ ] 🟡 **skillmd.ai / eliteai.tools / skywork.ai**：按各站收录表单提交，口径用 `marketing-kit.md` 第 1 节
- [ ] 🟡 **ClawdHub**：OpenClaw 生态注册表，用 clawhub CLI 或对应表单提交

## 三、达标后再做（有门槛，提前备好条目）

- [ ] ⏳ **awesome-agent-skills 类榜单 PR**：门槛示例 ≥20 star 且满 14 天（以各榜 CONTRIBUTING 为准）；条目模板见 `marketing-kit.md` 第 5 节
- [ ] ⏳ **skills.sh 排行榜**：靠真实安装量自然上榜，先靠内容外链带来首批安装

## 四、内容平台发布（成稿已备，粘贴即可）

- [ ] 📝 掘金 / 知乎 / 思否技术长文：`article-technical.md`
- [ ] 📝 小红书图文笔记：`xiaohongshu-note.md`
- [ ] 📝 抖音 / 视频号口播：`short-video-script.md`
- [ ] 📝 朋友圈 / 社群短帖：用 `marketing-kit.md` 第 2 节三句话 + 安装命令

## 五、复查节奏

- 提交 skills.sh issue 后，隔几天回查是否被收录、是否出现在 `https://skills.sh/zhenliu1486/ZYX`。
- 仓库满 14 天、star 到 20 后，再提 awesome 榜单 PR。
- 每发一篇内容，回链仓库地址；观察安装量与 star 变化，再决定下一轮渠道。
- 结构性改进（择机）：Anthropic 平台挂载仓库时只扫描根目录 `.claude/skills/`；当前规范目录为 `skills/`，后续可在仓库加一层 `.claude/skills/` 镜像（软链或安装期拷贝），不复制内容、避免双份漂移，以提升 Claude 侧挂载发现率。

## 六、合规红线

- 不刷星、不刷安装量、不夸大未实现的能力。
- 公开材料不含密钥、内部路径、未脱敏样本。
- 上游蒸馏器保留原始归属；外部依赖按清单安装，不写成「全部内置」。
