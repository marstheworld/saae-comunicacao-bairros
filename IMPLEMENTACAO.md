# 🌟 Resumo de Implementação & Portfólio técnico

<p align="center">
  <b>Protótipo Desktop Acadêmico • SAAE de Baixo Guandu (ES)</b>
  <br>
  <i>Prática de Extensão Interdisciplinar (PEI) — Análise e Desenvolvimento de Sistemas (Multivix)</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Concluído-success?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Domain-Comunicação_e_Cultura-blueviolet?style=for-the-badge" alt="Tema">
  <img src="https://img.shields.io/badge/QA-21_Testes_Aprovados-informational?style=for-the-badge" alt="Testes">
</p>

---

## 🎯 Visão Geral da Solução
Solução de engenharia desenvolvida para estruturar canais diretos de utilidade pública, mitigando gargalos na divulgação de manutenções e interrupções no abastecimento de água. 

* **Abordagem Tecnológica:** Aplicação desktop nativa para Windows estruturada com pilha 100% interna e desacoplada de serviços externos.
* **Segurança e Privacidade:** Arquitetura isolada projetada sob premissas estritamente acadêmicas, utilizando malha de dados puramente sintética (`TESTE-XXXX`) e operação offline.

---

## ⚙️ Core Features & Funcionalidades

- **CRUD de Moradores Fictícios:** Gestão completa de cadastros vinculados a matrizes territoriais e bandeiras de atividade (*Ativo*/*Inativo*).
- **Dinamismo Geográfico:** Interface escalável para injeção e manipulação de setores/bairros em tempo de execução.
- **Motor de Comunicados:** Sistema multicanal taxonomia em quatro categorias operacionais com templates editáveis e janelas de previsão de restabelecimento.
- **Filtro de Segmentação Relacional:** Seleção multi-setorial com apuração instantânea e blindagem contra duplicações de registros ativos.
- **Auditoria Transacional:** Mecanismo de dupla checagem (*Conferência Prévia*) atrelado à persistência atômica via transações SQLite.
- **Histórico Imutável:** Repositório de rastreabilidade temporal com "congelamento" estrutural de destinatários por evento.

---

## 🧠 Arquitetura de Dados & Decisões de Engenharia

* **Snapshots de Histórico:** Armazenamento desnormalizado de cópias de dados no histórico para assegurar que alterações cadastrais posteriores não retroajam corrompendo auditorias passadas.
* **Atomicidade de Transações:** Blocos de gravação operados sob diretrizes ACID em SQLite, revertendo estados incompletos em caso de interrupções.
* **Integridade de Estado:** Validação rígida de divergência temporal (exigência de recálculo/revisão caso alterações ocorram entre a tela de conferência e o commit).
* **Proteção de Inicialização:** Sistema de *bootstrap* automatizado com flags de persistência que impedem recriações cíclicas de dados de demonstração após limpezas manuais.
* **Isolamento de Testes:** Sandboxing total de suítes de qualidade em instâncias na memória RAM (`in-memory`) e diretórios voláteis temporários.

---

## 🛡️ Auditoria de Qualidade & Testes

> Homologado em **03/11/2026** sob ambiente Windows com **Python 3.12.10**, **Tk 8.6** e **SQLite 3.49.1**.

* **Cobertura Automatizada:** Validação de 21 cenários de estresse cobrindo integridade de chaves, restrições de formato anti-telefonia, inativação por regras de negócio e reversões transacionais.
* **Blindagem de Sockets:** Testes de intrusão lógica que bloqueiam qualquer tentativa de handshake ou abertura de sockets externos.
* **Inspeção Estática:** Auditoria de *imports* da árvore de módulos para assegurar a pureza do escopo offline.
* **Homologação Visual:** Validação prática de seleções cruzadas (ex: cruzamento *Centro + Rosário I* totalizando exatamente 12 alvos ativos em auditoria visual de janela).

---

## 📸 Guia de Evidências Visuais para Apresentação

1. **Painel de Cadastros:** Exibição da aba *Contatos* destacando identificadores padronizados e matriz de ativos.
2. **Filtro Territorial:** Demonstração do cruzamento de setores (*Centro + Rosário I*) refletindo o quantitativo exato de 12 alvos computados.
3. **Tela de Auditoria:** Janela de conferência de rascunho com o selo explícito de simulação isolada.
4. **Modal de Sucesso:** Confirmação de disparo em ambiente fechado.
5. **Livro de Registros:** Auditoria detalhada na aba *Histórico* evidenciando a integridade dos metadados salvos.
6. **Output de Testes:** Captura de tela ou arquivo de texto da suíte de testes executando o comando `python -m unittest -v` com status `OK`.

---

## 📌 Limites Estruturais do Escopo

* Entrega de cunho estritamente acadêmico/científico e conceitual.
* Desprovido de camadas de autenticação de usuários, módulos de instaladores empacotados (`.exe`) ou integrações nativas com gateways corporativos de mensageria (SMS/WhatsApp).
