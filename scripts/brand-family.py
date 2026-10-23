"""Familia de marca vectorial: una geometría y proporciones compartidas."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
import subprocess, shutil, zipfile, html

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'public/assets/brand'
KIT = ROOT / 'brand-kit'
KIT.mkdir(parents=True, exist_ok=True)
FONT = ROOT / 'public/assets/fonts/plus-jakarta.ttf'
fonts = {}
def letters(text, x, y, size, weight=800, spacing=-2.4):
    if weight not in fonts:
        f = instantiateVariableFont(TTFont(FONT), {'wght': weight}, inplace=True)
        fonts[weight] = (f.getGlyphSet(), f.getBestCmap(), f['head'].unitsPerEm)
    glyphs, cmap, units = fonts[weight]; scale=size/units; paths=[]
    for ch in text:
        glyph=glyphs[cmap[ord(ch)]]; pen=SVGPathPen(glyphs); glyph.draw(pen)
        paths.append(f'<path transform="translate({x:.3f} {y}) scale({scale:.6f} {-scale:.6f})" d="{pen.getCommands()}"/>')
        x += glyph.width*scale+spacing
    return ''.join(paths), x-spacing

BOWL = '<path d="M0 25V0h28c16 0 26 9 26 23S44 46 28 46H20l13-13c5-1 8-5 8-10 0-7-5-11-13-11H13L0 25Z"/>'
STEM = '<path d="m0 36 13-13v36L0 72V36Z"/>'
word, word_end = letters('pary', 0, 47, 64)
# El descriptor comparte centro óptico con el nombre; el espaciado es fijo en toda la familia.
studio, studio_end = letters('STUDIO', word_end+20, 42, 16, 650, 2.3)

def symbol(ink, accent):
    return f'<g fill="{accent}">{BOWL}</g><g fill="{ink}">{STEM}</g>'

def composition(kind, ink, accent):
    mark=symbol(ink,accent); words=f'<g fill="{ink}">{word}</g>'; descriptor=f'<g fill="{ink}">{studio}</g>'
    if kind=='isotipo': return 78,96,f'<g transform="translate(12 12)">{mark}</g>'
    if kind=='pary': return word_end+24,96,f'<g transform="translate(12 12)">{words}</g>'
    if kind=='pary-studio': return studio_end+24,96,f'<g transform="translate(12 12)">{words}{descriptor}</g>'
    if kind=='firma-pary': return word_end+106,96,f'<g transform="translate(12 12)">{mark}<g transform="translate(82 0)">{words}</g></g>'
    if kind=='firma-pary-studio': return studio_end+106,96,f'<g transform="translate(12 12)">{mark}<g transform="translate(82 0)">{words}{descriptor}</g></g>'
    if kind=='firma-vertical':
        # Alternativa compacta: símbolo, nombre y descriptor sobre un mismo eje.
        desc, dw=letters('STUDIO',0,0,15,650,3)
        width=word_end+40
        return width,208,f'<g transform="translate({(width-54)/2} 12)">{mark}</g><g fill="{ink}" transform="translate(20 99)">{word}</g><g fill="{ink}" transform="translate({(width-dw)/2} 190)">{desc}</g>'
    raise ValueError(kind)

def svg(w,h,body,title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.3f}" height="{h}" viewBox="0 0 {w:.3f} {h}"><title>{html.escape(title)}</title>{body}</svg>'

palettes={'color':('#142f2a','#146451'),'inversa':('#ffffff','#b8e6c9'),'negra':('#000000','#000000'),'blanca':('#ffffff','#ffffff')}
kinds=['isotipo','pary','pary-studio','firma-pary','firma-pary-studio','firma-vertical']
for kind in kinds:
    for variant,(ink,accent) in palettes.items():
        w,h,body=composition(kind,ink,accent)
        name=f'{kind}-{variant}'
        (KIT/f'{name}.svg').write_text(svg(w,h,body,f'Pary Studio · {kind} · {variant}'))
        subprocess.run(['magick','-background','none',str(KIT/f'{name}.svg'),'-resize','2400x1600',str(KIT/f'{name}.png')],check=True,stdout=subprocess.DEVNULL)

# Compatibilidad con las aplicaciones existentes: todas usan los mismos maestros.
for target,source in {'logo':'firma-pary-studio-color','logo-white':'firma-pary-studio-inversa','logo-black':'firma-pary-studio-negra','symbol':'isotipo-color','symbol-white':'isotipo-inversa','symbol-black':'isotipo-negra','wordmark':'pary-studio-color','pary':'pary-color','pary-logo':'firma-pary-color'}.items():
    for ext in ['svg','png']:
        shutil.copyfile(KIT/f'{source}.{ext}',OUT/f'{target}.{ext}')

# Lámina autónoma en SVG con tipografía trazada, apta para compartir.
parts=['<rect width="1600" height="1500" fill="#f6f5ef"/>']
def text(value,x,y,size,color='#142f2a',weight=650,spacing=-.4):
    body,_=letters(value,x,y,size,weight,spacing);parts.append(f'<g fill="{color}">{body}</g>')
def place(kind,x,y,maxw,maxh,variant='color'):
    w,h,body=composition(kind,*palettes[variant]);scale=min(maxw/w,maxh/h)
    parts.append(f'<g transform="translate({x+(maxw-w*scale)/2:.2f} {y+(maxh-h*scale)/2:.2f}) scale({scale:.4f})">{body}</g>')
text('PARY / SISTEMA DE IDENTIDAD',72,75,16,weight=650,spacing=2)
text('Una identidad. Distintas formas de firmar.',72,141,43,weight=750)
text('Misma P, mismo trazo, misma voz.',72,188,21,'#4f625b',500)
for x,y,w,h in [(72,234,400,306),(496,234,1032,306),(72,564,716,340),(812,564,716,340)]:
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="#ffffff" stroke="#d9e1d8"/>')
text('01 / ISOTIPO',100,273,13,spacing=1.5);place('isotipo',122,294,300,210)
text('02 / LOGOTIPOS',528,273,13,spacing=1.5);place('pary',552,293,310,200);place('pary-studio',900,293,574,200)
text('03 / FIRMA PARY',100,606,13,spacing=1.5);place('firma-pary',112,640,636,210)
text('04 / FIRMA PARY STUDIO',840,606,13,spacing=1.5);place('firma-pary-studio',852,640,636,210)
parts.append('<rect x="72" y="928" width="1456" height="310" rx="20" fill="#142f2a"/>')
text('UNA MARCA QUE FUNCIONA EN CLARO Y OSCURO',104,975,13,'#b8e6c9',650,1.5)
place('firma-pary-studio',112,1010,820,180,'inversa');place('isotipo',1032,1000,160,200,'blanca');place('pary',1220,1010,250,180,'blanca')
colors=[('Petróleo','#146451'),('Profundo','#142f2a'),('Marfil','#f6f5ef'),('Menta','#b8e6c9')]
for i,(label,color) in enumerate(colors):
    x=72+i*370;parts.append(f'<rect x="{x}" y="1270" width="346" height="70" rx="12" fill="{color}" stroke="#d9e1d8"/>')
    text(label,x,1373,17,weight=650);text(color.upper(),x,1403,14,'#4f625b',500,1)
text('Pary Studio · Geometría vectorial · Versiones a color, inversas y monocromáticas',72,1460,16,'#4f625b',500)
board=svg(1600,1500,''.join(parts),'Pary Studio · Sistema de identidad unificado')
(KIT/'sistema-de-marca.svg').write_text(board)
subprocess.run(['magick','-background','none',str(KIT/'sistema-de-marca.svg'),str(KIT/'sistema-de-marca.png')],check=True)
readme='''# Pary · Sistema de identidad

La P Conexión conserva sus dos trazos y el corte diagonal. El nombre usa minúsculas como decisión visual; en texto se escribe Pary o Pary Studio.

- isotipo: P para avatar, favicon y espacios reducidos.
- pary: logotipo sin símbolo ni descriptor.
- pary-studio: logotipo con descriptor alineado al centro óptico.
- firma-pary: símbolo y nombre.
- firma-pary-studio: firma principal, para web y documentos.
- firma-vertical: alternativa para espacios cuadrados.

Cada composición incluye color, inversa, negra y blanca. Los SVG están trazados y no requieren fuentes instaladas. Los PNG tienen fondo transparente. La lámina sistema-de-marca es una presentación sobre marfil.

Proporciones: símbolo de 54 × 72 unidades, distancia de 28 unidades hasta el nombre; descriptor a 20 unidades del nombre. Mantener un área libre exterior de al menos 13 unidades (ancho del asta del símbolo). No deformar, recolorear por partes, añadir sombras ni cambiar la separación.

Tamaños mínimos recomendados: isotipo 24 px de alto; firma Pary 140 px de ancho; firma Pary Studio 240 px de ancho. Debajo de ese tamaño, preferir la firma Pary o el isotipo para conservar legibilidad. En impresión, verificar una prueba al tamaño final.

Tipografía: Plus Jakarta Sans (licencia SIL OFL en la carpeta de fuentes del proyecto). Paleta: #146451, #142F2A, #F6F5EF y #B8E6C9.
'''
(KIT/'LEEME.md').write_text(readme)
with zipfile.ZipFile(ROOT/'pary-identidad.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(KIT.iterdir()):z.write(p,'pary-identidad/'+p.name)
print('Familia unificada: 6 composiciones × 4 versiones, SVG + PNG; lámina y ZIP.')
