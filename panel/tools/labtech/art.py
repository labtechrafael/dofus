"""Arte do mundo LabTech: icones de itens (a partir da arte do Antigravity em panel/world/labtech/art)
e a ilha desenhada no mapa-mundi. Qualquer PNG com o mesmo nome em art/ substitui o gerado."""
import colorsys
import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

ART = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'world', 'labtech', 'art'))
OUT = os.path.join(ART, 'gerado')

# Cores dos 12 nucleos (uma por classe, na ordem Feca..Pandawa)
CORE_COLORS = [(90, 170, 255), (80, 200, 90), (230, 190, 40), (140, 70, 200), (60, 80, 220), (240, 120, 30),
               (240, 90, 170), (220, 40, 40), (120, 220, 80), (40, 170, 90), (180, 20, 60), (60, 210, 220)]


def _fit(img, size=96):
    img = img.copy()
    img.thumbnail((size, size), Image.LANCZOS)
    return img


def load(name):
    """PNG do usuario (art/<name>.png) ou None."""
    p = os.path.join(ART, name + '.png')
    return Image.open(p).convert('RGBA') if os.path.exists(p) else None


def core_icon(i):
    s = 96
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    r, g, b = CORE_COLORS[i]
    # moldura de bronze com parafusos
    d.ellipse((6, 6, s - 6, s - 6), fill=(120, 72, 30, 255), outline=(60, 34, 12, 255), width=3)
    d.ellipse((16, 16, s - 16, s - 16), fill=(r // 3, g // 3, b // 3, 255))
    for k in range(6, 0, -1):  # brilho do nucleo
        f = k / 6
        c = (int(r + (255 - r) * (1 - f) * 0.6), int(g + (255 - g) * (1 - f) * 0.6), int(b + (255 - b) * (1 - f) * 0.6), 255)
        m = 18 + (6 - k) * 3
        d.ellipse((m, m, s - m, s - m), fill=c)
    d.ellipse((34, 28, 46, 40), fill=(255, 255, 255, 220))
    for a in range(0, 360, 60):
        x, y = s / 2 + math.cos(math.radians(a)) * 40, s / 2 + math.sin(math.radians(a)) * 40
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(210, 170, 90, 255))
    return img


def dofus_icon():
    s = 96
    img = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # ovo ambar (cerveja) com espuma no topo e 12 pontinhos coloridos
    d.ellipse((18, 12, 78, 90), fill=(214, 140, 30, 255), outline=(110, 60, 10, 255), width=3)
    d.ellipse((28, 22, 50, 50), fill=(250, 200, 90, 180))
    d.chord((16, 6, 80, 40), 180, 360, fill=(255, 250, 235, 255), outline=(200, 190, 170, 255))
    for i, c in enumerate(CORE_COLORS):
        a = math.radians(i * 30)
        x, y = 48 + math.cos(a) * 18, 58 + math.sin(a) * 22
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=c + (255,), outline=(60, 30, 5, 255))
    return img


def tinted(img, hue_shift, sat=1.0):
    """Recolore o liquido da caneca (tons amarelos/ambar) para variar as cervejas."""
    img = img.copy()
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            r, g, b, a = px[x, y]
            if a and r > 120 and g > 60 and b < 110 and r > b + 60:  # ambar
                h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                h = (h + hue_shift) % 1.0
                r2, g2, b2 = colorsys.hsv_to_rgb(h, min(1, s * sat), v)
                px[x, y] = (int(r2 * 255), int(g2 * 255), int(b2 * 255), a)
    return img


OUTL = (38, 24, 14, 255)
LEATHER = (132, 78, 38, 255)
LEATHER_D = (92, 52, 24, 255)
LEATHER_L = (170, 108, 58, 255)
STEEL = (150, 156, 164, 255)
STEEL_D = (96, 102, 112, 255)
STEEL_L = (205, 212, 220, 255)
CYAN = (40, 210, 222, 255)


