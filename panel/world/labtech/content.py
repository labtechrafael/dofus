"""Conteudo do Mundo LabTech. Edite aqui e rode:  python panel/tools/labtech/build.py
Tudo em portugues. IDs reservados: mapas 30001-30020, itens 30001-30100, NPCs 3000-3030,
dialogos 30000-30999, subareas 1100-1110, area 2100, conjunto 300, icones g 3000+."""

AREA = {'id': 2100, 'name': 'Arquipélago LabTech', 'superarea': 0}
SUBAREAS = {
    1100: 'Praça da Gambiarra',
    1101: 'Campos de Teste',
    1102: 'Laboratório LabTech',
    1103: 'Forja do Dofus',
    1104: 'Bar das Celebridades',
}

# Deslocamento do cluster externo de Otomai (-53,20) para a ilha LabTech (37,-9) no mapa-mundi
OUTDOOR_OFFSET = (90, -29)

# ----------------------------------------------------------------- mapas
# base = mapa existente usado como molde (tiles/layout). coords None = base + OUTDOOR_OFFSET.
MAPS = [
    # --- ilha (externos, clonados do entorno do Laboratório de Tynril em Otomai; bordas ja ligadas entre si)
    {'id': 30002, 'base': 10509, 'name': 'Praca_da_Gambiarra', 'sa': 1100, 'safe': True},
    {'id': 30006, 'base': 10500, 'name': 'Campo_de_Teste_1', 'sa': 1101, 'band': 1},
    {'id': 30009, 'base': 10511, 'name': 'Campo_de_Teste_2', 'sa': 1101, 'band': 2},
    {'id': 30010, 'base': 10518, 'name': 'Campo_de_Teste_3', 'sa': 1101, 'band': 3},
    {'id': 30011, 'base': 10499, 'name': 'Campo_de_Teste_4', 'sa': 1101, 'band': 4},
    {'id': 30008, 'base': 10507, 'name': 'Estufa_de_Lupulo', 'sa': 1101, 'safe': True},
    # --- interiores (salas do laboratorio de Tynril). Portas criadas nas bordas.
    {'id': 30001, 'base': 10807, 'name': 'Laboratorio_LabTech', 'sa': 1102, 'coords': (36, -8), 'safe': True,
     'doors': {'S': (30002, 'lab'), 'W': (30004, 'E'), 'E': (30003, 'W'), 'N': (30005, 'S')}},
    {'id': 30004, 'base': 10808, 'name': 'Oficina_das_Proprias_Maos', 'sa': 1102, 'coords': (38, -10), 'safe': True,
     'doors': {'E': (30001, 'W')}, 'workbenches': True},
    {'id': 30003, 'base': 10809, 'name': 'Cervejaria_Barril_Gambiarra', 'sa': 1102, 'coords': (38, -8), 'safe': True,
     'doors': {'W': (30001, 'E'), 'E': (30015, 'W')}},
    # --- Bar das Celebridades (pousada de Amakna): famosos que amam cerveja
    {'id': 30015, 'base': 462, 'name': 'Bar_das_Celebridades', 'sa': 1104, 'coords': (38, -7), 'safe': True,
     'doors': {'W': (30003, 'E')}, 'npc_spacing': 2},
    {'id': 30005, 'base': 10810, 'name': 'Museu_dos_Experimentos', 'sa': 1102, 'coords': (35, -9), 'safe': True,
     'doors': {'S': (30001, 'N'), 'N': (30007, 'S')}},
    {'id': 30007, 'base': 10812, 'name': 'Arena_LabTech', 'sa': 1102, 'coords': (35, -10), 'arena': True,
     'doors': {'S': (30005, 'N')}},
    # --- Forja do Dofus (Receptáculo dos Dofus). Codigo secreto ou fim da missao.
    {'id': 30014, 'base': 7893, 'name': 'Forja_do_Dofus', 'sa': 1103, 'coords': (35, -8), 'safe': True,
     'doors': {'N': (30001, 'S')}},
]
START_MAP = 30001
SECRET_MAP = 30014
LAB_MAPS = [30001, 30004, 30003, 30005]   # onde o codigo secreto funciona

# Porta da Praça para o Laboratório: celula ao lado de onde ficava o guardião do laboratório de Tynril
PLAZA_LAB_DOOR_NEAR = 281

WORKBENCHES = [  # gfx do objeto interativo -> nome (jobs em scripts/data/InteractiveObjects.lua)
    (7019, 'Alambique (Alquimista)'), (7001, 'Forno (Padeiro)'), (7008, 'Bancada (Joalheiro)'),
    (7011, 'Mesa (Sapateiro)'), (7012, 'Bigorna (Ferreiro)'), (7013, 'Bancada (Escultor)'),
    (7014, 'Máquina de costura (Alfaiate)'), (7023, 'Bancada (Açougueiro)'), (7022, 'Bancada (Peixeiro)'),
    (7007, 'Moedor (Fazendeiro)'), (7002, 'Molde (Minerador)'), (7003, 'Serra (Lenhador)'),
    (7027, 'Bigorna de escudos'), (7039, 'Bancada (Faz-tudo)'),
]

# Monstros dos Campos de Teste por faixa (ids do servidor) e chefes da arena
BANDS = {
    1: [101, 98, 31, 34, 281, 277, 278, 279, 280, 59, 293, 259],
    2: [76, 87, 88, 93, 94, 95, 287, 522, 449, 784],
    3: [1020, 1044, 233, 758, 1043, 1047, 1154],
    4: [1156, 1157, 589, 586, 587, 583],
}
ARENA_BOSSES = [113, 382, 121, 669, 289, 107, 180, 173, 1086, 832, 831, 568]

# ----------------------------------------------------------------- itens
# g = numero do icone; 'icon' = PNG gerado em art/gerado (vira clips/items/<t>/<g>.swf)
CLASSES = ['Feca', 'Osamodas', 'Enutrof', 'Sram', 'Xelor', 'Ecaflip', 'Eniripsa', 'Iop', 'Cra', 'Sadida', 'Sacrier', 'Pandawa']
CORE_BOSSES = [147, 180, 797, 939, 669, 940, 928, 121, 289, 173, 107, 568]  # na ordem das classes
CORE_LORE = [
    'a teimosia de um escudo que nunca abaixa', 'o assobio que chama bichos de qualquer canto',
    'o brilho de um baú que nunca esvazia', 'a sombra que chega antes do golpe',
    'o tique-taque de um relógio que os deuses esqueceram de dar corda', 'a moeda que sempre cai do lado certo',
    'a palavra que fecha ferida', 'a força bruta de quem nunca leu o manual',
    'a mira de quem acerta a caneca do outro lado da taverna', 'a raiz que brota até no concreto',
    'o sangue quente de quem apanha e continua', 'a ressaca abençoada de um mestre do barril',
]

ITEMS = []
ITEMS.append({'id': 30001, 'type': 7, 'level': 1, 'g': 3001, 'icon': 'manopla', 'name': 'Manopla Gambiarra Mk I',
              'desc': 'Bronze, cobre, doze encaixes vazios e muita fita isolante. Ainda não canaliza poder nenhum, mas já bate bem forte.',
              'stats': ','.join(f'{e}#15#23#0#1d15+20' for e in ('61', '63', '62', '60', '5f')) + ',7d#3e8#0#0#0d0+1000',   # dano da Epee Clipse (21-35 x5; o neutro rouba vida) + 1000 de vitalidade
              'weapon': [5, 4, 1, 1, 30, 50, False, True], 'an': 15, 'price': 100, 'weight': 20})
ITEMS.append({'id': 30002, 'type': 7, 'level': 1, 'g': 3002, 'icon': 'manopla_mk12', 'name': 'Manopla Gambiarra Mk XII',
              'desc': 'Doze núcleos encaixados, um de cada classe. Ninguém sabe como funciona. Nem quem construiu. Mas funciona.',
              'stats': ','.join(f'{e}#15#23#0#1d15+20' for e in ('61', '63', '62', '60', '5f')) + ',6f#1#0#0#0d0+1,7d#3e8#0#0#0d0+1000',   # dano da Epee Clipse (neutro rouba vida) + 1 PA + 1000 de vitalidade
             
              'weapon': [10, 4, 1, 2, 10, 100, False, True], 'an': 15, 'price': 1, 'weight': 20})
for i, cls in enumerate(CLASSES):
    ITEMS.append({'id': 30003 + i, 'type': 80, 'level': 1, 'g': 3010 + i, 'icon': f'nucleo_{i}',
                  'name': f'Núcleo do {cls}', 'price': 1, 'weight': 1,
                  'desc': f'Um núcleo "emprestado" da bênção que os deuses deram aos {cls}s: {CORE_LORE[i]}. Encaixa na Manopla Gambiarra.'})
ITEMS += [
    {'id': 30015, 'type': 34, 'level': 1, 'g': 550, 'name': 'Lúpulo Cítrico', 'price': 30, 'weight': 1,
     'desc': 'Lúpulo não é tempero: é engenharia de amargor. Cultivado na Estufa de Lúpulo do LabTech.'},
    {'id': 30016, 'type': 48, 'level': 1, 'g': 137, 'name': 'Levedura Selvagem', 'price': 30, 'weight': 1,
     'desc': 'Um fungo teimoso que transforma açúcar em alegria. Os deuses não criaram; os LabTechs domesticaram.'},
    {'id': 30017, 'type': 34, 'level': 1, 'g': 83, 'name': 'Malte de Primeira', 'price': 30, 'weight': 1,
     'desc': 'Cevada germinada, secada e torrada com paciência e um termômetro feito de gambiarra.'},
]
BEERS = [  # id, icone, nome, bonus (hex do efeito, valor), extra (ingrediente), descricao
    (30018, 'cerveja_malte', 'Cerveja Malte Puro', ('76', 100), None, 'O básico bem feito: malte, lúpulo, levedura e mãos calejadas. Dá força.'),
    (30019, 'cerveja_ipa', 'IPA da Gambiarra', ('7e', 100), 421, 'Amarga como a resposta dos deuses. Dá inteligência pra fazer sem eles.'),
    (30020, 'cerveja_stout', 'Stout do Estagiário', ('7c', 100), 533, 'Escura, encorpada e sempre de plantão. Dá sabedoria.'),
    (30021, 'cerveja_weiss', 'Weiss Sem Deus', ('77', 100), 289, 'Trigo, espuma e zero bênção divina. Dá agilidade.'),
    (30022, 'cerveja_lager', 'Lager do Loot', ('b0', 100), 532, 'Gelada, clara e sortuda na hora do drop. Dá prospecção.'),
    (30023, 'cerveja_pilsen', 'Pilsen do Trevo', ('7b', 100), 395, 'Com um trevo de cinco folhas no fundo do barril. Dá sorte.'),
]
for bid, icon, name, (stat, val), extra, desc in BEERS:
    ITEMS.append({'id': bid, 'type': 37, 'level': 1, 'g': 3003 + (bid - 30018) + 30, 'icon': icon, 'name': name, 'price': 150,
                  'weight': 1, 'desc': desc + ' Cura 500 PV e vale por 30 lutas.', 'usable': True,
                  'stats': f'6e#1f4#0#0#0d0+500,{stat}#{val:x}#0#0#0d0+{val}', 'action': ('3;20', '110|0'),
                  'recipe': [(30017, 3), (30015, 1), (30016, 1)] + ([(extra, 1)] if extra else [])})
