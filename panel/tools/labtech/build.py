"""Construtor do Mundo LabTech.  Uso:  python build.py [--sem-lang] [--sem-mundi]
Le panel/world/labtech/content.py e aplica tudo (idempotente): banco, Lua do servidor, lang do cliente,
arquivos do cliente (mapas, icones) e a ilha no mapa-mundi. Backups em backup/labtech/ (na raiz do projeto)."""
import io
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..'))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'world', 'labtech')))

import art  # noqa: E402
import classe13  # noqa: E402
import content as C  # noqa: E402
import mapgen  # noqa: E402
import swf  # noqa: E402
import swf_lang  # noqa: E402

ROOT = mapgen.ROOT
MYSQL = os.path.join(ROOT, 'runtime', 'mariadb', 'bin', 'mariadb.exe')
SCRIPTS = os.path.join(ROOT, 'server', 'game', 'scripts', 'data')
LANG = os.path.join(ROOT, 'server', 'web', 'lang')
CLIENT = mapgen.CLIENT
BACKUP = os.path.join(ROOT, 'backup', 'labtech')
GAME_CONFIG = os.path.join(ROOT, 'server', 'game', 'game.config.properties')
PANEL_DATA = os.path.abspath(os.path.join(HERE, '..', '..', 'data'))
LANG_VERSION_BUMP = 480
WORLD_TILE = (2, -1)

log = print


# ================================================================= util

def backup_once(path):
    """Copia o arquivo original para BACKUP (so na primeira vez)."""
    os.makedirs(BACKUP, exist_ok=True)
    dst = os.path.join(BACKUP, os.path.basename(path) + '.orig')
    if not os.path.exists(dst) and os.path.exists(path):
        shutil.copy2(path, dst)
    return dst


