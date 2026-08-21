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
- Bank for International Settlements — Innovation Hub (BIS)
- International Association of Privacy Professionals (IAPP)

### Current capabilities

- Collection from seven official sources
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
│   ├── run_bis.py
│   ├── run_camara.py
│   ├── run_eu_ai_office.py
│   ├── run_fsb.py
│   └── run_iapp.py
├── src
│   └── regulatory_ai_radar
│       ├── analysis
│       │   ├── __init__.py
│       │   └── relevance.py
│       ├── collectors
│       │   ├── __init__.py
│       │   ├── anpd.py
│       │   ├── bcb.py
│       │   ├── bis.py
│       │   ├── camara.py
│       │   ├── eu_ai_office.py
│       │   ├── fsb.py
│       │   └── iapp.py
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
│   ├── test_bis_collector.py
│   ├── test_camara_collector.py
│   ├── test_eu_ai_office_collector.py
│   ├── test_fsb_collector.py
│   ├── test_iapp_collector.py
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

The script collects up to five recent official ANPD news articles, normalizes them, stores new records, and skips duplicate URLs.

#### Collect BCB news

```powershell
python scripts\run_bcb.py
```

The script accesses the official BCB Atom feed, validates official links, orders articles from newest to oldest, and stores up to five recent records.

#### Collect Chamber of Deputies propositions

```powershell
python scripts\run_camara.py
```

The script searches the official Chamber API by regulatory topics, removes repeated results, orders propositions by date, and stores up to five recent records.

#### Collect European AI publications

```powershell
python scripts\run_eu_ai_office.py
```

The script accesses the European Commission digital strategy portal, selects the Artificial Intelligence topic, validates links, orders candidates, and extracts the most recent publications.

#### Collect FSB publications

```powershell
python scripts\run_fsb.py
```

The script accesses the official FSB Financial Innovation page, extracts publication cards, validates dated official URLs, and stores up to five recent records.

#### Collect BIS Innovation Hub publications

```powershell
python scripts\run_bis.py
```

This script:

1. accesses the official BIS Innovation Hub publication list;
2. validates the JSON response;
3. identifies official publication paths;
4. normalizes canonical BIS URLs;
5. removes duplicate candidates;
6. sorts all candidates from newest to oldest;
7. opens only the detail pages required by the limit;
8. extracts titles, summaries, content, dates, and URLs;
9. stores up to five recent publications;
10. skips URLs already stored.

#### Collect IAPP news articles

```powershell
python scripts\run_iapp.py
```

The script reads the official public IAPP news results, validates article URLs, removes duplicates, sorts publications from newest to oldest, and stores up to five recent records. For member-gated publications, it stores only the publicly available metadata and does not extract protected body content.

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

The dashboard is normally available at:

```text
http://localhost:8501
```

The dashboard provides:

- total and filtered publication metrics;
- number of relevant publications;
- number of high-relevance publications;
- average relevance score;
- source filters for ANPD, BCB, BIS, CAMARA, EU_AI_OFFICE, FSB, and IAPP;
- relevance-level filters;
- minimum-score selection;
- relevant-only selection;
- text search;
- ranked regulatory publication cards;
- links to original official publications.

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

The suite currently contains 40 tests covering:

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
- BIS publication ordering;
- BIS duplicate removal;
- BIS official-path validation;
- BIS article-content normalization;
- BIS collection-limit enforcement;
- IAPP structured-result extraction and ordering;
- IAPP URL validation and duplicate removal;
- IAPP public-body normalization;
- protection of member-gated article bodies;
- IAPP collection-limit enforcement;
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

#### Chamber of Deputies

The Chamber collector uses the official Open Data API:

```text
https://dadosabertos.camara.leg.br/api/v2/proposicoes
```

It searches propositions related to topics such as:

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

Only HTTPS links from the following official domain and path are accepted:

```text
digital-strategy.ec.europa.eu
/en/news/
```

#### Financial Stability Board

The FSB collector uses the official Financial Innovation page:

```text
https://www.fsb.org/policy_areas/financial-innovation/
```

Only HTTPS links belonging to these domains are accepted:

```text
fsb.org
www.fsb.org
```

Publication URLs must follow the official dated structure:

```text
/YYYY/MM/
```

Candidates are normalized, deduplicated, sorted, and opened only until the requested limit is reached.

#### Bank for International Settlements

The BIS collector uses the official BIS Innovation Hub publication list:

```text
https://www.bis.org/api/document_lists/bisih_publications.json
```

The endpoint provides structured information including:

- publication paths;
- official titles;
- publication dates;
- topics;
- institutional sources.

Only paths matching the official publication structure are accepted:

```text
/publ/<publication-identifier>
```

Examples include:

```text
/publ/othp109
/publ/othp112
```

The collector converts these paths into canonical official pages:

```text
https://www.bis.org/publ/<publication-identifier>.htm
```

Only these domains are accepted:

```text
bis.org
www.bis.org
```

The collector:

