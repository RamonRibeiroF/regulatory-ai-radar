# Regulatory AI Radar

[English](#english) | [Português](#português)

## English

### Overview

Regulatory AI Radar is a regulatory intelligence project focused on
Artificial Intelligence, governance, risk, data protection, and
financial-sector regulation.

The application collects publications from regulatory, financial, and
legislative sources, stores normalized information, calculates an
auditable regulatory relevance score, and presents the results in an
interactive dashboard.

### Objective

The project aims to:

- automate the collection of regulatory news and legislative
  propositions;
- identify content related to Artificial Intelligence;
- organize publications from multiple regulatory sources;
- prevent duplicate records;
- calculate regulatory relevance scores;
- support future impact analysis with Artificial Intelligence;
- provide structured data for dashboards and automated reports.

### Current sources

- Brazilian National Data Protection Authority (ANPD)
- Central Bank of Brazil (BCB)
- Brazilian Chamber of Deputies

### Current capabilities

- Collection of official ANPD news
- Collection of official BCB news through its Atom feed
- Collection of legislative propositions through the official Chamber
  of Deputies API
- Search for legislative propositions by regulatory topics
- Explicit newest-to-oldest publication ordering
- Extraction of publication metadata and content
- Normalization through a shared news structure
- Local persistence with SQLite
- Database mapping and queries with SQLAlchemy
- Duplicate prevention based on publication URLs
- Deterministic regulatory relevance scoring
- Keyword and category evidence for every score
- Ranking from highest to lowest relevance
- Persistence and updating of article analyses
- Automated tests for scoring and collection rules
- Interactive Streamlit dashboard
- Filters by source, relevance level, minimum score, and text
- Dynamic metrics and ranked regulatory publication cards
- Links to the original official publications

### Planned sources

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
│   ├── run_anpd.py
│   ├── run_bcb.py
│   └── run_camara.py
├── src
│   └── regulatory_ai_radar
│       ├── analysis
│       │   ├── __init__.py
│       │   └── relevance.py
│       ├── collectors
│       │   ├── __init__.py
│       │   ├── anpd.py
│       │   ├── bcb.py
│       │   └── camara.py
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
│   ├── test_bcb_collector.py
│   ├── test_camara_collector.py
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
- Internet connection for publication collection
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

#### Collect and store BCB news

```powershell
python scripts\run_bcb.py
```

This script:

1. accesses the official BCB Atom feed;
2. selects the current year automatically;
3. parses every valid feed entry;
4. rejects links outside the official BCB domain;
5. sorts articles explicitly from newest to oldest;
6. selects up to five recent articles;
7. stores new articles;
8. skips URLs that already exist.

#### Collect and store Chamber of Deputies propositions

```powershell
python scripts\run_camara.py
```

This script:

1. accesses the official Chamber of Deputies API;
2. searches recent propositions using regulatory keywords;
3. limits the search to selected legislative proposition types;
4. searches propositions presented during the last 90 days;
5. removes propositions returned by multiple searches;
6. sorts all valid propositions from newest to oldest;
7. selects up to five recent propositions;
8. stores new propositions;
9. skips URLs that already exist.

#### List stored publications

```powershell
python scripts\list_articles.py
```

This script reads the local database and displays the main information
for every stored publication.

#### Analyze and rank stored publications

```powershell
python scripts\analyze_articles.py
```

This script:

1. reads the stored publications from every source;
2. analyzes their title, summary, and body;
3. calculates an explainable relevance score;
4. classifies each publication as low, medium, or high relevance;
5. stores or updates the analysis;
6. ranks the publications from highest to lowest score.

Run the analysis script again after collecting publications from any
source so that the new records receive relevance scores.

#### Launch the dashboard

```powershell
python -m streamlit run dashboard\app.py
```

This command starts the local dashboard. It is normally available at:

```text
http://localhost:8501
```

The dashboard provides:

- total and filtered publication metrics;
- number of relevant publications;
- number of high-relevance publications;
- average relevance score;
- filters for ANPD, BCB, CAMARA, and future sources;
- filters by relevance level;
- minimum score selection;
- relevant-only selection;
- text search;
- ranked regulatory publication cards;
- links to original official publications.

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

The automated test suite currently contains 14 tests and validates:

- relevance score calculation;
- relevance thresholds;
- accent and capitalization normalization;
- maximum score enforcement;
- BCB Atom feed parsing;
- newest-to-oldest BCB ordering;
- BCB URL normalization;
- rejection of external BCB domains;
- BCB collection limits without unnecessary network requests;
- newest-to-oldest Chamber proposition ordering;
- Chamber proposition normalization;
- removal of duplicate Chamber search results;
- Chamber collection limits without unnecessary network requests;
- rejection of invalid Chamber search periods.

### Data normalization

All collectors return the same `NewsItem` structure:

```text
source
title
url
published_at
summary
body
collected_at
```

This shared contract allows the database, relevance analyzer, and
dashboard to process content without depending on the original source.

### BCB collection strategy

The BCB collector uses the institution's official Atom feed:

```text
https://www.bcb.gov.br/api/feed/sitebcb/sitefeeds/noticias
```

The current year is sent through the `ano` query parameter.

The feed already provides titles, publication dates, official links,
and article content. The collector still performs its own descending
date sort before applying the requested limit. This ensures that it
always selects the most recent entries even if the feed order changes.

Only links belonging to these domains are accepted:

```text
bcb.gov.br
www.bcb.gov.br
```

Query parameters and URL fragments are removed before persistence to
improve duplicate detection.

### Chamber of Deputies collection strategy

The Chamber collector uses the official Open Data REST API:

```text
https://dadosabertos.camara.leg.br/api/v2/proposicoes
```

The collector searches propositions associated with the following
regulatory topics:

```text
artificial intelligence
algorithms
data protection
personal data
cybersecurity
virtual assets
financial system
central bank
```

The original API searches are performed in Portuguese.

The collector currently considers these proposition types:

```text
PL
PLP
PEC
MPV
PDL
```

The default search period covers the last 90 days. Results returned by
multiple keyword searches are deduplicated through their official
proposition identifiers.

All valid results are explicitly sorted by presentation date before the
final limit is applied. This ensures that the collector selects the most
recent propositions across every configured topic.

Each proposition is linked to its official public tracking page:

```text
https://www.camara.leg.br/proposicoesWeb/fichadetramitacao
```

The proposition identifier is retained in the URL so that each record
remains unique and opens the correct legislative page.

The collection step identifies potential regulatory publications. The
relevance analyzer subsequently decides whether each proposition has
low, medium, or high relevance for the project.

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

The interface does not execute publication collection or modify
relevance scores. Collection and analysis remain separate operations.

This separation keeps the responsibilities clear:

```text
Regulatory and legislative sources
    ↓
Source collectors
    ↓
Publication normalization
    ↓
Publication persistence
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

- `news_articles`: normalized regulatory publications from every
  source;
- `article_analyses`: relevance scores and supporting evidence.

Publication URLs are unique and prevent duplicate records. Each
publication has one current analysis, which is updated when the scoring
script runs again.

The database file is local and is excluded from Git.

### Status

🚧 Under development.

#### Current stage

- [x] Initial project structure
- [x] ANPD news collector
- [x] BCB news collector
- [x] Chamber of Deputies proposition collector
- [x] Shared publication normalization
- [x] Database persistence
- [x] Duplicate prevention
- [x] Stored publication listing
- [x] Deterministic relevance ranking
- [x] Analysis persistence
- [x] Automated scoring tests
- [x] Automated BCB collector tests
- [x] Automated Chamber collector tests
- [x] Interactive multi-source dashboard
- [ ] Additional international regulatory sources
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
- XML and Atom
- REST APIs and JSON
- Git

---

## Português

### Visão geral

O Regulatory AI Radar é um projeto de inteligência regulatória voltado
ao acompanhamento de Inteligência Artificial, governança, riscos,
proteção de dados e regulação do setor financeiro.

A aplicação coleta publicações de fontes regulatórias, financeiras e
legislativas, armazena informações normalizadas, calcula um score
auditável de relevância regulatória e apresenta os resultados em um
dashboard interativo.

### Objetivo

O projeto tem como objetivos:

- automatizar a coleta de notícias regulatórias e proposições
  legislativas;
- identificar conteúdos relacionados à Inteligência Artificial;
- organizar publicações de diferentes fontes regulatórias;
- impedir o armazenamento de registros duplicados;
- calcular scores de relevância regulatória;
- apoiar futuras análises de impacto com Inteligência Artificial;
- fornecer dados estruturados para dashboards e relatórios
  automatizados.

### Fontes atuais

- Agência Nacional de Proteção de Dados (ANPD)
- Banco Central do Brasil (BCB)
- Câmara dos Deputados

### Funcionalidades atuais

- Coleta de notícias oficiais da ANPD
- Coleta de notícias oficiais do BCB por meio de seu feed Atom
- Coleta de proposições legislativas por meio da API oficial da Câmara
  dos Deputados
- Pesquisa de proposições legislativas por temas regulatórios
- Ordenação explícita das publicações da mais recente para a mais antiga
- Extração dos metadados e do conteúdo das publicações
- Normalização por meio de uma estrutura compartilhada
- Persistência local com SQLite
- Mapeamento e consultas ao banco com SQLAlchemy
- Prevenção de duplicidades por meio das URLs
- Score determinístico de relevância regulatória
- Evidências de palavras-chave e categorias para cada score
- Ranking da maior para a menor relevância
- Persistência e atualização das análises
- Testes automatizados para as regras de score e coleta
- Dashboard interativo com Streamlit
- Filtros por fonte, nível de relevância, score mínimo e texto
- Indicadores dinâmicos e cartões de publicações ranqueadas
- Links para as publicações oficiais originais

### Fontes planejadas

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
│   ├── run_anpd.py
│   ├── run_bcb.py
│   └── run_camara.py
├── src
│   └── regulatory_ai_radar
│       ├── analysis
│       │   ├── __init__.py
│       │   └── relevance.py
│       ├── collectors
│       │   ├── __init__.py
│       │   ├── anpd.py
│       │   ├── bcb.py
│       │   └── camara.py
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
│   ├── test_bcb_collector.py
│   ├── test_camara_collector.py
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
- Conexão com a internet para realizar as coletas
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

#### Coletar e armazenar notícias do BCB

```powershell
python scripts\run_bcb.py
```

Esse script:

1. acessa o feed Atom oficial do BCB;
2. seleciona automaticamente o ano atual;
3. interpreta todas as entradas válidas;
4. rejeita links externos ao domínio oficial;
5. ordena as notícias da mais recente para a mais antiga;
6. seleciona até cinco notícias recentes;
7. armazena as notícias novas;
8. ignora URLs que já estejam cadastradas.

#### Coletar e armazenar proposições da Câmara

```powershell
python scripts\run_camara.py
```

Esse script:

1. acessa a API oficial da Câmara dos Deputados;
2. pesquisa proposições recentes por palavras-chave regulatórias;
3. limita a pesquisa aos tipos de proposições legislativas selecionados;
4. pesquisa proposições apresentadas nos últimos 90 dias;
5. remove proposições encontradas por mais de uma pesquisa;
6. ordena todos os resultados válidos da data mais recente para a mais
   antiga;
7. seleciona até cinco proposições recentes;
8. armazena as novas proposições;
9. ignora URLs que já estejam cadastradas.

#### Listar as publicações armazenadas

```powershell
python scripts\list_articles.py
```

Esse script consulta o banco local e apresenta as principais
informações de cada publicação armazenada.

#### Analisar e classificar as publicações armazenadas

```powershell
python scripts\analyze_articles.py
```

Esse script:

1. consulta as publicações armazenadas de todas as fontes;
2. analisa o título, o resumo e o corpo;
3. calcula um score de relevância explicável;
4. classifica cada publicação como de relevância baixa, média ou alta;
5. armazena ou atualiza a análise;
6. ordena as publicações da maior para a menor pontuação.

Execute novamente o script de análise depois de coletar publicações de
qualquer fonte para que os novos registros recebam seus scores.

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

- total de publicações encontradas pelos filtros;
- quantidade de publicações relevantes;
- quantidade de publicações com relevância alta;
- média dos scores;
- filtros para ANPD, BCB, CAMARA e fontes futuras;
- filtros por nível de relevância;
- seleção de score mínimo;
- opção para exibir somente publicações relevantes;
- pesquisa textual;
- cartões de publicações ordenados pelo score;
- links para as publicações oficiais originais.

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

A suíte contém atualmente 14 testes automatizados que validam:

- cálculo do score de relevância;
- faixas de relevância;
- normalização de acentos e letras maiúsculas;
- limite máximo do score;
- interpretação do feed Atom do BCB;
- ordenação das notícias do BCB;
- normalização das URLs do BCB;
- rejeição de domínios externos no coletor do BCB;
- limites de coleta do BCB sem requisições desnecessárias;
- ordenação das proposições da Câmara;
- normalização das proposições da Câmara;
- remoção de resultados repetidos nas pesquisas da Câmara;
- limites de coleta da Câmara sem requisições desnecessárias;
- rejeição de períodos de pesquisa inválidos.

### Normalização dos dados

Todos os coletores retornam a mesma estrutura `NewsItem`:

```text
source
title
url
published_at
summary
body
collected_at
```

Esse contrato compartilhado permite que o banco, o analisador e o
dashboard processem o conteúdo sem depender da fonte original.

### Estratégia de coleta do BCB

O coletor do BCB utiliza o feed Atom oficial da instituição:

```text
https://www.bcb.gov.br/api/feed/sitebcb/sitefeeds/noticias
```

O ano atual é enviado por meio do parâmetro `ano`.

O feed já disponibiliza títulos, datas de publicação, links oficiais e
conteúdo. Mesmo assim, o coletor realiza sua própria ordenação
decrescente antes de aplicar o limite solicitado. Isso garante que as
notícias mais recentes sejam selecionadas mesmo que a ordem do feed
seja alterada.

Somente links pertencentes aos seguintes domínios são aceitos:

```text
bcb.gov.br
www.bcb.gov.br
```

Parâmetros de consulta e fragmentos são removidos das URLs antes da
persistência para melhorar a detecção de duplicidades.

### Estratégia de coleta da Câmara dos Deputados

O coletor da Câmara utiliza a API REST oficial de Dados Abertos:

```text
https://dadosabertos.camara.leg.br/api/v2/proposicoes
```

O coletor pesquisa proposições relacionadas aos seguintes temas
regulatórios:

```text
inteligência artificial
algoritmos
proteção de dados
dados pessoais
cibersegurança
ativos virtuais
sistema financeiro
banco central
```

Atualmente, são considerados estes tipos de proposições:

```text
PL
PLP
PEC
MPV
PDL
```

O período padrão de pesquisa corresponde aos últimos 90 dias. Os
resultados encontrados em mais de uma pesquisa são deduplicados por
meio do identificador oficial da proposição.

Todos os resultados válidos são ordenados explicitamente pela data de
apresentação antes da aplicação do limite final. Isso garante a seleção
das proposições mais recentes entre todos os temas configurados.

Cada proposição recebe um link para sua página pública oficial de
tramitação:

```text
https://www.camara.leg.br/proposicoesWeb/fichadetramitacao
```

O identificador da proposição permanece na URL para que cada registro
seja único e abra a página legislativa correta.

A coleta identifica publicações potencialmente regulatórias. Depois
disso, o analisador de relevância determina se cada proposição possui
relevância baixa, média ou alta para o projeto.

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

A interface não executa a coleta de publicações nem modifica os scores
de relevância. A coleta e a análise permanecem como operações
separadas.

Essa separação mantém claras as responsabilidades:

```text
Fontes regulatórias e legislativas
    ↓
Coletores das fontes
    ↓
Normalização das publicações
    ↓
Persistência das publicações
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

- `news_articles`: publicações regulatórias normalizadas de todas as
  fontes;
- `article_analyses`: scores de relevância e suas evidências.

As URLs das publicações são únicas e impedem registros duplicados. Cada
publicação possui uma análise atual, que é atualizada quando o script de
pontuação é executado novamente.

O arquivo do banco é local e não é enviado ao Git.

### Status

🚧 Em desenvolvimento.

#### Etapa atual

- [x] Estrutura inicial do projeto
- [x] Coletor de notícias da ANPD
- [x] Coletor de notícias do BCB
- [x] Coletor de proposições da Câmara dos Deputados
- [x] Normalização compartilhada das publicações
- [x] Persistência em banco de dados
- [x] Prevenção de duplicidades
- [x] Listagem das publicações armazenadas
- [x] Ranking determinístico de relevância
- [x] Persistência das análises
- [x] Testes automatizados do score
- [x] Testes automatizados do coletor do BCB
- [x] Testes automatizados do coletor da Câmara
- [x] Dashboard interativo com múltiplas fontes
- [ ] Outras fontes regulatórias internacionais
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
- XML e Atom
- APIs REST e JSON
- Git