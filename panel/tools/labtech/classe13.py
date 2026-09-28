"""Classe 13 (LabTech) no cliente: sprites (a partir de uma classe base oficial), acessorios Manopla/Caneca,
artes (criacao, rostos, retratos), registro da classe no core.swf e sprites.xml.  Chamado por build.py.

Estrategia: o corpo do LabTech e o de uma classe oficial (mesmo esqueleto => chapeus, capas, armas e escudos
encaixam no tamanho exato). A identidade vem das cores, do Jaleco/Visor (itens) e dos acessorios novos:
Manopla Gambiarra (arma, simbolo 7_<g>) e Caneca da Gambiarra (escudo, simbolo 82_<g>)."""
import os
import shutil
import struct
import zlib

from PIL import Image

import swf

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
CLIENTS = [os.path.join(ROOT, 'server', 'client-starloco', 'resources', 'app', 'retroclient'),
           os.path.join(ROOT, 'Client-Dofus-1-29-master', 'Client-Dofus-1-29-master', 'Client')]
CONCEPT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'world', 'labtech', 'art', 'conceito'))
ART = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'world', 'labtech', 'art'))
OUT = os.path.join(ART, 'gerado', 'classe13')
MARKER = 'LABTECH_CLASS_PATCH'
NUL = bytes(1)

# nomes ofuscados de dofus.Constants no cliente Retro (confirmados no loader.swf)
OBF = {'const': '\x1e\x1c\x05', 'order': '\x1d\x18\x07', 'episodic': '\x1e\x0f\x0c', 'skin_idx': '\x0b\x1d', 'skin_col': '\x0c\x01'}
PLAIN = {'const': 'Constants', 'order': 'GUILD_ORDER', 'episodic': 'EPISODIC_GUILD', 'skin_idx': 'BREED_SKIN_INDEXES',
         'skin_col': 'BREED_SKIN_BASE_COLOR'}


# ----------------------------------------------------------------- imagens de conceito

def _remove_background(img, tol=46):
    """Remove o fundo (papel/grade) por preenchimento a partir das bordas."""
    img = img.convert('RGBA')
    w, h = img.size
    px = img.load()
    seen = bytearray(w * h)
    stack = [(x, 0) for x in range(w)] + [(x, h - 1) for x in range(w)] + [(0, y) for y in range(h)] + [(w - 1, y) for y in range(h)]
    ref = px[0, 0]
    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= w or y >= h or seen[y * w + x]:
            continue
        seen[y * w + x] = 1
        r, g, b, a = px[x, y]
        near_ref = abs(r - ref[0]) + abs(g - ref[1]) + abs(b - ref[2]) <= tol * 3 and (r + g + b) >= 330
        # papel/grade bege quente (o jaleco e branco neutro, por isso nao entra)
        paper = r > 150 and g > 125 and b > 90 and 18 <= r - b <= 95 and r + g + b > 420
        if not (near_ref or paper):
            continue
        px[x, y] = (0, 0, 0, 0)
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    return img.crop(img.getbbox())


