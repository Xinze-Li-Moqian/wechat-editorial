---
name: wechat-editorial
description: 按已有公众号设计，将新闻、论文资料或中文正文制作成可复制的 HTML，支持 LaTeX 公式图片、插图、表格和代码。用于公众号写作、排版、设计调整及发布前检查。
---

# 公众号制作

保留用户认可的版式，交付一份有“复制全文”按钮的独立 HTML。正文是文字，公式是准确数学渲染的 PNG。不要将文章重做成网站或整篇长图。

## 内容

- 用户给完整正文，默认保留措辞；局部要求只改相应位置。用户要求重构时，先明确文章主线再整体调整。
- 新闻和论文解读先读原始来源，遵循 [资料核实](workflow/sources.md)。别混淆团队公告、论文结论与自己的推断。
- 阅读 [写作要求](workflow/writing.md)。结构随主题安排，不把历史示例的四节结构当成通用要求。
- 精确公式、编号、交换图用 LaTeX；如要生成插图，使用环境中可用的图像生成工具。整体风格参考 [设计规范](workflow/design.md)，不默认新增配图。

## 制作

- 按 [输入格式](workflow/input-format.md) 准备 JSON。示例在 `examples/article.json`，所有图片路径相对输入文件。
- 用 `scripts/build_article.py` 生成 HTML。默认样式在 `templates/theme.json`；支持 `--theme` 和 `--template`，可覆盖路径。
- 公式需重新渲染时读 [公式规范](workflow/formulas.md)，运行 `scripts/render_formula.py`。保持手机可读字号，保留 `.tex` 源码；不要把未渲染的 TeX、隐藏 MathML 或重复的公式文字带入复制区。
- 研究过程、稿件和素材放 `work/`，最终 HTML 放 `dist/`。不要为同一成品生成难以区分的多个版本。

## 交付

- 读 [交付检查](workflow/delivery.md)，运行 `scripts/check_article.py`。结构检查与真实渲染、公众号预览分开记录。
- 检查桌面与 375 / 430px 宽度，特别是公式、长代码和表格。若环境无法预览，说明实际完成的检查，别声称公众号粘贴已验证。
- 复制区只包含正文。默认不生成 href 链接；资料 URL 保留在 JSON，用户需要时可作为普通文字加入。
- 发布前仍需在用户的公众号编辑器核对结果。不要默认要求第三方插件，也不要自行上传、发布或改变账号设置。
