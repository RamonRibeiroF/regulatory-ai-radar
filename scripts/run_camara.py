from regulatory_ai_radar.collectors.camara import (
    CamaraCollector,
)
from regulatory_ai_radar.database.repository import (
    NewsRepository,
)
from regulatory_ai_radar.database.session import (
    SessionFactory,
    initialize_database,
)


def main() -> None:
    """Collect and persist propositions from the Chamber of Deputies."""

    print("=" * 70)
    print("REGULATORY AI RADAR")
    print("Collector: Brazilian Chamber of Deputies")
    print("=" * 70)

    # Step 1: create the database and its tables when necessary.
    initialize_database()

    # Step 2: create the Chamber of Deputies collector.
    collector = CamaraCollector()

    print("\nFetching legislative propositions...\n")

    # Step 3: request up to five recent regulatory propositions.
    news_items = collector.collect(
        limit=5,
        lookback_days=90,
    )

    print(
        f"{len(news_items)} propositions collected."
    )

    if not news_items:
        print(
            "No propositions were available for persistence."
        )
        return

    # Step 4: open a database session and persist the propositions.
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

    # Step 6: display the collected proposition titles and URLs.
    print("\nCollected propositions:")

    for index, item in enumerate(
        news_items,
        start=1,
    ):
        print(f"\n{index}. {item.title}")
        print(f"   Published at: {item.published_at}")
        print(f"   {item.url}")


# Run main() only when this file is executed directly.
if __name__ == "__main__":
    main()