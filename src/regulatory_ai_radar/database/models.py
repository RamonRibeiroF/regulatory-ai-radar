from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from regulatory_ai_radar.database.base import Base


def utc_now() -> datetime:
    """Return the current date and time in UTC."""

    return datetime.now(timezone.utc)


class NewsArticle(Base):
    """Represent a regulatory news article stored in the database."""

    # Step 1: define the news article table name.
    __tablename__ = "news_articles"

    # Step 2: create the primary identifier.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Step 3: store the source and main article information.
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
        index=True,
    )

    # Step 4: store optional publication content.
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    body: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Step 5: store collection and database creation timestamps.
    collected_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )


class ArticleAnalysis(Base):
    """Represent the deterministic relevance analysis of an article."""

    # Step 6: define the article analysis table and constraints.
    __tablename__ = "article_analyses"

    __table_args__ = (
        CheckConstraint(
            "score >= 0 AND score <= 100",
            name="ck_article_analyses_score",
        ),
        CheckConstraint(
            "level IN ('low', 'medium', 'high')",
            name="ck_article_analyses_level",
        ),
    )

    # Step 7: create the analysis primary identifier.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Step 8: associate one analysis with one stored article.
    article_id: Mapped[int] = mapped_column(
        ForeignKey(
            "news_articles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    # Step 9: store the calculated relevance classification.
    score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    level: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )

    is_relevant: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    # Step 10: store the evidence supporting the score.
    matched_keywords: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
    )

    matched_categories: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
    )

    # Step 11: record when the analysis was performed.
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )


class ClassificacaoLocalArtigo(Base):
    """Armazena a classificação local determinística de uma notícia."""

    # Passo 12: mantém o nome físico para compatibilidade com o SQLite atual.
    __tablename__ = "classificacoes_ia_artigos"

    __table_args__ = (
        CheckConstraint(
            "avaliacao_estrelas >= 1 AND avaliacao_estrelas <= 5",
            name="ck_classificacoes_ia_avaliacao_estrelas",
        ),
        CheckConstraint(
            "confianca_percentual >= 0 AND confianca_percentual <= 100",
            name="ck_classificacoes_ia_confianca_percentual",
        ),
    )

    # Passo 13: cria um único resultado local atual para cada notícia.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    artigo_id: Mapped[int] = mapped_column(
        ForeignKey(
            "news_articles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    # Passo 14: persiste estrelas, evidência e justificativa auditável.
    avaliacao_estrelas: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    confianca_percentual: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    justificativa: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    categorias: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
    )

    # Passo 15: identifica o algoritmo e os critérios responsáveis.
    nome_modelo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    versao_criterios: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # Passo 16: registra criação e última atualização.
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class ImpactoRegulatorioArtigo(Base):
    """Armazena o impacto regulatório local de uma notícia."""

    __tablename__ = "impactos_regulatorios_artigos"

    __table_args__ = (
        CheckConstraint(
            "pontuacao_impacto >= 0 AND pontuacao_impacto <= 100",
            name="ck_impactos_pontuacao",
        ),
        CheckConstraint(
            "nivel_impacto IN "
            "('baixo', 'moderado', 'alto', 'muito_alto', 'critico')",
            name="ck_impactos_nivel",
        ),
    )

    # Passo 17: mantém um único impacto atual para cada notícia.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    artigo_id: Mapped[int] = mapped_column(
        ForeignKey("news_articles.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Passo 18: persiste o total e as quatro parcelas auditáveis.
    pontuacao_impacto: Mapped[int] = mapped_column(Integer, nullable=False)
    nivel_impacto: Mapped[str] = mapped_column(String(20), nullable=False)
    forca_regulatoria: Mapped[int] = mapped_column(Integer, nullable=False)
    aplicabilidade_financeira: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    governanca_tecnologica: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    urgencia_operacional: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    evidencias: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    justificativa: Mapped[str] = mapped_column(Text, nullable=False)
    nome_modelo: Mapped[str] = mapped_column(String(100), nullable=False)
    versao_criterios: Mapped[str] = mapped_column(String(50), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class PipelineRun(Base):
    """Represent one complete automated pipeline execution."""

    # Step 17: define the pipeline execution table and status rules.
    __tablename__ = "pipeline_runs"

    __table_args__ = (
        CheckConstraint(
            "status IN ('running', 'success', 'partial', 'failed')",
            name="ck_pipeline_runs_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(10),
        default="running",
        nullable=False,
        index=True,
    )

    total_collected: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    total_inserted: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    total_skipped: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    total_analyzed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    analyses_created: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    analyses_updated: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    error_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


class PipelineSourceRun(Base):
    """Represent one source result inside a pipeline execution."""

    # Step 18: define per-source execution observability.
    __tablename__ = "pipeline_source_runs"

    __table_args__ = (
        CheckConstraint(
            "status IN ('success', 'failed')",
            name="ck_pipeline_source_runs_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    pipeline_run_id: Mapped[int] = mapped_column(
        ForeignKey(
            "pipeline_runs.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        index=True,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    finished_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    duration_seconds: Mapped[float] = mapped_column(
        nullable=False,
    )

    collected_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    inserted_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    skipped_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
