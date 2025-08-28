"""
Analyseur de Proverbes Arabes - Application complète avec interface graphique

Ce programme permet :
1. L'analyse lexicale et syntaxique d'une grammaire simple pour afficher des proverbes arabes
2. La vérification sémantique des correspondances entre conditions et proverbes
3. La gestion d'une base de données de proverbes
4. L'exécution de tests automatisés

Fonctionnalités principales :
- Interface utilisateur intuitive avec onglets
- Coloration syntaxique et mise en forme avancée
- Système d'autocomplétion pour les proverbes
- Vérification sémantique des correspondances condition/proverbe
- Gestion des fichiers de proverbes
- Batterie de tests intégrée
"""

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, ttk
from ply.lex import lex
from ply.yacc import yacc
from pprint import pformat
import os

# ==================== CONFIGURATION INITIALE ====================

# Fichier de stockage des proverbes
PROVERBES_FILE = "proverbes.txt"

# Proverbes par défaut (thème: texte)
DEFAULT_PROVERBES = {
    "CONSEIL": "أسمع كلام اللي يبكيك وماتسمعش كلام اللي يضحكك",
    "MODERATION": "إذا صاحبك عسل ما تلحسوش الكل",
    "SAGESSE": "إسأل مجرب ولا تسأل طبيب",
    "PRUDENCE": "اللي خاف نجى",
    "GENEROSITE": "أعمل الخير وارمي في البحر",
    "ADAPTATION": "أعمل كيف جارك وإلا حول باب دارك",
    "COURAGE": "اللي يخاف من العفريت يطلع له",
    "PREVENTION": "شد مشومك لا يجيك ما اشوم",
    "SANTE": "الصحة تاج على رؤوس الأصحاء",
    "VAINE": "اللي ينام عالجرح يلاقي الربح",
    "BIENETRE": "العقل السليم في الجسم السليم",
    "RICHESSE": "اللي عندو ما يموتش",
    "DETTE": "اللي عليه مليان، راهو خسران",
    "SATISFACTION": "القناعة كنز لا يفنى",
    "METEO": "اللي ما عندوش مطر، يستنا الندى",
    "AGRICULTURE": "اللي يزرع حصاد",
    "PATIENCE": "الصبر مفتاح الفرج",
    "EDUCATION": "اللي يربّي العود يربّي الحصاد",
    "FAMILLE": "اليد الواحدة ما تصفقش",
    "TEMPS": "الوقت اللي ما يقدّرش يقدّرك",
    "AGE": "الكبير كبير ولو طار",
    "JEUNESSE": "اللي يستعجل ياكل خبز حار",
    "EXPERIENCE": "الوقت شيخ",
    "OPPORTUNITE": "اللي يغامر يربح",
    "NAVIGATION": "المركب اللي ما تهزّش ما تمشّيش",
    "PECHE": "اللي يخاف من الموج ما يفرشش",
    "AMITIE": "إسأل على صاحبك إستغناش أما الطبيعة هي هي",
    "TRAHISON": "البقرة كيف اتطيح تكثر اسكاكينها",
    "ESPOIR_DECU": "عاش يتمني في عنبة مات جابولو عرجون",
    "INEFFICACITE ": "جا يعاون فيه على قبر بوه هربلو بالفاس",
    "REVANCHE": "الّي يبيعك بالفول بيعو بالقشور",
    "INJUSTICE": "عريان يسلب في ميت",
    "DESTINEE": "الي ليك لك و الي خاطيك خاطيك",
    "ECHEC": "جا يكحلها عماها",
    "VERITE": "اللي فيه طبة عمرها ماتتخبى",
    "AUTOJUSTIFICATION": "ضربو على قرعتو قال شعري طاح",
    "HERITAGE": "ولد الفار يطلع حفار",
    "FOLIE": "مهبولة و زغرتولها في وذنها",
    "OUBLI": "ملي دفنوه مازاروه",
    "NOSTALGIE": "اللي يبدل لحية بلحية يجي نهار يشتاقهم لثنين",
    "COINCIDENCE": "فردة ولقات اختها",
    "ABUS": "اللي يكثر مالعسل يمصاط",
    "IRONIE": "قلو يقوي سعدك قلو توة توة",
    "CONTRASTE_ACTIONS": "أعملْ الخير وأنساه واعْمل الشّر وتفكره",
    "RELIGION_TRAVAIL": "أعمِلْ الفرض وانقب الأرض",
    "IMITATION": "أعمِلْ كيف جارك وإلا حول باب دارك",
    "FIERTE": "إللّي يعْرف عِزَو كلام الناس ما يهزو",
    "HUMILITE": "كلّي راسو فيها وكلّي دارو فيها",
    "SOLIDARITE": "اللي ما يعرفك ما يثمنك",
    "JUSTICE": "اللي يزرع الشوك ما يجنيش الورد",
    "HONNETETE": "الصدق منجى والكذب مهلك",
    "TRAVAIL": "اليد اللي ما تقرضش ما تلسعش",
    "OPINIATRETE": "اللي ما يسمعش كلام الناس يسمع كلام الراس",
    "CHANCE": "اللي ما يربحش في القرعة يربح في اللقعة",
    "DISCERNEMENT": "اللي ما يعرف الصقر يشويه",
    "OPPORTUNITE_PERDUE": "الفرصة ما تباتش تاني",
    "TEMERITE": "اللي ما يخافش من الموت ما يخافش من الذكر",
    "AVARICE": "اللي يبخل على نفسه كيفاش يبخل على الناس",
    "MALCHANCE": "اللي ما يربحش في اللقعة يربح في القرعة",
    "INGRATITUDE": "ربّي الكلب عاضك",
    "HYPOCRISIE": "وجه حلو وقلب ملعون",
    "FATALISME": "اللي كتب ليك يجيك ولو كان تحت الأرض",
    "DETERMINATION": "اللي يخاف من العfريت يطلع له",
    "ESPOIR": "الصبر مفتاح الفرج",
    "TEMPERANCE": "اللي ياكل بزاف ياكلو بزاف",
    "RECONNAISSANCE": "اللي يعمل المعروف يلقاه",
    "MEFIANCE": "اللي يخاف من الشيطان يخاف من الظل",
    "AMBITION": "اللي ما يطيرش عالعالية ينام في الحضيضة",
    "RUSE": "اللي ما يعرفش يلعب بالعصا يلعب بالعصافير",
    "CHARITE": "اليد اللي ما تعطي ما تاخدش",
    "HABITUDE": "اللي يعود على الشيء يصير عليه",
    "DILIGENCE": "اللي يستعجل ياكل خبز حار",
    "PRESCIENCE": "اللي ما يعرفش آخر الدرب ما يمشيش في الليل",
    "OPINIATRE": "اللي ما يسمعش كلام الناس يسمع كلام الراس",
    "PERSEVERANCE": "اللي يضرب الحديد وهو بارد ما يطلعش منه نار",
    "TEMERITE": "اللي ما يخافش من الموت ما يخافش من الذكر",
    "CONFIANCE": "اللي يثق في الناس ينام قرير العين",
    "MALADRESSE": "اللي ما يعرفش يسبح يقول المي عميقة",
    "INGENIOSITE": "اللي ما عندوش حبل يربط به الحمار يربطه بذنبه",
    "OPPORTUNISME": "اللي ما يعرفش يلعب بالعصا يلعب بالعصافير",
    "PREVOYANCE": "اللي ما يخيطش جرابه ينام حافي",
    "RENONCEMENT": "اللي ما يقدرش على العنب يقول حامض",
    "AUDACE": "اللي ما يخافش من اللي يموت ما يخافش من اللي يذبح",
    "FATIGUE": "اللي ما ينامش بالليل ينام بالنهار",
    "OPPORTUNITE_SAISIE": "اللي يغتنم الفرصة ما يندمش",
    "PRECAUTION": "اللي ما يخيطش جرابه ينام حافي",
    "DISCIPLINE": "اللي ما يربّيش العود ما يربّيش الحصاد",
    "HONNEUR": "اللي ما يخافش من الموت ما يخافش من الذكر",
    "SERENITE": "اللي ما يهتمش بالدنيا ينام قرير العين"
}

