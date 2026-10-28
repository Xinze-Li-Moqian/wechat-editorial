import base64
import importlib.util
import json
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / (name + '.py'))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

builder, checker = module('build_article'), module('check_article')

class Extract(HTMLParser):
    def __init__(self):
        super().__init__(); self.images = []; self.pre = False; self.code = ''
    def handle_starttag(self, tag, attrs):
        if tag == 'img': self.images.append(dict(attrs))
        if tag == 'pre': self.pre = True
    def handle_endtag(self, tag):
        if tag == 'pre': self.pre = False
    def handle_data(self, data):
        if self.pre: self.code += data

class BuildTests(unittest.TestCase):
    def build_input(self, data, theme=None):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'article.json'
            source.write_text(json.dumps(data), encoding='utf-8')
            return builder.build(source, theme)

    def test_example_is_portable_and_embeds_exact_images(self):
        result = builder.build(ROOT / 'examples/article.json')
        self.assertEqual(checker.check(result).errors, [])
        parsed = Extract(); parsed.feed(result)
        self.assertEqual(len(parsed.images), 2)
        expected = ['illustration.jpg', 'equation.png']
        for image, name in zip(parsed.images, expected):
            self.assertEqual(base64.b64decode(image['src'].split(',')[1]),
                             (ROOT / 'examples/assets' / name).read_bytes())
        self.assertNotIn(str(ROOT), result)
        self.assertNotIn('gNg^{-1}', result)

    def test_text_and_code_are_escaped_without_losing_code(self):
        code = '<script>alert("test")</script>\n  x & y'
        result = self.build_input({'title': 'Example <title>', 'blocks': [
            {'type': 'paragraph', 'text': '<img src=x onerror=alert(1)>'},
            {'type': 'code', 'text': code}]})
        parsed = Extract(); parsed.feed(result)
        self.assertEqual(parsed.code, code)
        self.assertEqual(parsed.images, [])
        self.assertIn('&lt;img', result)
        self.assertEqual(checker.check(result).errors, [])

    def test_invalid_formula_sequence_fails(self):
        with self.assertRaisesRegex(ValueError, '公式编号'):
            self.build_input({'title': 'Example', 'blocks': [
                {'type': 'formula', 'number': 2, 'src': 'missing.png'}]})

    def test_invalid_table_fails(self):
        with self.assertRaisesRegex(ValueError, '列数'):
            self.build_input({'title': 'Example', 'blocks': [
                {'type': 'table', 'headers': ['A', 'B'], 'rows': [['one']]}]})

    def test_alternative_theme_changes_rendered_output(self):
        theme = json.loads((ROOT / 'templates/theme.json').read_text())
        theme['paragraph'] = 'font-size:23px;color:#123456;'
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'theme.json'
            path.write_text(json.dumps(theme))
            result = self.build_input({'title': 'Example', 'blocks': [
                {'type': 'paragraph', 'text': '正文'}]}, path)
        self.assertIn('font-size:23px;color:#123456;', result)

    def test_checker_rejects_external_images_and_links(self):
        result = checker.check('<section id="article" style="margin:0">'
            '<a href="https://example.com">link</a>'
            '<img src="file:///missing.png" style="width:100%;height:auto;"></section>')
        self.assertTrue(any('href' in e for e in result.errors))
        self.assertTrue(any('图片无效' in e for e in result.errors))

if __name__ == '__main__':
    unittest.main()
