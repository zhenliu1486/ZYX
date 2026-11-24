---
name: manju-character-library
display_name: "漫剧人物资产库"
description: >
  AI漫剧/短剧人物设定与提示词资产库。当用户需要为漫剧、短剧、AI视频生成角色设定、
  人物外貌描述、服装配饰方案，或需要批量生成人物提示词、保持角色一致性时使用。
  覆盖男频/女频、古风/现代/科幻/都市等题材，包含主角、配角、反派、群像的
  分类模板与可直接拼接的提示词公式。触发词：人物设定、角色设计、漫剧人物、
  角色提示词、人物一致性、女主男主、配角设定、立绘提示词。
---

# 漫剧人物资产库

为 AI 漫剧/短剧生产可复用的角色设定与提示词体系。核心目标：**一次设定，全剧复用，批量生成不跑脸**。

## 核心工作流

### 1. 按题材选人物模板

先定位题材，再从对应分类挑人物原型。详见 [references/characters.md](references/characters.md)。

| 题材 | 女频常用原型 | 男频常用原型 |
|---|---|---|
| 都市现代 | 霸总千金、逆袭女主、职场御姐、甜妹 | 兵王归来、赘婿逆袭、商界大佬、纨绔 |
| 古风仙侠 | 仙侠女主、王妃/皇后、才女、妖女 | 修仙男主、帝王、侠客、魔尊 |
| 玄幻奇幻 | 精灵法师、龙族公主、血族女王 | 龙傲天、暗黑战士、法师、刺客 |
| 校园青春 | 校花、学霸、转学生、甜妹 | 校草、学霸、体育生、痞帅 |
| 民国年代 | 千金小姐、女特务、戏子 | 军阀、地下党、少爷、黑帮 |

### 2. 按四层结构拼装提示词

每个人物必须输出以下四层，缺一不可：

```
[身份标签] + [外貌特征] + [服装造型] + [光影画质]
```

**示例（霸总女主）：**
```
cold CEO woman, sharp jawline, high cheekbones, long black hair in low bun,
wearing tailored white blazer and black pencil skirt, gold watch,
cinematic lighting, 8K, photorealistic, 35mm film grain
```

### 3. 人物一致性保持三原则

1. **固定锚点词**：每个人物选 3 个不可变锚点（如"左眼下一颗泪痣"、"栗色大波浪"、"身高178"），每张图必带。
2. **Seed 锁定**：同一人物所有生成使用同一 seed 值，偏差控制在 ±0.05。
3. **参考图回流**：先用文字生成满意定妆照，后续所有镜头以定妆照为 img2img 参考图，权重 0.6-0.8。

### 4. 批量生成指令格式

当需要一次生成多个人物时，按以下表格输出（每行一个人物）：

| 人物 | 身份 | 锚点词 | 主提示词 | 负面词 |
|---|---|---|---|---|
| 女主林晚 | 逆袭女主 | 栗色大波浪、右颊梨涡、165cm | ... | ... |
| 男主顾深 | 商界大佬 | 剑眉、短碎发、188cm | ... | ... |

## 提示词模板速查

### 男性通用正面词
```
handsome man, sharp facial features, defined jawline, clear eyes,
[hairstyle], [clothing], standing posture, cinematic half-body shot
```

### 女性通用正面词
```
beautiful woman, delicate features, fair skin, expressive eyes,
[hairstyle], [clothing], elegant posture, soft lighting
```

### 通用负面词（防 AI 感）
```
plastic skin, CGI, 3D render, anime, cartoon,
deformed hands, extra fingers, blurry, watermark, text, logo,
over-smoothed face, unrealistic proportions, doll-like
```

## 资源索引

- **[references/characters.md](references/characters.md)** — 200+ 人物原型详细设定库，按题材分类，含外貌、服装、性格、台词风格
- **[references/prompt-formula.md](references/prompt-formula.md)** — 提示词公式拆解与拼接示例，按景别（特写/半身/全身）调整
