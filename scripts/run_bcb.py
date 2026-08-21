from regulatory_ai_radar.collectors.bcb import BCBCollector
from regulatory_ai_radar.database.repository import NewsRepository
from regulatory_ai_radar.database.session import (
    SessionFactory,
    initialize_database,
)


def main() -> None:
    """Collect and persist news from the Central Bank of Brazil."""

    print("=" * 70)
    print("REGULATORY AI RADAR")
    print("Collector: Central Bank of Brazil")
    print("=" * 70)

    # Step 1: create the database and its tables when necessary.
    initialize_database()

    # Step 2: create the BCB news collector.
    collector = BCBCollector()

    print("\nFetching news articles...\n")

    # Step 3: request up to five official BCB news articles.
    news_items = collector.collect(
        limit=5
    )

    print(
        f"{len(news_items)} articles collected."
    )

    if not news_items:
        print(
            "No articles were available for persistence."
        )
        return

    # Step 4: open a database session and persist the articles.
    with SessionFactory() as session:
        repository = NewsRepository(
            session
        )

        result = repository.save_many(
            news_items
        )

        total_articles = repository.count()

    # Step 5: display the database operation summary.
    print("\nDatabase summary:")
    print(f"- Inserted: {result.inserted}")
    print(f"- Skipped as duplicates: {result.skipped}")
    print(f"- Total stored: {total_articles}")

    # Step 6: display the collected article titles and URLs.
    print("\nCollected articles:")

    for index, item in enumerate(
        news_items,
        start=1,
    ):
        print(f"\n{index}. {item.title}")
        print(f"   {item.url}")


# Run main() only when this file is executed directly.
if __name__ == "__main__":
    main()