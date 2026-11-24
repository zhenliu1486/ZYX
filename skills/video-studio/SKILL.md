---
name: video-studio
description: 影视/短剧/漫剧制作聚合入口。接到影视制作指令时，先在内部路由到对应子技能：剧本开发与结构、竖屏短剧编剧套路、人物设定库、场景库、打斗/动作戏分镜、微表情视频参数、从剧本到成片的全流程 SOP。当用户要构思故事/搭剧本框架、写竖屏短剧剧本与钩子反转、做角色/场景设定、设计动作打斗分镜、控制人物表情视频、或规划一部漫剧/短剧的完整生产流程时使用。仅覆盖内容生产侧，不负责电商带货编导（见 ecommerce-director）与 A 股类任务。
license: MIT
compatibility: 兼容 Agent Skills 标准宿主；子技能需与本入口同机安装。
metadata:
  author: "ZYX"
  version: "1.0.0"
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
| **动作/打斗戏** | 武侠对决、现代格斗、枪战、追逐戏的分镜镜头与 AI 生成提示词 | cinematic-fight-direction | `cinematic-fight-direction` |
| **微表情/表情视频** | 真实自然的面部表情视频、情绪变化控制、眼神/嘴角/呼吸/眨眼参数 | micro-expression-video | `micro-expression-video` |
| **全流程生产 SOP** | 规划一部漫剧/短剧从剧本拆分、分镜表、提示词批量生成、图片/视频生成、配音配乐到剪辑合成 | manju-production-pipeline | `manju-production-pipeline` |

## 2. 路由裁决

- **一句话能判断环节**：直接委派对应子技能。
- **跨环节任务**（如「从点子到成片」）：先走 screenplay-development / short-drama-screenwriter 定剧本，再按 manju-production-pipeline 全流程 SOP 串联人物、场景、动作、表情各环节。
- **信号模糊**：先问清当前处在「写剧本 / 做设定 / 出分镜 / 控表情 / 排全流程」哪一步，再分流，不猜。

## 3. 子技能路径解析

解析顺序：环境变量覆盖 → 本聚合层同级 skills 目录（安装器把内置子技能复制在旁边）→ 本机宿主目录探测（`~/.claude/skills`、`~/.openclaw/skills`、`~/.agents/skills`、`~/.doubao/agent_mode/workspace/.user_skills`）→ 报错提示安装。禁止把各子技能方法论复制进本聚合目录。上述 7 个子技能随 ZYX 仓库内置，安装器自动复制；依赖归属以 `../zyx/deps/manifest.json` 为准。

## 4. 边界

- 不产出电商带货编导方案（归 ecommerce-director）；不做投资决策类任务。
- 不替代子技能内部的具体方法论与模板；本层只做环节判定与委派衔接。
- 产物目录与命名遵循 zyx 共享产物规范（`../zyx/shared/artifacts/convention.md`，若可解析到）。
