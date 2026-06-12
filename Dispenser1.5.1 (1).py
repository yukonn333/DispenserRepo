import customtkinter as ctk
import sqlite3
from datetime import datetime
from plyer import notification

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

class Dispenserrr(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title('Dispenser 1.5')
        self.geometry('900x700')
        self.init_db()

        self.agendamentos = []
        self.editando_id = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tab_cadastro = self.tabview.add("Cadastro")
        self.tab_fichas = self.tabview.add("Agendamentos")

        self.setup_aba_cadastro()
        self.setup_aba_fichas()

        self.frame_historico = ctk.CTkFrame(self, width=250)
        self.frame_historico.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        ctk.CTkLabel(self.frame_historico, text="Histórico de Entregas", font=("arial", 16, "bold")).pack(pady=10)
        self.txt_historico = ctk.CTkTextbox(self.frame_historico, width=200, state="disabled")
        self.txt_historico.pack(padx=10, pady=10, fill="both", expand=True)

        self.carregar_agendamentos_db()
        self.verificar_horario()

    def setup_aba_cadastro(self):
        self.label_nome = ctk.CTkLabel(self.tab_cadastro, text="Nome do Animal:", font=("arial", 16))
        self.label_nome.pack(pady=(20, 0))
        self.entry_nome = ctk.CTkEntry(self.tab_cadastro, placeholder_text="Ex: Fulano", width=300)
        self.entry_nome.pack(pady=5)

        self.label_tipo = ctk.CTkLabel(self.tab_cadastro, text="Tipo de Animal:", font=("arial", 16))
        self.label_tipo.pack(pady=(10, 0))
        self.combo_tipo = ctk.CTkComboBox(self.tab_cadastro, values=["Cachorro", "Gato", "Pássaro", "Peixe", "Outro"], width=300)
        self.combo_tipo.pack(pady=5)

        self.label_instruacao = ctk.CTkLabel(self.tab_cadastro, text="Quantidade (g):", font=("arial", 16))
        self.label_instruacao.pack(pady=(10, 0))
        self.entry_racao = ctk.CTkEntry(self.tab_cadastro, placeholder_text="Ex: 500", width=300)
        self.entry_racao.pack(pady=5)

        self.label_lbl_horario = ctk.CTkLabel(self.tab_cadastro, text="Horário Agendado:", font=("arial", 16))
        self.label_lbl_horario.pack(pady=(10, 0))
        self.entry_hora = ctk.CTkEntry(self.tab_cadastro, placeholder_text="Ex: 08:30", width=300)
        self.entry_hora.pack(pady=5)

        self.check_repetir = ctk.CTkCheckBox(self.tab_cadastro, text="Repetir liberação", command=self.toggle_repetir, font=("arial", 14))
        self.check_repetir.pack(pady=10)

        self.label_vezes = ctk.CTkLabel(self.tab_cadastro, text="Quantidade de liberações:", font=("arial", 14))
        self.entry_vezes = ctk.CTkEntry(self.tab_cadastro, placeholder_text="Ex: 4", width=100)

        self.btn_confirmar = ctk.CTkButton(self.tab_cadastro, text="Salvar Agendamento", command=self.salvar_exibir, font=("roboto", 18), width=300)
        self.btn_confirmar.pack(pady=20)

        self.labelstat = ctk.CTkLabel(self.tab_cadastro, text="Pronto para cadastrar", text_color="yellow", font=("arial", 14))
        self.labelstat.pack()

    def toggle_repetir(self):
        if self.check_repetir.get() == 1:
            self.label_vezes.pack(pady=(5, 0))
            self.entry_vezes.pack(pady=5)
        else:
            self.label_vezes.pack_forget()
            self.entry_vezes.pack_forget()
            self.entry_vezes.delete(0, 'end')

    def setup_aba_fichas(self):
        self.scroll_fichas = ctk.CTkScrollableFrame(self.tab_fichas, width=500, height=500)
        self.scroll_fichas.pack(fill="both", expand=True, padx=10, pady=10)

    def init_db(self):
        conn = sqlite3.connect('dados_dispenser.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_animal TEXT,
                tipo_animal TEXT,
                quantidade TEXT,
                horario_agendado TEXT,
                status TEXT,
                repeticoes INTEGER DEFAULT 1
            )
        ''')
        conn.commit()
        conn.close()

    def carregar_agendamentos_db(self):
        self.agendamentos = []
        conn = sqlite3.connect('dados_dispenser.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome_animal, tipo_animal, quantidade, horario_agendado, repeticoes FROM registros WHERE status = 'Pendente'")
        rows = cursor.fetchall()
        for r in rows:
            self.agendamentos.append({"id": r[0], "nome": r[1], "tipo": r[2], "qtd": r[3], "hora": r[4], "vezes": r[5]})
        conn.close()
        self.atualizar_fichas_gui()

    def salvar_exibir(self):
        nome = self.entry_nome.get()
        tipo = self.combo_tipo.get()
        qtd = self.entry_racao.get()
        hora = self.entry_hora.get()
        
        vezes = 1
        if self.check_repetir.get() == 1:
            v_input = self.entry_vezes.get()
            if v_input.isdigit() and int(v_input) > 0:
                vezes = int(v_input)
            else:
                self.labelstat.configure(text="Erro: quantidade de liberações inválida", text_color="red")
                return

        if nome == "" or qtd == "" or hora == "":
            self.labelstat.configure(text="Erro: preencha todos os campos", text_color="red")
            return

        conn = sqlite3.connect('dados_dispenser.db')
        cursor = conn.cursor()

        if self.editando_id:
            cursor.execute('''UPDATE registros SET nome_animal=?, tipo_animal=?, quantidade=?, horario_agendado=?, repeticoes=? WHERE id=?''',
                           (nome, tipo, qtd, hora, vezes, self.editando_id))
            self.labelstat.configure(text="Agendamento atualizado!", text_color="green")
            self.editando_id = None
            self.btn_confirmar.configure(text="Salvar Agendamento")
        else:
            cursor.execute('''INSERT INTO registros (nome_animal, tipo_animal, quantidade, horario_agendado, status, repeticoes)
                              VALUES (?, ?, ?, ?, 'Pendente', ?)''', (nome, tipo, qtd, hora, vezes))
            self.labelstat.configure(text=f"Agendamento para {nome}!", text_color="green")

        conn.commit()
        conn.close()

        self.entry_nome.delete(0, 'end')
        self.entry_racao.delete(0, 'end')
        self.entry_hora.delete(0, 'end')
        self.check_repetir.deselect()
        self.toggle_repetir()

        self.carregar_agendamentos_db()

    def atualizar_fichas_gui(self):
        for widget in self.scroll_fichas.winfo_children():
            widget.destroy()

        for agend in self.agendamentos:
            ficha = ctk.CTkFrame(self.scroll_fichas)
            ficha.pack(fill="x", padx=10, pady=5)

            info = f"{agend['nome']} ({agend['tipo']}) - {agend['qtd']}g\nHorário: {agend['hora']} (Restam: {agend['vezes']}x)"
            ctk.CTkLabel(ficha, text=info, justify="left", font=("arial", 12, "bold")).pack(side="left", padx=10, pady=10)

            btn_del = ctk.CTkButton(ficha, text="X", width=30, fg_color="red", hover_color="#8B0000", command=lambda a=agend: self.excluir_agendamento(a))
            btn_del.pack(side="right", padx=5)

            btn_edit = ctk.CTkButton(ficha, text="Editar", width=60, command=lambda a=agend: self.preparar_edicao(a))
            btn_edit.pack(side="right", padx=5)

    def excluir_agendamento(self, agendamento):
        conn = sqlite3.connect('dados_dispenser.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM registros WHERE id=?", (agendamento['id'],))
        conn.commit()
        conn.close()
        self.carregar_agendamentos_db()

    def preparar_edicao(self, agendamento):
        self.entry_nome.delete(0, 'end')
        self.entry_nome.insert(0, agendamento['nome'])
        self.combo_tipo.set(agendamento['tipo'])
        self.entry_racao.delete(0, 'end')
        self.entry_racao.insert(0, agendamento['qtd'])
        self.entry_hora.delete(0, 'end')
        self.entry_hora.insert(0, agendamento['hora'])

        if agendamento['vezes'] > 1:
            self.check_repetir.select()
            self.toggle_repetir()
            self.entry_vezes.delete(0, 'end')
            self.entry_vezes.insert(0, str(agendamento['vezes']))
        else:
            self.check_repetir.deselect()
            self.toggle_repetir()

        self.editando_id = agendamento['id']
        self.btn_confirmar.configure(text="Atualizar Dados")
        self.tabview.set("Cadastro")

    def verificar_horario(self):
        agora = datetime.now().strftime("%H:%M")

        for agendamento in self.agendamentos[:]:
            if agendamento["hora"] == agora:
                self.notificar_sucesso(agendamento)
                self.processar_execucao(agendamento)

        self.after(60000, self.verificar_horario)

    def processar_execucao(self, agendamento):
        conn = sqlite3.connect('dados_dispenser.db')
        cursor = conn.cursor()
        
        novas_vezes = agendamento['vezes'] - 1
        
        if novas_vezes <= 0:
            cursor.execute("UPDATE registros SET status='Concluido', repeticoes=0 WHERE id=?", (agendamento['id'],))
        else:
            cursor.execute("UPDATE registros SET repeticoes=? WHERE id=?", (novas_vezes, agendamento['id']))
            
        conn.commit()
        conn.close()
        self.carregar_agendamentos_db()

    def notificar_sucesso(self, agend):
        agora_txt = datetime.now().strftime('%H:%M:%S')
        notification.notify(
            title="Dispenser de Ração",
            message=f"Sucesso! {agend['qtd']}g dispensadas para {agend['nome']}.",
            timeout=10
        )

        self.txt_historico.configure(state="normal")
        self.txt_historico.insert("end", f"[{agora_txt}] {agend['nome']}: {agend['qtd']}g\n")
        self.txt_historico.configure(state="disabled")
        self.txt_historico.see("end")

if __name__ == "__main__":
    app = Dispenserrr()
    app.mainloop()