# 真人感参数包

按镜头类型给出完整的真人感参数组合，可直接复制使用。

## 目录
- [通用真人感后缀](#通用真人感后缀)
- [特写镜头参数](#特写镜头参数)
- [半身镜头参数](#半身镜头参数)
- [全身镜头参数](#全身镜头参数)
- [按情绪调整](#按情绪调整)

---

## 通用真人感后缀

所有面部视频，必须加在提示词最后：

```
natural micro-expressions, subtle eye movements, natural blinking,
slight breathing motion, skin texture, visible pores, realistic skin,
slight facial asymmetry, natural variation, cinematic, photorealistic,
8K resolution, 35mm film grain, professional color grading
```

### 通用负面词

```
plastic skin, doll face, mannequin, smooth airbrushed skin,
CGI, 3D render, cartoon, anime, illustration,
exaggerated expression, frozen face, dead eyes, no blinking,
stiff movement, unnatural, over-smoothed, perfect symmetry,
deformed, blurry, low quality, watermark, text
```

---

## 特写镜头参数（面部大特写）

**适用**：情绪重点、眼泪、眼神变化

```
extreme close-up, face only, shallow depth of field,
85mm portrait lens, soft bokeh background,
[情绪关键词],
natural micro-expressions, subtle eye movements, natural blinking,
slight breathing motion, skin texture, visible pores, realistic skin,
slight facial asymmetry, natural variation,
cinematic lighting, rim light on face,
8K, photorealistic, 35mm film grain
```

**特写专属关键词**：
- 皮肤细节：`skin texture, pores, fine lines, natural skin`
- 眼神细节：`catchlight in eyes, glassy eyes, tear reflection`
- 微表情：`micro-expression, subtle movement, slight twitch`

---

## 半身镜头参数（对话/上半身）

**适用**：对话镜头、手势+表情

```
medium close-up, upper body, waist up,
[人物描述], [动作/表情],
[场景背景],
natural micro-expressions, natural blinking, slight breathing,
slight head movement, natural posture,
skin texture, realistic skin tones,
cinematic, 8K, photorealistic, film grain
```

**半身专属关键词**：
- 手部：`natural hand position, relaxed fingers, natural gesture`
- 头部：`slight head tilt, natural head movement`
- 肩膀：`relaxed shoulders, natural posture`

---

## 全身镜头参数（出场/动作）

**适用**：人物出场、动作戏、环境人物

```
full body shot, entire body visible, standing pose,
[人物全身描述], [动作],
[完整环境场景],
natural body posture, realistic proportions,
natural movement, walk cycle, dynamic pose,
cinematic wide shot, environmental portrait,
8K, photorealistic, film grain
```

**全身专属关键词**：
- 身体比例：`natural body proportions, realistic height`
- 动作：`natural movement, fluid motion, relaxed posture`
- 环境互动：`interaction with environment, natural stance`

---

## 按情绪调整

### 悲伤/难过
- **光线**：soft diffused light, cool blue tone, dim lighting
- **皮肤**：pale skin, tear-streaked cheeks, red eyes
- **动作**：slight trembling, shoulders hunched, looking down

### 愤怒
- **光线**：harsh lighting, strong shadows, high contrast
- **皮肤**：red face, tense neck muscles, sweat
- **动作**：clenched fists, jaw tight, leaning forward

### 喜悦/开心
- **光线**：bright warm light, golden hour, soft glow
- **皮肤**：rosy cheeks, natural glow, smiling eyes
- **动作**：relaxed posture, open body language, laughing

### 紧张/焦虑
- **光线**：flat lighting, cool tones, slightly dim
- **皮肤**：pale, slight sweating, fidgeting
- **动作**：fidgeting, darting eyes, tight posture

### 浪漫/温柔
- **光线**：warm candlelight, soft glow, shallow depth of field
- **皮肤**：soft skin, rosy cheeks, dewy eyes
- **动作**：slow movements, gentle gaze, close proximity

---

## 参数权重建议

### 最重要的参数（权重最高）
1. 皮肤真实感：`skin texture, pores, realistic skin`
2. 眼睛自然：`natural blinking, subtle eye movements, catchlight`
3. 不对称：`slight asymmetry, natural variation`

### 次要参数
4. 呼吸起伏：`slight breathing motion`
5. 微动作：`micro-expressions, subtle movements`
6. 光影：`cinematic lighting, rim light`

### 可有可无
7. 胶片颗粒：`film grain`
8. 画质：`8K, photorealistic`

**提示**：如果只能加3个词，就加：`skin texture, natural blinking, slight asymmetry`
