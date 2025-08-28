# -*- coding: utf-8 -*-
# ============ GÉNÉRATEUR DE CODE INTERMÉDIAIRE ============

class IntermediateCodeGenerator:
    def __init__(self):
        self.temp_counter = 0  # Compteur pour les variables temporaires
        self.label_counter = 0  # Compteur pour les labels
        self.code = []         # Liste des instructions générées
        self.current_ctx = []  # Contexte pour les conditions imbriquées

    def new_temp(self):
        """Génère un nouveau nom de variable temporaire"""
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def new_label(self):
        """Génère un nouveau label"""
        self.label_counter += 1
        return f"L{self.label_counter}"

    def generate(self, ast):
        """Point d'entrée principal pour la génération de code"""
        self.code = []
        self._generate_node(ast)
        return self.code

    def _generate_node(self, node):
        """Dispatch vers la méthode de génération appropriée"""
        if not node:
            return

        node_type = node[0]
        
        if node_type == 'CONDITION':
            self._generate_condition(node)
        elif node_type == 'AFFICHER':
            self._generate_print(node)
        elif isinstance(node, list):
            for n in node:
                self._generate_node(n)

    def _generate_condition(self, node):
        """Génère le code pour une structure conditionnelle"""
        if len(node) == 5:  # SI condition
            _, var, op, val, actions = node
            end_label = self.new_label()
            
            # Génération de la comparaison
            temp = self.new_temp()
            self.code.append(f"{temp} = {var} {op} {val}")
            self.code.append(f"ifFalse {temp} goto {end_label}")
            
            # Génération des actions
            self._generate_node(actions)
            self.code.append(f"label {end_label}")
            
        elif len(node) == 6:  # SINON SI condition
            _, _, var, op, val, actions = node
            end_label = self.current_ctx[-1]['end_label'] if self.current_ctx else self.new_label()
            
            temp = self.new_temp()
            self.code.append(f"{temp} = {var} {op} {val}")
            self.code.append(f"ifFalse {temp} goto {end_label}")
            
            self._generate_node(actions)

    def _generate_print(self, node):
        """Génère le code pour l'affichage d'un proverbe"""
        _, proverbe = node
        temp = self.new_temp()
        self.code.append(f"{temp} = allouer_tampon(256)")
        self.code.append(f"stocke_chaine {temp}, \"{proverbe}\"")
        self.code.append(f"appel_systeme afficher, {temp}")

    def optimize_code(self):
        """Applique des optimisations basiques au code généré"""
        optimized = []
        i = 0
        while i < len(self.code):
            instr = self.code[i]
            
            # Élimination des redondances
            if i+1 < len(self.code) and "ifFalse" in instr and "goto" in self.code[i+1]:
                target = instr.split()[-1]
                next_target = self.code[i+1].split()[-1]
                if target == next_target:
                    optimized.append(instr)
                    i += 1  # Saute l'instruction redondante
                    continue
                    
            optimized.append(instr)
            i += 1
            
        self.code = optimized

# ============ UTILISATION ============

if __name__ == "__main__":
    # Exemple d'AST issu de votre analyseur
    exemple_ast = [
        ('CONDITION', 
         'age', 
         '>', 
         18, 
         [
             ('AFFICHER', 'PROVERBE("اللّي فات مات")'),
             ('AFFICHER', 'PROVERBE("اللّي يحبّ يبكي")')
         ]),
        ('CONDITION',
         'sinon',
         'humeur',
         '==',
         '"حزين"',
         [
             ('AFFICHER', 'PROVERBE("طاح البير ومات عمّارُه")')
         ])
    ]

    # Génération du code
    generator = IntermediateCodeGenerator()
    intermediate_code = generator.generate(exemple_ast)
    
    print("\n=== CODE INTERMÉDIAIRE BRUT ===")
    for instruction in intermediate_code:
        print(instruction)

    # Optimisation
    generator.optimize_code()
    
    print("\n=== CODE OPTIMISÉ ===")
    for instruction in generator.code:
        print(instruction)