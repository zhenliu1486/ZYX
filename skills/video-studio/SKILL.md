---
name: video-studio
description: 影视/短剧/漫剧制作聚合入口。内部路由剧本开发、竖屏短剧编剧、人物设定、场景设定、导演运镜/机位/构图、镜头语言/分镜/转场、动作打斗分镜、提示词词汇增强、微表情参数、全流程 SOP。当用户要构思故事、写短剧剧本、做角色/场景、设计镜头或分镜、这场戏怎么拍、修 AI 视频 prompt、控表情、或规划从剧本到成片的生产流程时使用。
license: MIT
compatibility: 兼容 Agent Skills 标准宿主；子技能需与本入口同机安装。
metadata:
  author: "ZYX"
  version: "1.1.0"
  layer: "2-aggregator"
  schema: "agentskills.io"
allowed-tools: Read, Write, Edit, Bash, WebSearch, WebFetch
---

# video-studio · 影视制作聚合入口（第 2 层）

> 本 skill 是影视/短剧/漫剧内容生产的**内部路由聚合层**：接到指令后先判断处于制作链路的哪一环，再委派给对应子技能执行；不重复实现各子技能的方法论。子技能保持独立，各自维护。

## 1. 内部路由表

| 制作环节 | 判定信号 | 委派子技能 | 子技能目录名 |
|---|---|---|---|
| **故事/剧本开发** | 从零构思故事、搭剧本框架、人物弧光、三幕结构、节拍表、判断点子成不成立 | screenplay-development | `screenplay-development` |
| **竖屏短剧编剧** | 写女频甜宠/虐恋/逆袭、男频兵王/赘婿/修仙剧本，开头钩子、反转节奏、每集留悬念 | short-drama-screenwriter | `short-drama-screenwriter` |
| **人物设定** | 角色外貌、服装配饰、男女主/反派/群像设定，批量人物提示词，保持角色一致性 | manju-character-library | `manju-character-library` |
| **场景设定** | 故事背景、环境设定、分镜场景图，不同时间/天气/氛围场景批量生产 | manju-scene-library | `manju-scene-library` |
| **导演运镜/机位/构图** | 剧本/情绪 → 机位方案；这场戏怎么拍、机位怎么设计、为什么平、帮我改机位；12 情绪处方、8 beat 配镜、正反打、180°、竖屏 9:16、分镜表 | director-camera-composition | `director-camera-composition` |
| **镜头语言/分镜/转场** | 景别、机位、焦段、运镜、镜头清单、故事板、隐藏剪辑、甩镜、匹配剪辑、动作切、首尾帧衔接、对话正反打 | ai-camera-shots | `ai-camera-shots` |
| **提示词词汇/修 prompt（可选）** | 补光照/构图/镜头/色彩/情绪/材质/天气词汇，修「太平、太 AI、太泛」的 prompt，按模型避坑 | cinematic-video-prompt | `cinematic-video-prompt` |
| **动作/打斗戏** | 武侠对决、现代格斗、枪战、追逐戏的分镜镜头与 AI 生成提示词 | cinematic-fight-direction | `cinematic-fight-direction` |
| **微表情/表情视频** | 真实自然的面部表情视频、情绪变化控制、眼神/嘴角/呼吸/眨眼参数 | micro-expression-video | `micro-expression-video` |
| **全流程生产 SOP** | 规划一部漫剧/短剧从剧本拆分、分镜表、提示词批量生成、图片/视频生成、配音配乐到剪辑合成 | manju-production-pipeline | `manju-production-pipeline` |

## 2. 路由裁决

