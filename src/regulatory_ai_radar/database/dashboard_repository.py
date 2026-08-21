from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from regulatory_ai_radar.database.models import (
    ArticleAnalysis,
    NewsArticle,
)


@dataclass(frozen=True, slots=True)
class DashboardArticle:
    """Represent article data prepared for the dashboard."""

    id: int
    source: str
    title: str
    url: str
    published_at: datetime | None
    summary: str | None
    score: int | None
    level: str
    is_relevant: bool
    matched_keywords: tuple[str, ...]


class DashboardRepository:
    """Provide read-only data for the dashboard."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def list_articles(self) -> list[DashboardArticle]:
        """Return articles and their current relevance analysis."""

        # Step 1: combine news articles with their analyses.
        statement = (
            select(
                NewsArticle,
                ArticleAnalysis,
            )
            .outerjoin(
                ArticleAnalysis,
                ArticleAnalysis.article_id
                == NewsArticle.id,
            )
            .order_by(
                NewsArticle.id
            )
        )

        rows = self.session.execute(
            statement
        ).all()

        dashboard_articles: list[DashboardArticle] = []

        # Step 2: convert database rows into dashboard data.
        for article, analysis in rows:
            dashboard_article = DashboardArticle(
                id=article.id,
                source=article.source,
                title=article.title,
                url=article.url,
                published_at=article.published_at,
                summary=article.summary,
                score=(
                    analysis.score
                    if analysis
                    else None
                ),
                level=(
                    analysis.level
                    if analysis
                    else "not_analyzed"
                ),
                is_relevant=(
                    analysis.is_relevant
                    if analysis
                    else False
                ),
                matched_keywords=(
                    tuple(
                        analysis.matched_keywords
                    )
                    if analysis
                    else ()
                ),
            )

            dashboard_articles.append(
                dashboard_article
            )

        # Step 3: return data without exposing ORM objects.
        return dashboard_articles