"""Remodela o sprite oficial do Feca no LabTech, direto nos vetores do Flash:
- recolore as cores padrao (jaleco branco, calca grafite, cabelo castanho-escuro, botas marrons);
- desenha pecas novas em vetor (visor ciano, barba, cabelo baguncado/cacheado, jaleco longo)
  e as encaixa DENTRO das partes existentes (cabeca, zona do cabelo, zona do quadril).
Esqueleto, animacoes, nomes de instancia e pontos de encaixe de itens nao mudam.
"""
import math
import struct

import swf

NUL = bytes(1)


# ----------------------------------------------------------------- leitura de formas (para recolorir)

class Bits:
    def __init__(self, data, pos=0):
        self.d, self.i = data, pos * 8

    def ub(self, n):
        v = 0
        for _ in range(n):
            v = (v << 1) | ((self.d[self.i >> 3] >> (7 - (self.i & 7))) & 1)
            self.i += 1
        return v

    def sb(self, n):
        v = self.ub(n)
        return v - (1 << n) if n and v >> (n - 1) else v

    def align(self):
        self.i = (self.i + 7) & ~7

    @property
    def byte(self):
        return self.i >> 3


def _skip_matrix(b):
    if b.ub(1):
        n = b.ub(5); b.ub(n); b.ub(n)
    if b.ub(1):
        n = b.ub(5); b.ub(n); b.ub(n)
    n = b.ub(5); b.ub(n); b.ub(n)
    b.align()


def _fill_styles(d, p, code, colors):
    n = d[p]; p += 1
    if n == 0xFF and code != 2:
        n = struct.unpack_from('<H', d, p)[0]; p += 2
    rgba = code in (32, 83)
    for _ in range(n):
        t = d[p]; p += 1
        if t == 0:
            colors.append(p); p += 4 if rgba else 3
        elif t in (0x10, 0x12, 0x13):
            b = Bits(d, p); _skip_matrix(b); p = b.byte
            ng = d[p] & 0x0F; p += 1
            for _ in range(ng):
                p += 1; colors.append(p); p += 4 if rgba else 3
            if t == 0x13:
                p += 2
        elif 0x40 <= t <= 0x43:
            p += 2
            b = Bits(d, p); _skip_matrix(b); p = b.byte
        else:
            raise ValueError(f'fill {t:#x}')
    return p


def _line_styles(d, p, code, colors):
    n = d[p]; p += 1
    if n == 0xFF:
        n = struct.unpack_from('<H', d, p)[0]; p += 2
    for _ in range(n):
        p += 2
        if code == 83:
            f1 = d[p]; f2 = d[p + 1]; p += 2
            if (f1 & 0x30) >> 4 == 2:
                p += 2
            if f2 & 0x08:
                p = _fill_styles(bytes([1]) + d[p:], 0, code, []) + p - 1  # estilo de preenchimento na linha
            else:
                colors.append(p); p += 4
        else:
            colors.append(p); p += 4 if code == 32 else 3
    return p


def color_offsets(code, d):
    """Offsets (no bytes da tag) de todas as cores solidas da forma, inclusive estilos novos no meio."""
    colors = []
    _, rl = swf.read_rect(d[2:])
    p = 2 + rl
    if code == 83:
        _, rl2 = swf.read_rect(d[p:])
        p += rl2 + 1
    p = _fill_styles(d, p, code, colors)
    p = _line_styles(d, p, code, colors)
    b = Bits(d, p)
    nf, nl = b.ub(4), b.ub(4)
    while True:
        if b.ub(1) == 0:
            flags = b.ub(5)
            if flags == 0:
                break
            if flags & 1:
                n = b.ub(5); b.sb(n); b.sb(n)
            if flags & 2:
                b.ub(nf)
            if flags & 4:
                b.ub(nf)
            if flags & 8:
                b.ub(nl)
            if flags & 16:
                b.align()
                p = _fill_styles(d, b.byte, code, colors)
                p = _line_styles(d, p, code, colors)
                b = Bits(d, p)
                nf, nl = b.ub(4), b.ub(4)
        else:
            straight = b.ub(1)
            n = b.ub(4) + 2
            if straight:
                if b.ub(1):
                    b.sb(n); b.sb(n)
                else:
                    b.ub(1); b.sb(n)
            else:
                b.sb(n); b.sb(n); b.sb(n); b.sb(n)
    return colors


def _labtech_color(col):
    """Regra de cor por matiz: laranja vivo -> branco/creme do jaleco; azul -> grafite;
    castanho medio (cabelo) -> castanho-escuro; amarelo -> ciano. Pele e contornos ficam."""
    import colorsys
    r, g, b = col
    h, sat, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    hd = h * 360
    if 18 <= hd <= 42 and 0.55 < sat <= 0.88 and 0.45 <= v <= 0.68:   # cabelo e couros castanhos -> castanho-escuro
        return (0x3B, 0x26, 0x18) if v >= 0.56 else (0x2E, 0x1D, 0x12)
    if 12 <= hd <= 45 and sat > 0.62 and v > 0.8:            # tunica laranja -> jaleco branco/creme
        k = 0.8 + 0.2 * v
        return (int(242 * k), int(240 * k), int(234 * k))
    if 12 <= hd <= 45 and sat > 0.65 and 0.68 < v <= 0.8:     # sombra do laranja -> sombra do jaleco
        return (196, 194, 186)
    if 185 <= hd <= 250 and sat > 0.2 and v < 0.85:          # azuis -> grafite
        return (int(40 + 40 * v), int(43 + 40 * v), int(50 + 42 * v))
    if 50 <= hd <= 65 and sat > 0.6 and v > 0.85:           # amarelo (fivela) -> ciano
        return (0x27, 0xD0, 0xDC)
    return None