1. validates the JSON response;
2. validates publication paths;
3. builds canonical URLs;
4. removes duplicate URLs;
5. sorts all candidates from newest to oldest;
6. selects the most recent candidates;
7. opens only the pages required by the limit;
8. extracts summaries and main content from the official detail pages.

This strategy uses the BIS structured data source for discovery while preserving the official HTML publication page as the public URL.

#### International Association of Privacy Professionals

The IAPP collector reads the public server-rendered search results from:

```text
https://iapp.org/news
```

Only HTTPS links from the official IAPP domains and article path are accepted:

```text
iapp.org
www.iapp.org
/news/a/<article-slug>
```

The collector validates and decodes the structured results, canonicalizes URLs, removes duplicates, and explicitly sorts candidates from newest to oldest. Public article bodies are normalized from rich-text sections. When a result is marked as member-gated, only its publicly available title, date, summary, and URL are stored; protected body content is not extracted.

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
- [x] BIS Innovation Hub publication collector
- [x] IAPP news collector
- [x] Shared publication normalization
- [x] SQLite persistence
- [x] Duplicate prevention
- [x] Deterministic relevance ranking
- [x] Analysis persistence
- [x] Automated relevance tests
- [x] Automated tests for BCB, Chamber, European AI, FSB, BIS, and IAPP collectors
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
- priorizar as publicações mais recentes;
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
- Bank for International Settlements — Innovation Hub (BIS)
- International Association of Privacy Professionals (IAPP)

### Funcionalidades atuais

- Coleta de sete fontes oficiais
- Ordenação da publicação mais recente para a mais antiga
- Extração de títulos, datas, resumos, conteúdo e URLs
- Validação de domínios e caminhos oficiais
- Normalização compartilhada
- Persistência local com SQLite
- Mapeamento e consultas com SQLAlchemy
- Prevenção de duplicidades por URLs únicas
- Score determinístico de relevância
- Evidências de palavras-chave e categorias
- Ranking da maior para a menor relevância
- Persistência e atualização das análises
- Dashboard interativo com Streamlit
- Filtros por fonte, nível, score, relevância e texto
- Indicadores dinâmicos e cartões de publicações
- Links para publicações oficiais
- Testes automatizados dos coletores e da relevância

