# 手机可读公式

此模板使用准确 LaTeX 渲染为 PNG。公式不是由 imagegen 绘制，也不是把全篇正文截图。

```sh
python3 scripts/render_formula.py work/equation.tex --number 1 --output work/equation.png
```

输入只放数学表达式，不含文档环境与 `\tag`；例如 `\int_M K\,\mathrm{d}A=2\pi\chi(M)`。输出旁保留 `.render.tex`，便于追溯渲染参数。

渲染器需要 pdflatex 和 pdftoppm；通过 PATH 或 `--pdflatex` / `--pdftoppm` 指定。缺少时不要反复尝试或默认给用户装软件；选择环境里可用的准确数学渲染工具，维持以下规格。

- 12pt 字体、纸色 F7F8FC、字色 253A63、300dpi、4pt 边距。
- 默认 minipage 宽 **210pt**，较长式可用 `--width-pt 230`。以前 420pt 画布随手机整图缩小，实际字过小；210–230pt 让手机字约增大 1.8–2 倍。
- 图片 HTML：`display:block;width:100%;max-width:420px;height:auto;margin:0 auto;`。短公式应留自然空白，不强行裁剪放大到占满整屏；关键是缩窄渲染画布。
- 编号在 LaTeX 图中排好。空间不足时允许编号独占右下行，不能覆盖正文或被裁切。
- 使用 gathered/aligned/amscd 对长公式和交换图换行。交换图的上下行、箭头方向、自然性标注必须正确。不要通过更改命题含义来凑宽度。
- 渲染日志出现 Overfull hbox 必须修正后重跑；打开每个最终公式 PNG 检查缺字、上下标、编号与边缘裁切。
- 在手机宽度下，图内主要字符应接近正文尺寸，复杂下标可略小。不要仅把 900px 原图看清就认定在 300px 显示也清楚。

输入 TeX 源码保留在工作稿；复制 HTML 内不应含 `math`、`annotation`、`katex` 或未渲染的 TeX。图的 alt 留空，避免粘贴方将整段源码或替代文字显示出来。

更换主题底色后，用 `--paper` 和 `--ink` 指定六位十六进制颜色并重新渲染公式，避免公式图片出现异色底块。示例：`--paper F7F8FC --ink 253A63`。