def recolor(tags, mapping=None, tol=26):
    """Recolore todas as cores solidas das formas pela regra _labtech_color (mapping extra opcional)."""
    changed = 0
    out = []
    for c, d in tags:
        if c in (2, 22, 32, 83):
            try:
                offs = color_offsets(c, d)
            except Exception:
                out.append((c, d))
                continue
            d = bytearray(d)
            for o in offs:
                new = _labtech_color(tuple(d[o:o + 3]))
                if new:
                    d[o:o + 3] = bytes(new)
                    changed += 1
            d = bytes(d)
        out.append((c, d))
    return out, changed


# ----------------------------------------------------------------- formas novas (vetor)

class ShapeBuilder:
    """DefineShape3 com varios poligonos/curvas, cada um com cor RGBA e contorno opcional."""

    def __init__(self):
        self.parts = []   # (fill_rgba, line_rgba|None, line_w, [segmentos]) ; segmento = ('L', x, y) | ('Q', cx, cy, x, y) em twips

    def poly(self, pts, fill, line=None, width=10):
        segs = [('M',) + pts[0]] + [('L',) + p for p in pts[1:]] + [('L',) + pts[0]]
        self.parts.append((fill, line, width, segs))

    def circle(self, cx, cy, r, fill, line=None, width=10):
        segs, n = [], 8
        pts = [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n + 1)]
        segs.append(('M', int(pts[0][0]), int(pts[0][1])))
        for k in range(n):
            a = 2 * math.pi * (k + 0.5) / n
            k2 = r / math.cos(math.pi / n)
            segs.append(('Q', int(cx + k2 * math.cos(a)), int(cy + k2 * math.sin(a)), int(pts[k + 1][0]), int(pts[k + 1][1])))
        segs[-1] = ('Q', segs[-1][1], segs[-1][2], int(pts[0][0]), int(pts[0][1]))
        self.parts.append((fill, line, width, segs))

    def tag(self, shape_id):
        xs, ys = [], []
        for _, _, _, segs in self.parts:
            for s in segs:
                xs += [v for v in s[1::2]]
                ys += [v for v in s[2::2]]
        pad = 40
        bounds = swf.rect(int(min(xs)) - pad, int(max(xs)) + pad, int(min(ys)) - pad, int(max(ys)) + pad)
        fills = [p[0] for p in self.parts]
        lines = [(p[1], p[2]) for p in self.parts if p[1]]
        data = bytes([len(fills)]) + b''.join(bytes([0]) + bytes(f) for f in fills)
        data += bytes([len(lines)]) + b''.join(struct.pack('<H', w) + bytes(c) for c, w in lines)
        nfb = max(1, len(fills).bit_length())
        nlb = max(1, len(lines).bit_length()) if lines else 0
        w = swf.BitWriter()
        w.ub(nfb, 4); w.ub(nlb, 4)
        li = 0
        x = y = 0
        for idx, (fill, line, lw, segs) in enumerate(self.parts):
            mx, my = segs[0][1], segs[0][2]
            # StyleChange: MoveTo + FillStyle1 + LineStyle
            w.ub(0, 1)
            w.ub(0, 1)                       # StateNewStyles
            w.ub(1 if lines else 0, 1)       # StateLineStyle
            w.ub(1, 1)                       # StateFillStyle1
            w.ub(0, 1)                       # StateFillStyle0
            w.ub(1, 1)                       # StateMoveTo
            n = swf.nbits_signed(mx, my)
            w.ub(n, 5); w.sb(mx, n); w.sb(my, n)
            w.ub(idx + 1, nfb)
            if lines:
                if line:
                    li += 1
                    w.ub(li, nlb)
                else:
                    w.ub(0, nlb)
            x, y = mx, my
            for s in segs[1:]:
                if s[0] == 'L':
                    dx, dy = s[1] - x, s[2] - y
                    if dx == 0 and dy == 0:
                        continue
                    w.ub(1, 1); w.ub(1, 1)
                    nb = max(swf.nbits_signed(dx, dy), 2)
                    w.ub(nb - 2, 4)
                    w.ub(1, 1); w.sb(dx, nb); w.sb(dy, nb)
                    x, y = s[1], s[2]
                else:
                    cdx, cdy = s[1] - x, s[2] - y
                    adx, ady = s[3] - s[1], s[4] - s[2]
                    w.ub(1, 1); w.ub(0, 1)
                    nb = max(swf.nbits_signed(cdx, cdy, adx, ady), 2)
                    w.ub(nb - 2, 4)
                    w.sb(cdx, nb); w.sb(cdy, nb); w.sb(adx, nb); w.sb(ady, nb)
                    x, y = s[3], s[4]
        w.ub(0, 6)
        return (32, struct.pack('<H', shape_id) + bounds + data + w.bytes())


# ----------------------------------------------------------------- insercao dentro de sprites

def _sprite_children(d):
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


def place_tag(depth, char, sx=None, sy=None, tx=0, ty=0):
    w = swf.BitWriter()
    if sx is not None:
        w.ub(1, 1)
        n = max(swf.nbits_signed(int(sx * 65536), int(sy * 65536)), 2)
        w.ub(n, 5); w.sb(int(sx * 65536), n); w.sb(int(sy * 65536), n)
    else:
        w.ub(0, 1)
    w.ub(0, 1)
    n = swf.nbits_signed(int(tx), int(ty))
    w.ub(n, 5); w.sb(int(tx), n); w.sb(int(ty), n)
    return (26, bytes([0x06]) + struct.pack('<HH', depth, char) + w.bytes())