def _px_icon(draw_fn, size=48):
    """Desenha em grade pequena e amplia sem suavizar (pixel art), com contorno escuro."""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(img))
    # contorno: pixels transparentes vizinhos de pixels pintados viram contorno
    px = img.load()
    out = img.copy()
    op = out.load()
    for y in range(size):
        for x in range(size):
            if px[x, y][3] == 0 and any(0 <= x + dx < size and 0 <= y + dy < size and px[x + dx, y + dy][3] > 0
                                        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                op[x, y] = OUTL
    return out.resize((size * 2, size * 2), Image.NEAREST)


def belt_icon():
    def f(d):
        d.polygon([(4, 22), (44, 18), (44, 27), (4, 31)], fill=LEATHER)
        d.line([(4, 24), (44, 20)], fill=LEATHER_L)
        d.line([(4, 30), (44, 26)], fill=LEATHER_D)
        d.rectangle((19, 18, 28, 29), fill=STEEL)
        d.rectangle((21, 20, 26, 27), fill=LEATHER)
        d.line([(19, 18), (28, 18)], fill=STEEL_L)
        d.rectangle((6, 27, 15, 38), fill=LEATHER_D)          # bolsa esquerda
        d.rectangle((6, 27, 15, 30), fill=LEATHER)
        d.rectangle((10, 30, 11, 32), fill=STEEL_L)
        d.rectangle((32, 24, 41, 36), fill=LEATHER_D)         # bolsa direita
        d.rectangle((32, 24, 41, 27), fill=LEATHER)
        d.rectangle((36, 27, 37, 29), fill=STEEL_L)
        d.rectangle((44, 21, 46, 33), fill=STEEL)              # chave inglesa pendurada
        d.rectangle((43, 33, 47, 37), fill=STEEL_D)
        d.rectangle((45, 34, 45, 36), fill=(0, 0, 0, 0))
        d.ellipse((25, 29, 30, 36), fill=CYAN)                  # frasco ciano
        d.rectangle((26, 27, 29, 29), fill=STEEL_L)
    return _px_icon(f)


def boots_icon():
    def f(d):
        for ox in (4, 24):
            d.rectangle((ox + 4, 8, ox + 13, 30), fill=LEATHER)          # cano
            d.rectangle((ox + 4, 8, ox + 13, 11), fill=LEATHER_L)
            d.rectangle((ox + 4, 18, ox + 13, 21), fill=STEEL)             # tira de metal
            d.point([(ox + 6, 19), (ox + 11, 19)], fill=STEEL_L)
            d.polygon([(ox + 3, 30), (ox + 14, 30), (ox + 19, 35), (ox + 19, 40), (ox + 3, 40)], fill=LEATHER_D)
            d.polygon([(ox + 12, 33), (ox + 19, 35), (ox + 19, 39), (ox + 13, 39)], fill=STEEL)   # biqueira de aco
            d.line([(ox + 3, 40), (ox + 19, 40)], fill=(30, 20, 12, 255))
    return _px_icon(f)


def ring_icon():
    def f(d):
        # anel feito de uma porca sextavada, com uma mini chave inglesa soldada
        cx, cy = 22, 26
        pts = [(cx + 14 * math.cos(math.radians(a)), cy + 14 * math.sin(math.radians(a))) for a in range(0, 360, 60)]
        d.polygon(pts, fill=STEEL)
        pts2 = [(cx + 13 * math.cos(math.radians(a)), cy + 13 * math.sin(math.radians(a)) - 1) for a in range(180, 361, 60)]
        d.line(pts2, fill=STEEL_L, width=1)
        d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=(0, 0, 0, 0))
        d.polygon([(30, 8), (34, 4), (40, 10), (36, 14)], fill=STEEL_D)     # chave inglesa
        d.rectangle((37, 12, 44, 15), fill=STEEL)
        d.point([(33, 7), (34, 8)], fill=STEEL_L)
        d.ellipse((18, 12, 21, 15), fill=CYAN)                              # nucleo ciano
    return _px_icon(f)


