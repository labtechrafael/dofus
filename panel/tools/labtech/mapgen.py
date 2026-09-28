"""Mapas do Dofus 1: leitura dos mapas Lua do StarLoco, codificacao de celulas, cifra do mapData
e geracao de mapas novos (arquivo Lua do servidor + SWF do cliente).

Portado de CellsDataProvider.java (b64ToLong / encodeCellData) e CryptManager.java (prepareKey / decypherData).
"""
import glob
import os
import random
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import swf_lang  # noqa: E402  (parser de SWF do painel)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
LUA_MAPS = os.path.join(ROOT, 'server', 'game', 'scripts', 'data', 'maps')
CLIENT = os.path.join(ROOT, 'server', 'client-starloco', 'resources', 'app', 'retroclient')
CLIENT_MAPS = os.path.join(CLIENT, 'data', 'maps')

HASH = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
IDX = {c: i for i, c in enumerate(HASH)}

FIELDS = ('active', 'los', 'movement', 'groundLevel', 'groundSlope', 'groundNum', 'groundFlip', 'groundRot',
          'obj1Num', 'obj1Flip', 'obj1Rot', 'obj2Num', 'obj2Flip', 'obj2Interactive')


# ---------------------------------------------------------------- celulas

def decode_cell(s):
    d = [IDX[c] for c in s]
    return {
        'active': (d[0] & 0x20) >> 5,
        'los': d[0] & 1,
        'movement': (d[2] & 0x38) >> 3,
        'groundLevel': d[1] & 0xF,
        'groundSlope': (d[4] & 0x3C) >> 2,
        'groundNum': ((d[0] & 0x18) << 6) | ((d[2] & 7) << 6) | d[3],
        'groundFlip': (d[4] & 2) >> 1,
        'groundRot': (d[1] & 0x30) >> 4,
        'obj1Num': ((d[0] & 4) << 11) | ((d[4] & 1) << 12) | (d[5] << 6) | d[6],
        'obj1Flip': (d[7] & 8) >> 3,
        'obj1Rot': (d[7] & 0x30) >> 4,
        'obj2Num': ((d[0] & 2) << 12) | ((d[7] & 1) << 12) | (d[8] << 6) | d[9],
        'obj2Flip': (d[7] & 4) >> 2,
        'obj2Interactive': (d[7] & 2) >> 1,
    }


def encode_cell(c):
    g, o1, o2 = c['groundNum'], c['obj1Num'], c['obj2Num']
    vals = [
        (c['active'] << 5) | ((g & 0x600) >> 6) | ((o1 & 0x2000) >> 11) | ((o2 & 0x2000) >> 12) | c['los'],
        (c['groundRot'] << 4) | c['groundLevel'],
        (c['movement'] << 3) | ((g >> 6) & 7),
        g & 0x3F,
        (c['groundSlope'] << 2) | (c['groundFlip'] << 1) | ((o1 >> 12) & 1),
        (o1 >> 6) & 0x3F,
        o1 & 0x3F,
        (c['obj1Rot'] << 4) | (c['obj1Flip'] << 3) | (c['obj2Flip'] << 2) | (c['obj2Interactive'] << 1) | ((o2 >> 12) & 1),
        (o2 >> 6) & 0x3F,
        o2 & 0x3F,
    ]
    return ''.join(HASH[v] for v in vals)


def decode_cells(data):
    return [decode_cell(data[i:i + 10]) for i in range(0, len(data), 10)]


def encode_cells(cells):
    return ''.join(encode_cell(c) for c in cells)


def cell_xy(cell_id, width):
    """Posicao do losango na grade (para preview e distancias)."""
    row, col = divmod(cell_id, width * 2 - 1)
    if col < width:
        return col * 2, row * 2
    return (col - width) * 2 + 1, row * 2 + 1


def encode_cell_list(cells):
    return ''.join(HASH[c >> 6] + HASH[c & 63] for c in cells)


def decode_cell_list(s):
    return [IDX[s[i]] * 64 + IDX[s[i + 1]] for i in range(0, len(s), 2)]


# ---------------------------------------------------------------- cifra

def prepare_key(hexkey):
    raw = bytes.fromhex(hexkey).decode('latin-1')
    return urllib.parse.unquote(raw, encoding='latin-1')


def encrypt_map_data(plain, hexkey):
    k = prepare_key(hexkey)
    cs = (sum(ord(c) % 16 for c in k) % 16) * 2
    esc = urllib.parse.quote(plain, safe='')
    return ''.join('%02x' % (ord(ch) ^ ord(k[(i + cs) % len(k)])) for i, ch in enumerate(esc))


