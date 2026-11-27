# Upstream

- Repo: https://github.com/joost/ai-camera-shots
- Commit: `326478f2af64a1dbf3b65b1207904e2731db39d3`
- License: MIT（见 `LICENSE`）
- Synced: 2026-11-27

## 为什么内置

`ai-camera-shots` 只有约 64KB，是完整的镜头语法层：五决策、34 种镜头、运镜、转场、9:16、对话覆盖、镜头清单格式。它和 ZYX 的 R5 影视链路强耦合，内置后所有宿主开箱可用。

## 同步方式

```bash
git clone --depth 1 https://github.com/joost/ai-camera-shots /tmp/ai-camera-shots
cp /tmp/ai-camera-shots/skills/ai-camera-shots/SKILL.md skills/ai-camera-shots/SKILL.md
cp /tmp/ai-camera-shots/skills/ai-camera-shots/references/*.md skills/ai-camera-shots/references/
cp /tmp/ai-camera-shots/LICENSE skills/ai-camera-shots/LICENSE
```

同步后检查：`SKILL.md` frontmatter 的 `name` 仍为 `ai-camera-shots`，引用文件路径未变。
