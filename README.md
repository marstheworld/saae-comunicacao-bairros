# 💧 SAAE Baixo Guandu — Comunicação por Bairros

![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)
![Interface](https://img.shields.io/badge/GUI-Tkinter%20%2F%20ttk-lightgrey)
![Database](https://img.shields.io/badge/Database-SQLite3-003B57?logo=sqlite&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-34%20passing-brightgreen)
![Status](https://img.shields.io/badge/Status-Academic%20Prototype-orange)

Protótipo de aplicação desktop desenvolvido para demonstrar como avisos de utilidade pública sobre o abastecimento de água podem ser segmentados e direcionados aos moradores dos bairros afetados no município de Baixo Guandu (ES). 

Projeto desenvolvido no âmbito da **Prática de Extensão Interdisciplinar (PEI)** do curso de **Análise e Desenvolvimento de Sistemas (Multivix)**, vinculado à temática **Comunicação e Cultura**.

> ⚠️ **AVISO DE DEMONSTRAÇÃO:** Este aplicativo opera exclusivamente em ambiente local e offline, utilizando **apenas dados fictícios**. Nenhuma mensagem real (SMS, WhatsApp ou e-mail) é enviada e não há integração com sistemas oficiais da autarquia.

---

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Pré-requisitos e Execução](#-pré-requisitos-e-execução)
- [Guia Rápido de Uso](#-guia-rápido-de-uso)
- [Roteiro de Demonstração (Banca)](#-roteiro-de-demonstração-banca)
- [Suíte de Testes Automatizados](#-suíte-de-testes-automatizados)
- [Arquitetura e Banco de Dados](#-arquitetura-e-banco-de-dados)
- [Escopo e Limitações](#-escopo-e-limitações)

---

## ✨ Funcionalidades

- **Gestão de Contatos Fictícios:** Cadastro, consulta, edição e exclusão de moradores simulados vinculados a bairros e status (*Ativo* ou *Inativo*), com bloqueio automático de números de telefone reais e identificadores duplicados.
- **Gestão Dinâmica de Bairros:** Inclusão e exclusão protegida de bairros na base demonstrativa (impedindo a remoção de áreas com contatos ou históricos vinculados).
- **Preparação de Comunicados:** Categorização por tipo (*Manutenção programada*, *Interrupção emergencial*, *Normalização do abastecimento* e *Outro comunicado*) com modelos editáveis e campo opcional de previsão de retorno.
- **Segmentação em Tempo Real:** Seleção múltipla de bairros com contagem instantânea de destinatários ativos elegíveis, sem duplicidade.
- **Conferência Prévia e Transações Seguras:** Tela obrigatória de revisão antes da confirmação e gravação transacional atômica no banco local.
- **Histórico Imutável:** Registro persistente com data, hora, mensagem e cópia congelada dos destinatários da época da operação.

---

## 🚀 Pré-requisitos e Execução

### Requisitos
- **Sistema Operacional:** Windows (testado no Windows 11).
- **Python:** Versão `3.12` ou superior (verificado com `Python 3.12.10` e `Tk 8.6`).
- **Dependências:** Nenhuma biblioteca externa é necessária (`pip` dispensado). Utiliza apenas a biblioteca padrão do Python (`tkinter`, `sqlite3`, `unittest`). *(Certifique-se de que a opção **Tcl/Tk** esteja marcada na instalação do Python).*

### Como Executar

1. Clone o repositório ou baixe os arquivos do projeto:
   ```bash
   git clone https://github.com/seu-usuario/saae-comunicacao-bairros.git
   cd saae-comunicacao-bairros
   ```

2. **Via Interface (Windows):** Dê um duplo clique no arquivo **`iniciar.pyw`** na pasta raiz do projeto.

3. **Via Terminal (PowerShell / CMD):**
   ```powershell
   python app.py
   ```
   *(Ou `py -3 app.py` caso utilize o launcher padrão do Windows).*

> 💡 **Inicialização do Banco:** Na primeira abertura, o arquivo `dados/prototipo.sqlite3` é gerado automaticamente com **24 contatos fictícios** distribuídos entre *Centro*, *Rosário I* e *Rosário II* (6 ativos e 2 inativos por bairro).

---

## 🖥️ Guia Rápido de Uso

### 1. Aba Contatos
- Clique em **Novo contato**, preencha um nome fictício, um identificador no padrão `TESTE-0001` (4 a 8 dígitos) e selecione o bairro.
- Para editar, clique sobre uma linha da tabela (o formulário exibirá o modo `Editando: TESTE-...`), faça os ajustes e clique em **Salvar alterações**.
- Desmarque **Cadastro ativo** para excluir o contato das simulações sem apagá-lo da base.
- Utilize **Adicionar bairro** ou **Excluir bairro** para gerenciar a lista territorial de demonstração.

### 2. Aba Comunicados
1. Selecione o **Tipo de comunicado**.
2. Marque um ou mais **Bairros afetados** e acompanhe a contagem dinâmica de contatos ativos abaixo da lista.
3. Redija o aviso ou clique em **Usar modelo de mensagem**.
4. *(Opcional)* Informe uma **Previsão de normalização**.
5. Clique em **2. Conferir simulação** para revisar os dados e destinatários.
6. Clique em **Confirmar simulação** para registrar (ou **Voltar e editar** para ajustar o rascunho).

### 3. Aba Histórico
- Consulte todas as simulações gravadas localmente (situação sempre marcada como `Simulado`).
- Selecione uma linha e clique em **Ver detalhes e destinatários** para auditar a lista exata de contatos contemplados naquela data.

---

## 🎯 Roteiro de Demonstração (Banca)

Para validar o fluxo completo em menos de 2 minutos utilizando os dados iniciais:

1. Acesse a aba **Comunicados** e escolha o tipo **Interrupção emergencial**.
2. Selecione os bairros **Centro** e **Rosário I** — o sistema indicará **12 contatos ativos** (ignorando os 4 inativos).
3. Clique em **Usar modelo de mensagem** e preencha uma previsão fictícia (ex.: `Hoje, às 18h`).
4. Clique em **2. Conferir simulação**, valide a lista e clique em **Confirmar simulação**.
5. Observe o resumo de **12 avisos simulados** e verifique o registro gravado na aba **Histórico**.

---

## 🧪 Suíte de Testes Automatizados

O projeto conta com **34 testes automatizados** (`unittest`) que validam regras de negócio, integridade do banco, bloqueio de conexões externas (sockets) e comportamento da interface gráfica. Todos os testes rodam em bancos temporários ou em memória, sem alterar os dados da demonstração.

Dentro da pasta do projeto, execute:

```powershell
# Executar toda a suíte de testes (regras + interface + correções)
python -m unittest -v

# Executar apenas os testes de regras de negócio e banco de dados
python -m unittest -v test_dados

# Salvar o log de execução em arquivo de texto
python -m unittest -v 2>&1 | Tee-Object -FilePath resultado_testes.txt
```

---

## 📂 Arquitetura e Banco de Dados

### Estrutura de Arquivos (`main/`)
```text
main/
├── iniciar.pyw           # Ponto de entrada gráfico no Windows (sem console)
├── app.py                # Interface gráfica (Tkinter/ttk), abas e eventos
├── dados.py              # Camada de persistência (SQLite), validações e regras
├── test_dados.py         # Testes unitários das regras de negócio e banco
├── test_interface.py     # Testes automatizados dos componentes visuais
├── test_correcoes.py     # Testes de regressão das melhorias de usabilidade
├── IMPLEMENTACAO.md      # Documentação técnica detalhada e evidências
└── dados/                # Diretório gerado em tempo de execução
    ├── prototipo.sqlite3 # Banco de dados local SQLite
    └── erros.log         # Registro local de exceções da interface
```

### Modelagem Relacional (SQLite)
O banco local é estruturado em **5 tabelas**:
- `bairros`: Cadastro territorial demonstrativo.
- `contatos`: Registros fictícios vinculados aos bairros e status de atividade.
- `comunicados`: Cabeçalho das operações simuladas (tipo, texto, data/hora e previsão).
- `comunicado_bairros`: Relacionamento N:N entre comunicados e regiões afetadas.
- `destinatarios`: Cópia histórica imutável dos contatos contemplados em cada simulação.

---

## 🔒 Escopo e Limitações

- **Finalidade Acadêmica:** Protótipo desenvolvido exclusivamente para validação conceitual e demonstração de fluxo em ambiente local.
- **Ausência de Integrações:** Não realiza disparos reais via APIs de mensageria (WhatsApp Business, SMS), não possui autenticação de usuários nem criptografia em repouso.
- **Conformidade LGPD:** Embora os identificadores sejam bloqueados para padrões telefônicos, os campos de nome e mensagem são abertos; o sistema não está dimensionado para operar com dados pessoais reais em produção sem análise institucional e adequação legal prévia pelo SAAE.
