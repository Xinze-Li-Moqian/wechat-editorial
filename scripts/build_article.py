#!/usr/bin/env python3
"""Build a self-contained WeChat copy page using only the Python standard library."""
import argparse
import base64
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def build(source, theme_path=None, template_path=None):
    data = json.loads(source.read_text(encoding='utf-8'))
    theme = json.loads((theme_path or ROOT / 'templates/theme.json').read_text(encoding='utf-8'))
    def esc(value):
        return html.escape(str(value), quote=True)
    def tag(name, content, style='', extra=''):
        return f'<{name} style="{esc(style)}"{extra}>{content}</{name}>'
    def image(src, formula=False, width=420):
        path = (source.parent / src).resolve()
        raw = path.read_bytes()
        if raw.startswith(b'\x89PNG\r\n\x1a\n'):
            mime = 'image/png'
        elif raw.startswith(b'\xff\xd8\xff'):
            mime = 'image/jpeg'
        else:
            raise ValueError(f'请使用 PNG 或 JPEG 图片：{path.name}')
        if formula and mime != 'image/png':
            raise ValueError('公式请使用 LaTeX 渲染的 PNG')
        style = 'display:block;width:100%;height:auto;margin:0 auto;'
        if formula:
            width = int(width)
            if not 200 <= width <= 790:
                raise ValueError('width_px 必须在 200–790 之间')
            style += f'max-width:{width}px;'
        return f'<img alt="" src="data:{mime};base64,{base64.b64encode(raw).decode()}" style="{style}">'
    def prose(block):
        if ('text' in block) == ('segments' in block):
            raise ValueError('段落需提供 text 或 segments，二选一')
        if 'text' in block:
            return esc(block['text']).replace('\n', '<br>')
        pieces = []
        for segment in block['segments']:
            value = esc(segment['text']).replace('\n', '<br>')
            if segment.get('bold'):
                value = tag('strong', value, theme['emphasis'])
            if segment.get('italic'):
                value = tag('em', value)
            if segment.get('superscript'):
                value = tag('sup', value, 'font-size:11px;color:#3F5CE6;')
            pieces.append(value)
        return ''.join(pieces)
    if not isinstance(data.get('title'), str) or not data['title'].strip():
        raise ValueError('需要文章标题')
    squares = ''.join(tag('span', '', f'display:inline-block;width:8px;height:8px;margin-right:6px;background:{color};') for color in ('#3F5CE6','#A995F4','#F0A34C'))
    header = tag('p', squares, 'margin:0;padding:0;line-height:8px;', ' aria-hidden="true"')
    header += tag('h1', esc(data['title']), theme['title'])
    for field in ('subtitle', 'byline'):
        if data.get(field):
            header += tag('p', esc(data[field]), theme[field])
    content = tag('section', header, theme['title_panel'])
    if data.get('cover'):
        content += tag('p', image(data['cover']), 'margin:22px 0 30px;padding:0;line-height:0;')
    else:
        content += '<section style="height:28px;"></section>'
    body = []
    equation = 0
    for block in data.get('blocks', []):
        kind = block['type']
        if kind == 'paragraph':
            body.append(tag('p', prose(block), theme['paragraph']))
        elif kind == 'heading':
            square = tag('span', '', 'display:inline-block;width:9px;height:9px;margin-right:10px;background:#3F5CE6;vertical-align:middle;', ' aria-hidden="true"')
            body.append(tag('h2', square + prose(block), theme['heading']))
        elif kind == 'code':
            caption = tag('p', esc(block['caption']), theme['code_caption']) if block.get('caption') else ''
            code = tag('pre', tag('code', esc(block['text']), theme['code']), theme['code'])
            body.append(tag('section', caption + code, theme['code_panel']))
        elif kind == 'table':
            headers, rows = block['headers'], block['rows']
            if not headers or any(len(row) != len(headers) for row in rows):
                raise ValueError('表格应有列标题，且每行与标题列数相同')
            def cell(value, header=False):
                style = theme['table_cell'] + (theme['table_header'] if header else '')
                return tag('th' if header else 'td', esc(value).replace('\n', '<br>'), style,
                           ' scope="col"' if header else '')
            head = '<thead><tr>' + ''.join(cell(x, True) for x in headers) + '</tr></thead>'
            rows_html = ''.join('<tr>' + ''.join(cell(x) for x in row) + '</tr>' for row in rows)
            body.append(tag('table', head + '<tbody>' + rows_html + '</tbody>', theme['table']))
        elif kind in ('image', 'formula'):
            if kind == 'formula':
                equation += 1
                if block.get('number') != equation:
                    raise ValueError(f'公式编号应依次排列；此处应为 {equation}，编号须在 PNG 中渲染')
            figure = image(block['src'], kind == 'formula', block.get('width_px',420))
            if block.get('caption'):
                figure += tag('p', esc(block['caption']), theme['caption'])
            body.append(tag('section', figure, 'margin:30px 0;padding:0;text-align:center;'))
        else:
            raise ValueError(f'未知正文块：{kind}')
    if data.get('sources'):
        notes = [tag('p', '资料来源', 'margin:0 0 10px;font-size:13px;font-weight:700;color:#64707F;')]
        for source_item in data['sources']:
            label = ' · '.join(str(source_item[k]) for k in ('publisher','title','date') if source_item.get(k))
            notes.append(tag('p', esc(label), 'margin:0 0 8px;font-size:12px;line-height:1.8;color:#64707F;word-break:break-word;'))
        body.append(tag('section', ''.join(notes), 'margin:36px 0 0;padding:20px 0 0;border-top:1px solid #D8DFEA;'))
    content += tag('section', ''.join(body), theme['body'])
    article = tag('section', content, theme['article'], ' id="article" lang="zh-CN"')
    template = (template_path or ROOT / 'templates/page.html').read_text(encoding='utf-8')
    return template.replace('{{TITLE}}', esc(data['title'])).replace('{{ARTICLE}}', article)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--theme', type=Path, help='可选主题 JSON；默认 templates/theme.json')
    parser.add_argument('--template', type=Path, help='可选页面模板；默认 templates/page.html')
    args = parser.parse_args()
    try:
        result = build(args.input.resolve(), args.theme, args.template)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding='utf-8')
    except (ValueError, KeyError, OSError, TypeError) as exc:
        parser.exit(1, f'生成失败：{exc}\n')
    print(f'已生成：{args.output}（{len(result.encode()):,} bytes）')

if __name__ == '__main__':
    main()