### Fontes planejadas

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
│   ├── run_bis.py
│   ├── run_camara.py
│   ├── run_eu_ai_office.py
│   ├── run_fsb.py
│   └── run_iapp.py
├── src
│   └── regulatory_ai_radar
│       ├── analysis
│       │   ├── __init__.py
│       │   └── relevance.py
│       ├── collectors
│       │   ├── __init__.py
│       │   ├── anpd.py
│       │   ├── bcb.py
│       │   ├── bis.py
│       │   ├── camara.py
│       │   ├── eu_ai_office.py
│       │   ├── fsb.py
│       │   └── iapp.py
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
│   ├── test_bis_collector.py
│   ├── test_camara_collector.py
│   ├── test_eu_ai_office_collector.py
│   ├── test_fsb_collector.py
│   ├── test_iapp_collector.py
│   └── test_relevance.py
├── .gitignore
├── pyproject.toml
└── README.md
```

A pasta `data` é criada automaticamente durante a inicialização do banco e não é enviada ao Git.

### Requisitos

- Python 3.12 ou superior
- Git
- Conexão com a internet
- Navegador moderno para o dashboard

### Instalação

Clone o repositório:

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

### Utilização

#### Coletar notícias da ANPD

```powershell
python scripts\run_anpd.py
```

Coleta até cinco notícias recentes, normaliza os dados, armazena registros novos e ignora URLs duplicadas.

#### Coletar notícias do BCB

```powershell
python scripts\run_bcb.py
```

Acessa o feed Atom oficial, valida links, ordena as notícias e armazena até cinco registros recentes.

#### Coletar proposições da Câmara

```powershell
python scripts\run_camara.py
```

Pesquisa temas regulatórios na API oficial, remove resultados repetidos, ordena as proposições e armazena até cinco registros.

#### Coletar publicações europeias sobre IA

```powershell
python scripts\run_eu_ai_office.py
```

Acessa o portal da Comissão Europeia, seleciona o tópico de IA, valida os links e extrai as publicações mais recentes.

#### Coletar publicações do FSB

```powershell
python scripts\run_fsb.py
```

Acessa a página oficial de inovação financeira, valida os links datados e armazena até cinco publicações.

#### Coletar publicações do BIS Innovation Hub

```powershell
python scripts\run_bis.py
```

O script:

1. acessa a lista oficial do BIS Innovation Hub;
2. valida a resposta JSON;
3. identifica os caminhos oficiais;
4. constrói URLs canônicas;
5. remove candidatos duplicados;
6. ordena os resultados da data mais recente para a mais antiga;
7. abre somente as páginas necessárias;
8. extrai títulos, resumos, conteúdo, datas e URLs;
9. armazena até cinco publicações;
10. ignora registros duplicados.

#### Coletar notícias da IAPP

```powershell
python scripts\run_iapp.py
```

O script lê os resultados públicos oficiais da IAPP, valida as URLs dos artigos, remove duplicidades, ordena as publicações da mais recente para a mais antiga e armazena até cinco registros. Para publicações restritas a membros, somente os metadados públicos são armazenados; o conteúdo protegido do corpo não é extraído.

#### Listar publicações

```powershell
python scripts\list_articles.py
```

Consulta o banco e exibe as informações principais das publicações.

#### Analisar publicações

```powershell
python scripts\analyze_articles.py
```

Calcula o score, define o nível, registra evidências, persiste as análises e apresenta o ranking.

Execute novamente depois de cada coleta.

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
- filtros para ANPD, BCB, BIS, CAMARA, EU_AI_OFFICE, FSB e IAPP;
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

Verifique a sintaxe e a indentação:

```powershell
python -m compileall src scripts tests dashboard
```

Execute os testes:

```powershell
python -m unittest discover -s tests -v
```

A suíte possui 40 testes e verifica:

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
- ordenação, normalização e limites do FSB;
- validação dos domínios do FSB;
- ordenação das publicações do BIS;
- remoção de resultados duplicados do BIS;
- validação dos caminhos oficiais do BIS;
- normalização do conteúdo do BIS;
- respeito ao limite de coleta do BIS;
- extração e ordenação dos resultados estruturados da IAPP;
- validação de URLs e remoção de duplicidades da IAPP;
- normalização do corpo de artigos públicos da IAPP;
- proteção do corpo de artigos restritos a membros;
- respeito ao limite de coleta da IAPP;
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

Esse contrato permite que o banco, o analisador e o dashboard processem todas as fontes da mesma maneira.

### Estratégias de coleta

#### BCB

Utiliza o feed Atom oficial:

```text
https://www.bcb.gov.br/api/feed/sitebcb/sitefeeds/noticias
```

Somente os domínios oficiais são aceitos.

#### Câmara dos Deputados

Utiliza a API oficial:

```text
https://dadosabertos.camara.leg.br/api/v2/proposicoes
```

Pesquisa temas regulatórios e remove resultados repetidos pelo identificador oficial.

#### Publicações europeias sobre IA

Utiliza:

```text
https://digital-strategy.ec.europa.eu/en/news
```

Com o tópico:

```text
topic=119
```

Somente links oficiais de notícias são aceitos.

#### Financial Stability Board

Utiliza:

```text
https://www.fsb.org/policy_areas/financial-innovation/
```

Somente links dos domínios oficiais e com caminhos datados são aceitos.

#### Bank for International Settlements

Utiliza a lista estruturada oficial:

```text
https://www.bis.org/api/document_lists/bisih_publications.json
```

São aceitos somente caminhos como:

```text
/publ/othp109
/publ/othp112
```

Eles são convertidos em páginas oficiais:

```text
https://www.bis.org/publ/othp109.htm
https://www.bis.org/publ/othp112.htm
```

O coletor valida a resposta, normaliza os caminhos, elimina duplicidades, ordena as candidatas e abre somente as páginas necessárias para alcançar o limite.

#### International Association of Privacy Professionals

O coletor da IAPP lê os resultados públicos renderizados no servidor em:

```text
https://iapp.org/news
```

São aceitos somente links HTTPS dos domínios oficiais e com o caminho de artigos:

```text
iapp.org
www.iapp.org
/news/a/<slug-do-artigo>
```

O coletor valida e interpreta os resultados estruturados, transforma as URLs em formato canônico, elimina duplicidades e ordena explicitamente as publicações da mais recente para a mais antiga. O corpo de artigos públicos é normalizado a partir das seções de texto. Quando a publicação é restrita a membros, somente título, data, resumo e URL disponíveis publicamente são armazenados; o corpo protegido não é extraído.

### Score de relevância

O modelo inicial é determinístico, auditável e não utiliza um Large Language Model.

O analisador:

- normaliza maiúsculas, acentos, pontuação e espaços;
- procura palavras-chave e expressões regulatórias;
- atribui pesos predefinidos;
- acrescenta bônus de 50% para termos no título;
- limita o score a 100;
- registra palavras-chave e categorias.

| Score | Nível | Relevante |
|---:|---|---|
| 0–29 | Baixa | Não |
| 30–59 | Média | Sim |
| 60–100 | Alta | Sim |

### Arquitetura

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

As URLs são únicas e impedem duplicidades. O banco local não é enviado ao Git.

### Status

🚧 Em desenvolvimento.

#### Etapa atual

- [x] Estrutura inicial
- [x] Coletor da ANPD
- [x] Coletor do BCB
- [x] Coletor da Câmara
- [x] Coletor europeu de IA
- [x] Coletor do FSB
- [x] Coletor do BIS Innovation Hub
- [x] Coletor de notícias da IAPP
- [x] Normalização compartilhada
- [x] Persistência com SQLite
- [x] Prevenção de duplicidades
- [x] Ranking determinístico
- [x] Persistência das análises
- [x] Testes automatizados de relevância
- [x] Testes dos coletores BCB, Câmara, Comissão Europeia, FSB, BIS e IAPP
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