def sql_run(sql):
    path = os.path.join(BACKUP, 'last_build.sql')
    os.makedirs(BACKUP, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(sql)
    with open(path, 'rb') as f:
        r = subprocess.run([MYSQL, '-u', 'root', '--default-character-set=utf8mb4'], stdin=f, capture_output=True)
    if r.returncode:
        raise SystemExit('Erro SQL:\n' + r.stderr.decode('utf-8', 'replace'))


def sql_query(sql):
    r = subprocess.run([MYSQL, '-u', 'root', '-N', '-B', '--default-character-set=utf8mb4', '-e', sql], capture_output=True)
    return [line.split('\t') for line in r.stdout.decode('utf-8', 'replace').splitlines() if line]


def q(v):
    if v is None:
        return 'NULL'
    if isinstance(v, (int, float)):
        return str(v)
    return "'" + str(v).replace('\\', '\\\\').replace("'", "\\'") + "'"


def upper_ascii(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').upper()


def lua_str(s):
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


# ================================================================= mapas

def walkable(c):
    return c['active'] and c['movement'] >= 2


def free(c):
    return walkable(c) and not c['obj2Num'] and not c['obj1Num']


def dist(a, b, w):
    ax, ay = mapgen.cell_xy(a, w)
    bx, by = mapgen.cell_xy(b, w)
    return max(abs(ax - bx), abs(ay - by))


def edge_cell(cells, w, side):
    """Celula andavel mais extrema de um lado (N/S/E/W), perto do meio do outro eixo."""
    pts = [(i, *mapgen.cell_xy(i, w)) for i, c in enumerate(cells) if walkable(c)]
    xs = [p[1] for p in pts]
    ys = [p[2] for p in pts]
    mx, my = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    key = {'N': lambda p: (p[2], abs(p[1] - mx)), 'S': lambda p: (-p[2], abs(p[1] - mx)),
           'W': lambda p: (p[1], abs(p[2] - my)), 'E': lambda p: (-p[1], abs(p[2] - my))}[side]
    return min(pts, key=key)[0]


def near_cell(cells, w, target, avoid, min_d=2, max_d=6):
    """Celula livre perto de target (para aterrissar / NPC ao lado de porta)."""
    best = None
    for i, c in enumerate(cells):
        if not walkable(c) or i in avoid:
            continue
        d = dist(i, target, w)
        if min_d <= d <= max_d and (best is None or d < best[0]):
            best = (d, i)
    return best[1] if best else target


def central_cells(cells, w, avoid, count, spacing=3, need_free=True):
    """Escolhe celulas livres espalhadas, a partir do centro."""
    pts = [i for i, c in enumerate(cells) if (free(c) if need_free else walkable(c)) and i not in avoid]
    if not pts:
        return []
    xs = [mapgen.cell_xy(i, w) for i in pts]
    cx = sum(p[0] for p in xs) / len(xs)
    cy = sum(p[1] for p in xs) / len(xs)
    pts.sort(key=lambda i: (mapgen.cell_xy(i, w)[0] - cx) ** 2 + (mapgen.cell_xy(i, w)[1] - cy) ** 2)
    out = []
    for i in pts:
        if all(dist(i, o, w) >= spacing for o in out) and all(dist(i, a, w) >= 2 for a in avoid):
            out.append(i)
        if len(out) >= count:
            break
    return out


def has_free_neighbor(cells, w, i, taken):
    return any(walkable(c) and j not in taken and dist(i, j, w) == 1 for j, c in enumerate(cells))


def build_maps():
    idx = mapgen.map_index()
    specs = {m['id']: dict(m) for m in C.MAPS}
    base_to_new = {m['base']: m['id'] for m in C.MAPS if 'coords' not in m}
    out_dir = os.path.join(SCRIPTS, 'maps', 'labtech')
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, f))

    # 1) celulas + portas
    for mid, s in specs.items():
        b = idx[s['base']]
        s['cells'] = mapgen.decode_cells(b['cells'])
        s['width'], s['height'] = b['width'], b['height']
        s['date'] = b['date']  # a data so identifica o arquivo; id novo garante arquivo novo
        s['date'] = '26092701' + str(mid)[-2:]
        if 'coords' in s:
            s['x'], s['y'] = s['coords']
        else:
            s['x'], s['y'] = b['x'] + C.OUTDOOR_OFFSET[0], b['y'] + C.OUTDOOR_OFFSET[1]
        s['positions'] = mapgen.field_from_src(b['src'], 'positions', '')
        s['vars'] = mapgen.client_map_vars(b['id'], b['date'])
        s['capabilities'] = s['vars'].get('capabilities') or 111
        s['triggers'] = {}     # cell -> (map, cell)
        s['door_cells'] = {}   # side -> cell
        s['npcs'] = {}
        # triggers originais do cluster externo, remapeados
        for cell, target, tcell in re.findall(r'\[(\d+)\]\s*=\s*moveEndTeleport\((\d+),\s*(\d+)\)', b['src']):
            if int(target) in base_to_new:
                s['triggers'][int(cell)] = (base_to_new[int(target)], int(tcell))
        # limpa objetos interativos herdados que nao vamos usar (mantem cenario)
        for c in s['cells']:
            if c['obj2Interactive'] and c['obj2Num'] not in (7000,):
                c['obj2Interactive'] = 0
    for mid, s in specs.items():
        for side in s.get('doors', {}):
            s['door_cells'][side] = edge_cell(s['cells'], s['width'], side)
    plaza = specs[30002]
    plaza['door_cells']['lab'] = plaza_door = near_cell(plaza['cells'], plaza['width'], C.PLAZA_LAB_DOOR_NEAR, set(), 0, 4)
    plaza['triggers'][plaza_door] = None  # preenchido abaixo

    def landing(dest, side):
        s = specs[dest]
        door = s['door_cells'].get(side)
        if door is None:
            return s['landing']
        return near_cell(s['cells'], s['width'], door, set(s['triggers']) | set(s['door_cells'].values()))

    for mid, s in specs.items():
        s['landing'] = central_cells(s['cells'], s['width'], set(s['triggers']) | set(s['door_cells'].values()), 1, need_free=False)[0]
    for mid, s in specs.items():
        for side, (dest, dest_side) in s.get('doors', {}).items():
            s['triggers'][s['door_cells'][side]] = (dest, landing(dest, dest_side))
    lab = specs[C.START_MAP]
    plaza['triggers'][plaza_door] = (C.START_MAP, landing(C.START_MAP, 'S'))

    # 2) zaap na praça, bancadas na oficina, NPCs
    for mid, s in specs.items():
        w = s['width']
        taken = set(s['triggers']) | {s['landing']}
        if mid == 30002:
            cand = central_cells(s['cells'], w, taken, 12, spacing=2)
            zc = next(i for i in cand if has_free_neighbor(s['cells'], w, i, taken))
            c = s['cells'][zc]
            c.update(obj2Num=7000, obj2Interactive=1, movement=1)
            s['zaapCell'] = next(j for j, cc in enumerate(s['cells']) if walkable(cc) and dist(zc, j, w) == 1 and j not in taken)
            taken |= {zc, s['zaapCell']}
        if s.get('workbenches'):
            benches = []
            for i in central_cells(s['cells'], w, taken, 40, spacing=2):
                if len(benches) >= len(C.WORKBENCHES):
                    break
                if has_free_neighbor(s['cells'], w, i, taken | set(benches)):
                    benches.append(i)
            for cell, (gfx, _) in zip(benches, C.WORKBENCHES):
                s['cells'][cell].update(obj2Num=gfx, obj2Interactive=1, movement=1)
            taken |= set(benches)
            s['benches'] = benches
        here = [n for n in C.NPCS if mid in n['maps']]
        # NPCs "de chegada" (Estagiario) ficam a 2 celulas de onde o jogador aparece, bem a vista
        for n in [n for n in here if n.get('near_landing')]:
            cell = near_cell(s['cells'], w, s['landing'], taken, 2, 3)
            s['npcs'][n['id']] = cell
            taken.add(cell)
        here = [n for n in here if not n.get('near_landing')]
        cells = central_cells(s['cells'], w, taken, len(here), spacing=s.get('npc_spacing', 3))
        for n, cell in zip(here, cells):
            s['npcs'][n['id']] = cell
        taken |= set(cells)

    # 3) Lua + SWF
    for mid, s in specs.items():
        extra = []
        if s['npcs']:
            extra.append('map.npcs = {\n' + ',\n'.join(f'    [{n}] = {{{c}, 3}}' for n, c in s['npcs'].items()) + '\n}')
        if s['triggers']:
            extra.append('map.onMovementEnd = {\n' + ',\n'.join(
                f'    [{c}] = moveEndTeleport({t[0]}, {t[1]})' for c, t in sorted(s['triggers'].items())) + '\n}')
        if s.get('zaapCell') is not None:
            extra.append(f'map.zaapCell = {s["zaapCell"]}')
        mobs = C.BANDS.get(s.get('band')) if s.get('band') else (C.ARENA_BOSSES if s.get('arena') else None)
        if mobs:
            extra.append('map.allowedMobGrades = {\n' + ',\n'.join(f'    {{{m}, {g}}}' for m in mobs for g in range(1, 6)) + '\n}')
        s['mobGroupsCount'] = 0 if s.get('safe') or not mobs else (3 if s.get('arena') else 5)
        s['mobGroupsMinSize'], s['mobGroupsMaxSize'] = (1, 2) if s.get('arena') else (2, 5)
        v = s['vars']
        spec = dict(id=mid, date=s['date'], cells=s['cells'], width=s['width'], height=s['height'], x=s['x'], y=s['y'],
                    subArea=s['sa'], positions=s['positions'], capabilities=s['capabilities'], name=s['name'],
                    mobGroupsCount=s['mobGroupsCount'], mobGroupsMinSize=s['mobGroupsMinSize'],
                    mobGroupsMaxSize=s['mobGroupsMaxSize'], extra_lua='\n'.join(extra),
                    background=v.get('backgroundNum') or 0, ambiance=v.get('ambianceId') or 0,
                    music=v.get('musicId') or 0, outdoor=bool(v.get('bOutdoor')), canAggro=not s.get('safe'))
        s['key'] = mapgen.write_map(spec, out_dir)
        log(f"  mapa {mid} {s['name']} ({s['x']},{s['y']}) npcs={len(s['npcs'])} saidas={len(s['triggers'])}")
    return specs


