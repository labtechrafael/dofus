"""Chat vivo do Mundo LabTech: gera server/game/scripts/labtech/chat_vivo.tsv, lido pelo ChatVivo.java.

Tudo o que dá para tirar dos dados do jogo sai daqui, pronto para o servidor escolher conforme o personagem:
  - builds por nível e atributo (força, inteligência, agilidade, sorte), peça por peça, com itens à venda no Mercador;
  - conjuntos por nível;
  - fichas dos chefes: nível, PV, PA, PM, resistências, feitiços, onde aparecem e como vencer (lido dos feitiços);
  - zonas: os monstros de cada subárea e a faixa de nível, para "o que tem aqui" e "onde upar".
Os textos escritos à mão (dicas, curiosidades, segredos) ficam em content.py (CHAT_VIVO).
Linhas do TSV: tipo e colunas separadas por tabulação; o servidor relê o arquivo quando ele muda."""
import glob
import json
import os
import re

import content as C
import swf_lang

ELEMENTOS = {   # atributo -> (id do efeito, nome, dano de arma que combina)
    'forca': (118, 'Força', (97, 100)), 'inteligencia': (126, 'Inteligência', (99,)),
    'agilidade': (119, 'Agilidade', (98,)), 'sorte': (123, 'Sorte', (96,)),
}
NEGATIVO = {157: 118, 155: 126, 154: 119, 152: 123, 153: 125, 156: 124, 168: 111, 169: 128, 116: 117}
PESOS = {125: 0.35, 124: 0.25, 111: 55, 128: 40, 117: 12, 112: 3, 138: 1.0, 182: 4, 115: 4, 174: 0.02, 176: 0.1,
         210: 0.6, 211: 0.6, 212: 0.6, 213: 0.6, 214: 0.6}
SLOTS = [(6, 'chapéu', (16,)), (7, 'capa', (17, 81)), (0, 'amuleto', (1,)), (2, 'anel', (9,)), (4, 'anel', (9,)),
         (3, 'cinto', (10,)), (5, 'botas', (11,)), (1, 'arma', (2, 3, 4, 5, 6, 7, 8, 19))]
NIVEIS = [1] + list(range(10, 201, 10))
EL_RES = ['neutro', 'terra', 'fogo', 'água', 'ar']
DANO_EL = {96: 'água', 97: 'terra', 98: 'ar', 99: 'fogo', 100: 'neutro', 91: 'água', 92: 'terra', 93: 'ar', 94: 'fogo', 95: 'neutro'}


def stats_de(txt, media=True):
    """statsTemplate (hex) -> {efeito: valor}; faixa vira a média (ou o máximo)."""
    out = {}
    for part in (txt or '').split(','):
        f = part.split('#')
        if len(f) < 3 or not f[0]:
            continue
        try:
            eid, a, b = int(f[0], 16), int(f[1] or '0', 16), int(f[2] or '0', 16)
        except ValueError:
            continue
        v = (a + b) / 2 if (media and b > a) else max(a, b)
        if eid in NEGATIVO:
            eid, v = NEGATIVO[eid], -v
        out[eid] = out.get(eid, 0) + v
    return out


def dano_arma(txt, efeitos):
    tot = 0
    for part in (txt or '').split(','):
        f = part.split('#')
        if len(f) >= 3 and f[0]:
            try:
                eid, a, b = int(f[0], 16), int(f[1] or '0', 16), int(f[2] or '0', 16)
            except ValueError:
                continue
            if eid in efeitos:
                tot += (a + max(a, b)) / 2
    return tot


def nota(st, elem):
    eid = ELEMENTOS[elem][0]
    s = st.get(eid, 0) * 1.0
    s += sum(st.get(o[0], 0) * 0.15 for k, o in ELEMENTOS.items() if k != elem)
    s += sum(st.get(k, 0) * w for k, w in PESOS.items())
    return s


