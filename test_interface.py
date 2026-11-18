"""Testes da ligação entre widgets e regras; usam banco em memória."""

import tkinter as tk
from tkinter import ttk
import unittest
from unittest.mock import patch

from app import Aplicativo
from dados import Banco, TIPOS


class InterfaceTest(unittest.TestCase):
    def setUp(self):
        self.banco = Banco(":memory:")
        self.addCleanup(self.banco.fechar)
        self.app = Aplicativo(self.banco)
        self.app.withdraw()
        self.addCleanup(self.app.destroy)

    def filhos(self, widget):
        for filho in widget.winfo_children():
            yield filho
            yield from self.filhos(filho)

    def botao(self, texto):
        return next(w for w in self.filhos(self.app) if isinstance(w, ttk.Button) and w.cget("text") == texto)

    def preparar_formulario(self):
        self.app.tipo.set(TIPOS[1])
        for codigo in list(self.app.bairro_checks)[:2]:
            self.app.bairro_checks[codigo].set(True)
        self.app.mensagem.insert("1.0", "Mensagem fictícia para verificação da interface.")
        self.app.previsao.set("Hoje, às 18h")
        self.app.atualizar_contagem()

    def test_fluxo_completo_com_confirmacao_e_historico(self):
        self.preparar_formulario()
        self.assertIn("12 contato(s)", self.app.contagem.get())
        self.app.conferir()
        self.assertEqual(len(self.banco.historico()), 0)
        with patch("app.messagebox.showinfo") as resultado:
            self.botao("Confirmar simulação").invoke()
        resultado.assert_called_once()
        self.assertEqual(len(self.banco.historico()), 1)
        self.assertEqual(self.app.abas.select(), str(self.app.aba_historico))
        self.assertIn("12", self.app.texto_historico())
        self.assertIn("Mensagem fictícia", self.app.texto_historico())
        self.assertEqual(self.app.mensagem.get("1.0", "end").strip(), "")
        self.assertEqual(self.app.bairros_selecionados(), [])
        self.app.ver_detalhes()
        self.botao("Fechar").invoke()

    def test_voltar_da_conferencia_preserva_rascunho_sem_registrar(self):
        self.preparar_formulario()
        self.app.conferir()
        self.botao("Voltar e editar").invoke()
        self.assertEqual(self.banco.historico(), [])
        self.assertIn("Mensagem fictícia", self.app.mensagem.get("1.0", "end"))

    def test_cadastro_edicao_e_exclusao_pela_interface(self):
        self.app.nome.set("Pessoa fictícia da interface")
        self.app.identificador.set("TESTE-0099")
        self.app.bairro_contato.set("Centro")
        self.app.salvar_contato()
        self.assertEqual(len(self.banco.contatos()), 25)
        self.app.ativo.set(False)
        self.app.salvar_contato()
        self.assertFalse(self.app.contatos_por_id[self.app.contato_id]["ativo"])
        with patch("app.messagebox.askyesno", return_value=False):
            self.app.excluir_contato()
        self.assertEqual(len(self.banco.contatos()), 25)
        with patch("app.messagebox.askyesno", return_value=True):
            self.app.excluir_contato()
        self.assertEqual(len(self.banco.contatos()), 24)

    def test_adicionar_bairro_atualiza_cadastro_e_selecao(self):
        with patch("app.simpledialog.askstring", return_value="Bairro fictício adicional"):
            self.app.adicionar_bairro()
        self.assertIn("Bairro fictício adicional", self.app.combo_bairro.cget("values"))
        self.assertEqual(len(self.app.bairro_checks), 4)

    def test_botoes_visiveis_no_tamanho_minimo_da_janela(self):
        self.app.geometry("940x700")
        self.app.deiconify()
        for aba in (self.app.aba_contatos, self.app.aba_comunicados, self.app.aba_historico):
            self.app.abas.select(aba)
            self.app.update()
            for widget in self.filhos(aba):
                if isinstance(widget, ttk.Button):
                    with self.subTest(botao=widget.cget("text")):
                        self.assertTrue(widget.winfo_ismapped())
                        self.assertGreaterEqual(widget.winfo_height(), widget.winfo_reqheight())
                        self.assertLessEqual(widget.winfo_rooty() + widget.winfo_height(), self.app.winfo_rooty() + self.app.winfo_height())


if __name__ == "__main__":
    unittest.main()
