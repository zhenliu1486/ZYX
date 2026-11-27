# video-studio 子技能映射明细

> 本文件是聚合层 `SKILL.md` 路由表的展开清单；子技能保持独立安装，本目录不复制其方法论。

| 制作环节 | 子技能目录名 | 主要产出 | 衔接上游 / 下游 |
|---|---|---|---|
| 故事/剧本开发 | `screenplay-development` | 故事点子评估、三幕结构、英雄之旅、救猫咪节拍表、人物弧光 | 上游：用户原始构思；下游：编剧/全流程 SOP |
| 竖屏短剧编剧 | `short-drama-screenwriter` | 女频甜宠/虐恋/逆袭、男频兵王/赘婿/修仙剧本，开头钩子、反转节奏、集尾悬念 | 上游：剧本框架；下游：人物/场景设定、分镜 |
| 人物设定 | `manju-character-library` | 角色外貌、服装配饰、群像设定、批量人物提示词、角色一致性 | 上游：剧本；下游：人物图片/视频生成 |
| 场景设定 | `manju-scene-library` | 故事背景、环境设定、分镜场景图、时间/天气/氛围场景批量生产 | 上游：剧本；下游：场景图片/视频生成 |
| 导演运镜/机位/构图 | `director-camera-composition` | 情绪→六维处方、beat→镜头配比、机位/运镜/构图、正反打、180°、竖屏 9:16、分镜表、提示词四查重写 | 上游：剧本/情绪/提示词；下游：镜头语法、动作分镜、词汇增强、生成 |
| 镜头语言/分镜/转场 | `ai-camera-shots` | 五决策、34 种镜头、运镜、隐藏剪辑/甩镜/匹配剪辑/动作切/首尾帧、9:16、对话正反打、镜头清单 | 上游：导演层/剧本/场景/人物；下游：动作分镜、提示词词汇包、生成 |
| 提示词词汇/修 prompt（可选） | `cinematic-video-prompt` | 光照/构图/镜头/色彩/情绪/材质/天气词汇，prompt 公式、模型避坑、修「太平/太 AI」 | 上游：镜头清单；下游：图片/视频生成 |
| 动作/打斗戏 | `cinematic-fight-direction` | 武侠对决、现代格斗、枪战、追逐戏分镜镜头与 AI 生成提示词 | 上游：剧本/场景/导演层；下游：动作片段生成 |
| 微表情/表情视频 | `micro-expression-video` | 真实自然面部表情视频、情绪变化控制、眼神/嘴角/呼吸/眨眼参数 | 上游：人物设定；下游：人物特写片段生成 |
| 全流程生产 SOP | `manju-production-pipeline` | 剧本拆分、分镜表、提示词批量生成、图片/视频生成、配音配乐、剪辑合成 | 串联以上各环节的总流程 |

## 跨环节串联顺序

1. 构思与结构：`screenplay-development`（或直接 `short-drama-screenwriter` 进短剧套路）。
2. 剧本落地：`short-drama-screenwriter` 出分集剧本与钩子反转。
3. 设定资产：`manju-character-library` + `manju-scene-library`。
4. 导演判断：`director-camera-composition` 逼出一句话、拆 beat、定情绪曲线与机位。
5. 镜头语法：`ai-camera-shots` 校验景别/机位/焦段/运镜/转场与镜头清单。
6. 提示词增强：`cinematic-video-prompt`（可选）补光照/构图/色彩/情绪/材质，或修 prompt。
7. 动作与表演：`cinematic-fight-direction`（动作戏）+ `micro-expression-video`（表情）。
8. 成片流程：`manju-production-pipeline` 串联拆分、生成、配音、剪辑。

## 边界

- 电商带货信息流编导不归本聚合层，归 `ecommerce-director`。
- 本层不内嵌各子技能模板；缺哪个子技能时，doctor/路由脚本会提示未检测到并指向安装。`cinematic-video-prompt` 未装时，镜头/转场可由内置 `director-camera-composition` + `ai-camera-shots` 独立完成。
- 动作/打斗/枪战/追逐以 `cinematic-fight-direction` 为主控；导演层与镜头层只补通用景别、运镜与转场，不重新定义打斗结构。
- `director-camera-composition` 是中文导演层，框架重组自两个 MIT 上游；`ai-camera-shots` 是 MIT 镜头语法层，二者都保留了 `LICENSE` / `UPSTREAM.md`。
