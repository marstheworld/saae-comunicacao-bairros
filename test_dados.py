"""Execute: python -m unittest -v"""

import ast
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from dados import Banco, TIPOS


class RegrasTest(unittest.TestCase):
    def setUp(self):
        self.banco = Banco(":memory:", demonstracao=False)
        self.addCleanup(self.banco.fechar)
        self.centro = self.banco.adicionar_bairro("Centro")
        self.rosario = self.banco.adicionar_bairro("Rosário I")
        self.vazio = self.banco.adicionar_bairro("Bairro de teste")
        self.a = self.banco.salvar_contato("Pessoa fictícia A", "TESTE-0001", self.centro)
        self.banco.salvar_contato("Pessoa fictícia B", "TESTE-0002", self.rosario)
        self.banco.salvar_contato("Pessoa fictícia inativa", "TESTE-0003", self.centro, False)

    def previa(self):
        return self.banco.preparar(TIPOS[1], [self.centro, self.rosario], "Aviso de teste.", "Hoje, às 18h")

    def test_cadastro_e_associacao_ao_bairro(self):
        contato = next(c for c in self.banco.contatos() if c["id"] == self.a)
        self.assertEqual(contato["bairro"], "Centro")
        self.assertEqual(contato["identificador"], "TESTE-0001")

    def test_um_bairro_exclui_inativos(self):
        self.assertEqual([c[0] for c in self.banco.destinatarios([self.centro])], [self.a])

    def test_multiplos_bairros_sem_repetir_destinatarios(self):
        contatos = self.banco.destinatarios([self.centro, self.rosario, self.centro])
        self.assertEqual(len(contatos), 2)
        self.assertEqual(len({c[0] for c in contatos}), 2)

    def test_identificador_duplicado_e_numero_real_bloqueados(self):
        for identificador in ("TESTE-0001", "teste-0001", "27999999999", "TESTE-12"):
            with self.subTest(identificador=identificador), self.assertRaises(ValueError):
                self.banco.salvar_contato("Fictício", identificador, self.centro)

    def test_contato_sem_nome_ou_bairro_bloqueado(self):
        for nome, bairro in ((" ", self.centro), ("Fictício", None), ("Fictício", 999)):
            with self.subTest(nome=nome, bairro=bairro), self.assertRaises(ValueError):
                self.banco.salvar_contato(nome, "TESTE-0099", bairro)

    def test_edicao_muda_bairro_e_situacao(self):
        self.banco.salvar_contato("Fictício editado", "TESTE-0001", self.rosario, False, self.a)
        self.assertEqual(self.banco.destinatarios([self.centro]), ())
        self.assertEqual(len(self.banco.destinatarios([self.rosario])), 1)
        contato = next(c for c in self.banco.contatos() if c["id"] == self.a)
        self.assertEqual(contato["bairro_id"], self.rosario)
        self.assertEqual(contato["nome"], "Fictício editado")

    def test_bairro_duplicado_bloqueado(self):
        with self.assertRaises(ValueError):
            self.banco.adicionar_bairro("  CENTRO  ")

    def test_comunicados_invalidos_nao_gravam_historico(self):
        for tipo, bairros, mensagem in (
            (TIPOS[0], [], "Teste"), (TIPOS[0], [self.centro], " "),
            ("Inválido", [self.centro], "Teste"), (TIPOS[0], [999], "Teste"),
            (TIPOS[0], [self.vazio], "Teste"), (TIPOS[0], [self.centro], "x" * 5001),
        ):
            with self.subTest(tipo=tipo, bairros=bairros), self.assertRaises(ValueError):
                self.banco.preparar(tipo, bairros, mensagem)
        self.assertEqual(self.banco.historico(), [])

    def test_previa_nao_grava(self):
        self.previa()
        self.assertEqual(self.banco.historico(), [])

    def test_simulacao_e_historico_sem_rede(self):
        with patch("socket.socket", side_effect=AssertionError("Rede proibida")), \
             patch("socket.create_connection", side_effect=AssertionError("Rede proibida")):
            codigo = self.banco.simular(self.previa())
        registro, bairros, contatos = self.banco.detalhes(codigo)
        self.assertEqual(registro["situacao"], "Simulado")
        self.assertEqual(registro["quantidade"], 2)
        self.assertEqual(registro["previsao"], "Hoje, às 18h")
        self.assertEqual(registro["mensagem"], "Aviso de teste.")
        self.assertEqual(bairros, ["Centro", "Rosário I"])
        self.assertEqual(len(contatos), 2)
        self.assertTrue(registro["data"])

    def test_historico_preservado_apos_edicao_e_exclusao(self):
        codigo = self.banco.simular(self.previa())
        self.banco.salvar_contato("Outro nome fictício", "TESTE-0090", self.rosario, True, self.a)
        self.banco.excluir_contato(self.a)
        registro, _, contatos = self.banco.detalhes(codigo)
        self.assertEqual(registro["quantidade"], 2)
        self.assertEqual(contatos[0]["nome"], "Pessoa fictícia A")
        self.assertEqual(contatos[0]["identificador"], "TESTE-0001")

    def test_repeticao_da_confirmacao_bloqueada(self):
        previa = self.previa()
        self.banco.simular(previa)
        with self.assertRaises(ValueError):
            self.banco.simular(previa)
        self.assertEqual(len(self.banco.historico()), 1)

    def test_mudanca_entre_previa_e_confirmacao_exige_nova_conferencia(self):
        previa = self.previa()
        self.banco.salvar_contato("Fictício novo", "TESTE-0088", self.centro)
        with self.assertRaisesRegex(ValueError, "cadastros mudaram"):
            self.banco.simular(previa)
        self.assertEqual(self.banco.historico(), [])

    def test_falha_no_registro_desfaz_operacao_inteira(self):
        self.banco.con.executescript("""
            CREATE TRIGGER falha_teste BEFORE INSERT ON destinatarios
            BEGIN SELECT RAISE(ABORT, 'falha de teste'); END;
        """)
        with self.assertRaises(sqlite3.IntegrityError):
            self.banco.simular(self.previa())
        self.assertEqual(self.banco.historico(), [])
        self.assertEqual(self.banco.con.execute("SELECT COUNT(*) FROM comunicado_bairros").fetchone()[0], 0)


