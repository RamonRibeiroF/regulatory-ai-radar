from regulatory_ai_radar.collectors.eu_ai_office import (
    EUAIOfficeCollector,
)
from regulatory_ai_radar.database.repository import (
    NewsRepository,
)
from regulatory_ai_radar.database.session import (
    SessionFactory,
    initialize_database,
)


def main() -> None:
    """Collect and persist European AI publications."""

    print("=" * 70)
    print("REGULATORY AI RADAR")
    print("Collector: European AI Office")
    print("=" * 70)

    # Step 1: create the database and its tables when necessary.
    initialize_database()

    # Step 2: create the European AI publication collector.
    collector = EUAIOfficeCollector()

    print("\nFetching European AI publications...\n")

    # Step 3: request up to five recent official publications.
    news_items = collector.collect(
        limit=5
    )

    print(
        f"{len(news_items)} publications collected."
    )

    if not news_items:
        print(
            "No publications were available for persistence."
        )
        return

    # Step 4: open a database session and persist the publications.
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

    # Step 6: display publication titles, dates, and URLs.
    print("\nCollected publications:")

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