def amulet_icon(mug):
    img = Image.new('RGBA', (96, 96), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.arc((14, 2, 82, 70), 200, 340, fill=(92, 60, 30, 255), width=4)      # cordao
    m = mug.copy()
    m.thumbnail((50, 56), Image.NEAREST)
    img.paste(m, (48 - m.width // 2, 34), m)
    return img


def icon_images():
    """{nome: Image} de todos os icones LabTech."""
    icons = {}
    for n in ('manopla', 'caneca', 'drone', 'visor', 'jaleco'):
        img = load(n)
        if img is not None:
            icons[n] = _fit(img)
    icons['manopla_mk12'] = _fit(load('manopla3') or load('manopla'))
    for i in range(12):
        icons[f'nucleo_{i}'] = load(f'nucleo_{i}') or core_icon(i)
    icons['dofus'] = load('dofus') or dofus_icon()
    icons['cinto'] = load('cinto') or belt_icon()
    icons['botas'] = load('botas') or boots_icon()
    icons['anel'] = load('anel') or ring_icon()
    if 'caneca' in icons:
        icons['amuleto'] = load('amuleto') or amulet_icon(icons['caneca'])
    base = icons.get('caneca')
    for name, shift, sat in [('cerveja_malte', 0.0, 1.0), ('cerveja_ipa', -0.03, 1.2), ('cerveja_stout', 0.0, 0.5),
                             ('cerveja_weiss', 0.03, 0.6), ('cerveja_lager', 0.02, 1.1), ('cerveja_pilsen', 0.06, 1.0)]:
        img = load(name)
        if img is None and base is not None:
            img = tinted(base, shift, sat)
            if name == 'cerveja_stout':
                img = Image.eval(img, lambda v: v)  # mantem transparencia
                px = img.load()
                for y in range(img.height):
                    for x in range(img.width):
                        r, g, b, a = px[x, y]
                        if a and r > 90 and b < 110 and r > b + 40:
                            px[x, y] = (int(r * 0.35), int(g * 0.25), int(b * 0.2), a)
        if img is not None:
            icons[name] = _fit(img)
    return icons


def island_from_world(tile_img, source_img, center, crop=(330, 0, 600, 190), radius=210, label=None):
    """Ilha no estilo real do mapa-mundi do Dofus 1.29: recorta um pedaco de terreno original
    (vila com cabanas, praia e selva de Otomai) e cola no tile vazio, estendendo o oceano em volta."""
    img = tile_img.convert('RGB').copy()
    w, h = img.size
    px = img.load()
    # oceano: cor cinza mais comum do mapa-mundi
    colors = sorted((c for c in source_img.convert('RGB').getcolors(1 << 20) if abs(c[1][0] - c[1][2]) < 8 and 90 < c[1][0] < 200), reverse=True)
    ocean = colors[0][1] if colors else (128, 128, 128)
    cx, cy = center
    # 1) transforma o "vazio" preto (e a linha de borda escura) em oceano perto da ilha, com transicao suave
    for y in range(h):
        for x in range(w):
            d = math.hypot(x - cx, (y - cy) * 1.4)
            if d > radius + 60:
                continue
            r, g, b = px[x, y]
            gray = abs(r - g) < 12 and abs(g - b) < 12
            if r + g + b < 330 or (gray and d <= radius):
                t = 1.0 if d <= radius else max(0.0, 1 - (d - radius) / 60)
                px[x, y] = tuple(int(ocean[k] * t + (r, g, b)[k] * (1 - t)) for k in range(3))
    # 2) terreno real recortado, com mascara (tudo que nao e oceano), fechado por uma elipse suave
    src = source_img.convert('RGB').crop(crop)
    sw, sh = src.size
    mask = Image.new('L', (sw, sh), 0)
    mp, sp = mask.load(), src.load()
    for y in range(sh):
        for x in range(sw):
            r, g, b = sp[x, y]
            land = abs(r - ocean[0]) + abs(g - ocean[1]) + abs(b - ocean[2]) > 40
            ex, ey = (x - sw / 2) / (sw / 2), (y - sh / 2) / (sh / 2)
            # contorno irregular (como as ilhas do mapa-mundi), sem esfumar
            wob = 0.06 * math.sin(math.atan2(ey, ex) * 7) + 0.04 * math.sin(math.atan2(ey, ex) * 13)
            mp[x, y] = 255 if land and (ex * ex + ey * ey) < 0.82 + wob else 0
    pos = (int(cx - sw / 2), int(cy - sh / 2))
    # faixa de praia (areia com borda clara), igual a costa das ilhas do Dofus
    beach = mask.filter(ImageFilter.MaxFilter(9))
    img.paste((214, 196, 150), pos, beach.filter(ImageFilter.MaxFilter(3)))
    img.paste((236, 222, 178), pos, beach)
    img.paste(src, pos, mask)
    if label:
        d = ImageDraw.Draw(img)
        tx, ty = int(cx - len(label) * 3), int(cy + sh / 2 - 8)
        d.text((tx + 1, ty + 1), label, fill=(40, 30, 20))
        d.text((tx, ty), label, fill=(255, 250, 235))
    return img


def island_tile(tile_img, maps, labels):
    """Desenha a ilha LabTech por cima do tile do mapa-mundi (600x345).
    maps: lista de (x_local_px, y_local_px) dos centros dos mapas; labels: [(x, y, texto)]."""
    img = tile_img.convert('RGB').copy()
    w, h = img.size
    xs = [p[0] for p in maps]
    ys = [p[1] for p in maps]
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    rx, ry = (max(xs) - min(xs)) / 2 + 55, (max(ys) - min(ys)) / 2 + 38
    rnd = random.Random(7)

    def blob(scale, jitter):
        pts = []
        for k in range(48):
            a = 2 * math.pi * k / 48
            r = 1 + rnd.uniform(-jitter, jitter)
            pts.append((cx + math.cos(a) * rx * scale * r, cy + math.sin(a) * ry * scale * r))
        return pts

    # cor do oceano do mapa-mundi (tom cinza mais comum que nao e preto)
    colors = sorted((c for c in img.getcolors(w * h) if sum(c[1]) > 200 and abs(c[1][0] - c[1][2]) < 12), reverse=True)
    ocean = colors[0][1] if colors else (150, 150, 150)
    sea = Image.new('RGBA', img.size, (0, 0, 0, 0))
    ds = ImageDraw.Draw(sea)
    ds.ellipse((cx - rx - 110, cy - ry - 80, cx + rx + 110, cy + ry + 80), fill=ocean + (255,))
    ds.rectangle((0, cy - ry - 40, cx, cy + ry + 60), fill=ocean + (255,))     # liga ao mar existente
    sea = sea.filter(ImageFilter.GaussianBlur(6))
    img.paste(sea, (0, 0), sea)
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.polygon(blob(1.18, 0.05), fill=(170, 170, 170, 150))           # agua rasa
    d.polygon(blob(1.05, 0.06), fill=(232, 214, 168, 255))           # areia
    d.polygon(blob(0.88, 0.07), fill=(206, 186, 138, 255))           # terra (mesmo tom do mapa-mundi)
    layer = layer.filter(ImageFilter.GaussianBlur(1.2))
    img.paste(layer, (0, 0), layer)
    d = ImageDraw.Draw(img)
    # grade dos mapas (40x23) no estilo dos outros lugares do mundi
    for (x, y) in maps:
        d.rectangle((x - 20, y - 11, x + 19, y + 11), outline=(170, 150, 110))
    # predio do laboratorio + chamine com vapor de lupulo + barril
    lx, ly = cx - 6, cy - 4
    d.polygon([(lx - 16, ly + 8), (lx - 16, ly - 6), (lx, ly - 16), (lx + 16, ly - 6), (lx + 16, ly + 8)],
              fill=(245, 245, 240), outline=(70, 55, 40))
    d.rectangle((lx - 4, ly - 1, lx + 4, ly + 8), fill=(40, 190, 200))
    d.rectangle((lx + 8, ly - 22, lx + 12, ly - 10), fill=(120, 80, 40))
    for k in range(3):
        d.ellipse((lx + 8 + k * 4, ly - 30 - k * 5, lx + 16 + k * 4, ly - 24 - k * 5), fill=(235, 235, 225))
    bx, by = cx + 26, cy + 10
    d.ellipse((bx - 7, by - 9, bx + 7, by + 9), fill=(150, 95, 45), outline=(70, 40, 15))
    d.line((bx - 7, by - 3, bx + 7, by - 3), fill=(70, 40, 15))
    d.line((bx - 7, by + 3, bx + 7, by + 3), fill=(70, 40, 15))
    for (x, y, text) in labels:
        d.text((x + 1, y + 1), text, fill=(40, 30, 20))
        d.text((x, y), text, fill=(255, 250, 235))
    return img


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, img in icon_images().items():
        img.save(os.path.join(OUT, name + '.png'))
        print(name, img.size)