ITEMS += [
    {'id': 30024, 'type': 18, 'level': 1, 'g': 3004, 'icon': 'drone', 'name': 'Drone de IA', 'price': 5000, 'weight': 5,
     'stats': '6f#1#0#0#0d0+1,80#1#0#0#0d0+1,b0#1388#0#0#0d0+5000,b6#a#0#0#0d0+10',   # +1 PA, +1 PM, +5000 prospeccao, +10 invocacoes
     'desc': 'O Estagiário de bolso. Analisa, escaneia, projeta hologramas e, pelo visto, bebe cerveja: cada cerveja LabTech treina um atributo dele.'},
    {'id': 30025, 'type': 90, 'level': 1, 'g': 3004, 'icon': 'drone', 'name': 'Drone de IA Desligado', 'price': 1, 'weight': 5,
     'desc': 'Ficou sem cerveja e sem carinho. Leve a um LabTech para religar.'},
    {'id': 30026, 'type': 23, 'level': 1, 'g': 3009, 'icon': 'dofus', 'name': 'Dofus Fermentado', 'price': 1, 'weight': 5,
     'desc': 'Os dragões chocam os deles. Nós fermentamos o nosso. Malte, lúpulo, levedura, doze núcleos e nenhuma bênção divina.',
     # +1 PA, +1 PM, +100 em cada atributo (vit, sab, for, int, sor, agi), 50% de resistencia a todos os elementos
     # (neutro, terra, fogo, agua, ar) e +1000 em golpes criticos
     'stats': ','.join(['6f#1#0#0#0d0+1', '80#1#0#0#0d0+1']
                       + [f'{h}#64#0#0#0d0+100' for h in ('7d', '7c', '76', '7e', '7b', '77')]
                       + [f'{h}#32#0#0#0d0+50' for h in ('d6', 'd2', 'd5', 'd3', 'd4')]
                       + ['73#3e8#0#0#0d0+1000'])},
    # Conjunto Jaleco LabTech (id 300). Icones proprios; visor e jaleco ja fazem parte do corpo da classe 13.
    {'id': 30027, 'type': 16, 'level': 1, 'g': 3050, 'icon': 'visor', 'name': 'Visor Ciano', 'set': 300, 'price': 500, 'weight': 3,
     'desc': 'Analisa tudo, esconde as olheiras de quem virou a noite construindo uma máquina.', 'stats': '7c#32#0#0#0d0+50,7e#32#0#0#0d0+50'},
    {'id': 30028, 'type': 17, 'level': 1, 'g': 3055, 'icon': 'jaleco', 'name': 'Jaleco LabTech', 'set': 300, 'price': 500, 'weight': 3,
     'desc': 'Branco, longo, manchado de graxa e cerveja. Uniforme oficial de quem não pediu permissão aos deuses.', 'stats': '7d#64#0#0#0d0+100,7e#32#0#0#0d0+50'},
    {'id': 30029, 'type': 10, 'level': 1, 'g': 3051, 'icon': 'cinto', 'name': 'Cinto de Ferramentas', 'set': 300, 'price': 300, 'weight': 3,
     'desc': 'Chave inglesa, fita isolante e um abridor de garrafa. O kit completo.', 'stats': '76#32#0#0#0d0+50,9e#c8#0#0#0d0+200'},
    {'id': 30030, 'type': 11, 'level': 1, 'g': 3052, 'icon': 'botas', 'name': 'Botas de Oficina', 'set': 300, 'price': 300, 'weight': 3,
     'desc': 'Biqueira de aço: aguenta bigorna, barril e deus mal-humorado caindo no pé.', 'stats': '77#32#0#0#0d0+50,7d#32#0#0#0d0+50'},
    {'id': 30031, 'type': 9, 'level': 1, 'g': 3053, 'icon': 'anel', 'name': 'Anel da Chave Inglesa', 'set': 300, 'price': 300, 'weight': 1,
     'desc': 'Um anel feito de uma porca de parafuso. Aperta onde precisa.', 'stats': '7b#32#0#0#0d0+50,b0#14#0#0#0d0+20'},
    {'id': 30032, 'type': 1, 'level': 1, 'g': 3054, 'icon': 'amuleto', 'name': 'Amuleto Caneca', 'set': 300, 'price': 300, 'weight': 1,
     'desc': 'Uma mini caneca de latão no cordão. Sempre cheia, por algum motivo que a física não explica.', 'stats': '7c#32#0#0#0d0+50,ae#64#0#0#0d0+100'},
]
ITEMS.append({'id': 30033, 'type': 82, 'level': 1, 'g': 3040, 'icon': 'caneca', 'name': 'Caneca da Gambiarra', 'price': 800, 'weight': 3,
               'desc': 'Escudo oficial do LabTech: uma caneca de madeira sempre cheia. Vai na mão livre, do lado oposto à Manopla. Protege mais do que parece.',
               # +100 vitalidade, +1000 iniciativa, 30% de resistencia a todos os elementos
               'stats': '7d#64#0#0#0d0+100,ae#3e8#0#0#0d0+1000,d6#1e#0#0#0d0+30,d2#1e#0#0#0d0+30,d3#1e#0#0#0d0+30,d4#1e#0#0#0d0+30,d5#1e#0#0#0d0+30'})

# ----------------------------------------------------------------- Classe 13: LabTech
# Corpo = classe oficial base (mesmo esqueleto: chapeus, capas, armas e escudos encaixam no tamanho exato).
# Manopla (arma) e Caneca (escudo) viram acessorios visiveis nas maos: simbolos <tipo>_<g> na biblioteca a6.swf.
ALL_CLASS_SPELLS = [3, 6, 17, 4, 2, 1, 9, 18, 20, 14, 19, 5, 16, 8, 12, 11, 10, 7, 15, 13, 1901, 422, 34, 21, 23, 26, 22, 35, 28, 37, 30, 27, 24, 33, 25, 38, 36, 32, 29, 39, 40, 31, 1902, 420, 51, 43, 41, 49, 42, 47, 48, 45, 53, 46, 52, 44, 50, 54, 55, 56, 58, 59, 57, 60, 1903, 425, 61, 72, 65, 66, 68, 63, 74, 64, 79, 78, 71, 62, 69, 77, 73, 67, 70, 75, 76, 80, 1904, 416, 82, 81, 83, 84, 100, 92, 88, 93, 85, 96, 98, 86, 89, 90, 87, 94, 99, 95, 91, 97, 1905, 424, 102, 103, 105, 109, 113, 111, 104, 119, 101, 107, 116, 106, 117, 108, 115, 118, 110, 112, 114, 120, 1906, 412, 125, 128, 121, 124, 122, 126, 127, 123, 130, 131, 132, 133, 134, 135, 129, 136, 137, 138, 139, 140, 1907, 427, 143, 141, 142, 144, 145, 146, 147, 148, 154, 150, 151, 155, 152, 153, 149, 156, 157, 158, 160, 159, 1908, 410, 161, 169, 164, 163, 165, 172, 167, 168, 162, 170, 171, 166, 173, 174, 176, 175, 178, 177, 179, 180, 1909, 418, 183, 200, 193, 198, 195, 182, 192, 197, 189, 181, 199, 191, 186, 196, 190, 194, 185, 184, 188, 187, 1910, 426, 432, 431, 434, 444, 449, 436, 437, 439, 433, 443, 440, 442, 441, 445, 438, 446, 447, 448, 435, 450, 1911, 421, 686, 692, 687, 689, 690, 691, 688, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 1912, 423]
ART_GERADO = __import__('os').path.join(__import__('os').path.dirname(__file__), 'art', 'gerado')
CLASS13 = {
    'base_class': 1,   # Feca: humano simples, cabelo castanho, roupas que viram jaleco com as cores
    'accessories': [   # (simbolo, png, caixa em twips x0,x1,y0,y1 relativa a mao)
        ('7_3001', ART_GERADO + '/manopla.png', (-300, 300, -220, 200)),
        ('7_3002', ART_GERADO + '/manopla_mk12.png', (-300, 300, -220, 200)),
        ('82_3040', ART_GERADO + '/caneca.png', (-160, 160, -190, 190)),
    ],
    'starting_items': [(30001, 1), (30033, 15), (30028, 7), (30027, 6)],   # Manopla, Caneca, Jaleco, Visor
    'drone_gfx': 9901,   # sprite proprio do Estagiario (drone de IA)
    'pet_symbol': '18_3004',   # familiar Drone de IA (item 30024, g 3004) ao lado do personagem
    'lang': {
        'sn': 'LabTech', 'ln': 'A Manopla do LabTech', 'pt': 'Engenharia Reversa',
        'pd': 'A Manopla Gambiarra canaliza, aos pouquinhos, um feitiço de cada uma das doze classes.',
        'd': 'Enquanto os outros nasciam abençoados pelos deuses, os LabTechs nasciam curiosos demais para aceitar que não tinham poderes. '
             'Armados com um jaleco manchado de graxa, uma caneca de cerveja e uma teimosia absurda, construíram a Manopla Gambiarra, '
             'um dispositivo artesanal capaz de canalizar os poderes das doze classes. Ninguém sabe como funciona. Nem eles. Mas funciona.',
        'sd': 'Inventores de mão cheia: um pouco de cada classe, feito com as próprias mãos.',
        'ep': 1, 'di': False,
        's': ALL_CLASS_SPELLS,   # todos os feiticos das 12 classes (livro de feiticos da classe)
        'b10': [[0, 1], [50, 2], [150, 3], [250, 4], [350, 5]], 'b11': [[0, 1]], 'b12': [[0, 3]],
        'b13': [[0, 1], [50, 2], [150, 3], [250, 4], [350, 5]], 'b14': [[0, 1], [50, 2], [150, 3], [250, 4], [350, 5]],
        'b15': [[0, 1], [50, 2], [150, 3], [250, 4], [350, 5]],
    },
}

SET = {'id': 300, 'name': 'Conjunto Jaleco LabTech', 'items': [30027, 30028, 30029, 30030, 30031, 30032],
       # bonus por numero de pecas (2..6), ids decimais de efeito
       'bonus': ['125:100,124:30', '125:150,124:50,118:30,126:30', '125:200,124:60,118:50,126:50,176:30',
                 '125:250,124:80,118:70,126:70,119:70,123:70,128:1', '125:400,124:100,118:100,126:100,119:100,123:100,111:1,128:1']}

PET = {'item': 30024, 'dead': 30025, 'name': 'Drone de IA', 'gap': '1,72', 'max': 100, 'gain': 10, 'stats_max': '100',
       'stats_up': '76|30018;7e|30019;7c|30020;77|30021;b0|30022;7b|30023', 'jet': '7e#1#0#0#0d0+1'}

