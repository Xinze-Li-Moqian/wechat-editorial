#!/usr/bin/env python3
"""Check the portable copy region; this does not replace visual or WeChat testing."""
import argparse
import base64
import binascii
from html.parser import HTMLParser
from pathlib import Path

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

class ArticleCheck(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.article_depth = None
        self.articles = 0
        self.images = 0
        self.errors = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get('id') == 'article':
            self.articles += 1
            self.article_depth = len(self.stack)
        if self.article_depth is not None:
            if tag in {'script', 'style', 'math', 'annotation', 'button', 'iframe'}:
                self.errors.append(f'正文包含不适合复制的标签：{tag}')
            if 'href' in attrs:
                self.errors.append('正文包含 href 链接')
            if tag in {'p', 'h1', 'h2', 'section', 'img', 'table', 'pre'} and not attrs.get('style'):
                self.errors.append(f'{tag} 缺少内联样式')
            if tag == 'img':
                self.images += 1
                src = attrs.get('src', '')
                try:
                    header, encoded = src.split(',', 1)
                    if header not in {'data:image/png;base64', 'data:image/jpeg;base64'}:
                        raise ValueError('图片须内嵌为 PNG/JPEG')
                    data = base64.b64decode(encoded, validate=True)
                    signature = b'\x89PNG\r\n\x1a\n' if 'png' in header else b'\xff\xd8\xff'
                    if not data.startswith(signature):
                        raise ValueError('图片格式与内容不符')
                except (ValueError, binascii.Error) as exc:
                    self.errors.append(f'图片无效：{exc}')
                style = attrs.get('style', '').replace(' ', '')
                if 'width:100%' not in style or 'height:auto' not in style:
                    self.errors.append('图片缺少自适应宽高')
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f'标签闭合不匹配：{tag}')
            return
        self.stack.pop()
        if self.article_depth is not None and len(self.stack) == self.article_depth:
            self.article_depth = None

def check(source):
    parser = ArticleCheck()
    parser.feed(source)
    parser.close()
    if parser.articles != 1:
        parser.errors.append('必须恰有一个 #article 复制区')
    if parser.stack:
        parser.errors.append('存在未闭合标签')
    return parser

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('input', type=Path)
    args = ap.parse_args()
    try:
        result = check(args.input.read_text(encoding='utf-8'))
    except OSError as exc:
        ap.exit(1, f'读取失败：{exc}\n')
    if result.errors:
        ap.exit(1, '\n'.join(result.errors) + '\n')
    print(f'结构检查通过：1 个复制区，{result.images} 张内嵌图片。仍需视觉及公众号预览。')

if __name__ == '__main__':
    main()
