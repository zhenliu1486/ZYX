---
name: cinematic-fight-direction
display_name: "电影级打斗分镜"
description: >
  AI漫剧/短剧打斗戏分镜与动作提示词设计。当用户需要设计动作戏、打斗场面、
  武侠对决、现代格斗、枪战、追逐戏的分镜头脚本和AI生成提示词时使用。
  提供武侠、现代格斗、枪战、追逐四大类动作戏的标准分镜模板、运镜公式、
  动作关键词和节奏控制方法。触发词：打斗分镜、动作戏、武打、对决、
  枪战、追逐、动作设计、运镜、慢动作、打斗提示词。
---

# 电影级打斗分镜

为 AI 漫剧/短剧设计有电影感的动作戏分镜。核心目标：**每个镜头有明确的动作+运镜+情绪，批量生成不混乱**。

## 核心工作流

### 1. 按动作类型选模板

详见 [references/fight-templates.md](references/fight-templates.md)。

| 动作类型 | 典型场景 | 节奏特点 |
|---|---|---|
| 武侠对决 | 古风、仙侠、江湖 | 慢镜+快切结合，招式华丽 |
| 现代格斗 | 都市、动作片 | 近身短打，快速剪辑 |
| 枪战对峙 | 警匪、谍战 | 紧张静态+爆发射击 |
| 追逐戏 | 汽车、跑步、跑酷 | 长镜头+跟拍，动感强 |

### 2. 打斗戏五段式结构

每场完整打斗必须包含以下五拍，缺一不可：

```
①对峙铺垫 → ②第一招试探 → ③高潮对决 → ④一方受创 → ⑤胜负定格
```

**每拍对应镜头数**（标准30秒打斗）：
- ①对峙：3-4个镜头（眼神、站姿、环境）
- ②试探：2-3个镜头（第一招、格挡）
- ③高潮：5-8个镜头（快速对打、慢动作穿插）
- ④受创：2-3个镜头（倒地、受伤特写）
- ⑤定格：1-2个镜头（胜者站立、环境收尾）

### 3. 单镜头提示词公式

```
[景别] + [人物动作] + [运镜方式] + [环境] + [光影/速度效果] + [画质]
```

**示例（武侠挥剑）：**
```
medium close-up, warrior swinging sword downward, slow motion,
camera following blade movement, ancient courtyard background,
dust and leaves flying, dramatic backlight, cinematic, 8K, wuxia style
```

### 4. 打斗节奏控制

| 节奏段 | 镜头时长 | 运镜 | 速度感 |
|---|---|---|---|
| 对峙 | 3-5秒 | 固定/缓慢推镜 | 正常/慢 |
| 试探 | 1-2秒 | 快速切换 | 正常 |
| 高潮 | 0.5-1秒/镜 | 手持/跟拍 | 快切+穿插慢动作 |
| 受创 | 2-3秒 | 慢动作 | 慢放 |
| 定格 | 3-5秒 | 缓慢拉镜 | 正常/渐慢 |

## 运镜关键词速查

### 推进/拉近
```
dolly in, push in, zoom in, camera approaching
```

### 拉远/后退
```
dolly out, pull back, zoom out, camera retreating
```

### 跟随
```
tracking shot, follow shot, handheld follow, steadicam
```

### 环绕
```
orbit shot, camera circling, 360 degree shot
```

### 升降
```
crane shot, drone shot, camera rising/falling
```

### 晃动（紧张感）
```
handheld, shaky cam, jerky camera, motion blur
```

### 慢动作
```
slow motion, slow-mo, 120fps, time freeze, bullet time
```

## 动作关键词库

### 武侠动作
```
sword swing, sword draw, palm strike, kick, leap, landing,
block, parry, dodge, qi energy, flying sword, martial arts stance
```

### 现代格斗
```
punch, jab, cross, hook, uppercut, kick, knee, elbow,
grapple, throw, takedown, block, dodge, clinch
```

### 枪战
```
gun draw, firing, muzzle flash, shell ejection, reloading,
crouch shooting, aim down sights, cover fire
```

### 追逐
```
running, sprinting, jumping, vaulting, sliding,
parkour, climbing, car chase, weaving through crowd
```

## 资源索引

- **[references/fight-templates.md](references/fight-templates.md)** — 四大类动作戏完整分镜模板，含逐镜提示词
- **[references/speed-emotion.md](references/speed-emotion.md)** — 速度感与情绪对照表，按打斗阶段给出节奏参数