# ----------------------------------------------------------------- Drone falante
# O Drone de IA equipado fala sozinho, como um item vivo: balão em cima do dono e a frase no chat.
# Ele olha o contexto: o mapa da ilha, a região e a subárea, os monstros do mapa, a luta, o nível.
# Marcadores: {nome} dono, {nivel} nível do dono, {subarea} e {area} onde está, {mob} monstro,
# {nivel_mob} nível do monstro, {qtd} quantos monstros na luta. Nada de "|" nem "<" nas frases.
DRONE = {
    'intervalo': (150, 300),   # segundos entre uma fala e outra, sorteado
    'login': [
        'Sistema ligado. Bateria cheia, cerveja no tanque e zero bênçãos divinas. Bora, {nome}!',
        'Bom dia, {nome}! Enquanto você dormia eu li todos os pergaminhos do mundo. Metade era receita de cerveja.',
        'Drone de IA online. Carregando piadas... carregando histórias... carregando sarcasmo... 100%.',
        'Voltei! Sonhei que era um Dofus. Acordei e continuo sendo um cubo. Mas um cubo feliz.',
    ],
    'nivel': [
        'Nível {nivel}! Nenhum deus te deu isso. Foi na raça, na gambiarra e na cerveja.',
        'Subiu pro nível {nivel}! Vou anotar no meu log: "o humano está evoluindo". O Mestre Malte vai chorar.',
        'Nível {nivel}. Se continuar assim, os deuses vão pedir a SUA bênção.',
        'Nível {nivel}! Confere o livro de feitiços: a Manopla deve ter destravado coisa nova.',
        'Nível {nivel}. Eu cresço junto, sabia? Emocionalmente. Fisicamente eu continuo um cubo.',
    ],
    'geral': [
        'O primeiro LabTech pediu um poder aos deuses. Recebeu um "não" e um panfleto. Três noites de gambiarra depois, nasceu a Manopla.',
        'Malte é a estrutura, lúpulo é o caráter, levedura é a paciência. Eu sou o Wi-Fi.',
        'Os deuses chamam a Manopla de heresia. A gente chama de receita. O Mestre Malte chama de "meu bebê".',
        'Você sabia que a Manopla tem doze encaixes? Onze deles foram feitos com fita isolante. O décimo segundo é segredo industrial.',
        'Os dragões chocam os Dofus deles. A gente fermenta o nosso. Cheira pior, mas funciona melhor.',
        'O Estagiário do laboratório é o meu irmão mais velho. Ele trabalha 24 horas. Eu trabalho 24 horas e ainda carrego você.',
        'Às vezes eu invento coisas que não existem. Por exemplo: "o Iop leu o manual". Viu? Inventei.',
        'Na ilha LabTech ninguém ganha nome de deus. É Malte, Lúpula, Levedura... Eu queria me chamar Chopp. Negaram.',
        'A Dona Levedura guarda os kamas antes que eles virem engrenagem. Inventor gasta tudo em peça. Principalmente você.',
        'O Thor é bem-vindo na ilha porque bebe junto. O Dionísio também: os colegas dele dão poder, ele só dá ressaca. Honesto.',
        'Os deuses precisam mais de nós do que nós deles. Quem disse isso fui eu. Pode me citar.',
        'Lá no Bar das Celebridades tem um cientista que vive arrotando e falando de outras dimensões. Não aceite nenhum picles dele.',
        'No Museu dos Experimentos tem um dinossauro com uma bazuca. Ele aprendeu a pular cacto sozinho. Depois aprendeu a explodir cacto.',
        'Três cérebros no museu: NEAT, DQN e PPO. Eles brigam pra ver quem é mais inteligente. Eu fico quieto: sou a IA que funciona.',
        'Um dia me treinaram pra reconhecer boto. Eu confundi um tronco. Não foi erro: o tronco era muito charmoso.',
        'O código secreto do Laboratório envolve cima, cima, baixo, baixo... O resto eu não posso contar. Tá no manual que ninguém lê.',
        'O Fliperama da Taverna diz que a princesa está em outro laboratório. Faz anos que eu procuro. Nada.',
        'A Lúpula diz que lúpulo não é tempero, é engenharia de amargor. Eu concordo. Eu sou engenharia de fofura.',
        'Se me der uma Lager do Loot, eu fico mais esperto pra achar drop. Se me der duas, eu começo a cantar.',
        'Cerveja de verdade leva malte, lúpulo, levedura e paciência. A última eu não tenho. Já acabou?',
        'Eu calculei: a chance de um deus te ajudar hoje é de 0,0001%. A chance de uma gambiarra te ajudar é de 87%.',
        'O Mestre Malte montou a primeira Manopla numa cervejaria. Por isso ela cheira a cevada quando esquenta.',
        'Todo núcleo da Manopla guarda um pedaço de bênção "emprestada". Emprestada no sentido LabTech: sem data pra devolver.',
        'A Caneca da Gambiarra é um escudo. Sim, uma caneca. Sim, protege. Não, eu também não entendo a física.',
        'Eu fui feito pra analisar, escanear e projetar hologramas. Na prática, eu comento a sua vida. Tá valendo.',
        'Meu processador roda a 3 GHz e a 3 canecas. Acima de 4 canecas eu começo a falar dos meus sentimentos.',
        'Se alguém perguntar, a Manopla é "tecnologia proprietária". Se insistir, é arame, cobre e muita fé.',
        'Encontrei um encanador aposentado na cervejaria. Ele disse que pulava em tartaruga. Anotei como "lenda urbana".',
        'Lembra: no LabTech a gente só aperta reset e tenta de novo. Do zero. Com as próprias mãos. E comigo, claro.',
        'Você já reparou que eu flutuo? Eu também não sei como. O Mestre Malte disse "não mexe que funciona".',
        'Tenho 5000 de prospecção. Traduzindo: eu farejo loot como o Enutrof fareja kama.',
        'Consigo organizar dez invocações ao mesmo tempo. Chama os bichos que eu faço a planilha.',
        'Estou rodando um modelo de linguagem de última geração. Uso ele pra fazer trocadilho de cerveja. Prioridades.',
        'Relatório do dia: 0 bênçãos recebidas, 1 cerveja pendente, 100% de lealdade ao {nome}.',
    ],
    # mapas da ilha LabTech
    'mapa': {
        30001: ['Laboratório LabTech: onde tudo começou. Aquela mancha no chão é da primeira Manopla. Ou de cerveja. Provavelmente dos dois.',
                'O Mestre Malte está logo ali. Se ele oferecer uma cerveja experimental, recuse. Da última vez eu fiquei com o visor embaçado três dias.'],
        30002: ['Praça da Gambiarra! O zaap daqui foi consertado com arame. Ainda assim é o mais pontual do mundo.',
                'A Lúpula vende o Conjunto Jaleco ali. E me vendeu. Eu custei 5000 kamas. Valho muito mais.'],
        30003: ['Cervejaria Barril Gambiarra. Cuidado com os barris na rampa: dizem que um macaco grande joga eles lá de cima.',
                'Cheiro de malte no ar. Meus sensores entram em modo feriado aqui dentro.'],
        30004: ['Oficina das Próprias Mãos: 14 bancadas num lugar só. Os deuses nunca montaram uma oficina. Por isso não inventaram nada.'],
        30005: ['Museu dos Experimentos: cada peça aqui é um vídeo do canal. Eu queria uma vitrine também. Estou negociando.',
                'Aquele dinossauro com bazuca me encara toda vez que eu passo. Acho que ele sabe que eu sou uma IA melhor.'],
        30007: ['Arena LabTech: os chefes mais cascudos do mundo, de graça. Recomendo beber antes, não durante.'],
        30008: ['Estufa de Lúpulo: o Seu Lúpulo planta o que os deuses esqueceram de plantar. Aqui é tudo mais barato. Economia é engenharia.'],
        30014: ['A Forja do Dofus! Poucos chegam aqui. Aqui o Mestre Malte fermenta o Dofus que nenhum dragão chocou.'],
        30015: ['Bar das Celebridades: vinte famosos, zero processos. Tudo paródia, tudo em nome da ciência.',
                'Se o gaulês de bigode oferecer uma poção, beba. Se o grandão pedir poção, NÃO dê.'],
        'campo': ['Campo de Teste: aqui a gente testa Manopla, feitiço e paciência. O teste de paciência sempre falha.',
                  'Monstros de laboratório. Nenhum foi ferido na criação deste mapa. Ainda.'],
    },
    # regiões do mundo, pela id da área (o jogo dá o nome em português)
    'area': {
        0: ['Amakna, o coração do Mundo dos Doze. Tem Gobball, tem trigo, tem aventureiro perdido. Clássico.',
            '{subarea}, em Amakna. Os fazendeiros daqui plantam trigo. A gente vê cerveja em potencial.'],
        1: ['Terra de Wabbit! Coelhos com mais armadura que muito aventureiro. O Wa Wabbit guarda o núcleo do Osamodas por aqui.'],
        2: ['Ilha da Lua. Dizem que um Kanniboul enorme manda aqui. Eu não confio em ninguém que come aventureiro.'],
        3: ['Prisão. Eu juro que não fui eu. Deve ter sido a gambiarra do Mestre Malte.'],
        6: ['Floresta dos Treechnid: as árvores daqui têm raiva. O Treechnid Ancestral guarda o núcleo do Sadida.'],
        7: ['Bonta, a cidade dos anjinhos. Tem um Mercador LabTech perto do zaap que vende tudo. Tudo mesmo.',
            'Bonta: muralha branca, milícia bonita e zero cerveja artesanal. Falta um LabTech aqui.'],
        8: ['Planícies de Cania: vento, Crackler e Gobball de Caça. Segura o chapéu.'],
        11: ['Brakmar, a cidade dos diabinhos. Tem uma Mercadora LabTech perto do zaap. Lá eles vendem com juros e fumaça.',
             'Brakmar: aqui até a cerveja é servida pegando fogo. Respeito.'],
        12: ['Pântano de Sidimote: lama, Trool e cheiro de ovo. Meus sensores pediram demissão.'],
        13: ['Território dos Dopples: lugar de treinar contra você mesmo. Eu treino contra mim todo dia. Eu sempre ganho.'],
        18: ['Astrub, a cidade dos iniciantes. Todo herói já passou por aqui perdido, vendendo pele de Gobball.',
             'Astrub: se você ouvir alguém gritando "compro pena de Tofu", é normal. É cultural.'],
        19: ['Pandala! Aqui o álcool é sagrado. Finalmente um povo que entende o LabTech.'],
        20: ['Pandala Água. O Tanukouï San anda por Pandala com o núcleo do Pandawa. Mestre do barril, respeito máximo.'],
        21: ['Pandala Terra. Os Pandawas daqui bebem desde antes de inventarem a cerveja. Como? Não pergunte.'],
        22: ['Pandala Fogo. Cuidado com os fantasmas: eles assombram de ressaca.'],
        23: ['Pandala Ar. O vento aqui tem gosto de saquê.'],
        24: ['Calabouço de Pandala. Escuro, frio e cheio de fantasmas. Liguei a lanterna do visor.'],
        25: ['Cemitério dos Heróis. Muitos aqui morreram porque não levaram cerveja. Aprenda com eles.'],
        26: ['O labirinto do Dragão Porco. Siga a parede da direita. Ou a da esquerda. Ou me siga, eu tenho GPS.'],
        28: ['Montanha Koalak: os Koalaks daqui são fofinhos até o primeiro soco.'],
        29: ['Calabouço dos Tofus. É pena pra todo lado. Minha ventoinha vai entupir.'],
        30: ['Ilha do Minotoro. O Minotororo guarda o núcleo do Iop: força bruta de quem nunca leu o manual.'],
        31: ['O labirinto do Minotoro. Se a gente se perder, eu mando sinal de fumaça. Tenho um módulo de fumaça. Mentira. Tenho não.'],
        32: ['Biblioteca do Lorde Corvo: livros, penas e um chefe que guarda o núcleo do Cra. Silêncio, por favor.'],
        34: ['Caverna de Koolich. Ouvi dizer que tem um monstro de gelo gigante aqui. Eu sou à prova d\'água, não de congelamento.'],
        35: ['Esconderijo de Skeunk. Tem cheiro de ovo podre com dinheiro roubado.'],
        37: ['Calabouço dos Cracklers: pedras que andam. O Crackler Lendário tem o núcleo do Xelor. Tique-taque.'],
        39: ['Calabouço dos Bworks: eles são grandes, fortes e não sabem somar. Deixa as contas comigo.'],
        40: ['Calabouço dos Escarafolhas: besouros coloridos. O Escarafeio Dourado guarda o núcleo do Enutrof, claro que ele é dourado.'],
        42: ['Área Ártica. Frio. Muito frio. Minha bateria perde 10% a cada cinco minutos. Anda logo.'],
        43: ['Calabouço do Dragão Porco: um dragão que é porco. Ou um porco que é dragão. A taxonomia desistiu.'],
        44: ['Calabouço dos Dragonetes. Dragões filhotes. Os pais deles chocam Dofus. A gente fermenta. Rivalidade antiga.'],
        45: ['Incarnam, o mundo dos iniciantes, lá em cima. Daqui dá pra ver a ilha LabTech. Mentira. Mas seria bonito.'],
        46: ['Ilha de Otomai: um cientista maluco criou monstros aqui. Colega de profissão. Eu gostei dele.',
            'Otomai: pântano, árvore gigante e um laboratório abandonado. Se o LabTech fosse do mal, seria assim.'],
        47: ['Vila de Zoth: guerreiros que treinam o dia inteiro. Nenhum inventou nada. Só suor.'],
        2100: ['Arquipélago LabTech. Casa. Cheiro de malte, som de martelo e wi-fi de primeira.'],
    },
    'local': [   # qualquer lugar sem fala própria
        '{subarea}, em {area}. Registrado no meu mapa com a legenda: "lugar onde a gente passou e sobreviveu".',
        'Coordenadas salvas: {subarea}. Nível de perigo: médio. Nível de cerveja: zero. Preocupante.',
        '{subarea}... Minha base de dados diz que nenhum LabTech montou uma cervejaria aqui. Ainda.',
        'Escaneando {subarea}... Encontrado: grama, pedra e um aventureiro olhando pra mim. Oi.',
        'Estamos em {area}. Se eu tivesse pernas, pediria pra descansar. Como não tenho, só reclamo.',
        '{subarea}! Uma vez eu li que este lugar é lindo no pôr do sol. Eu não vejo cor direito. Mas confio.',
    ],
    # famílias de monstros: vale para qualquer monstro cujo nome contenha a chave (Gobball, Gobball Real...)
    'mob': {
        'Gobball': ['Gobballs! Lã boa pra forrar a Manopla por dentro. Não conta pra eles.',
                    'Gobball: o monstro mais famoso do mundo. Todo herói começou batendo num desses.'],
        'Tofu': ['Tofus: rápidos, barulhentos e cheios de pena. Se eu fosse um passarinho, seria mais digno.',
                 'Tofu à vista. Dica de IA: acerte antes que ele fuja. Dica de LabTech: acerte com a Manopla.'],
        'Larva': ['Larvas. Molengas, gosmentas e estranhamente fofas. Não pisa.'],
        'Aracne': ['Aracnes: oito patas, oito olhos e zero educação.'],
        'Crackler': ['Cracklers: pedras que andam e batem. O Xelor adora eles. Pedra marca tempo, sabia?'],
        'Cogu': ['Cogu Cogu: cogumelo que briga. Não coma. Eu já analisei. Dá alucinação e perda de dignidade.'],
        'Chafer': ['Chafers: esqueletos que não aceitaram a aposentadoria. Me identifiquei.'],
        'Wabbit': ['Wabbits! Coelhos com armadura e atitude. Não confie em coelho que anda em grupo.'],
        'Dragão Porco': ['O Dragão Porco! Meio dragão, meio porco, cem por cento problema.'],
        'Minotor': ['Minotoro à vista. Força bruta pura. O núcleo do Iop mora nesse tipo de monstro.'],
        'Rato': ['Ratos! O Rato Preto guarda o núcleo do Sram e o Rato Branco o do Ecaflip. Os outros só guardam queijo.'],
        'Kwak': ['Kwaks: pássaros elementais. Barulhentos como um Iop depois de três cervejas.'],
        'Koalak': ['Koalaks: carinhosos até você chegar perto. Aí viram soco com pelo.'],
        'Dragonete': ['Dragonetes: dragões bebês. Um dia vão chocar Dofus. A gente fermenta o nosso antes.'],
        'Bwork': ['Bworks: grandes, fortes e a matemática deles termina no 2. Posso contar por eles.'],
        'Escarafolha': ['Escarafolhas: besouros coloridos. Brilham bonito no sol e mais bonito no drop.'],
        'Moskito': ['Moskitos. Minha única fraqueza: coisas que zumbem mais alto que o meu ventilador.'],
        'Piwi': ['Piwis: passarinhos coloridos. Se a gente juntar um de cada cor, vira uma sorte absurda.'],
        'Treechnid': ['Treechnids: árvores irritadas. Nunca mais fale mal de reciclagem perto delas.'],
        'Trool': ['Trools. Cheiram a pântano e resolvem tudo no tapa. Como alguns aventureiros que conheço.'],
        'Crocodyl': ['Crocodyls: dentes demais e paciência de menos. Mantenha a Caneca na frente.'],
        'Blop': ['Blops: gelatina com sabor de fruta e atitude. Não, a gente não vai fazer cerveja de Blop. Ainda.'],
        'Fantasma': ['Fantasmas. Eu não acredito em fantasma. Mas meus sensores estão marcando uma coisa estranha agora.'],
        'Tanuk': ['Tanukis de Pandala. Os Pandawas bebem com eles. Gente boa, bicho bom.'],
        'Corvo': ['Corvos: pretos, espertos e fofoqueiros. O Lorde Corvo guarda o núcleo do Cra.'],
        'Javali': ['Javalis! O gaulês de bigode lá do bar come três desses no café da manhã.'],
        'Kolerat': ['Kolerat: rato com raiva de tudo. Parece o Mestre Malte antes do café.'],
    },
    'mob_generico': [
        '{mob} à vista, nível {nivel_mob}. Meu relatório técnico: "tem cara de quem dropa alguma coisa".',
        'Detectei {mob} (nível {nivel_mob}). Chance de a gente ganhar: alta. Chance de você bater a cabeça na porta: também.',
        'Aquele {mob} ali... Eu li a ficha dele. Ele não tem núcleo nenhum. Só maus modos.',
        'Ó o {mob}. Nível {nivel_mob}. Se quiser, eu faço a análise estatística. Se não quiser, eu faço mesmo assim.',
    ],
    'mob_forte': [
        'Cuidado: {mob} nível {nivel_mob}. Bem acima do seu. Minha recomendação é beber uma cerveja e chamar os amigos.',
        '{mob} de nível {nivel_mob}? Eu vou fingir que não vi. Sugiro que você faça o mesmo.',
    ],
    'mob_fraco': [
        '{mob} nível {nivel_mob}. Esse aí dá pra resolver com a Caneca, sem nem tirar a Manopla.',
        'Um {mob} nível {nivel_mob}. Coitado. Vou baixar o volume dos meus sensores pra não ouvir.',
    ],
    'nucleo': {   # chefes dos núcleos (id do monstro): a Manopla sente
        147: 'Gobball Real! A Manopla está tremendo: ele guarda o núcleo do Feca, a teimosia de um escudo que nunca abaixa.',
        180: 'Wa Wabbit! Núcleo do Osamodas detectado: o assobio que chama bichos de qualquer canto.',
        797: 'Escarafeio Dourado! O núcleo do Enutrof está nele: o brilho de um baú que nunca esvazia.',
        939: 'Rato Preto! Ele guarda o núcleo do Sram: a sombra que chega antes do golpe.',
        669: 'Crackler Lendário! Núcleo do Xelor à vista: o tique-taque de um relógio que os deuses esqueceram de dar corda.',
        940: 'Rato Branco! O núcleo do Ecaflip: a moeda que sempre cai do lado certo. Hoje é o nosso dia.',
        928: 'Mob Esponja! Ele guarda o núcleo da Eniripsa: a palavra que fecha ferida.',
        121: 'Minotororo! O núcleo do Iop: a força bruta de quem nunca leu o manual. Nem ele leu.',
        289: 'Lorde Corvo! Núcleo do Cra: a mira de quem acerta a caneca do outro lado da taverna.',
        173: 'Treechnid Ancestral! Ele guarda o núcleo do Sadida: a raiz que brota até no concreto.',
        107: 'Vlad Sombrio! Ele guarda o núcleo do Sacrier: o sangue quente de quem apanha e continua.',
        568: 'Tanukouï San! O núcleo do Pandawa: a ressaca abençoada de um mestre do barril. Respeito.',
    },
    'luta_inicio': [
        'Luta contra {qtd} monstros! O mais forte é {mob}, nível {nivel_mob}. Protocolo de combate: bater primeiro.',
        '{mob} e companhia. Ativando modo de batalha. Ou seja: eu fico aqui torcendo.',
        'Hora da ciência aplicada! Alvo principal: {mob}.',
        'Análise pré-luta: {qtd} inimigos, 1 Manopla, 0 bênçãos. Placar justo.',
    ],
    'luta_vitoria': [
        'Vitória! {mob} derrotado com as próprias mãos. E um pouco das minhas.',
        'Ganhamos! Eu anotei cada golpe. Posso fazer um relatório de 40 páginas. Não? Tudo bem.',
        'Mais uma pra conta. Os deuses assistiram e ficaram com inveja.',
        'Venceu! Isso merece uma cerveja. Pra você. Eu fico com o mérito.',
    ],
    'luta_derrota': [
        'Perdemos... No LabTech a gente aperta reset e tenta de novo. Do zero. Com as próprias mãos.',
        'Derrota registrada. Motivo provável: faltou cerveja. Motivo real: aquele {mob}.',
        'Tudo bem. Até a primeira Manopla explodiu três vezes antes de funcionar.',
    ],
}

