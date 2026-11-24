# 可选模板（Obsidian Templater / 手动复制均可）

这些模板只是**可选项**：R7 不内置 Obsidian 插件配置，`wiki.py new-page` 已经能生成同结构的 frontmatter。
想用 Obsidian 的模板功能时，把本目录复制到你的模板文件夹，或直接照抄 frontmatter。

| 文件 | 页面类型 | 放到 |
|---|---|---|
| `source.md` | 来源摘要 | `wiki/sources/summary-<slug>.md` |
| `entity.md` | 实体 | `wiki/entities/<slug>.md` |
| `concept.md` | 概念 | `wiki/concepts/<slug>.md` |
| `comparison.md` | 对比 | `wiki/comparisons/<slug>.md` |
| `synthesis.md` | 综述 | `wiki/syntheses/<slug>.md` |

占位符：`{{title}}`、`{{slug}}`、`{{date}}`；Templater 会替换，手动用时直接改。
