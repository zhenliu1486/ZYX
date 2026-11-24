---
name: micro-expression-video
display_name: "微表情视频生成"
description: >
  AI真人感微表情视频生成提示词与参数控制。当用户需要生成真实自然的
  人物面部表情视频、控制情绪变化、避免AI感塑料脸、或需要精确描述
  微表情（眼神、嘴角、呼吸、眨眼等）时使用。提供真人感参数包、
  微表情关键词库、情绪渐变模板和常见问题修正方案。
  触发词：微表情、真人感、面部表情、情绪变化、眼神、
  表情视频、不自然、AI脸、塑料脸、自然表情。
---

# 微表情视频生成

让AI生成的人物有真实、细腻、自然的面部表情。核心目标：**不像AI，像真人**。

## 核心原则

### 真人感三要素

1. **微动作**：不是大表情，而是细微的眼神变化、嘴角抽动、呼吸起伏
2. **不对称**：真人表情不是完全对称的，左右脸有细微差异
3. **过渡自然**：情绪不是瞬间切换的，有渐变过程

---

## 真人感必备参数

所有面部视频提示词，必须加上以下"真人感后缀"：

```
natural micro-expressions, subtle eye movements,
natural blinking, slight breathing motion,
skin texture, pores, realistic skin,
symmetry slight variation, natural facial asymmetry,
cinematic, photorealistic, 8K, film grain
```

### 防AI感负面词

```
negative prompt: plastic skin, doll face, mannequin,
smooth skin, CGI, 3D render, cartoon, anime,
exaggerated expression, frozen face, dead eyes,
no blink, stiff, unnatural, over-smoothed
```

---

## 微表情关键词库

详见 [references/micro-expression-keywords.md](references/micro-expression-keywords.md)。

### 眼神变化

| 情绪 | 关键词 |
|---|---|
| 惊讶 | eyes widening, eyebrows raising, pupils dilating |
| 悲伤 | eyes welling up, teary eyes, gaze lowering |
| 愤怒 | eyes narrowing, glaring, jaw tightening |
| 思考 | eyes glancing sideways, slight squinting, looking away |
| 害羞 | eyes darting down, cheeks flushing, avoiding eye contact |
| 魅惑 | half-lidded eyes, slow blink, gaze holding |
| 冷漠 | blank stare, dead eyes, unblinking |
| 温柔 | soft eyes, slight smile in eyes, warm gaze |

### 嘴部变化

| 情绪 | 关键词 |
|---|---|
| 忍住不哭 | trembling lips, biting lower lip, chin quivering |
| 强忍怒火 | clenched jaw, thin lips, nostril flaring |
| 欲言又止 | lips parting slightly, hesitating, pressing lips together |
| 苦笑 | sad smile, corners of mouth twitching down |
| 惊讶 | mouth falling open, lips parting |

### 头部动作

| 情绪 | 关键词 |
|---|---|
| 倾听 | slight head tilt, nodding slightly |
| 思考 | head resting on hand, looking up |
| 失望 | looking down, shaking head slightly |
| 坚定 | chin lifting, looking straight ahead |

---

## 情绪渐变模板

真人的情绪不是瞬间切换的，而是有一个渐变过程。详见 [references/emotion-transition.md](references/emotion-transition.md)。

**示例：从平静到震惊**
```
0-1秒：平静，中性表情，自然眨眼
1-2秒：眉毛微微抬起，眼睛开始睁大
2-3秒：嘴微微张开，眼神凝固
3-4秒：完全震惊，瞳孔放大，身体僵硬
```

---

## 常见问题修正

| 问题 | 修正方法 |
|---|---|
| 脸像塑料/假人 | 加 skin texture, pores, realistic skin；负面词加 plastic skin, doll |
| 眼睛死的/没神 | 加 natural blinking, subtle eye movements；负面词加 dead eyes, no blink |
| 表情太夸张 | 加 subtle expression, micro-expression；负面词加 exaggerated |
| 完全不动/僵 | 加 slight breathing, subtle movements；负面词加 frozen, stiff |
| 嘴型不对 | 避免说话镜头，或用对口型专用模型 |
| 左右脸完全对称 | 加 slight asymmetry, natural facial variation |

## 资源索引

- **[references/micro-expression-keywords.md](references/micro-expression-keywords.md)** — 按情绪分类的完整微表情关键词库，含眼神、嘴部、头部、肢体
- **[references/emotion-transition.md](references/emotion-transition.md)** — 情绪渐变模板，从A情绪到B情绪的逐秒变化
- **[references/realistic-params.md](references/realistic-params.md)** — 真人感参数包，按镜头类型给出完整参数组合
