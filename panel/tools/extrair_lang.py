"""Gera panel/data/lang/*.json (textos em portugues usados pelo painel) a partir dos lang do servidor web.

Os lang sao dados do jogo (Ankama): por isso os JSON nao vao para o repositorio e sao gerados na instalacao,
depois do build do Mundo LabTech (para ja incluirem os itens, NPCs e mapas novos).
Uso: python panel/tools/extrair_lang.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import swf_lang  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
LANG = os.path.join(ROOT, 'server', 'web', 'lang')
OUT = os.path.join(ROOT, 'panel', 'data', 'lang')
NOMES = ['classes', 'crafts', 'dialog', 'dungeons', 'effects', 'hints', 'interactiveobjects', 'items', 'itemsets',
         'itemstats', 'jobs', 'maps', 'monsters', 'names', 'npc', 'rides', 'skills', 'spells']


def versoes():
    txt = open(os.path.join(LANG, 'versions_pt.txt'), encoding='utf-8').read().strip()
    out = {}
    for parte in txt.split('=', 1)[1].split('|'):
        if parte.count(',') == 2:
            nome, _, ver = parte.split(',')
            out[nome] = ver
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    ver = versoes()
    for nome in NOMES:
        src = os.path.join(LANG, 'swf', f'{nome}_pt_{ver[nome]}.swf')
        env = swf_lang.parse_swf(src)
        env = {k: v for k, v in env.items() if k not in ('System', '_parent')}
        with open(os.path.join(OUT, nome + '.json'), 'w', encoding='utf-8') as f:
            json.dump(swf_lang.to_json(env), f, ensure_ascii=False)
        print(f'  {nome}: {os.path.basename(src)}')


if __name__ == '__main__':
    main()
