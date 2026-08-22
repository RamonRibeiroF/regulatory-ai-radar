# Regulatory AI Radar

A local regulatory-intelligence pipeline that collects recent official
publications, removes duplicates, ranks relevance, estimates regulatory impact,
and presents the results in an interactive dashboard.

The project is deterministic, auditable, and does not require paid APIs. Its
classifications are rule-based and do not train or claim to be an AI model.

## What it delivers

- ten official Brazilian and international sources;
- collection of the latest publications from each source;
- local SQLite persistence and URL-based duplicate prevention;
- deterministic relevance score and one-to-five-star classification;
- deterministic regulatory-impact score with auditable evidence;
- isolated source failures and persistent pipeline history;
- daily hidden execution on Windows with local logs;
- read-only Streamlit dashboard with filters and monitoring;
- automated tests without live network calls.

## Sources

| Code | Source |
| --- | --- |
| `ANPD` | Brazilian National Data Protection Authority |
| `BCB` | Central Bank of Brazil |
| `CAMARA` | Brazilian Chamber of Deputies |
| `EU_AI_OFFICE` | European AI Office |
| `FSB` | Financial Stability Board |
| `BIS` | BIS Innovation Hub |
| `IAPP` | International Association of Privacy Professionals |
| `OECD_AI` | OECD.AI |
| `EBA` | European Banking Authority — Digital Finance |
| `FCA_AI_LAB` | Financial Conduct Authority — AI Lab |

## Processing flow

```text
Official sources
      ↓
Collectors → normalization → SQLite deduplication
      ↓
Relevance analysis → local stars → regulatory impact
      ↓
Pipeline history and Streamlit dashboard
```

The unified pipeline executes each source independently. A failed source is
recorded without discarding successful results from the others.

## Classification

### Relevance

The relevance analyzer assigns a score from 0 to 100 using matched keywords and
categories. The local star classifier converts the score using fixed ranges:

| Score | Stars |
| --- | --- |
| 0–19 | 1 |
| 20–39 | 2 |
| 40–59 | 3 |
| 60–79 | 4 |
| 80–100 | 5 |

### Regulatory impact

Impact is calculated independently from relevance. Its four components total
100 points:

| Component | Maximum |
| --- | ---: |
| Regulatory force | 30 |
| Financial applicability | 30 |
| Technology and data governance | 25 |
| Operational urgency | 15 |

| Impact score | Level |
| --- | --- |
| 0–19 | Low |
| 20–39 | Moderate |
| 40–59 | High |
| 60–79 | Very high |
| 80–100 | Critical |

Each stored result includes its component scores, matched evidence, explanation,
model name, and criteria version.

## Setup

Requirements: Python 3.12 or newer and Git.

```powershell
git clone <repository-url>
cd regulatory-ai-radar
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## Usage

```powershell
# Run the complete pipeline.
python scripts\run_pipeline.py --limit 5

# Recalculate existing local classifications.
python scripts\classify_articles_local.py
python scripts\classify_article_impacts.py

# Open the dashboard.
python -m streamlit run dashboard\app.py

