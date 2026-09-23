"""Assemble editable chapter drafts and generated tables into one TeX source."""
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
parts = ['preamble', 'foundations', 'gbm_theory', 'nonaffine_theory',
         'controls', 'code', 'results', 'closing']
text = '\n\n'.join((HERE / 'drafts' / (p+'.tex')).read_text() for p in parts)
text = re.sub(r'\\input\{(assets/[^}]+\.tex)\}',
              lambda m: (HERE / m.group(1)).read_text(), text)
out = HERE / 'Problem4_Chinese_Tutorial.tex'
out.write_text(text, encoding='utf-8')
print(out)
