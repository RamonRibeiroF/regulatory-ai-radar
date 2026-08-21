# Regulatory AI Radar

[English](#english) | [Português](#português)

## English

### Overview

Regulatory AI Radar is a regulatory intelligence project focused on
Artificial Intelligence, governance, risk, data protection, and
financial-sector regulation.

The application collects publications from regulatory and institutional
sources, stores normalized information, calculates an auditable
regulatory relevance score, and presents the results in an interactive
dashboard.

### Objective

The project aims to:

- automate the collection of regulatory news and publications;
- identify content related to Artificial Intelligence;
- organize publications from multiple regulatory sources;
- prevent duplicate records;
- calculate regulatory relevance scores;
- support future impact analysis with Artificial Intelligence;
- provide structured data for dashboards and automated reports.

### Current capabilities

- Collection of news published by the Brazilian National Data
  Protection Authority (ANPD)
- Extraction of article metadata and content
- Normalization of collected news
- Local persistence with SQLite
- Database mapping and queries with SQLAlchemy
- Duplicate prevention based on article URLs
- Deterministic regulatory relevance scoring
- Keyword and category evidence for every score
- Ranking from highest to lowest relevance
- Persistence and updating of article analyses
- Automated unit tests for the scoring rules
- Interactive Streamlit dashboard
- Filters by source, relevance level, minimum score, and text
- Dynamic metrics and ranked regulatory news cards
- Links to the original regulatory publications

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
- Identification of impacts on financial institutions
- Automated summaries
- Detection of similar publications
- Regulatory change history
- Daily automated collection
- Alerts and periodic regulatory reports
- Cloud deployment

### Project structure

```text
regulatory-ai-radar
├── dashboard
│   └── app.py
├── scripts
│   ├── analyze_articles.py
│   ├── list_articles.py
│   └── run_anpd.py
├── src
│   └── regulatory_ai_radar
│       ├── analysis
│       │   ├── __init__.py
│       │   └── relevance.py
│       ├── collectors
│       │   ├── __init__.py
│       │   └── anpd.py
│       ├── database
│       │   ├── __init__.py
│       │   ├── analysis_repository.py
│       │   ├── base.py
│       │   ├── dashboard_repository.py
│       │   ├── models.py
│       │   ├── repository.py
│       │   └── session.py
│       ├── __init__.py
│       └── entities.py
├── tests
│   └── test_relevance.py
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
- Modern web browser for the dashboard

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

#### Analyze and rank stored articles

```powershell
python scripts\analyze_articles.py
```

This script:

1. reads the stored articles;
2. analyzes their title, summary, and body;
3. calculates an explainable relevance score;
4. classifies each article as low, medium, or high relevance;
5. stores or updates the analysis;
6. ranks the articles from highest to lowest score.

#### Launch the dashboard

```powershell
python -m streamlit run dashboard\app.py
```

This command starts the local dashboard. It is normally available at:

```text
http://localhost:8501
```

The dashboard provides:

- total and filtered article metrics;
- number of relevant articles;
- number of high-relevance articles;
- average relevance score;
- filters by source and relevance level;
- minimum score selection;
- relevant-only selection;
- text search;
- ranked regulatory news cards;
- links to original publications.

To stop the local dashboard server, return to the terminal and press:

```text
Ctrl + C
```

#### Validate Python files

```powershell
python -m compileall src scripts tests dashboard
```

This command checks the project files for syntax and indentation errors.

#### Run automated tests

```powershell
python -m unittest discover -s tests -v
```

This command validates the deterministic scoring rules.

### Relevance scoring

The initial relevance model is deterministic and auditable. It does not
use a Large Language Model.

The analyzer:

- normalizes capitalization, accents, punctuation, and whitespace;
- searches for complete regulatory keywords and expressions;
- assigns a predefined weight to each matched keyword;
- adds a 50% bonus when a keyword appears in the title;
- limits the final score to 100;
- records the matched keywords and categories.

The relevance levels are:

| Score | Level | Relevant |
|---:|---|---|
| 0–29 | Low | No |
| 30–59 | Medium | Yes |
| 60–100 | High | Yes |

The deterministic score provides an objective and explainable baseline
for future Artificial Intelligence analysis.

### Dashboard

The Streamlit dashboard reads the local SQLite database through a
dedicated read-only repository.

The interface does not execute news collection or modify relevance
scores. Collection and analysis remain separate operations.

This separation keeps the responsibilities clear:

```text
Collectors
    ↓
News persistence
    ↓
Relevance analysis
    ↓
Analysis persistence
    ↓
Dashboard visualization
```

Dashboard data is cached for a short period to reduce unnecessary
database queries while keeping the interface updated.

### Database

The application uses SQLite for local persistence. The database is
created automatically at:

```text
data/regulatory_ai_radar.db
```

SQLAlchemy provides the database models, sessions, queries, constraints,
and transaction management.

The database currently contains:

- `news_articles`: normalized regulatory news;
- `article_analyses`: relevance scores and supporting evidence.

Article URLs are unique and prevent duplicate news records. Each article
has one current analysis, which is updated when the scoring script runs
again.

The database file is local and is excluded from Git.

### Status

🚧 Under development.

#### Current stage

- [x] Initial project structure
- [x] First ANPD news collector
- [x] Database persistence
- [x] Duplicate prevention
- [x] Stored article listing
- [x] Deterministic relevance ranking
- [x] Analysis persistence
- [x] Automated scoring tests
- [x] Interactive dashboard
- [ ] Additional regulatory sources
- [ ] Artificial Intelligence classification
- [ ] Daily automation
- [ ] Cloud deployment

### Technologies

- Python
- Beautiful Soup
- Requests
- SQLAlchemy
- SQLite
- Streamlit
- Git

---

## Português

### Visão geral

O Regulatory AI Radar é um projeto de inteligência regulatória voltado
ao acompanhamento de Inteligência Artificial, governança, riscos,
proteção de dados e regulação do setor financeiro.

A aplicação coleta publicações de fontes regulatórias e institucionais,
armazena informações normalizadas, calcula um score auditável de
relevância regulatória e apresenta os resultados em um dashboard
interativo.

### Objetivo

O projeto tem como objetivos:

- automatizar a coleta de notícias e publicações regulatórias;
- identificar conteúdos relacionados à Inteligência Artificial;
- organizar publicações de diferentes fontes regulatórias;
- impedir o armazenamento de registros duplicados;
- calcular scores de relevância regulatória;
- apoiar futuras análises de impacto com Inteligência Artificial;
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
- Score determinístico de relevância regulatória
- Evidências de palavras-chave e categorias para cada score
- Ranking da maior para a menor relevância
- Persistência e atualização das análises
- Testes unitários automatizados para as regras de pontuação
- Dashboard interativo com Streamlit
- Filtros por fonte, nível de relevância, score mínimo e texto
- Indicadores dinâmicos e cartões de notícias ranqueadas
- Links para as publicações regulatórias originais

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
- Classificação de conteúdo com Inteligência Artificial
- Identificação de impactos para instituições financeiras
- Resumos automatizados
- Detecção de publicações semelhantes
- Histórico de mudanças regulatórias
- Coleta diária automatizada
- Alertas e relatórios regulatórios periódicos
- Publicação em ambiente de nuvem

### Estrutura do projeto

```text
regulatory-ai-radar
├── dashboard
│   └── app.py
├── scripts
│   ├── analyze_articles.py
│   ├── list_articles.py
│   └── run_anpd.py
├── src
│   └── regulatory_ai_radar
│       ├── analysis
│       │   ├── __init__.py
│       │   └── relevance.py
│       ├── collectors
│       │   ├── __init__.py
│       │   └── anpd.py
│       ├── database
│       │   ├── __init__.py
│       │   ├── analysis_repository.py
│       │   ├── base.py
│       │   ├── dashboard_repository.py
│       │   ├── models.py
│       │   ├── repository.py
│       │   └── session.py
│       ├── __init__.py
│       └── entities.py
├── tests
│   └── test_relevance.py
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
- Navegador moderno para acessar o dashboard

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

#### Analisar e classificar as notícias armazenadas

```powershell
python scripts\analyze_articles.py
```

Esse script:

1. consulta as notícias armazenadas;
2. analisa o título, o resumo e o corpo;
3. calcula um score de relevância explicável;
4. classifica cada notícia como de relevância baixa, média ou alta;
5. armazena ou atualiza a análise;
6. ordena as notícias da maior para a menor pontuação.

#### Iniciar o dashboard

```powershell
python -m streamlit run dashboard\app.py
```

Esse comando inicia o dashboard local. Normalmente, ele estará
disponível em:

```text
http://localhost:8501
```

O dashboard oferece:

- total de notícias encontradas pelos filtros;
- quantidade de notícias relevantes;
- quantidade de notícias com relevância alta;
- média dos scores;
- filtros por fonte e nível de relevância;
- seleção de score mínimo;
- opção para exibir somente notícias relevantes;
- pesquisa textual;
- cartões de notícias ordenados pelo score;
- links para as publicações originais.

Para encerrar o servidor local do dashboard, retorne ao terminal e
pressione:

```text
Ctrl + C
```

#### Validar os arquivos Python

```powershell
python -m compileall src scripts tests dashboard
```

Esse comando verifica erros de sintaxe e indentação nos arquivos do
projeto.

#### Executar os testes automatizados

```powershell
python -m unittest discover -s tests -v
```

Esse comando valida as regras determinísticas de pontuação.

### Score de relevância

O modelo inicial de relevância é determinístico e auditável. Ele não
utiliza um Large Language Model.

O analisador:

- normaliza letras maiúsculas, acentos, pontuação e espaços;
- procura palavras-chave e expressões regulatórias completas;
- atribui um peso predefinido a cada termo encontrado;
- adiciona um bônus de 50% quando o termo aparece no título;
- limita o score final a 100;
- registra as palavras e categorias encontradas.

As faixas de relevância são:

| Score | Nível | Relevante |
|---:|---|---|
| 0–29 | Baixa | Não |
| 30–59 | Média | Sim |
| 60–100 | Alta | Sim |

O score determinístico fornece uma base objetiva e explicável para uma
futura análise com Inteligência Artificial.

### Dashboard

O dashboard do Streamlit consulta o banco SQLite local por meio de um
repositório dedicado exclusivamente à leitura.

A interface não executa a coleta de notícias nem modifica os scores de
relevância. A coleta e a análise permanecem como operações separadas.

Essa separação mantém claras as responsabilidades:

```text
Coletores
    ↓
Persistência das notícias
    ↓
Análise de relevância
    ↓
Persistência das análises
    ↓
Visualização no dashboard
```

Os dados do dashboard são mantidos em cache por um curto período para
reduzir consultas desnecessárias e manter a interface atualizada.

### Banco de dados

A aplicação utiliza SQLite para persistência local. O banco é criado
automaticamente em:

```text
data/regulatory_ai_radar.db
```

O SQLAlchemy fornece os modelos, sessões, consultas, restrições e
gerenciamento das transações.

Atualmente, o banco contém:

- `news_articles`: notícias regulatórias normalizadas;
- `article_analyses`: scores de relevância e suas evidências.

As URLs das notícias são únicas e impedem registros duplicados. Cada
notícia possui uma análise atual, que é atualizada quando o script de
pontuação é executado novamente.

O arquivo do banco é local e não é enviado ao Git.

### Status

🚧 Em desenvolvimento.

#### Etapa atual

- [x] Estrutura inicial do projeto
- [x] Primeiro coletor de notícias da ANPD
- [x] Persistência em banco de dados
- [x] Prevenção de duplicidades
- [x] Listagem das notícias armazenadas
- [x] Ranking determinístico de relevância
- [x] Persistência das análises
- [x] Testes automatizados do score
- [x] Dashboard interativo
- [ ] Outras fontes regulatórias
- [ ] Classificação com Inteligência Artificial
- [ ] Automação diária
- [ ] Publicação em ambiente de nuvem

### Tecnologias

- Python
- Beautiful Soup
- Requests
- SQLAlchemy
- SQLite
- Streamlit
- Git