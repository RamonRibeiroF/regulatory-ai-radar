from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from regulatory_ai_radar.analysis import RelevanceResult
from regulatory_ai_radar.database.models import ArticleAnalysis


@dataclass(frozen=True, slots=True)
class AnalysisSaveResult:
    """Represent the result of saving article analyses."""

    created: int
    updated: int


class ArticleAnalysisRepository:
    """Provide database operations for article analyses."""

    def __init__(
        self,
        session: Session,
    ) -> None:
        self.session = session

    def save_many(
        self,
        analysis_items: Iterable[
            tuple[int, RelevanceResult]
        ],
    ) -> AnalysisSaveResult:
        """Create or update relevance analyses."""

        created = 0
        updated = 0

        try:
            # Step 1: process each article analysis.
            for article_id, result in analysis_items:
                # Step 2: search for an existing analysis.
                existing_analysis = self.session.scalar(
                    select(ArticleAnalysis).where(
                        ArticleAnalysis.article_id
                        == article_id
                    )
                )

                if existing_analysis is None:
                    # Step 3: create the first analysis for the article.
                    analysis = ArticleAnalysis(
                        article_id=article_id,
                        score=result.score,
                        level=result.level,
                        is_relevant=result.is_relevant,
                        matched_keywords=list(
                            result.matched_keywords
                        ),
                        matched_categories=list(
                            result.matched_categories
                        ),
                    )

                    self.session.add(
                        analysis
                    )
                    created += 1
                    continue

                # Step 4: update the existing analysis.
                existing_analysis.score = result.score
                existing_analysis.level = result.level
                existing_analysis.is_relevant = (
                    result.is_relevant
                )
                existing_analysis.matched_keywords = list(
                    result.matched_keywords
                )
                existing_analysis.matched_categories = list(
                    result.matched_categories
                )
                existing_analysis.analyzed_at = datetime.now(
                    timezone.utc
                )

                updated += 1

            # Step 5: commit all analyses as one transaction.
            self.session.commit()

        except Exception:
            # Step 6: undo every change if the transaction fails.
            self.session.rollback()
            raise

        return AnalysisSaveResult(
            created=created,
            updated=updated,
        )

    def count(self) -> int:
        """Return the total number of stored analyses."""

        total = self.session.scalar(
            select(
                func.count(
                    ArticleAnalysis.id
                )
            )
        )

        return total or 0