def add_to_sprite(tags, sprite_id, new_places, max_new_depth=True):
    """Insere PlaceObject2 no 1o quadro do sprite (profundidades acima das existentes, na ordem dada)."""
    out = []
    for c, d in tags:
        if c == 39 and struct.unpack_from('<H', d, 0)[0] == sprite_id:
            kids = _sprite_children(d)
            depths = [struct.unpack_from('<H', dd, 1)[0] for cc, dd in kids if cc == 26]
            base = max(depths or [0]) + 1
            first_show = next(i for i, (cc, _) in enumerate(kids) if cc == 1)
            ins = []
            for k, (char, sx, sy, tx, ty) in enumerate(new_places):
                ins.append(place_tag(base + k, char, sx, sy, tx, ty))
            kids = kids[:first_show] + ins + kids[first_show:]
            d = d[:4] + b''.join(swf.encode_tag(cc, dd) for cc, dd in kids)
        out.append((c, d))
    return out


def _pushes(d):
    """Valores empilhados (ActionPush) de uma DoAction, em ordem."""
    out, p = [], 0
    while p < len(d):
        op = d[p]
        if op < 0x80:
            p += 1
            continue
        ln = struct.unpack_from('<H', d, p + 1)[0]
        body = d[p + 3:p + 3 + ln]
        if op == 0x96:
            q = 0
            while q < len(body):
                t = body[q]; q += 1
                if t == 0:
                    e = body.index(0, q); out.append(body[q:e].decode('latin1')); q = e + 1
                elif t == 1:
                    out.append(struct.unpack_from('<f', body, q)[0]); q += 4
                elif t in (2, 3):
                    out.append(None)
                elif t == 4:
                    q += 1
                elif t == 5:
                    out.append(bool(body[q])); q += 1
                elif t == 6:
                    raw = body[q:q + 8]; out.append(struct.unpack('<d', raw[4:] + raw[:4])[0]); q += 8
                elif t == 7:
                    out.append(struct.unpack_from('<i', body, q)[0]); q += 4
                elif t == 8:
                    out.append(('c', body[q])); q += 1
                elif t == 9:
                    out.append(('c', struct.unpack_from('<H', body, q)[0])); q += 2
                else:
                    break
        p += 3 + ln
    return out


def shield_points(defs):
    """Sprites que encaixam o escudo: DoAction GAC.applyAccessory(this, 4, rotulo). -> {id: rotulo}"""
    out = {}
    for cid, (c, d) in defs.items():
        if c != 39:
            continue
        for tc, td in _sprite_children(d):
            if tc == 12 and b'applyAccessory' in td:
                v = _pushes(td)
                if len(v) >= 4 and v[2] == 'this' and v[3] == 3 and v[1] == 4 and isinstance(v[0], str):
                    out[cid] = v[0]
    return out


def _matrix(a, b, c, d, tx, ty):
    w = swf.BitWriter()
    if (a, d) != (1.0, 1.0):
        w.ub(1, 1)
        n = max(swf.nbits_signed(int(a * 65536), int(d * 65536)), 2)
        w.ub(n, 5); w.sb(int(a * 65536), n); w.sb(int(d * 65536), n)
    else:
        w.ub(0, 1)
    if b or c:
        w.ub(1, 1)
        n = max(swf.nbits_signed(int(b * 65536), int(c * 65536)), 2)
        w.ub(n, 5); w.sb(int(b * 65536), n); w.sb(int(c * 65536), n)
    else:
        w.ub(0, 1)
    n = swf.nbits_signed(int(tx), int(ty))
    w.ub(n, 5); w.sb(int(tx), n); w.sb(int(ty), n)
    return w.bytes()


GAUNTLET_DEPTH = 3000   # profundidade do clipe da manopla = ponto do escudo + isto
GAUNTLET_X = 0.8        # a outra mao fica um pouco mais perto do corpo que o espelho exato
G_OUT = (0x2A, 0x1C, 0x12, 255)
G_LEATHER = (0x6B, 0x3D, 0x16, 255)
G_BRASS = (0xC8, 0x8A, 0x2E, 255)
G_BRASS_D = (0x8A, 0x5A, 0x1E, 255)
G_CORE = (0x27, 0xD0, 0xDC, 255)
G_CORE_L = (0xB8, 0xF6, 0xFF, 255)


def _gauntlet(sb, flip=False, k=1.0):
    """Manopla Gambiarra em vetor (luva fechada de lado): punho de couro, mao de latao com dedos e polegar,
    nucleo ciano. Contorno escuro como o traco dos sprites do jogo."""
    s = -1 if flip else 1
    w = int(12 * k) or 1

    def P(pts):
        return [(int(s * x * k), int(y * k)) for x, y in pts]

    def C(x, y, r, col):
        sb.circle(int(s * x * k), int(y * k), int(r * k), col, G_OUT, w)

    sb.poly(P([(-150, -62), (-62, -80), (-62, 80), (-150, 64)]), G_LEATHER, G_OUT, w)          # punho
    sb.poly(P([(-62, -92), (58, -98), (104, -70), (116, -18), (110, 58), (78, 92), (-62, 88)]), G_BRASS, G_OUT, w)  # mao
    for y in (-62, -18, 28):                                                                    # dedos
        C(102, y, 24, G_BRASS)
    sb.poly(P([(-24, 22), (48, 14), (62, 44), (-14, 58)]), G_BRASS_D, G_OUT, w)                # polegar
    C(-8, -34, 28, G_CORE)                                                                      # nucleo
    sb.circle(int(s * -16 * k), int(-42 * k), int(9 * k), G_CORE_L)

