"""Identidad Pary: la P distintiva es la primera letra del nombre completo."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
import html
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'public/assets/brand'
KIT = ROOT / 'brand-kit'
KIT.mkdir(parents=True, exist_ok=True)
FONT = ROOT / 'public/assets/fonts/plus-jakarta.ttf'
fonts = {}


def letters(text, x, y, size, weight=650, spacing=0):
    if weight not in fonts:
        f = instantiateVariableFont(TTFont(FONT), {'wght': weight}, inplace=True)
        fonts[weight] = (f.getGlyphSet(), f.getBestCmap(), f['head'].unitsPerEm)
    glyphs, cmap, units = fonts[weight]
    scale = size / units
    paths = []
    for ch in text:
        glyph = glyphs[cmap[ord(ch)]]
        pen = SVGPathPen(glyphs)
        glyph.draw(pen)
        paths.append(f'<path transform="translate({x:.3f} {y}) scale({scale:.6f} {-scale:.6f})" d="{pen.getCommands()}"/>')
        x += glyph.width * scale + spacing
    return ''.join(paths), x - spacing


# P Conexión: curva y corte diagonal. Esta geometría se usa una sola vez en el nombre.
BOWL = '<path d="M0 25V0h28c16 0 26 9 26 23S44 46 28 46H20l13-13c5-1 8-5 8-10 0-7-5-11-13-11H13L0 25Z"/>'
STEM = '<path d="m0 36 13-13v36L0 72V36Z"/>'
# Letras dibujadas para la P, no un nombre tipográfico colocado después del isotipo.
# Altura de x 50, línea base 72; a con curva abierta, r compacta, y con remate diagonal.
A = '<path fill-rule="evenodd" d="M94 22H105V72H94V66C90 71 85 73 79 73C65 73 57 62 57 47S65 21 79 21C85 21 90 24 94 29V22ZM81 32C73 32 69 38 69 47S73 62 81 62C89 62 94 56 94 47S89 32 81 32Z"/>'
R = '<path d="M114 72V22H126V30C131 23 137 21 146 22V34H141C131 34 126 40 126 51V72Z"/>'
Y = '<path d="M150 22H163L177 55L190 22H203L174 90H161L170 69Z"/>'
ARY = A + R + Y
# Studio comparte línea base y utiliza caja mixta para pertenecer al mismo nombre.
STUDIO, FULL_END = letters('Studio', 218, 72, 90, 750, -2)
# Compensación óptica: el corte y la forma estrecha de la P reducen su presencia.
P_SCALE = 1.15
P_EXTRA_X = 54 * (P_SCALE - 1)
P_EXTRA_Y = 72 * (P_SCALE - 1)


def symbol(ink, accent):
    return f'<g fill="{accent}">{BOWL}</g><g fill="{ink}">{STEM}</g>'


def wordmark(ink, accent, full=True):
    return f'<g transform="scale({P_SCALE})">{symbol(ink, accent)}</g><g transform="translate({P_EXTRA_X} {P_EXTRA_Y})" fill="{ink}">{ARY}{STUDIO if full else ""}</g>'


def composition(kind, ink, accent):
    if kind == 'isotipo':
        return 88, 88, f'<g transform="translate(17 8)">{symbol(ink, accent)}</g>'
    if kind in ('pary', 'firma-pary'):
        return 219 + P_EXTRA_X, 106 + P_EXTRA_Y, f'<g transform="translate(8 8)">{wordmark(ink, accent, False)}</g>'
    if kind in ('pary-studio', 'firma-pary-studio'):
        return FULL_END + 16 + P_EXTRA_X, 106 + P_EXTRA_Y, f'<g transform="translate(8 8)">{wordmark(ink, accent)}</g>'
    if kind == 'firma-vertical':
        desc, _ = letters('Studio', 0, 162 + P_EXTRA_Y, 90, 750, -2)
        return FULL_END - 202, 180 + P_EXTRA_Y, f'<g transform="translate(8 8)">{wordmark(ink, accent, False)}<g fill="{ink}">{desc}</g></g>'
    raise ValueError(kind)


def svg(w, h, body, title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}" height="{h}" viewBox="0 0 {w:.3f} {h}"><title>{html.escape(title)}</title>{body}</svg>'


def raster(source, target, size='2400x1600'):
    subprocess.run(['magick', '-background', 'none', str(source), '-resize', size, str(target)], check=True, stdout=subprocess.DEVNULL)


palettes = {'color': ('#142f2a', '#146451'), 'inversa': ('#ffffff', '#b8e6c9'), 'negra': ('#000000', '#000000'), 'blanca': ('#ffffff', '#ffffff')}
kinds = ['isotipo', 'pary', 'pary-studio', 'firma-pary', 'firma-pary-studio', 'firma-vertical']
for kind in kinds:
    for variant, (ink, accent) in palettes.items():
        w, h, body = composition(kind, ink, accent)
        name = f'{kind}-{variant}'
        source = KIT / f'{name}.svg'
        source.write_text(svg(w, h, body, f'Pary Studio · {kind} · {variant}'))
        raster(source, KIT / f'{name}.png')

# Los alias históricos apuntan al mismo logotipo integrado, nunca a una P duplicada.
aliases = {'logo': 'pary-studio-color', 'logo-white': 'pary-studio-inversa', 'logo-black': 'pary-studio-negra', 'symbol': 'isotipo-color', 'symbol-white': 'isotipo-inversa', 'symbol-black': 'isotipo-negra', 'wordmark': 'pary-studio-color', 'pary': 'pary-color', 'pary-logo': 'pary-color'}
for target, source in aliases.items():
    for ext in ('svg', 'png'):
        shutil.copyfile(KIT / f'{source}.{ext}', OUT / f'{target}.{ext}')

# Lámina de presentación. La composición principal se muestra con una sola P.
parts = ['<rect width="1600" height="1540" fill="#f6f5ef"/>']


def text(value, x, y, size, color='#142f2a', weight=650, spacing=-.4):
    body, _ = letters(value, x, y, size, weight, spacing)
    parts.append(f'<g fill="{color}">{body}</g>')


def place(kind, x, y, maxw, maxh, variant='color'):
    w, h, body = composition(kind, *palettes[variant])
    scale = min(maxw / w, maxh / h)
    parts.append(f'<g transform="translate({x + (maxw-w*scale)/2:.2f} {y + (maxh-h*scale)/2:.2f}) scale({scale:.4f})">{body}</g>')


def panel(x, y, w, h, fill='#ffffff'):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="22" fill="{fill}"/>')


text('PARY STUDIO / IDENTIDAD INTEGRADA', 72, 76, 15, spacing=1.7)
text('La P es parte del nombre.', 72, 143, 46, weight=750)
text('Un lettering propio. Un símbolo que nace de la misma palabra.', 72, 188, 21, '#4f625b', 500)
panel(72, 234, 1456, 346)
text('01 / LOGOTIPO PRINCIPAL', 108, 278, 13, spacing=1.5)
place('pary-studio', 180, 314, 1240, 212)
panel(72, 604, 424, 336)
panel(520, 604, 1008, 336)
text('02 / ISOTIPO', 108, 650, 13, spacing=1.5)
place('isotipo', 182, 690, 204, 204)
text('03 / VERSIÓN CORTA', 556, 650, 13, spacing=1.5)
place('pary', 714, 680, 620, 218)
panel(72, 964, 1456, 300, '#142f2a')
text('04 / SOBRE FONDO OSCURO', 108, 1010, 13, '#b8e6c9', 650, 1.5)
place('pary-studio', 156, 1052, 1288, 172, 'inversa')
text('UNA MISMA GEOMETRÍA', 72, 1315, 13, spacing=1.5)
text('P integrada al nombre · Curvas y diagonales compartidas · Versiones a una tinta', 72, 1354, 20, '#4f625b', 500)
for i, (label, color) in enumerate([('Petróleo', '#146451'), ('Profundo', '#142f2a'), ('Marfil', '#f6f5ef'), ('Menta', '#b8e6c9')]):
    x = 72 + i * 370
    parts.append(f'<rect x="{x}" y="1390" width="346" height="52" rx="10" fill="{color}" stroke="#d9e1d8"/>')
    text(label, x, 1475, 16)
    text(color.upper(), x, 1500, 13, '#4f625b', 500, 1)
board = svg(1600, 1540, ''.join(parts), 'Pary Studio · La P integrada al nombre')
(KIT / 'sistema-de-marca.svg').write_text(board)
raster(KIT / 'sistema-de-marca.svg', KIT / 'sistema-de-marca.png', '1600x1540')

# Vista para revisar el uso real a tamaños pequeños; no sustituye los originales.
parts = ['<rect width="1600" height="900" fill="#f6f5ef"/>']
text('PARY STUDIO / PRUEBAS DE USO', 72, 72, 15, spacing=1.7)
panel(72, 115, 1456, 130)
place('pary-studio', 108, 141, 260, 70)
text('Servicios', 765, 190, 19, weight=600)
text('Proyectos', 910, 190, 19, weight=600)
text('El estudio', 1060, 190, 19, weight=600)
panel(1260, 147, 230, 62, '#146451')
text('Hablemos', 1314, 188, 19, '#ffffff', 650)
text('Cabecera de escritorio', 72, 282, 17, '#4f625b', 500)
panel(72, 332, 430, 260)
place('pary-studio', 96, 368, 188, 52)
text('Hablemos', 346, 402, 15, weight=600)
text('Software sólido.', 96, 481, 33, weight=750)
text('Para lo que viene.', 96, 527, 33, '#146451', 750)
text('Cabecera móvil', 72, 631, 17, '#4f625b', 500)
panel(530, 332, 998, 260)
text('ISOTIPO / TAMAÑO REAL', 566, 378, 12, spacing=1.5)
for i, size in enumerate((16, 24, 32, 48, 64)):
    x = 585 + i * 175
    place('isotipo', x, 450, size, size)
    text(f'{size} px', x, 552, 14, '#4f625b', 500)
text('La forma debe funcionar también sin color.', 72, 725, 30, weight=700)
place('pary-studio', 64, 754, 340, 90, 'negra')
panel(850, 700, 678, 155, '#142f2a')
place('pary-studio', 890, 725, 598, 104, 'blanca')
(KIT / 'pruebas-de-uso.svg').write_text(svg(1600, 900, ''.join(parts), 'Pary Studio · Pruebas de uso y reducción'))
raster(KIT / 'pruebas-de-uso.svg', KIT / 'pruebas-de-uso.png', '1600x900')

# La pieza de redes comparte el mismo maestro; evita conservar la firma anterior.
parts = ['<rect width="1200" height="630" fill="#142f2a"/>']
place('pary-studio', 62, 50, 510, 135, 'inversa')
text('Software sólido.', 72, 314, 66, '#ffffff', 750)
text('Para lo que viene.', 72, 395, 66, '#b8e6c9', 750)
text('Ecommerce y sistemas comerciales', 76, 512, 24, '#ffffff', 500)
text('parystudio.com', 76, 566, 19, '#b8e6c9', 500)
(OUT / 'social-card.svg').write_text(svg(1200, 630, ''.join(parts), 'Pary Studio · Software sólido. Para lo que viene.'))
raster(OUT / 'social-card.svg', OUT / 'social-card.png', '1200x630')

(KIT / 'LEEME.md').write_text('''# Pary Studio · Identidad integrada

La P Conexión es la primera letra del nombre. Pary se dibuja como una sola palabra: la P distintiva seguida de las letras a, r, y construidas para ella. Studio comparte línea base y usa caja mixta.

## Composiciones

- `pary-studio`: logotipo principal completo, con una sola P.
- `pary`: versión corta del mismo lettering.
- `isotipo`: la misma P extraída del nombre; avatar y favicon.
- `firma-vertical`: Pary sobre Studio, sin añadir un símbolo encima.
- `firma-pary` y `firma-pary-studio`: alias de compatibilidad de las versiones anteriores; contienen los logotipos integrados.

Cada composición incluye color, inversa, negra y blanca. SVG vectoriales trazados y PNG transparentes. La lámina y las pruebas de uso son presentaciones; no usarlas como originales del logo.

## Construcción y uso

P base de 54 × 72 unidades, ampliada un 15 % en el logotipo para compensar su corte diagonal. Conserva la geometría del isotipo y alinea su base con el nombre; el resto de las letras mantiene una altura de x de 50. El corte de la P y el remate de la y aportan la diagonal característica; la a y la P comparten curvas de grosor próximo. La distancia entre letras se decide ópticamente y no se modifica al colocar el logo.

Área libre mínima: 13 unidades, equivalentes al asta de la P, alrededor de la silueta visible. El margen del archivo no reemplaza esta reserva en cada aplicación. Tamaños de partida: logotipo completo 160 px de ancho, Pary 80 px, isotipo 16 px. Revisar el soporte final; usar el símbolo para favicon. No estirar, añadir otra P, recolorear letras por separado ni aplicar sombras o contornos.

El lettering de Pary es vectorial propio. Studio y los textos de presentación se basan en Plus Jakarta Sans (SIL OFL en la carpeta de fuentes). No requieren fuentes instaladas para reproducir los SVG. La tipografía de lectura del sitio conserva Plus Jakarta Sans.

Paleta: petróleo #146451, profundo #142F2A, marfil #F6F5EF y menta #B8E6C9. La silueta se mantiene en las versiones de una tinta.

La revisión de legibilidad y aplicaciones no constituye una búsqueda de registro o disponibilidad marcaria.
''')
with zipfile.ZipFile(ROOT / 'pary-identidad.zip', 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(KIT.iterdir()):
        z.write(p, 'pary-identidad/' + p.name)
print(f'Identidad integrada: ancho del logotipo {FULL_END + 16 + P_EXTRA_X:.2f}; SVG, PNG, aplicaciones y ZIP generados.')
