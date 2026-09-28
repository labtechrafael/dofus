"""Gera docs/HISTORIAS.md a partir de content.py: todas as falas de todos os personagens da ilha (e dos Mercadores),
a lore dos 12 nucleos e a descricao de todos os itens. Rode de novo sempre que mudar uma fala.
Uso: python panel/tools/labtech/docs_gen.py"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, '..', '..', 'world', 'labtech')))
import content as C  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(ROOT, 'docs', 'HISTORIAS.md')

LUGAR = {mid: nome for nome, mid in C.ELEVATOR}
LUGAR.update({30014: 'Forja do Dofus', 30002: 'Praça da Gambiarra'})
LUGAR = {k: re.sub(r'\s*\(.*\)$', '', v) for k, v in LUGAR.items()}
ORDEM = [30001, 30002, 30004, 30003, 30015, 30005, 30007, 30008, 30014]
ACOES = {
    'giveGauntlet': 'entrega a Manopla Gambiarra Mk I',
    'assembleGauntlet': 'encaixa os 12 núcleos e entrega a Manopla Gambiarra Mk XII (+1 PA e alcance 2)',
    'forgeDofus': 'forja o Dofus Fermentado (se você tiver 10 Malte, 10 Lúpulo e 10 Levedura)',
    'openBank': 'abre o banco',
    'arcade': 'joga uma partida: aparece uma das telas abaixo, ao acaso',
}


def locais(n):
    loja = next((l for l in C.LOJA_NPCS if l['id'] == n['id']), None)
    if loja:
        return ['Bonta, ao lado do zaap' if loja['map'] == 4263 else 'Brâkmar, ao lado do zaap']
    return [LUGAR.get(m, str(m)) for m in n.get('maps', {})]


def acao(alvo):
    code = alvo[4:]
    for k, txt in ACOES.items():
        if k in code:
            return txt
    return None


def npc_md(n):
    d = C.DIALOGS.get(n['id'])
    if not d:
        return ''
    nodes = {k: v for k, v in d.items() if not k.endswith('_lua')}
    L = [f"### {n['name']}", f"*{', '.join(locais(n))}*", '']
    feitos = set()
    teleportes, prateleiras = [], []

    def no(key, nivel=0):
        feitos.add(key)
        texto, respostas = nodes[key]
        L.append('> ' + texto)
        L.append('')
        for resp, alvo in respostas:
            alvo = alvo or 'inicio'
            if alvo == 'fim' or resp.startswith('Voltar'):
                continue
            if isinstance(alvo, str) and alvo.startswith('lua:'):
                if 'teleport' in alvo:
                    teleportes.append(resp)
                elif 'lojaAbrir' in alvo:
                    prateleiras.append(resp)
                else:
                    a = acao(alvo)
                    L.append(f'**— {resp}** *({a})*' if a else f'**— {resp}**')
                    L.append('')
                continue
            if alvo in nodes and alvo not in feitos:
                L.append(f'**— {resp}**')
                L.append('')
                no(alvo, nivel + 1)
        if teleportes and key == 'inicio' and n['id'] == 3001:
            L.append('**Destinos do elevador:** ' + ', '.join(teleportes) + '.')
            L.append('')
            teleportes.clear()

    inicio = 'inicio' if 'inicio' in nodes else next(iter(nodes))
    no(inicio)
    if prateleiras:
        L.append('**Prateleiras:** ' + ', '.join(p for p in prateleiras) + '.')
        L.append('')
    resto = [k for k in nodes if k not in feitos]
    if resto:
        titulo = 'Telas do fliperama' if n['id'] == 3006 else 'Em outros momentos'
        L.append(f'**{titulo}:**')
        L.append('')
        for k in resto:
            if k in feitos:
                continue
            no(k)
    return '\n'.join(L)


def main():
    L = ['# Histórias da Ilha LabTech', '',
         'Todas as falas de todos os personagens, gerado automaticamente a partir de',
         '[`panel/world/labtech/content.py`](../panel/world/labtech/content.py) '
         '(rode `python panel/tools/labtech/docs_gen.py` para atualizar).', '',
         '> **Spoiler!** Aqui estão todas as conversas, a missão inteira e os segredos da ilha.', '',
         '## Sumário', '',
         '- [A classe LabTech](#a-classe-labtech)', '- [Os 12 núcleos](#os-12-núcleos)',
         '- [Personagens da ilha](#personagens-da-ilha)', '- [Bar das Celebridades](#bar-das-celebridades)',
         '- [Mercadores LabTech](#mercadores-labtech)', '- [Itens e suas histórias](#itens-e-suas-histórias)', '']
    lang = C.CLASS13['lang']
    L += ['## A classe LabTech', '', f"*{lang['sd']}*", '', lang['d'], '',
          f"**{lang['pt']}**: {lang['pd']}", '']
    L += ['## Os 12 núcleos', '',
          'A Manopla Gambiarra precisa de um núcleo de cada classe. Cada um guarda um pedaço da bênção que os deuses '
          'deram de mão beijada às doze classes, e cada chefe solta o seu.', '', '| Núcleo | Chefe | O que ele guarda |',
          '|---|---|---|']
    chefes = ['Gobball Real', 'Wa Wabbit', 'Escarafeio Dourado', 'Rato Preto', 'Crackler Lendário', 'Rato Branco',
              'Mob Esponja', 'Minotororo', 'Lorde Corvo', 'Treechnid Ancestral', 'Vlad Sombrio', 'Tanukouï San']
    for i, (classe, lore) in enumerate(zip(C.CLASSES, C.CORE_LORE)):
        L.append(f'| {classe} | {chefes[i]} | {lore[0].upper() + lore[1:]} |')
    L.append('')
    celeb_ids = {3014 + i for i in range(len(C.CELEBRITIES))}
    loja_ids = {l['id'] for l in C.LOJA_NPCS}
    L += ['## Personagens da ilha', '']
    ilha = [n for n in C.NPCS if n['id'] not in celeb_ids and n['id'] not in loja_ids]
    ilha.sort(key=lambda n: min((ORDEM.index(m) for m in n.get('maps', {}) if m in ORDEM), default=99))
    for n in ilha:
        L += [npc_md(n), '']
    L += ['## Bar das Celebridades', '', 'Vinte famosos que amam cerveja, todos em versão paródia.', '']
    for n in C.NPCS:
        if n['id'] in celeb_ids:
            L += [npc_md(n), '']
    L += ['## Mercadores LabTech', '']
    for n in C.NPCS:
        if n['id'] in loja_ids:
            L += [npc_md(n), '']
    L += ['## Itens e suas histórias', '', '| Item | Descrição |', '|---|---|']
    for it in C.ITEMS:
        if it.get('desc'):
            L.append(f"| **{it['name']}** | {it['desc']} |")
    L.append('')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(L))
    print('ok', OUT)


if __name__ == '__main__':
    main()
