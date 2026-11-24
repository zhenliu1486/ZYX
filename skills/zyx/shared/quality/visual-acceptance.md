# 视觉验收（Look Gate）

> 适用：PPT/PPTX、HTML 页面、PDF、封面、海报、分镜图、视频缩略图等任何“用户会看见”的产物。
> 借鉴 Omarchy 的 `omarchy agent look theme/app/plugin/page`：先把结果渲染成图，让 agent 自己看，再决定是否交付。**不看图，不算验收。**

## 1. 三步

1. **生成产物**：正常落盘到 `zyx-output/<来源>/<产物>/`。
2. **渲染成图**：
   ```bash
   python3 ../../scripts/look.py <产物路径> --out <产物目录>/look
   ```
   输出 `look/look.png`（contact sheet）、`look.json`、`MANIFEST.md`。
3. **亲自看图**：用 Read 打开 `look.png`，按下面六条检查；有问题改源文件，重跑，直到通过。

## 2. 六条检查

- **溢出 / 裁切**：标题、表格、代码块是否出界；长页面是否被截断。
- **对比度**：正文与背景、按钮与底色是否够读；深色主题下有没有“黑字黑底”。
- **层级**：第一眼是否看到该看的东西；标题、正文、注释是否三级清楚。
- **可读性**：手机宽度（390px）下字是否过小；封面在信息流里是否 1 秒能读。
- **一致性**：同一页的圆角、间距、字体、配色是否统一；图标有没有缺字。
- **缺字 / 乱码**：中文、emoji、特殊符号是否渲染成方框。

## 3. 通过标准

- `look.png` 里没有上述六类问题，或剩余问题已在 `MANIFEST.md` 标注“已知且可接受”。
- `look.json` 的 `pages` 覆盖了全部页面；超过 8 页的 PPT 用 `--pages` 全量渲染，不能只看前 8 页就宣称通过。
- `MANIFEST.md` 记录“视觉验收：通过（日期）/ 未通过项 / 修复动作”。

## 4. 工具缺失时

- HTML 需要 chromium 或 playwright；PPTX/PDF 需要 libreoffice + pdftoppm；视频需要 ffmpeg；拼图需要 Pillow 或 ImageMagick。
- 缺工具时 `look.py` 返回 3 并明确报错。此时在 `MANIFEST.md` 写“未做视觉验收（缺 X）”，**不得宣称已验证**。
- 纯文本产物（Markdown 报告、代码、Skill 文档）不需要跑 Look Gate。

## 5. 边界

- 只读源产物，不改文件；渲染中间件在临时目录，跑完清理。
- 不上传、不联网；图片只落本机 `zyx-output/look/` 或指定 `--out`。
- 视觉验收是“人/agent 看图判断”，不是自动审美评分；`look.py` 只负责把结果摊开。
