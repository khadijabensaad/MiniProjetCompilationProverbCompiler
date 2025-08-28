class SemanticAnalyzer:
    def __init__(self, proverbes):
        self.errors = []
        self.warnings = []
        self.symbol_table = {}
        self.used_proverbs = set()
        self.proverbes = proverbes
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
        """Retourne les thèmes attendus pour une variable et valeur donnée"""
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
        """Vérifie la cohérence sémantique entre condition et proverbe"""
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
        """Analyse sémantique d'une condition avec vérification renforcée"""
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
        """Analyse sémantique des actions avec vérification des proverbes"""
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