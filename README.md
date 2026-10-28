# 公众号工作流与设计模板

将新闻、论文资料或中文正文，制作成一份可复制到公众号编辑器的 HTML。

这个仓库保存写作要求、蓝金风格模板和生成脚本。正文保持可编辑文字，公式由 LaTeX 排成图片，插图嵌入成品。适合配合 Codex 使用，也可以单独修改设计和制作稿件。

## 先看效果

下载仓库后，用浏览器打开 **`examples/preview.html`**。它包含标题、段落、插图、公式、代码和表格，可切换 375 / 430 / 790px 文章宽度。

**修改设计的入口是 `templates/theme.json`。** 每个组件的样式集中保存于此；`templates/page.html` 管理预览工具和复制按钮。预览文件由脚本生成，不需要直接编辑它。

```sh
python3 scripts/build_article.py examples/article.json --output dist/设计预览.html
```

打开 `dist/设计预览.html` 查看修改结果。普通文章生成只需 Python 3.9+，无第三方 Python 依赖，无需安装前端构建工具。

## 用 Codex 制作文章

在 Codex 中打开这个仓库，例如输入：

> 按仓库里的公众号工作流，把以下新闻和论文制作成文章。先核对原始来源，按我给的大纲写作，沿用现有设计。公式转图片，最终输出一份可复制的 HTML。

`AGENTS.md` 引导 Codex 使用根目录的 `SKILL.md`。写作、设计和发布要求位于 `workflow/`。文章结构由主题和用户决定，不强制所有稿件使用相同章节。

## 自己制作一篇文章

1. 把 `examples/article.json` 复制到 `work/my-article/article.json`，替换标题、正文和图片路径。
2. 图片路径相对该 JSON 文件。公式使用已有 PNG 即可；需要新公式时见下方命令。
3. 生成并检查：

```sh
python3 scripts/build_article.py work/my-article/article.json --output dist/公众号复制版.html
python3 scripts/check_article.py dist/公众号复制版.html
```

4. 在浏览器中打开成品，检查桌面及手机宽度，点击“复制全文”后粘贴到公众号正文框。继续在公众号预览中核对图片和公式，再自行保存、发布。

图片内嵌、关键样式内联，复制区不带网页工具栏。模板沿用了此前实际发布成功的格式；新设计或新粘贴环境仍以公众号预览为准。检查脚本验证文件结构，不代替视觉检查。

## 数学公式

示例已经附带公式 PNG，不需要安装 LaTeX 即可生成预览。**重新渲染公式**需要本地 `pdflatex` 与 `pdftoppm`（TeX 与 Poppler），并安装 `standalone`、`amsmath`、`amssymb`、`amscd`、`xcolor` 包。

```sh
python3 scripts/render_formula.py examples/assets/equation.tex --number 1 --output work/equation.png
```

默认以 210pt 画布、12pt 字体、300dpi 渲染，兼顾手机阅读。修改底色后，可用 `--paper F7F8FC --ink 253A63` 同步公式颜色。原始 TeX 保留，编号写入图片；不把 KaTeX 或隐藏 MathML 直接复制到公众号。长公式、交换图和工具路径设置见 [公式规范](workflow/formulas.md)。

## 仓库内容

```text
templates/        页面模板与组件样式
scripts/          文章生成、公式渲染、成品检查
workflow/         写作、资料核实、设计、交付与输入格式
examples/         示例输入、图片和生成好的预览
SKILL.md          可复用的 Codex 技能入口
AGENTS.md         Codex 在仓库中工作的约定
tests/           生成器的行为检查
```

工作稿放 `work/`，新成品放 `dist/`；两者默认不提交。仓库不包含公众号账号信息、第三方论文截图或本次 AxiomMath 新闻正文。示例蓝金插图来自本工作流此前生成的配图，公式示例为正规子群的定义。

## 检查与维护

```sh
python3 -m unittest discover -s tests -v
python3 scripts/build_article.py examples/article.json --output examples/preview.html
python3 scripts/check_article.py examples/preview.html
```

更改模板后同步生成示例预览。GitHub Actions 会运行生成测试和结构检查，并提供示例 HTML 下载；不会向公众号发布内容。

若以后需要在线 Markdown 编辑器，可参考 [doocs/md](https://github.com/doocs/md) 的自定义主题与编辑功能。本仓库目前沿用 JSON → HTML 的制作方式，没有引入该项目依赖。