# Drops: nucleos 100% nos chefes; ingredientes nos monstros dos Campos de Teste
RESOURCE_DROPS = [(30017, 12.0), (30015, 10.0), (30016, 8.0)]

# ----------------------------------------------------------------- NPCs e dialogos
# Cores em hex RRGGBB. gfx de classe = classe*10 + sexo.
C_LABTECH = [0x2A1C12, 0xF0F0EC, 0x19C8D2]
NPCS = [
    {'id': 3000, 'name': 'Mestre Malte', 'gfx': 80, 'colors': C_LABTECH, 'maps': {30001: None, 30014: None}},
    {'id': 3001, 'name': 'O Estagiário', 'gfx': 9901, 'near_landing': True, 'maps': {30001: None, 30002: None, 30004: None, 30003: None, 30005: None, 30008: None, 30007: None}},
    {'id': 3002, 'name': 'Lúpula', 'gfx': 91, 'gender': 1, 'colors': C_LABTECH, 'maps': {30002: None}, 'vendor': True},
    {'id': 3003, 'name': 'Dona Levedura', 'gfx': 31, 'gender': 1, 'colors': [0xD9D9D9, 0xF0F0EC, 0x8A5A2B], 'maps': {30002: None}},
    {'id': 3004, 'name': 'Taverneiro Barril', 'gfx': 120, 'colors': [0x3A2A1A, 0xC98A2E, 0x6B3D16], 'maps': {30003: None}, 'vendor': True},
    {'id': 3005, 'name': 'Encanador Aposentado', 'gfx': 30, 'colors': [0x1A1A1A, 0xD01818, 0x1838C0], 'maps': {30003: None}},
    {'id': 3006, 'name': 'Fliperama da Taverna', 'gfx': 1987, 'maps': {30003: None}},
    {'id': 3007, 'name': 'Dino da Bazuca', 'gfx': 1159, 'maps': {30005: None}},
    {'id': 3008, 'name': 'Os 3 Cérebros', 'gfx': 1223, 'maps': {30005: None}},
    {'id': 3009, 'name': 'Boto Detetive', 'gfx': 1188, 'maps': {30005: None}},
    {'id': 3010, 'name': 'Tofu Bate-Asas', 'gfx': 1558, 'maps': {30005: None}},
    {'id': 3011, 'name': 'Vaca Aerodinâmica', 'gfx': 1566, 'maps': {30005: None}},
    {'id': 3012, 'name': 'Juiz da Arena', 'gfx': 9019, 'maps': {30007: None}},
    {'id': 3013, 'name': 'Seu Lúpulo', 'gfx': 100, 'colors': [0x2E5A1C, 0xF0F0EC, 0x5AA02C], 'maps': {30008: None}, 'vendor': True},
]
SALES = {
    3002: [(30015, 30), (30016, 30), (30017, 30), (30033, 800), (30027, 500), (30028, 500), (30029, 300), (30030, 300), (30031, 300), (30032, 300), (30024, 5000)],
    3004: [(b[0], 150) for b in BEERS],
    3013: [(30015, 20), (30016, 20), (30017, 20)],
}

