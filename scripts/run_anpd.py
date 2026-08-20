import json
from dataclasses import asdict

from regulatory_ai_radar.collectors.anpd import (
    ANPDCollector,
)


def main() -> None:
    print("=" * 70)
    print("REGULATORY AI RADAR")
    print("Collector: ANPD")
    print("=" * 70)

    # Step 1: create the ANPD collector.
    collector = ANPDCollector()

    print("\nFetching news articles...\n")

    # Step 2: request up to five news articles.
    news_items = collector.collect(
        limit=5
    )

    # Step 3: display the number of collected articles.
    print(
        f"{len(news_items)} articles collected.\n"
    )

    # Step 4: process each collected article individually.
    for index, item in enumerate(
        news_items,
        start=1,
    ):
        print("=" * 70)
        print(f"ARTICLE {index}")
        print("=" * 70)

        # Step 5: convert the article into readable JSON.
        print(
            json.dumps(
                asdict(item),
                ensure_ascii=False,
                indent=2,
            )
        )

        print()


# Run main() only when this file is executed directly.
if __name__ == "__main__":
    main()