def gerar(log, sql_query, panel_data, scripts, lang_dir, spells_version):
    lang = lambda n: json.load(open(os.path.join(panel_data, 'lang', n + '.json'), encoding='utf-8'))
    I = lang('items')['I']['u']
    SETS = lang('itemsets')['IS']
    M = lang('monsters')['M']
    MA = lang('maps')['MA']
    S = swf_lang.parse_swf(os.path.join(lang_dir, 'swf', f'spells_pt_{spells_version}.swf'))['S']
    nome_item = lambda i: (I.get(str(i)) or {}).get('n')
    rows = []

    # ------------------------------------------------------------ itens e builds
    tipos = sorted({t for _, _, ts in SLOTS for t in ts})
    itens = {}
    for iid, typ, lvl, st, pano, cond in sql_query(
            'SELECT id, type, level, statsTemplate, panoplie, conditions FROM starloco_game.item_template '
            f'WHERE type IN ({",".join(map(str, tipos))}) AND id < 30000'):
        iid, typ, lvl = int(iid), int(typ), int(lvl)
        if cond.strip() or not nome_item(iid) or lvl > 200:
            continue
        itens[iid] = {'t': typ, 'l': lvl, 's': st, 'st': stats_de(st), 'p': int(pano)}
    usados = set()
    for L in NIVEIS:
        for elem, (_, _, dano) in ELEMENTOS.items():
            escolha, pegos = [], set()
            for pos, _, ts in SLOTS:
                cands = [(nota(it['st'], elem) + (dano_arma(it['s'], dano) * 2.5 if pos == 1 else 0), iid)
                         for iid, it in itens.items() if it['t'] in ts and it['l'] <= L and iid not in pegos]
                cands = [c for c in cands if c[0] > 0]
                if not cands:
                    continue
                best = max(cands)[1]
                pegos.add(best)
                escolha.append(f'{pos}={best}')
                usados.add(best)
            if escolha:
                rows.append(('build', f'{L}:{elem}', ';'.join(escolha)))

    # conjuntos: nível = maior nível das peças; nota por atributo com todas as peças + bônus completo
    bonus_db = {int(r[0]): r[2] for r in sql_query('SELECT ID, items, bonus FROM starloco_game.itemsets')}
    for sid, s in SETS.items():
        ids = [i for i in s.get('i', []) if i in itens or nome_item(i)]
        pecas = [itens[i] for i in s.get('i', []) if i in itens]
        if len(pecas) < 3 or len(pecas) != len(s.get('i', [])):
            continue
        total = {}
        for it in pecas:
            for k, v in it['st'].items():
                total[k] = total.get(k, 0) + v
        blocos = [b for b in (bonus_db.get(int(sid)) or '').split(';') if b.strip()]
        completo = blocos[-1] if blocos else ''
        for par in completo.split(','):
            if ':' in par:
                k, v = par.split(':')[:2]
                try:
                    k = int(k)
                    total[NEGATIVO.get(k, k)] = total.get(NEGATIVO.get(k, k), 0) + (-1 if k in NEGATIVO else 1) * int(v)
                except ValueError:
                    pass
        nivel = max(it['l'] for it in pecas)
        notas = [round(nota(total, e)) for e in ELEMENTOS]
        resumo = []
        for k, rot in ((111, 'PA'), (128, 'PM'), (117, 'alcance')):
            if total.get(k, 0) >= 1:
                resumo.append(f'+{int(total[k])} {rot}')
        for e, (eid, nm, _) in ELEMENTOS.items():
            if total.get(eid, 0) >= 20:
                resumo.append(f'+{int(total[eid])} {nm.lower()}')
        if total.get(125, 0) >= 20:
            resumo.append(f'+{int(total[125])} vitalidade')
        if total.get(124, 0) >= 20:
            resumo.append(f'+{int(total[124])} sabedoria')
        rows.append(('conjunto', sid, str(nivel), ','.join(map(str, notas)), s['n'],
                     ','.join(map(str, s['i'])), ', '.join(resumo[:6])))
        usados.update(i for i in s['i'] if i in itens)
    for iid in sorted(usados):
        rows.append(('item', str(iid), nome_item(iid), itens[iid]['s']))

    # ------------------------------------------------------------ onde cada monstro aparece (mapas Lua do servidor)
    grades = {}
    for mid, g, pdvs, points in sql_query('SELECT id, grades, pdvs, points FROM starloco_game.monsters'):
        lv = []
        for part in g.split('|'):
            if '@' in part:
                try:
                    lv.append(int(part.split('@')[0]))
                except ValueError:
                    pass
        grades[int(mid)] = {'lv': lv, 'raw': g, 'pdv': pdvs, 'pts': points}
    spawn = {}   # subárea -> {monstro: {graus}}
    for f in glob.glob(os.path.join(scripts, 'maps', '**', '*.lua'), recursive=True):
        src = open(f, encoding='utf-8', errors='replace').read()
        d = re.search(r'MapDef\([\s\S]*?,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*\)', src)
        pool = src.split('allowedMobGrades')[1] if 'allowedMobGrades' in src else None
        if not d or not pool:
            continue
        sa = int(d.group(3))
        tabela = re.split(r'\n\s*\}', pool, maxsplit=1)[0]   # só a tabela allowedMobGrades
        for m, g in re.findall(r'\{\s*(\d+)\s*,\s*(\d+)\s*\}', tabela):
            spawn.setdefault(sa, {}).setdefault(int(m), set()).add(int(g))
    nome_mob = lambda m: (M.get(str(m)) or {}).get('n') or f'#{m}'
    sa_nome = lambda sa: (MA['sa'].get(str(sa)) or {}).get('n') or C.SUBAREAS.get(sa)
    sa_area = lambda sa: (MA['sa'].get(str(sa)) or {}).get('a', C.AREA['id'] if sa in C.SUBAREAS else None)
    area_nome = lambda a: C.AREA['name'] if a == C.AREA['id'] else (MA['a'].get(str(a)) or {}).get('n')
    onde = {}
    for sa, mobs in spawn.items():
        nm = sa_nome(sa)
        if not nm or nm.startswith('//') or nm == 'null':
            continue
        faixa, partes = [], []
        for m, gs in sorted(mobs.items(), key=lambda x: min((grades.get(x[0], {}).get('lv') or [0]))):
            lv = grades.get(m, {}).get('lv') or []
            lvs = [lv[g - 1] for g in gs if 0 < g <= len(lv)]
            if not lvs:
                continue
            faixa += lvs
            partes.append(f'{nome_mob(m)} ({min(lvs)}' + (f'–{max(lvs)})' if max(lvs) != min(lvs) else ')'))
            onde.setdefault(m, []).append(sa)
        if faixa:
            an = area_nome(sa_area(sa)) or ''
            rows.append(('zona', str(sa), str(min(faixa)), str(max(faixa)), f'{nm}' + (f' ({an})' if an and an != nm else ''),
                         ', '.join(partes[:8]) + (f' e mais {len(partes) - 8}' if len(partes) > 8 else '')))

    # ------------------------------------------------------------ chefes
    efeitos_feitico = {}
    for sid, lv in sql_query('SELECT id, lvl5 FROM starloco_game.sorts'):
        seg = lv.split(',')[0] if lv else ''
        efeitos_feitico[int(sid)] = [int(e.split(';')[0]) for e in seg.split('|') if e and e.split(';')[0].lstrip('-').isdigit()]
    chefes = {int(r[0]) for r in sql_query('SELECT id FROM starloco_game.monsters WHERE isBoss = 1')}
    chefes |= set(C.CORE_BOSSES) | set(C.ARENA_BOSSES)
    spells_db = {int(r[0]): r[1] for r in sql_query('SELECT id, spells FROM starloco_game.monsters')}
    notas_mao = C.CHAT_VIVO.get('chefe_notas', {})
    for m in sorted(chefes):
        g = grades.get(m)
        if not g or not g['lv'] or str(m) not in M:
            continue
        nome = nome_mob(m)
        lvs = g['lv']
        pdvs = [int(x) for x in g['pdv'].split('|') if x.strip().isdigit()][:len(lvs)]
        pts = [p.split(';') for p in g['pts'].split('|') if ';' in p][:len(lvs)]
        if not pdvs or max(pdvs) < 50 or all(p[0].strip() in ('', '0') for p in pts):
            continue   # baú do tesouro, alvos parados: marcados como chefe no banco, mas não são luta de chefe
        res = []
        ultimo = g['raw'].split('|')[len(lvs) - 1]
        if '@' in ultimo:
            try:
                res = [int(x) for x in ultimo.split('@')[1].split(';')[:5]]
            except ValueError:
                res = []
        magias = [s.split('@')[0] for s in (spells_db.get(m) or '').split('|')[-2 if (spells_db.get(m) or '').endswith('|') else -1].split(';') if '@' in s]
        nomes_magias, efs = [], set()
        for sp in magias:
            try:
                sp = int(sp)
            except ValueError:
                continue
            n = (S.get(sp) or {}).get('n')
            if n and n not in nomes_magias:
                nomes_magias.append(n)
            efs.update(efeitos_feitico.get(sp, []))
        ficha = f'{nome} (nv. {min(lvs)}' + (f'–{max(lvs)}' if max(lvs) != min(lvs) else '') + ')'
        if pdvs:
            ficha += f': {min(pdvs):,}'.replace(',', '.') + (f'–{max(pdvs):,}'.replace(',', '.') if max(pdvs) != min(pdvs) else '') + ' PV'
        if pts:
            ficha += f', {pts[0][0]} PA e {pts[0][1]} PM'
        ficha += '.'
        dicas = []
        if len(res) == 5:
            fraco = min(range(5), key=lambda i: res[i])
            forte = max(range(5), key=lambda i: res[i])
            ficha += f' Resistências: ' + ', '.join(f'{EL_RES[i]} {res[i]}%' for i in range(5)) + '.'
            dicas.append(f'bata de {EL_RES[fraco]} ({res[fraco]}%)' + (f' e evite {EL_RES[forte]} ({res[forte]}%)' if res[forte] - res[fraco] >= 15 else ''))
        if nomes_magias:
            ficha += ' Feitiços: ' + ', '.join(nomes_magias[:5]) + '.'
        locais = []
        for sa in onde.get(m, [])[:3]:
            n = sa_nome(sa)
            an = area_nome(sa_area(sa))
            locais.append(n + (f' ({an})' if an and an != n else ''))
        if locais:
            ficha += ' Onde: ' + '; '.join(locais) + '.'
        elementos_dano = sorted({DANO_EL[e] for e in efs if e in DANO_EL})
        if elementos_dano:
            dicas.append('ele bate de ' + ' e '.join(elementos_dano) + ': suba a resistência a ' + ('esse elemento' if len(elementos_dano) == 1 else 'esses elementos'))
        if efs & {181, 180, 405}:
            dicas.append('ele invoca criaturas: limpe as invocações antes que o grupo seja cercado')
        if efs & {108, 81}:
            dicas.append('ele se cura: concentre o dano num turno só')
        if efs & {84, 101, 168}:
            dicas.append('ele tira PA: leve esquiva PA ou feitiços baratos')
        if efs & {77, 127, 169}:
            dicas.append('ele tira PM: não conte com fugir, fique perto de quem cura')
        if efs & {5, 6}:
            dicas.append('ele empurra ou puxa: cuidado com o posicionamento perto das paredes')
        if efs & {107, 106, 220}:
            dicas.append('ele reflete dano: olhe os buffs dele antes de bater')
        if efs & {150}:
            dicas.append('ele fica invisível: guarde golpes de área')
        if efs & {400, 401}:
            dicas.append('ele solta armadilhas ou glifos: observe as casas marcadas')
        if efs & {91, 92, 93, 94, 95}:
            dicas.append('ele rouba vida: dano rápido, luta curta')
        if pts and pts[0][1].isdigit() and int(pts[0][1]) >= 6:
            dicas.append(f'com {pts[0][1]} PM ele alcança todo mundo: segure ele no corpo a corpo')
        texto_dica = f'Como vencer {nome}: ' + '; '.join(dicas[:4]) + '.' if dicas else ''
        extras = []
        if m in C.CORE_BOSSES:
            extras.append(f'No LabTech ele solta o Núcleo do {C.CLASSES[C.CORE_BOSSES.index(m)]} sempre (100%).')
        if m in C.ARENA_BOSSES:
            extras.append('Aparece também na Arena LabTech.')
        if m in notas_mao:
            extras.append(notas_mao[m])
        if extras:
            texto_dica = (texto_dica + ' ' if texto_dica else '') + ' '.join(extras)
        rows.append(('chefe', str(m), str(min(lvs)), str(max(lvs)), ficha, texto_dica or f'{nome}: vá em grupo e leve cura.'))

    # ------------------------------------------------------------ nomes em português e onde cada monstro vive
    for m, v in M.items():
        if isinstance(v, dict) and v.get('n'):
            rows.append(('nome_mob', m, v['n']))
    todas_sa = set(int(k) for k in MA['sa']) | set(C.SUBAREAS)
    for sa in sorted(todas_sa):
        n = sa_nome(sa)
        if not n or n == 'null':
            continue
        n = n.lstrip('/')
        an = area_nome(sa_area(sa))
        rows.append(('nome_sa', str(sa), n + (f' ({an})' if an and an != n else '')))
    for m, sas in onde.items():
        rows.append(('mob_zona', str(m), ','.join(map(str, sas[:6]))))

    # ------------------------------------------------------------ raros (arquimonstros e aparições especiais) e procurados
    extra = {int(r[0]): r[1].strip() for r in sql_query('SELECT idMob, subArea, chances FROM starloco_game.extra_monster')}
    procurados = {m: extra.get(m, '') for m in C.CHAT_VIVO['procurados']}   # os fugitivos dos avisos de procurado
    raros = set(extra) | {int(r[0]) for r in sql_query('SELECT id FROM starloco_game.monsters WHERE isArchmonster = 1')}
    for m in sorted(raros - set(procurados)):
        if str(m) in M:
            rows.append(('raro', str(m), ''))
    for m, sas in sorted(procurados.items()):
        if str(m) in M:
            rows.append(('procurado', str(m), sas))

    # ------------------------------------------------------------ lugares escondidos nos arquivos do servidor
    mapas_lua = {}
    for f in glob.glob(os.path.join(scripts, 'maps', '**', '*.lua'), recursive=True):
        mm = re.match(r'(\d+)_', os.path.basename(f))
        if mm:
            mapas_lua[int(mm.group(1))] = f
    def coords(mid):
        """Coordenadas do MapDef do próprio mapa do servidor (o lang não tem todas)."""
        f = mapas_lua.get(mid)
        d = re.search(r'MapDef\([\s\S]*?,\s*(-?\d+)\s*,\s*(-?\d+)\s*,\s*(\d+)\s*\)', open(f, encoding='utf-8', errors='replace').read()) if f else None
        if d:
            return int(d.group(1)), int(d.group(2))
        m = MA['m'].get(str(mid)) or {}
        return m.get('x', '?'), m.get('y', '?')
    for pasta, nome, obs in C.CHAT_VIVO['pastas_secretas']:
        ids = sorted(int(re.match(r'(\d+)_', os.path.basename(f)).group(1))
                     for f in glob.glob(os.path.join(scripts, 'maps', pasta, '**', '*.lua'), recursive=True)
                     if re.match(r'(\d+)_', os.path.basename(f)))
        if ids:
            x, y = coords(ids[0])
            rows.append(('local_secreto', str(ids[0]), nome, f'{x},{y}', obs.replace('{mapas}', str(len(ids)))))
    por_sa = {}
    for mid, m in MA['m'].items():
        if isinstance(m, dict) and int(mid) in mapas_lua:
            por_sa.setdefault(m.get('sa'), []).append(int(mid))
    for sa, obs in C.CHAT_VIVO['subareas_ocultas'].items():
        ids = sorted(por_sa.get(sa, []))
        if ids:
            x, y = coords(ids[0])
            rows.append(('local_secreto', str(ids[0]), sa_nome(sa).lstrip('/'), f'{x},{y}', obs.replace('{mapas}', str(len(ids)))))

    # ------------------------------------------------------------ Rota dos Calabouços (scripts dos calabouços do servidor)
    boss_ids = {int(r[0]) for r in sql_query('SELECT id FROM starloco_game.monsters WHERE isBoss = 1')}
    calab = []
    for f in sorted(glob.glob(os.path.join(scripts, 'dungeons', '*.lua'))):
        chave = os.path.splitext(os.path.basename(f))[0]
        if chave.lower().startswith('nowel'):
            continue
        src = open(f, encoding='utf-8', errors='replace').read()
        salas = [int(x) for x in re.findall(r'\[(\d{3,6})\]\s*=\s*\{', src)]
        mobs = {int(x) for x in re.findall(r'\{\s*(\d+)\s*,\s*\{', src)}
        if not salas or not mobs:
            continue
        chefe = [m for m in mobs if m in boss_ids] or list(mobs)
        chefe = max(chefe, key=lambda m: max(grades.get(m, {}).get('lv') or [0]))
        lv = grades.get(chefe, {}).get('lv') or [0]
        sa = (MA['m'].get(str(salas[0])) or {}).get('sa')
        nome = ((area_nome(sa_area(sa)) if sa is not None else None) or '').lstrip('/')
        calab.append([chave, nome, chefe, lv, salas])
    usados_nome = {}
    for c in calab:
        usados_nome[c[1]] = usados_nome.get(c[1], 0) + 1
    for chave, nome, chefe, lv, salas in calab:
        generico = not nome.lower().startswith(('calabou', 'caverna', 'labirinto', 'biblioteca', 'esconderijo', 'santu'))
        if generico or usados_nome[nome] > 1:
            nome = f'Calabouço de {nome_mob(chefe)}'
        rows.append(('calabouco', chave, nome, str(chefe), f'{min(lv)}-{max(lv)}', str(salas[0]), ','.join(map(str, salas))))

    # ------------------------------------------------------------ textos escritos à mão (content.py)
    CV = C.CHAT_VIVO
    rows.append(('config', 'intervalo', '%d-%d' % CV['intervalo']))
    for regra, (quem, frases) in CV['dicas'].items():
        rows += [('dica', regra, quem, f) for f in frases]
    for (a, b), frases in CV['dicas_nivel'].items():
        rows += [('dica_nivel', f'{a}-{b}', 'O Estagiário', f) for f in frases]
    rows += [('curiosidade', '', q, f) for q, f in CV['curiosidades']]
    rows += [('segredo', '', q, f) for q, f in CV['segredos']]
    rows += [('boas_vindas', '', 'O Estagiário', f) for f in CV['boas_vindas']]
    for tipo, (quem, frases) in CV['modelos'].items():
        rows += [('modelo', tipo, quem, f) for f in frases]
    for tipo, (quem, frases) in CV['eventos'].items():
        rows += [('evento', tipo, quem, f) for f in frases]
    FG = C.FIGURANTES
    rows.append(('fig_config', 'quantidade', str(FG['quantidade'])))
    rows += [('fig_apelido', '', a) for a in FG['apelidos']]
    for tipo, frases in FG['falas'].items():
        rows += [('fig_fala', tipo, f) for f in frases]
    rows.append(('estatistica', 'jogo', f'{len(M):,}'.replace(',', '.') + '|' + f'{len(I):,}'.replace(',', '.') + '|'
                 + str(len(SETS)) + '|' + str(len(chefes))))

    for r in rows:
        for c in r[1:]:
            assert '\t' not in c and '\n' not in c, r
    out = os.path.join(os.path.dirname(scripts), 'labtech')
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, 'chat_vivo.tsv'), 'w', encoding='utf-8', newline='\n') as f:
        f.write('# Gerado por panel/tools/labtech/chatvivo.py (build.py). Lido pelo ChatVivo.java.\n')
        f.writelines('\t'.join(r) + '\n' for r in rows)
    cont = {}
    for r in rows:
        cont[r[0]] = cont.get(r[0], 0) + 1
    log('  chat vivo: ' + ', '.join(f'{k} {v}' for k, v in sorted(cont.items())))
