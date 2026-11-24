# 批量生成指令格式

## 目录
- [图片批量生成指令](#图片批量生成指令)
- [视频批量生成指令](#视频批量生成指令)
- [参数配置模板](#参数配置模板)
- [常见问题与修正](#常见问题与修正)

---

## 图片批量生成指令

### 标准格式

```
【参考图】
- 人物定妆图：[URL或本地路径]
- 场景参考图：[URL或本地路径]（如有）

【全局参数】
- 画幅：9:16（竖屏）/ 16:9（横屏）
- 风格：cinematic, photorealistic, 8K, 35mm film grain
- 统一负面词：plastic skin, CGI, 3D render, anime, cartoon, deformed, watermark, text

【逐镜提示词】
[镜号1]：[本镜完整提示词]
[镜号2]：[本镜完整提示词]
[镜号3]：[本镜完整提示词]
...
```

### 示例

```
【参考图】
- 女主定妆：https://xxx/linwan.png
- 男主定妆：https://xxx/gushen.png
- 总裁办公室空镜：https://xxx/office.png

【全局参数】
- 画幅：9:16
- 风格：cinematic, photorealistic, 8K, 35mm film grain, soft lighting
- 负面词：plastic skin, CGI, 3D render, anime, cartoon, deformed hands, extra fingers, watermark, text, logo

【逐镜】
1-01：wide shot, modern CEO office, woman standing in front of desk, man sitting behind, floor-to-ceiling windows, city view, daytime natural light
1-02：close shot, cold face CEO man, pushing document across desk, sharp eyes, office background
1-03：extreme close-up, shocked woman face, wide eyes, slightly open mouth, tears welling up, shallow depth of field
```

---

## 视频批量生成指令

### 标准格式

```
【参考帧】
- 每镜对应图片：[镜号: 图片URL]

【全局参数】
- 时长：每镜3秒
- 帧率：24fps
- 风格：cinematic motion, natural movement

【逐镜运动指令】
[镜号1]：[运镜+微动描述]
[镜号2]：[运镜+微动描述]
...
```

### 逐镜运动指令模板

| 镜头类型 | 运动指令模板 |
|---|---|
| 对话固定镜头 | `slow push in, subtle head movement, natural blinking, 3 seconds` |
| 情绪特写 | `slow push in, eyes slowly welling up, slight lip trembling, hair gently moving` |
| 走路镜头 | `tracking shot, person walking forward, natural arm swing, background passing by` |
| 动作镜头 | `dynamic motion, quick movement, motion blur, action pose` |
| 环境空镜 | `slow pan, clouds moving, light shifting, subtle environmental motion` |

---

## 参数配置模板

### 人物一致性参数
```
参考图权重：0.7-0.8
面部相似度：0.85
服装一致性：0.8
seed：固定同一人物同一seed
```

### 场景一致性参数
```
场景参考图权重：0.6-0.7
色调统一：暖色调/冷色调固定
构图角度：固定平视/俯视/仰视
```

### 画质参数
```
分辨率：1080x1920（竖屏）/ 1920x1080（横屏）
采样步数：30-50
CFG scale：7-9
高清修复：开启
```

---

## 常见问题与修正

| 问题 | 原因 | 修正方法 |
|---|---|---|
| 人物脸变了 | 参考图权重太低 | 提高参考图权重到0.8，加更多面部锚定词 |
| 场景不对 | 场景参考不够 | 加场景关键词，用场景图做img2img |
| 手变形 | 模型通病 | 避免手部特写，或用负面词排除 |
| 服装变了 | 描述不够细 | 服装描述放提示词最前面 |
| 整体偏AI感 | 缺胶片质感 | 加 35mm film grain, photorealistic, skin texture |
| 画面太亮/太暗 | 光影描述缺失 | 明确加 lighting 描述（low key/soft light 等） |
