"""Gera as imagens do README (docs/imagens) a partir do cliente instalado: o LabTech em alta, a corrida com a
manopla, os medalhoes da criacao, o elenco do Bar das Celebridades e alguns retratos de dialogo.
As imagens mostram arte do jogo (Dofus (c) Ankama) renderizada localmente; servem so de ilustracao do projeto.
Uso: python panel/tools/labtech/imagens_readme.py"""
import concurrent.futures as cf
import glob
import os
import shutil
import struct
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'world', 'labtech')))
import swf  # noqa: E402
import content as C  # noqa: E402
import remodel  # noqa: E402
import classe13 as c13  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
CLIENT = os.path.join(ROOT, 'server', 'client-starloco', 'resources', 'app', 'retroclient')
SPR = os.path.join(CLIENT, 'clips', 'sprites')
BIG = os.path.join(CLIENT, 'clips', 'artworks', 'big')
OUT = os.path.join(ROOT, 'docs', 'imagens')
JAVA = os.path.join(ROOT, 'runtime', 'jdk21', 'bin', 'java.exe')
FFDEC = os.path.join(ROOT, 'runtime', 'ffdec', 'ffdec-cli.jar')
PERGAMINHO = ((238, 226, 196), (206, 186, 146))


def fonte(tam):
    for f in ('C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/arialbd.ttf', 'C:/Windows/Fonts/verdanab.ttf'):
        if os.path.exists(f):
            return ImageFont.truetype(f, tam)
    return ImageFont.load_default()


def fundo(w, h):
    """Pergaminho: degrade vertical com vinheta suave."""
    im = Image.new('RGB', (w, h))
    (r1, g1, b1), (r2, g2, b2) = PERGAMINHO
    d = ImageDraw.Draw(im)
    for y in range(h):
        k = y / max(1, h - 1)
        d.line([(0, y), (w, y)], fill=(int(r1 + (r2 - r1) * k), int(g1 + (g2 - g1) * k), int(b1 + (b2 - b1) * k)))
    vin = Image.new('L', (w, h), 0)
    ImageDraw.Draw(vin).rectangle([w * 0.04, h * 0.06, w * 0.96, h * 0.94], fill=255)
    vin = vin.filter(ImageFilter.GaussianBlur(min(w, h) * 0.08))
    escuro = Image.new('RGB', (w, h), (150, 128, 92))
    return Image.composite(im, escuro, vin)


def exports(path):
    s = swf.read_swf(path)
    ex = {}
    for c, d in s.tags:
        if c == 56:
            n, q = struct.unpack_from('<H', d, 0)[0], 2
            for _ in range(n):
                cid = struct.unpack_from('<H', d, q)[0]
                e = d.index(bytes(1), q + 2)
                ex[d[q + 2:e].decode('latin1')] = cid
                q = e + 1
    return s, ex


def inner_anim(s, cid):
    """As animacoes tem 1 quadro na raiz e o movimento num clipe de dentro: devolve esse clipe."""
    defs = remodel._defs(s.tags)
    for tc, td in remodel._sprite_children(defs[cid][1]):
        if tc == 26:
            ch = c13._parse_place2(td)['char']
            if ch in defs and defs[ch][0] == 39 and struct.unpack_from('<H', defs[ch][1], 2)[0] > 1:
                return ch
    return cid


def render(path, anim, frames=(1,), zoom=8, inner=False):
    """Renderiza quadros de uma animacao exportada; devolve lista de imagens recortadas (RGBA)."""
    s, ex = exports(path)
    nomes = [anim] if isinstance(anim, str) else list(anim)
    nome = next((n for n in nomes if n in ex), None)
    if nome is None:
        return []
    cid = inner_anim(s, ex[nome]) if inner else ex[nome]
    out = tempfile.mkdtemp(prefix='lt_img_')
    subprocess.run([JAVA, '-jar', FFDEC, '-selectid', str(cid), '-select', ','.join(map(str, frames)), '-zoom', str(zoom),
                    '-export', 'sprite', out, path], capture_output=True, timeout=900)
    ims = []
    for f in frames:
        g = glob.glob(os.path.join(out, f'DefineSprite_{cid}*', f'{f}.png'))
        if g:
            im = Image.open(g[0]).convert('RGBA')
            bb = im.getbbox()
            ims.append(im.crop(bb) if bb else im)
    shutil.rmtree(out, ignore_errors=True)
    return ims