# ==================== ANALYSE SEMANTIQUE AMELIOREE ====================


class SemanticAnalyzer:
    """
    Analyseur sémantique amélioré avec vérification des correspondances
    entre conditions et proverbes affichés.

    Attributs:
        errors (list): Liste des erreurs sémantiques détectées
        warnings (list): Liste des avertissements sémantiques
        symbol_table (dict): Table des symboles (variables déclarées)
        used_proverbs (set): Ensemble des proverbes utilisés
        proverbes (dict): Dictionnaire des proverbes disponibles
        themes_attendus (dict): Règles de correspondance condition/proverbe
    """

    def __init__(self, proverbes):
        """Initialise l'analyseur avec les proverbes disponibles"""
        self.errors = []
        self.warnings = []
        self.symbol_table = {}
        self.used_proverbs = set()
        self.proverbes = proverbes

        # Définition des thèmes attendus pour chaque type de condition
        self.themes_attendus = {
            # Conditions string avec valeurs possibles et thèmes attendus
            "humeur": {
                "triste": ["CONSEIL", "PATIENCE", "SOLIDARITE"],
                "joyeuse": ["BIENETRE", "SATISFACTION", "FIERTE"],
                "colere": ["PRUDENCE", "MODERATION", "TEMPERANCE"],
                "peur": ["COURAGE", "DETERMINATION", "TEMERITE"]
            },
            "besoin": {
                "conseil": ["CONSEIL", "SAGESSE", "EXPERIENCE"],
                "aide": ["SOLIDARITE", "GENEROSITE", "CHARITE"],
                "argent": ["RICHESSE", "DETTE", "SATISFACTION"],
                "sante": ["SANTE", "BIENETRE", "PATIENCE"]
            },
            "situation": {
                "difficile": ["PERSEVERANCE", "PATIENCE", "ESPOIR"],
                "facile": ["MODERATION", "PRUDENCE", "HUMILITE"],
                "dangereuse": ["COURAGE", "PRUDENCE", "PREVENTION"],
                "incertaine": ["PATIENCE", "SAGESSE", "PREVOYANCE"]
            },
            # Conditions numériques avec seuils et thèmes attendus
            "age": {
                (0, 18): ["JEUNESSE", "EDUCATION", "DISCIPLINE"],
                (19, 40): ["AMBITION", "TRAVAIL", "OPPORTUNITE"],
                (41, 60): ["SAGESSE", "EXPERIENCE", "PRUDENCE"],
                (61, 150): ["AGE", "PATIENCE", "SATISFACTION"]
            },
            "richesse": {
                (0, 1000): ["SATISFACTION", "GENEROSITE", "TRAVAIL"],
                (1001, 10000): ["RICHESSE", "PRUDENCE", "MODERATION"],
                (10001, 100000): ["GENEROSITE", "CHARITE", "HONNETETE"],
                (100001, float('inf')): ["AVARICE", "OPPORTUNISME", "HYPOCRISIE"]
            }
        }

    def get_expected_themes(self, var, val=None):
        """
        Retourne les thèmes attendus pour une variable et valeur donnée

        Args:
            var (str): Nom de la variable conditionnelle
            val (str/int/float): Valeur de la variable (optionnel)

        Returns:
            list: Liste des thèmes de proverbes attendus
        """
        expected = []

        # Pour les variables string
        if var in self.themes_attendus and isinstance(self.themes_attendus[var], dict):
            if val and val in self.themes_attendus[var]:
                expected.extend(self.themes_attendus[var][val])
            else:
                # Si pas de valeur spécifique, prendre tous les thèmes possibles
                for themes in self.themes_attendus[var].values():
                    expected.extend(themes)

        # Pour les variables numériques
        elif var in self.themes_attendus and isinstance(self.themes_attendus[var], dict):
            if isinstance(val, (int, float)):
                for (min_val, max_val), themes in self.themes_attendus[var].items():
                    if min_val <= val <= max_val:
                        expected.extend(themes)
            else:
                # Si pas de valeur spécifique, prendre tous les thèmes possibles
                for themes in self.themes_attendus[var].values():
                    expected.extend(themes)

        return list(set(expected))  # Éliminer les doublons

    def check_condition_proverb_match(self, var, val, proverb_theme):
        """
        Vérifie la cohérence sémantique entre condition et proverbe

        Args:
            var (str): Variable de la condition
            val (str/int/float): Valeur de la condition
            proverb_theme (str): Thème du proverbe à afficher

        Returns:
            bool: True si la correspondance est valide, False sinon
        """
        expected_themes = self.get_expected_themes(var, val)

        if not expected_themes:
            self.warnings.append(f"Aucun thème attendu défini pour la variable '{var}'")
            return True

        if proverb_theme not in expected_themes:
            self.errors.append(
                f"Incohérence sémantique: le proverbe '{proverb_theme}' ({self.proverbes[proverb_theme]}) "
                f"ne correspond pas à la condition '{var} == {val}'. "
                f"Thèmes attendus: {', '.join(expected_themes)}"
            )
            return False
        return True

    def check_condition(self, condition):
        """
        Analyse sémantique d'une condition avec vérification renforcée

        Args:
            condition (tuple): Condition à analyser sous forme de tuple
        """
        if len(condition) == 5:  # SI condition
            var, op, val, actions = condition[1], condition[2], condition[3], condition[4]

            # Vérification déclaration variable
            if var not in self.symbol_table:
                self.symbol_table[var] = 'string' if op == '==' else 'number'

            # Vérification type cohérent
            if op == '==' and self.symbol_table.get(var) != 'string':
                self.errors.append(f"Type incompatible pour {var} (attendu: string)")
            elif op == '>' and self.symbol_table.get(var) != 'number':
                self.errors.append(f"Type incompatible pour {var} (attendu: number)")

            # Vérifier les actions
            self.check_actions(var, val, actions)

        else:  # SINON SI condition
            var, op, val, actions = condition[3], condition[4], condition[5], condition[6]

            if var not in self.symbol_table:
                self.symbol_table[var] = 'number'
            elif self.symbol_table[var] != 'number':
                self.errors.append(f"Type incompatible pour {var} (attendu: number)")

            # Vérifier les actions
            self.check_actions(var, val, actions)

    def check_actions(self, condition_var, condition_val, actions):
        """
        Analyse sémantique des actions avec vérification des proverbes

        Args:
            condition_var (str): Variable de la condition parente
            condition_val (str/int/float): Valeur de la condition parente
            actions (list): Liste des actions à analyser
        """
        for action in actions:
            if action[0] == 'AFFICHER':
                if "PROVERBE INCONNU" in action[1]:
                    self.errors.append(f"Proverbe inconnu: {action[1]}")
                else:
                    # Extraire le thème du proverbe vérifié
                    parts = action[1].split(':')
                    if len(parts) > 0:
                        proverb_theme = parts[0].strip()
                        if proverb_theme in self.proverbes:
                            self.used_proverbs.add(proverb_theme)
                            # Vérifier la cohérence sémantique
                            self.check_condition_proverb_match(condition_var, condition_val, proverb_theme)