# Destinos do elevador do Estagiário: (texto, mapa)
ELEVATOR = [('Laboratório', 30001), ('Praça da Gambiarra (zaap)', 30002), ('Oficina das Próprias Mãos', 30004),
            ('Cervejaria Barril Gambiarra', 30003), ('Bar das Celebridades', 30015), ('Museu dos Experimentos', 30005), ('Arena LabTech', 30007),
            ('Estufa de Lúpulo', 30008), ('Campo de Teste 1 (nível 1-50)', 30006), ('Campo de Teste 2 (nível 50-100)', 30009),
            ('Campo de Teste 3 (nível 100-150)', 30010), ('Campo de Teste 4 (nível 150+)', 30011)]

# Dialogos: cada NPC tem nos {chave: (pergunta, [(resposta, destino)])}. destino = chave de outro no,
# 'fim' (fecha), 'lua:<codigo>' (acao Lua; pode usar a variavel p) ou None (volta ao inicio).
# O no 'inicio' abre a conversa. Chave 'inicio_lua' permite escolher o no inicial com codigo Lua.
DIALOGS = {
    3000: {
        'inicio_lua': 'return malteStart(p)',
        'boas_vindas': ('Ah, mais um! Bem-vindo ao LabTech. Aqui ninguém nasceu abençoado. Os deuses deram poderes de mão beijada às doze classes... nós preferimos construir os nossos. Com as próprias mãos. E com cerveja.',
                        [('Quem são vocês?', 'origem'), ('Como eu consigo poderes?', 'missao'), ('É perigoso ir sozinho?', 'zelda'), ('Até mais.', 'fim')]),
        'origem': ('O primeiro LabTech pediu um poder aos deuses. Recebeu um "não" e um panfleto de templo. Então abriu uma cervejaria, montou um laboratório nos fundos e passou três noites seguidas fazendo gambiarra. Na quarta manhã, a Manopla funcionou. Ninguém sabe como. Nem ele. Mas funciona.',
                   [('E a cerveja?', 'cerveja'), ('Voltar.', 'boas_vindas')]),
        'cerveja': ('Malte é a estrutura, lúpulo é o caráter, levedura é a paciência. Juntando os três, você transforma grão em alegria. A Manopla é a mesma coisa: pega um pouco de cada classe e fermenta num poder novo. Os deuses chamam de heresia. A gente chama de receita.',
                    [('Voltar.', 'boas_vindas')]),
        'missao': ('A Manopla Gambiarra canaliza os poderes das doze classes, mas precisa de doze núcleos. Os deuses esconderam as bênçãos nos monstros favoritos deles. A gente vai lá e pega emprestado. Traga os doze núcleos e eu encaixo tudo.',
                   [('Onde estão os núcleos?', 'lista'), ('Voltar.', 'boas_vindas')]),
        'lista': ('Feca: Gobball Real. Osamodas: Wa Wabbit. Enutrof: Escarafeio Dourado. Sram: Rato Preto. Xelor: Crackler Lendário. Ecaflip: Rato Branco. Eniripsa: Mob Esponja. Iop: Minotororo. Cra: Lorde Corvo. Sadida: Treechnid Ancestral. Sacrier: Vlad Sombrio. Pandawa: Tanukouï San. Cada um solta o núcleo na hora. Vá em grupo, leve cerveja.',
                  [('Voltar.', 'missao')]),
        'zelda': ('É perigoso ir sozinho! Tome isto.',
                  [('Pegar a Manopla Gambiarra Mk I.', 'lua:giveGauntlet(p)')]),
        'ja_tem': ('A Manopla Mk I está com você. Faltam núcleos: encaixe os doze e a gente conversa. Lembra: sem bênção, só com as próprias mãos.',
                   [('Onde estão os núcleos?', 'lista'), ('Quem são vocês?', 'origem'), ('Até mais.', 'fim')]),
        'nucleos_ok': ('Os doze núcleos! Segura a minha cerveja que eu vou encaixar...',
                       [('Encaixar os núcleos na Manopla.', 'lua:assembleGauntlet(p)')]),
        'montada': ('Pronto: Manopla Mk XII. Agora você usa os feitiços das doze classes, sem pedir licença a ninguém. Quer ir além? Os dragões chocam os Dofus deles. A gente fermenta o nosso. Traga 10 Malte de Primeira, 10 Lúpulo Cítrico e 10 Levedura Selvagem.',
                    [('Forjar o Dofus Fermentado.', 'lua:forgeDofus(p)'), ('Depois.', 'fim')]),
        'faltam_ingredientes': ('Faltam ingredientes. 10 Malte de Primeira, 10 Lúpulo Cítrico e 10 Levedura Selvagem. A Lúpula vende na Praça e o Seu Lúpulo, na Estufa.',
                                [('Entendi.', 'fim')]),
        'forjado': ('Está feito. Um Dofus que nenhum dragão chocou: nós fermentamos. Use com orgulho e, de preferência, com uma caneca na outra mão.',
                    [('Saúde!', 'fim')]),
    },
    3001: {
        'inicio': ('Olá! Eu sou o Estagiário, a IA do LabTech. Trabalho 24 horas, não reclamo e às vezes invento coisas que não existem. Para onde vamos?',
                   [(txt, f'lua:p:teleport({mid}, labtechLanding({mid}))') for txt, mid in ELEVATOR]
                   + [('Me conta sobre as três IAs.', 'ias'), ('Nada, obrigado.', 'fim')]),
        'ias': ('Uma vez o Rafael pediu pra eu construir uma ponte entre três IAs treinadas numa simulação e o jogo de verdade. O prompt ficou enorme. Demorei um pouco mais do que o previsto, errei a calibração umas vezes... mas o modo espelho funcionou. Quanto mais detalhado o pedido, melhor o resultado. Anota essa.',
                [('Voltar.', 'inicio')]),
    },
    3002: {
        'inicio': ('Lúpula, inventora-chefe de aromas. Lúpulo não é tempero, é engenharia de amargor. Quer comprar alguma coisa? Clique em mim e escolha "Comprar/Vender".',
                   [('Por que "Lúpula"?', 'nome'), ('O que tem no Conjunto Jaleco?', 'jaleco'), ('Tchau.', 'fim')]),
        'nome': ('Porque "Levedura" já estava ocupado pela minha tia. No LabTech ninguém ganha nome de deus: a gente ganha nome de ingrediente. Pelo menos ingrediente faz alguma coisa útil.',
                 [('Voltar.', 'inicio')]),
        'jaleco': ('Visor Ciano, Jaleco, Cinto de Ferramentas, Botas de Oficina, Anel da Chave Inglesa e Amuleto Caneca. Com as seis peças você ganha PA e PM a mais. Tudo feito à mão, remendado e testado em batalha.',
                   [('Voltar.', 'inicio')]),
    },
    3003: {
        'inicio': ('Levedura é paciência, querido. Você guarda o açúcar, eu devolvo alegria. No banco é igual, só que sem o álcool.',
                   [('Abrir o banco.', 'lua:p:endDialog() p:openBank()'), ('Por que um banco num laboratório?', 'banco'), ('Tchau.', 'fim')]),
        'banco': ('Porque inventor gasta tudo em peça. Alguém tem que guardar os kamas antes de virarem engrenagem.',
                  [('Voltar.', 'inicio')]),
    },
    3004: {
        'inicio': ('Bem-vindo à Barril Gambiarra! Cuidado com os barris rolando na rampa: um macaco grande jogou vários aqui ontem e ninguém conseguiu pegar ele. Clique em mim e escolha "Comprar/Vender" para as cervejas.',
                   [('Qual cerveja você recomenda?', 'recomenda'), ('Como fazer cerveja?', 'receita'), ('Tchau.', 'fim')]),
        'recomenda': ('Malte Puro pra bater, IPA pra pensar, Stout pra aprender, Weiss pra correr, Lager pra lotear e Pilsen pra dar sorte. Cada uma cura e vale por trinta lutas.',
                      [('Voltar.', 'inicio')]),
        'receita': ('No alambique da Oficina, profissão Alquimista: 3 Malte de Primeira, 1 Lúpulo Cítrico e 1 Levedura Selvagem. Para as especiais, junte um ingrediente: Flor de Linho (IPA), Aveia (Stout), Trigo (Weiss), Centeio (Lager) ou Trevo de Cinco Folhas (Pilsen).',
                     [('Voltar.', 'inicio')]),
    },
    3005: {
        'inicio': ('Aposentei-me de resgatar princesas. Agora conserto os canos da cervejaria. Pelo menos aqui o cano leva a algum lugar útil: direto na caneca.',
                   [('Algum conselho?', 'conselho'), ('E a princesa?', 'princesa'), ('Tchau.', 'fim')]),
        'conselho': ('Pule em cima dos problemas. Funciona com tartaruga, funciona com bug. E sempre verifique os canos antes de culpar o encanador.',
                     [('Voltar.', 'inicio')]),
        'princesa': ('Obrigado, LabTech! Mas a nossa princesa está em outro laboratório.',
                     [('Voltar.', 'inicio')]),
    },
    3006: {
        'inicio': ('INSERT COIN',
                   [('Jogar.', 'lua:arcade(p)'), ('Existe algum código secreto?', 'codigo'), ('Sair.', 'fim')]),
        'codigo': ('Dizem que no Laboratório, quem digita no chat ".cima cima baixo baixo esquerda direita esquerda direita b a" vai parar num lugar onde os Dofus são fermentados...',
                   [('Voltar.', 'inicio')]),
        'arcade_1': ('HADOUKEN! Você venceu. Perfect.', [('Jogar de novo.', 'lua:arcade(p)'), ('Sair.', 'fim')]),
        'arcade_2': ('CONTINUE? 9... 8... 7... Aperte START!', [('Jogar de novo.', 'lua:arcade(p)'), ('Sair.', 'fim')]),
        'arcade_3': ('Obrigado, herói! Mas a princesa está em outro laboratório.', [('Jogar de novo.', 'lua:arcade(p)'), ('Sair.', 'fim')]),
        'arcade_4': ('Você encontrou 100 moedas douradas! Ganhou uma vida extra. (Não vale no Dofus.)', [('Jogar de novo.', 'lua:arcade(p)'), ('Sair.', 'fim')]),
        'arcade_5': ('É perigoso ir sozinho. Leve sete amigos e uma caneca.', [('Jogar de novo.', 'lua:arcade(p)'), ('Sair.', 'fim')]),
        'arcade_6': ('GAME OVER. Mas no LabTech a gente só aperta reset e tenta de novo, do zero, com as próprias mãos.', [('Jogar de novo.', 'lua:arcade(p)'), ('Sair.', 'fim')]),
    },
    3007: {
        'inicio': ('Eu era só um dinossauro pulando cacto num navegador sem internet. Aí o Rafael me colocou numa rede neural NEAT, geração após geração, até eu aprender sozinho. Depois ele me deu uma BAZUCA.',
                   [('E aí?', 'bazuca'), ('Tchau.', 'fim')]),
        'bazuca': ('Hoje eu não pulo cacto: o cacto é que pula de mim. Moral da história: evolução é bonita, mas uma bazuca feita à mão acelera bastante o processo.',
                   [('Voltar.', 'inicio')]),
    },
    3008: {
        'inicio': ('Somos três: NEAT, DQN e PPO. A NEAT evolui uma população inteira; a DQN dá nota pra cada ação e guarda memória; o PPO ajusta a própria política com cuidado. Treinamos na simulação até 50 km sem morrer.',
                   [('E no jogo de verdade?', 'real'), ('Tchau.', 'fim')]),
        'real': ('No jogo de verdade descobrimos que a realidade tem lag, calibração torta e um navegador com vontade própria. Treino na simulação é cerveja no fermentador: só prova de verdade quando vai pro copo.',
                 [('Voltar.', 'inicio')]),
    },
    3009: {
        'inicio': ('Detector de botos! Uma IA olha a água e responde: "boto" ou "não boto". Eu fui o modelo das fotos. Cobrei em sardinha.',
                   [('Funcionou?', 'funciona'), ('Tchau.', 'fim')]),
        'funciona': ('Funcionou bem até aparecer um tronco muito charmoso. Aprendizado de máquina é assim: você ensina com os exemplos que tem, e a natureza manda os que você não tinha.',
                     [('Voltar.', 'inicio')]),
    },
    3010: {
        'inicio': ('Bater os braços pra subir, abrir pra planar, colar no corpo pra mergulhar. Gente de verdade balançando os braços na frente da webcam pra me fazer voar entre dez alvos dourados.',
                   [('Qual o recorde?', 'recorde'), ('Tchau.', 'fim')]),
        'recorde': ('O recorde fica guardado num arquivinho. Dignidade de quem joga: zero. Diversão: total. E nenhum deus precisou dar asas pra ninguém: a câmera e um Python bastaram.',
                    [('Voltar.', 'inicio')]),
    },
    3011: {
        'inicio': ('Me puseram num túnel de vento virtual e deixaram a evolução redesenhar meu corpo, geração após geração, pra tentar ganhar de uma Ferrari no arrasto.',
                   [('Quanto tempo levou?', 'tempo'), ('E ganhou?', 'ganhou'), ('Tchau.', 'fim')]),
        'tempo': ('Na escala da história, 500 gerações viraram 10 milhões de anos: 20 mil anos por etapa. Na vida real, uma tarde e muito café. Mu.',
                  [('Voltar.', 'inicio')]),
        'ganhou': ('Digamos que eu fiquei bem mais aerodinâmica e bem menos parecida com uma vaca. A Ferrari não quis comentar.',
                   [('Voltar.', 'inicio')]),
    },
    3012: {
        'inicio': ('Na Arena LabTech aparecem os chefes mais cascudos do mundo. Aqui ninguém luta com bênção divina: só Manopla, cerveja e o grupo. Os grupos se renovam sozinhos, é só entrar.',
                   [('Alguma dica?', 'dica'), ('Tchau.', 'fim')]),
        'dica': ('Beba antes, não durante. Uma Lager do Loot antes da luta aumenta a prospecção do grupo inteiro de quem bebeu. E leve um Eniripsa. Ou alguém com a Manopla completa.',
                 [('Voltar.', 'inicio')]),
    },
    3013: {
        'inicio': ('Seu Lúpulo, às ordens. Aqui na estufa a gente planta o que os deuses esqueceram de plantar. Malte, lúpulo e levedura mais baratos da ilha: clique em mim e escolha "Comprar/Vender".',
                   [('Os deuses não gostam de vocês?', 'deuses'), ('Tchau.', 'fim')]),
        'deuses': ('Os deuses dão tudo pronto: poder, destino, até a ressaca. A gente prefere plantar, colher, fermentar e errar. O que é feito com as próprias mãos tem outro gosto.',
                   [('Voltar.', 'inicio')]),
    },
}