- **一句话能判断环节**：直接委派对应子技能。
- **跨环节任务**（如「从点子到成片」）：先走 screenplay-development / short-drama-screenwriter 定剧本，再按 manju-production-pipeline 全流程 SOP 串联人物、场景、导演、动作、表情各环节。
- **信号模糊**：先问清当前处在「写剧本 / 做设定 / 出分镜 / 控表情 / 排全流程」哪一步，再分流，不猜。
- **剧本/情绪 → 机位方案**：以 `director-camera-composition` 为主导演层。它先逼出这场戏的一句话，拆 beat，按 12 情绪处方和 8 beat 配比给出机位/运镜/构图/分镜表；需要补标准镜头语法或转场词时，再联动 `ai-camera-shots`。
- **纯镜头语法/分镜/转场/镜头清单**：走 `ai-camera-shots`；如果同时要补光照/色彩/材质词汇，再接 `cinematic-video-prompt`。
- **已有提示词诊断/重写**：先走 `director-camera-composition` 的四查与机位改写；需要补词汇时再接 `cinematic-video-prompt`。
- **动作/打斗/枪战/追逐**：以 `cinematic-fight-direction` 为主，招式、节奏、动作模板都由它定；需要通用景别/运镜/转场补充时，再联动 `ai-camera-shots`，不让通用镜头层抢走动作戏主控。

## 3. 导演层与镜头层的分工（重点）

`director-camera-composition`、`ai-camera-shots`、`cinematic-video-prompt` 有重叠，但不是同一层，不能各出一份分镜：

1. **先导演判断**：由 `director-camera-composition` 回答“这一场要让观众感觉到什么”，拆 beat，定情绪曲线，再落到机位/运镜/构图/分镜表。它管叙事意图与镜头选择。
2. **再查镜头语法**：由 `ai-camera-shots` 提供五决策（景别 / 高度与倾角 / 朝向 / 镜头与焦点 / 运镜）和镜头之间的 join（硬切、动作切、隐藏剪辑、首尾帧桥接），作为导演层的词典与兜底。它不重新决定这场戏的情绪。
3. **再补提示词词汇**：由 `cinematic-video-prompt` 给同一组分镜补光照、构图、镜头、色彩、情绪、材质、天气，或修复「太平/太 AI」的 prompt。它不重新定分镜，只做词汇增强。
4. **动作戏插队**：动作/打斗的招式与节奏仍由 `cinematic-fight-direction` 负责；导演层与镜头层只负责它的镜头语言与转场衔接。
5. **外部包缺失**：`cinematic-video-prompt` 没装时，直接用 `director-camera-composition` + `ai-camera-shots` 完成镜头与 prompt，不阻断；在结果里注明「未装词汇包，未做深度词汇增强」。

输出约定：最终 prompt 用英文（模型可读），解释用中文；调用 `cinematic-video-prompt` 时忽略它默认的越南语说明，不要把越南语直接交给用户。

## 4. 子技能路径解析

解析顺序：环境变量覆盖 → 本聚合层同级 skills 目录（安装器把内置子技能复制在旁边）→ 本机宿主目录探测（`~/.claude/skills`、`~/.openclaw/skills`、`~/.agents/skills`、`~/.doubao/agent_mode/workspace/.user_skills`）→ 报错提示安装。禁止把各子技能方法论复制进本聚合目录。上述 9 个子技能随 ZYX 仓库内置，安装器自动复制；`cinematic-video-prompt` 是可选外部词汇包，用 `install.sh --install-deps` 或单独 clone；依赖归属以 `../zyx/deps/manifest.json` 为准。

## 5. 边界

- 不产出电商带货编导方案（归 ecommerce-director）；不做投资决策类任务。
- 不替代子技能内部的具体方法论与模板；本层只做环节判定与委派衔接。
- 产物目录与命名遵循 zyx 共享产物规范（`../zyx/shared/artifacts/convention.md`，若可解析到）。
- `director-camera-composition` 是中文导演层，框架重组自 `joost/ai-camera-shots` 与 `Rylaispirit/cinematic-video-prompt-skill`（均 MIT）；同步时保留其 `LICENSE` 与 `UPSTREAM.md`。
- `ai-camera-shots` 是 MIT 上游，已内置并在 `UPSTREAM.md` 记录 commit；同步时保留其 `SKILL.md` 主体，不把它的 references 复制进 `video-studio`。
- `cinematic-video-prompt` 是 MIT 可选外部包，内容含越南语解释；ZYX 只用它的英文词汇与模型避坑经验，不把它整包复制进仓库。
