# 提示词公式拆解

按景别、情绪、场景调整的人物提示词拼装公式。

## 目录
- [通用公式结构](#通用公式结构)
- [按景别调整](#按景别调整)
- [按情绪调整](#按情绪调整)
- [按场景调整](#按场景调整)
- [完整示例](#完整示例)

---

## 通用公式结构

```
[镜头景别], [人物年龄/性别], [面部特征], [发型], [服装], [动作/姿态], [场景背景], [光影], [画质参数]
```

**权重建议**（逗号分隔，越靠前权重越高）：
- 面部特征：权重最高，直接决定像不像
- 服装：权重中等，决定身份感
- 背景：权重最低，可虚化

---

## 按景别调整

### 1. 特写（面部表情）
```
close-up portrait, [face features only], [expression], shallow depth of field,
soft bokeh background, cinematic lighting, 85mm lens
```
**关键词**：`close-up, extreme close-up, face only, skin texture`

### 2. 半身（对话镜头）
```
medium shot, upper body, [clothing details], [hand gesture],
waist-up composition, natural lighting
```
**关键词**：`medium shot, half body, upper body, waist up`

### 3. 全身（出场/定妆）
```
full body shot, [full outfit], [pose], standing/full length,
wide composition, environment visible
```
**关键词**：`full body, full length, entire body, standing pose`

---

## 按情绪调整

| 情绪 | 面部关键词 | 身体语言 |
|---|---|---|
| 愤怒 | furrowed brows, glaring eyes, clenched jaw | crossed arms, leaning forward |
| 悲伤 | teary eyes, trembling lips, pale face | looking down, hunched shoulders |
| 喜悦 | smiling eyes, dimples, bright expression | open posture, relaxed |
| 惊讶 | wide eyes, open mouth, raised brows | hand on chest, leaning back |
| 冷漠 | blank stare, thin lips, cold eyes | arms crossed, turned away |
| 魅惑 | half-lidded eyes, smirk, parted lips | leaning closer, hair falling |
| 恐惧 | widened eyes, pale, sweating | shrinking back, trembling |

---

## 按场景调整

### 室内（办公室）
```
modern office background, desk, computer, floor-to-ceiling windows,
city skyline, natural light from window
```

### 室内（卧室）
```
cozy bedroom, soft bedding, warm lamp light, curtains,
intimate atmosphere
```

### 室外（街道）
```
city street background, buildings, pedestrians, daylight,
urban atmosphere
```

### 室外（自然）
```
nature background, trees, sky, sunlight through leaves,
fresh air, bokeh foliage
```

---

## 完整示例

### 示例1：女主定妆照（都市逆袭）
```
full body shot, 25-year-old woman, oval face, almond eyes, natural makeup,
long chestnut wavy hair, slim figure 165cm,
wearing white blouse and black pencil skirt, white heels, gold watch,
standing confidently, arms crossed,
modern office background with floor-to-ceiling windows,
cinematic lighting, 8K, photorealistic, 35mm film grain, shallow depth of field
```

### 示例2：男主特写（霸总冷漠）
```
extreme close-up, 28-year-old man, sharp jawline, chiseled features,
short textured black hair, cold thin lips, sharp eyes,
wearing white dress shirt with top button undone,
cold expression, looking away,
dark background, rim lighting, 85mm portrait lens,
8K, skin texture, cinematic, film grain
```

### 示例3：古风女主（仙侠）
```
medium shot, 20-year-old woman, delicate phoenix eyes, long black hair in loose bun with hairpin,
wearing flowing white hanfu with silver embroidery,
holding sword, gentle but determined expression,
mountain pavilion background, mist, soft sunlight,
xianxia style, cinematic, wuxia aesthetic, 8K
```

---

## 负面词模板

### 通用防AI感
```
plastic skin, CGI, 3D render, anime, cartoon, illustration,
deformed hands, extra fingers, missing fingers, blurry, out of focus,
watermark, text, logo, signature,
over-smoothed face, doll-like, unrealistic proportions,
bad anatomy, mutated, disfigured
```

### 人物一致性负面
```
different person, changed face, altered features, hairstyle change,
different outfit, extra character, duplicate,
```