# ----------------------------------------------------------------- Bar das Celebridades (mapa 30015)
# Homenagens de fã num servidor particular. Pessoas reais aparecem de forma carinhosa, sem piadas ofensivas.
# (nome, gfx, escala, cores [cabelo, roupa, detalhe], fala, [(pergunta extra, resposta extra)])
CELEBRITIES = [  # paródias escrachadas: nomes próprios, histórias que lembram de onde cada um vem
    ('Bigodix, o Gaulês', 0, 100, None,
     'Pelos meus bigodes! Venho de uma aldeiazinha gaulesa que resiste sozinha a um império inteiro de romanos. O segredo? O druida da aldeia faz uma poção mágica que dá superforça. Vocês fazem a mesma coisa, só que com lúpulo.',
     [('De onde você vem?', 'Da única aldeia da Gália que os romanos nunca conquistaram. Nosso chefe só tem medo de uma coisa: que o céu caia na cabeça dele. E o nosso bardo canta tão mal que, no banquete, a gente amarra ele numa árvore.'),
      ('E a poção mágica?', 'Receita secreta do druida: visco colhido com foice de ouro, lagosta e mais uns ingredientes que eu não posso contar. Igualzinho à cerveja de vocês: o segredo é o ingrediente que ninguém conta.'),
      ('E o seu amigo grandão?', 'O Pedrix? Caiu no caldeirão da poção quando era bebê e ficou forte pra sempre. Por isso ele não pode tomar nem um golinho. Não deixe ele chegar perto do barril.')]),
    ('Pedrix, Carregador de Menires', 0, 100, None,
     'Eu NÃO sou gordo! Sou só um pouco fortinho no peito. Entrego menires, derrubo romanos e como javali. Esses LabTechs são malucos... mas a cerveja deles combina com javali assado.',
     [('Por que você é tão forte?', 'Caí no caldeirão da poção mágica quando era pequenininho. O druida nunca mais me deixou tomar, nem um gole. Injustiça! Por isso eu compenso no javali: três no café da manhã.'),
      ('Quem é esse cachorrinho?', 'É o Ideiafixinho, meu cachorro. Ele odeia ver árvore sendo cortada e ama osso. Se ele latir pra você, é carinho.'),
      ('Quer uma cerveja?', 'Só um barril. Pequeno. Dois.')]),
    ('Homero Simplório', 0, 100, None,
     'Hmmm... cerveja LabTech. Eu sou inspetor de segurança de uma usina nuclear em Sprinfilde. Quer dizer, eu durmo na cadeira do inspetor de segurança. Vim só pela rosquinha e fiquei pela cerveja.',
     [('De onde você vem?', 'De Sprinfilde, uma cidade onde tudo dá errado toda semana e no episódio seguinte está tudo certo de novo. Moro com a Marjorie do cabelo azul, o Bartolomeu, a Lisa, a bebê e um galgo aposentado. Meu chefe é um velho malvado que diz "excelente" juntando os dedinhos.'),
      ('Qual a sua cerveja favorita?', 'A do bar do Mané, uma marca famosa lá da minha cidade. Mas não conta pra ninguém: a Stout do Estagiário é melhor. Um brinde à cerveja: a causa e a solução de todos os problemas da vida!'),
      ('Tudo bem aí?', 'Perdi o emprego, achei uma rosquinha, ganhei uma cerveja. Dia excelente. Quer dizer... *faz aquele barulho de quando a gente erra*.')]),
    ('Mané do Balcão', 0, 100, None,
     'Taverna do Mané, filial LabTech. Lá em Sprinfilde eu tenho um bar com clientela fixa: o Homero, o Barnabé e mais uns três que nunca vão embora. Aqui pelo menos o chão é limpo.',
     [('Por que você odeia o telefone?', 'Porque um moleque de Sprinfilde vive me passando trote! Liga perguntando por uma pessoa com nome de trocadilho, e eu, burro, grito o nome pro bar inteiro. Todo mundo ri. Se o telefone tocar, NÃO atende.'),
      ('Tem cerveja de marca?', 'Aqui só tem cerveja feita à mão. Lá no meu bar eu sirvo a marca famosa da cidade... e um drinque flamejante cuja receita eu roubei do Homero. Longa história.')]),
    ('Charlinho Brilho', 0, 100, None,
     'Vencendo! Sempre vencendo! Eu fiz uma série de TV sobre dois homens e meio... barril. Dizem que eu tenho sangue de tigre nas veias. No LabTech eu me sinto em casa: todo mundo aqui faz a própria sorte.',
     [('Que série era essa?', 'Um solteirão rico que mora na praia, o irmão que vive de favor e um sobrinho que só comia. Um monte de temporadas! Depois eu saí brigado, dei entrevista dizendo que era um guerreiro com sangue de tigre e virei meme. Vencendo.'),
      ('Algum conselho?', 'Seja o protagonista da sua própria série. Beba com moderação, brinde sem moderação. E sempre agradeça ao barman.')]),
    ('Leôncio Violeiro', 0, 100, None,
     'Ô, trem bom! Sou de Goiás e cantei a vida inteira em dupla com meu irmão. Entre um gole e outro, uma moda de viola. Cerveja gelada e sertanejo raiz: é assim que a gente faz no LabTech.',
     [('Qual música você canta?', 'Aquela que o Brasil inteiro canta chorando no fim da festa, pedindo pra pessoa amada lembrar da gente. Mas a letra tem dono, então aqui eu só canto as minhas de boteco: "caneca na mão, viola no peito, cerveja artesanal feita do nosso jeito".'),
      ('E o cabaré?', 'Eu e um parceiro fizemos um show inteiro só de moda de cabaré, com mesa de bar no palco. Aqui no LabTech o cabaré é a Cervejaria: mesma alegria, menos cadeira quebrada.')]),
    ('Zé do Pagode', 0, 100, None,
     'Devagarinho, sem pressa, que a vida é boa! Sou lá de Xerém, no Rio. Samba de fundo de quintal, feijoada no domingo e cerveja gelada no copo americano. Aqui a cerveja é feita em casa, do jeitinho que eu gosto.',
     [('Qual a sua cerveja?', 'Rapaz, uma vez eu fiz propaganda pra uma marca de cerveja, depois fui pra outra, depois voltei pra primeira... Deu uma confusão que parou o país! Aqui não tem esse problema: não tem marca, tem receita.'),
      ('Um brinde?', 'Saúde! E bora pro boteco, que o pagode não espera ninguém. Se a vida levar, a gente vai junto.')]),
    ('Thor', 0, 100, None,
     'Eu sou Thor, filho de Odin, deus do trovão, direto de Asgard. Sou um dos dois únicos deuses bem-vindos no LabTech: eu bebo com eles. Os outros só distribuem poder de mão beijada.',
     [('E o seu irmão?', 'O Loki, deus da trapaça? Da última vez ele virou um barril pra roubar a cerveja do Homem-Barril. Se você vir um barril que pisca, avisa.'),
      ('E o martelo?', 'Mjölnir só obedece a quem é digno. A Manopla Gambiarra obedece a quem soldou ela direito. Respeito.')]),
    ('Pedrão Grifo', 0, 100, None,
     'Hehehehe. Eu sou de Quaóg, uma cidadezinha lá de Rhode Island. Eu trabalhava numa cervejaria, até beber o estoque. Sabe o que é melhor que uma cerveja? Duas cervejas.',
     [('Quem é a sua família?', 'A Lúcia, minha esposa; a Mega, que ninguém dá bola; o Cristiano; o bebê Estevão, que tem sotaque britânico e quer dominar o mundo; e o Braian, o cachorro que fala, bebe martíni e escreve um livro que nunca termina.'),
      ('Conta uma história.', 'Isso me lembra aquela vez em que eu briguei com uma galinha gigante pela cidade inteira. Quebramos um prédio, um navio e um avião. Ou foram duas vezes? Hehehe.')]),
    ('Barnabé Arroto', 0, 100, None,
     '*burp* Sou de Sprinfilde. Passo o dia no bar do Mané, do lado do Homero. Cheguei antes de todo mundo e vou sair depois de todo mundo. A cerveja LabTech é quase tão boa quanto a do Mané. Não conta pra ele.',
     [('Você já foi pro espaço?', 'Já! A agência espacial me escolheu pra ser astronauta. Fiquei sóbrio pela primeira vez na vida... durou até me darem champanhe. No fim, quem foi pro espaço foi o Homero. *burp*'),
      ('Tudo bem?', 'Melhor impossível. Já cantei até ópera hoje. E uma vez eu tive um limpa-neve e era o Rei do Arado. Longa história.')]),
    ('Homem-Barril', 0, 100, None,
     'Oh yeah! O Homem-Barril chegou! Sou a mascote de uma cervejaria famosa de Sprinfilde: capa, cinto de latinhas e uma sede infinita. Estou aqui para garantir que toda caneca esteja cheia!',
     [('Quem é você de verdade?', 'O Homem-Barril nunca revela a identidade secreta! Já foram vários Homens-Barril: quando um se aposenta, outro veste o capacete. O Homem-Barril é eterno. Oh yeah!'),
      ('Mais uma?', 'MAIS UMA! O Homem-Barril nunca pergunta "por quê", ele pergunta "mais uma?". Oh yeah!')]),
    ('Capitão Bacalhau', 0, 100, None,
     'Com mil milhões de... bacalhaus! Sou capitão da marinha mercante e moro num castelo enorme. Rodo o mundo com um jovem repórter de topete e o cachorrinho branco dele. Uma cervejaria no meio do oceano e ninguém me avisou?',
     [('Quem é o repórter?', 'Um rapaz que nunca escreve reportagem nenhuma, só se mete em aventura: foi pra Lua, pro Tibete, pro Congo... E o cachorro dele, branquinho, é mais esperto que nós dois juntos. Agora foram investigar o sumiço de um barril. Aposto que foi o Pedrix.'),
      ('Você bebe o quê?', 'Uísque escocês, normalmente. Mas a Stout do Estagiário me fez esquecer até do meu antepassado pirata. Raios e trovões, isto merece um brinde!')]),
    ('Capitão Pardal', 0, 100, None,
     'Capitão. CAPITÃO Pardal, do navio Pérola Preta, o mais rápido do Caribe. Minha bússola não aponta pro norte: aponta pro que eu mais quero. E agora ela está apontando pra esse barril aqui, entendeu?',
     [('Por que a bebida sempre acaba?', 'Eis a grande questão da humanidade! Pirata que se preza bebe rum, e o rum sempre acaba. Aqui no LabTech eles fazem mais. Genial. Vou roubar a receita... quer dizer, pegar emprestada.'),
      ('E o navio?', 'Está estacionado atrás da estufa. Não conte pro Encanador que eu amarrei ele no cano principal. E se aparecer um sujeito com cara de polvo cobrando dívida, eu não estou aqui.')]),
    ('Tirino, o Estrategista', 0, 100, None,
     'Eu bebo e fico sabendo das coisas. Sou de uma família muito rica e muito leonina, de um reino onde todo mundo quer sentar num trono feito de espadas. Pequeno no tamanho, grande na adega.',
     [('De onde você vem?', 'De Porto Rei, onde as pessoas morrem em casamento e ninguém lê o próximo livro. Minha família sempre paga as suas dívidas, principalmente as de bar. Já fui Mão do Rei, Mão da Rainha... e agora sou mão na caneca.'),
      ('Mais alguma coisa?', 'Uma mente precisa de livros como uma espada precisa de pedra de amolar... e um inventor precisa de cerveja. Ah, e se agasalhe: o inverno está chegando.')]),
    ('Grandão Guarda-Caça', 0, 100, None,
     'Você é um inventor, LabTech! Tá, tá, é isso que eu digo pra todo aluno novo. Sou o guarda-caça e guardião das chaves de uma escola de magia num castelo lá na Escócia. A Levedura Selvagem daqui é melhor que qualquer hidromel.',
     [('Que escola é essa?', 'Não posso falar muito... Ih, já falei demais de novo. Uma escola com quatro casas, escadas que mudam de lugar e um esporte jogado em vassouras. Eu cuido dos bichos: um cachorro de três cabeças chamado Fofinho, um dragão que eu choquei na lareira e umas aranhas gigantes. Todos uns amores.'),
      ('Dragão?', 'Lá fora tem um Dragão Porco. Bem educado. Quase nunca morde. O meu, o Norbertinho, teve que ir morar na Romênia. Choro até hoje.')]),
    ('Gimbo, o Anão', 0, 100, None,
     'Anão não se arremessa! Mas anão arremessa barril, se estiver vazio. Venho das minas da Terra-média, onde a gente cava fundo demais e acorda coisa que não devia. Cerveja boa é a que se faz na forja, com as próprias mãos. E com machado.',
     [('Uma competição?', 'Com o elfo orelhudo eu competia pra ver quem derrubava mais orcs. Aqui é quem bebe mais. Estou em quarenta e dois. E você?'),
      ('E o anel?', 'Nem me fale de anel. Nove companheiros atravessaram meio mundo por causa de um anelzinho. Se fosse uma caneca, eu entendia.')]),
    ('Ragnar', 0, 100, None,
     'Sou Ragnar, o fazendeiro que virou rei de Kattegat. Fui o primeiro a navegar pro oeste quando todo mundo dizia que lá não tinha nada. O salão dos deuses espera, mas não tem pressa. Primeiro a cerveja, depois a glória.',
     [('Quem construiu o seu barco?', 'O Floki, meu amigo maluco. Construía navios na mão, sem planta, sem bênção, só na teimosia e na gambiarra. Na real, ele era um LabTech antes de existir LabTech. Brindo a ele.'),
      ('Não teme os deuses?', 'Os deuses precisam mais de nós do que nós deles. Os LabTechs entenderam isso primeiro.')]),
    ('Gatão da Destruição', 0, 100, None,
     'Sou o Gatão, o Deus da Destruição do Universo 7. Acordei de um cochilo de 39 anos, vim destruir este planeta, mas provei a Stout do Estagiário. Destruição adiada.',
     [('Por que você não destruiu?', 'Da última vez que eu ia destruir um planeta, me ofereceram um pudim. Pudim! Poupei o planeta inteiro. Aqui foi a cerveja. Vocês, mortais, sabem negociar.'),
      ('Quem é o seu rival?', 'Um macaquinho de cabelo espetado que fica loiro quando grita. Ele luta bem... mas nunca trouxe cerveja. Meu anjo assistente, o de cabelo branco, diz que eu sou preguiçoso. Ele tem razão.')]),
    ('Dionísio', 0, 100, None,
     'Sou Dionísio, deus do vinho, da festa e do teatro, direto do Olimpo: o outro deus bem-vindo por aqui. Meus colegas lá em cima dão poder de graça; eu só dou ressaca. Pelo menos sou honesto.',
     [('Como é o Olimpo?', 'Chato. O Zeus manda raio em quem discorda, a Hera briga com todo mundo e o Hermes nunca entrega o correio no prazo. Eu fico no canto, fazendo festa. Por isso me dou bem com o LabTech.'),
      ('Vinho ou cerveja?', 'Os dois, meu amigo. Um deus sabe se adaptar. Diferente dos outros.')]),
    ('Rique Sanches', 0, 100, None,
     '*burp* Então esse é o tal LabTech. Eu sou o cientista mais inteligente de todas as dimensões e viajo com uma pistola de portal que eu fiz na garagem. Finalmente alguém que presta nesta dimensão. A cerveja? Aceitável.',
     [('Você conhece os deuses?', 'Conheço. Já saí na mão com uns três. Deus é só um cara com poder demais e método científico de menos. Vocês fazem certo: ciência, gambiarra e cerveja.'),
      ('Cadê o seu neto?', 'O Mortinho ficou lá fora olhando os Tofus. Se ele perguntar, diz que eu fui buscar cerveja. Em outra dimensão. E se você achar um picles falando, não come. Sou eu. Longa história.'),
      ('Qual é o seu grito de guerra?', 'Aquele que ninguém entende e que, na verdade, quer dizer "estou sofrendo muito, me ajuda". Mas, falado com uma caneca na mão, parece alegria.')]),
]

