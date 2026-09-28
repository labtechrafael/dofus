"""Traduz o menu de administrador do cliente (rc-menuadmin.xml) para portugues.

So os rotulos (label="...") mudam; comandos ficam iguais. Nomes proprios (monstros, conjuntos, titulos) ficam
como estao. O original fica em backup/labtech na primeira execucao. Grava em UTF-8 (o Flash le XML como UTF-8)."""
import os
import re
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
CLIENTS = [os.path.join(ROOT, 'server', 'client-starloco', 'resources', 'app', 'retroclient'),
           os.path.join(ROOT, 'Client-Dofus-1-29-master', 'Client-Dofus-1-29-master', 'Client')]
BACKUP = os.path.join(ROOT, 'backup', 'labtech')

EXATO = {
    'Menu Admin': 'Menu do Administrador', 'Recharger le fichier XML': 'Recarregar este menu (XML)',
    'Sauvegarde Serveur': 'Salvar o servidor', 'SPAWN un grp de mobs': 'Criar grupo de monstros',
    'Groupe Officiel': 'Grupos oficiais', 'Monstre': 'Monstro', 'Faire venir le joueur': 'Trazer o jogador até mim',
    'Dons': 'Presentes', 'Alignement': 'Alinhamento', 'Aligner le joueur en Neutre': 'Deixar o jogador Neutro',
    'Aligner le joueur en Bontarien': 'Alinhar o jogador a Bonta', 'Aligner le joueur en Brakmarien': 'Alinhar o jogador a Brâkmar',
    'Aligner le joueur en Mercenaire': 'Tornar o jogador Mercenário', 'Grade': 'Grau',
    'Recolte': 'Coleta', 'Bucheron': 'Lenhador', 'Ajoute le Metier': 'Aprender a profissão', 'Ajoute le métier': 'Aprender a profissão',
    'Oublier le Metier': 'Esquecer a profissão', "Ajoute l Objet": 'Dar a ferramenta', 'XP a ajoute': 'XP a adicionar',
    'Level 100': 'Nível 100', 'Alchimiste': 'Alquimista', 'Mineur': 'Minerador', 'Paysan': 'Camponês', 'Pecheur': 'Pescador',
    'Chasseur': 'Caçador', 'Craft': 'Fabricação', 'Forgeur d Epee': 'Ferreiro de Espadas', 'Sculteur d Arc': 'Escultor de Arcos',
    'Forgeur de Marteau': 'Ferreiro de Martelos', 'Coordonier': 'Sapateiro', 'Bijoutier': 'Joalheiro',
    'Forgeur de Dague': 'Ferreiro de Adagas', 'Sculteur Baton': 'Escultor de Cajados', 'Sculteur Baguette': 'Escultor de Varinhas',
    'Forgeur Pelle': 'Ferreiro de Pás', 'Boulanger': 'Padeiro', 'Tailleur': 'Alfaiate', 'Forgeur Hache': 'Ferreiro de Machados',
    'Boucher': 'Açougueiro', 'Poissonier': 'Peixeiro', 'Forgeur de Bouclier': 'Ferreiro de Escudos', 'Bricoleur': 'Faz-tudo',
    'Forgemagie': 'Forjamagia', 'Forgemage de Dague': 'Forjamago de Adagas', "Forgemage d Epee": 'Forjamago de Espadas',
    'Forgemage de Marteau': 'Forjamago de Martelos', 'Forgemage de marteau': 'Forjamago de Martelos',
    'Forgemage de Pelle': 'Forjamago de Pás', 'Scultemage D Arc': 'Esculpimago de Arcos',
    'Scultemage D Baguette': 'Esculpimago de Varinhas', 'Forgemage de Hache': 'Forjamago de Machados',
    'Scultemage de Baton': 'Esculpimago de Cajados', 'Cordomage': 'Sapatomago', 'Joaillomage': 'Joalheimago',
    'Costumage': 'Costuremago', 'Autres': 'Outros', 'Guilde': 'Guilda', 'Creer une Guilde': 'Criar uma guilda',
    'Titres': 'Títulos', 'Enlever le titre': 'Remover o título', 'Titres Vampyres': 'Títulos Vampyros',
    'Titres Pourfendeurs': 'Títulos de Matador', 'Titres Primordiaux': 'Títulos Primordiais', 'Artisanat': 'Artesanato',
    'Forgeurs': 'Ferreiros', 'Sculpteurs': 'Escultores', 'Artisants': 'Artesãos', 'Mage': 'Magos',
    'Heros Bicentenaire': 'Herói Bicentenário', 'Terreur de la Presque-ile': 'Terror da Península', 'Undefined': 'Indefinido',
    'Niveau': 'Nível', 'Points de caracteristiques': 'Pontos de característica', 'GM Level': 'Nível de GM',
    'Points de sorts': 'Pontos de feitiço', 'Sort Elementaire': 'Feitiços elementais', 'Sort Maitrise': 'Feitiços de maestria',
    'Haches': 'Machados', 'batons': 'Cajados', 'Epees': 'Espadas', 'Arcs': 'Arcos', 'Marteaux': 'Martelos',
    'Baguettes': 'Varinhas', 'Dagues': 'Adagas', 'Pelles': 'Pás', 'Sort Classe': 'Feitiços de classe',
    "Sort d'Invocation": 'Feitiços de invocação', 'Invocation dArakne': 'Invocação de Aracne',
    'Invocation de Chaferfu': 'Invocação de Chafer Furioso', 'Panoplies': 'Conjuntos', 'Plus de 120': 'Mais de 120',
    'Issues de cadeaux': 'Vindos de presentes', 'Classee': 'Classificados', 'Moins de 60': 'Menos de 60',
    'Plus de 60': 'Mais de 60', 'Non classee': 'Não classificados', 'Objets': 'Objetos',
    'Faire la commande boutique': 'Entregar pedidos da loja', 'Donner une dinde Squelette': 'Dar um Dragoperu Esqueleto',
    'Cmds Admin serveur': 'Comandos de servidor', 'Signaler sa presence': 'Avisar que estou aqui', 'au joueur': 'ao jogador',
    'au administrateur': 'aos administradores', 'Informations': 'Informações', 'Sur le serveur': 'Sobre o servidor',
    'Qui est la ?': 'Quem está online?', 'Informations sur la map': 'Informações do mapa', 'Sur le joueur': 'Sobre o jogador',
    'Nom du joueur: %p': 'Nome do jogador: %p', 'Nom de la guilde: %g': 'Nome da guilda: %g', 'Date: %d': 'Data: %d',
    'Heure: %h': 'Hora: %h', 'Heure (raccourcie, sans decalages): %t': 'Hora (curta, sem fuso): %t', 'MyName: %n': 'Meu nome: %n',
    'Infos version: %v': 'Versão: %v', 'Nom du serveur : %s': 'Nome do servidor: %s', 'MenuAdmin by Truearena': 'Menu de admin por Truearena',
    'Actions sur le serveur': 'Ações no servidor', 'Sauvegarde': 'Salvamento', 'Sauvegarder': 'Salvar agora',
    'Reboot': 'Reiniciar', 'Reboot dans 30 minutes': 'Reiniciar em 30 minutos', 'Annuler le Reboot': 'Cancelar o reinício',
    'Exit (en cas de bug)': 'Desligar (em caso de erro)', 'Exit': 'Desligar', 'Moderation': 'Moderação', 'Avertir': 'Avisar',
    'Sanction': 'Punição', 'Avertissement': 'Advertência', 'flood=mute': 'Flood = silenciado', 'Use /b !': 'Use /b !',
    'Use /r !': 'Use /r !', 'Insulte': 'Insulto', 'Sanctions': 'Punições', 'Sanctions graves': 'Punições graves',
    "Envoyer a la prison d'Alkatraz": 'Mandar para a prisão de Alkatraz', 'Envoyer a la prison Astrub': 'Mandar para a prisão de Astrub',
    'Exclure': 'Expulsar', 'Bannir': 'Banir', 'Debannir': 'Desbanir', 'Ban IP': 'Banir IP', 'Mute': 'Silenciar',
    'Une minute': 'Um minuto', 'Trois minutes': 'Três minutos', 'Dix minutes': 'Dez minutos', 'Une heure': 'Uma hora',
    'Deux heure': 'Duas horas', 'Infini': 'Para sempre', 'Empecher de parler pour une duree donnee': 'Impedir de falar por um tempo',
    'Redonner la parole': 'Devolver a fala', 'Jeux': 'Jogos', 'Fun': 'Diversão', 'Baffer': 'Dar um tapa',
    'Avertir pour sa guilde': 'Avisar sobre a guilda', 'Mechant': 'Malvado', 'I Love You': 'Eu te amo', 'Animateur': 'Animador',
    'Noob': 'Novato', 'Bannir ?': 'Banir?', 'Bonjour les amis': 'Olá, amigos', 'Malade': 'Doente', 'Teleporter': 'Teleportar',
    'Par joueur': 'Por jogador', 'Aller au joueur': 'Ir até o jogador', 'Par Zone': 'Por região', 'Nord': 'Norte', 'Sud': 'Sul',
    'Divers': 'Diversos', 'Aller au zoneShop': 'Ir para a área da loja', 'Donjons': 'Masmorras', 'Champs': 'Campos',
    'Ensable': 'Arenoso', 'Forgeron': 'Ferreiros', 'Canides': 'Canídeos', 'Temples': 'Templos', 'Enclos': 'Cercados',
    'Enclos Brakmarien': 'Cercado de Brâkmar', 'Enclos Bontarien': 'Cercado de Bonta', 'Actions sur la map': 'Ações no mapa',
    'Combats': 'Lutas', 'Rafraichir les monstres': 'Recriar os monstros', 'Avertir la map': 'Avisar o mapa',
    'Animation': 'Eventos', 'Annonce Event': 'Anunciar evento', "Avertir d'un event": 'Avisar de um evento',
    "Avertir d'un event morph": 'Avisar de um evento de transformação', "Avertir d'un event PVP": 'Avisar de um evento PvP',
    "Avertir d'un event Cache cache": 'Avisar de um evento de esconde-esconde', 'Interfaces': 'Janelas',
    'Gestionnaire des items (type vue)': 'Gerenciador de itens', 'Gestionnaire des monstres': 'Gerenciador de monstros',
    'Gestionnaire de looks': 'Gerenciador de aparências', 'Gestionnaire de Panos': 'Gerenciador de conjuntos',
    'Se transformer': 'Transformar-se', 'guess': 'aleatório', 'Taille': 'Tamanho', '100% (basique)': '100% (normal)',
    'Looks': 'Aparências', 'Rendre son apparence': 'Voltar à aparência normal', 'Rendre invisible': 'Ficar invisível',
    'Protecteurs des Mois': 'Protetores dos Meses', 'Autre :': 'Outros:', "Avertir d'un reboot": 'Avisar de um reinício',
    'Infos version': 'Informações da versão', 'Donjon MAX': 'Masmorra MÁX', 'Chene Mou': 'Carvalho Mole',
    'Kralamour Geant': 'Kralamar Gigante', 'Maitre Corbac': 'Mestre Corvok', 'Faire venir': 'Trazer',
    'Incarnam - (Devant le) Donjon': 'Incarnam - Frente da masmorra', 'Incarnam - Transport vers Astrub': 'Incarnam - Transporte para Astrub',
    'Incarnam - Taverne (10354)': 'Incarnam - Taverna (10354)', "Astrub - Puit avec l'osamodas": 'Astrub - Poço do Osamodas',
    'Astrub - Quete Dofawa': 'Astrub - Missão do Dofawa', 'Astrub - Jardin': 'Astrub - Jardim',
    'Astrub - Zone Shop (Zaap)': 'Astrub - Área da loja (zaap)', 'Astrub - Maison Mercenaire': 'Astrub - Casa dos Mercenários',
    'Astrub - Zone Agro': 'Astrub - Área agressiva', 'Astrub - Foret': 'Astrub - Floresta', 'Astrub - Champs': 'Astrub - Campos',
    'Astrub - Prairies': 'Astrub - Pradarias', 'Astrub - Coins des Tofus': 'Astrub - Canto dos Tofus',
    'Amakna - Porte de Sufokia [10, 22] (10354)': 'Amakna - Portão de Sufokia [10, 22] (10354)',
    'Amakna - Plaine des scarafeuilles [-1, 24] (1242)': 'Amakna - Planície dos Escaravelhos [-1, 24] (1242)',
    'Villages des brigandins [-18, -26] (6855)': 'Vila dos Bandidos [-18, -26] (6855)',
    'Plaines de Cania - Plaines Rocheuses [-14, -47] (3250)': 'Planícies de Cania - Planícies Rochosas [-14, -47] (3250)',
    'Plaines de Cania - Massif de Cania [-20, -20] (3022)': 'Planícies de Cania - Maciço de Cania [-20, -20] (3022)',
    'Landes de Sidimote': 'Charnecas de Sidimote', 'Landes de Sidimote [-24, 12] (4739)': 'Charnecas de Sidimote [-24, 12] (4739)',
    'Alkatraz - Prison': 'Alkatraz - Prisão', "Prison d'Astrub": 'Prisão de Astrub', 'Astrub - Prison': 'Astrub - Prisão',
    "Ile d'Otomai - Le village Cotier [-46, 18] (10643)": 'Ilha de Otomai - Vila Costeira [-46, 18] (10643)',
    'Bandits de Cania': 'Bandidos de Cania', 'Grozilla et Grasmera': 'Grozilla e Grasmera', 'Wa Wabbit': 'Wa Wabbit',
    'Capture d\'ame': 'Captura de alma', 'Capture de monture': 'Captura de montaria', 'Doom(Admin)': 'Doom (admin)',
    'Tuerie(admin)': 'Massacre (admin)', 'Liberation': 'Libertação', 'Marteau de Moon': 'Martelo de Moon',
    'Boomrang Perfide': 'Bumerangue Pérfido', 'Foudraiement': 'Fulminação', '1 a 20': '1 a 20',
}
PADROES = [
    (r'^Monter niveau (\d+)$', r'Subir para o nível \1'),
    (r'^\+ ([\d ]+) points? \(\+ ?(\d+) niveaux?\)$', r'+\1 pontos (+\2 níveis)'),
    (r'^Temple (.+)$', r'Templo \1'),
    (r'^Forgeur de (.+) Primordial$', r'Ferreiro Primordial (\1)'),
    (r"^Forgeur d'(.+) Primordial$", r'Ferreiro Primordial (\1)'),
    (r'^Sculpteur de (.+) Primordial$', r'Escultor Primordial (\1)'),
    (r"^Sculpteur d'(.+) Primordial$", r'Escultor Primordial (\1)'),
    (r'^Forgemage de (.+) Primordial$', r'Forjamago Primordial (\1)'),
    (r"^Forgemage d'(.+) Primordial$", r'Forjamago Primordial (\1)'),
    (r'^Sculptemage de (.+) Primordial$', r'Esculpimago Primordial (\1)'),
    (r"^Sculptemage d'(.+) Primordial$", r'Esculpimago Primordial (\1)'),
    (r'^(.+) Primordial$', r'\1 Primordial'),
]


def traduz(label):
    if label in EXATO:
        return EXATO[label]
    for pat, rep in PADROES:
        if re.match(pat, label):
            return re.sub(pat, rep, label)
    return label


def main():
    for client in CLIENTS:
        path = os.path.join(client, 'rc-menuadmin.xml')
        if not os.path.exists(path):
            continue
        os.makedirs(BACKUP, exist_ok=True)
        orig = os.path.join(BACKUP, 'rc-menuadmin.xml.orig')
        if not os.path.exists(orig):
            shutil.copy2(path, orig)
        raw = open(orig, 'rb').read()
        try:
            text = raw.decode('utf-8')
        except UnicodeDecodeError:
            text = raw.decode('latin-1')
        n = 0

        def sub(m):
            nonlocal n
            new = traduz(m.group(1))
            n += new != m.group(1)
            return 'label="' + new.replace('"', '&quot;') + '"'
        text = re.sub(r'label="([^"]*)"', sub, text)
        open(path, 'w', encoding='utf-8', newline='').write(text)
        print(f'{path}: {n} rotulos traduzidos')


if __name__ == '__main__':
    main()
