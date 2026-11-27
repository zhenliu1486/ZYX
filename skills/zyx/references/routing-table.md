# 路由判定表

## 1. 八类原料判定信号

| 目标 | 原料类型 | 典型信号（原话/素材） | 产物形态 | 边界（不要误分流） |
|---|---|---|---|---|
| **R1 女娲** `nuwa-skill` | 一个人 | 「乔布斯怎么想」「芒格的思维方式」「蒸馏 XX」「做个 XX 视角」「学他的决策习惯」；素材是某人的著作、访谈、演讲、聊天记录 | 人物视角 Skill（心智模型 / 招式 / 启发式 / 声音 / 边界） | 不做行业打法、不做书里的通用方法论；作者人设扮演归这里，不归仓颉 |
| **R2 大师** `master-skill` | 一个细分行业 | 「我是做跨境电商的」「帮我蒸一个 AI 基础设施大师」「让 agent 变成 X 行资深人」；原料是行业资料、岗位实践、工具栈 | 行业 Master Skill（镜片 / playbook / 表达 DNA / 质量基准 / 反模式 / 时效层），含人物 sub-skill | 粒度是细分领域，不覆盖泛行业；不做单一人物复刻 |
| **R3 仓颉** `cangjie-skill` | 长内容 | 「拆《穷查理宝典》」「把这个 B 站视频/播客/课程/访谈做成 skill」；原料是书、长视频转写、播客文字稿、课程稿、长文 | 原子能力卡 + 编译 Skill 包（single / pack） | 不做书摘、读后感、作者角色扮演；纯观点/评论类内容不蒸馏 |
| **R4 dbs 家族** | 当下问题 | 「我这门生意行不行」「这篇文案哪里不抓人」「帮我把这事写成决策记录」「派给员工跟进」；无新 Skill 产出诉求 | 诊断报告 / 成稿 / 决策记录 / 派单结果 | 不把当下问题沉淀成可安装 Skill；要沉淀走 R1/R2/R3 |
| **R5 内容生产** | 影视/短剧/漫剧制作 | 「构思这个故事」「写竖屏短剧剧本」「做角色/场景设定」「这场戏怎么拍」「设计机位/运镜/构图」「设计打斗分镜」「控人物表情视频」「排从剧本到成片的流程」 | 剧本/设定/导演机位方案/分镜/参数/流程方案 | 电商带货编导不归这里；投资决策走 R8；内部再由 video-studio 聚合层路由到对应子技能；剧本/情绪→机位方案以 director-camera-composition 为主导演层 |
| **R6 产物迭代** | 已有产物二次打磨 | 「这份 skill/报告/文档再改改」「按我的反馈迭代这版」「这版哪里没打中、怎么改」 | 迭代后的产物 + 反馈规则记录 | 不是从零蒸馏/生产；指向 F2R 负反馈迭代，必要时联动 resonate / ai-check 打磨 |
| **R7 知识库** `wiki-vault` | 长期知识库（个人/领域 Wiki） | 「建一个关于 X 的知识库」「把这篇/这本书加进我的 X 库」「我库里关于 X 都有什么结论」「体检一下我的库」；原料是持续要往里喂的文章/论文/转写/数据 | 持续累积的 Obsidian Markdown 知识库（摘要/实体/概念/对比/综述页 + 索引/日志/热缓存） | 只要一次性拆成 Skill 包走 R3；人物/行业深挖走 R1/R2；眼下判断走 R4；不从零生产影视内容 |

### 信号冲突时的裁决
- 既像「人」又像「行业」：看产物诉求——要「像他一样想」走 R1；要「懂这行怎么做」走 R2。
- 既像「书」又像「人」：书里讲的通用方法走 R3；书作者本人的思维与决策走 R1。
- 既像「生产」又像「蒸馏」：要从零做一个新片子/新脚本走 R5；要把已有材料提炼成可复用方法包走 R3。
- 既像「长内容」又像「知识库」：要一次性蒸馏成可安装 Skill 包走 R3；要长期累积、反复摄入、库内检索走 R7。
- 既像「当下问题」又像「知识库」：只要眼下判断、不要求进长期库走 R4；要落进持久库并可回溯链接走 R7。
- 既像「产物迭代」又像「知识库」：改已有库内页面、反馈要沉淀成规则时，先走 R6 显性化规则，再回写 R7。
- 既像「当下问题」又像「投资」：具体到某只票/某个组合的买卖、仓位、止损走 R8；只谈生意经营层面走 R4。
- 完全模糊、看不出原料类型：先问一个问题——「你想得到的是：一个人的视角 / 一整行的打法 / 一份可复用方法包 / 眼下这件事的判断 / 一段可生产的内容 / 还是把已有产物再改一版？」再分流。

| **R8 投资决策** `ashare-four-dim-decision` | 投资 / 股票 / 波段 | 「现在能买吗」「帮我看看这只票」「我想做波段」「超短线怎么打」「仓位怎么分」「什么时候卖」「该不该割」；原料是行情、持仓、资金量、交易周期 | 四维打分 + 动态权重 + 风控闸门 → 候选标的表（买点/止损/目标/仓位）+ 精确到日期与时段执行表 + 复盘回填表 | 不做代下单、不承诺收益；纯宏观闲聊不走 R8；泛商业诊断走 R4；从零生产内容走 R5 |

## 2. 衔接关系（已在蒸馏器内部实现，入口写清路径即可）