# ==================== GESTION DES PROVERBES ====================


def init_proverbes_file():
    """
    Crée le fichier proverbes.txt s'il n'existe pas
    avec les proverbes par défaut
    """
    if not os.path.exists(PROVERBES_FILE):
        with open(PROVERBES_FILE, 'w', encoding='utf-8') as f:
            for cle, val in DEFAULT_PROVERBES.items():
                f.write(f"{cle}:{val}\n")


def charger_proverbes():
    """
    Charge les proverbes depuis le fichier texte

    Returns:
        dict: Dictionnaire des proverbes {thème: texte}
    """
    proverbes = {}
    try:
        with open(PROVERBES_FILE, 'r', encoding='utf-8') as f:
            for ligne in f:
                if ':' in ligne:
                    cle, val = ligne.split(':', 1)
                    proverbes[cle.strip()] = val.strip()
        return proverbes
    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de charger les proverbes: {str(e)}")
        return DEFAULT_PROVERBES

# ==================== ANALYSEUR LEXICAL ET SYNTAXIQUE ====================


# ==================== Début ANALYSEUR LEXICAL ====================


def init_analyzer(proverbes):
    """
    Initialise l'analyseur lexical et syntaxique

    Args:
        proverbes (dict): Dictionnaire des proverbes disponibles

    Returns:
        tuple: (lexer, parser, symbol_table)
    """
    # Définition des tokens
    tokens = ('SI', 'SINON', 'EGAL', 'SUPERIEUR', 'AFFICHER', 'ET',
              'PROVERBE', 'NOMBRE', 'STRING', 'NOM', 'DPOINTS')

    # Définition des expressions régulières pour les tokens simples
    t_EGAL = r'=='
    t_SUPERIEUR = r'>'
    t_DPOINTS = r':'
    t_ignore = ' \t'

    # Mots réservés
    reserved = {
        'si': 'SI',
        'sinon': 'SINON',
        'afficher': 'AFFICHER',
        'et': 'ET'
    }

    # Fonctions de traitement des tokens complexes
    # Tokenise les appels de proverbes (PROVERBE("texte")) et extrait le contenu
    def t_PROVERBE(t):
        r'PROVERBE\(\s*"([^"]+)"\s*\)'
        t.value = t.value[9:-1].strip('"\' ')
        return t

    # Tokenise les nombres entiers et les convertit en type int
    def t_NOMBRE(t):
        r'\d+'
        t.value = int(t.value)
        return t

    # Tokenise les chaînes entre guillemets et supprime les guillemets
    def t_STRING(t):
        r'"[^"]+"'
        t.value = t.value[1:-1]
        return t

    # Tokenise les identifiants et vérifie s'ils sont des mots réservés
    def t_NOM(t):
        r'[a-zA-Z_éèà][a-zA-Z0-9_éèà]*'
        t.type = reserved.get(t.value.lower(), 'NOM')
        return t

    # Gère les sauts de ligne et initialise la numérotation des lignes à 1
    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)
        if not hasattr(t.lexer, 'lineno_initialized'):
            t.lexer.lineno = 1
            t.lexer.lineno_initialized = True

    # Gère les erreurs lexicales en levant une exception avec le caractère fautif
    def t_error(t):
        raise SyntaxError(f"Erreur lexicale: '{t.value[0]}' (ligne {t.lineno})")

    # Crée et retourne l'instance du lexer configuré
    lexer = lex()

    # Création du lexer
    lexer = lex()

    # ==================== FIN ANALYSEUR LEXICAL ====================

    # ==================== DEBUT ANALYSEUR  SYNTAXIQUE ====================

    # Table des symboles pour le parser
    symbol_table = {}

    # Définition de la grammaire
    # Règle de grammaire pour la structure principale d'un conseil (peut contenir une ou plusieurs conditions)
    def p_conseil(p):
        '''conseil : condition
                  | conseil condition'''
        if len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = p[1] + [p[2]]
