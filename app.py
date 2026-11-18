"""Interface do protótipo acadêmico. Execute com python app.py."""

from datetime import datetime
import logging
from pathlib import Path
import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from tkinter.scrolledtext import ScrolledText

from dados import Banco, TIPOS


MODELOS = {
    TIPOS[0]: "Informamos que haverá manutenção programada na rede de abastecimento dos bairros selecionados. Durante o serviço, poderá ocorrer interrupção no fornecimento de água. Agradecemos a compreensão.",
    TIPOS[1]: "Informamos uma interrupção emergencial no abastecimento dos bairros selecionados. A equipe está trabalhando para restabelecer o serviço. Agradecemos a compreensão.",
    TIPOS[2]: "Informamos que o abastecimento dos bairros selecionados foi restabelecido. O retorno da água poderá ocorrer de forma gradual. Agradecemos a compreensão.",
    TIPOS[3]: "Escreva aqui o comunicado para os bairros selecionados.",
}


def data_legivel(valor):
    return datetime.fromisoformat(valor).strftime("%d/%m/%Y %H:%M:%S")


class Aplicativo(tk.Tk):
    def __init__(self, banco):
        super().__init__()
        self.banco = banco
        self.title("SAAE de Baixo Guandu — Protótipo acadêmico")
        self.geometry("1080x760")
        self.minsize(940, 700)
        self.configure(bg="#f3f6f8")
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.contato_id = None
        self.bairro_checks = {}
        estilo = ttk.Style(self)
        estilo.theme_use("clam")
        estilo.configure(".", font=("Segoe UI", 10), background="#f3f6f8", foreground="#183445")
        estilo.configure("TButton", padding=(12, 7))
        estilo.configure("TNotebook.Tab", padding=(20, 10))
        estilo.configure("Treeview", background="white", fieldbackground="white", rowheight=29)
        estilo.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=7)
        estilo.map("Treeview", background=[("selected", "#176c82")], foreground=[("selected", "white")])
        estilo.configure("Destaque.TButton", background="#176c82", foreground="white")
        estilo.map("Destaque.TButton", background=[("active", "#12586a"), ("disabled", "#aebbc2")])
        estilo.configure("Titulo.TLabel", font=("Segoe UI", 19, "bold"))
        estilo.configure("Subtitulo.TLabel", foreground="#526a78")
        topo = ttk.Frame(self, padding=(24, 18, 24, 12))
        topo.pack(fill="x")
        ttk.Label(topo, text="Comunicação com os bairros", style="Titulo.TLabel").pack(anchor="w")
        ttk.Label(topo, text="SAAE de Baixo Guandu — Protótipo acadêmico", style="Subtitulo.TLabel").pack(anchor="w", pady=(4, 0))
        tk.Label(self, text="DEMONSTRAÇÃO  •  Dados fictícios  •  Nenhuma mensagem real é enviada",
                 bg="#e0f1f4", fg="#15566a", font=("Segoe UI", 10, "bold"), pady=10).pack(fill="x", padx=24)
        self.abas = ttk.Notebook(self)
        self.abas.pack(fill="both", expand=True, padx=24, pady=(16, 8))
        self.aba_contatos = ttk.Frame(self.abas, padding=18)
        self.aba_comunicados = ttk.Frame(self.abas, padding=18)
        self.aba_historico = ttk.Frame(self.abas, padding=18)
        for aba, titulo in ((self.aba_contatos, "Contatos"), (self.aba_comunicados, "Comunicados"), (self.aba_historico, "Histórico")):
            self.abas.add(aba, text=titulo)
        self.status = tk.StringVar(value="Pronto para demonstrar. Funcionamento local e offline.")
        ttk.Label(self, textvariable=self.status, style="Subtitulo.TLabel", padding=(24, 4, 24, 12)).pack(side="bottom", fill="x", before=self.abas)
        self.montar_contatos()
        self.montar_comunicados()
        self.montar_historico()
        self.atualizar_bairros()
        self.atualizar_contatos()
        self.atualizar_historico()

    def report_callback_exception(self, classe, erro, traceback):
        if isinstance(erro, ValueError):
            messagebox.showwarning("Confira as informações", str(erro), parent=self)
        elif isinstance(erro, sqlite3.Error):
            logging.error("Erro de banco", exc_info=(classe, erro, traceback))
            messagebox.showerror("Não foi possível salvar ou consultar", "O banco local está indisponível. Feche outras janelas do protótipo e tente novamente.\nSe persistir, consulte o arquivo dados/erros.log.", parent=self)
        else:
            logging.error("Erro da interface", exc_info=(classe, erro, traceback))
            messagebox.showerror("Não foi possível concluir", "Ocorreu um erro inesperado. Consulte dados/erros.log para revisão técnica.", parent=self)

    def tabela(self, pai, colunas, larguras, altura=6):
        quadro = ttk.Frame(pai)
        quadro.pack(fill="both", expand=True, pady=(8, 8))
        arvore = ttk.Treeview(quadro, columns=colunas, show="headings", selectmode="browse", height=altura)
        for coluna, largura in zip(colunas, larguras):
            arvore.heading(coluna, text=coluna)
            arvore.column(coluna, width=largura, minwidth=70)
        rolagem = ttk.Scrollbar(quadro, orient="vertical", command=arvore.yview)
        arvore.configure(yscrollcommand=rolagem.set)
        arvore.pack(side="left", fill="both", expand=True)
        rolagem.pack(side="right", fill="y")
        return arvore

    def montar_contatos(self):
        ttk.Label(self.aba_contatos, text="Cadastre apenas moradores inventados e identificadores de teste.").pack(anchor="w")
        self.total_contatos = tk.StringVar()
        ttk.Label(self.aba_contatos, textvariable=self.total_contatos, style="Subtitulo.TLabel").pack(anchor="w", pady=(5, 0))
        self.lista_contatos = self.tabela(self.aba_contatos, ("Nome fictício", "Identificador", "Bairro", "Situação"), (320, 170, 240, 100))
        self.lista_contatos.bind("<<TreeviewSelect>>", self.selecionar_contato)
        form = ttk.LabelFrame(self.aba_contatos, text="Cadastro de teste", padding=12)
        form.pack(side="bottom", fill="x", pady=(4, 8), before=self.lista_contatos.master)
        form.columnconfigure(0, weight=2)
        form.columnconfigure(1, weight=1)
        form.columnconfigure(2, weight=1)
        self.nome = tk.StringVar()
        self.identificador = tk.StringVar()
        self.bairro_contato = tk.StringVar()
        self.ativo = tk.BooleanVar(value=True)
        for coluna, texto in enumerate(("Nome fictício", "Identificador (ex.: TESTE-0025)", "Bairro")):
            ttk.Label(form, text=texto).grid(row=0, column=coluna, sticky="w", padx=(0, 12))
        self.campo_nome = ttk.Entry(form, textvariable=self.nome)
        self.campo_nome.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=6)
        ttk.Entry(form, textvariable=self.identificador).grid(row=1, column=1, sticky="ew", padx=(0, 12))
        self.combo_bairro = ttk.Combobox(form, textvariable=self.bairro_contato, state="readonly", width=20)
        self.combo_bairro.grid(row=1, column=2, sticky="ew")
        ttk.Checkbutton(form, text="Cadastro ativo (participa das simulações)", variable=self.ativo).grid(row=2, column=0, columnspan=3, sticky="w", pady=4)
        acoes = ttk.Frame(self.aba_contatos)
        acoes.pack(side="bottom", fill="x", before=form)
        for texto, comando in (("Novo contato", self.novo_contato), ("Salvar contato", self.salvar_contato), ("Excluir selecionado", self.excluir_contato)):
            ttk.Button(acoes, text=texto, command=comando).pack(side="left", padx=(0, 8))
        ttk.Button(acoes, text="Adicionar bairro", command=self.adicionar_bairro).pack(side="right")

    def atualizar_contatos(self):
        self.lista_contatos.delete(*self.lista_contatos.get_children())
        self.contatos_por_id = {c["id"]: c for c in self.banco.contatos()}
        for c in self.contatos_por_id.values():
            self.lista_contatos.insert("", "end", iid=str(c["id"]), values=(c["nome"], c["identificador"], c["bairro"], "Ativo" if c["ativo"] else "Inativo"))
        ativos = sum(c["ativo"] for c in self.contatos_por_id.values())
        self.total_contatos.set(f"{len(self.contatos_por_id)} contatos fictícios  •  {ativos} ativos")
        self.lista_contatos.yview_moveto(0)
        self.atualizar_contagem()

    def selecionar_contato(self, evento=None):
        selecao = self.lista_contatos.selection()
        if not selecao:
            return
        self.contato_id = int(selecao[0])
        c = self.contatos_por_id[self.contato_id]
        self.nome.set(c["nome"])
        self.identificador.set(c["identificador"])
        self.bairro_contato.set(c["bairro"])
        self.ativo.set(bool(c["ativo"]))

    def novo_contato(self):
        self.lista_contatos.selection_remove(*self.lista_contatos.selection())
        self.contato_id = None
        self.nome.set("")
        self.identificador.set("")
        self.bairro_contato.set("")
        self.ativo.set(True)
        self.campo_nome.focus_set()

    def salvar_contato(self):
        codigo = self.banco.salvar_contato(self.nome.get(), self.identificador.get(), self.bairros_por_nome.get(self.bairro_contato.get()), self.ativo.get(), self.contato_id)
        self.atualizar_contatos()
        self.lista_contatos.selection_set(str(codigo))
        self.lista_contatos.see(str(codigo))
        self.selecionar_contato()
        self.status.set("Contato fictício salvo.")

    def excluir_contato(self):
        if self.contato_id is None:
            raise ValueError("Selecione um contato na lista para excluir.")
        if messagebox.askyesno("Excluir contato fictício", f"Excluir {self.nome.get()}?\nOs registros anteriores do histórico serão preservados.", parent=self):
            self.banco.excluir_contato(self.contato_id)
            self.novo_contato()
            self.atualizar_contatos()
            self.status.set("Contato fictício excluído.")

    def adicionar_bairro(self):
        nome = simpledialog.askstring("Adicionar bairro", "Nome do bairro para demonstração:", parent=self)
        if nome is not None:
            self.banco.adicionar_bairro(nome)
            self.atualizar_bairros()
            self.status.set("Bairro adicionado à lista demonstrativa.")

    def montar_comunicados(self):
        painel = self.aba_comunicados
        rodape = ttk.Frame(painel)
        rodape.pack(side="bottom", fill="x")
        self.previsao = tk.StringVar()
        ttk.Label(rodape, text="Previsão de normalização (opcional; ex.: hoje, às 18h)").pack(anchor="w")
        ttk.Entry(rodape, textvariable=self.previsao).pack(fill="x", pady=(4, 10))
        ttk.Button(rodape, text="2. Conferir simulação", command=self.conferir, style="Destaque.TButton").pack(anchor="e")
        ttk.Label(painel, text="1. Prepare o aviso e selecione os bairros afetados.", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))
        linha = ttk.Frame(painel)
        linha.pack(fill="x")
        self.tipo = tk.StringVar(value=TIPOS[0])
        ttk.Label(linha, text="Tipo de comunicado").pack(anchor="w")
        ttk.Combobox(linha, textvariable=self.tipo, values=TIPOS, state="readonly", width=38).pack(side="left", pady=5)
        ttk.Button(linha, text="Usar modelo de mensagem", command=self.usar_modelo).pack(side="left", padx=12)
        quadro = ttk.LabelFrame(painel, text="Bairros afetados — selecione um ou mais", padding=6)
        quadro.pack(fill="x", pady=(8, 8))
        canvas = tk.Canvas(quadro, height=50, bg="#f3f6f8", highlightthickness=0)
        scroll = ttk.Scrollbar(quadro, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        canvas.pack(side="left", fill="x", expand=True)
        self.quadro_bairros = ttk.Frame(canvas)
        janela = canvas.create_window((0, 0), window=self.quadro_bairros, anchor="nw")
        self.quadro_bairros.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(janela, width=e.width))
        ttk.Label(painel, text="Lista demonstrativa; não é uma relação oficial ou completa do município.", style="Subtitulo.TLabel").pack(anchor="w")
        self.contagem = tk.StringVar()
        ttk.Label(painel, textvariable=self.contagem, font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(5, 8))
        ttk.Label(painel, text="Mensagem (até 5.000 caracteres)").pack(anchor="w")
        self.mensagem = ScrolledText(painel, height=5, wrap="word", font=("Segoe UI", 11), relief="solid", borderwidth=1, padx=8, pady=8)
        self.mensagem.pack(fill="both", expand=True, pady=(4, 8))

    def atualizar_bairros(self):
        selecionados = self.bairros_selecionados()
        self.bairros_por_nome = {b["nome"]: b["id"] for b in self.banco.bairros()}
        self.combo_bairro.configure(values=list(self.bairros_por_nome))
        for widget in self.quadro_bairros.winfo_children():
            widget.destroy()
        self.bairro_checks = {}
        for indice, (nome, codigo) in enumerate(self.bairros_por_nome.items()):
            var = tk.BooleanVar(value=codigo in selecionados)
            self.bairro_checks[codigo] = var
            ttk.Checkbutton(self.quadro_bairros, text=nome, variable=var, command=self.atualizar_contagem).grid(row=indice // 3, column=indice % 3, sticky="w", padx=(8, 24), pady=5)
        self.atualizar_contagem()

    def bairros_selecionados(self):
        return [codigo for codigo, var in self.bairro_checks.items() if var.get()]

    def atualizar_contagem(self):
        bairros = self.bairros_selecionados()
        quantidade = len(self.banco.destinatarios(bairros))
        self.contagem.set(f"{len(bairros)} bairro(s) selecionado(s)  •  {quantidade} contato(s) ativo(s) para simulação")

    def usar_modelo(self):
        if self.mensagem.get("1.0", "end").strip() and not messagebox.askyesno("Substituir mensagem", "Substituir o texto atual pelo modelo selecionado?", parent=self):
            return
        self.mensagem.delete("1.0", "end")
        self.mensagem.insert("1.0", MODELOS[self.tipo.get()])

    def janela_texto(self, titulo, texto):
        janela = tk.Toplevel(self)
        janela.title(titulo)
        janela.geometry("780x620")
        janela.minsize(640, 500)
        janela.transient(self)
        janela.grab_set()
        ttk.Label(janela, text=titulo, font=("Segoe UI", 15, "bold"), padding=16).pack(anchor="w")
        acoes = ttk.Frame(janela, padding=(16, 0, 16, 16))
        acoes.pack(side="bottom", fill="x")
        conteudo = ScrolledText(janela, wrap="word", font=("Segoe UI", 11), padx=14, pady=12)
        conteudo.pack(fill="both", expand=True, padx=16, pady=(0, 12))
        conteudo.insert("1.0", texto)
        conteudo.configure(state="disabled")
        janela.bind("<Escape>", lambda e: janela.destroy())
        return janela, acoes

    def conferir(self):
        previa = self.banco.preparar(self.tipo.get(), self.bairros_selecionados(), self.mensagem.get("1.0", "end"), self.previsao.get())
        texto = (
            "ENVIO SIMULADO — nenhuma mensagem será enviada de verdade.\n\n"
            f"Tipo: {previa.tipo}\n"
            f"Bairros: {', '.join(b[1] for b in previa.bairros)}\n"
            f"Destinatários ativos: {len(previa.destinatarios)}\n"
            f"Previsão de normalização: {previa.previsao or 'Não informada'}\n\n"
            f"MENSAGEM\n{previa.mensagem}\n\n"
            "DESTINATÁRIOS FICTÍCIOS\n" + "\n".join(f"{c[2]} • {c[1]} • {c[3]}" for c in previa.destinatarios)
        )
        janela, acoes = self.janela_texto("Confira antes de confirmar", texto)
        ttk.Button(acoes, text="Voltar e editar", command=janela.destroy).pack(side="left")
        confirmar = ttk.Button(acoes, text="Confirmar simulação", style="Destaque.TButton")
        confirmar.pack(side="right")

        def registrar():
            confirmar.configure(state="disabled")
            try:
                codigo = self.banco.simular(previa)
            except Exception:
                janela.destroy()
                raise
            janela.destroy()
            self.mensagem.delete("1.0", "end")
            self.previsao.set("")
            for var in self.bairro_checks.values():
                var.set(False)
            self.atualizar_contagem()
            self.atualizar_historico()
            self.abas.select(self.aba_historico)
            self.lista_historico.selection_set(str(codigo))
            self.lista_historico.see(str(codigo))
            self.mostrar_resumo()
            self.status.set(f"Simulação #{codigo} registrada. Nenhuma mensagem real foi enviada.")
            messagebox.showinfo("Simulação concluída!", f"Bairros selecionados: {len(previa.bairros)}\nContatos identificados: {len(previa.destinatarios)}\nAvisos simulados: {len(previa.destinatarios)}\n\nNenhuma mensagem foi enviada de verdade.", parent=self)

        confirmar.configure(command=registrar)

    def montar_historico(self):
        acoes = ttk.Frame(self.aba_historico)
        acoes.pack(side="bottom", fill="x")
        ttk.Button(acoes, text="Atualizar histórico", command=self.atualizar_historico).pack(side="left")
        ttk.Button(acoes, text="Ver detalhes e destinatários", command=self.ver_detalhes).pack(side="right")
        ttk.Label(self.aba_historico, text="Operações simuladas salvas neste computador.").pack(anchor="w")
        self.lista_historico = self.tabela(self.aba_historico, ("Nº", "Data e horário", "Tipo", "Contatos", "Situação"), (70, 190, 320, 90, 110), altura=6)
        self.lista_historico.bind("<<TreeviewSelect>>", self.mostrar_resumo)
        self.lista_historico.bind("<Double-1>", lambda e: self.ver_detalhes())
        self.resumo = ScrolledText(self.aba_historico, height=7, wrap="word", font=("Segoe UI", 10), padx=10, pady=10)
        self.resumo.pack(fill="both", expand=True, pady=(4, 12))
        self.resumo.configure(state="disabled")

    def atualizar_historico(self):
        self.lista_historico.delete(*self.lista_historico.get_children())
        for registro in self.banco.historico():
            self.lista_historico.insert("", "end", iid=str(registro["id"]), values=(registro["id"], data_legivel(registro["data"]), registro["tipo"], registro["quantidade"], registro["situacao"]))
        self.resumo.configure(state="normal")
        self.resumo.delete("1.0", "end")
        self.resumo.insert("1.0", "Selecione uma operação para consultar a mensagem.\nSe a lista estiver vazia, registre a primeira simulação na aba Comunicados.")
        self.resumo.configure(state="disabled")

    def texto_historico(self, completo=False):
        selecao = self.lista_historico.selection()
        if not selecao:
            raise ValueError("Selecione uma operação no histórico.")
        registro, bairros, contatos = self.banco.detalhes(int(selecao[0]))
        texto = (
            f"Simulação #{registro['id']} • {data_legivel(registro['data'])} • {registro['situacao']}\n"
            f"Tipo: {registro['tipo']}\nBairros: {', '.join(bairros)}\n"
            f"Contatos identificados / avisos simulados: {registro['quantidade']}\n"
            f"Previsão de normalização: {registro['previsao'] or 'Não informada'}\n\n"
            f"{registro['mensagem']}\n\nNenhuma mensagem foi enviada de verdade."
        )
        if completo:
            texto += "\n\nDESTINATÁRIOS NA DATA DA SIMULAÇÃO\n" + "\n".join(f"{c['identificador']} • {c['nome']} • {c['bairro']}" for c in contatos)
        return texto

    def mostrar_resumo(self, evento=None):
        if not self.lista_historico.selection():
            return
        texto = self.texto_historico()
        self.resumo.configure(state="normal")
        self.resumo.delete("1.0", "end")
        self.resumo.insert("1.0", texto)
        self.resumo.configure(state="disabled")

    def ver_detalhes(self):
        janela, acoes = self.janela_texto("Detalhes da simulação", self.texto_historico(completo=True))
        ttk.Button(acoes, text="Fechar", command=janela.destroy).pack(side="right")


def main():
    pasta = Path(__file__).resolve().parent / "dados"
    banco = None
    try:
        pasta.mkdir(exist_ok=True)
        logging.basicConfig(filename=pasta / "erros.log", encoding="utf-8", level=logging.ERROR,
                            format="%(asctime)s %(levelname)s %(message)s")
        banco = Banco()
        aplicativo = Aplicativo(banco)
        aplicativo.mainloop()
    except (OSError, sqlite3.Error) as erro:
        raiz = tk.Tk()
        raiz.withdraw()
        messagebox.showerror("Não foi possível abrir", f"Verifique se a pasta dev permite salvar arquivos e se o banco está disponível.\n\nDetalhe: {erro}", parent=raiz)
        raiz.destroy()
    finally:
        if banco is not None:
            banco.fechar()


if __name__ == "__main__":
    main()
