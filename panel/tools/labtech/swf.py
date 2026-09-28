"""Leitura e escrita minima de SWF (Flash) para o mundo LabTech.

- read_swf / write_swf: tags brutas
- ActionBuilder: gera bytecode AS1/AS2 (push, get/set variavel e membro, objetos, arrays)
- map_swf: arquivo de mapa do cliente (variaveis id, width, mapData...)
- patch_lang: insere entradas novas num arquivo lang antes do DoAction que define FILE_END
- icon_swf: icone de item a partir de uma imagem PNG
"""
import io
import struct
import zlib

# ---------------------------------------------------------------- SWF bruto

class Swf:
    def __init__(self, signature, version, header_rect, frame_rate, frame_count, tags):
        self.signature = signature      # b'FWS' ou b'CWS'
        self.version = version
        self.header_rect = header_rect  # bytes do RECT do palco
        self.frame_rate = frame_rate    # u16 (8.8)
        self.frame_count = frame_count
        self.tags = tags                # lista de (codigo, bytes)


def read_swf(path_or_bytes):
    raw = open(path_or_bytes, 'rb').read() if isinstance(path_or_bytes, str) else path_or_bytes
    sig, version = raw[:3], raw[3]
    body = zlib.decompress(raw[8:]) if sig == b'CWS' else raw[8:]
    nbits = body[0] >> 3
    rect_len = (5 + 4 * nbits + 7) // 8
    rect = body[:rect_len]
    frame_rate, frame_count = struct.unpack_from('<HH', body, rect_len)
    pos = rect_len + 4
    tags = []
    while pos < len(body):
        code_len = struct.unpack_from('<H', body, pos)[0]
        pos += 2
        code, length = code_len >> 6, code_len & 0x3F
        if length == 0x3F:
            length = struct.unpack_from('<I', body, pos)[0]
            pos += 4
        tags.append((code, body[pos:pos + length]))
        pos += length
        if code == 0:
            break
    return Swf(sig, version, rect, frame_rate, frame_count, tags)


def encode_tag(code, data, force_long=False):
    if len(data) < 0x3F and not force_long:
        return struct.pack('<H', (code << 6) | len(data)) + data
    return struct.pack('<HI', (code << 6) | 0x3F, len(data)) + data


# Tags que o Flash exige em formato "longo" mesmo quando pequenas
LONG_TAGS = {6, 20, 21, 35, 36, 90}


def write_swf(swf, path=None, compress=None):
    body = swf.header_rect + struct.pack('<HH', swf.frame_rate, swf.frame_count)
    body += b''.join(encode_tag(c, d, c in LONG_TAGS) for c, d in swf.tags)
    compress = (swf.signature == b'CWS') if compress is None else compress
    total = 8 + len(body)
    data = (b'CWS' if compress else b'FWS') + bytes([swf.version]) + struct.pack('<I', total)
    data += zlib.compress(body, 9) if compress else body
    if path:
        with open(path, 'wb') as f:
            f.write(data)
    return data


# ---------------------------------------------------------------- bits / RECT

class BitWriter:
    def __init__(self):
        self.bits = []

    def ub(self, value, n):
        for i in range(n - 1, -1, -1):
            self.bits.append((value >> i) & 1)

    def sb(self, value, n):
        self.ub(value & ((1 << n) - 1), n)

    def bytes(self):
        while len(self.bits) % 8:
            self.bits.append(0)
        return bytes(int(''.join(map(str, self.bits[i:i + 8])), 2) for i in range(0, len(self.bits), 8))


def nbits_signed(*values):
    n = 1
    for v in values:
        while not (-(1 << (n - 1)) <= v < (1 << (n - 1))):
            n += 1
    return n


def rect(xmin, xmax, ymin, ymax):
    """RECT em twips."""
    n = nbits_signed(xmin, xmax, ymin, ymax)
    w = BitWriter()
    w.ub(n, 5)
    for v in (xmin, xmax, ymin, ymax):
        w.sb(v, n)
    return w.bytes()


def read_rect(data):
    bits = ''.join(f'{b:08b}' for b in data[:20])
    n = int(bits[:5], 2)
    vals = []
    for i in range(4):
        v = int(bits[5 + i * n:5 + (i + 1) * n], 2)
        vals.append(v - (1 << n) if v >> (n - 1) else v)
    return vals, (5 + 4 * n + 7) // 8


