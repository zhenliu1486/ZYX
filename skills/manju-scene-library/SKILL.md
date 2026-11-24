---
name: manju-scene-library
display_name: "漫剧场景资产库"
description: >
  AI漫剧/短剧场景提示词资产库。当用户需要生成故事背景、环境设定、
  分镜场景图，或需要批量生产不同时间/天气/氛围的场景图时使用。
  覆盖都市、古风、现代、科幻、校园、民国等题材，包含室内/室外/
  日景/夜景/雨景/雪景等氛围模板，以及光影构图参数。
  触发词：场景提示词、背景图、环境设定、漫剧场景、分镜场景、
  场景生成、室内场景、室外场景、光影氛围。
---

# 漫剧场景资产库

为 AI 漫剧/短剧提供可复用的场景提示词体系。核心目标：**同一场景多氛围复用，批量生成不穿帮**。

## 核心工作流

### 1. 按题材定位场景大类

详见 [references/scenes.md](references/scenes.md)。

| 题材 | 室内高频场景 | 室外高频场景 |
|---|---|---|
| 都市现代 | 办公室、家、酒店、餐厅、医院 | 街道、停车场、天台、酒吧 |
| 古风仙侠 | 宫殿、书房、闺房、山洞 | 山林、渡口、城楼、集市 |
| 玄幻奇幻 | 城堡、魔法塔、神殿 | 森林、废墟、天空、地下 |
| 校园青春 | 教室、图书馆、宿舍、食堂 | 操场、校门口、天台、樱花道 |
| 民国年代 | 公馆、戏院、火车站 | 租界街道、码头、弄堂 |

### 2. 按五要素拼装场景提示词

```
[空间类型] + [时间/天气] + [光影氛围] + [构图角度] + [画质参数]
```

**示例（总裁办公室夜景）：**
```
luxurious corner office, night time, city skyline through floor-to-ceiling windows,
desk with leather chair, warm desk lamp light, cool blue moonlight,
wide angle shot from window side, cinematic, 8K, photorealistic
```

### 3. 同场景多氛围批量生成

同一空间换时间/天气/情绪，只需替换"时间/天气"和"光影氛围"两层：

| 基础空间 | 时间天气 | 光影氛围 |
|---|---|---|
| 都市街道 | 清晨/正午/黄昏/深夜 | 暖光/冷光/雨夜/雪天 |
| 古风宫殿 | 日出/正午/月夜 | 金碧辉煌/清冷肃穆/落雪 |
| 森林 | 晨雾/正午/黄昏 | 丁达尔光/幽暗/萤火虫 |

### 4. 场景一致性保持

1. **空间锚定**：每个核心场景固定 2-3 个特征物（如"落地窗+皮质沙发+落地灯"），所有镜头必带。
2. **色调统一**：同一场景的所有镜头保持主色调（冷蓝/暖黄），避免忽明忽暗。
3. **透视一致**：固定机位角度（平视/俯视/仰视），避免跳轴。

## 光影氛围速查

### 电影感光影关键词
```
cinematic lighting, rim light, backlight, soft diffused light,
low key lighting, high key lighting, golden hour, blue hour,
chiaroscuro, volumetric light, god rays, lens flare
```

### 情绪-光影对照

| 情绪 | 光影关键词 |
|---|---|
| 浪漫/温馨 | warm golden light, soft glow, candlelight, bokeh |
| 紧张/悬疑 | low key, harsh shadows, single light source, neon |
| 悲伤/孤独 | cool blue tone, desaturated, rain reflection, dim |
| 霸气/强势 | backlight silhouette, rim light, dramatic contrast |
| 清新/治愈 | bright natural light, soft shadows, pastel colors |
| 古风仙气 | misty, ethereal, moonlit, incense smoke |

## 资源索引

- **[references/scenes.md](references/scenes.md)** — 300+ 场景详细模板，按题材×室内外×时间分类
- **[references/lighting-composition.md](references/lighting-composition.md)** — 光影与构图参数手册，按镜头类型给出具体参数