def render_big(gfx):
    """Arte big/<gfx>.swf inteira (palco largo), recortada no que foi desenhado."""
    from PIL import ImageChops
    s = swf.read_swf(os.path.join(BIG, f'{gfx}.swf'))
    s.header_rect = swf.rect(-6000, 6000, -9000, 3000)
    tmp = tempfile.mkdtemp(prefix='lt_big_')
    src = os.path.join(tmp, 'a.swf')
    swf.write_swf(s, src)
    subprocess.run([JAVA, '-jar', FFDEC, '-format', 'frame:png', '-zoom', '2', '-export', 'frame', os.path.join(tmp, 'o'), src],
                   capture_output=True, timeout=900)
    p = os.path.join(tmp, 'o', '1.png')
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert('RGB')
    bb = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).point(lambda v: 255 if v > 10 else 0).getbbox()
    im = im.crop(bb) if bb else im
    # branco do palco -> transparente
    a = ImageChops.difference(im, Image.new('RGB', im.size, (255, 255, 255))).convert('L').point(lambda v: 255 if v > 6 else 0)
    im = im.convert('RGBA')
    im.putalpha(a)
    shutil.rmtree(tmp, ignore_errors=True)
    return im


def sombra(img, off=(6, 8), raio=6, alpha=90):
    base = Image.new('RGBA', (img.width + 40, img.height + 40), (0, 0, 0, 0))
    sh = Image.new('RGBA', img.size, (40, 25, 10, alpha))
    sh.putalpha(img.split()[3].point(lambda v: v * alpha // 255))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(raio)), (20 + off[0], 20 + off[1]))
    base.alpha_composite(img, (20, 20))
    return base


def cole(tela, img, cx, base_y):
    tela.alpha_composite(img, (int(cx - img.width / 2), int(base_y - img.height)))


def titulo(tela, texto, y, tam=44):
    d = ImageDraw.Draw(tela)
    f = fonte(tam)
    w = d.textlength(texto, font=f)
    x = (tela.width - w) / 2
    d.text((x + 2, y + 2), texto, font=f, fill=(90, 60, 30, 160))
    d.text((x, y), texto, font=f, fill=(74, 46, 20))


def img_labtech():
    jobs = [('130.swf', 'staticF'), ('130.swf', 'staticR'), ('131.swf', 'staticL'), ('131.swf', 'staticF')]
    with cf.ThreadPoolExecutor(4) as pool:
        res = list(pool.map(lambda j: render(os.path.join(SPR, j[0]), j[1], zoom=10), jobs))
    tela = fundo(1400, 620).convert('RGBA')
    titulo(tela, 'LabTech: a 13ª classe', 22)
    xs = [220, 520, 880, 1180]
    for x, ims in zip(xs, res):
        if ims:
            im = ims[0]
            k = 470 / im.height
            im = im.resize((int(im.width * k), 470), Image.LANCZOS)
            cole(tela, sombra(im), x, 612)
    drone = Image.open(os.path.join(C.ART_GERADO, 'drone.png')).convert('RGBA')
    drone.thumbnail((110, 110), Image.LANCZOS)
    cole(tela, sombra(drone), 700, 330)
    tela.convert('RGB').save(os.path.join(OUT, 'labtech.png'), optimize=True)


def img_corrida():
    ims = render(os.path.join(SPR, '130.swf'), 'runS', frames=(1, 3, 5, 7, 9, 11), zoom=6, inner=True)
    tela = fundo(1400, 360).convert('RGBA')
    titulo(tela, 'A manopla faz parte do braço: aparece parado, andando e correndo', 18, 34)
    for k, im in enumerate(ims):
        s = 250 / im.height
        im = im.resize((int(im.width * s), 250), Image.LANCZOS)
        cole(tela, sombra(im), 140 + k * 225, 350)
    tela.convert('RGB').save(os.path.join(OUT, 'corrida.png'), optimize=True)


def img_criacao():
    tela = fundo(1000, 560).convert('RGBA')
    titulo(tela, 'Tela de criação', 16, 38)
    for k, nome in enumerate(('medalhao_m', 'medalhao_f')):
        p = os.path.join(C.ART_GERADO, 'classe13', nome + '.png')
        if os.path.exists(p):
            im = Image.open(p).convert('RGBA')
            im.thumbnail((420, 460), Image.LANCZOS)
            cole(tela, sombra(im), 270 + k * 460, 548)
    tela.convert('RGB').save(os.path.join(OUT, 'criacao.png'), optimize=True)


def img_celebridades():
    celebs = C.CELEB_SPRITES
    with cf.ThreadPoolExecutor(6) as pool:
        res = list(pool.map(lambda c: render(os.path.join(SPR, f"{c['gfx']}.swf"), ('staticS', 'staticR', 'staticF'), zoom=5), celebs))
    cols, cw, ch = 5, 280, 300
    rows = (len(celebs) + cols - 1) // cols
    tela = fundo(cols * cw + 40, rows * ch + 110).convert('RGBA')
    titulo(tela, 'Bar das Celebridades (paródias)', 22, 40)
    d = ImageDraw.Draw(tela)
    f = fonte(20)
    for k, (c, ims) in enumerate(zip(celebs, res)):
        x0, y0 = 20 + (k % cols) * cw, 90 + (k // cols) * ch
        if ims:
            im = ims[0]
            im.thumbnail((cw - 30, ch - 70), Image.LANCZOS)
            cole(tela, sombra(im, off=(4, 5), raio=4), x0 + cw / 2, y0 + ch - 50)
        w = d.textlength(c['nome'], font=f)
        d.text((x0 + (cw - w) / 2, y0 + ch - 40), c['nome'], font=f, fill=(74, 46, 20))
    tela.convert('RGB').save(os.path.join(OUT, 'celebridades.png'), optimize=True)


def img_retratos():
    escolha = ['Homero Simplório', 'Rique Sanches', 'Capitão Pardal', 'Gatão da Destruição', 'Grandão Guarda-Caça']
    gfx = {c['nome']: c['gfx'] for c in C.CELEB_SPRITES}
    ids = [gfx[n] for n in escolha] + [9901]
    with cf.ThreadPoolExecutor(6) as pool:
        res = list(pool.map(render_big, ids))
    tela = fundo(1400, 400).convert('RGBA')
    titulo(tela, 'Retratos dos diálogos', 14, 36)
    for k, im in enumerate(res):
        if im is None:
            continue
        im.thumbnail((210, 300), Image.LANCZOS)
        cole(tela, sombra(im), 130 + k * 228, 388)
    tela.convert('RGB').save(os.path.join(OUT, 'retratos.png'), optimize=True)


def img_mapa():
    p = os.path.join(C.ART_GERADO, 'mundi_tile.png')
    if os.path.exists(p):
        im = Image.open(p).convert('RGB').crop((120, 30, 470, 280)).resize((700, 500), Image.LANCZOS)
        im.save(os.path.join(OUT, 'mapa-mundi.png'), optimize=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    for f in (img_labtech, img_corrida, img_criacao, img_celebridades, img_retratos, img_mapa):
        f()
        print('  ok', f.__name__)


if __name__ == '__main__':
    main()