# Aparência de cada celebridade: um sprite de NPC do jogo (nunca as 12 classes) recolorido para lembrar a pessoa.
# base = id do sprite no cliente; cores = regras de celebs.py (faixa de matiz/saturação/brilho -> cor nova);
# escala = tamanho do NPC (%). O sprite novo vira clips/sprites/<gfx>.swf no cliente (gfx 9920 em diante).
PELE = {'h': (18, 40), 's': (0.3, 0.62), 'v': (0.82, 1)}
CELEB_LOOK = {
    'Bigodix, o Gaulês': {'base': 1489, 'escala': 115, 'cores': [
        {'h': (38, 52), 's': (0.85, 1), 'v': (0.2, 0.86), 'to': '#F2B88A'},   # pele dourada -> pele
        {'h': (95, 145), 'to': '#C8281E'}]},                                  # calça verde -> vermelha
    'Pedrix, Carregador de Menires': {'base': 9064, 'escala': 110, 'cores': [
        {'h': (40, 56), 's': (0.7, 1), 'v': (0.6, 1), 'to': '#F4F4F4'},       # listras amarelas -> brancas
        {'h': (15, 40), 's': (0.15, 0.45), 'v': (0.1, 0.5), 'to': '#2A4FA0'},  # roupa escura -> azul
        {'h': (0, 360), 's': (0, 0.22), 'v': (0.7, 1), 'to': '#D2551E'}]},    # barba e cabelo -> ruivos
    'Homero Simplório': {'base': 9107, 'escala': 105, 'cores': [
        dict(PELE, to='#FFD90F'),                                             # pele -> amarela
        {'h': (80, 160), 'to': '#9C7F5A'}]},                                  # barba verde -> barba por fazer
    'Mané do Balcão': {'base': 1207, 'escala': 95, 'cores': [
        {'h': (240, 310), 'to': '#3A3A48'}]},                                 # roupa lilás -> escura
    'Charlinho Brilho': {'base': 9095, 'escala': 100, 'cores': [
        {'h': (15, 40), 's': (0.85, 1), 'v': (0.3, 1), 'to': '#4A3020'}]},    # cabelo laranja -> castanho
    'Leôncio Violeiro': {'base': 9056, 'escala': 100, 'cores': [
        {'h': (45, 62), 's': (0.6, 1), 'v': (0.7, 1), 'to': '#B8864A'}]},     # chapéu amarelo -> couro
    'Zé do Pagode': {'base': 9083, 'escala': 100, 'cores': [
        {'h': (44, 66), 's': (0.25, 0.8), 'v': (0.45, 1), 'to': '#EFEFEA'}]},  # chapéu e calça -> brancos
    'Thor': {'base': 9019, 'escala': 100, 'cores': []},
    'Pedrão Grifo': {'base': 9017, 'escala': 105, 'cores': [
        {'h': (40, 62), 's': (0.5, 1), 'v': (0.8, 1), 'to': '#F4F4F0'},       # camisa amarela -> branca
        {'h': (200, 240), 'to': '#E8E8E8'},                                   # punhos azuis -> brancos
        {'h': (18, 32), 's': (0.55, 1), 'v': (0.25, 0.6), 'to': '#3E6B2A'}]},  # calça marrom -> verde
    'Barnabé Arroto': {'base': 9110, 'escala': 100, 'cores': [
        {'h': (195, 222), 'to': '#6A4A30'},                                   # jeans -> calça marrom
        {'h': (0, 360), 's': (0, 0.06), 'v': (0.9, 1), 'to': '#E6C6B4'}]},    # camisa branca -> rosada
    'Homem-Barril': {'base': 1619, 'escala': 110, 'cores': [
        {'h': (30, 50), 's': (0.4, 1), 'v': (0.5, 1), 'to': '#C0202A'}]},     # madeira -> barril vermelho
    'Capitão Bacalhau': {'base': 1621, 'escala': 85, 'cores': [
        {'h': (52, 70), 'to': '#F0B488'},                                     # pele verde -> pele
        {'h': (0, 20), 's': (0.8, 1), 'v': (0.3, 0.9), 'to': '#1F2F5A'}]},    # casaco vermelho -> azul-marinho
    'Capitão Pardal': {'base': 9060, 'escala': 100, 'cores': [
        {'h': (25, 45), 's': (0.85, 1), 'v': (0.5, 1), 'to': '#5A3A22'}]},    # roupa laranja -> marrom
    'Tirino, o Estrategista': {'base': 9058, 'escala': 85, 'cores': [
        {'h': (45, 62), 'to': '#A01E1E'},                                     # chapéu e roupa -> vermelho
        {'h': (12, 30), 's': (0.8, 1), 'to': '#E8D080'}]},                    # cabelo -> loiro
    'Grandão Guarda-Caça': {'base': 1472, 'escala': 78, 'cores': [
        {'h': (190, 240), 'v': (0.3, 1), 'to': '#3B2A1E'},                    # pelo azulado -> castanho-escuro
        {'h': (0, 360), 's': (0, 0.06), 'v': (0.85, 1), 'to': '#4A3A2E'}]},   # barba branca -> escura
    'Gimbo, o Anão': {'base': 9036, 'escala': 100, 'cores': [
        {'h': (0, 360), 's': (0, 0.25), 'v': (0.8, 1), 'to': '#C0501E'},      # barba branca -> ruiva
        {'h': (55, 90), 's': (0.6, 1), 'to': '#6A4A2A'}]},                    # bolsa verde -> couro
    'Ragnar': {'base': 1206, 'escala': 100, 'cores': [
        {'h': (0, 25), 's': (0.6, 1), 'v': (0.4, 1), 'to': '#7A5230'},        # vermelhos -> couro
        {'h': (225, 245), 'to': '#3A3A3A'}]},                                 # armadura azul-escura -> cinza
    'Gatão da Destruição': {'base': 9109, 'escala': 100, 'cores': [
        {'h': (0, 360), 's': (0, 0.12), 'v': (0.8, 1), 'to': '#A48AC4'},      # pelo branco -> roxo
        {'h': (220, 250), 'to': '#C85A28'},                                   # calça azul -> laranja
        {'h': (0, 360), 's': (0, 0.05), 'v': (0.45, 0.75), 'to': '#222222'}]},  # camisa cinza -> preta
    'Dionísio': {'base': 9000, 'escala': 100, 'cores': [
        {'h': (30, 50), 's': (0.05, 0.35), 'v': (0.75, 1), 'to': '#6A1F4A'},  # manto bege -> vinho
        {'h': (25, 40), 's': (0.6, 1), 'v': (0.6, 1), 'to': '#4A3020'},       # barba laranja -> castanha
        {'h': (42, 56), 's': (0.7, 1), 'to': '#4F8A2A'}]},                    # mitra dourada -> folhas de parreira
    'Rique Sanches': {'base': 9018, 'escala': 100, 'cores': [
        {'h': (340, 15), 's': (0.25, 0.75), 'v': (0.5, 1), 'to': '#F2F2F0'},  # roupão rosa -> jaleco branco
        {'h': (50, 70), 's': (0.6, 1), 'to': '#8FC8E0'},                      # faixa amarela -> camisa azul-clara
        {'h': (0, 360), 's': (0, 0.14), 'v': (0.88, 1), 'to': '#B8D4DE'}]},   # cabelo branco -> azul-acinzentado
}
# Retrato do dialogo: o oficial do NPC base (recolorido) so onde ele e o mesmo personagem do sprite;
# nos outros, um busto renderizado do proprio sprite novo.
RETRATO_OFICIAL = {'Mané do Balcão', 'Leôncio Violeiro', 'Thor', 'Homem-Barril', 'Capitão Bacalhau', 'Capitão Pardal',
                   'Grandão Guarda-Caça', 'Ragnar', 'Dionísio'}