# ---------------------------------------------------------------- ActionScript

class ActionBuilder:
    """Gera bytecode AS1/AS2 sem ConstantPool (strings inline, tipo 0)."""

    def __init__(self):
        self.out = io.BytesIO()

    def _action(self, code, payload=b''):
        self.out.write(bytes([code]))
        if code >= 0x80:
            self.out.write(struct.pack('<H', len(payload)) + payload)

    def push(self, *values):
        payload = b''
        for v in values:
            if v is None:
                payload += b'\x02'
            elif isinstance(v, bool):
                payload += b'\x05' + bytes([1 if v else 0])
            elif isinstance(v, int) and -2**31 <= v < 2**31:
                payload += b'\x07' + struct.pack('<i', v)
            elif isinstance(v, (int, float)):
                d = struct.pack('<d', float(v))
                payload += b'\x06' + d[4:] + d[:4]  # double do AS1 tem as metades trocadas
            else:
                payload += b'\x00' + str(v).encode('utf-8') + b'\x00'
        # Push tem limite de 65535 bytes: divide se preciso
        self._action(0x96, payload)
        return self

    def get_variable(self): self._action(0x1C); return self
    def set_variable(self): self._action(0x1D); return self
    def get_member(self): self._action(0x4E); return self
    def set_member(self): self._action(0x4F); return self
    def call_method(self): self._action(0x52); return self
    def pop(self): self._action(0x17); return self
    def init_object(self): self._action(0x43); return self
    def init_array(self): self._action(0x42); return self

    def value(self, v):
        """Empilha um valor Python (dict -> objeto, list -> array)."""
        if isinstance(v, dict):
            for k, item in v.items():
                self.push(str(k))
                self.value(item)
            self.push(len(v)).init_object()
        elif isinstance(v, (list, tuple)):
            for item in reversed(v):
                self.value(item)
            self.push(len(v)).init_array()
        else:
            self.push(v)
        return self

    def set_var(self, name, v):
        self.push(name)
        self.value(v)
        return self.set_variable()

    def path(self, *names):
        """Empilha o objeto no caminho (ex.: 'I', 'u')."""
        self.push(names[0]).get_variable()
        for n in names[1:]:
            self.push(n).get_member()
        return self

    def set_path(self, path, key, v):
        """path[key] = v   (ex.: I.u[30001] = {...})"""
        self.path(*path)
        self.push(key)
        self.value(v)
        return self.set_member()

    def allow_domain(self):
        # System.security.allowDomain(_parent._url)
        self.push('_parent').get_variable().push('_url').get_member()
        self.push(1).push('System').get_variable().push('security').get_member()
        self.push('allowDomain').call_method().pop()
        return self

    def bytes(self):
        return self.out.getvalue() + b'\x00'


# ---------------------------------------------------------------- mapas

def map_swf(path, map_id, width, height, map_data_hex, background=0, ambiance=0, music=0,
            outdoor=True, capabilities=111, can_aggro=True):
    a = ActionBuilder().allow_domain()
    for name, v in [('id', map_id), ('width', width), ('height', height), ('backgroundNum', background),
                    ('ambianceId', ambiance), ('musicId', music), ('bOutdoor', outdoor),
                    ('capabilities', capabilities), ('mapData', map_data_hex), ('canAggro', can_aggro),
                    ('canUseInventory', True), ('canUseObject', True), ('canChangeCharac', True)]:
        a.set_var(name, v)
    swf = Swf(b'CWS', 6, rect(0, 20, 0, 20), 20 << 8, 1,
              [(9, b'\x00\x00\x00'), (12, a.bytes()), (1, b''), (0, b'')])
    return write_swf(swf, path)


# ---------------------------------------------------------------- lang



