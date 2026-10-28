# 稿件输入格式

输入 UTF-8 JSON，基本示例见 `examples/article.json`。所有图片路径相对 JSON 文件所在目录。必须有非空 `title`；`subtitle`、`byline`、`cover`、`sources` 均可省略。

`blocks` 支持以下组件：

```json
[
  {"type": "paragraph", "text": "正文。"},
  {"type": "heading", "text": "小标题"},
  {"type": "paragraph", "segments": [
    {"text": "普通文字"},
    {"text": "重点", "bold": true},
    {"text": "[1]", "superscript": true}
  ]},
  {"type": "image", "src": "figure.jpg", "caption": "图片说明。"},
  {"type": "formula", "src": "eq1.png", "number": 1,
   "latex": "gNg^{-1}=N", "width_px": 420},
  {"type": "code", "caption": "文件名与行号", "text": "example (n : Nat) : n + 0 = n := by\n  rfl"},
  {"type": "table", "headers": ["项目", "说明"], "rows": [["A", "内容"], ["B", "内容"]]}
]
```

- 段落和小标题可用 `text` 或 `segments`，二选一。segments 支持 `bold`、`italic`、`superscript`。
- 所有文本自动转义，输入中的 HTML 不会被执行。代码保留换行、缩进；长行在窄屏换行。
- 普通图片支持 PNG/JPEG。公式只接受 PNG，按文中次序编号 1、2、3……，PNG 内的编号须与 JSON 一致。
- 公式 `latex` 仅供工作稿记录，不写入发布 HTML；`width_px` 默认为 420，范围 200–790，实际宽度不超过容器。
- 表格必须有列标题，每行列数相同；单元格内 `\n` 可换行。
- sources 形如 `{"title":"[1] 资料名称", "publisher":"机构", "date":"2026-10-28", "url":"https://example.com"}`。生成器显示 publisher / title / date；URL 留在输入中供核查。

主题文件是组件名到内联 CSS 的映射。用 `--theme templates/my-theme.json` 可试验另一套完整主题；不要将主生成器与示例文件绑定到某台电脑的绝对路径。