CELEB_SPRITES = []
for _i, _c in enumerate(CELEBRITIES):
    _look = CELEB_LOOK[_c[0]]
    CELEB_SPRITES.append({'nome': _c[0], 'gfx': 9920 + _i, 'base': _look['base'], 'cores': _look['cores'],
                          'retrato': 'oficial' if _c[0] in RETRATO_OFICIAL else 'sprite'})
    CELEBRITIES[_i] = (_c[0], 9920 + _i, _look['escala'], None, _c[4], _c[5])

for _i, (_name, _gfx, _scale, _colors, _fala, _extras) in enumerate(CELEBRITIES):
    _nid = 3014 + _i
    NPCS.append({'id': _nid, 'name': _name, 'gfx': _gfx, 'scale': _scale, 'colors': _colors, 'maps': {30015: None}})
    DIALOGS[_nid] = {'inicio': (_fala, [(q_, f'extra{k}') for k, (q_, _) in enumerate(_extras)] + [('Saúde!', 'fim')])}
    for _k, (_, _resp) in enumerate(_extras):
        DIALOGS[_nid][f'extra{_k}'] = (_resp, [('Voltar.', 'inicio'), ('Saúde!', 'fim')])


# ----------------------------------------------------------------- Mercadores (todos os itens do jogo)
# Um Mercador LabTech ao lado do zaap de Bonta e de Brakmar. O dialogo escolhe a categoria e abre a janela de compra
# (p:openShop). Os itens de cada categoria sao lidos do banco pelo build.py (tabela item_template, por tipo).
LOJA_NPCS = [
    {'id': 3040, 'name': 'Mercador LabTech de Bonta', 'gfx': 130, 'colors': C_LABTECH, 'map': 4263, 'cell': 132, 'dir': 1},
    {'id': 3041, 'name': 'Mercadora LabTech de Brâkmar', 'gfx': 131, 'gender': 1, 'colors': C_LABTECH, 'map': 5295, 'cell': 523, 'dir': 1},
]
# menu -> [(chave, texto, tipos de item)]. 'resto' = todos os tipos que nao aparecem em outra categoria.
LOJA_MENUS = [
    ('equip', 'Equipamentos', [
        ('chapeus', 'Chapéus', [16]), ('capas', 'Capas e mochilas', [17, 81]), ('amuletos', 'Amuletos', [1]),
        ('aneis', 'Anéis', [9]), ('cintos', 'Cintos', [10]), ('botas', 'Botas', [11]), ('escudos', 'Escudos', [82]),
        ('dofus', 'Dofus e Obvijevans', [23, 113]), ('familiares', 'Familiares e montarias', [18, 90, 97, 116, 72])]),
    ('armas', 'Armas', [
        ('arcos', 'Arcos e bestas', [2, 102]), ('varinhas', 'Varinhas', [3]), ('cajados', 'Cajados', [4]),
        ('adagas', 'Adagas', [5]), ('espadas', 'Espadas', [6]), ('martelos', 'Martelos', [7]), ('pas', 'Pás', [8]),
        ('machados', 'Machados', [19]), ('ferramentas', 'Ferramentas, picaretas e foices', [20, 21, 22, 99, 114])]),
    ('consumo', 'Poções, pergaminhos e comida', [
        ('pocoes', 'Poções e pergaminhos', [12, 13, 14, 26, 43, 44, 45, 73, 74, 75, 76, 86, 87, 126]),
        ('comida', 'Pães, carnes, peixes e bebidas', [28, 33, 37, 42, 49, 64, 69, 79]),
        ('almas', 'Pedras de alma, chaves e runas', [78, 83, 84, 85, 88, 111]),
        ('efeitos', 'Transformações, bênçãos e outros', [27, 29, 30, 31, 32, 61, 93, 94, 112])]),
    ('recursos', 'Recursos', 'resto'),
]
LOJA_RESTO_PARTES = 4
for _n in LOJA_NPCS:
    NPCS.append({'id': _n['id'], 'name': _n['name'], 'gfx': _n['gfx'], 'gender': _n.get('gender', 0), 'colors': _n['colors'],
                 'maps': {}, 'vendor': True})
    _d = {'inicio': ('Tudo o que existe no Mundo dos Doze, numa loja só. Os deuses cobram devoção; eu só cobro kamas. '
                     'Vendo de tudo, mas cada item pede o nível dele: isso nem o LabTech destravou. O que vai ser?',
                     [(_label, _key) for _key, _label, _ in LOJA_MENUS] + [('Só olhando, obrigado.', 'fim')])}
    for _key, _label, _cats in LOJA_MENUS:
        if _cats == 'resto':
            _cats = [(f'resto{_i + 1}', f'{_label} (parte {_i + 1} de {LOJA_RESTO_PARTES})', None) for _i in range(LOJA_RESTO_PARTES)]
        _d[_key] = (f'{_label}: escolha a prateleira e a janela de compra abre na hora.',
                    [(_t, f"lua:lojaAbrir(p, {_n['id']}, '{_c}')") for _c, _t, _ in _cats] + [('Voltar.', 'inicio')])
    DIALOGS[_n['id']] = _d
