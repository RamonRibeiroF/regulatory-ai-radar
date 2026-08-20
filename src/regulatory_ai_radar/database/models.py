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
    """Represent the relevance analysis of a stored article."""

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