# Regulatory AI Radar

[English](#english) | [Português](#português)

## English

### Overview

Regulatory AI Radar is a regulatory intelligence project focused on Artificial Intelligence, governance, risk, data protection, financial regulation, and legislative monitoring.

The application collects publications from official national and international sources, normalizes and stores their content, calculates an auditable regulatory relevance score, and presents the results in an interactive dashboard.

### Objectives

The project aims to:

- automate regulatory and legislative publication collection;
- prioritize the most recent publications;
- identify content related to Artificial Intelligence and regulation;
- organize publications from multiple official sources;
- prevent duplicate records;
- calculate explainable regulatory relevance scores;
- support future AI-assisted impact analysis;
- provide structured information for dashboards and reports.

### Current sources

- Brazilian National Data Protection Authority (ANPD)
- Central Bank of Brazil (BCB)
- Brazilian Chamber of Deputies
- European Commission — Artificial Intelligence topic
- Financial Stability Board (FSB)

### Current capabilities

- Collection from five official sources
- Explicit newest-to-oldest ordering
- Extraction of titles, dates, summaries, content, and official URLs
- Official domain and publication-path validation
- Shared publication normalization
- Local SQLite persistence
- Database mapping and queries with SQLAlchemy
- Duplicate prevention through unique publication URLs
- Deterministic regulatory relevance scoring
- Keyword and category evidence for every score
- Ranking from highest to lowest relevance
- Persistence and updating of analyses
- Interactive Streamlit dashboard
- Filters by source, level, minimum score, relevance, and text
- Dynamic metrics and ranked publication cards
- Links to original official publications
- Automated collector and relevance tests

### Planned sources

- Bank for International Settlements (BIS)
- International Association of Privacy Professionals (IAPP)
- OECD.AI

### Planned features

- Additional regulatory collectors
- AI-assisted content classification
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
│   ├── run_camara.py
│   ├── run_eu_ai_office.py
│   └── run_fsb.py
├── src
│   └── regulatory_ai_radar
│       ├── analysis
│       │   ├── __init__.py
│       │   └── relevance.py
│       ├── collectors
│       │   ├── __init__.py
│       │   ├── anpd.py
│       │   ├── bcb.py
│       │   ├── camara.py
│       │   ├── eu_ai_office.py
│       │   └── fsb.py
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
│   ├── test_eu_ai_office_collector.py
│   ├── test_fsb_collector.py
│   └── test_relevance.py
├── .gitignore
├── pyproject.toml
└── README.md
```

The local `data` directory is created automatically when the application initializes the database. Its contents are excluded from Git.

### Requirements

- Python 3.12 or later
- Git
- Internet connection for publication collection
- Modern web browser for the dashboard

### Installation

Clone the repository and enter its directory:

```powershell
git clone <repository-url>
cd regulatory-ai-radar
```

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project and its dependencies in editable mode:

```powershell
python -m pip install -e .
```

Editable mode allows source-code changes to be used without reinstalling the project after every modification.

### Usage

#### Collect ANPD news

```powershell
python scripts\run_anpd.py
```

This script:

1. initializes the SQLite database;
2. collects up to five recent ANPD news articles;
3. normalizes the collected data;
4. stores new articles;
5. skips URLs already stored;
6. displays a persistence summary.

#### Collect BCB news

```powershell
python scripts\run_bcb.py
```

This script:

1. accesses the official BCB Atom feed;
2. selects the current year automatically;
3. parses valid feed entries;
4. rejects external links;
5. sorts articles from newest to oldest;
6. selects up to five recent articles;
7. stores new articles;
8. skips duplicates.

#### Collect Chamber of Deputies propositions

```powershell
python scripts\run_camara.py
```

This script:

1. accesses the official Chamber of Deputies API;
2. searches recent propositions using regulatory topics;
3. limits the search to selected proposition types;
4. searches the configured recent period;
5. removes repeated search results;
6. sorts propositions from newest to oldest;
7. selects up to five propositions;
8. stores new records;
9. skips duplicates.

#### Collect European AI publications

```powershell
python scripts\run_eu_ai_office.py
```

This script:

1. accesses the European Commission digital strategy portal;
2. selects the official Artificial Intelligence topic;
3. identifies publication cards and dates;
4. validates official European Commission links;
5. removes repeated links;
6. sorts candidates from newest to oldest;
7. opens only the necessary detail pages;
8. extracts titles, summaries, and content;
9. stores new publications;
10. skips duplicates.

#### Collect FSB publications

```powershell
python scripts\run_fsb.py
```

This script:

1. accesses the official FSB Financial Innovation page;
2. identifies official publication cards;
3. extracts titles, publication dates, summaries, and URLs;
4. validates FSB domains and dated publication paths;
5. removes repeated publication URLs;
6. sorts candidates from newest to oldest;
7. opens only the detail pages required by the limit;
8. extracts normalized publication content;
9. stores up to five recent publications;
10. skips URLs already stored.

#### List stored publications

```powershell
python scripts\list_articles.py
```

This script reads the local database and displays the main information for every stored publication.

#### Analyze and rank publications

```powershell
python scripts\analyze_articles.py
```

This script:

1. reads publications from every source;
2. analyzes titles, summaries, and bodies;
3. calculates an explainable relevance score;
4. classifies publications as low, medium, or high relevance;
5. stores or updates each analysis;
6. ranks publications from highest to lowest score.

Run this script again after collecting new publications so the new records receive relevance scores.

#### Launch the dashboard

```powershell
python -m streamlit run dashboard\app.py
```

The local dashboard is normally available at:

```text
http://localhost:8501
```

The dashboard provides:

- total and filtered publication metrics;
- number of relevant publications;
- number of high-relevance publications;
- average relevance score;
- source filters for ANPD, BCB, CAMARA, EU_AI_OFFICE, and FSB;
- relevance-level filters;
- minimum-score selection;
- relevant-only selection;
- text search;
- ranked regulatory publication cards;
- links to original publications.

To stop the dashboard, return to the terminal and press:

```text
Ctrl + C
```

### Validation

Check all Python files for syntax and indentation errors:

```powershell
python -m compileall src scripts tests dashboard
```

Run the automated test suite:

```powershell
python -m unittest discover -s tests -v
```

The suite currently contains 26 tests covering:

- relevance score calculation;
- relevance thresholds;
- accent and capitalization normalization;
- article-body score contribution;
- maximum score enforcement;
- BCB Atom feed parsing and ordering;
- BCB URL normalization and domain validation;
- BCB collection limits;
- Chamber proposition ordering and normalization;
- Chamber duplicate removal and period validation;
- European publication ordering and normalization;
- European URL validation and collection limits;
- FSB publication ordering;
- FSB duplicate-card removal;
- FSB official-domain validation;
- FSB article-content normalization;
- FSB collection-limit enforcement;
- zero-limit collection without network requests.

### Data normalization

Every collector returns the same `NewsItem` structure:

```text
source
title
url
published_at
summary
body
collected_at
```

This shared contract allows the database, relevance analyzer, and dashboard to process publications without depending on their original source.

### Collection strategies

#### BCB

The BCB collector uses the institution’s official Atom feed:

```text
https://www.bcb.gov.br/api/feed/sitebcb/sitefeeds/noticias
```

The current year is sent through the `ano` parameter. Entries are explicitly sorted before the collection limit is applied.

Only these domains are accepted:

```text
bcb.gov.br
www.bcb.gov.br
```

Query parameters and fragments are removed before persistence.

#### Chamber of Deputies

The Chamber collector uses the official Open Data API:

```text
https://dadosabertos.camara.leg.br/api/v2/proposicoes
```

The collector searches propositions associated with regulatory topics such as:

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

The original searches are performed in Portuguese.

The selected proposition types are:

```text
PL
PLP
PEC
MPV
PDL
```

Results returned by multiple searches are deduplicated through their official identifiers and sorted by presentation date.

#### European AI publications

The European collector uses the official Shaping Europe’s Digital Future portal:

```text
https://digital-strategy.ec.europa.eu/en/news
```

The listing uses the official Artificial Intelligence topic:

```text
topic=119
```

Only HTTPS links from the following domain and path are accepted:

```text
digital-strategy.ec.europa.eu
/en/news/
```

Candidates are deduplicated and sorted before detail pages are requested.

#### Financial Stability Board

The FSB collector uses the official Financial Innovation policy page:

```text
https://www.fsb.org/policy_areas/financial-innovation/
```

This listing provides structured publication cards containing titles, dates, summaries, and official links.

Only HTTPS links belonging to these domains are accepted:

```text
fsb.org
www.fsb.org
```

Publication URLs must also follow the official dated structure:

```text
/YYYY/MM/
```

The collector:

1. normalizes official URLs;
2. removes query parameters and fragments;
3. removes duplicate candidates;
4. sorts candidates from newest to oldest;
5. opens only the pages required to reach the requested limit;
6. extracts the main publication content.

This approach keeps HTTP requests controlled while providing enough information for relevance analysis.

### Relevance scoring

The initial relevance model is deterministic and auditable. It does not use a Large Language Model.

The analyzer:

- normalizes capitalization, accents, punctuation, and whitespace;
- searches for complete regulatory keywords and expressions;
- assigns a predefined weight to each matched keyword;
- adds a 50% bonus when a keyword appears in the title;
- limits the final score to 100;
- records matched keywords and categories.

| Score | Level | Relevant |
|---:|---|---|
| 0–29 | Low | No |
| 30–59 | Medium | Yes |
| 60–100 | High | Yes |

This deterministic score provides an objective and explainable baseline for future AI-assisted analysis.

### Dashboard architecture

The Streamlit dashboard reads the local SQLite database through a dedicated read-only repository.

Collection, analysis, and visualization remain separate operations:

```text
Official regulatory and institutional sources
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

The dashboard does not perform collection or modify relevance scores.

### Database

The application uses SQLite for local persistence:

```text
data/regulatory_ai_radar.db
```

SQLAlchemy provides models, sessions, queries, constraints, and transaction management.

The database contains:

- `news_articles`: normalized publications from every source;
- `article_analyses`: relevance scores and supporting evidence.

Publication URLs are unique and prevent duplicate records. Each publication has one current analysis that is updated whenever the analysis script runs again.

The database file is excluded from Git.

### Status

🚧 Under development.

#### Current stage

- [x] Initial project structure
- [x] ANPD news collector
- [x] BCB news collector
- [x] Chamber of Deputies proposition collector
- [x] European AI publication collector
- [x] FSB publication collector
- [x] Shared publication normalization
- [x] SQLite persistence
- [x] Duplicate prevention
- [x] Deterministic relevance ranking
- [x] Analysis persistence
- [x] Automated relevance tests
- [x] Automated tests for BCB, Chamber, European AI, and FSB collectors
- [x] Interactive multi-source dashboard
- [ ] Additional international regulatory sources
- [ ] AI-assisted classification
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
- HTML parsing
- Git

---

## Português

### Visão geral

O Regulatory AI Radar é um projeto de inteligência regulatória voltado ao acompanhamento de Inteligência Artificial, governança, riscos, proteção de dados, regulação financeira e atividade legislativa.

A aplicação coleta publicações de fontes oficiais nacionais e internacionais, normaliza e armazena o conteúdo, calcula um score auditável de relevância regulatória e apresenta os resultados em um dashboard interativo.

### Objetivos

O projeto busca:

- automatizar a coleta de publicações regulatórias e legislativas;
- priorizar sempre as publicações mais recentes;
- identificar conteúdos relacionados à Inteligência Artificial e à regulação;
- organizar publicações de diferentes fontes oficiais;
- impedir registros duplicados;
- calcular scores explicáveis de relevância regulatória;
- apoiar futuras análises de impacto com IA;
- fornecer informações estruturadas para dashboards e relatórios.

### Fontes atuais

- Agência Nacional de Proteção de Dados (ANPD)
- Banco Central do Brasil (BCB)
- Câmara dos Deputados
- Comissão Europeia — tópico de Inteligência Artificial
- Financial Stability Board (FSB)

### Funcionalidades atuais

- Coleta de cinco fontes oficiais
- Ordenação explícita da publicação mais recente para a mais antiga
- Extração de títulos, datas, resumos, conteúdo e URLs
- Validação dos domínios e caminhos oficiais
- Normalização compartilhada das publicações
- Persistência local com SQLite
- Mapeamento e consultas com SQLAlchemy
- Prevenção de duplicidades por URLs únicas
- Score determinístico de relevância regulatória
- Evidências de palavras-chave e categorias
- Ranking da maior para a menor relevância
- Persistência e atualização das análises
- Dashboard interativo com Streamlit
- Filtros por fonte, nível, score, relevância e texto
- Indicadores dinâmicos e cartões de publicações
- Links para as publicações oficiais
- Testes automatizados dos coletores e da relevância

### Fontes planejadas

- Bank for International Settlements (BIS)
- International Association of Privacy Professionals (IAPP)
- OECD.AI

### Funcionalidades planejadas

- Coletores adicionais
- Classificação de conteúdo assistida por IA
- Identificação de impactos para instituições financeiras
- Resumos automatizados
- Detecção de publicações semelhantes
- Histórico de mudanças regulatórias
- Coleta diária automatizada
- Alertas e relatórios periódicos
- Publicação em nuvem

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
│   ├── run_camara.py
│   ├── run_eu_ai_office.py
│   └── run_fsb.py
├── src
│   └── regulatory_ai_radar
│       ├── analysis
│       │   ├── __init__.py
│       │   └── relevance.py
│       ├── collectors
│       │   ├── __init__.py
│       │   ├── anpd.py
│       │   ├── bcb.py
│       │   ├── camara.py
│       │   ├── eu_ai_office.py
│       │   └── fsb.py
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
│   ├── test_eu_ai_office_collector.py
│   ├── test_fsb_collector.py
│   └── test_relevance.py
├── .gitignore
├── pyproject.toml
└── README.md
```

A pasta local `data` é criada automaticamente durante a inicialização do banco e não é enviada ao Git.

### Requisitos

- Python 3.12 ou superior
- Git
- Conexão com a internet
- Navegador moderno para acessar o dashboard

### Instalação

Clone o repositório e entre na pasta:

```powershell
git clone <url-do-repositorio>
cd regulatory-ai-radar
```

Crie o ambiente virtual:

```powershell
py -m venv .venv
```

Ative-o:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale o projeto em modo editável:

```powershell
python -m pip install -e .
```

O modo editável permite utilizar as alterações no código sem reinstalar o projeto a cada modificação.

### Utilização

#### Coletar notícias da ANPD

```powershell
python scripts\run_anpd.py
```

O script inicializa o banco, coleta até cinco notícias recentes, normaliza os dados, armazena registros novos e ignora URLs duplicadas.

#### Coletar notícias do BCB

```powershell
python scripts\run_bcb.py
```

O script acessa o feed Atom oficial, seleciona o ano atual, valida os links, ordena as notícias e armazena até cinco registros recentes.

#### Coletar proposições da Câmara

```powershell
python scripts\run_camara.py
```

O script pesquisa temas regulatórios na API oficial, remove resultados repetidos, ordena as proposições pela data e armazena até cinco registros.

#### Coletar publicações europeias sobre IA

```powershell
python scripts\run_eu_ai_office.py
```

O script acessa o portal da Comissão Europeia, seleciona o tópico de IA, valida os links, ordena as publicações e extrai o conteúdo das páginas mais recentes.

#### Coletar publicações do FSB

```powershell
python scripts\run_fsb.py
```

O script:

1. acessa a página oficial de inovação financeira do FSB;
2. identifica os cartões das publicações;
3. extrai títulos, datas, resumos e URLs;
4. valida domínios e caminhos oficiais;
5. remove URLs repetidas;
6. ordena as publicações da mais recente para a mais antiga;
7. abre somente as páginas necessárias;
8. extrai e normaliza o conteúdo;
9. armazena até cinco publicações;
10. ignora registros duplicados.

#### Listar publicações

```powershell
python scripts\list_articles.py
```

Consulta o banco local e exibe as informações principais das publicações.

#### Analisar e classificar publicações

```powershell
python scripts\analyze_articles.py
```

O script calcula o score, define o nível de relevância, registra as evidências, persiste a análise e apresenta o ranking.

Execute novamente esse comando depois de cada coleta.

#### Iniciar o dashboard

```powershell
python -m streamlit run dashboard\app.py
```

O dashboard estará normalmente disponível em:

```text
http://localhost:8501
```

Ele oferece:

- indicadores totais e filtrados;
- quantidade de publicações relevantes;
- quantidade com relevância alta;
- média dos scores;
- filtros para ANPD, BCB, CAMARA, EU_AI_OFFICE e FSB;
- filtro por nível;
- score mínimo;
- opção para exibir somente publicações relevantes;
- pesquisa textual;
- cartões ordenados pelo score;
- links para as publicações originais.

Para encerrar:

```text
Ctrl + C
```

### Validação

Verifique sintaxe e indentação:

```powershell
python -m compileall src scripts tests dashboard
```

Execute os testes:

```powershell
python -m unittest discover -s tests -v
```

A suíte possui 26 testes e verifica:

- cálculo e faixas do score;
- normalização de acentos e letras;
- contribuição do corpo da publicação;
- limite máximo do score;
- interpretação e ordenação do feed do BCB;
- normalização e validação das URLs do BCB;
- limites de coleta do BCB;
- ordenação e normalização das proposições da Câmara;
- remoção de duplicidades e validação de períodos;
- ordenação e normalização das publicações europeias;
- validação das URLs e limites do coletor europeu;
- ordenação das publicações do FSB;
- remoção de cartões repetidos do FSB;
- validação dos domínios oficiais do FSB;
- normalização do conteúdo do FSB;
- respeito ao limite de coleta do FSB;
- ausência de requisições quando o limite é zero.

### Normalização dos dados

Todos os coletores retornam a estrutura `NewsItem`:

```text
source
title
url
published_at
summary
body
collected_at
```

Esse contrato permite que o banco, o analisador e o dashboard processem todas as fontes da mesma forma.

### Estratégias de coleta

#### BCB

O coletor utiliza o feed Atom oficial:

```text
https://www.bcb.gov.br/api/feed/sitebcb/sitefeeds/noticias
```

Somente estes domínios são aceitos:

```text
bcb.gov.br
www.bcb.gov.br
```

Os resultados são ordenados antes da aplicação do limite.

#### Câmara dos Deputados

O coletor utiliza a API oficial:

```text
https://dadosabertos.camara.leg.br/api/v2/proposicoes
```

Ele pesquisa temas como IA, algoritmos, proteção de dados, cibersegurança, ativos virtuais, sistema financeiro e Banco Central.

Os tipos considerados são:

```text
PL
PLP
PEC
MPV
PDL
```

Resultados repetidos são removidos pelo identificador oficial.

#### Publicações europeias sobre IA

O coletor utiliza:

```text
https://digital-strategy.ec.europa.eu/en/news
```

Com o tópico:

```text
topic=119
```

Somente links HTTPS do domínio e caminho oficiais são aceitos:

```text
digital-strategy.ec.europa.eu
/en/news/
```

#### Financial Stability Board

O coletor utiliza a página oficial de Financial Innovation:

```text
https://www.fsb.org/policy_areas/financial-innovation/
```

Somente links HTTPS dos seguintes domínios são aceitos:

```text
fsb.org
www.fsb.org
```

Os links também devem seguir o padrão oficial de publicações:

```text
/YYYY/MM/
```

O coletor normaliza as URLs, remove parâmetros, elimina duplicidades, ordena os candidatos e abre somente as páginas necessárias para alcançar o limite solicitado.

### Score de relevância

O modelo inicial é determinístico, auditável e não utiliza um Large Language Model.

O analisador:

- normaliza maiúsculas, acentos, pontuação e espaços;
- procura palavras-chave e expressões regulatórias;
- atribui pesos predefinidos;
- acrescenta bônus de 50% para termos encontrados no título;
- limita o score a 100;
- registra palavras-chave e categorias.

| Score | Nível | Relevante |
|---:|---|---|
| 0–29 | Baixa | Não |
| 30–59 | Média | Sim |
| 60–100 | Alta | Sim |

### Arquitetura do dashboard

O dashboard consulta o SQLite por meio de um repositório dedicado à leitura.

```text
Fontes oficiais
    ↓
Coletores
    ↓
Normalização
    ↓
Persistência das publicações
    ↓
Análise de relevância
    ↓
Persistência das análises
    ↓
Dashboard
```

A interface não executa coletas nem modifica os scores.

### Banco de dados

O SQLite é criado automaticamente em:

```text
data/regulatory_ai_radar.db
```

O banco contém:

- `news_articles`: publicações normalizadas;
- `article_analyses`: scores e evidências.

As URLs são únicas e impedem duplicidades. O arquivo do banco não é enviado ao Git.

### Status

🚧 Em desenvolvimento.

#### Etapa atual

- [x] Estrutura inicial
- [x] Coletor da ANPD
- [x] Coletor do BCB
- [x] Coletor da Câmara
- [x] Coletor europeu de IA
- [x] Coletor do FSB
- [x] Normalização compartilhada
- [x] Persistência com SQLite
- [x] Prevenção de duplicidades
- [x] Ranking determinístico
- [x] Persistência das análises
- [x] Testes automatizados de relevância
- [x] Testes dos coletores BCB, Câmara, Comissão Europeia e FSB
- [x] Dashboard interativo com múltiplas fontes
- [ ] Outras fontes internacionais
- [ ] Classificação assistida por IA
- [ ] Automação diária
- [ ] Publicação em nuvem

### Tecnologias

- Python
- Beautiful Soup
- Requests
- SQLAlchemy
- SQLite
- Streamlit
- XML e Atom
- APIs REST e JSON
- Interpretação de HTML
- Git