# Run all tests.
python -m unittest discover -s tests -v
```

The dashboard is available at [http://localhost:8501](http://localhost:8501).
The Windows scheduler can call `scripts\run_scheduled_pipeline.vbs`, which runs
the PowerShell launcher invisibly and writes execution output to `logs\`.

## Local data

The SQLite database and generated logs remain local and are ignored by Git.
Main tables store publications, relevance analyses, local stars, regulatory
impact, pipeline executions, and per-source execution details.

## Current status

- [x] Ten official collectors
- [x] Shared normalization and SQLite persistence
- [x] Duplicate prevention
- [x] Deterministic relevance ranking and local stars
- [x] Audited local classification ranges
- [x] Deterministic regulatory-impact classification
- [x] Unified and monitored pipeline
- [x] Interactive multi-source dashboard
- [x] Daily hidden execution on Windows
- [x] Automated tests

---

# Regulatory AI Radar — Português

Pipeline local de inteligência regulatória que coleta publicações oficiais
recentes, remove duplicidades, ordena por relevância, estima o impacto
regulatório e apresenta os resultados em um dashboard interativo.

O projeto é determinístico, auditável e não depende de APIs pagas. Suas
classificações são baseadas em regras e não treinam nem alegam ser um modelo de
IA.

## Entregas

- dez fontes oficiais brasileiras e internacionais;
- coleta das publicações mais recentes de cada fonte;
- persistência local em SQLite e prevenção de duplicidades por URL;
- score determinístico de relevância e classificação de uma a cinco estrelas;
- score determinístico de impacto regulatório com evidências auditáveis;
- isolamento de falhas por fonte e histórico persistente do pipeline;
- execução diária oculta no Windows com logs locais;
- dashboard Streamlit somente leitura, com filtros e monitoramento;
- testes automatizados sem chamadas reais de rede.

## Fontes

| Código | Fonte |
| --- | --- |
| `ANPD` | Autoridade Nacional de Proteção de Dados |
| `BCB` | Banco Central do Brasil |
| `CAMARA` | Câmara dos Deputados |
| `EU_AI_OFFICE` | Escritório Europeu de Inteligência Artificial |
| `FSB` | Financial Stability Board |
| `BIS` | BIS Innovation Hub |
| `IAPP` | International Association of Privacy Professionals |
| `OECD_AI` | OECD.AI |
| `EBA` | European Banking Authority — Digital Finance |
| `FCA_AI_LAB` | Financial Conduct Authority — AI Lab |

## Fluxo

```text
Fontes oficiais
      ↓
Coletores → normalização → deduplicação no SQLite
      ↓
Análise de relevância → estrelas locais → impacto regulatório
      ↓
Histórico do pipeline e dashboard Streamlit
```

O pipeline unificado executa cada fonte de forma independente. A falha de uma
fonte é registrada sem descartar os resultados obtidos nas demais.

## Classificação

### Relevância

O analisador atribui um score de 0 a 100 com base nas palavras-chave e
categorias identificadas. A classificação local converte o score em estrelas:

| Score | Estrelas |
| --- | --- |
| 0–19 | 1 |
| 20–39 | 2 |
| 40–59 | 3 |
| 60–79 | 4 |
| 80–100 | 5 |

### Impacto regulatório

O impacto é calculado separadamente da relevância. Seus quatro componentes
totalizam 100 pontos:

| Componente | Máximo |
| --- | ---: |
| Força regulatória | 30 |
| Aplicabilidade financeira | 30 |
| Governança tecnológica e de dados | 25 |
| Urgência operacional | 15 |

| Score de impacto | Nível |
| --- | --- |
| 0–19 | Baixo |
| 20–39 | Moderado |
| 40–59 | Alto |
| 60–79 | Muito alto |
| 80–100 | Crítico |

Cada resultado armazena as parcelas, evidências encontradas, justificativa,
nome do modelo e versão dos critérios.

## Instalação

Requisitos: Python 3.12 ou superior e Git.

```powershell
git clone <url-do-repositorio>
cd regulatory-ai-radar
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
```

## Uso

```powershell
# Executar o pipeline completo.
python scripts\run_pipeline.py --limit 5

# Recalcular as classificações existentes.
python scripts\classify_articles_local.py
python scripts\classify_article_impacts.py

# Abrir o dashboard.
python -m streamlit run dashboard\app.py

# Executar os testes.
python -m unittest discover -s tests -v
```

O dashboard fica disponível em
[http://localhost:8501](http://localhost:8501). O Agendador do Windows pode
chamar `scripts\run_scheduled_pipeline.vbs`, que executa o iniciador PowerShell
de forma oculta e grava a saída em `logs\`.

## Dados locais

O banco SQLite e os logs gerados permanecem locais e são ignorados pelo Git. As
tabelas principais armazenam publicações, análises de relevância, estrelas
locais, impacto regulatório e execuções do pipeline por fonte.

## Situação atual

- [x] Dez coletores oficiais
- [x] Normalização compartilhada e persistência SQLite
- [x] Prevenção de duplicidades
- [x] Ranking determinístico de relevância e estrelas locais
- [x] Faixas locais de classificação auditadas
- [x] Classificação determinística de impacto regulatório
- [x] Pipeline unificado e monitorado
- [x] Dashboard interativo com múltiplas fontes
- [x] Execução diária oculta no Windows
- [x] Testes automatizados