# ================================================================= Lua (NPCs, missao, skills)

def lua_color(c):
    return str(c if c is not None else -1)


def build_npcs(specs, dialog_ids):
    out_dir = os.path.join(SCRIPTS, 'npcs', 'labtech')
    os.makedirs(out_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        os.remove(os.path.join(out_dir, f))

    class_spells = json.load(open(os.path.join(PANEL_DATA, 'class-spells.json'), encoding='utf-8'))
    all_spells = sorted({s for ids in class_spells.values() for s in ids})
    landing = ',\n'.join(f'    [{mid}] = {s["landing"]}' for mid, s in sorted(specs.items()))
    cores = ', '.join(str(30003 + i) for i in range(12))
    lib = f'''-- Gerado por panel/tools/labtech/build.py: funcoes do Mundo LabTech (missao "Com as Proprias Maos").
LABTECH_LANDING = {{
{landing}
}}
LABTECH_CORES = {{{cores}}}
LABTECH_SPELLS = {{{', '.join(map(str, all_spells))}}}

function labtechLanding(mapId) return LABTECH_LANDING[mapId] or 0 end

local function has(p, id, qty) return p:getItem(id, qty or 1) ~= nil end

local function allCores(p)
    for _, id in ipairs(LABTECH_CORES) do
        if not has(p, id) then return false end
    end
    return true
end

function malteStart(p)
    if has(p, 30002) then return "montada" end
    if has(p, 30001) then
        if allCores(p) then return "nucleos_ok" end
        return "ja_tem"
    end
    return "boas_vindas"
end

function giveGauntlet(p)
    if not has(p, 30001) and not has(p, 30002) then p:addItem(30001, 1) end
    return "ja_tem"
end

function assembleGauntlet(p)
    if not has(p, 30001) or not allCores(p) then return "ja_tem" end
    for _, id in ipairs(LABTECH_CORES) do p:consumeItem(id, 1) end
    p:consumeItem(30001, 1)
    p:addItem(30002, 1)
    for _, s in ipairs(LABTECH_SPELLS) do
        if p:spellLevel(s) < 6 then p:setSpellLevel(s, 6) end
    end
    return "montada"
end

function forgeDofus(p)
    if not (has(p, 30017, 10) and has(p, 30015, 10) and has(p, 30016, 10)) then return "faltam_ingredientes" end
    p:consumeItem(30017, 10)
    p:consumeItem(30015, 10)
    p:consumeItem(30016, 10)
    p:addItem(30026, 1)
    return "forjado"
end

function arcade(p) return "arcade_" .. math.random(1, 6) end
'''
    with open(os.path.join(out_dir, '_labtech.lua'), 'w', encoding='utf-8') as f:
        f.write(lib)

    for n in C.NPCS:
        nid = n['id']
        d = C.DIALOGS.get(nid, {})
        nodes = {k: v for k, v in d.items() if not k.endswith('_lua')}
        lines = [f'-- Gerado por panel/tools/labtech/build.py - {n["name"]}',
                 f'local npc = Npc({nid}, {n["gfx"]})',
                 f'npc.gender = {n.get("gender", 0)}']
        if n.get('colors'):
            lines.append('npc.colors = {' + ', '.join(lua_color(c) for c in n['colors']) + '}')
        if n.get('scale'):
            lines.append(f'npc.scaleX = {n["scale"]}\nnpc.scaleY = {n["scale"]}')
        if nid in C.SALES:
            lines.append('npc.sales = {\n' + ',\n'.join(f'    {{item={i}, price={p}}}' for i, p in C.SALES[nid]) + '\n}')
        if nodes:
            node_rows, go_rows = [], []
            for key, (question, answers) in nodes.items():
                qid = dialog_ids['q'][(nid, key)]
                aids = [dialog_ids['a'][(nid, key, i)] for i in range(len(answers))]
                node_rows.append(f'    {key} = {{{qid}, {{{", ".join(map(str, aids))}}}}}')
                for aid, (_, target) in zip(aids, answers):
                    if target == 'fim':
                        go_rows.append(f'    [{aid}] = false')
                    elif target is None:
                        go_rows.append(f'    [{aid}] = "{d.get("inicio") and "inicio" or next(iter(nodes))}"')
                    elif target.startswith('lua:'):
                        code = target[4:]
                        if code.startswith('p:teleport'):
                            code = 'p:endDialog() ' + code
                        elif not code.startswith('p:'):
                            code = 'return ' + code
                        go_rows.append(f'    [{aid}] = function(p) {code} end')
                    else:
                        go_rows.append(f'    [{aid}] = "{target}"')
            start = d.get('inicio_lua', 'return "inicio"')
            lines.append('local NODES = {\n' + ',\n'.join(node_rows) + '\n}')
            lines.append('local GO = {\n' + ',\n'.join(go_rows) + '\n}')
            lines.append(f'''local function show(p, key)
    local n = NODES[key]
    if n then p:ask(n[1], n[2]) else p:endDialog() end
end
local function start(p) {start} end
function npc:onTalk(p, answer)
    if answer == 0 then show(p, start(p)) return end
    local t = GO[answer]
    if t == nil then return end
    if t == false then p:endDialog() return end
    if type(t) == "function" then
        local r = t(p)
        if type(r) == "string" then show(p, r) end
        return
    end
    show(p, t)
end''')
        lines.append('RegisterNPCDef(npc)\n')
        with open(os.path.join(out_dir, f'{nid}_{re.sub(r"[^A-Za-z0-9]+", "_", upper_ascii(n["name"]).title())}.lua'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))


def build_shops():
    """Mercadores de Bonta e Brakmar: todos os itens do jogo, separados por categoria (tipo de item).
    Gera scripts/data/zz_labtech/lojas.lua (carregado depois dos mapas pelo Data.lua)."""
    rows = sql_query('SELECT id, type FROM starloco_game.item_template ORDER BY type, id')
    by_type = {}
    for iid, typ in rows:
        by_type.setdefault(int(typ), []).append(int(iid))
    shelves, used = {}, set()
    for _, _, cats in C.LOJA_MENUS:
        if cats == 'resto':
            continue
        for key, _, types in cats:
            shelves[key] = [i for t in types for i in by_type.get(t, [])]
            used.update(types)
    rest = [i for t in sorted(by_type) if t not in used for i in by_type[t]]
    n = C.LOJA_RESTO_PARTES
    size = -(-len(rest) // n)
    for k in range(n):
        shelves[f'resto{k + 1}'] = rest[k * size:(k + 1) * size]

    out_dir = os.path.join(SCRIPTS, 'zz_labtech')
    os.makedirs(out_dir, exist_ok=True)
    lines = ['-- Gerado por panel/tools/labtech/build.py: Mercadores LabTech (todos os itens do jogo).',
             'LOJA_ITENS = {}',
             'local function lista(txt)',
             '    local t = {}',
             '    for id in string.gmatch(txt, "%d+") do t[#t + 1] = {item = tonumber(id)} end',
             '    return t',
             'end']
    for key, ids in shelves.items():   # texto (e nao tabela literal): o Lua do servidor vira bytecode Java, com limite de tamanho
        lines.append(f'LOJA_ITENS.{key} = lista("{",".join(map(str, ids))}")')
    lines.append('''LOJA_ESCOLHA = LOJA_ESCOLHA or {}

function lojaAbrir(p, npcId, key)
    LOJA_ESCOLHA[p:id()] = key
    p:openShop(npcId)
end

local function vitrine(self, p)
    return LOJA_ITENS[LOJA_ESCOLHA[p:id()] or "chapeus"] or {}
end
''')
    for npc in C.LOJA_NPCS:
        lines.append(f'if NPCS[{npc["id"]}] then NPCS[{npc["id"]}].salesList = vitrine end')
        lines.append(f'if MAPS[{npc["map"]}] then MAPS[{npc["map"]}].npcs[{npc["id"]}] = {{{npc["cell"]}, {npc["dir"]}}} end')
    with open(os.path.join(out_dir, 'lojas.lua'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    data_lua = os.path.join(os.path.dirname(SCRIPTS), 'Data.lua')
    src = open(data_lua, encoding='utf-8').read()
    hook = 'loadPack("data/zz_labtech") -- LabTech: lojas e ajustes em mapas oficiais (depois dos mapas)'
    if hook not in src:
        backup_once(data_lua)
        src = src.replace('loadPack("data/dungeons") -- Always load after maps',
                          'loadPack("data/dungeons") -- Always load after maps\n' + hook)
        open(data_lua, 'w', encoding='utf-8').write(src)
    log(f'  lojas: {sum(len(v) for v in shelves.values())} itens em {len(shelves)} prateleiras '
        f'({", ".join(f"{k}={len(v)}" for k, v in shelves.items())})')


def build_craft_skills():
    """Registra o craft de todas as bancadas (e corrige as que estavam sem contagem de ingredientes)."""
    rows = sql_query('SELECT id, crafts FROM starloco_game.jobs_data')
    pairs = []
    for jid, crafts in rows:
        jid = int(jid)
        if 43 <= jid <= 50 or 62 <= jid <= 64:   # forjamagia tem logica propria
            continue
        for part in (crafts or '').split('|'):
            if ';' in part:
                pairs.append((int(part.split(';')[0]), jid))
    body = ',\n'.join(f'    [{s}] = {j}' for s, j in sorted(set(pairs)))
    lua = f'''-- Gerado por panel/tools/labtech/build.py: craft em todas as bancadas (Oficina das Proprias Maos e o resto do mundo).
-- Registra as skills de craft que nao existiam e corrige as que estavam sem contagem de ingredientes.
local CRAFT_SKILLS = {{
{body}
}}
for skillId, jobId in pairs(CRAFT_SKILLS) do
    registerCraftSkill(skillId, {{jobID = jobId}}, ingredientsForCraftJob(jobId))
end
'''
    with open(os.path.join(SCRIPTS, 'skills', 'zz_labtech_crafts.lua'), 'w', encoding='utf-8') as f:
        f.write(lua)
    log(f'  skills de craft registradas: {len(set(pairs))}')


# ================================================================= banco

def build_db():
    items = {i['id']: i for i in C.ITEMS}
    ids = ','.join(map(str, items))
    s = ['USE starloco_game;',
         f'DELETE FROM item_template WHERE id BETWEEN 30001 AND 30100;',
         f'DELETE FROM objectsactions WHERE template BETWEEN 30001 AND 30100;',
         f'DELETE FROM crafts WHERE id BETWEEN 30001 AND 30100;',
         f'DELETE FROM pets WHERE TemplateID BETWEEN 30001 AND 30100;',
         f'DELETE FROM itemsets WHERE ID = {C.SET["id"]};',
         f'DELETE FROM drops WHERE objectId BETWEEN 30001 AND 30100;']
    for it in C.ITEMS:
        arm = ''
        if it.get('weapon'):
            e = it['weapon']  # [critBonus, AP, minRange, maxRange, critRate, failRate, lineOnly, los]
            arm = f'{e[1]};{e[2]};{e[3]};{e[4]};{e[5]};{e[0]};0'
        s.append('INSERT INTO item_template (id,type,name,level,statsTemplate,pod,panoplie,prix,conditions,armesInfos,sold,avgPrice,points,exchangesObject,newPrice) VALUES '
                 f"({it['id']},{it['type']},{q(it['name'])},{it['level']},{q(it.get('stats', ''))},{it.get('weight', 1)},"
                 f"{it.get('set', -1)},{it.get('price', 1)},'',{q(arm)},0,0,0,0,0);")
        if it.get('action'):
            s.append(f"INSERT INTO objectsactions (template,type,args) VALUES ({it['id']},{q(it['action'][0])},{q(it['action'][1])});")
        if it.get('recipe'):
            s.append(f"INSERT INTO crafts (id,craft) VALUES ({it['id']},{q(';'.join(f'{a}*{b}' for a, b in it['recipe']))});")
    st = C.SET
    s.append(f"INSERT INTO itemsets (ID,name,items,bonus) VALUES ({st['id']},{q(st['name'])},{q(', '.join(map(str, st['items'])))},{q(';'.join(st['bonus']) + ';')});")
    p = C.PET
    s.append('INSERT INTO pets (Familier,TemplateID,Type,Gap,StatsUp,Max,Gain,DeadTemplate,Epo,StatsMax,jet) VALUES '
             f"({q(p['name'])},{p['item']},2,{q(p['gap'])},{q(p['stats_up'])},{p['max']},{p['gain']},{p['dead']},-1,{q(p['stats_max'])},{q(p['jet'])});")
    # drops: nucleos 100% nos chefes
    for i, boss in enumerate(C.CORE_BOSSES):
        s.append('INSERT INTO drops (monsterName,monsterId,objectName,objectId,percentGrade1,percentGrade2,percentGrade3,percentGrade4,percentGrade5,ceil,action,level) VALUES '
                 f"('',{boss},{q(items[30003 + i]['name'])},{30003 + i},100,100,100,100,100,0,-1,-1);")
    for band in C.BANDS.values():
        for mob in band:
            for obj, pct in C.RESOURCE_DROPS:
                s.append('INSERT INTO drops (monsterName,monsterId,objectName,objectId,percentGrade1,percentGrade2,percentGrade3,percentGrade4,percentGrade5,ceil,action,level) VALUES '
                         f"('',{mob},{q(items[obj]['name'])},{obj},{pct},{pct},{pct},{pct},{pct},0,-1,-1);")
    # alquimista faz as cervejas (skill 23)
    beer_ids = [it['id'] for it in C.ITEMS if it.get('recipe')]
    crafts = sql_query('SELECT crafts FROM starloco_game.jobs_data WHERE id = 26')[0][0]
    parts = []
    for part in crafts.split('|'):
        sk, lst = part.split(';', 1)
        vals = [v for v in lst.split(',') if v and not (30001 <= int(v) <= 30100)]
        if sk == '23':
            vals += [str(b) for b in beer_ids]
        parts.append(sk + ';' + ','.join(vals))
    s.append(f"UPDATE jobs_data SET crafts = {q('|'.join(parts))} WHERE id = 26;")
    # area e subareas
    s += ['USE starloco_login;',
          f"DELETE FROM world_base_areas WHERE id = {C.AREA['id']};",
          f"INSERT INTO world_base_areas (id,superarea,name) VALUES ({C.AREA['id']},{C.AREA['superarea']},{q(C.AREA['name'])});",
          'DELETE FROM world_base_sub_areas WHERE id BETWEEN 1100 AND 1110;']
    for sid, name in C.SUBAREAS.items():
        s.append(f"INSERT INTO world_base_sub_areas (id,area,name,nearest_sub_areas) VALUES ({sid},{C.AREA['id']},{q(name)},'');")
    sa_cols = [r[0] for r in sql_query('SHOW COLUMNS FROM starloco_game.subarea_data')]
    s += ['USE starloco_game;', 'DELETE FROM subarea_data WHERE id BETWEEN 1100 AND 1110;']
    for sid in C.SUBAREAS:
        s.append(f"INSERT INTO subarea_data ({','.join(sa_cols)}) VALUES ({sid}{',0' * (len(sa_cols) - 1)});")
    sql_run('\n'.join(s) + '\n')
    log(f'  banco: {len(C.ITEMS)} itens, conjunto {C.SET["id"]}, drops, receitas, subáreas')


# ================================================================= lang do cliente

def lang_versions():
    orig = backup_once(os.path.join(LANG, 'versions_pt.txt'))
    txt = open(orig, encoding='utf-8').read().strip()
    entries = [e.split(',') for e in txt.replace('&f=', '').split('|') if e]
    return txt, {name: int(ver) for name, _, ver in entries}


def build_lang(specs, dialog_ids):
    txt, vers = lang_versions()
    items = C.ITEMS
    patches = {n: [] for n in ('items', 'itemsets', 'npc', 'dialog', 'maps', 'hints', 'crafts', 'classes')}
    # classe 13 (LabTech): copia a classe base e sobrescreve textos, custos e feiticos
    base_g = json.load(open(os.path.join(PANEL_DATA, 'lang', 'classes.json'), encoding='utf-8'))['G'][str(C.CLASS13['base_class'])]
    g13 = dict(base_g)
    g13.update(C.CLASS13['lang'])
    patches['classes'].append((('G',), 13, g13))
    lang_items = json.load(open(os.path.join(PANEL_DATA, 'lang', 'items.json'), encoding='utf-8'))['I']['u']
    for it in items:
        e = {'n': it['name'], 'nn': upper_ascii(it['name']), 't': it['type'], 'd': it['desc'], 'ep': 1, 'g': it['g'],
             'l': it['level'], 'w': it.get('weight', 1), 'p': it.get('price', 1), 'fm': True, 'wd': True}
        if it.get('weapon'):
            e['e'] = it['weapon']
            e['an'] = it.get('an', 15)
        if it.get('set'):
            e['s'] = it['set']
        if it.get('usable'):
            e['u'] = True
            e['ut'] = True
        patches['items'].append((('I', 'u'), it['id'], e))
        if it.get('recipe'):
            patches['crafts'].append((('CR',), it['id'], [[a, b] for a, b in it['recipe']]))
    patches['itemsets'].append((('IS',), C.SET['id'], {'n': C.SET['name'], 'i': C.SET['items']}))
    for n in C.NPCS:
        patches['npc'].append((('N', 'd'), n['id'], {'n': n['name'], 'a': [1, 3] if n.get('vendor') else [3]}))
    for (nid, key), qid in dialog_ids['q'].items():
        patches['dialog'].append((('D', 'q'), qid, C.DIALOGS[nid][key][0]))
    for (nid, key, i), aid in dialog_ids['a'].items():
        patches['dialog'].append((('D', 'a'), aid, C.DIALOGS[nid][key][1][i][0]))
    maps_lang = json.load(open(os.path.join(PANEL_DATA, 'lang', 'maps.json'), encoding='utf-8'))['MA']
    patches['maps'].append((('MA', 'a'), C.AREA['id'], {'n': C.AREA['name'], 'sua': C.AREA['superarea']}))
    for sid, name in C.SUBAREAS.items():
        patches['maps'].append((('MA', 'sa'), sid, {'n': name, 'a': C.AREA['id'], 'm': [], 'v': [s for s in C.SUBAREAS if s != sid]}))
    for mid, s in specs.items():
        base = dict(maps_lang['m'].get(str(s['base']), {}))
        base.update({'x': s['x'], 'y': s['y'], 'sa': s['sa']})
        base.pop('d', None)
        pos = (s['positions'] or '|').split('|')
        base['p1'], base['p2'] = pos[0], pos[1] if len(pos) > 1 else ''
        patches['maps'].append((('MA', 'm'), mid, base))
    hints_env = swf_lang.parse_swf(os.path.join(LANG, 'swf', f'hints_pt_{vers["hints"]}.swf'))
    nhints = len(hints_env['HI'])
    hint_list = [(30002, 410, 4, 'Zaap LabTech'), (30003, 408, 4, 'Cervejaria Barril Gambiarra'),
                 (30001, 418, 4, 'Laboratório LabTech'), (30004, 309, 3, 'Oficina das Próprias Mãos'),
                 (30005, 417, 4, 'Museu dos Experimentos'), (30007, 411, 4, 'Arena LabTech'),
                 (30014, 429, 4, 'Forja do Dofus'), (30015, 408, 4, 'Bar das Celebridades')]
    for k, (m, g, c, name) in enumerate(hint_list):
        patches['hints'].append((('HI',), nhints + k, {'m': m, 'g': g, 'c': c, 'n': name}))

    new_vers = dict(vers)
    for name, entries in patches.items():
        v = vers[name]
        nv = v + LANG_VERSION_BUMP
        src = os.path.join(LANG, 'swf', f'{name}_pt_{v}.swf')
        dst = os.path.join(LANG, 'swf', f'{name}_pt_{nv}.swf')
        # o proprio arquivo declara VERSION; a entrada nova sobrescreve para bater com o nome do arquivo
        swf.patch_lang(src, dst, entries + [(('VERSION',), None, nv)])
        new_vers[name] = nv
        check = swf_lang.parse_swf(dst)
        assert check.get('FILE_END') is True, f'{name}: FILE_END ausente'
        log(f'  lang {name}: {len(entries)} entradas -> {os.path.basename(dst)}')
    out = '&f=' + '|'.join(f'{n},pt,{new_vers[n]}' for n in [e.split(',')[0] for e in txt.replace('&f=', '').split('|') if e]) + '|'
    with open(os.path.join(LANG, 'versions_pt.txt'), 'w', encoding='utf-8') as f:
        f.write(out)


def dialog_id_table():
    ids = {'q': {}, 'a': {}}
    qn, an = 30000, 30000
    for nid in sorted(C.DIALOGS):
        for key, val in C.DIALOGS[nid].items():
            if key.endswith('_lua'):
                continue
            ids['q'][(nid, key)] = qn
            qn += 1
            for i in range(len(val[1])):
                ids['a'][(nid, key, i)] = an
                an += 1
    assert qn < 31000 and an < 31000
    return ids


# ================================================================= cliente (icones, mundi)

def build_icons():
    icons = art.icon_images()
    n = 0
    for it in C.ITEMS:
        name = it.get('icon')
        if not name:
            path = os.path.join(CLIENT, 'clips', 'items', str(it['type']), f'{it["g"]}.swf')
            if not os.path.exists(path):
                log(f'  AVISO: icone inexistente {path}')
            continue
        img = icons[name]
        tmp = os.path.join(art.OUT, name + '.png')
        os.makedirs(art.OUT, exist_ok=True)
        img.save(tmp)
        folder = os.path.join(CLIENT, 'clips', 'items', str(it['type']))
        os.makedirs(folder, exist_ok=True)
        swf.icon_swf(os.path.join(folder, f'{it["g"]}.swf'), tmp)
        n += 1
    log(f'  icones: {n}')


def build_world_tile(specs):
    path = os.path.join(CLIENT, 'clips', 'maps', '0.swf')
    orig = backup_once(path)
    S = swf.read_swf(orig)
    byid, exports, jpegtables = {}, {}, None
    for i, (c, d) in enumerate(S.tags):
        if c in (2, 22, 32, 39, 20, 21, 35, 36, 6):
            byid[struct.unpack_from('<H', d, 0)[0]] = i
        if c == 8:
            jpegtables = d
        if c == 56:
            n = struct.unpack_from('<H', d, 0)[0]
            p = 2
            for _ in range(n):
                cid = struct.unpack_from('<H', d, p)[0]
                p += 2
                e = d.index(b'\0', p)
                exports[d[p:e].decode()] = cid
                p = e + 1
    from PIL import Image

    def tile_bitmap(name):
        """(indice da tag do bitmap, id do bitmap, imagem) de um tile exportado do mapa-mundi."""
        sprite = S.tags[byid[exports[name]]][1]
        shape_id = struct.unpack_from('<H', sprite, 4 + 2 + 3)[0]
        sd = S.tags[byid[shape_id]][1]
        _, rl = swf.read_rect(sd[2:])
        bmp = struct.unpack_from('<H', sd, 2 + rl + 2)[0]
        bc, bd = S.tags[byid[bmp]]
        if bc == 35:
            jpg = bd[6:6 + struct.unpack_from('<I', bd, 2)[0]]
        elif bc == 6 and not bd[2:4] == b'\xff\xd8':
            jpg = jpegtables[:-2] + bd[4:]
        else:
            jpg = bd[2:]
        return byid[bmp], bmp, Image.open(io.BytesIO(jpg.replace(b'\xff\xd9\xff\xd8', b''))).convert('RGB')

    tx, ty = WORLD_TILE
    bi, bitmap_id, tile = tile_bitmap(f'{tx}_{ty}')
    _, _, otomai = tile_bitmap('-4_1')   # vila de Otomai, de onde os mapas externos foram clonados
    pts = []
    for s in specs.values():
        if s['vars'].get('bOutdoor') or 'coords' in s:
            pts.append(((s['x'] - 15 * tx) * 40 + 20, (s['y'] - 15 * ty) * 23 + 11))
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    img = art.island_from_world(tile, otomai, (cx, cy), label='LabTech')
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=92)
    S.tags[bi] = (21, struct.pack('<H', bitmap_id) + buf.getvalue())
    swf.write_swf(S, path)
    img.save(os.path.join(art.OUT, 'mundi_tile.png'))
    log(f'  mapa-mundi: ilha desenhada no tile {tx}_{ty}')


def build_config():
    backup_once(GAME_CONFIG)
    txt = open(GAME_CONFIG, encoding='utf-8').read()
    return txt


def main():
    args = set(sys.argv[1:])
    log('Construindo o Mundo LabTech...')
    dialog_ids = dialog_id_table()
    build_db()
    specs = build_maps()
    build_npcs(specs, dialog_ids)
    build_craft_skills()
    build_shops()
    build_icons()
    if '--sem-lang' not in args:
        build_lang(specs, dialog_ids)
    if '--sem-mundi' not in args:
        build_world_tile(specs)
    if '--sem-classe' not in args:
        classe13.build(C.CLASS13, log)
    # mapa inicial de todo personagem novo
    backup_once(GAME_CONFIG)
    cfg = open(GAME_CONFIG, encoding='utf-8').read()
    cfg = re.sub(r'system\.server\.game\.start\.map .*', f'system.server.game.start.map {C.START_MAP}', cfg)
    cfg = re.sub(r'system\.server\.game\.start\.cell .*', f'system.server.game.start.cell {specs[C.START_MAP]["landing"]}', cfg)
    open(GAME_CONFIG, 'w', encoding='utf-8').write(cfg)
    summary = {mid: {'nome': s['name'], 'x': s['x'], 'y': s['y'], 'chegada': s['landing'], 'npcs': s['npcs'],
                     'saidas': {str(k): v for k, v in s['triggers'].items()}, 'zaap': s.get('zaapCell'),
                     'bancadas': s.get('benches')} for mid, s in specs.items()}
    json.dump(summary, open(os.path.join(HERE, '..', '..', 'world', 'labtech', 'mundo_gerado.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    log('Pronto. Reinicie o servidor de jogo e reabra os clientes.')


if __name__ == '__main__':
    main()