def _mat_mul(M, m):
    A, B, C, D, TX, TY = M
    a, b, c, d, tx, ty = m
    return (A * a + C * b, B * a + D * b, A * c + C * d, B * c + D * d, A * tx + C * ty + TX, B * tx + D * ty + TY)


def _first_places(defs, sid):
    import classe13 as c13
    out = []
    for tc, td in _sprite_children(defs[sid][1]):
        if tc == 1:
            break
        if tc == 26:
            pl = c13._parse_place2(td)
            if pl['char'] is not None:
                out.append(pl)
    return out


def _skin_box(defs, sid, depth=0):
    """Caixa (coordenadas do sprite) das formas cor de pele alcancaveis no 1o quadro, ate 2 niveis."""
    import classe13 as c13
    boxes = []
    for pl in _first_places(defs, sid):
        ch = pl['char']
        if ch not in defs:
            continue
        if defs[ch][0] == 39:
            if depth < 2:
                b = _skin_box(defs, ch, depth + 1)
                if b:
                    boxes.append(c13._apply(pl['matrix'], b))
        elif _is_skin(defs, ch):
            boxes.append(c13._apply(pl['matrix'], _bounds(defs, ch)))
    if not boxes:
        return None
    return (min(b[0] for b in boxes), max(b[1] for b in boxes), min(b[2] for b in boxes), max(b[3] for b in boxes))


def _arm_parts(defs, max_size=8 * 20):
    """Partes pequenas do corpo com pele (maos, antebracos): id -> caixa da pele."""
    out = {}
    for cid, (c, d) in defs.items():
        if c == 39:
            b = _skin_box(defs, cid)
            if b and b[1] - b[0] <= max_size and b[3] - b[2] <= max_size:
                out[cid] = b
    return out


ARM_COLORS = {
    'mao': ((0xC8, 0x8A, 0x2E), (0x8A, 0x5A, 0x1E)),        # latao
    'antebraco': ((0xB0, 0x6A, 0x30), (0x7A, 0x45, 0x1E)),  # cobre
}


def _metal(role):
    import colorsys
    light, dark = ARM_COLORS[role]

    def fn(col):
        r, g, b = col
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if 12 <= h * 360 <= 45 and 0.12 <= s <= 0.75 and v >= 0.55:
            return light if v >= 0.9 else dark
        return None
    return fn


def _recolored_shape(code, d, new_id, fn):
    offs = color_offsets(code, d)
    b = bytearray(d)
    b[0:2] = struct.pack('<H', new_id)
    for o in offs:
        new = fn(tuple(b[o:o + 3]))
        if new:
            b[o:o + 3] = bytes(new)
    return code, bytes(b)


def _strip_name(pl):
    """Remove o nome de instancia (zonas de cor 'c...' seriam tingidas pelo cliente por cima do metal)."""
    rest = pl['rest']
    fl = pl['flags']
    if not fl & 0x20:
        return fl, rest
    p = 0
    head = b''
    if fl & 0x08:   # cxform com alfa: pula os bits
        bits = Bits(rest, 0)
        ha, hm = bits.ub(1), bits.ub(1)
        n = bits.ub(4)
        bits.ub(n * 4 * (ha + hm))
        p = (bits.i + 7) // 8
        head = rest[:p]
    if fl & 0x10:
        head += rest[p:p + 2]
        p += 2
    e = rest.index(0, p)
    return fl & ~0x20, head + rest[e + 1:]


def _arm_copy(defs, sid, role, nid, k, top=True, cache=None):
    """Copia o sprite de uma parte do braco com a pele pintada de metal (e maior k vezes, no topo).
    Devolve (novo_id, novas_defs, proximo_id)."""
    import classe13 as c13
    cache = {} if cache is None else cache
    fn = _metal(role)
    new_defs = []
    box = _skin_box(defs, sid) if top else None
    cx, cy = ((box[0] + box[1]) / 2, (box[2] + box[3]) / 2) if box else (0, 0)
    kids = _sprite_children(defs[sid][1])
    out = []
    scaled = set()
    max_depth = 0
    first_frame_done = False
    for tc, td in kids:
        if tc == 26:
            pl = c13._parse_place2(td)
            dep = pl['depth']
            max_depth = max(max_depth, dep)
            ch = pl['char']
            if ch is not None and ch in defs:
                if defs[ch][0] == 39:
                    key = ('s', ch)
                    if key not in cache:
                        new_sub, dd, nid = _arm_copy(defs, ch, role, nid, 1.0, False, cache)
                        new_defs += dd
                        cache[key] = new_sub
                    new_ch = cache[key]
                elif defs[ch][0] in (2, 22, 32, 83):
                    key = ('f', ch)
                    if key not in cache:
                        new_defs.append(_recolored_shape(defs[ch][0], defs[ch][1], nid, fn))
                        cache[key] = nid
                        nid += 1
                    new_ch = cache[key]
                else:
                    new_ch = ch
                fl, rest = _strip_name(pl)
                a, b, c_, d_, tx, ty = pl['matrix']
                if top:
                    a, b, c_, d_, tx, ty = k * a, k * b, k * c_, k * d_, k * tx + (1 - k) * cx, k * ty + (1 - k) * cy
                    scaled.add(dep)
                td = bytes([fl | 0x04]) + struct.pack('<HH', dep, new_ch) + _matrix(a, b, c_, d_, tx, ty) + rest
            elif ch is None and dep in scaled and pl['flags'] & 0x04:
                a, b, c_, d_, tx, ty = pl['matrix']
                fl, rest = _strip_name(pl)
                td = bytes([fl]) + struct.pack('<H', dep) + _matrix(k * a, k * b, k * c_, k * d_, k * tx + (1 - k) * cx,
                                                                   k * ty + (1 - k) * cy) + rest
        elif tc == 1 and top and not first_frame_done and box:
            first_frame_done = True
            sb = ShapeBuilder()
            _arm_decor(sb, role, box, k)
            if sb.parts:
                new_defs.append(sb.tag(nid))
                out.append((26, bytes([0x06]) + struct.pack('<HH', max_depth + 1, nid) + NUL))
                nid += 1
        out.append((tc, td))
    new_id = nid
    nid += 1
    frames = struct.unpack_from('<H', defs[sid][1], 2)[0]
    new_defs.append((39, struct.pack('<HH', new_id, frames) + b''.join(swf.encode_tag(tc, td) for tc, td in out)))
    return new_id, new_defs, nid