def decrypt_map_data(hexdata, hexkey):
    k = prepare_key(hexkey)
    cs = (sum(ord(c) % 16 for c in k) % 16) * 2
    out = ''.join(chr(int(hexdata[i:i + 2], 16) ^ ord(k[(i // 2 + cs) % len(k)])) for i in range(0, len(hexdata), 2))
    return urllib.parse.unquote(out)


def new_key(seed, length=160):
    """Chave aleatoria (sem '%', para nao depender de URL-decode) em hex."""
    rnd = random.Random(seed)
    chars = [c for c in map(chr, range(0x21, 0x7F)) if c not in '%+\'"\\']
    return ''.join('%02x' % ord(rnd.choice(chars)) for _ in range(length))


# ---------------------------------------------------------------- mapas existentes

MAPDEF_RE = re.compile(r'MapDef\(\s*(\d+)\s*,\s*"(\d+)"\s*,\s*"([0-9a-fA-F]*)"\s*,\s*"([A-Za-z0-9_-]+)"\s*,'
                       r'\s*(\d+)\s*,\s*(\d+)\s*,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*\)', re.S)

_index = None


def map_index():
    """{id: {id,date,key,cells,width,height,x,y,subArea,file}} de todos os mapas Lua."""
    global _index
    if _index is None:
        _index = {}
        for f in glob.glob(os.path.join(LUA_MAPS, '**', '*.lua'), recursive=True):
            src = open(f, encoding='utf-8', errors='replace').read()
            for m in MAPDEF_RE.finditer(src):
                mid = int(m.group(1))
                _index[mid] = {'id': mid, 'date': m.group(2), 'key': m.group(3), 'cells': m.group(4),
                               'width': int(m.group(5)), 'height': int(m.group(6)), 'x': int(m.group(7)),
                               'y': int(m.group(8)), 'subArea': int(m.group(9)), 'file': f, 'src': src}
    return _index


def client_map_vars(map_id, date):
    path = os.path.join(CLIENT_MAPS, f'{map_id}_{date}X.swf')
    if not os.path.exists(path):
        return {}
    env = swf_lang.parse_swf(path)
    return {k: env.get(k) for k in ('backgroundNum', 'ambianceId', 'musicId', 'bOutdoor', 'capabilities')}


def field_from_src(src, name, default=None):
    m = re.search(r'map\.' + name + r'\s*=\s*("?[^\n"]*"?)', src)
    if not m:
        return default
    return m.group(1).strip('"')


# ---------------------------------------------------------------- geracao

LUA_TEMPLATE = '''-- Gerado por panel/tools/labtech/build.py - Mundo LabTech. Nao editar a mao: edite labtech.json.
local map = MapDef(
\t{id},
\t"{date}",
\t"{key}",
\t"{cells}",
\t{width},
\t{height},
\t{x},
\t{y},
\t{subArea}
)
map.positions = "{positions}"
map.capabilities = {capabilities}
map.mobGroupsCount = {mobGroupsCount}
map.mobGroupsMinSize = {mobGroupsMinSize}
map.mobGroupsMaxSize = {mobGroupsMaxSize}
{extra}
'''


def write_map(spec, lua_dir):
    """spec: dict com id, date, cells (lista de celulas), width, height, x, y, subArea, positions,
    capabilities, bg/ambiance/music/outdoor, extra_lua (texto), name (para o nome do arquivo)."""
    hexkey = spec.get('key') or new_key(spec['id'])
    plain = encode_cells(spec['cells'])
    with open(os.path.join(lua_dir, f"{spec['id']}_{spec['name']}.lua"), 'w', encoding='utf-8') as f:
        f.write(LUA_TEMPLATE.format(
            id=spec['id'], date=spec['date'], key=hexkey, cells=plain, width=spec['width'], height=spec['height'],
            x=spec['x'], y=spec['y'], subArea=spec['subArea'], positions=spec.get('positions', ''),
            capabilities=spec.get('capabilities', 111), mobGroupsCount=spec.get('mobGroupsCount', 0),
            mobGroupsMinSize=spec.get('mobGroupsMinSize', 1), mobGroupsMaxSize=spec.get('mobGroupsMaxSize', 8),
            extra=spec.get('extra_lua', '')))
    from swf import map_swf  # noqa: E402
    map_swf(os.path.join(CLIENT_MAPS, f"{spec['id']}_{spec['date']}X.swf"), spec['id'], spec['width'], spec['height'],
            encrypt_map_data(plain, hexkey), background=spec.get('background', 0), ambiance=spec.get('ambiance', 0),
            music=spec.get('music', 0), outdoor=spec.get('outdoor', True), capabilities=spec.get('capabilities', 111),
            can_aggro=spec.get('canAggro', True))
    return hexkey


def preview_png(cells, width, path, marks=None, title=''):
    """Preview esquematico: losangos por celula (verde andavel, cinza bloqueada, amarelo interativo)."""
    from PIL import Image, ImageDraw
    marks = marks or {}
    cw, ch = 34, 17
    rows = (len(cells) // (2 * width - 1)) * 2 + 2
    img = Image.new('RGB', (width * cw + cw, rows * ch // 2 + ch * 2 + 20), (24, 26, 30))
    d = ImageDraw.Draw(img)
    for i, c in enumerate(cells):
        gx, gy = cell_xy(i, width)
        cx, cy = gx * cw // 2 + cw // 2, gy * ch // 2 + ch + 20
        color = (60, 60, 64)
        if c['active'] and c['movement'] >= 2:
            color = (70, 140, 80)
        if c['obj2Interactive']:
            color = (220, 180, 40)
        if i in marks:
            color = marks[i]
        d.polygon([(cx, cy - ch // 2), (cx + cw // 2, cy), (cx, cy + ch // 2), (cx - cw // 2, cy)], fill=color, outline=(20, 20, 20))
    d.text((6, 4), title, fill=(230, 230, 230))
    img.save(path)


if __name__ == '__main__':
    # Autoteste: ida e volta de todas as celulas + cifra do mapa 10294 igual ao SWF original.
    idx = map_index()
    print('mapas Lua:', len(idx))
    m = idx[10294]
    assert encode_cells(decode_cells(m['cells'])) == m['cells'], 'codec de celulas divergiu'
    bad = [mid for mid, mm in idx.items() if encode_cells(decode_cells(mm['cells'])) != mm['cells']]
    print('mapas com ida e volta diferente:', len(bad), bad[:5])
    env = swf_lang.parse_swf(os.path.join(CLIENT_MAPS, f"10294_{m['date']}X.swf"))
    assert encrypt_map_data(m['cells'], m['key']) == env['mapData'].lower(), 'cifra divergiu'
    assert decrypt_map_data(env['mapData'], m['key']) == m['cells']
    print('cifra OK; vars cliente:', client_map_vars(10294, m['date']))