def patch_lang(src_path, dst_path, entries):
    """Copia um arquivo lang acrescentando entradas antes do DoAction que define FILE_END.
    entries: lista de (path_tuple, key, value), ex.: (('I','u'), 30001, {...});
    key None = variavel global (path_tuple[0] = value)."""
    swf = read_swf(src_path)
    blocks, builder = [], ActionBuilder()
    for path, key, value in entries:
        if key is None:
            builder.set_var(path[0], value)
        else:
            builder.set_path(path, key, value)
        if builder.out.tell() > 55000:  # DoAction tem limite pratico de 64 KB por registro
            blocks.append(builder.bytes())
            builder = ActionBuilder()
    # FILE_END volta a ser marcado no fim do nosso bloco
    builder.set_var('FILE_END', True)
    blocks.append(builder.bytes())
    # Insere DEPOIS do ultimo DoAction original: em arquivos pequenos todo o conteudo (inclusive
    # "G = new Object()") esta num unico DoAction, e inserir antes faria nossas entradas serem apagadas.
    idx = max(i for i, (c, d) in enumerate(swf.tags) if c == 12) + 1
    swf.tags = swf.tags[:idx] + [(12, b) for b in blocks] + swf.tags[idx:]
    return write_swf(swf, dst_path)


# ---------------------------------------------------------------- icones

def icon_swf(path, png_path, size=None):
    """Icone de item: bitmap (DefineBitsLossless2) + shape com preenchimento de bitmap + PlaceObject2."""
    from PIL import Image
    img = Image.open(png_path).convert('RGBA')
    if size:
        img = img.resize(size, Image.NEAREST)
    w, h = img.size
    argb = bytearray()
    for r, g, b, al in img.getdata():
        # ARGB pre-multiplicado
        argb += bytes([al, r * al // 255, g * al // 255, b * al // 255])
    bitmap_id, shape_id = 1, 2
    lossless = struct.pack('<HBHH', bitmap_id, 5, w, h) + zlib.compress(bytes(argb), 9)

    tw, th = w * 20, h * 20
    x0, y0 = -tw // 2, -th // 2
    bw = BitWriter()
    # FILLSTYLEARRAY: 1 estilo, bitmap recortado (0x41), matriz escala 20 (twips/pixel) + translação
    fill = bytes([1, 0x41]) + struct.pack('<H', bitmap_id)
    m = BitWriter()
    m.ub(1, 1)                       # HasScale
    nb = nbits_signed(20 << 16) + 1
    m.ub(nb, 5); m.sb(20 << 16, nb); m.sb(20 << 16, nb)
    m.ub(0, 1)                       # HasRotate
    nt = nbits_signed(x0, y0)
    m.ub(nt, 5); m.sb(x0, nt); m.sb(y0, nt)
    fill += m.bytes()
    lines = bytes([0])               # sem linhas
    # registros: move para (x0,y0) com fillStyle1 = 1; 4 arestas retas; fim
    sr = BitWriter()
    sr.ub(1, 4); sr.ub(0, 4)         # NumFillBits=1, NumLineBits=0
    # StyleChangeRecord: TypeFlag 0, StateNewStyles 0, LineStyle 0, FillStyle1 1, FillStyle0 0, MoveTo 1
    sr.ub(0, 1); sr.ub(0, 1); sr.ub(0, 1); sr.ub(1, 1); sr.ub(0, 1); sr.ub(1, 1)
    nm = nbits_signed(x0, y0)
    sr.ub(nm, 5); sr.sb(x0, nm); sr.sb(y0, nm)
    sr.ub(1, 1)                      # FillStyle1 index (1 bit)

    def edge(dx, dy):
        sr.ub(1, 1); sr.ub(1, 1)     # TypeFlag=1 (aresta), StraightFlag=1
        n = max(nbits_signed(dx, dy), 2)
        sr.ub(n - 2, 4)
        if dx and dy:
            sr.ub(1, 1); sr.sb(dx, n); sr.sb(dy, n)
        else:
            sr.ub(0, 1); sr.ub(1 if dy else 0, 1); sr.sb(dy if dy else dx, n)
    edge(tw, 0); edge(0, th); edge(-tw, 0); edge(0, -th)
    sr.ub(0, 6)                      # EndShapeRecord
    shape = struct.pack('<H', shape_id) + rect(x0, x0 + tw, y0, y0 + th) + fill + lines + sr.bytes()

    place = bytes([0x06]) + struct.pack('<HH', 1, shape_id) + b'\x00'   # HasCharacter+HasMatrix, depth 1, matriz vazia
    swf = Swf(b'FWS', 7, rect(0, 550 * 20, 0, 400 * 20), 12 << 8, 1,
              [(9, b'\xff\xff\xff'), (36, lossless), (2, shape), (26, place), (1, b''), (0, b'')])
    return write_swf(swf, path)