class PersistenciaTest(unittest.TestCase):
    def test_dados_iniciais_persistencia_e_inicializacao_unica(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent, prefix="teste_") as pasta:
            caminho = Path(pasta) / "teste.sqlite3"
            banco = Banco(caminho)
            try:
                self.assertEqual(len(banco.contatos()), 24)
                bairros = [b["id"] for b in banco.bairros()]
                self.assertEqual(len(banco.destinatarios(bairros)), 18)
                self.assertEqual(len(banco.destinatarios(bairros[:2])), 12)
                banco.simular(banco.preparar(TIPOS[0], bairros, "Persistência de teste"))
            finally:
                banco.fechar()
            banco = Banco(caminho)
            try:
                self.assertEqual(len(banco.contatos()), 24)
                self.assertEqual(len(banco.historico()), 1)
                for contato in banco.contatos():
                    banco.excluir_contato(contato["id"])
            finally:
                banco.fechar()
            banco = Banco(caminho)
            try:
                self.assertEqual(banco.contatos(), [])
                self.assertEqual(len(banco.detalhes(1)[2]), 18)
            finally:
                banco.fechar()

    def test_modulos_do_produto_usam_apenas_biblioteca_padrao_sem_integracoes(self):
        permitidos = {"dataclasses", "datetime", "pathlib", "re", "sqlite3", "uuid",
                      "tkinter", "logging", "dados"}
        for nome in ("dados.py", "app.py"):
            arvore = ast.parse(Path(__file__).with_name(nome).read_text(encoding="utf-8"))
            for no in ast.walk(arvore):
                if isinstance(no, ast.Import):
                    for item in no.names:
                        self.assertIn(item.name.split(".")[0], permitidos)
                elif isinstance(no, ast.ImportFrom):
                    self.assertIn(no.module.split(".")[0], permitidos)


if __name__ == "__main__":
    unittest.main()
