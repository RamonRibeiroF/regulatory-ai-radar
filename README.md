# Regulatory AI Radar

[English](#english) | [Português](#português)

## English

### Overview

Regulatory AI Radar is a regulatory intelligence project focused on
Artificial Intelligence, governance, risk, data protection, and
financial-sector regulation.

The application collects publications from regulatory and institutional
sources and stores normalized information for future classification,
analysis, and monitoring.

### Objective

The project aims to:

- automate the collection of regulatory news and publications;
- identify content related to Artificial Intelligence;
- organize publications from multiple regulatory sources;
- prevent duplicate records;
- support future relevance and impact analysis;
- provide structured data for dashboards and automated reports.

### Current capabilities

- Collection of news published by the Brazilian National Data
  Protection Authority (ANPD)
- Extraction of article metadata and content
- Normalization of collected news
- Local persistence with SQLite
- Database mapping and queries with SQLAlchemy
- Duplicate prevention based on article URLs
- Script for listing stored articles

### Planned sources

- Brazilian National Data Protection Authority (ANPD)
- Central Bank of Brazil
- Brazilian Chamber of Deputies
- European AI Office
- Financial Stability Board
- Bank for International Settlements
- International Association of Privacy Professionals (IAPP)
- OECD.AI

### Planned features

- Additional regulatory source collectors
- Artificial Intelligence content classification
- Regulatory relevance scoring
- Identification of impacts on financial institutions
- Automated summaries
- Detection of similar publications
- Monitoring dashboard
- Regulatory change history
- Daily automated collection

### Project structure

```text
regulatory-ai-radar
├── scripts
│   ├── list_articles.py
│   └── run_anpd.py
├── src
│   └── regulatory_ai_radar
│       ├── collectors
│       │   ├── __init__.py
│       │   └── anpd.py
│       ├── database
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── models.py
│       │   ├── repository.py
│       │   └── session.py
│       ├── __init__.py
│       └── entities.py
├── .gitignore
├── pyproject.toml
└── README.md
```

The local `data` directory is created automatically when the
application initializes the database. Its contents are not committed
to Git.

### Requirements

- Python 3.12 or later
- Git
- Internet connection for news collection

### Installation

Clone the repository and enter the project directory:

```powershell
git clone <repository-url>
cd regulatory-ai-radar
```

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate the virtual environment in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project and its dependencies in editable mode:

```powershell
python -m pip install -e .
```

Editable mode allows changes in the source code to be used without
reinstalling the project after each modification.

### Usage

#### Collect and store ANPD news

```powershell
python scripts\run_anpd.py
```

This script:

1. initializes the SQLite database;
2. collects up to five ANPD news articles;
3. normalizes the collected information;
4. stores new articles;
5. skips articles whose URLs already exist;
6. displays a collection and persistence summary.

#### List stored articles

```powershell
python scripts\list_articles.py
```

This script reads the local database and displays the main information
for every stored article.

#### Validate Python files

```powershell
python -m compileall src scripts
```

This command checks the project files for syntax and indentation errors
without running the news collection.

### Database

The application uses SQLite for local persistence. The database is
created automatically at:

```text
data/regulatory_ai_radar.db
```

SQLAlchemy provides the database models, sessions, queries, and
transaction management.

Article URLs are unique in the database and are used to prevent
duplicate records.

### Status

🚧 Under development.

#### Current stage

- [x] Initial project structure
- [x] First ANPD news collector
- [x] Database persistence
- [x] Duplicate prevention
- [x] Stored article listing
- [ ] Additional regulatory sources
- [ ] Relevance ranking
- [ ] Artificial Intelligence classification
- [ ] Dashboard
- [ ] Daily automation

### Technologies

- Python
- Beautiful Soup
- Requests
- SQLAlchemy
- SQLite
- Git

---

## Português

### Visão geral

O Regulatory AI Radar é um projeto de inteligência regulatória voltado
ao acompanhamento de Inteligência Artificial, governança, riscos,
proteção de dados e regulação do setor financeiro.

A aplicação coleta publicações de fontes regulatórias e institucionais
e armazena informações normalizadas para futura classificação, análise
e monitoramento.

### Objetivo

O projeto tem como objetivos:

- automatizar a coleta de notícias e publicações regulatórias;
- identificar conteúdos relacionados à Inteligência Artificial;
- organizar publicações de diferentes fontes regulatórias;
- impedir o armazenamento de registros duplicados;
- apoiar futuras análises de relevância e impacto;
- fornecer dados estruturados para dashboards e relatórios
  automatizados.

### Funcionalidades atuais

- Coleta de notícias publicadas pela Agência Nacional de Proteção de
  Dados (ANPD)
- Extração dos metadados e do conteúdo das notícias
- Normalização das notícias coletadas
- Persistência local com SQLite
- Mapeamento e consultas ao banco com SQLAlchemy
- Prevenção de duplicidades por meio das URLs
- Script para listar as notícias armazenadas

### Fontes planejadas

- Agência Nacional de Proteção de Dados (ANPD)
- Banco Central do Brasil
- Câmara dos Deputados
- European AI Office
- Financial Stability Board
- Bank for International Settlements
- International Association of Privacy Professionals (IAPP)
- OECD.AI

### Funcionalidades planejadas

- Coletores para outras fontes regulatórias
- Classificação de conteúdos relacionados à Inteligência Artificial
- Pontuação de relevância regulatória
- Identificação de impactos para instituições financeiras
- Resumos automatizados
- Detecção de publicações semelhantes
- Dashboard de acompanhamento
- Histórico de mudanças regulatórias
- Coleta diária automatizada

### Estrutura do projeto

```text
regulatory-ai-radar
├── scripts
│   ├── list_articles.py
│   └── run_anpd.py
├── src
│   └── regulatory_ai_radar
│       ├── collectors
│       │   ├── __init__.py
│       │   └── anpd.py
│       ├── database
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── models.py
│       │   ├── repository.py
│       │   └── session.py
│       ├── __init__.py
│       └── entities.py
├── .gitignore
├── pyproject.toml
└── README.md
```

A pasta local `data` é criada automaticamente quando a aplicação
inicializa o banco. Seu conteúdo não é enviado ao Git.

### Requisitos

- Python 3.12 ou superior
- Git
- Conexão com a internet para realizar a coleta

### Instalação

Clone o repositório e entre na pasta do projeto:

```powershell
git clone <url-do-repositorio>
cd regulatory-ai-radar
```

Crie um ambiente virtual:

```powershell
py -m venv .venv
```

Ative o ambiente virtual no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale o projeto e suas dependências em modo editável:

```powershell
python -m pip install -e .
```

O modo editável permite utilizar as alterações feitas no código-fonte
sem reinstalar o projeto depois de cada modificação.

### Utilização

#### Coletar e armazenar notícias da ANPD

```powershell
python scripts\run_anpd.py
```

Esse script:

1. inicializa o banco SQLite;
2. coleta até cinco notícias da ANPD;
3. normaliza as informações coletadas;
4. armazena as notícias novas;
5. ignora notícias cujas URLs já estejam cadastradas;
6. apresenta um resumo da coleta e da persistência.

#### Listar as notícias armazenadas

```powershell
python scripts\list_articles.py
```

Esse script consulta o banco local e apresenta as principais
informações de cada notícia armazenada.

#### Validar os arquivos Python

```powershell
python -m compileall src scripts
```

Esse comando verifica erros de sintaxe e indentação sem executar a
coleta de notícias.

### Banco de dados

A aplicação utiliza SQLite para persistência local. O banco é criado
automaticamente em:

```text
data/regulatory_ai_radar.db
```

O SQLAlchemy fornece os modelos, as sessões, as consultas e o
gerenciamento das transações.

As URLs das notícias são únicas no banco e são utilizadas para impedir
registros duplicados.

### Status

🚧 Em desenvolvimento.

#### Etapa atual

- [x] Estrutura inicial do projeto
- [x] Primeiro coletor de notícias da ANPD
- [x] Persistência em banco de dados
- [x] Prevenção de duplicidades
- [x] Listagem das notícias armazenadas
- [ ] Outras fontes regulatórias
- [ ] Ranking de relevância
- [ ] Classificação com Inteligência Artificial
- [ ] Dashboard
- [ ] Automação diária

### Tecnologias

- Python
- Beautiful Soup
- Requests
- SQLAlchemy
- SQLite
- Git