def _arm_decor(sb, role, box, k):
    """Detalhes da manopla: nucleo ciano no dorso da mao; tira de couro e 3 gemas (os nucleos) no antebraco."""
    x0, x1, y0, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = (x1 - x0) * k, (y1 - y0) * k
    r = max(10, int(min(w, h) * 0.2))
    line = max(6, r // 3)
    if role == 'mao':
        sb.circle(int(cx), int(cy), r, G_CORE, G_OUT, line)
        sb.circle(int(cx - r * 0.35), int(cy - r * 0.35), max(4, r // 3), G_CORE_L)
    else:
        vertical = h >= w
        sw = max(8, int(min(w, h) * 0.18))
        if vertical:
            yb = cy - h * 0.34
            sb.poly([(int(cx - w / 2), int(yb - sw / 2)), (int(cx + w / 2), int(yb - sw / 2)),
                     (int(cx + w / 2), int(yb + sw / 2)), (int(cx - w / 2), int(yb + sw / 2))], G_LEATHER, G_OUT, line)
            gems = [(cx, cy - h * 0.08), (cx, cy + h * 0.14), (cx, cy + h * 0.34)]
        else:
            xb = cx - w * 0.34
            sb.poly([(int(xb - sw / 2), int(cy - h / 2)), (int(xb + sw / 2), int(cy - h / 2)),
                     (int(xb + sw / 2), int(cy + h / 2)), (int(xb - sw / 2), int(cy + h / 2))], G_LEATHER, G_OUT, line)
            gems = [(cx - w * 0.08, cy), (cx + w * 0.14, cy), (cx + w * 0.34, cy)]
        gr = max(6, int(min(w, h) * 0.13))
        for (gx, gy), col in zip(gems, [(0xE0, 0x30, 0x30, 255), (0x30, 0xC0, 0x50, 255), (0x9A, 0x40, 0xD0, 255)]):
            sb.circle(int(gx), int(gy), gr, col, G_OUT, max(4, line // 2))


# Animacoes que so existem em outras classes. O LabTech usa feiticos das 12 classes: se o cliente pede uma
# animacao que o boneco nao tem, ele fica esperando o fim dela e a luta trava. Cada nome aponta para uma
# animacao equivalente do boneco (que chama applyEnd/applyAnim no fim, como a original).
ANIM_ALIASES = {
    'anim18endL': 'anim18EndL', 'anim18endR': 'anim18EndR',             # Enutrof, Xelor
    'anim8L_CLIP': 'anim8L',                                             # Cra, Sadida, Sacrier, Pandawa
    'spGo0L': 'runL', 'spGo0R': 'runR', 'spShoot0L': 'anim1L', 'spShoot0R': 'anim1R',   # Ecaflip
    'spBack0L': 'anim1L', 'spBack0R': 'anim1R', 'spEnd0L': 'staticL', 'spEnd0R': 'staticR',
    'static_CL': 'staticL', 'static_CR': 'staticR', 'walk_CL': 'walkL', 'walk_CR': 'walkR',   # Pandawa carregando
    'run_CL': 'runL', 'run_CR': 'runR', 'hit_CL': 'hitL', 'hit_CR': 'hitR', 'die_CL': 'dieL', 'die_CR': 'dieR',
    'carring_CL': 'staticL', 'carring_CR': 'staticR', 'carringR': 'anim1R',
    'carringThrow_CL': 'anim1L', 'carringThrow_CR': 'anim1R', 'carringEnd_CL': 'anim1L', 'carringEnd_CR': 'anim1R',
}


def add_anim_aliases(tags):
    """Exporta os nomes de ANIM_ALIASES que faltam, apontando para o sprite da animacao equivalente."""
    ex = {}
    for c, d in tags:
        if c == 56:
            n, q = struct.unpack_from('<H', d, 0)[0], 2
            for _ in range(n):
                cid = struct.unpack_from('<H', d, q)[0]
                e = d.index(NUL, q + 2)
                ex[d[q + 2:e].decode('latin1')] = cid
                q = e + 1
    novos = [(name, ex[alvo]) for name, alvo in ANIM_ALIASES.items() if name not in ex and alvo in ex]
    if not novos:
        return tags
    tag = (56, struct.pack('<H', len(novos)) + b''.join(struct.pack('<H', cid) + name.encode() + NUL for name, cid in novos))
    last = max(i for i, (c, _) in enumerate(tags) if c == 56)
    return tags[:last + 1] + [tag] + tags[last + 1:]


def _swap_char(td, new_id):
    """PlaceObject2 com desenho: troca o id do desenho (bytes 3-4)."""
    t = bytearray(td)
    t[3:5] = struct.pack('<H', new_id)
    return bytes(t)


def _arm_roles(disp, points, parts):
    """No quadro atual: {profundidade: 'mao'|'antebraco'} do braco oposto ao escudo."""
    shield = [e['m'] for e in disp.values() if e['ch'] in points]
    if not shield:
        return {}
    sx = shield[0][4]
    cand = []
    for dep, e in disp.items():
        if e['ch'] in parts:
            x0, x1, y0, y1 = parts[e['ch']]
            m = e['m']
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            cand.append((dep, m[0] * cx + m[2] * cy + m[4], m[1] * cx + m[3] * cy + m[5]))
    if not cand:
        return {}
    low = max(c[2] for c in cand)
    hands = [c for c in cand if c[2] >= low - 3 * 20]
    hand = max(hands, key=lambda c: abs(c[1] - sx))
    if abs(hand[1] - sx) <= 2 * 20:
        return {}
    roles = {hand[0]: 'mao'}
    fore = [c for c in cand if c[0] != hand[0] and hand[2] - 8 * 20 <= c[2] < hand[2] and abs(c[1] - hand[1]) <= 5 * 20]
    if fore:
        f = min(fore, key=lambda c: (c[1] - hand[1]) ** 2 + (c[2] - hand[2]) ** 2)
        roles[f[0]] = 'antebraco'
    return roles


def add_gauntlet(tags, k_hand=1.35, k_fore=1.25):
    """A manopla e o proprio braco: nos clipes de corpo que encaixam o escudo, a mao e o antebraco do lado oposto
    ao escudo sao trocados (na mesma profundidade, seguindo a animacao) por copias pintadas de latao/cobre, um
    pouco maiores, com o nucleo ciano e as gemas."""
    import classe13 as c13
    defs = _defs(tags)
    points = shield_points(defs)
    parts = _arm_parts(defs)
    if not points or not parts:
        return tags, 0
    nid = next_id(tags)
    copies, new_defs = {}, []
    swapped = 0

    def copy_for(sid, role):
        nonlocal nid
        if (sid, role) not in copies:
            new_id, dd, nid = _arm_copy(defs, sid, role, nid, k_hand if role == 'mao' else k_fore)
            new_defs.extend(dd)
            copies[(sid, role)] = new_id
        return copies[(sid, role)]

    out = []
    for c, d in tags:
        if c == 39:
            kids = _sprite_children(d)
            if any(tc == 26 and c13._parse_place2(td)['char'] in points for tc, td in kids):
                # Cada parte do corpo fica na sua camada (profundidade) durante a animacao inteira. A mao e o
                # antebraco da manopla sao escolhidos por posicao no primeiro quadro em que aparecem e, dai em
                # diante, TUDO que for desenhado naquelas camadas vira metal (braco levantado, correndo etc.).
                disp, new = {}, []
                layer, hist = {}, {}   # camada -> papel; camada -> [indices das colocacoes com desenho]
                for tc, td in kids:
                    if tc == 26:
                        pl = c13._parse_place2(td)
                        dep, fl = pl['depth'], pl['flags']
                        if fl & 0x02:
                            old = disp.get(dep)
                            m = pl['matrix'] if fl & 0x04 else (old['m'] if old and fl & 0x01 else (1, 0, 0, 1, 0, 0))
                            disp[dep] = {'ch': pl['char'], 'm': m}
                            hist.setdefault(dep, []).append(len(new))
                            if dep in layer and pl['char'] in parts:
                                td = _swap_char(td, copy_for(pl['char'], layer[dep]))
                                swapped += 1
                        elif dep in disp and fl & 0x04:
                            disp[dep]['m'] = pl['matrix']
                    elif tc in (5, 28):
                        disp.pop(struct.unpack_from('<H', td, 2 if tc == 5 else 0)[0], None)
                    elif tc == 1:
                        faltam = {'mao', 'antebraco'} - set(layer.values())
                        if faltam:
                            for dep, role in _arm_roles(disp, points, parts).items():
                                if role in faltam and dep not in layer:
                                    layer[dep] = role
                                    for i in hist.get(dep, []):   # inclusive o que ja foi desenhado antes
                                        ch = c13._parse_place2(new[i][1])['char']
                                        if ch in parts:
                                            new[i] = (26, _swap_char(new[i][1], copy_for(ch, role)))
                                            swapped += 1
                    new.append((tc, td))
                d = d[:4] + b''.join(swf.encode_tag(tc, td) for tc, td in new)
        out.append((c, d))
    first = next(i for i, (c, _) in enumerate(out) if c in (39, 1))
    return out[:first] + new_defs + out[first:], swapped


U = 20  # 1 unidade = 20 twips

PALETTE = {
    (0xFA, 0x95, 0x2F): (0xF2, 0xF0, 0xEA),   # tunica laranja -> jaleco branco
    (0xBF, 0x69, 0x15): (0xC9, 0xC7, 0xC0),   # sombra laranja -> sombra do jaleco
    (0x40, 0x6F, 0x96): (0x3A, 0x3D, 0x45),   # azul -> calca/gola grafite
    (0x68, 0x76, 0xAC): (0x4A, 0x4E, 0x58),
    (0x9E, 0x61, 0x24): (0x3B, 0x26, 0x18),   # cabelo -> castanho-escuro
    (0xFF, 0xFF, 0x33): (0x27, 0xD0, 0xDC),   # fivela amarela -> detalhe ciano
}
HAIR = (0x3B, 0x26, 0x18, 255)
BEARD = (0x5A, 0x3A, 0x22, 230)
FRAME = (0x26, 0x2B, 0x33, 255)
LENS = (0x27, 0xD0, 0xDC, 255)
SHINE = (0xB8, 0xF6, 0xFF, 255)
SKIN = [(0xFF, 0xCE, 0x8C), (0xFE, 0xBF, 0x74)]


def _defs(tags):
    return {struct.unpack_from('<H', d, 0)[0]: (c, d) for c, d in tags if c in (2, 22, 32, 83, 39, 46)}


def _kids(d):
    import classe13
    out = []
    for c, dd in _sprite_children(d):
        if c == 1:
            break
        if c == 26:
            pl = classe13._parse_place2(dd)
            name = ''
            if pl['flags'] & 0x20 and not pl['flags'] & 0x18:
                name = pl['rest'][:pl['rest'].index(NUL)].decode('latin1')
            out.append((pl['depth'], pl['char'], name))
    return out


def _bounds(defs, cid):
    c, d = defs[cid]
    return tuple(swf.read_rect(d[2:])[0])


def _is_skin(defs, cid):
    c, d = defs.get(cid, (None, None))
    if c not in (2, 22, 32, 83):
        return False
    try:
        cols = [tuple(d[o:o + 3]) for o in color_offsets(c, d)]
    except Exception:
        return False
    return any(sum(abs(a - b) for a, b in zip(col, s)) < 20 for col in cols for s in SKIN)


def _visor(sb, face, side):
    x0, x1, y0, y1 = face
    h = y1 - y0
    ye = y0 + h * 0.40
    hv = max(1.5 * U, h * 0.22)
    mid = (x0 + x1) / 2
    if side == 'F':
        a, b = x0 + (x1 - x0) * 0.04, x1 - (x1 - x0) * 0.04
    elif side in ('R', 'S'):
        a, b = mid - (x1 - x0) * 0.15, x1 + 0.4 * U
    elif side == 'L':
        a, b = x0 - 0.4 * U, mid + (x1 - x0) * 0.15
    else:  # B: so a alca por tras da cabeca
        sb.poly([(int(x0 - 0.2 * U), int(ye)), (int(x1 + 0.2 * U), int(ye)), (int(x1 + 0.2 * U), int(ye + 0.7 * U)),
                 (int(x0 - 0.2 * U), int(ye + 0.7 * U))], FRAME)
        return
    pad = 0.35 * U
    sb.poly([(int(a - pad), int(ye - pad)), (int(b + pad), int(ye - pad)), (int(b + pad), int(ye + hv + pad)),
             (int(a - pad), int(ye + hv + pad))], FRAME)
    sb.poly([(int(a), int(ye)), (int(b), int(ye)), (int(b), int(ye + hv)), (int(a), int(ye + hv))], LENS)
    sb.poly([(int(a + (b - a) * 0.12), int(ye + hv * 0.15)), (int(a + (b - a) * 0.45), int(ye + hv * 0.15)),
             (int(a + (b - a) * 0.38), int(ye + hv * 0.45)), (int(a + (b - a) * 0.10), int(ye + hv * 0.45))], SHINE)
    # alca do visor ate o lado da cabeca
    if side in ('R', 'S'):
        sb.poly([(int(x0 - 0.2 * U), int(ye + hv * 0.3)), (int(a), int(ye + hv * 0.3)), (int(a), int(ye + hv * 0.75)),
                 (int(x0 - 0.2 * U), int(ye + hv * 0.75))], FRAME)
    elif side == 'L':
        sb.poly([(int(b), int(ye + hv * 0.3)), (int(x1 + 0.2 * U), int(ye + hv * 0.3)), (int(x1 + 0.2 * U), int(ye + hv * 0.75)),
                 (int(b), int(ye + hv * 0.75))], FRAME)


def _beard(sb, face, side):
    """Barba curta: faixa fina contornando o queixo (nao cobre a boca)."""
    x0, x1, y0, y1 = face
    h, w = y1 - y0, x1 - x0
    if side == 'F':
        pts = [(x0 + w * 0.18, y0 + h * 0.74), (x0 + w * 0.3, y1 - h * 0.1), (x0 + w * 0.5, y1 - h * 0.02),
               (x1 - w * 0.3, y1 - h * 0.1), (x1 - w * 0.18, y0 + h * 0.74), (x1 - w * 0.24, y1 + h * 0.03),
               (x0 + w * 0.5, y1 + h * 0.1), (x0 + w * 0.24, y1 + h * 0.03)]
    elif side in ('R', 'S'):
        pts = [(x0 + w * 0.42, y0 + h * 0.72), (x0 + w * 0.55, y1 - h * 0.08), (x1 - w * 0.12, y1 - h * 0.06),
               (x1 - w * 0.05, y1 + h * 0.04), (x0 + w * 0.5, y1 + h * 0.08), (x0 + w * 0.36, y1 - h * 0.05)]
    elif side == 'L':
        pts = [(x1 - w * 0.42, y0 + h * 0.72), (x1 - w * 0.55, y1 - h * 0.08), (x0 + w * 0.12, y1 - h * 0.06),
               (x0 + w * 0.05, y1 + h * 0.04), (x1 - w * 0.5, y1 + h * 0.08), (x1 - w * 0.36, y1 - h * 0.05)]
    else:
        return
    sb.poly([(int(x), int(y)) for x, y in pts], BEARD)


def _spikes(sb, hair):
    """Cabelo baguncado: poucas mechas curtas e tortas saindo do topo."""
    # Uma peca so: franja em zigue-zague presa ao domo do cabelo (base bem dentro do cabelo, pontas pouco para fora),
    # para nao ficar "coroa" solta acima da cabeca.
    x0, x1, y0, y1 = hair
    w = x1 - x0
    rx = w * 0.46
    ry = min(w * 0.46, (y1 - y0) * 0.6)
    cx, cy = (x0 + x1) / 2, y0 + ry

    def at(deg, k):
        a = math.radians(deg)
        return cx + math.cos(a) * rx * k, cy + math.sin(a) * ry * k

    start, end, n = 200, 340, 7
    outer = []
    for i in range(n * 2 + 1):
        deg = start + (end - start) * i / (n * 2)
        if i % 2:   # ponta, inclinada para o lado em que o cabelo "cai"
            tilt = (deg - 270) * 0.25
            outer.append(at(deg + tilt, 1.16 + 0.05 * ((i // 2) % 2)))
        else:       # vale (um pouco para dentro do contorno)
            outer.append(at(deg, 0.95))
    inner = [at(deg, 0.62) for deg in (end, 305, 270, 235, start)]
    sb.poly([(int(x), int(y)) for x, y in outer + inner], HAIR)


def _curls(sb, hair, face):
    """Cabelo cacheado volumoso: cachos grandes sobrepostos no contorno e descendo ate os ombros."""
    x0, x1, y0, y1 = hair
    cx = (x0 + x1) / 2
    w = x1 - x0
    fy1 = face[3] if face else y1
    r = 1.45 * U
    # contorno superior (so levemente acima do cabelo original)
    for k in range(5):
        a = math.pi * (1.1 + 0.8 * k / 4)
        sb.circle(cx + math.cos(a) * w * 0.52, y0 + 1.2 * U + math.sin(a) * 1.1 * U, r, HAIR)
    # laterais descendo (volume para fora do rosto)
    for side in (-1, 1):
        yy = y0 + 1.6 * U
        k = 0
        while yy < fy1 + 3.5 * U:
            sb.circle(cx + side * (w * 0.52 + 0.3 * U + (0.4 * U if k % 2 else 0)), yy, r * (1.0 if k % 2 else 1.12), HAIR)
            yy += 1.35 * U
            k += 1


def labtechify(src, dst, female=False, coat_scale=1.8):
    s = swf.read_swf(src)
    tags, changed = recolor(s.tags, PALETTE)
    defs = _defs(tags)
    nid = next_id(tags)
    added = 0
    new_defs = []
    for cid, (c, d) in list(defs.items()):
        if c != 39:
            continue
        kids = _kids(d)
        names = [n for _, _, n in kids]
        hair_kids = [(dep, ch, n) for dep, ch, n in kids if 'Cheveux' in n]
        # ---- cabeca: visor + barba
        if hair_kids:
            side = hair_kids[0][2].split('_')[-2] if hair_kids[0][2].count('_') >= 2 else 'F'
            face_ch = next((ch for dep, ch, n in kids if not n and ch in defs and _is_skin(defs, ch)), None)
            if face_ch:
                face = _bounds(defs, face_ch)
                sb = ShapeBuilder()
                if not female:
                    _beard(sb, face, side)
                _visor(sb, face, side)
                if sb.parts:
                    new_defs.append(sb.tag(nid))
                    tags = add_to_sprite(tags, cid, [(nid, None, None, 0, 0)])
                    nid += 1
                    added += 1
            # ---- cabelo: dentro da zona de cor (segue a cor escolhida pelo jogador)
            top = min(hair_kids, key=lambda k: _bounds(defs, _kids(defs[k[1]][1])[0][1])[2] if defs.get(k[1], (0,))[0] == 39 and _kids(defs[k[1]][1]) else 0)
            zone = top[1]
            if defs.get(zone, (0,))[0] == 39 and _kids(defs[zone][1]):
                inner = _kids(defs[zone][1])[0][1]
                if inner in defs and defs[inner][0] != 39:
                    hb = _bounds(defs, inner)
                    sb = ShapeBuilder()
                    if female:
                        _curls(sb, hb, _bounds(defs, face_ch) if face_ch else None)
                    else:
                        _spikes(sb, hb)
                    new_defs.append(sb.tag(nid))
                    tags = add_to_sprite(tags, zone, [(nid, None, None, 0, 0)])
                    nid += 1
                    added += 1
        # ---- quadril: jaleco longo (copia esticada da zona de cor do quadril)
        for dep, ch, n in kids:
            if n.endswith('Bassin') and defs.get(ch, (0,))[0] == 39:
                zk = _kids(defs[ch][1])
                if zk and zk[0][1] in defs and defs[zk[0][1]][0] != 39:
                    b = _bounds(defs, zk[0][1])
                    ty = b[2] - b[2] * coat_scale
                    tags = add_to_sprite(tags, ch, [(zk[0][1], 1.0, coat_scale, 0, ty)])
                    added += 1
        defs = _defs(tags)
    first_show = next(i for i, (c, _) in enumerate(tags) if c == 1)
    # formas novas antes do primeiro quadro, e antes do primeiro sprite (definidas antes de qualquer uso)
    first_sprite = next(i for i, (c, _) in enumerate(tags) if c == 39)
    at = min(first_show, first_sprite)
    tags = tags[:at] + new_defs + tags[at:]
    # manopla no corpo (na mao oposta ao escudo), sempre visivel, independente da arma equipada
    import os
    import classe13
    from PIL import Image
    tags, n = add_gauntlet(tags)
    added += n
    tags = add_anim_aliases(tags)
    s.tags = tags
    swf.write_swf(s, dst)
    return changed, added


def next_id(tags):
    return max(struct.unpack_from('<H', d, 0)[0] for c, d in tags if c in (2, 20, 21, 22, 32, 35, 36, 39, 83, 6, 46, 84, 10, 11, 37, 48, 75, 7, 34)) + 1
