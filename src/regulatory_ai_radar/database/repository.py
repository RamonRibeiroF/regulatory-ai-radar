from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from regulatory_ai_radar.database.models import NewsArticle
from regulatory_ai_radar.entities import NewsItem


@dataclass(frozen=True, slots=True)
class SaveResult:
    """Represent the result of a database save operation."""

    inserted: int
    skipped: int


def parse_datetime(value: str | None) -> datetime | None:
    """Convert an ISO 8601 string into a datetime object."""

    if value is None:
        return None

    return datetime.fromisoformat(value)


class NewsRepository:
    """Provide database operations for regulatory news articles."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def save_many(
        self,
        news_items: Iterable[NewsItem],
    ) -> SaveResult:
        """Save new articles and skip URLs already in the database."""

        inserted = 0
        skipped = 0

        try:
            # Step 1: process each collected news article.
            for item in news_items:
                # Step 2: check whether the URL already exists.
                existing_id = self.session.scalar(
                    select(NewsArticle.id).where(
                        NewsArticle.url == item.url
                    )
                )

                if existing_id is not None:
                    skipped += 1
                    continue

                # Step 3: convert the normalized item into an ORM model.
                article = NewsArticle(
                    source=item.source,
                    title=item.title,
                    url=item.url,
                    published_at=parse_datetime(
                        item.published_at
                    ),
                    summary=item.summary,
                    body=item.body,
                    collected_at=datetime.fromisoformat(
                        item.collected_at
                    ),
                )

                # Step 4: add the new article to the current session.
                self.session.add(article)
                inserted += 1

            # Step 5: commit all changes as one transaction.
            self.session.commit()

        except Exception:
            # Step 6: undo the transaction if any operation fails.
            self.session.rollback()
            raise

        return SaveResult(
            inserted=inserted,
            skipped=skipped,
        )

    def count(self) -> int:
        """Return the total number of stored articles."""

        total = self.session.scalar(
            select(
                func.count(NewsArticle.id)
            )
        )

        return total or 0