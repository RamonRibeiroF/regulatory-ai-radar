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


class ArticleFeedback(Base):
    """Representa o feedback de relevância dado pelo usuário."""

    # Passo 12: define a tabela e as regras de avaliação.
    __tablename__ = "article_feedback"

    __table_args__ = (
        CheckConstraint(
            "human_rating >= 1 AND human_rating <= 5",
            name="ck_article_feedback_human_rating",
        ),
    )

    # Passo 13: cria o identificador principal do feedback.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Passo 14: associa um único feedback atual a uma notícia.
    article_id: Mapped[int] = mapped_column(
        ForeignKey(
            "news_articles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    # Passo 15: armazena a avaliação e a explicação opcional.
    human_rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Passo 16: registra os horários de criação e modificação.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
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
