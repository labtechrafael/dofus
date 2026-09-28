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
              'stats': '64#3e8#5dc#0#1d501+999',   # 1000 a 1500 de dano neutro
              'weapon': [5, 4, 1, 1, 30, 50, False, True], 'an': 15, 'price': 100, 'weight': 20})
ITEMS.append({'id': 30002, 'type': 7, 'level': 1, 'g': 3002, 'icon': 'manopla_mk12', 'name': 'Manopla Gambiarra Mk XII',
              'desc': 'Doze núcleos encaixados, um de cada classe. Ninguém sabe como funciona. Nem quem construiu. Mas funciona.',
              'stats': ','.join(f'{e}#7d0#bb8#0#1d1001+1999' for e in ('61', '63', '62', '60', '64')) + ',6f#1#0#0#0d0+1',   # 2000 a 3000 em cada elemento
             
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
     'stats': '6f#1#0#0#0d0+1,80#1#0#0#0d0+1,b0#1388#0#0#0d0+5000',   # +1 PA, +1 PM, +5000 prospeccao
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
CELEBRITIES = [  # paródias (nomes e falas próprios, sem bordões nem letras de terceiros)
    ('Bigodix, o Gaulês', 80, 80, [0xE8C04A, 0x202020, 0xC02020],
     'Pelos meus bigodes! Os deuses daqui dão poder de mão beijada? Na minha aldeia o druida faz uma poção mágica com as próprias mãos. É quase uma cervejaria.',
     [('E o seu amigo grandão?', 'O Pedrix? Caiu num caldeirão quando era pequeno. Não deixe ele chegar perto do barril.')]),
    ('Pedrix, Carregador de Menires', 120, 135, [0xC0502A, 0x3A6FD0, 0xE8E8E8],
     'Eu NÃO sou gordo! É o jaleco que é justo. Esses LabTechs são malucos... mas a cerveja deles combina com javali assado.',
     [('Quer uma cerveja?', 'Só um barril. Pequeno. Dois.')]),
    ('Homero Simplório', 30, 110, [0x1A1A1A, 0xF0F0F0, 0x3050A0],
     'Hmmm... cerveja LabTech. Eu vim só pela rosquinha, mas fiquei pela cerveja. E pelo sofá. Principalmente pelo sofá.',
     [('Tudo bem aí?', 'Perdi o emprego, achei uma rosquinha, ganhei uma cerveja. Dia excelente.')]),
    ('Mané do Balcão', 40, 100, [0x2A2A2A, 0x6A7A50, 0xE8E8E8],
     'Taverna do Mané, filial LabTech. Se o telefone tocar procurando alguém de nome esquisito, não atenda. É trote.',
     [('Tem cerveja de marca?', 'Aqui só tem cerveja feita à mão. Marca famosa é pra quem não sabe fermentar.')]),
    ('Charlinho Brilho', 60, 100, [0x4A3020, 0x1A2A4A, 0xE0E0E0],
     'Vencendo, sempre vencendo! Vim ao LabTech porque aqui todo mundo faz a própria sorte. Bebo com moderação, brindo sem moderação.',
     [('Algum conselho?', 'Seja o protagonista da sua própria série. E sempre agradeça ao barman.')]),
    ('Leôncio Violeiro', 90, 100, [0x2A1A10, 0x8A5A2A, 0xE8D8A0],
     'Ô, trem bom! Entre um gole e outro, uma moda de viola. Cerveja gelada e sertanejo raiz: é assim que a gente faz no LabTech.',
     [('Canta uma?', 'Essa eu fiz agora: "caneca na mão, viola no peito, cerveja artesanal feita do nosso jeito".')]),
    ('Zé do Pagode', 120, 100, [0x9A9A9A, 0xF4F4F4, 0x2A6A2A],
     'Devagarinho, sem pressa, que a vida é boa! Aqui no LabTech o samba é de fundo de quintal e a cerveja é feita em casa, do jeitinho que eu gosto.',
     [('Um brinde?', 'Saúde! E bora pro boteco, que o pagode não espera ninguém.')]),
    ('Thor', 80, 110, [0xE8C84A, 0x5A5A6A, 0xB01818],
     'Eu sou Thor, filho de Odin. Sou um dos dois únicos deuses bem-vindos no LabTech: eu bebo com eles. Os outros só distribuem poder de mão beijada.',
     [('E o martelo?', 'Mjölnir só obedece a quem é digno. A Manopla Gambiarra obedece a quem soldou ela direito. Respeito.')]),
    ('Pedrão Grifo', 30, 115, [0x5A3A20, 0xF0F0F0, 0x3A6A2A],
     'Hehehehe. Sabe o que é melhor que uma cerveja? Duas cervejas. Sabe o que é melhor que duas? O laboratório inteiro.',
     [('Conta uma história.', 'Isso me lembra aquela vez em que eu briguei com uma galinha gigante pela cidade inteira. Ou foram duas vezes? Hehehe.')]),
    ('Barnabé Arroto', 30, 105, [0x5A3A1A, 0xE0B080, 0x3A3A7A],
     '*burp* Cheguei antes de todo mundo e vou sair depois de todo mundo. Cerveja LabTech é quase tão boa quanto a do Mané. Não conta pra ele.',
     [('Tudo bem?', 'Melhor impossível. Já cantei até ópera hoje.')]),
    ('Homem-Barril', 80, 105, [0x2A1A10, 0xD01818, 0x1838A0],
     'Opa, opa! O Homem-Barril está aqui para garantir que toda caneca esteja cheia! Ele nunca pergunta "por quê", ele pergunta "mais uma?"',
     [('Mais uma?', 'MAIS UMA!')]),
    ('Capitão Bacalhau', 30, 100, [0x1A1A1A, 0x1A2A6A, 0xE8E8E8],
     'Macacos me mordam! Uma cervejaria no meio do oceano e ninguém me avisou? Com mil tempestades, isto merece um brinde!',
     [('E o seu amigo repórter?', 'Foi investigar o sumiço de um barril. Aposto que foi o Pedrix.')]),
    ('Capitão Pardal', 40, 100, [0x1A1A1A, 0x6A2A1A, 0xC8B070],
     'Capitão. CAPITÃO Pardal. Por que a cerveja sempre acaba? Eu sei, pirata que se preza bebe rum. Mas o lúpulo daqui é excelente, entendeu?',
     [('E o navio?', 'Está estacionado atrás da estufa. Não conte pro Encanador que eu amarrei ele no cano principal.')]),
    ('Tirino, o Estrategista', 30, 75, [0xD8C890, 0x6A1A1A, 0xC8A040],
     'Pequeno no tamanho, grande na adega. O LabTech não pediu nada aos deuses e ainda assim tem a melhor cerveja do mundo. Isso é política.',
     [('Mais alguma coisa?', 'Quem lê muito e bebe bem nunca perde uma discussão. Pelo menos não lembra de ter perdido.')]),
    ('Grandão Guarda-Caça', 120, 145, [0x2A1A10, 0x5A3A20, 0x3A2A1A],
     'Ih, falei demais de novo... mas a Levedura Selvagem daqui é melhor que qualquer hidromel. Cuidado com o dragão lá fora: ele adora malte.',
     [('Dragão?', 'É um Dragão Porco. Bem educado. Quase nunca morde.')]),
    ('Gimbo, o Anão', 30, 85, [0xC0502A, 0x6A6A70, 0x8A2A1A],
     'Anão não se arremessa: anão arremessa barril, e só se estiver vazio. Cerveja boa é a que se faz na forja, com as próprias mãos. E com machado.',
     [('Uma competição?', 'Quem beber mais ganha. Estou em quarenta e dois. E você?')]),
    ('Ragnar', 110, 105, [0xD8C890, 0x4A4A4A, 0x6A3A1A],
     'O salão dos deuses espera, mas não tem pressa. Primeiro a cerveja, depois a glória. Os deuses que me esperem sentados.',
     [('Não teme os deuses?', 'Os deuses precisam mais de nós do que nós deles. Os LabTechs entenderam isso primeiro.')]),
    ('Gatão da Destruição', 60, 100, [0x6A4A8A, 0x1A1A1A, 0xD8B040],
     'Sou o Gatão, o Deus da Destruição. Vim destruir este planeta, mas provei a Stout do Estagiário. Destruição adiada.',
     [('E agora?', 'Tragam mais uma. Se estiver boa, talvez eu esqueça de vez.')]),
    ('Dionísio', 100, 105, [0x3A1A4A, 0x7A2A8A, 0xD8C040],
     'Sou Dionísio, deus do vinho e da festa: o outro deus bem-vindo por aqui. Meus colegas lá em cima dão poder de graça; eu só dou ressaca. Pelo menos sou honesto.',
     [('Vinho ou cerveja?', 'Os dois, meu amigo. Um deus sabe se adaptar. Diferente dos outros.')]),
]
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
                     'E aqui qualquer item serve em qualquer nível: o LabTech tirou a trava. O que vai ser?',
                     [(_label, _key) for _key, _label, _ in LOJA_MENUS] + [('Só olhando, obrigado.', 'fim')])}
    for _key, _label, _cats in LOJA_MENUS:
        if _cats == 'resto':
            _cats = [(f'resto{_i + 1}', f'{_label} (parte {_i + 1} de {LOJA_RESTO_PARTES})', None) for _i in range(LOJA_RESTO_PARTES)]
        _d[_key] = (f'{_label}: escolha a prateleira e a janela de compra abre na hora.',
                    [(_t, f"lua:lojaAbrir(p, {_n['id']}, '{_c}')") for _c, _t, _ in _cats] + [('Voltar.', 'inicio')])
    DIALOGS[_n['id']] = _d