# Règle de grammaire pour les conditions SI/SINON SI avec gestion de la table des symboles

    def p_condition(p):
        '''condition : SI NOM EGAL STRING DPOINTS actions
                    | SI NOM SUPERIEUR NOMBRE DPOINTS actions
                    | SINON SI NOM SUPERIEUR NOMBRE DPOINTS actions'''
        if len(p) == 7:
            if p[2] not in symbol_table:
                symbol_table[p[2]] = 'string' if p[3] == '==' else 'number'
            p[0] = ('CONDITION', p[2], p[3], p[4], p[6])
        else:
            if p[3] not in symbol_table:
                symbol_table[p[3]] = 'number'
            p[0] = ('CONDITION', 'sinon', p[3], p[4], p[5], p[7])

    def verifier_proverbe(texte):
        """
        Vérifie si le proverbe existe exactement et retourne sa version complète

        Args:
            texte (str): Texte du proverbe à vérifier

        Returns:
            str: Version complète du proverbe ou message d'erreur
        """
        # Nettoyer le texte des espaces et guillemets supplémentaires
        texte = texte.strip().strip('"\'')

        # Normaliser l'unicode pour la comparaison
        texte = texte.replace('"', '').replace("'", "")

        # Recherche exacte dans les valeurs de proverbes
        for cle, val in proverbes.items():
            if texte == val:
                return f"{cle}: {val}"

        # Si non trouvé, vérifier si c'est une partie d'un proverbe existant
        for cle, val in proverbes.items():
            if texte in val:
                return f"ATTENTION: Partiel - {cle}: {val}"

        return f"PROVERBE INCONNU: {texte}"

     # Règle de grammaire pour les actions d'affichage (simple ou multiples avec ET)
    def p_actions(p):
        '''actions : AFFICHER PROVERBE
                | actions ET PROVERBE'''
        if len(p) == 3:
            verified = verifier_proverbe(p[2])
            if "ATTENTION:" in verified:
                # Afficher un warning pour les proverbes partiels
                p[0] = [('AFFICHER', verified), ('WARNING', "Le proverbe saisi est partiel")]
            else:
                p[0] = [('AFFICHER', verified)]
        else:
            verified = verifier_proverbe(p[3])
            if "ATTENTION:" in verified:
                p[0] = p[1] + [('AFFICHER', verified), ('WARNING', "Le proverbe saisi est partiel")]
            else:
                p[0] = p[1] + [('AFFICHER', verified)]

     # Gestion des erreurs syntaxiques avec localisation précise
    def p_error(p):
        if p:
            raise SyntaxError(f"Erreur syntaxique ligne {p.lineno}: '{p.value}'")
        else:
            raise SyntaxError("Erreur: Fin de fichier inattendue")

    # Création du parser
    parser = yacc()

    return lexer, parser, symbol_table

# ==================== INTERFACE AMÉLIORÉE ====================


class ImprovedText(scrolledtext.ScrolledText):
    """
    Widget Text amélioré avec des méthodes de formatage prédéfinies

    Hérite de ScrolledText et ajoute des méthodes pour :
    - Afficher des en-têtes, sections, sous-sections
    - Afficher des messages avec différents niveaux (erreur, avertissement, succès)
    - Formater des éléments spécifiques (proverbes, symboles, code)
    """

    def __init__(self, *args, **kwargs):
        """Initialise le widget avec des styles par défaut"""
        kwargs.setdefault('font', ('Arial', 11))
        super().__init__(*args, **kwargs)
        self.configure(
            font=('Arial', 11),
            wrap=tk.WORD,
            undo=True,
            maxundo=-1,
            autoseparators=True,
            bg='#f8f9fa'  # Fond légèrement grisé
        )

        # Configuration des tags pour le style
        self.tag_config('header', foreground='#2c3e50', font=('Arial', 12, 'bold'),
                        spacing3=10, underline=True)
        self.tag_config('section', foreground='#3498db', font=('Arial', 11, 'bold'),
                        spacing1=5, spacing3=5)
        self.tag_config('subsection', foreground='#2980b9', font=('Arial', 11, 'italic'),
                        spacing1=3)
        self.tag_config('success', foreground='#27ae60')
        self.tag_config('error', foreground='#e74c3c')
        self.tag_config('warning', foreground='#f39c12')
        self.tag_config('info', foreground='#7f8c8d')
        self.tag_config('proverb', foreground='#16a085', font=('Arial', 11, 'bold'))
        self.tag_config('symbol', foreground='#8e44ad')
        self.tag_config('token', foreground='#2c3e50', font=('Consolas', 10))
        self.tag_config('code', foreground='#34495e', font=('Consolas', 10))
        self.tag_config('divider', foreground='#bdc3c7')

    def add_header(self, text):
        """Ajoute un en-tête avec soulignement"""
        self.insert(tk.END, f"\n{text.upper()}\n", 'header')
        self.insert(tk.END, "=" * len(text) + "\n", 'header')

    def add_section(self, text):
        """Ajoute une section avec soulignement"""
        self.insert(tk.END, f"\n{text}\n", 'section')
        self.insert(tk.END, "-" * len(text) + "\n", 'section')

    def add_subsection(self, text):
        """Ajoute une sous-section avec puce"""
        self.insert(tk.END, f"\n• {text}\n", 'subsection')

    def add_divider(self):
        """Ajoute une ligne de séparation horizontale"""
        self.insert(tk.END, "\n" + "─" * 80 + "\n", 'divider')

    def add_error(self, message):
        """Ajoute un message d'erreur avec icône"""
        self.insert(tk.END, f"✖ {message}\n", 'error')

    def add_warning(self, message):
        """Ajoute un message d'avertissement avec icône"""
        self.insert(tk.END, f"⚠ {message}\n", 'warning')

    def add_success(self, message):
        """Ajoute un message de succès avec icône"""
        self.insert(tk.END, f"✓ {message}\n", 'success')

    def add_info(self, message):
        """Ajoute un message d'information standard"""
        self.insert(tk.END, f"{message}\n", 'info')

    def add_proverb(self, theme, proverb):
        """Ajoute un proverbe avec formatage spécial"""
        self.insert(tk.END, f"{theme}: ", 'proverb')
        self.insert(tk.END, f"{proverb}\n", 'info')

    def add_symbol(self, var, typ):
        """Ajoute une entrée de la table des symboles avec formatage"""
        self.insert(tk.END, f"{var}: ", 'symbol')
        self.insert(tk.END, f"{typ}\n", 'info')

    def add_token(self, token_type, token_value, lineno):
        """Ajoute un token avec formatage spécial"""
        self.insert(tk.END, f"{token_type:15}", 'token')
        self.insert(tk.END, f"{str(token_value):30}", 'info')
        self.insert(tk.END, f"(ligne {lineno})\n", 'info')

    def add_code(self, code):
        """Ajoute du code avec formatage spécial"""
        self.insert(tk.END, f"{code}\n", 'code')