def _clean_floor(img, band=0.22):
    """Remove o chao quadriculado e textos da faixa de baixo: tira tons claros/acinzentados e
    qualquer pedaco que nao esteja ligado as pernas (parte de cima da imagem)."""
    import colorsys
    img = img.copy()
    px = img.load()
    w, h = img.size
    y0 = int(h * (1 - band))
    for y in range(y0, h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if not a:
                continue
            _, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
            if (s < 0.25 and v > 0.28) or (v > 0.6 and s < 0.45):
                px[x, y] = (0, 0, 0, 0)
    # mantem so o que esta conectado a linha y0 (pernas/botas)
    keep = set()
    stack = [(x, y0 - 1) for x in range(w) if px[x, y0 - 1][3]]
    while stack:
        x, y = stack.pop()
        if (x, y) in keep or not (0 <= x < w and y0 - 1 <= y < h) or not px[x, y][3]:
            continue
        keep.add((x, y))
        stack += [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
    for y in range(y0, h):
        for x in range(w):
            if (x, y) not in keep:
                px[x, y] = (0, 0, 0, 0)
    bb = img.getbbox()
    return img.crop(bb) if bb else img


def _largest_component(img):
    """Mantem so o maior pedaco opaco (tira drones soltos, textos e restos do fundo)."""
    a = img.split()[3].point(lambda v: 255 if v > 20 else 0)
    w, h = img.size
    px = a.load()
    seen = bytearray(w * h)
    best = []
    for sy in range(0, h, 2):
        for sx in range(0, w, 2):
            if px[sx, sy] and not seen[sy * w + sx]:
                comp, stack = [], [(sx, sy)]
                seen[sy * w + sx] = 1
                while stack:
                    x, y = stack.pop()
                    comp.append((x, y))
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < w and 0 <= ny < h and px[nx, ny] and not seen[ny * w + nx]:
                            seen[ny * w + nx] = 1
                            stack.append((nx, ny))
                if len(comp) > len(best):
                    best = comp
    mask = Image.new('L', (w, h), 0)
    mp = mask.load()
    for x, y in best:
        mp[x, y] = 255
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    bb = out.getbbox()
    return out.crop(bb) if bb else out


def labtech_symbol(size=512):
    """Simbolo da classe (silhueta): engrenagem com os 12 nucleos vazados e uma caneca no centro."""
    import math
    from PIL import ImageDraw
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size / 2
    col = (255, 255, 255, 255)
    teeth = 12
    pts = []
    for k in range(teeth * 4):
        a = 2 * math.pi * k / (teeth * 4)
        r = c * (0.96 if (k % 4) in (1, 2) else 0.8)
        pts.append((c + math.cos(a) * r, c + math.sin(a) * r))
    d.polygon(pts, fill=col)
    d.ellipse((c - c * 0.58, c - c * 0.58, c + c * 0.58, c + c * 0.58), fill=(0, 0, 0, 0))
    for k in range(12):   # 12 nucleos vazados no aro
        a = -math.pi / 2 + 2 * math.pi * k / 12
        x, y = c + math.cos(a) * c * 0.69, c + math.sin(a) * c * 0.69
        rr = c * 0.055
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(0, 0, 0, 0))
    # caneca: corpo, alca e espuma
    mw, mh = c * 0.5, c * 0.62
    x0, y0 = c - mw * 0.6, c - mh * 0.35
    d.rounded_rectangle((x0, y0, x0 + mw, y0 + mh), radius=c * 0.06, fill=col)
    d.ellipse((x0 + mw - c * 0.08, y0 + mh * 0.18, x0 + mw + c * 0.26, y0 + mh * 0.78), outline=col, width=int(c * 0.08))
    for fx, fr in ((0.1, 0.16), (0.42, 0.2), (0.78, 0.15)):
        d.ellipse((x0 + mw * fx - c * fr, y0 - c * fr * 1.1, x0 + mw * fx + c * fr, y0 + c * fr * 0.9), fill=col)
    return img


def _ring_base():
    """Anel bege das classes, renderizado do cliente do proprio usuario (arte da Ankama: nao vai para o repositorio).
    Fonte: clips/artworks/breeds/back/1.swf (fundo do Feca), sprite 2, zoom 4."""
    import subprocess
    import tempfile
    import glob
    out = os.path.join(ART, 'classe13', '_anel_base.png')
    if os.path.exists(out):
        return out
    src = next((os.path.join(c, 'clips', 'artworks', 'breeds', 'back', '1.swf') for c in CLIENTS
                if os.path.exists(os.path.join(c, 'clips', 'artworks', 'breeds', 'back', '1.swf'))), None)
    if src is None:
        raise RuntimeError('cliente nao encontrado: coloque o Dofus Retro 1.39.8 em server/client-starloco')
    tmp = tempfile.mkdtemp(prefix='lt_ring_')
    subprocess.run([os.path.join(ROOT, 'runtime', 'jdk21', 'bin', 'java.exe'), '-jar',
                    os.path.join(ROOT, 'runtime', 'ffdec', 'ffdec-cli.jar'), '-selectid', '2', '-zoom', '4',
                    '-export', 'sprite', tmp, src], capture_output=True, timeout=600)
    found = glob.glob(os.path.join(tmp, 'DefineSprite_2*', '1.png'))
    if not found:
        raise RuntimeError('nao consegui renderizar o anel das classes com o JPEXS')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    shutil.copy2(found[0], out)
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def _ring(with_symbol=None):
    """Anel oficial das classes (bege dentado) sem o simbolo do Feca; opcionalmente com um simbolo novo
    pintado no mesmo bege translucido."""
    base = Image.open(_ring_base()).convert('RGBA')
    w, h = base.size
    px = base.load()
    c = w / 2
    inner = w * 0.36
    for y in range(h):
        for x in range(w):
            if (x - c) ** 2 + (y - c) ** 2 < inner ** 2:
                px[x, y] = (0, 0, 0, 0)
    if with_symbol is not None:
        sym = with_symbol.convert('RGBA')
        k = (w * 0.62) / max(sym.size)
        sym = sym.resize((int(sym.width * k), int(sym.height * k)), Image.LANCZOS)
        tint = Image.new('RGBA', sym.size, (152, 135, 105, 0))
        alpha = sym.split()[3].point(lambda v: int(v * 0.73))
        tint.putalpha(alpha)
        base.paste(tint, (int(c - sym.width / 2), int(c - sym.height / 2)), tint)
    return base


def _medallion(bust, ring):
    """Composicao igual a das outras classes: anel embaixo, busto dentro; a cabeca pode sair por cima,
    o resto e cortado pela borda do circulo."""
    rw = ring.width
    W, H = rw, int(rw * 198 / 156)
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ry = H - rw
    canvas.paste(ring, (0, ry), ring)
    b = bust.copy()
    k = (H * 0.97) / b.height                    # cabeca encosta no topo (sai por cima do anel)
    if b.width * k > W * 1.12:
        k = W * 1.12 / b.width
    b = b.resize((int(b.width * k), int(b.height * k)), Image.LANCZOS)
    bx, by = int(W / 2 - b.width / 2), H - int(rw * 0.04) - b.height
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    layer.paste(b, (bx, by), b)
    cx, cy, r = W / 2, ry + rw / 2, rw * 0.47
    lp = layer.load()
    for y in range(H):
        for x in range(W):
            if y > cy and (x - cx) ** 2 + (y - cy) ** 2 > r * r:
                lp[x, y] = (0, 0, 0, 0)
    canvas.alpha_composite(layer)
    return canvas


def concept_images():
    """PNGs em art/classe13/<nome>.png substituem os recortes automaticos."""
    male = Image.open(os.path.join(CONCEPT, 'labtech_male_white_1790527165720.jpg')).convert('RGB')
    female = Image.open(os.path.join(CONCEPT, 'labtech_female_white_1790527176412.jpg')).convert('RGB')
    imgs = {
        'corpo_m': _clean_floor(_remove_background(male.crop((30, 160, 580, 935)))),
        'corpo_f': _clean_floor(_remove_background(female.crop((60, 120, 498, 945)))),
        'rosto_m': male.crop((700, 668, 958, 938)).convert('RGBA'),
        'rosto_f': female.crop((600, 590, 965, 960)).convert('RGBA'),
        'costas_m': _remove_background(male.crop((660, 130, 1000, 600))),
    }
    imgs['meio_m'] = imgs['corpo_m'].crop((0, 0, imgs['corpo_m'].width, int(imgs['corpo_m'].height * 0.62)))
    imgs['meio_f'] = imgs['corpo_f'].crop((0, 0, imgs['corpo_f'].width, int(imgs['corpo_f'].height * 0.62)))
    imgs['emblema'] = emblem(256, faint=False)
    imgs['emblema_fundo'] = emblem(512, faint=True)
    # bustos (cabeca ate a cintura, com a manopla e a caneca), sem o drone solto
    imgs['busto_m'] = _largest_component(_remove_background(male.crop((40, 165, 570, 660))))
    imgs['busto_f'] = _largest_component(_remove_background(female.crop((65, 125, 505, 610))))
    ring_plain = _ring()
    imgs['medalhao_m'] = _medallion(imgs['busto_m'], ring_plain)
    imgs['medalhao_f'] = _medallion(imgs['busto_f'], ring_plain)
    imgs['medalhao_fundo'] = _ring(labtech_symbol())
    duo = os.path.join(CONCEPT, 'labtech_duo_white_1790527187046.jpg')
    if os.path.exists(duo):
        imgs['cena'] = Image.open(duo).convert('RGBA')
    for k in list(imgs):
        p = os.path.join(ART, 'classe13', k + '.png')
        if os.path.exists(p):
            imgs[k] = Image.open(p).convert('RGBA')
    os.makedirs(OUT, exist_ok=True)
    for k, im in imgs.items():
        im.save(os.path.join(OUT, k + '.png'))
    return imgs


def sprite_portraits(sprite_dir, imgs, pose='staticR', zoom=20):
    """Retratos no estilo do jogo: renderiza o proprio boneco remodelado (vetor do Dofus) com o JPEXS e recorta
    busto (cabeca ate a cintura) e rosto. Substitui os recortes da arte conceitual (pixel art)."""
    import subprocess, tempfile, glob
    ffdec = os.path.join(ROOT, 'runtime', 'ffdec', 'ffdec-cli.jar')
    java = os.path.join(ROOT, 'runtime', 'jdk21', 'bin', 'java.exe')
    if not (os.path.exists(ffdec) and os.path.exists(java)):
        return
    ring_plain = _ring()
    for sex, tag in ((0, 'm'), (1, 'f')):
        path = os.path.join(sprite_dir, f'{130 + sex}.swf')
        s = swf.read_swf(path)
        ex = {}
        for c, d in s.tags:
            if c == 56:
                n, p = struct.unpack_from('<H', d, 0)[0], 2
                for _ in range(n):
                    cid = struct.unpack_from('<H', d, p)[0]
                    e = d.index(NUL, p + 2)
                    ex[d[p + 2:e].decode('latin1')] = cid
                    p = e + 1
        if pose not in ex:
            continue
        out = tempfile.mkdtemp(prefix='lt_portrait_')
        cid = ex[pose]
        subprocess.run([java, '-jar', ffdec, '-selectid', str(cid), '-select', f'{cid}:1', '-zoom', str(zoom),
                        '-export', 'sprite', out, path], capture_output=True, timeout=900)
        found = glob.glob(os.path.join(out, f'DefineSprite_{cid}*', '1.png'))
        if not found:
            continue
        full = Image.open(found[0]).convert('RGBA')
        full = full.crop(full.getbbox())
        a = full.split()[3].point(lambda v: 255 if v > 200 else 0)    # sombra no chao e translucida: fica de fora
        full = full.crop(a.getbbox())
        w, h = full.size
        bust = full.crop((0, 0, w, int(h * 0.60)))
        bust = bust.crop(bust.getbbox())
        face = full.crop((0, 0, w, int(h * 0.34)))
        face = face.crop(face.getbbox())
        side = max(face.size)
        sq = Image.new('RGBA', (side, side), (0, 0, 0, 0))
        sq.paste(face, ((side - face.width) // 2, side - face.height), face)
        imgs['busto_' + tag] = bust
        imgs['rosto_' + tag] = sq
        imgs['medalhao_' + tag] = _medallion(bust, ring_plain)
        shutil.rmtree(out, ignore_errors=True)
    os.makedirs(OUT, exist_ok=True)
    for k in ('busto_m', 'busto_f', 'rosto_m', 'rosto_f', 'medalhao_m', 'medalhao_f'):
        if k in imgs:
            imgs[k].save(os.path.join(OUT, k + '.png'))


def emblem(size, faint=False):
    """Emblema da classe no estilo dos simbolos do Dofus: anel de bronze dentado com os 12 nucleos
    coloridos e a Manopla no centro. faint=True gera a versao grande e translucida do fundo."""
    import math
    from PIL import ImageDraw
    import art
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    c = size / 2
    ring = (150, 132, 100, 150) if faint else (122, 74, 32, 255)
    inner = (205, 190, 160, 110) if faint else (242, 232, 205, 255)
    teeth = 24
    pts = []
    for k in range(teeth * 2):
        r = c * (0.97 if k % 2 == 0 else 0.88)
        a = math.pi * k / teeth
        pts.append((c + math.cos(a) * r, c + math.sin(a) * r))
    d.polygon(pts, fill=ring)
    d.ellipse((c * 0.22, c * 0.22, size - c * 0.22, size - c * 0.22), fill=inner)
    d.ellipse((c * 0.22, c * 0.22, size - c * 0.22, size - c * 0.22), outline=ring, width=max(2, size // 60))
    for i, col in enumerate(art.CORE_COLORS):
        a = -math.pi / 2 + 2 * math.pi * i / 12
        x, y = c + math.cos(a) * c * 0.66, c + math.sin(a) * c * 0.66
        rr = size * 0.045
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=col + ((150,) if faint else (255,)), outline=(60, 34, 12, 200))
    if not faint:
        g = Image.open(os.path.join(ART, 'gerado', 'manopla.png')).convert('RGBA')
        g.thumbnail((int(size * 0.62), int(size * 0.62)))
        img.paste(g, (int(c - g.width / 2), int(c - g.height / 2)), g)
    return img


# ----------------------------------------------------------------- tags de bitmap

def _lossless(bitmap_id, img):
    img = img.convert('RGBA')
    w, h = img.size
    argb = bytearray()
    for r, g, b, a in img.getdata():
        argb += bytes([a, r * a // 255, g * a // 255, b * a // 255])
    return (36, struct.pack('<HBHH', bitmap_id, 5, w, h) + zlib.compress(bytes(argb), 9))


def _matrix_bits(w, sx=None, sy=None, tx=0, ty=0):
    if sx is not None:
        w.ub(1, 1)
        n = max(swf.nbits_signed(int(sx * 65536), int(sy * 65536)), 2)
        w.ub(n, 5); w.sb(int(sx * 65536), n); w.sb(int(sy * 65536), n)
    else:
        w.ub(0, 1)
    w.ub(0, 1)
    n = swf.nbits_signed(tx, ty)
    w.ub(n, 5); w.sb(tx, n); w.sb(ty, n)


def _bitmap_shape(shape_id, bitmap_id, img_size, box):
    """DefineShape com preenchimento de bitmap ocupando box (twips: x0,x1,y0,y1)."""
    x0, x1, y0, y1 = box
    iw, ih = img_size
    fill = swf.BitWriter()
    _matrix_bits(fill, (x1 - x0) / iw, (y1 - y0) / ih, x0, y0)
    styles = bytes([1, 0x41]) + struct.pack('<H', bitmap_id) + fill.bytes() + bytes([0])
    sr = swf.BitWriter()
    sr.ub(1, 4); sr.ub(0, 4)
    sr.ub(0, 1); sr.ub(0, 1); sr.ub(0, 1); sr.ub(1, 1); sr.ub(0, 1); sr.ub(1, 1)
    n = swf.nbits_signed(x0, y0)
    sr.ub(n, 5); sr.sb(x0, n); sr.sb(y0, n)
    sr.ub(1, 1)

    def edge(dx, dy):
        sr.ub(1, 1); sr.ub(1, 1)
        m = max(swf.nbits_signed(dx, dy), 2)
        sr.ub(m - 2, 4)
        sr.ub(0, 1); sr.ub(1 if dy else 0, 1); sr.sb(dy if dy else dx, m)
    edge(x1 - x0, 0); edge(0, y1 - y0); edge(x0 - x1, 0); edge(0, y0 - y1)
    sr.ub(0, 6)
    return (2, struct.pack('<H', shape_id) + swf.rect(x0, x1, y0, y1) + styles + sr.bytes())


def _fit(img, box, mode='contain'):
    """Retorna (img redimensionada, box ajustado mantendo proporcao, centralizado)."""
    x0, x1, y0, y1 = box
    bw, bh = x1 - x0, y1 - y0
    iw, ih = img.size
    scale = min(bw / iw, bh / ih) if mode == 'contain' else max(bw / iw, bh / ih)
    w, h = int(iw * scale), int(ih * scale)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    # resolucao do bitmap: ~1 pixel por 20 twips * 2 (nitidez)
    px_w = max(8, min(iw, int(w / 20 * 6)))   # 6 px por unidade: a arte e ampliada no inicio do turno
    px_h = max(8, int(px_w * ih / iw))
    return img.resize((px_w, px_h), Image.LANCZOS), (cx - w // 2, cx + w // 2, cy - h // 2, cy + h // 2)


# ----------------------------------------------------------------- artes no formato das originais

def _parse_sprite_tags(d):
    p, out = 4, []
    while p < len(d):
        cl = struct.unpack_from('<H', d, p)[0]
        p += 2
        c, ln = cl >> 6, cl & 0x3F
        if ln == 0x3F:
            ln = struct.unpack_from('<I', d, p)[0]
            p += 4
        out.append((c, d[p:p + ln]))
        p += ln
    return out


def _read_matrix(b, pos_bits=0):
    """MATRIX do SWF -> ((a, b, c, d, tx, ty), bits consumidos)."""
    bits = ''.join(f'{x:08b}' for x in b[:40])
    i = pos_bits

    def ub(n):
        nonlocal i
        v = int(bits[i:i + n], 2) if n else 0
        i += n
        return v

    def sb(n):
        v = ub(n)
        return v - (1 << n) if n and v >> (n - 1) else v
    a = d = 1.0
    bb = cc = 0.0
    if ub(1):
        n = ub(5); a = sb(n) / 65536; d = sb(n) / 65536
    if ub(1):
        n = ub(5); bb = sb(n) / 65536; cc = sb(n) / 65536
    n = ub(5)
    tx, ty = sb(n), sb(n)
    return (a, bb, cc, d, tx, ty), (i + 7) // 8


def _parse_place2(d):
    """PlaceObject2 -> dict(flags, depth, char, matrix, rest(bytes apos a matriz))."""
    fl = d[0]
    depth = struct.unpack_from('<H', d, 1)[0]
    p = 3
    char = None
    if fl & 2:
        char = struct.unpack_from('<H', d, p)[0]
        p += 2
    m = (1.0, 0.0, 0.0, 1.0, 0, 0)
    if fl & 4:
        m, n = _read_matrix(d[p:])
        p += n
    return {'flags': fl, 'depth': depth, 'char': char, 'matrix': m, 'rest': d[p:]}


def _apply(m, box):
    a, b, c, d, tx, ty = m
    xs, ys = [], []
    for x in (box[0], box[1]):
        for y in (box[2], box[3]):
            xs.append(a * x + c * y + tx)
            ys.append(b * x + d * y + ty)
    return (min(xs), max(xs), min(ys), max(ys))


def _union(boxes):
    boxes = [b for b in boxes if b]
    if not boxes:
        return None
    return (min(b[0] for b in boxes), max(b[1] for b in boxes), min(b[2] for b in boxes), max(b[3] for b in boxes))


def composition_bounds(s):
    """Caixa (twips) do que a raiz mostra no 1o quadro, seguindo as matrizes de cada sprite."""
    defs = {}
    for c, d in s.tags:
        if c in (2, 22, 32, 83, 39, 46, 84):
            defs[struct.unpack_from('<H', d, 0)[0]] = (c, d)

    def bounds(cid, depth=0):
        if cid not in defs or depth > 8:
            return None
        c, d = defs[cid]
        if c in (2, 22, 32, 83, 46, 84):
            r, _ = swf.read_rect(d[2:])
            return tuple(r)
        boxes = []
        for cc, dd in _parse_sprite_tags(d):
            if cc == 1:
                break
            if cc == 26:
                pl = _parse_place2(dd)
                if pl['char']:
                    boxes.append(_apply(pl['matrix'], bounds(pl['char'], depth + 1) or (0, 0, 0, 0)))
        return _union(boxes)

    boxes, root = [], None
    for c, d in s.tags:
        if c == 1:
            break
        if c == 26:
            pl = _parse_place2(d)
            if pl['char']:
                root = root or pl
                boxes.append(_apply(pl['matrix'], bounds(pl['char']) or (0, 0, 0, 0)))
    return _union(boxes), root


def visible_box(base_path, pad=4000):
    """Caixa (twips) do que a arte original realmente desenha: renderiza com o JPEXS num palco largo.
    Algumas artes (ex.: big/) tem mascaras/areas vazias que deixam composition_bounds bem maior que o desenho."""
    import subprocess, tempfile
    from PIL import ImageChops
    ffdec = os.path.join(ROOT, 'runtime', 'ffdec', 'ffdec-cli.jar')
    java = os.path.join(ROOT, 'runtime', 'jdk21', 'bin', 'java.exe')
    s = swf.read_swf(base_path)
    x0, y0 = -pad, -int(pad * 1.5)
    s.header_rect = swf.rect(x0, pad, y0, pad // 2)
    tmp = tempfile.mkdtemp(prefix='lt_box_')
    src = os.path.join(tmp, 'a.swf')
    swf.write_swf(s, src)
    subprocess.run([java, '-jar', ffdec, '-format', 'frame:png', '-export', 'frame', os.path.join(tmp, 'out'), src],
                   capture_output=True, timeout=600)
    png = os.path.join(tmp, 'out', '1.png')
    if not os.path.exists(png):
        return None
    im = Image.open(png).convert('RGB')
    k = (2 * pad) / im.width                  # twips por pixel
    bb = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).point(lambda v: 255 if v > 12 else 0).getbbox()
    shutil.rmtree(tmp, ignore_errors=True)
    if not bb:
        return None
    return (int(x0 + bb[0] * k), int(x0 + bb[2] * k), int(y0 + bb[1] * k), int(y0 + bb[3] * k))


def _eye_center(img):
    """Centro do visor (pixels ciano) na imagem, em fracao (x, y); sem visor, um ponto tipico de rosto."""
    im = img.convert('RGBA')
    small = im.resize((max(1, im.width // 4), max(1, im.height // 4)))
    pts = [(x, y) for y in range(int(small.height * 0.45)) for x in range(small.width)   # so a cabeca (fivela/botoes sao ciano tambem)
           for r, g, b, a in [small.getpixel((x, y))] if a > 128 and r < 110 and g > 160 and b > 170]
    if len(pts) < 4:
        return 0.5, 0.3
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return (min(xs) + max(xs)) / 2 / small.width, (min(ys) + max(ys)) / 2 / small.height


def _mask_like(base, img, im, fitted):
    """Arte big/: o painel da luta usa o clipe "_mcMask" da arte para enquadrar/ampliar o retrato (faixa dos olhos).
    Copia o _mcMask da arte original (mesmo tamanho) e o centraliza no visor da nossa imagem."""
    defs = {struct.unpack_from('<H', d, 0)[0]: (c, d) for c, d in base.tags if c in (2, 22, 32, 83, 39)}
    for c, d in base.tags:
        if c != 26 or b'_mcMask\x00' not in d:
            continue
        pl = _parse_place2(d)
        spr = defs.get(pl['char'])
        if not spr or spr[0] != 39:
            return None
        inner = [_parse_place2(td) for tc, td in _parse_sprite_tags(spr[1]) if tc == 26]
        if not inner or inner[0]['char'] not in defs:
            return None
        sc, sd = defs[inner[0]['char']]
        sx0, sx1, sy0, sy1 = swf.read_rect(sd[2:])[0]
        a, b_, c_, d_, tx, ty = pl['matrix']
        w, h = (sx1 - sx0) * a, (sy1 - sy0) * d_
        fx, fy = _eye_center(img)
        cx = fitted[0] + (fitted[1] - fitted[0]) * fx
        cy = fitted[2] + (fitted[3] - fitted[2]) * fy
        shape_id, sprite_id = 20, 21
        shape = (sc, struct.pack('<H', shape_id) + sd[2:])
        sprite = (39, struct.pack('<HH', sprite_id, 1) + swf.encode_tag(26, bytes([0x06]) + struct.pack('<HH', 1, shape_id) + NUL)
                  + swf.encode_tag(1, b'') + swf.encode_tag(0, b''))
        m = swf.BitWriter()
        _matrix_bits(m, a, d_, int(cx - w / 2 - sx0 * a), int(cy - h / 2 - sy0 * d_))
        place = bytes([0x26]) + struct.pack('<HH', pl['depth'] + 100, sprite_id) + m.bytes() + b'_mcMask' + NUL
        return [shape, sprite, (26, place)]
    return None


def art_like(base_path, img, out_path, mode='contain', base_class=None, box=None):
    """Gera um SWF com a imagem ocupando exatamente a area visivel da arte original (mesmo palco,
    mesma caixa final na raiz, mesmo nome de instancia/profundidade), preservando acoes e rotulos."""
    s = swf.read_swf(base_path)
    cbox, root = composition_bounds(s)
    anchor_bottom = box is not None
    box = tuple(int(v) for v in (box or cbox))
    im, fitted = _fit(img, box, mode)
    if anchor_bottom:   # busto apoiado na base, como o desenho oficial
        dy = box[3] - fitted[3]
        fitted = (fitted[0], fitted[1], fitted[2] + dy, fitted[3] + dy)
    keep = [(c, d) for c, d in s.tags if c in (69, 9, 24, 12, 43)]
    bitmap_id, shape_id, sprite_id = 1, 2, 3
    inner = bytes([0x06]) + struct.pack('<HH', 1, shape_id) + NUL
    sprite = struct.pack('<HH', sprite_id, 1) + swf.encode_tag(26, inner) + swf.encode_tag(1, b'') + swf.encode_tag(0, b'')
    # mesma profundidade e nome da instancia original (ex.: "illu", usado pelos scripts de cor), matriz identidade
    name = b''
    if root['flags'] & 0x20 and not root['flags'] & 0x18:
        name = root['rest'][:root['rest'].index(NUL) + 1]
    place = bytes([0x06 | (0x20 if name else 0)]) + struct.pack('<HH', root['depth'], sprite_id) + NUL + name
    tags = [t for t in keep if t[0] in (69, 9)] + [_lossless(bitmap_id, im), _bitmap_shape(shape_id, bitmap_id, im.size, fitted),
                                                   (39, sprite)] + [t for t in keep if t[0] not in (69, 9)] + [(26, place), (1, b''), (0, b'')]
    # mantem os simbolos exportados da original (ex.: miniPerso1 -> miniPerso13)
    names = []
    for c, d in s.tags:
        if c == 56:
            n = struct.unpack_from('<H', d, 0)[0]
            p = 2
            for _ in range(n):
                e = d.index(NUL, p + 2)
                names.append(d[p + 2:e].decode('latin1'))
                p = e + 1
    if names:
        if base_class is not None:
            names = [nm[:-len(str(base_class))] + '13' if nm.endswith(str(base_class)) else nm for nm in names]
        exp = struct.pack('<H', len(names)) + b''.join(struct.pack('<H', sprite_id) + nm.encode() + NUL for nm in names)
        tags.insert(tags.index((39, sprite)) + 1, (56, exp))
    mask = _mask_like(s, img, im, fitted)
    if mask:
        tags = tags[:-2] + mask + tags[-2:]
    s.tags = tags
    s.frame_count = 1
    swf.write_swf(s, out_path)


# ----------------------------------------------------------------- acessorios (Manopla e Caneca)

def _accessory_sprite(sprite_id, shape_r, shape_l):
    body = struct.pack('<HH', sprite_id, 2)
    body += swf.encode_tag(43, b'R\x00')
    body += swf.encode_tag(26, bytes([0x06]) + struct.pack('<HH', 1, shape_r) + NUL)
    body += swf.encode_tag(1, b'')
    body += swf.encode_tag(43, b'L\x00')
    body += swf.encode_tag(28, struct.pack('<H', 1))
    body += swf.encode_tag(26, bytes([0x06]) + struct.pack('<HH', 1, shape_l) + NUL)
    body += swf.encode_tag(1, b'')
    body += swf.encode_tag(0, b'')
    return (39, body)


def add_accessories(src_path, lib_path, items):
    """items: lista de (nome_simbolo, imagem, caixa_twips). Sempre parte do arquivo original (src_path)."""
    s = swf.read_swf(src_path)
    names = {n for n, _, _ in items}
    # remove simbolos antigos com esses nomes (e suas definicoes, marcadas pelo ExportAssets proprio)
    new_tags, drop_ids = [], set()
    for c, d in s.tags:
        if c == 56 and d.endswith(NUL) and any(n.encode() + NUL in d for n in names) and MARKER.encode() in d:
            n = struct.unpack_from('<H', d, 0)[0]
            p = 2
            for _ in range(n):
                drop_ids.add(struct.unpack_from('<H', d, p)[0])
                p = d.index(b'\0', p + 2) + 1
            continue
        new_tags.append((c, d))
    # ids a remover: sprites exportados + formas/bitmaps logo abaixo (usamos faixa contigua)
    if drop_ids:
        lo = min(drop_ids) - 4 * len(names)
        new_tags = [(c, d) for c, d in new_tags if not (c in (2, 36, 39) and lo <= struct.unpack_from('<H', d, 0)[0] <= max(drop_ids))]
    max_id = max((struct.unpack_from('<H', d, 0)[0] for c, d in new_tags if c in (2, 20, 21, 22, 32, 35, 36, 39, 83, 6, 10, 11, 37, 46, 48, 75, 7, 34)), default=0)
    nid = max_id + 1
    defs, exports = [], []
    for name, img, box in items:
        bid_r, sid_r, bid_l, sid_l, spr = nid, nid + 1, nid + 2, nid + 3, nid + 4
        nid += 5
        im, fitted = _fit(img, box, 'contain')
        mirrored = im.transpose(Image.FLIP_LEFT_RIGHT)
        defs += [_lossless(bid_r, im), _bitmap_shape(sid_r, bid_r, im.size, fitted),
                 _lossless(bid_l, mirrored), _bitmap_shape(sid_l, bid_l, mirrored.size, fitted),
                 _accessory_sprite(spr, sid_r, sid_l)]
        exports.append((spr, name))
    exp = struct.pack('<H', len(exports) + 1) + b''.join(struct.pack('<H', i) + n.encode() + NUL for i, n in exports)
    exp += struct.pack('<H', exports[0][0]) + MARKER.encode() + NUL
    idx = next(i for i, (c, _) in enumerate(new_tags) if c == 1)   # antes do primeiro ShowFrame
    new_tags = new_tags[:idx] + defs + [(56, exp)] + new_tags[idx:]
    s.tags = new_tags
    swf.write_swf(s, lib_path)


# ----------------------------------------------------------------- core.swf: registra a classe 13

def _core_patch_code(names, base_class):
    """AS2: C = _global.dofus[Constants]; C.order[12]=13; PAYING[12]=false; EPISODIC[12]=1;
    SKIN_IDX[0|1][12] = SKIN_IDX[0|1][base-1]; SKIN_COL idem."""
    a = swf.ActionBuilder()
    a.push('__ltC').push('_global').get_variable().push('dofus').get_member().push(names['const']).get_member().set_variable()
    a.push(MARKER, True).set_variable()

    def member(*chain):
        a.push('__ltC').get_variable()
        for k in chain:
            a.push(k).get_member()

    member(names['order']); a.push(12, 13).set_member()
    member('PAYING_GUILD'); a.push(12, False).set_member()
    member(names['episodic']); a.push(12, 1).set_member()
    for key in ('skin_idx', 'skin_col'):
        for sex in (0, 1):
            member(names[key], sex)
            a.push(12)
            member(names[key], sex, base_class - 1)
            a.set_member()
    return a.bytes()


def patch_core(client, base_class):
    path = os.path.join(client, 'modules', 'core.swf')
    if not os.path.exists(path):
        return False
    bak = path + '.labtech.bak'
    if not os.path.exists(bak):
        shutil.copy2(path, bak)
    s = swf.read_swf(bak)
    names = OBF if b'\x1e\x1c\x05' in b''.join(d for c, d in s.tags if c in (12, 59)) else PLAIN
    code = _core_patch_code(names, base_class)
    idx = max(i for i, (c, _) in enumerate(s.tags) if c == 1)
    import spellsui   # janela de feiticos: filtro pelas 12 racas
    s.tags = s.tags[:idx] + [(12, code), (12, spellsui.patch_code())] + s.tags[idx:]
    swf.write_swf(s, path)
    return True


def add_pet(lib_path, name, img, frames=16):
    """Familiar (acessorio 18_<g>) no formato dos oficiais: rotulos L,R,S,F,B (parado) e WL..WB (andando),
    cada um com a animacao do drone flutuando; tamanho de um familiar (~14 unidades), origem no chao."""
    import math
    from PIL import ImageDraw
    s = swf.read_swf(lib_path)
    nid = max(struct.unpack_from('<H', d, 0)[0] for c, d in s.tags if c in (2, 6, 7, 10, 11, 14, 20, 21, 22, 32, 33, 34, 35, 36, 37, 39, 46, 48, 60, 75, 83, 84, 87, 90, 91)) + 1
    body = img.convert('RGBA')
    glow = Image.new('RGBA', (48, 18), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((1, 1, 47, 17), fill=(40, 220, 235, 90))
    defs = []
    shapes = {}
    for side, im in (('R', body), ('L', body.transpose(Image.FLIP_LEFT_RIGHT))):
        fitted_im, fitted = _fit(im, (-140, 140, -360, -80), 'contain')
        defs += [_lossless(nid, fitted_im), _bitmap_shape(nid + 1, nid, fitted_im.size, fitted)]
        shapes[side] = nid + 1
        nid += 2
    defs += [_lossless(nid, glow), _bitmap_shape(nid + 1, nid, glow.size, (-120, 120, -45, 45))]
    glow_shape = nid + 1
    nid += 2
    bob = {}
    for side in ('R', 'L'):
        body_tags = swf.encode_tag(26, bytes([0x06]) + struct.pack('<HH', 1, glow_shape) + NUL)
        body_tags += swf.encode_tag(26, bytes([0x06]) + struct.pack('<HH', 2, shapes[side]) + NUL) + swf.encode_tag(1, b'')
        for f in range(1, frames):
            c, d = _move(2, int(math.sin(2 * math.pi * f / frames) * 30))
            body_tags += swf.encode_tag(c, d) + swf.encode_tag(1, b'')
        body_tags += swf.encode_tag(0, b'')
        defs.append((39, struct.pack('<HH', nid, frames) + body_tags))
        bob[side] = nid
        nid += 1
    labels = [('L', 'L'), ('R', 'R'), ('S', 'R'), ('F', 'R'), ('B', 'L'), ('WL', 'L'), ('WR', 'R'), ('WS', 'R'), ('WF', 'R'), ('WB', 'L')]
    pet = b''
    for i, (label, side) in enumerate(labels):
        if i:
            pet += swf.encode_tag(28, struct.pack('<H', 1))
        pet += swf.encode_tag(43, label.encode() + NUL)
        pet += swf.encode_tag(26, bytes([0x06]) + struct.pack('<HH', 1, bob[side]) + NUL)
        pet += swf.encode_tag(12, b'\x07\x00')        # stop()
        pet += swf.encode_tag(1, b'')
    pet += swf.encode_tag(0, b'')
    defs.append((39, struct.pack('<HH', nid, len(labels)) + pet))
    exp = (56, struct.pack('<H', 1) + struct.pack('<H', nid) + name.encode() + NUL)
    idx = next(i for i, (c, _) in enumerate(s.tags) if c == 1)
    s.tags = s.tags[:idx] + defs + [exp] + s.tags[idx:]
    swf.write_swf(s, lib_path)


# ----------------------------------------------------------------- sprite do Estagiario (drone de IA)

NPC_ANIMS = ['static', 'walk', 'run', 'hit', 'die', 'bonus', 'anim0', 'anim1', 'anim2']


def _move(depth, matrix_ty):
    """PlaceObject2 que move o objeto da profundidade (so troca a matriz)."""
    w = swf.BitWriter()
    _matrix_bits(w, None, None, 0, matrix_ty)
    return (26, bytes([0x05]) + struct.pack('<H', depth) + w.bytes())


def drone_sprite(path, img, frames=16):
    """Sprite de NPC: drone cubico flutuando (sobe e desce) com brilho ciano no chao.
    Origem (0,0) = ponto no chao; o drone paira na altura do peito de um personagem."""
    import math
    from PIL import ImageDraw
    body = img.convert('RGBA')
    glow = Image.new('RGBA', (64, 24), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((2, 2, 62, 22), fill=(40, 220, 235, 90))
    tags = [(9, b'\xff\xff\xff')]
    body_box = (-240, 240, -900, -420)      # ~24 x 24 unidades, pairando entre 21 e 45 acima do chao
    glow_box = (-180, 180, -60, 60)
    ids = {}
    nid = 1
    for side, im in (('R', body), ('L', body.transpose(Image.FLIP_LEFT_RIGHT))):
        b, sh = nid, nid + 1
        fitted_im, fitted = _fit(im, body_box, 'contain')
        tags += [_lossless(b, fitted_im), _bitmap_shape(sh, b, fitted_im.size, fitted)]
        ids[side] = sh
        nid += 2
    gb, gs = nid, nid + 1
    tags += [_lossless(gb, glow), _bitmap_shape(gs, gb, glow.size, glow_box)]
    nid += 2
    exports = []
    for side in ('R', 'L'):
        spr = nid
        nid += 1
        body_tags = swf.encode_tag(26, bytes([0x06]) + struct.pack('<HH', 1, gs) + NUL)
        body_tags += swf.encode_tag(26, bytes([0x06]) + struct.pack('<HH', 2, ids[side]) + NUL)
        body_tags += swf.encode_tag(1, b'')
        for f in range(1, frames):
            c, d = _move(2, int(math.sin(2 * math.pi * f / frames) * 50))
            body_tags += swf.encode_tag(c, d) + swf.encode_tag(1, b'')
        body_tags += swf.encode_tag(0, b'')
        tags.append((39, struct.pack('<HH', spr, frames) + body_tags))
        for a in NPC_ANIMS:
            exports.append((spr, a + side))
    tags.append((56, struct.pack('<H', len(exports)) + b''.join(struct.pack('<H', i) + n.encode() + NUL for i, n in exports)))
    tags += [(1, b''), (0, b'')]
    s = swf.Swf(b'CWS', 7, swf.rect(0, 550 * 20, 0, 400 * 20), 25 << 8, 1, tags)
    swf.write_swf(s, path)


# ----------------------------------------------------------------- tudo

def build(cfg, log=print):
    """cfg: dict com base_class, accessories [(simbolo, png, caixa)], sprites_xml_names."""
    base = cfg['base_class']
    imgs = concept_images()
    for client in CLIENTS:
        if not os.path.isdir(client):
            continue
        sp = os.path.join(client, 'clips', 'sprites')
        art = os.path.join(client, 'clips', 'artworks')
        # 1) sprites jogaveis = sprites da classe base (esqueleto oficial)
        import remodel
        for sex in (0, 1):
            # corpo remodelado a partir do sprite oficial da classe base (cores, visor, barba, cabelo, jaleco longo)
            remodel.labtechify(os.path.join(sp, f'{base * 10 + sex}.swf'), os.path.join(sp, f'{130 + sex}.swf'), female=bool(sex))
        # retratos (criacao, rosto, luta, grupo) a partir do boneco remodelado, no traco do jogo
        if client == CLIENTS[0]:
            sprite_portraits(sp, imgs)
        # 2) artes no mesmo enquadramento das originais da classe base
        jobs = [('breeds', f'{base}.swf', '13.swf', 'emblema', 'contain'),
                ('breeds/back', f'{base}.swf', '13.swf', 'medalhao_fundo', 'contain'),
                ('breeds/slide', f'{base * 10}.swf', '130.swf', 'medalhao_m', 'contain'),
                ('breeds/slide', f'{base * 10 + 1}.swf', '131.swf', 'medalhao_f', 'contain'),
                ('faces', f'{base * 10}.swf', '130.swf', 'busto_m', 'contain'),
                ('faces', f'{base * 10 + 1}.swf', '131.swf', 'busto_f', 'contain'),
                ('big', f'{base * 10}.swf', '130.swf', 'busto_m', 'contain'),
                ('big', f'{base * 10 + 1}.swf', '131.swf', 'busto_f', 'contain'),
                ('mini', f'{base * 10}.swf', '130.swf', 'rosto_m', 'cover'),
                ('mini', f'{base * 10 + 1}.swf', '131.swf', 'rosto_f', 'cover'),
                ('symbols', f'{base}.swf', '13.swf', 'emblema', 'contain')]
        for folder, src, dst, img, mode in jobs:
            bp = os.path.join(art, folder, src)
            if os.path.exists(bp) and img in imgs:
                try:
                    box = visible_box(bp) if folder == 'big' else None   # big/: encaixa na area desenhada
                    art_like(bp, imgs[img], os.path.join(art, folder, dst), mode, base, box)
                except Exception as e:  # uma arte com estrutura diferente nao pode travar o resto
                    log(f'  AVISO arte {folder}/{dst}: {e}; copiando a da classe base')
                    shutil.copy2(bp, os.path.join(art, folder, dst))
        # 3) acessorios Manopla (arma) e Caneca (escudo)
        lib = os.path.join(sp, 'accessories', 'a6.swf')
        if os.path.exists(lib):
            bak = lib + '.labtech.bak'
            if not os.path.exists(bak):
                shutil.copy2(lib, bak)
            items = [(name, Image.open(png).convert('RGBA'), box) for name, png, box in cfg['accessories']]
            add_accessories(bak, lib, items)
            if cfg.get('pet_symbol'):   # familiar Drone de IA ao lado do personagem
                add_pet(lib, cfg['pet_symbol'], Image.open(os.path.join(ART, 'gerado', 'drone.png')))
        # 3b) sprite do Estagiario (drone de IA)
        if cfg.get('drone_gfx'):
            drone_sprite(os.path.join(sp, f"{cfg['drone_gfx']}.swf"), Image.open(os.path.join(ART, 'gerado', 'drone.png')))
        # 4) core.swf e sprites.xml
        patch_core(client, base)
        xml = os.path.join(sp, 'sprites.xml')
        if os.path.exists(xml):
            txt = open(xml, encoding='utf-8', errors='replace').read()
            if 'id="130"' not in txt:
                txt = txt.replace('</type>', '<sprite id="130" name="LabTech" />\n<sprite id="131" name="LabTech" />\n</type>', 1)
                open(xml, 'w', encoding='utf-8').write(txt)
        log(f'  classe 13 no cliente: {client}')
