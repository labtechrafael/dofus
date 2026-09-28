"""Celebridades do bar com personagem proprio: cada uma e um sprite de NPC do jogo (nao as 12 classes)
recolorido para lembrar a pessoa. O sprite novo e gravado no cliente como clips/sprites/<gfx>.swf (a partir da
copia original), entao nada da Ankama vai para o repositorio: so a receita (base + trocas de cor) em content.py.

Regra de cor: {'h': (h0, h1), 's': (s0, s1), 'v': (v0, v1), 'to': '#RRGGBB'} (matiz em graus, pode dar a volta
em 360). Todas as cores da forma que caem na faixa ganham a matiz/saturacao do alvo e o brilho e reescalado pela
media do grupo, entao sombras e luzes do desenho original continuam."""
import colorsys
import os
import shutil
from collections import Counter

import swf
from remodel import color_offsets

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SHAPES = (2, 22, 32, 83)


def _hsv(rgb):
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    return h * 360, s, v


def _match(rule, rgb):
    h, s, v = _hsv(rgb)
    h0, h1 = rule.get('h', (0, 360))
    ok_h = (h0 <= h <= h1) if h0 <= h1 else (h >= h0 or h <= h1)
    s0, s1 = rule.get('s', (0, 1))
    v0, v1 = rule.get('v', (0, 1))
    return ok_h and s0 <= s <= s1 and v0 <= v <= v1


def palette(path):
    s = swf.read_swf(path)
    cnt = Counter()
    for c, d in s.tags:
        if c in SHAPES:
            try:
                for o in color_offsets(c, d):
                    cnt[tuple(d[o:o + 3])] += 1
            except Exception:
                pass
    return cnt


def recolor_sprite(src, dst, rules):
    """Copia src para dst trocando as cores pelas regras (a primeira regra que casar vale)."""
    s = swf.read_swf(src)
    pal = palette(src)
    groups = []
    for r in rules:
        cols = [(c, n) for c, n in pal.items() if _match(r, c)]
        tot = sum(n for _, n in cols) or 1
        ms = sum(_hsv(c)[1] * n for c, n in cols) / tot
        mv = sum(_hsv(c)[2] * n for c, n in cols) / tot
        th, ts, tv = _hsv(tuple(int(r['to'][i:i + 2], 16) for i in (1, 3, 5)))
        groups.append((r, ms or 1e-6, mv or 1e-6, th, ts, tv))

    def new_color(rgb):
        for r, ms, mv, th, ts, tv in groups:
            if _match(r, rgb):
                _, s_, v_ = _hsv(rgb)
                s2 = ts   # saturacao do alvo (branco puro tem s=0 e ficaria branco)
                v2 = min(1.0, v_ * tv / mv)
                return tuple(int(round(x * 255)) for x in colorsys.hsv_to_rgb(th / 360, s2, v2))
        return None

    tags, changed = [], 0
    for c, d in s.tags:
        if c in SHAPES:
            try:
                offs = color_offsets(c, d)
            except Exception:
                offs = []
            b = bytearray(d)
            for o in offs:
                n = new_color(tuple(b[o:o + 3]))
                if n:
                    b[o:o + 3] = bytes(n)
                    changed += 1
            d = bytes(b)
        tags.append((c, d))
    s.tags = tags
    swf.write_swf(s, dst)
    return changed


def _render_bust(sprite_path, frac=0.6, zoom=8):
    """Renderiza a pose parada do sprite com o JPEXS e devolve o busto (topo do corpo) como imagem."""
    import glob
    import struct
    import subprocess
    import tempfile
    from PIL import Image
    s = swf.read_swf(sprite_path)
    ex = {}
    for c, d in s.tags:
        if c == 56:
            n, q = struct.unpack_from('<H', d, 0)[0], 2
            for _ in range(n):
                cid = struct.unpack_from('<H', d, q)[0]
                e = d.index(bytes(1), q + 2)
                ex[d[q + 2:e].decode('latin1')] = cid
                q = e + 1
    anim = next((a for a in ('staticS', 'staticR', 'staticF', 'staticL') if a in ex), None)
    if anim is None:
        return None
    out = tempfile.mkdtemp(prefix='lt_bust_')
    subprocess.run([os.path.join(ROOT, 'runtime', 'jdk21', 'bin', 'java.exe'), '-jar', os.path.join(ROOT, 'runtime', 'ffdec', 'ffdec-cli.jar'),
                    '-selectid', str(ex[anim]), '-select', '1', '-zoom', str(zoom), '-export', 'sprite', out, sprite_path],
                   capture_output=True, timeout=600)
    found = glob.glob(os.path.join(out, f'DefineSprite_{ex[anim]}*', '1.png'))
    if not found:
        return None
    im = Image.open(found[0]).convert('RGBA')
    im = im.crop(im.getbbox())
    a = im.split()[3].point(lambda v: 255 if v > 200 else 0)   # fora a sombra no chao (translucida)
    im = im.crop(a.getbbox())
    im = im.crop((0, 0, im.width, int(im.height * frac)))
    shutil.rmtree(out, ignore_errors=True)
    return im.crop(im.getbbox())


def build_portraits(celebs, clients, extra=(), log=print):
    """Retrato do dialogo (artworks/big/<gfx>.swf): o do NPC base recolorido com as mesmas regras; se o NPC base
    nao tiver retrato, um busto renderizado do proprio sprite novo. extra = [(gfx, imagem PIL)] prontos."""
    import classe13
    for client in clients:
        big = os.path.join(client, 'clips', 'artworks', 'big')
        template = os.path.join(big, '9017.swf')
        if not os.path.isdir(big) or not os.path.exists(template):
            continue
        box = None
        feitos = 0
        for c in celebs:
            src = os.path.join(big, f"{c['base']}.swf")
            dst = os.path.join(big, f"{c['gfx']}.swf")
            if c.get('retrato') == 'oficial' and os.path.exists(src):
                if c.get('cores'):
                    recolor_sprite(src, dst, c['cores'])
                else:
                    shutil.copy2(src, dst)
            else:
                img = _render_bust(os.path.join(client, 'clips', 'sprites', f"{c['gfx']}.swf"))
                if img is None:
                    continue
                box = box or classe13.visible_box(template)
                classe13.art_like(template, img, dst, 'contain', None, box)
            feitos += 1
        for gfx, img in extra:
            box = box or classe13.visible_box(template)
            classe13.art_like(template, img, os.path.join(big, f'{gfx}.swf'), 'contain', None, box)
            feitos += 1
        log(f'  retratos de dialogo: {feitos} em {big}')


def build(celebs, clients, log=print):
    """celebs: lista de dicts com 'gfx' (novo id), 'base' (id do sprite do jogo) e 'cores' (regras)."""
    for client in clients:
        sp = os.path.join(client, 'clips', 'sprites')
        if not os.path.isdir(sp):
            continue
        feitos = 0
        for c in celebs:
            src = os.path.join(sp, f"{c['base']}.swf")
            if not os.path.exists(src):
                log(f"  AVISO: sprite base {c['base']} nao existe no cliente ({c['nome']})")
                continue
            dst = os.path.join(sp, f"{c['gfx']}.swf")
            if c.get('cores'):
                recolor_sprite(src, dst, c['cores'])
            else:
                shutil.copy2(src, dst)
            feitos += 1
        log(f'  celebridades: {feitos} sprites em {sp}')
