# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
from code_intermediaire import IntermediateCodeGenerator  # Importez votre classe ici

class TargetCodeGenerator:
    def __init__(self):
        self.reset_generator()

    def reset_generator(self):
        self.asm_output = []
        self.label_count = 0
        self.temp_count = 0
        self.string_table = {}
        self.var_offset = 8  # Offset de base (ebp+8)
        self.current_scope = "global"
        self.functions = {}

    def generate_asm(self, intermediate_code):
        self.reset_generator()
        
        # En-tête du programme
        self._emit_header()
        
        # Traduction ligne par ligne
        for line in intermediate_code:
            if not line.strip():
                continue
            self._translate(line.strip())
        
        # Pied de page
        self._emit_footer()
        
        # Ajout des données constantes
        self._emit_string_table()
        
        return "\n".join(self.asm_output)

    def _emit_header(self):
        self.asm_output.extend([
            "; Généré automatiquement par le compilateur",
            "section .text",
            "global _start",
            "extern printf, exit",
            "",
            "_start:",
            "    push ebp",
            "    mov ebp, esp",
            f"    sub esp, {self.var_offset - 8}  ; Allocation variables"
        ])

    def _emit_footer(self):
        self.asm_output.extend([
            "    mov esp, ebp",
            "    pop ebp",
            "    mov eax, 1      ; sys_exit",
            "    xor ebx, ebx    ; status 0",
            "    int 0x80"
        ])

    def _emit_string_table(self):
        if self.string_table:
            self.asm_output.append("\nsection .data")
            for label, text in self.string_table.items():
                self.asm_output.append(f'{label}: db "{text}", 0')

    def _translate(self, line):
        # Détection du type d'instruction
        if "=" in line:
            self._handle_assignment(line)
        elif line.startswith("iffalse"):
            self._handle_cond_jump(line)
        elif line.startswith("PROVERBE"):
            self._handle_print(line)
        elif line.startswith("LABEL"):
            self._handle_label(line)
        elif line.startswith("GOTO"):
            self._handle_jump(line)
        else:
            self.asm_output.append(f"; Instruction non reconnue: {line}")

    def _handle_assignment(self, line):
        left, right = line.split("=", 1)
        left = left.strip()
        right = right.strip()

        if ">" in right:
            self._gen_comparison(left, right, "setg")
        elif "<" in right:
            self._gen_comparison(left, right, "setl")
        elif "==" in right:
            self._gen_comparison(left, right, "sete")
        else:
            self.asm_output.extend([
                f"    mov eax, {right}",
                f"    mov [ebp-{self._get_offset(left)}], eax"
            ])

    def _gen_comparison(self, dest, expr, set_op):
        a, b = expr.split(set_op[3:], 1)
        a = a.strip()
        b = b.strip()
        
        self.asm_output.extend([
            f"    mov eax, [ebp-{self._get_offset(a)}]",
            f"    cmp eax, {b}",
            f"    {set_op} al",
            "    movzx eax, al",
            f"    mov [ebp-{self._get_offset(dest)}], eax"
        ])

    def _handle_cond_jump(self, line):
        _, var, _, label = line.split()
        self.asm_output.extend([
            f"    mov eax, [ebp-{self._get_offset(var)}]",
            "    cmp eax, 0",
            f"    je {label}"
        ])

    def _handle_print(self, line):
        text = line.split('"')[1]
        label = self._get_string_label(text)
        self.asm_output.extend([
            f"    push {label}",
            "    push printf_format",
            "    call printf",
            "    add esp, 8"
        ])

    def _handle_label(self, line):
        label = line.split()[1]
        self.asm_output.append(f"{label}:")

    def _handle_jump(self, line):
        label = line.split()[1]
        self.asm_output.append(f"    jmp {label}")

    def _get_offset(self, var):
        """Gère l'allocation mémoire des variables"""
        if var.startswith("t"):
            idx = int(var[1:])
            offset = 4 * (idx + 2)  # t0 -> ebp-8, t1 -> ebp-12, etc.
            if offset >= self.var_offset:
                self.var_offset = offset + 4
            return offset
        return 0

    def _get_string_label(self, text):
        """Gère les chaînes constantes"""
        if text not in self.string_table.values():
            label = f"str_{len(self.string_table)}"
            self.string_table[label] = text
            return label
        return next(k for k, v in self.string_table.items() if v == text)


class CodeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Générateur de Code Intermédiaire")
        self.root.geometry("1000x700")
        self.setup_ui()
        self.generator = IntermediateCodeGenerator()

    def setup_ui(self):
        # Configuration du style
        style = ttk.Style()
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))

        # Frame principale
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Section d'entrée AST
        input_frame = ttk.LabelFrame(main_frame, text="Entrée AST", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        self.ast_input = scrolledtext.ScrolledText(input_frame, height=10, font=('Consolas', 10))
        self.ast_input.pack(fill=tk.X)
        self.ast_input.insert(tk.END, """[
    ('CONDITION', 'age', '>', 18, [
        ('AFFICHER', 'PROVERBE("اللّي فات مات")'),
        ('AFFICHER', 'PROVERBE("اللّي يحبّ يبكي")')
    ]),
    ('CONDITION', 'sinon', 'humeur', '==', '"حزين"', [
        ('AFFICHER', 'PROVERBE("طاح البير ومات عمّارُه")')
    ])
]""")

        # Boutons de contrôle
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(button_frame, text="Générer le Code", command=self.generate_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Optimiser", command=self.optimize_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Effacer Tout", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exporter", command=self.export_code).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Générer ASM", command=self.generate_asm).pack(side=tk.LEFT, padx=5)

        # Section de sortie
        output_frame = ttk.LabelFrame(main_frame, text="Code Intermédiaire", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.code_output = scrolledtext.ScrolledText(output_frame, height=15, font=('Consolas', 10))
        self.code_output.pack(fill=tk.BOTH, expand=True)

        # Section d'optimisation
        opt_frame = ttk.LabelFrame(main_frame, text="Optimisations", padding="10")
        opt_frame.pack(fill=tk.BOTH, pady=5)

        self.opt_output = scrolledtext.ScrolledText(opt_frame, height=5, font=('Consolas', 10))
        self.opt_output.pack(fill=tk.BOTH)

        # Status bar
        self.status = ttk.Label(main_frame, text="Prêt", relief=tk.SUNKEN)
        self.status.pack(fill=tk.X, pady=(5,0))

    def generate_code(self):
        try:
            ast_input = self.ast_input.get("1.0", tk.END)
            ast = eval(ast_input)  # Attention: eval peut être dangereux dans une vraie application

            self.generator = IntermediateCodeGenerator()
            code = self.generator.generate(ast)

            self.code_output.delete("1.0", tk.END)
            for instruction in code:
                self.code_output.insert(tk.END, instruction + "\n")

            self.status["text"] = "Code généré avec succès"
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération:\n{str(e)}")
            self.status["text"] = "Erreur lors de la génération"

    def optimize_code(self):
        try:
            if not hasattr(self.generator, 'code'):
                messagebox.showwarning("Avertissement", "Générez d'abord le code avant d'optimiser")
                return

            self.generator.optimize_code()

            self.opt_output.delete("1.0", tk.END)
            for instruction in self.generator.code:
                self.opt_output.insert(tk.END, instruction + "\n")

            self.status["text"] = "Code optimisé avec succès"
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'optimisation:\n{str(e)}")
            self.status["text"] = "Erreur lors de l'optimisation"

    def generate_asm(self):
        try:
            intermediate_code = self.code_output.get("1.0", tk.END).splitlines()
            generator = TargetCodeGenerator()
            asm_code = generator.generate_asm(intermediate_code)

            # Afficher dans une nouvelle fenêtre
            asm_window = tk.Toplevel()
            asm_text = scrolledtext.ScrolledText(asm_window, font=('Consolas', 10))
            asm_text.insert(tk.END, asm_code)
            asm_text.pack(fill=tk.BOTH, expand=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la génération ASM:\n{str(e)}")

    def clear_all(self):
        self.ast_input.delete("1.0", tk.END)
        self.code_output.delete("1.0", tk.END)
        self.opt_output.delete("1.0", tk.END)
        self.status["text"] = "Champs effacés"

    def export_code(self):
        try:
            # Générer d'abord le code ASM
            intermediate_code = self.code_output.get("1.0", tk.END).splitlines()
            generator = TargetCodeGenerator()
            asm_code = generator.generate_asm(intermediate_code)
        
            if not asm_code.strip():
                messagebox.showwarning("Avertissement", "Aucun code ASM à exporter")
                return
            
        # Demander le fichier de destination
            file_path = filedialog.asksaveasfilename(
                defaultextension=".asm",
                filetypes=[
                    ("Fichiers Assembleur", "*.asm"),
                    ("Tous les fichiers", "*.*")
                ]
            )
        
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(asm_code)
                self.status["text"] = f"Code ASM exporté vers {file_path}"
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'export ASM:\n{str(e)}")
            self.status["text"] = "Erreur lors de l'export ASM"


if __name__ == "__main__":
    root = tk.Tk()
    app = CodeGeneratorApp(root)
    root.mainloop()