- **大师 → 女娲**：R2 大师在 Phase 3 生成 top3 行业人物 sub-skill 时，委派给 R1 女娲流水线。衔接时把女娲安装目录作为 R1 路径传入，不在大师目录里复制女娲文件。
- **仓颉 → 素材前置转写**：R3 仓颉要求先有文字稿/字幕转写。**无文字稿时先走转写链路**：平台视频/播客先用 `dbs-video-extract` 提取语音文字稿；本地音视频走本地转写；拿到文字稿后再进仓颉 RIA-TV++ 流水线。
- **仓颉 → 达尔文**：R3 仓颉阶段 4 的压力测试兼容达尔文评测协议；压测用例口径见 `../shared/darwin/`，达尔文本体作为第 3 层底座引用，不内嵌进仓颉。
- **内容生产 → video-studio**：R5 先到 `video-studio` 聚合入口，由其内部路由到剧本/编剧/人物/场景/导演运镜/镜头语言/动作/表情/提示词/全流程对应子技能。
- **内容生产 → 导演层与镜头层**：剧本/情绪→机位方案先走 `director-camera-composition`；标准景别/机位/焦段/运镜/转场/镜头清单走 `ai-camera-shots` 做词典与兜底；动作戏仍由 `cinematic-fight-direction` 主控；`cinematic-video-prompt` 只在需要补光照/色彩/材质词汇时可选接入。
- **产物迭代 → F2R**：R6 已有产物二次修改迭代，指向 `f2r-feedback-iteration`（负反馈迭代：把人的判断显性化为规则、小样本迭代 + 回归测试）；需要诊断稿件共鸣断点时联动 `dbs-resonate`，需要查 AI 味/机器化表达时联动 `dbs-ai-check`。
- **知识库 → 晋级/深挖/改版**：R7 库内沉淀出独立复用价值（过三重验证 + 具备独立复用价值）才委派 R3 打包成 Skill；人物/行业深挖交 R1/R2，wiki 只留摘要与 wikilink；页面按反馈改版联动 R6。
- **投资决策 → 四维子技能**：R8 先进 `ashare-four-dim-decision` 总控，由其按需读取四个子技能 SKILL.md（情绪 `ashare-sentiment-cycle`、风口 `ashare-theme-wind`、资金 `ashare-capital-flow`、技术 `ashare-technical-structure`）打分后统一加权；`../../ashare-four-dim-decision/scripts/score.py` 做确定性计算，不手算。
- **投资决策 → 产物**：方案按 `../references/artifact-layout.md` 落盘到 `ashare-four-dim-decision/<日期>-<标的或组合>/`，含四维打分表、执行时间表、复盘回填表。
- **dbs 内部路由**：R4 先到 dbs 主调度台（`dbs`），由它按问题类型分发到具体 dbs 子 skill；zyx 不直接挑 dbs 子项。

## 3. 路径解析

对每个蒸馏器，按以下顺序解析本机绝对路径，找到第一个存在 `SKILL.md` 的目录：

1. 环境变量（若设置）：`$NUWA_SKILL_DIR`、`$MASTER_SKILL_DIR`、`$CANGJIE_SKILL_DIR`、`$DBS_SKILL_DIR`。
2. zyx 所在的同级 skills 目录（安装器把内置兄弟技能复制在 zyx 旁边）。
3. 本机宿主 skill 目录依次探测：
   - `~/.claude/skills/<repo>`
   - `~/.openclaw/skills/<repo>`
   - `~/.agents/skills/<repo>`
   - Doubao 用户技能目录 `~/.doubao/agent_mode/workspace/.user_skills/<repo>`
4. 都不存在：报错说明「未检测到 <repo>，请先安装」，并给出上游仓库地址；不要凭空假设路径。

> 下表是摘要；依赖的来源类型、安装命令、必需/可选与子技能归属，权威清单在 `../deps/manifest.json`。

| 代号 | 目录名 | 上游仓库 / 来源 |
|---|---|---|
| R1 | `nuwa-skill` | https://github.com/alchaincyf/nuwa-skill（git，必需） |
| R2 | `master-skill` | https://github.com/swaylq/master-skill（git，必需） |
| R3 | `cangjie-skill` | https://github.com/kangarooking/cangjie-skill（git，必需） |
| R4 | `dbs-*`（主目录 `dbs`） | https://github.com/dontbesilent2025/dbskill（npx，必需） |
| R5 | `video-studio`（聚合层） | 随仓库内置；9 个子技能随仓库内置，见 video-studio/SKILL.md |
| R6 | `f2r-feedback-iteration` | 随仓库内置 |
| R7 | `wiki-vault` | 随仓库内置 |
| R8 | `ashare-four-dim-decision`（+4 子技能） | 随仓库内置 |
| 可选 | `darwin-skill` | https://github.com/alchaincyf/darwin-skill（git，可选压测底座） |

## 4. 发布与远端动作边界

建远端仓库、push、打 tag、发 Release、公开测试材料，都需要用户在当轮明确授权；未授权时只做本地准备与校验。发布前先按 `../shared/quality/qa-audit.md` 脱敏：不提交密钥、内部路径、本机配置、未脱敏的私密样本与运行记录。

## 5. 环境层例外（Omarchy）

Omarchy / Hyprland / 桌面主题 / 快捷键等请求不是「原料类型」，**不进 R1–R7**：先跑 `../scripts/omarchy-bridge.py status` 做只读握手，再交给 Omarchy 自带的 `omarchy` skill 执行。ZYX 不改 `/usr/share/omarchy`、不自动写 `~/.agents/AGENTS.md`、不新增 R8。
