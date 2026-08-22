from regulatory_ai_radar.collectors.fca_ai_lab import FCAAiLabCollector
from regulatory_ai_radar.database.repository import NewsRepository
from regulatory_ai_radar.database.session import (
    SessionFactory,
    initialize_database,
)


def main() -> None:
    """Collect and persist recent FCA artificial intelligence publications."""

    print("=" * 70)
    print("REGULATORY AI RADAR")
    print("Collector: Financial Conduct Authority - AI Lab")
    print("=" * 70)

    # Passo 1: garantir que as tabelas do SQLite existam.
    initialize_database()

    # Passo 2: coletar até cinco publicações recentes.
    print("\nFetching FCA AI publications...\n")
    news_items = FCAAiLabCollector().collect(limit=5)
    print(f"{len(news_items)} publications collected.")

    if not news_items:
        print("No publications were available for persistence.")
        return

    # Passo 3: salvar somente URLs ainda não armazenadas.
    with SessionFactory() as session:
        repository = NewsRepository(session)
        result = repository.save_many(news_items)
        total_articles = repository.count()

    print("\nDatabase summary:")
    print(f"- Inserted: {result.inserted}")
    print(f"- Skipped as duplicates: {result.skipped}")
    print(f"- Total stored: {total_articles}")

    print("\nCollected publications:")
    for index, item in enumerate(news_items, start=1):
        print(f"\n{index}. {item.title}")
        print(f"   Published at: {item.published_at}")
        print(f"   {item.url}")


if __name__ == "__main__":
    main()
