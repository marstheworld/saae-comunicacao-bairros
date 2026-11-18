"""Persistência local e regras do protótipo. Não realiza comunicação externa."""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import sqlite3
from uuid import uuid4


TIPOS = (
    "Manutenção programada", "Interrupção emergencial",
    "Normalização do abastecimento", "Outro comunicado",
)


@dataclass(frozen=True)
class Previa:
    token: str
    tipo: str
    bairros: tuple  # (id, nome)
    mensagem: str
    previsao: str
    destinatarios: tuple  # (id, nome fictício, identificador, bairro)


class Banco:
    def __init__(self, caminho=None, demonstracao=True):
        if caminho is None:
            caminho = Path(__file__).resolve().parent / "dados" / "prototipo.sqlite3"
            caminho.parent.mkdir(parents=True, exist_ok=True)
        self.con = sqlite3.connect(caminho)
        self.con.row_factory = sqlite3.Row
        self.con.execute("PRAGMA foreign_keys = ON")
        self.con.executescript("""
            CREATE TABLE IF NOT EXISTS bairros (
                id INTEGER PRIMARY KEY, nome TEXT NOT NULL,
                chave TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS contatos (
                id INTEGER PRIMARY KEY, nome TEXT NOT NULL,
                identificador TEXT NOT NULL UNIQUE,
                bairro_id INTEGER NOT NULL REFERENCES bairros(id),
                ativo INTEGER NOT NULL CHECK (ativo IN (0, 1))
            );
            CREATE TABLE IF NOT EXISTS comunicados (
                id INTEGER PRIMARY KEY, token TEXT NOT NULL UNIQUE,
                data TEXT NOT NULL, tipo TEXT NOT NULL, mensagem TEXT NOT NULL,
                previsao TEXT NOT NULL, quantidade INTEGER NOT NULL,
                situacao TEXT NOT NULL CHECK (situacao = 'Simulado')
            );
            CREATE TABLE IF NOT EXISTS comunicado_bairros (
                comunicado_id INTEGER NOT NULL REFERENCES comunicados(id),
                bairro_id INTEGER NOT NULL REFERENCES bairros(id),
                nome TEXT NOT NULL,
                PRIMARY KEY (comunicado_id, bairro_id)
            );
            CREATE TABLE IF NOT EXISTS destinatarios (
                comunicado_id INTEGER NOT NULL REFERENCES comunicados(id),
                contato_id INTEGER NOT NULL,
                nome TEXT NOT NULL, identificador TEXT NOT NULL, bairro TEXT NOT NULL,
                PRIMARY KEY (comunicado_id, contato_id)
            );
        """)
        # A versão marca a inicialização, inclusive após exclusão dos contatos.
        if self.con.execute("PRAGMA user_version").fetchone()[0] == 0:
            with self.con:
                if demonstracao and not self.con.execute("SELECT 1 FROM bairros").fetchone():
                    for numero, nome in enumerate(("Centro", "Rosário I", "Rosário II")):
                        bairro = self.con.execute(
                            "INSERT INTO bairros(nome, chave) VALUES (?, ?)",
                            (nome, nome.casefold()),
                        ).lastrowid
                        for posicao in range(1, 9):
                            indice = numero * 8 + posicao
                            self.con.execute(
                                "INSERT INTO contatos(nome, identificador, bairro_id, ativo) VALUES (?, ?, ?, ?)",
                                (f"Morador fictício {indice:02}", f"TESTE-{indice:04}", bairro, int(posicao <= 6)),
                            )
                self.con.execute("PRAGMA user_version = 1")

    def fechar(self):
        self.con.close()

    def bairros(self):
        return self.con.execute("SELECT id, nome FROM bairros ORDER BY nome").fetchall()

    def adicionar_bairro(self, nome):
        nome = " ".join(nome.split())
        if not nome or len(nome) > 80:
            raise ValueError("Informe um nome de bairro com até 80 caracteres.")
        try:
            with self.con:
                return self.con.execute(
                    "INSERT INTO bairros(nome, chave) VALUES (?, ?)", (nome, nome.casefold())
                ).lastrowid
        except sqlite3.IntegrityError as erro:
            raise ValueError("Esse bairro já está cadastrado.") from erro

    def contatos(self):
        return self.con.execute("""
            SELECT c.*, b.nome AS bairro FROM contatos c
            JOIN bairros b ON b.id = c.bairro_id ORDER BY c.nome, c.id
        """).fetchall()

    def salvar_contato(self, nome, identificador, bairro_id, ativo=True, contato_id=None):
        nome = nome.strip()
        identificador = identificador.strip().upper()
        if not nome or len(nome) > 100:
            raise ValueError("Informe um nome fictício com até 100 caracteres.")
        if not re.fullmatch(r"TESTE-[0-9]{4,8}", identificador):
            raise ValueError("Use um identificador fictício como TESTE-0001 (4 a 8 dígitos).")
        if not self.con.execute("SELECT 1 FROM bairros WHERE id = ?", (bairro_id,)).fetchone():
            raise ValueError("Selecione um bairro cadastrado.")
        if ativo not in (True, False):
            raise ValueError("A situação deve ser ativa ou inativa.")
        try:
            with self.con:
                valores = (nome, identificador, bairro_id, int(ativo))
                if contato_id is None:
                    return self.con.execute(
                        "INSERT INTO contatos(nome, identificador, bairro_id, ativo) VALUES (?, ?, ?, ?)", valores
                    ).lastrowid
                cursor = self.con.execute(
                    "UPDATE contatos SET nome=?, identificador=?, bairro_id=?, ativo=? WHERE id=?",
                    (*valores, contato_id),
                )
                if cursor.rowcount != 1:
                    raise ValueError("O contato não existe mais. Atualize a lista.")
                return contato_id
        except sqlite3.IntegrityError as erro:
            raise ValueError("Já existe um contato com esse identificador fictício.") from erro

    def excluir_contato(self, contato_id):
        with self.con:
            if self.con.execute("DELETE FROM contatos WHERE id=?", (contato_id,)).rowcount != 1:
                raise ValueError("Selecione um contato existente.")

    def destinatarios(self, bairro_ids):
        ids = tuple(sorted(set(bairro_ids)))
        if not ids:
            return ()
        marcadores = ",".join("?" for _ in ids)
        return tuple(tuple(row) for row in self.con.execute(f"""
            SELECT c.id, c.nome, c.identificador, b.nome FROM contatos c
            JOIN bairros b ON b.id=c.bairro_id
            WHERE c.ativo=1 AND c.bairro_id IN ({marcadores}) ORDER BY c.id
        """, ids))

    def preparar(self, tipo, bairro_ids, mensagem, previsao=""):
        if tipo not in TIPOS:
            raise ValueError("Selecione um tipo de comunicado válido.")
        mensagem, previsao = mensagem.strip(), previsao.strip()
        if not mensagem or len(mensagem) > 5000:
            raise ValueError("Escreva uma mensagem com 1 a 5.000 caracteres.")
        if len(previsao) > 160:
            raise ValueError("Use até 160 caracteres na previsão de normalização.")
        ids = set(bairro_ids)
        if not ids:
            raise ValueError("Selecione pelo menos um bairro.")
        bairros = tuple((b["id"], b["nome"]) for b in self.bairros() if b["id"] in ids)
        if len(bairros) != len(ids):
            raise ValueError("Há um bairro inválido na seleção. Confira os bairros.")
        destinatarios = self.destinatarios(ids)
        if not destinatarios:
            raise ValueError("Nenhum contato ativo foi encontrado nos bairros selecionados.")
        return Previa(str(uuid4()), tipo, bairros, mensagem, previsao, destinatarios)

    def simular(self, previa):
        """Registra uma operação e uma cópia de cada destinatário, atomicamente."""
        with self.con:
            self.con.execute("BEGIN IMMEDIATE")
            if self.con.execute("SELECT 1 FROM comunicados WHERE token=?", (previa.token,)).fetchone():
                raise ValueError("Esta simulação já foi registrada. Consulte o histórico.")
            atual = self.preparar(previa.tipo, [b[0] for b in previa.bairros], previa.mensagem, previa.previsao)
            if atual.destinatarios != previa.destinatarios or atual.bairros != previa.bairros:
                raise ValueError("Os cadastros mudaram. Feche a conferência e confira novamente.")
            comunicado_id = self.con.execute("""
                INSERT INTO comunicados(token, data, tipo, mensagem, previsao, quantidade, situacao)
                VALUES (?, ?, ?, ?, ?, ?, 'Simulado')
            """, (previa.token, datetime.now().astimezone().isoformat(timespec="seconds"),
                  previa.tipo, previa.mensagem, previa.previsao, len(previa.destinatarios))).lastrowid
            self.con.executemany(
                "INSERT INTO comunicado_bairros(comunicado_id, bairro_id, nome) VALUES (?, ?, ?)",
                [(comunicado_id, *bairro) for bairro in previa.bairros],
            )
            # Sem vínculo FK com o cadastro: excluir/editar contato não altera o histórico.
            self.con.executemany(
                "INSERT INTO destinatarios(comunicado_id, contato_id, nome, identificador, bairro) VALUES (?, ?, ?, ?, ?)",
                [(comunicado_id, *contato) for contato in previa.destinatarios],
            )
        return comunicado_id

    def historico(self):
        return self.con.execute("SELECT * FROM comunicados ORDER BY id DESC").fetchall()

    def detalhes(self, comunicado_id):
        registro = self.con.execute("SELECT * FROM comunicados WHERE id=?", (comunicado_id,)).fetchone()
        if registro is None:
            raise ValueError("Selecione um comunicado existente.")
        bairros = self.con.execute(
            "SELECT nome FROM comunicado_bairros WHERE comunicado_id=? ORDER BY nome", (comunicado_id,)
        ).fetchall()
        contatos = self.con.execute(
            "SELECT nome, identificador, bairro FROM destinatarios WHERE comunicado_id=? ORDER BY contato_id",
            (comunicado_id,),
        ).fetchall()
        return registro, [b[0] for b in bairros], contatos
