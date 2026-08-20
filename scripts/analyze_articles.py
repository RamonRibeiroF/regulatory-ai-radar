from sqlalchemy import select

from regulatory_ai_radar.analysis import RelevanceAnalyzer
from regulatory_ai_radar.database.analysis_repository import (
    ArticleAnalysisRepository,
)
from regulatory_ai_radar.database.models import NewsArticle
from regulatory_ai_radar.database.session import (
    SessionFactory,
    initialize_database,
)


def main() -> None:
    """Analyze, rank, and persist stored news articles."""

    # Step 1: create the new database table when necessary.
    initialize_database()

    # Step 2: create the regulatory relevance analyzer.
    analyzer = RelevanceAnalyzer()

    # Step 3: retrieve all stored articles from the database.
    with SessionFactory() as session:
        statement = select(NewsArticle).order_by(
            NewsArticle.id
        )

        articles = session.scalars(
            statement
        ).all()

    if not articles:
        print("No articles found.")
        return

    analyzed_articles = []

    # Step 4: calculate the relevance of every stored article.
    for article in articles:
        result = analyzer.analyze(
            title=article.title,
            summary=article.summary,
            body=article.body,
        )

        analyzed_articles.append(
            (
                article,
                result,
            )
        )

    # Step 5: store the analysis results in the database.
    with SessionFactory() as session:
        repository = ArticleAnalysisRepository(
            session
        )

        save_result = repository.save_many(
            (
                article.id,
                result,
            )
            for article, result in analyzed_articles
        )

        total_analyses = repository.count()

    # Step 6: rank the articles from highest to lowest score.
    analyzed_articles.sort(
        key=lambda item: (
            -item[1].score,
            item[0].id,
        )
    )

    relevant_count = sum(
        result.is_relevant
        for _, result in analyzed_articles
    )

    # Step 7: display the analysis and persistence summary.
    print("=" * 70)
    print("REGULATORY AI RADAR")
    print(f"Analyzed articles: {len(analyzed_articles)}")
    print(f"Relevant articles: {relevant_count}")
    print("=" * 70)

    print("\nAnalysis database summary:")
    print(f"- Created: {save_result.created}")
    print(f"- Updated: {save_result.updated}")
    print(f"- Total stored: {total_analyses}")

    # Step 8: display the ranked analysis results.
    for position, (article, result) in enumerate(
        analyzed_articles,
        start=1,
    ):
        matched_keywords = (
            ", ".join(result.matched_keywords)
            if result.matched_keywords
            else "None"
        )

        print(f"\nRank: {position}")
        print(f"ID: {article.id}")
        print(f"Score: {result.score}")
        print(f"Level: {result.level}")
        print(f"Relevant: {result.is_relevant}")
        print(f"Title: {article.title}")
        print(f"Matched keywords: {matched_keywords}")
        print(f"URL: {article.url}")


# Run main() only when this file is executed directly.
if __name__ == "__main__":
    main()