class AnalyseurApp:
    """
    Application principale avec interface graphique

    Attributs:
        root (tk.Tk): Fenêtre principale
        proverbes (dict): Dictionnaire des proverbes chargés
        lexer: Analyseur lexical
        parser: Analyseur syntaxique
        symbol_table (dict): Table des symboles
    """

    def __init__(self, root):
        """Initialise l'application avec l'interface graphique"""
        self.root = root
        self.root.title("Analyseur de Proverbes Arabes")
        self.root.geometry("1000x800")

        # Charger les proverbes
        init_proverbes_file()
        self.proverbes = charger_proverbes()
        self.lexer, self.parser, self.symbol_table = init_analyzer(self.proverbes)

        # Configuration du style
        self.setup_style()

        # Création des widgets
        self.create_widgets()

        # Configuration de l'autocomplétion
        self.setup_input_autocomplete()

    def setup_style(self):
        """Configure le style de l'interface"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabel', background='#f5f5f5', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), padding=5)
        style.configure('TNotebook', background='#f5f5f5')
        style.configure('TNotebook.Tab', font=('Arial', 10, 'bold'), padding=[10, 5])
        style.configure('TLabelframe', font=('Arial', 10, 'bold'))
        style.configure('TLabelframe.Label', font=('Arial', 10, 'bold'))
        style.map('TButton',
                  foreground=[('active', 'black'), ('!active', 'black')],
                  background=[('active', '#e1e1e1'), ('!active', '#f0f0f0')])

    def setup_input_autocomplete(self):
        """Configure l'autocomplétion pour les proverbes"""
        def autocomplete(event):
            word = self.input_text.get("insert-1c wordstart", "insert-1c wordend")
            if word.startswith('PROVERBE("') and len(word) > 10:
                partial = word[10:]
                matches = [p for p in self.proverbes.values() if p.startswith(partial)]
                if matches:
                    self.input_text.insert("insert", matches[0][len(partial):] + '")')
                    return "break"
            return None

        self.input_text.bind('<Tab>', autocomplete)

    def create_widgets(self):
        """Crée tous les widgets de l'interface"""
        # Notebook (onglets)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Onglet Analyse
        self.analyse_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analyse_frame, text='Analyse')
        self.setup_analyse_tab()

        # Onglet Proverbes
        self.proverbes_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.proverbes_frame, text='Proverbes')
        self.setup_proverbes_tab()

        # Onglet Tests
        self.tests_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.tests_frame, text='Tests')
        self.setup_tests_tab()

    def setup_analyse_tab(self):
        """Configure l'onglet Analyse avec les zones de saisie et résultats"""
        # PanedWindow pour redimensionnement
        main_paned = ttk.PanedWindow(self.analyse_frame, orient=tk.VERTICAL)
        main_paned.pack(expand=True, fill='both', padx=10, pady=10)

        # Zone de saisie (40%)
        input_frame = ttk.LabelFrame(main_paned, text="Entrée - Saisissez votre grammaire")
        self.input_text = ImprovedText(input_frame, wrap=tk.WORD, font=('Arial', 11),
                                       padx=10, pady=10, undo=True)
        self.input_text.pack(expand=True, fill='both', padx=5, pady=5)
        main_paned.add(input_frame, weight=1)

        # Boutons d'analyse
        btn_frame = ttk.Frame(main_paned)
        ttk.Button(btn_frame, text="Analyser (Ctrl+Enter)", command=self.analyser_grammaire).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Effacer", command=self.effacer_resultats).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Exporter résultats", command=self.exporter_resultats).pack(side='left', padx=5)
        main_paned.add(btn_frame)

        # Résultats (60%)
        result_frame = ttk.LabelFrame(main_paned, text="Résultats de l'analyse")
        self.result_text = ImprovedText(result_frame, wrap=tk.WORD, font=('Consolas', 11),
                                        padx=10, pady=10)
        self.result_text.pack(expand=True, fill='both', padx=5, pady=5)
        main_paned.add(result_frame, weight=2)

        # Raccourci clavier
        self.root.bind('<Control-Return>', lambda e: self.analyser_grammaire())

    def setup_proverbes_tab(self):
        """Configure l'onglet Proverbes avec la liste et les options de filtrage"""
        # Frame principale
        main_frame = ttk.Frame(self.proverbes_frame)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Contrôles supérieurs
        ctrl_frame = ttk.Frame(main_frame)
        ctrl_frame.pack(fill='x', pady=(0, 10))

        # Boutons de gauche
        left_btn_frame = ttk.Frame(ctrl_frame)
        left_btn_frame.pack(side='left')

        ttk.Button(left_btn_frame, text="Actualiser", command=self.actualiser_proverbes).pack(side='left', padx=5)
        ttk.Button(left_btn_frame, text="Ouvrir fichier",
                   command=self.ouvrir_fichier_proverbes).pack(side='left', padx=5)
        ttk.Button(left_btn_frame, text="Exporter liste", command=self.exporter_proverbes).pack(side='left', padx=5)

        # Options d'organisation
        org_frame = ttk.Frame(ctrl_frame)
        org_frame.pack(side='left', padx=20)

        ttk.Label(org_frame, text="Organiser par:").pack(side='left')
        self.sort_var = tk.StringVar(value='theme')
        ttk.Radiobutton(org_frame, text="Thème", variable=self.sort_var,
                        value='theme', command=self.afficher_proverbes).pack(side='left', padx=5)
        ttk.Radiobutton(org_frame, text="Valeur", variable=self.sort_var,
                        value='valeur', command=self.afficher_proverbes).pack(side='left', padx=5)

        # Options de filtre
        filter_frame = ttk.Frame(ctrl_frame)
        filter_frame.pack(side='left')

        ttk.Label(filter_frame, text="Filtrer par catégorie:").pack(side='left')
        self.filter_var = tk.StringVar(value='tous')
        categories = ['tous'] + sorted(list(set([k.split('_')[0] for k in self.proverbes.keys() if '_' in k])))
        ttk.OptionMenu(filter_frame, self.filter_var, *categories,
                       command=lambda _: self.filtrer_proverbes()).pack(side='left', padx=5)

        # Barre de recherche à droite
        search_frame = ttk.Frame(ctrl_frame)
        search_frame.pack(side='right', padx=5)

        ttk.Label(search_frame, text="Rechercher:").pack(side='left')
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=25)
        search_entry.pack(side='left', padx=5)
        search_entry.bind('<KeyRelease>', lambda e: self.filtrer_proverbes())

        # Liste des proverbes avec cadre défilant
        list_frame = ttk.LabelFrame(main_frame, text="Liste des proverbes disponibles")
        list_frame.pack(expand=True, fill='both')

        # Création d'un canvas avec scrollbar
        canvas = tk.Canvas(list_frame, bg='white')
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.proverbes_list = ImprovedText(scrollable_frame, wrap=tk.WORD,
                                           padx=10, pady=10, height=20)
        self.proverbes_list.pack(expand=True, fill='both')

        self.afficher_proverbes()

    def afficher_proverbes(self):
        """Affiche la liste des proverbes organisée selon les options choisies"""
        self.proverbes_list.delete(1.0, tk.END)

        # Récupérer les options d'organisation
        sort_by = self.sort_var.get()
        filter_by = self.filter_var.get()
        search_term = self.search_var.get().lower()

        # Préparer la liste des proverbes
        proverbes_list = []

        for theme, proverbe in self.proverbes.items():
            # Filtrer par catégorie
            if filter_by != 'tous':
                theme_parts = theme.split('_')
                if len(theme_parts) > 1:
                    categorie = theme_parts[0]
                    if categorie.lower() != filter_by.lower():
                        continue

            # Filtrer par terme de recherche
            if search_term and (search_term not in theme.lower() and
                                search_term not in proverbe.lower()):
                continue

            proverbes_list.append((theme, proverbe))

        # Trier selon l'option choisie
        if sort_by == 'theme':
            proverbes_list.sort(key=lambda x: x[0])
        else:  # 'valeur'
            proverbes_list.sort(key=lambda x: x[1])

        # Afficher les proverbes
        current_category = None
        for theme, proverbe in proverbes_list:
            # Afficher l'en-tête de catégorie si on filtre par 'tous'
            if filter_by == 'tous':
                theme_parts = theme.split('_')
                if len(theme_parts) > 1:
                    categorie = theme_parts[0]
                    if categorie != current_category:
                        current_category = categorie
                        self.proverbes_list.insert(tk.END, f"\n=== {current_category.upper()} ===\n", 'header')

            self.proverbes_list.insert(tk.END, f"{theme}:\n", 'proverb')
            self.proverbes_list.insert(tk.END, f"{proverbe}\n\n", 'info')

    def filtrer_proverbes(self):
        """Filtre les proverbes selon les critères de recherche et d'organisation"""
        self.afficher_proverbes()

    def setup_tests_tab(self):
        """Configure l'onglet des tests avec les boutons appropriés"""
        # Frame principale
        main_frame = ttk.Frame(self.tests_frame)
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Tests prédéfinis
        test_frame = ttk.LabelFrame(main_frame, text="Tests prédéfinis")
        test_frame.pack(fill='x', pady=(0, 10))

        # Canvas avec scrollbar
        canvas = tk.Canvas(test_frame)
        scrollbar = ttk.Scrollbar(test_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.test_var = tk.StringVar()

        # Tests valides (8 tests)
        valid_tests = [
            ("Test conseil simple (valide)", """si humeur == "triste":
    afficher PROVERBE("أسمع كلام اللي يبكيك وماتسمعش كلام اللي يضحكك")"""),
            ("Test condition numérique (valide)", """si age > 60:
    afficher PROVERBE("إسأل مجرب ولا تسأل طبيب")"""),
            ("Test santé (valide)", """si sante == "fragile":
    afficher PROVERBE("الصحة تاج على رؤوس الأصحاء")"""),
            ("Test finances (valide)", """si richesse == "abondante":
    afficher PROVERBE("اللي عندو ما يموتش")"""),
            ("Test météo (valide)", """si meteo == "secheresse":
    afficher PROVERBE("اللي ما عندوش مطر، يستنا الندى")"""),
            ("Test éducation (valide)", """si enfant == "desobeissant":
    afficher PROVERBE("اللي يربّي العود يربّي الحصاد")"""),
            ("Test conseils combinés (valide)", """si besoin == "conseil":
    afficher PROVERBE("أعمل الخير وارمي في البحر")
    et PROVERBE("شد مشومك لا يجيك ما اشوم")"""),
            ("Test conditions mixtes (valide)", """si humeur == "joyeuse":
    afficher PROVERBE("العقل السليم في الجسم السليم")
sinon si age > 30:
    afficher PROVERBE("الوقت شيخ")""")
        ]

        # Tests non valides lexicaux (2 tests)
        lexical_invalid_tests = [
            ("Test lexical invalide 1 (caractère spécial)", """si humeur@ == "triste":
    afficher PROVERBE("أسمع كلام اللي يبكيك وماتسمعش كلام اللي يضحكك")"""),
            ("Test lexical invalide 2 (nombre mal formé)", """si age > 60ans:
    afficher PROVERBE("الكبير كبير ولو طار")""")
        ]

        # Tests non valides syntaxiques (2 tests)
        syntax_invalid_tests = [
            ("Test syntaxique invalide 1 (opérateur manquant)", """si humeur "triste":
    afficher PROVERBE("أسمع كلام اللي يبكيك وماتسمعش كلام اللي يضحكك")"""),
            ("Test syntaxique invalide 2 (structure incorrecte)", """si age > 60
    afficher PROVERBE("إسأل مجرب ولا تسأل طبيب")""")
        ]

        # Tests non valides sémantiques (2 tests)
        semantic_invalid_tests = [
            ("Test sémantique invalide 1 (proverbe inapproprié)", """si humeur == "triste":
    afficher PROVERBE("اللي عندو ما يموتش")"""),
            ("Test sémantique invalide 2 (type incompatible)", """si age == "soixante":
    afficher PROVERBE("الكبير كبير ولو طار")""")
        ]

        # Ajout de tous les tests
        tests = valid_tests + lexical_invalid_tests + syntax_invalid_tests + semantic_invalid_tests

        # Création des boutons radio pour chaque test
        for text, code in tests:
            ttk.Radiobutton(scrollable_frame, text=text, variable=self.test_var,
                            value=code).pack(anchor='w', padx=5, pady=2)

        # Boutons de test
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=5)

        ttk.Button(btn_frame, text="Charger test", command=self.charger_test).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Tests sémantiques", command=self.run_semantic_tests).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Effacer", command=self.effacer_tout).pack(side='left', padx=5)

    def run_semantic_tests(self):
        """Exécute une batterie de tests sémantiques avec 2 tests non valides de chaque type"""
        self.result_text.delete(1.0, tk.END)
        self.result_text.add_section("TESTS COMPLETS (12 tests)")
        self.result_text.add_info(
            "Incluant 8 tests valides, 2 non valides lexicaux, 2 non valides syntaxiques et 2 non valides sémantiques")

        # Tests valides
        self.result_text.add_subsection("\nTESTS VALIDES (8)")
        valid_tests = [
            {
                "name": "Test conseil simple",
                "code": """si humeur == "triste":
    afficher PROVERBE("أسمع كلام اللي يبكيك وماتسمعش كلام اللي يضحكك")""",
                "expected": {
                    "symbols": {"humeur": "string"},
                    "proverbs": ["CONSEIL"],
                    "errors": 0,
                    "warnings": 0
                }
            },
            {
                "name": "Test condition numérique",
                "code": """si age > 60:
    afficher PROVERBE("إسأل مجرب ولا تسأل طبيب")""",
                "expected": {
                    "symbols": {"age": "number"},
                    "proverbs": ["SAGESSE"],
                    "errors": 0,
                    "warnings": 0
                }
            },
            {
                "name": "Test santé",
                "code": """si sante == "fragile":
    afficher PROVERBE("الصحة تاج على رؤوس الأصحاء")""",
                "expected": {
                    "symbols": {"sante": "string"},
                    "proverbs": ["SANTE"],
                    "errors": 0,
                    "warnings": 0
                }
            },
            {
                "name": "Test finances",
                "code": """si richesse == "abondante":
    afficher PROVERBE("اللي عندو ما يموتش")""",
                "expected": {
                    "symbols": {"richesse": "string"},
                    "proverbs": ["RICHESSE"],
                    "errors": 0,
                    "warnings": 0
                }
            },
            {
                "name": "Test météo",
                "code": """si meteo == "secheresse":
    afficher PROVERBE("اللي ما عندوش مطر، يستنا الندى")""",
                "expected": {
                    "symbols": {"meteo": "string"},
                    "proverbs": ["METEO"],
                    "errors": 0,
                    "warnings": 0
                }
            },
            {
                "name": "Test éducation",
                "code": """si enfant == "desobeissant":
    afficher PROVERBE("اللي يربّي العود يربّي الحصاد")""",
                "expected": {
                    "symbols": {"enfant": "string"},
                    "proverbs": ["EDUCATION"],
                    "errors": 0,
                    "warnings": 0
                }
            },
            {
                "name": "Test conseils combinés",
                "code": """si besoin == "conseil":
    afficher PROVERBE("أعمل الخير وارمي في البحر")
    et PROVERBE("شد مشومك لا يجيك ما اشوم")""",
                "expected": {
                    "symbols": {"besoin": "string"},
                    "proverbs": ["GENEROSITE", "PREVENTION"],
                    "errors": 0,
                    "warnings": 0
                }
            },
            {
                "name": "Test conditions mixtes",
                "code": """si humeur == "joyeuse":
    afficher PROVERBE("العقل السليم في الجسم السليم")
sinon si age > 30:
    afficher PROVERBE("الوقت شيخ")""",
                "expected": {
                    "symbols": {"humeur": "string", "age": "number"},
                    "proverbs": ["BIENETRE", "EXPERIENCE"],
                    "errors": 0,
                    "warnings": 0
                }
            }
        ]

        # Tests non valides lexicaux
        self.result_text.add_subsection("\nTESTS NON VALIDES LEXICAUX (2)")
        lexical_invalid_tests = [
            {
                "name": "Test lexical invalide 1 (caractère spécial)",
                "code": """si humeur@ == "triste":
    afficher PROVERBE("أسمع كلام اللي يبكيك وماتسمعش كلام اللي يضحكك")""",
                "expected": {
                    "errors": 1,  # Doit détecter l'erreur lexicale
                    "lexical_error": True
                }
            },
            {
                "name": "Test lexical invalide 2 (nombre mal formé)",
                "code": """si age > 60ans:
    afficher PROVERBE("الكبير كبير ولو طار")""",
                "expected": {
                    "errors": 1,
                    "lexical_error": True
                }
            }
        ]

        # Tests non valides syntaxiques
        self.result_text.add_subsection("\nTESTS NON VALIDES SYNTAXIQUES (2)")
        syntax_invalid_tests = [
            {
                "name": "Test syntaxique invalide 1 (opérateur manquant)",
                "code": """si humeur "triste":
    afficher PROVERBE("أسمع كلام اللي يبكيك وماتسمعش كلام اللي يضحكك")""",
                "expected": {
                    "errors": 1,  # Doit détecter l'erreur syntaxique
                    "syntax_error": True
                }
            },
            {
                "name": "Test syntaxique invalide 2 (structure incorrecte)",
                "code": """si age > 60
    afficher PROVERBE("إسأل مجرب ولا تسأل طبيب")""",
                "expected": {
                    "errors": 1,
                    "syntax_error": True
                }
            }
        ]

        # Tests non valides sémantiques
        self.result_text.add_subsection("\nTESTS NON VALIDES SEMANTIQUES (2)")
        semantic_invalid_tests = [
            {
                "name": "Test sémantique invalide 1 (proverbe inapproprié)",
                "code": """si humeur == "triste":
    afficher PROVERBE("اللي عندو ما يموتش")""",
                "expected": {
                    "symbols": {"humeur": "string"},
                    "proverbs": ["RICHESSE"],
                    "errors": 1,  # Doit détecter l'incohérence sémantique
                    "warnings": 0
                }
            },
            {
                "name": "Test sémantique invalide 2 (type incompatible)",
                "code": """si age == "soixante":
    afficher PROVERBE("الكبير كبير ولو طار")""",
                "expected": {
                    "symbols": {"age": "string"},
                    "proverbs": ["AGE"],
                    "errors": 1,
                    "warnings": 0
                }
            }
        ]

        # Exécution de tous les tests
        all_tests = valid_tests + lexical_invalid_tests + syntax_invalid_tests + semantic_invalid_tests

        for test in all_tests:
            self.run_single_test(test)

    def run_single_test(self, test):
        """Exécute un test individuel et affiche les résultats"""
        self.result_text.add_info(f"\nTest: {test['name']}")
        self.result_text.add_info(f"Code:\n{test['code']}")

        try:
            # Réinitialisation
            self.symbol_table.clear()
            analyzer = SemanticAnalyzer(self.proverbes)

            # Analyse
            result = self.parser.parse(test['code'])

            # Vérification sémantique
            if isinstance(result, list):
                for condition in result:
                    analyzer.check_condition(condition)

            # Vérification des résultats
            test_passed = True
            details = []

            # 1. Vérification table des symboles
            if 'symbols' in test['expected']:
                self.result_text.add_info("\nSymboles attendus vs obtenus:")
                for var, typ in test['expected']['symbols'].items():
                    if var in analyzer.symbol_table:
                        if analyzer.symbol_table[var] == typ:
                            details.append(f"{var}: {typ} (OK)")
                        else:
                            details.append(f"{var}: attendu {typ}, obtenu {analyzer.symbol_table.get(var)}")
                            test_passed = False
                    else:
                        details.append(f"{var}: non déclaré")
                        test_passed = False

                for detail in details:
                    if "OK)" in detail:
                        self.result_text.add_success(detail)
                    else:
                        self.result_text.add_error(detail)

            # 2. Vérification proverbes utilisés
            if 'proverbs' in test['expected']:
                self.result_text.add_info("\nProverbes attendus vs obtenus:")
                expected_proverbs = set(test['expected']['proverbs'])
                used_proverbs = analyzer.used_proverbs
                details = []

                for proverb in expected_proverbs:
                    if proverb in used_proverbs:
                        details.append(f"{proverb} (OK)")
                    else:
                        details.append(f"{proverb} (manquant)")
                        test_passed = False

                for proverb in used_proverbs:
                    if proverb not in expected_proverbs:
                        details.append(f"{proverb} (inattendu)")
                        test_passed = False

                for detail in details:
                    if "OK)" in detail:
                        self.result_text.add_success(detail)
                    elif "manquant" in detail:
                        self.result_text.add_error(detail)
                    else:
                        self.result_text.add_warning(detail)

            # 3. Vérification erreurs/avertissements
            expected_errors = test['expected'].get('errors', 0)
            expected_warnings = test['expected'].get('warnings', 0)

            if len(analyzer.errors) != expected_errors:
                test_passed = False
                self.result_text.add_error(
                    f"\nErreurs: attendu {expected_errors}, obtenu {len(analyzer.errors)}"
                )

            if len(analyzer.warnings) != expected_warnings:
                test_passed = False
                self.result_text.add_error(
                    f"\nAvertissements: attendu {expected_warnings}, obtenu {len(analyzer.warnings)}"
                )

            if analyzer.errors:
                self.result_text.add_subsection("Erreurs détectées:")
                for err in analyzer.errors:
                    self.result_text.add_error(f"- {err}")

            if analyzer.warnings:
                self.result_text.add_subsection("Avertissements détectés:")
                for warn in analyzer.warnings:
                    self.result_text.add_warning(f"- {warn}")

            # Résumé du test
            if test['expected'].get('lexical_error', False) or test['expected'].get('syntax_error', False):
                if analyzer.errors:
                    self.result_text.add_success("\nTEST RÉUSSI! (Erreur détectée comme attendue)")
                else:
                    self.result_text.add_error("\nTEST ÉCHOUÉ! (Erreur non détectée)")
            elif test_passed:
                self.result_text.add_success("\nTEST RÉUSSI!")
            else:
                self.result_text.add_error("\nTEST ÉCHOUÉ!")

            self.result_text.insert(tk.END, "\n" + "=" * 80 + "\n")

        except Exception as e:
            if test['expected'].get('lexical_error', False) or test['expected'].get('syntax_error', False):
                self.result_text.add_success(f"\nErreur détectée comme attendue: {str(e)}")
            else:
                self.result_text.add_error(f"\nErreur d'exécution: {str(e)}")
            self.result_text.insert(tk.END, "\n" + "=" * 80 + "\n")

    def actualiser_proverbes(self):
        """Recharge les proverbes depuis le fichier"""
        self.proverbes = charger_proverbes()
        self.afficher_proverbes()
        messagebox.showinfo("Info", "Proverbes actualisés avec succès!")

    def ouvrir_fichier_proverbes(self):
        """Ouvre le fichier proverbes.txt dans l'éditeur par défaut"""
        try:
            os.startfile(PROVERBES_FILE)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier: {str(e)}")

    def exporter_proverbes(self):
        """Exporte la liste des proverbes dans un fichier"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
            title="Exporter les proverbes"
        )
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    for theme, proverbe in sorted(self.proverbes.items()):
                        f.write(f"{theme}: {proverbe}\n\n")
                messagebox.showinfo("Succès", "Proverbes exportés avec succès!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")

    def exporter_resultats(self):
        """Exporte les résultats d'analyse dans un fichier"""
        if not self.result_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Attention", "Aucun résultat à exporter")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")],
            title="Exporter les résultats"
        )
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(self.result_text.get(1.0, tk.END))
                messagebox.showinfo("Succès", "Résultats exportés avec succès!")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")

    def charger_test(self):
        """Charge un test prédéfini dans la zone de saisie"""
        test_code = self.test_var.get()
        if test_code:
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(tk.END, test_code)
            self.notebook.select(0)  # Basculer vers l'onglet Analyse
            messagebox.showinfo("Test chargé", "Le test a été chargé dans l'onglet Analyse")

    def effacer_tout(self):
        """Efface toutes les zones de texte"""
        self.input_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.test_var.set("")

    def effacer_resultats(self):
        """Efface les zones de saisie et de résultats"""
        self.input_text.delete(1.0, tk.END)
        self.result_text.delete(1.0, tk.END)

    def analyser_grammaire(self):
        """Analyse complète avec vérification sémantique et gestion des proverbes partiels"""
        code = self.input_text.get(1.0, tk.END).strip()
        if not code:
            messagebox.showwarning("Attention", "Veuillez saisir une grammaire à analyser")
            return

        try:
            # Réinitialisation
            self.symbol_table.clear()
            self.result_text.delete(1.0, tk.END)
            analyzer = SemanticAnalyzer(self.proverbes)

            # Analyse lexicale
            self.result_text.add_header("Analyse Lexicale")
            self.lexer.input(code)
            tokens = list(self.lexer)

            self.result_text.add_section("Tokens détectés")
            for tok in tokens:
                self.result_text.add_token(tok.type, tok.value, tok.lineno)

            # Analyse syntaxique
            self.result_text.add_header("Analyse Syntaxique")
            result = self.parser.parse(code)

            self.result_text.add_section("Arbre syntaxique généré")
            self.result_text.insert(tk.END, pformat(result, width=80, indent=2), 'code')

            # Analyse sémantique
            self.result_text.add_header("Analyse Sémantique")
            if isinstance(result, list):
                for condition in result:
                    analyzer.check_condition(condition)
                    # Vérification des avertissements sur les proverbes partiels
                    actions = condition[4] if len(condition) == 5 else condition[6]
                    for action in actions:
                        if isinstance(action, tuple) and action[0] == 'WARNING':
                            analyzer.warnings.append(action[1])

            # Affichage des résultats sémantiques
            self.result_text.add_section("Table des symboles")
            if analyzer.symbol_table:
                for var, typ in analyzer.symbol_table.items():
                    self.result_text.add_symbol(var, typ)
            else:
                self.result_text.add_info("Aucune variable déclarée")

            # Erreurs et avertissements
            self.result_text.add_section("Vérifications sémantiques")
            if analyzer.errors or analyzer.warnings:
                if analyzer.errors:
                    self.result_text.add_subsection("Erreurs détectées")
                    for err in analyzer.errors:
                        self.result_text.add_error(err)
                if analyzer.warnings:
                    self.result_text.add_subsection("Avertissements détectés")
                    for warn in analyzer.warnings:
                        self.result_text.add_warning(warn)
            else:
                self.result_text.add_success("Aucune erreur sémantique détectée")

            # Proverbes utilisés
            self.result_text.add_header("Proverbes Utilisés")
            if analyzer.used_proverbs:
                for theme in sorted(analyzer.used_proverbs):
                    self.result_text.add_proverb(theme, self.proverbes[theme])
            else:
                self.result_text.add_info("Aucun proverbe valide utilisé dans ce code")

            self.result_text.add_divider()
            messagebox.showinfo("Succès", "Analyse terminée avec succès!")

        except Exception as e:
            self.result_text.add_header("Erreur d'analyse")
            self.result_text.add_error(str(e))
            self.result_text.add_divider()
            messagebox.showerror("Erreur", f"Erreur d'analyse:\n{str(e)}")

# ==================== LANCEMENT DE L'APPLICATION ====================


if __name__ == "__main__":
    root = tk.Tk()
    app = AnalyseurApp(root)
    root.mainloop()
