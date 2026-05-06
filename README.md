# 🛡️ Zero Trust Access Audit Hub

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data_Engineering-150458.svg)

## 📌 Visão Executiva
O **Zero Trust Audit Hub** é uma plataforma automatizada de auditoria de acessos e Controles Gerais de TI (ITGC). Desenvolvido para atuar como um motor de compliance de alta velocidade, o sistema substitui horas de cruzamento manual de planilhas por uma esteira de dados inteligente que identifica violações de políticas de acesso em milissegundos.

Este projeto nasceu da revisão arquitetural de um **Case Técnico de Auditoria (Big Four)**, evoluindo de simples scripts de validação para um ecossistema completo de engenharia de dados desacoplado e orientado a regras de negócio.

---

## 🎯 Casos de Uso (O que o sistema resolve?)

O motor do sistema realiza o cruzamento multidimensional entre bases do RH (Ativos, Desligados, Transferidos) e os logs do Sistema de TI, cobrindo três pilares fundamentais de auditoria:

1. **Revogação de Acessos (Offboarding):** 
   * Identifica ex-colaboradores que acessaram a rede após a data de demissão (Risco Crítico).
   * Audita SLAs de bloqueio, apontando quando a TI demora mais de 7 dias (contingência) para revogar o acesso (Falha de Controle).
2. **Revisão de Transferências (Segregação de Funções - SoD):** 
   * Detecta colaboradores transferidos de área que ainda mantêm privilégios e módulos do cargo antigo, prevenindo fraudes e acessos indevidos.
3. **Detecção de Contas Fantasmas (Orphan Accounts):** 
   * *Feature Avançada:* Mapeia usuários ativos no sistema de TI que não possuem vínculo mapeado no RH (nem como ativos, nem como desligados), identificando possíveis *backdoors* ou falhas graves de governança.

---

## 🏗️ Arquitetura de Engenharia de Dados

O projeto foi construído utilizando um padrão profissional de **Arquitetura Desacoplada**, separando a interface da lógica de processamento:

```text
zero-trust-access-audit/
├── pipeline/
│   ├── ingestion.py         # Camada Raw: Extração e tipagem inicial dos dados.
│   ├── transformation.py    # Camada Trusted: Motor de cruzamento vetorizado e classificação de risco.
│   └── orchestrator.py      # Maestro: Roteamento de dados entre a ingestão e as regras de negócio.
├── app.py                   # Frontend: Interface de usuário e geração de relatórios (Streamlit).
└── requirements.txt         # Dependências do ambiente.

Tecnologias Utilizadas
Pandas & NumPy: Processamento vetorizado massivo, eliminando loops ineficientes e garantindo performance.

Streamlit: Construção de painéis gerenciais interativos e renderização condicional.

In-Memory Buffers (BytesIO): Geração dinâmica de relatórios Excel multi-abas sem necessidade de gravação no disco do servidor.

##🚀 Como Executar o Projeto
Opção 1: Visualização em Nuvem (Recomendado)
Acesse a aplicação operando em tempo real através do Streamlit Community Cloud:
👉 [https://zero-trust-access-audit.streamlit.app/]

Opção 2: Execução Local
Para rodar a esteira de dados na sua máquina:
```
Clone o repositório:
```bash
git clone [https://github.com/SEU_USUARIO/zero-trust-access-audit.git](https://github.com/SEU_USUARIO/zero-trust-access-audit.git)
```

Crie e ative o ambiente virtual:

```bash
   python -m venv .venv
   source .venv/Scripts/activate  # No Windows
```
Instale as dependências:

```bash
pip install -r requirements.txt
```

Inicie o Servidor de Auditoria:

```Bash
streamlit run app.py
```

📊 Relatório Master Consolidado
A ferramenta conta com um gerador automático de relatórios. Na opção Auditoria Completa, o usuário pode realizar o download de um Parecer de Auditoria em Excel, contendo abas separadas e higienizadas para cada matriz de risco (Desligamentos, Transferências e Fantasmas), entregando o valor de negócio pronto para a tomada de decisão da diretoria