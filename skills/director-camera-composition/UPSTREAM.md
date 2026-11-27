# Upstream

本技能是中文“剧本 / 提示词 → 机位方案”的导演层，框架重组自两个 MIT 开源 Claude Skill：

- https://github.com/joost/ai-camera-shots
  - commit: `326478f2af64a1dbf3b65b1207904e2731db39d3`
  - 提供：五决策、34 镜型、转场、检查清单
- https://github.com/Rylaispirit/cinematic-video-prompt-skill
  - commit: `389c193`
  - 提供：词表广度、prompt 公式、模型避坑

## 本技能新增

- 12 种情绪 × 六维处方
- 8 种 beat × 镜头配比
- 情绪转换三种走法
- 提示词四查、中文九段公式与字数口径
- 竖屏 9:16 原生构图
- 分镜表六行格式
- 一分钟机位口播模板

## 同步方式

本技能正文与 references 为中文改写版，不直接覆盖上游英文原文。同步上游时：

1. 先读上游 `SKILL.md` 与 references，确认术语和镜头语法没有破坏性变更。
2. 只把新增术语/失败点补进本技能对应 reference，不整包替换。
3. 保留本目录 `LICENSE` 中的上游版权声明。
