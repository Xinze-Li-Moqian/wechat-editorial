#!/usr/bin/env python3
"""Render an editable LaTeX math fragment as a mobile-sized numbered PNG."""
import argparse
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

def executable(override, name, fallback):
    value = override or shutil.which(name) or (fallback if Path(fallback).is_file() else None)
    if not value:
        raise ValueError(f'未找到 {name}；需要本地 TeX / Poppler，或指定工具路径')
    return value

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--number', type=int, required=True)
    parser.add_argument('--width-pt', type=int, default=210)
    parser.add_argument('--ink', default='253A63', help='公式字色，六位十六进制')
    parser.add_argument('--paper', default='F7F8FC', help='公式底色，六位十六进制')
    parser.add_argument('--pdflatex')
    parser.add_argument('--pdftoppm')
    args = parser.parse_args()
    try:
        if args.number < 1 or not 140 <= args.width_pt <= 300:
            raise ValueError('编号必须为正数；公式画布宽度应在 140–300pt 之间')
        if args.output.suffix.lower() != '.png':
            raise ValueError('输出扩展名必须为 .png')
        if not all(re.fullmatch(r'[0-9a-fA-F]{6}', x) for x in (args.ink, args.paper)):
            raise ValueError('字色与底色须为六位十六进制，例如 F7F8FC')
        latex = executable(args.pdflatex, 'pdflatex', '/Library/TeX/texbin/pdflatex')
        raster = executable(args.pdftoppm, 'pdftoppm', '/opt/homebrew/bin/pdftoppm')
        fragment = args.input.read_text(encoding='utf-8').strip()
        if not fragment or any(t in fragment for t in ('\\documentclass', '\\begin{document}', '\\tag')):
            raise ValueError('输入只需数学片段；不要包含文档环境或 tag 编号')
        source = r'''\documentclass[12pt,border=4pt]{standalone}
\usepackage{amsmath,amssymb,amscd,xcolor}
\definecolor{ink}{HTML}{INKHEX}
\definecolor{paper}{HTML}{PAPERHEX}
\begin{document}
\pagecolor{paper}\color{ink}
\begin{minipage}{WIDTHpt}
\begin{equation*}
FRAGMENT
\tag{NUMBER}
\end{equation*}
\end{minipage}
\end{document}
'''.replace('WIDTH',str(args.width_pt)).replace('INKHEX',args.ink).replace('PAPERHEX',args.paper).replace('NUMBER',str(args.number)).replace('FRAGMENT',fragment)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='formula-') as folder:
            path = Path(folder)
            (path / 'formula.tex').write_text(source, encoding='utf-8')
            run = subprocess.run([latex,'-no-shell-escape','-interaction=nonstopmode','-halt-on-error','formula.tex'],cwd=path,capture_output=True,text=True,timeout=60)
            log = (path / 'formula.log').read_text(errors='replace') if (path / 'formula.log').exists() else run.stdout
            if run.returncode:
                raise ValueError('LaTeX 编译失败：\n' + run.stdout[-2500:])
            if 'Overfull \\hbox' in log:
                raise ValueError('公式超宽：请用 aligned / gathered 合理分行，或小幅调整 --width-pt；不要缩小字号')
            subprocess.run([raster,'-r','300','-png','-singlefile',str(path/'formula.pdf'),str(path/'formula')],check=True,capture_output=True,timeout=60)
            shutil.copyfile(path/'formula.png',args.output)
        args.output.with_suffix('.render.tex').write_text(source, encoding='utf-8')
    except (ValueError,OSError,subprocess.SubprocessError) as exc:
        parser.exit(1,f'公式生成失败：{exc}\n')
    print(f'已生成：{args.output}')

if __name__ == '__main__':
    main()
