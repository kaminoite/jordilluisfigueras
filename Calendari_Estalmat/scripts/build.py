#!/usr/bin/env python3
"""Genera les dades JavaScript i la versió autocontinguda (només biblioteca estàndard)."""
from pathlib import Path
import base64
import json
import mimetypes
import re

ROOT = Path(__file__).resolve().parents[1]


def data_uri(path):
    """Converteix un recurs local en una URL de dades per a l’HTML autònom."""
    mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def build():
    problems = json.loads((ROOT / 'data/problemes.json').read_text(encoding='utf-8'))
    diagrams = {p.stem: p.read_text(encoding='utf-8')
                for p in sorted((ROOT / 'assets/figures').glob('*.svg'))}
    # Els pictogrames s’incrusten perquè també funcionin sense connexió.
    for image in sorted((ROOT / 'assets/figures').glob('*.png')):
        diagrams[image.stem] = '<img src="' + data_uri(image) + '" alt="Llama" style="width:180px;max-width:100%;height:auto">'
    generated = '// GENERAT per scripts/build.py. Editeu els fitxers font, no aquest fitxer.\n'
    for name, values, destination in [
        ('problems', problems, 'data/problemes.js'),
        ('diagrams', diagrams, 'js/diagrames.js'),
    ]:
        code = generated + f'const {name} = ' + json.dumps(values, ensure_ascii=False, indent=2) + ';\n'
        (ROOT / destination).write_text(code, encoding='utf-8')

    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    css = (ROOT / 'css/estils.css').read_text(encoding='utf-8')
    css = re.sub(r"url\(['\"]?(\.\./[^)'\"]+)['\"]?\)",
                 lambda m: 'url("' + data_uri((ROOT / 'css' / m[1]).resolve()) + '")', css)
    html = html.replace('<link rel="stylesheet" href="css/estils.css">', '<style>\n' + css + '\n</style>')
    scripts = re.findall(r'<script defer src="([^"]+)"></script>', html)
    html = re.sub(r'  <script defer src="[^"]+"></script>\n', '', html)
    # Els scripts en línia es col·loquen al final perquè el DOM ja existeixi.
    inline = '\n'.join('<script>\n' + (ROOT / path).read_text(encoding='utf-8').replace('</script', '<\\/script') + '\n</script>' for path in scripts)
    html = html.replace('</body>', inline + '\n</body>')
    html = re.sub(r'src="(assets/[^"]+)"', lambda m: 'src="' + data_uri(ROOT / m[1]) + '"', html)
    html = html.replace('  <!-- Scripts clàssics: el projecte també funciona obrint index.html directament. -->\n', '')
    (ROOT / 'dist').mkdir(exist_ok=True)
    target = ROOT / 'dist/Calendari_Estalmat.html'
    target.write_text(html, encoding='utf-8')
    print(f'Generat: {target.name} ({target.stat().st_size:,} bytes)')


if __name__ == '__main__':
    build()
