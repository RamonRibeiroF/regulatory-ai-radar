from sqlalchemy import select

from regulatory_ai_radar.database.models import NewsArticle
from regulatory_ai_radar.database.session import SessionFactory


def main() -> None:
    """List all news articles stored in the database."""

    # Step 1: open a database session.
    with SessionFactory() as session:
        # Step 2: build a query ordered by the article identifier.
        statement = select(NewsArticle).order_by(
            NewsArticle.id
        )

        # Step 3: execute the query and retrieve the stored articles.
        articles = session.scalars(
            statement
        ).all()

    # Step 4: display the total number of stored articles.
    print("=" * 70)
    print("REGULATORY AI RADAR")
    print(f"Stored articles: {len(articles)}")
    print("=" * 70)

    # Step 5: stop when the database contains no articles.
    if not articles:
        print("\nNo articles found.")
        return

    # Step 6: display the main information for each article.
    for article in articles:
        publication_date = (
            article.published_at.isoformat()
            if article.published_at
            else "Not available"
        )

        print(f"\nID: {article.id}")
        print(f"Source: {article.source}")
        print(f"Title: {article.title}")
        print(f"Published at: {publication_date}")
        print(f"URL: {article.url}")


# Run main() only when this file is executed directly.
if __name__ == "__main__":
    main()