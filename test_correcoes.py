"""Testes das correções feitas após a validação de usuário (P1 a P7)."""

import unittest
from unittest.mock import patch

from app import Aplicativo, MODELOS
from dados import Banco, TEXTO_EXEMPLO, TIPOS


class CorrecoesDadosTest(unittest.TestCase):
    def setUp(self):
        self.banco = Banco(":memory:")
        self.addCleanup(self.banco.fechar)
        self.centro = next(b["id"] for b in self.banco.bairros() if b["nome"] == "Centro")

    def test_p3_texto_de_exemplo_nao_e_aceito_como_mensagem(self):
        with self.assertRaisesRegex(ValueError, "texto de exemplo"):
            self.banco.preparar(TIPOS[3], [self.centro], TEXTO_EXEMPLO)
        self.assertEqual(self.banco.historico(), [])

    def test_p5_nome_com_telefone_bloqueado(self):
        for nome in ("27 99999-9999", "(27) 99999-9999", "Maria 27999999999", "Ana 3333.4444"):
            with self.subTest(nome=nome), self.assertRaisesRegex(ValueError, "telefone"):
                self.banco.salvar_contato(nome, "TESTE-0090", self.centro)
        # nomes comuns continuam aceitos
        self.banco.salvar_contato("Morador fictício 25", "TESTE-0090", self.centro)

    def test_p7_excluir_bairro_sem_contatos(self):
        novo = self.banco.adicionar_bairro("Bairro criado por engano")
        self.banco.excluir_bairro(novo)
        self.assertNotIn("Bairro criado por engano", [b["nome"] for b in self.banco.bairros()])

    def test_p7_bairro_com_contatos_ou_historico_nao_e_excluido(self):
        with self.assertRaisesRegex(ValueError, "possui contatos"):
            self.banco.excluir_bairro(self.centro)
        novo = self.banco.adicionar_bairro("Bairro usado")
        contato = self.banco.salvar_contato("Morador fictício X", "TESTE-0091", novo)
        self.banco.simular(self.banco.preparar(TIPOS[0], [novo], "Aviso fictício."))
        self.banco.excluir_contato(contato)
        with self.assertRaisesRegex(ValueError, "simulações"):
            self.banco.excluir_bairro(novo)


class CorrecoesInterfaceTest(unittest.TestCase):
    def setUp(self):
        self.banco = Banco(":memory:")
        self.addCleanup(self.banco.fechar)
        self.app = Aplicativo(self.banco)
        self.app.withdraw()
        self.addCleanup(self.app.destroy)

    def test_p1_area_de_bairros_cresce_ate_tres_linhas(self):
        altura_1_linha = int(self.app.canvas_bairros.cget("height"))
        for i in range(4):
            self.banco.adicionar_bairro(f"Bairro fictício {i}")
        self.app.atualizar_bairros()  # 7 bairros = 3 linhas
        self.assertGreaterEqual(int(self.app.canvas_bairros.cget("height")), altura_1_linha * 3)
        for i in range(4, 10):
            self.banco.adicionar_bairro(f"Bairro fictício {i}")
        self.app.atualizar_bairros()  # 13 bairros: limite de 3 linhas + rolagem
        self.assertLess(int(self.app.canvas_bairros.cget("height")), altura_1_linha * 4)
        self.assertTrue(hasattr(self.app, "rolar_bairros"))

    def test_p2_formulario_indica_cadastro_ou_edicao(self):
        self.assertEqual(self.app.botao_salvar.cget("text"), "Cadastrar contato")
        self.app.lista_contatos.selection_set(self.app.lista_contatos.get_children()[0])
        self.app.selecionar_contato()
        self.assertEqual(self.app.botao_salvar.cget("text"), "Salvar alterações")
        self.assertIn("Editando", self.app.form_contato.cget("text"))
        self.app.novo_contato()
        self.assertEqual(self.app.botao_salvar.cget("text"), "Cadastrar contato")
        self.assertIn("Novo contato", self.app.form_contato.cget("text"))

    def test_p4_trocar_tipo_atualiza_modelo_sem_edicao(self):
        self.app.tipo.set(TIPOS[0])
        self.app.usar_modelo()
        self.app.tipo.set(TIPOS[2])
        self.app.trocar_tipo()
        self.assertEqual(self.app.mensagem.get("1.0", "end").strip(), MODELOS[TIPOS[2]])

    def test_p4_trocar_tipo_pergunta_antes_de_apagar_texto_editado(self):
        self.app.mensagem.insert("1.0", "Texto escrito pelo funcionário.")
        self.app.tipo.set(TIPOS[1])
        with patch("app.messagebox.askyesno", return_value=False) as pergunta:
            self.app.trocar_tipo()
        pergunta.assert_called_once()
        self.assertEqual(self.app.mensagem.get("1.0", "end").strip(), "Texto escrito pelo funcionário.")

    def test_p6_status_volta_ao_padrao_ao_trocar_de_aba(self):
        self.app.abas.select(self.app.aba_contatos)
        self.app.avisar("Contato fictício excluído.")
        self.app.abas.select(self.app.aba_comunicados)
        self.app.update()
        self.assertEqual(self.app.status.get(), self.app.status_padrao)


if __name__ == "__main__":
    unittest.main()
