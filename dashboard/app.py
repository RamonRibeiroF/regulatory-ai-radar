from datetime import datetime

import streamlit as st

from regulatory_ai_radar.database.dashboard_repository import (
    DashboardArticle,
    DashboardRepository,
)
from regulatory_ai_radar.database.session import (
    SessionFactory,
    initialize_database,
)


# Step 1: load dashboard data with a short cache.
@st.cache_data(ttl=60)
def load_articles() -> list[DashboardArticle]:
    """Load articles and analyses from the local database."""

    initialize_database()

    with SessionFactory() as session:
        repository = DashboardRepository(
            session
        )

        return repository.list_articles()


# Step 2: format publication dates for display.
def format_publication_date(
    publication_date: datetime | None,
) -> str:
    """Format a publication date or return a fallback value."""

    if publication_date is None:
        return "Not available"

    return publication_date.strftime(
        "%Y-%m-%d %H:%M"
    )


# Step 3: apply the filters selected in the sidebar.
def filter_articles(
    articles: list[DashboardArticle],
    selected_sources: list[str],
    selected_levels: list[str],
    minimum_score: int,
    relevant_only: bool,
    search_query: str,
) -> list[DashboardArticle]:
    """Filter articles using dashboard controls."""

    normalized_query = search_query.strip().lower()
    filtered_articles = []

    for article in articles:
        article_score = article.score or 0

        searchable_content = " ".join(
            (
                article.title,
                article.summary or "",
                " ".join(
                    article.matched_keywords
                ),
            )
        ).lower()

        if article.source not in selected_sources:
            continue

        if article.level not in selected_levels:
            continue

        if article_score < minimum_score:
            continue

        if relevant_only and not article.is_relevant:
            continue

        if (
            normalized_query
            and normalized_query
            not in searchable_content
        ):
            continue

        filtered_articles.append(
            article
        )

    # Step 4: rank filtered articles by score and identifier.
    return sorted(
        filtered_articles,
        key=lambda article: (
            article.score or 0,
            article.id,
        ),
        reverse=True,
    )


# Step 5: display summary metrics for the current selection.
def render_metrics(
    articles: list[DashboardArticle],
) -> None:
    """Render dashboard summary metrics."""

    total_articles = len(
        articles
    )

    relevant_articles = sum(
        article.is_relevant
        for article in articles
    )

    high_relevance_articles = sum(
        article.level == "high"
        for article in articles
    )

    available_scores = [
        article.score
        for article in articles
        if article.score is not None
    ]

    average_score = (
        sum(available_scores)
        / len(available_scores)
        if available_scores
        else 0
    )

    metric_columns = st.columns(
        4
    )

    metric_columns[0].metric(
        "Displayed articles",
        total_articles,
    )

    metric_columns[1].metric(
        "Relevant articles",
        relevant_articles,
    )

    metric_columns[2].metric(
        "High relevance",
        high_relevance_articles,
    )

    metric_columns[3].metric(
        "Average score",
        f"{average_score:.1f}",
    )


# Step 6: display one regulatory news card.
def render_article(
    article: DashboardArticle,
    position: int,
) -> None:
    """Render a single ranked article."""

    with st.container(
        border=True
    ):
        st.subheader(
            f"{position}. {article.title}"
        )

        information_columns = st.columns(
            3
        )

        information_columns[0].metric(
            "Score",
            (
                article.score
                if article.score is not None
                else "N/A"
            ),
        )

        information_columns[1].metric(
            "Level",
            article.level.replace(
                "_",
                " ",
            ).title(),
        )

        information_columns[2].metric(
            "Relevant",
            (
                "Yes"
                if article.is_relevant
                else "No"
            ),
        )

        st.write(
            f"**Source:** {article.source}"
        )

        st.write(
            "**Published at:** "
            f"{format_publication_date(article.published_at)}"
        )

        if article.summary:
            st.write(
                article.summary
            )

        matched_keywords = (
            ", ".join(
                article.matched_keywords
            )
            if article.matched_keywords
            else "None"
        )

        st.caption(
            f"Matched keywords: {matched_keywords}"
        )

        st.link_button(
            "Open original article",
            article.url,
        )


def main() -> None:
    """Render the Regulatory AI Radar dashboard."""

    # Step 7: configure the browser tab and dashboard layout.
    st.set_page_config(
        page_title="Regulatory AI Radar",
        page_icon="⚖️",
        layout="wide",
    )

    # Step 8: display the dashboard title and description.
    st.title(
        "Regulatory AI Radar"
    )

    st.caption(
        "Regulatory intelligence for Artificial Intelligence, "
        "data protection, governance, and financial regulation."
    )

    articles = load_articles()

    if not articles:
        st.warning(
            "No articles are currently stored. "
            "Run the ANPD collector before opening the dashboard."
        )
        return

    # Step 9: create the interactive sidebar filters.
    st.sidebar.header(
        "Filters"
    )

    available_sources = sorted(
        {
            article.source
            for article in articles
        }
    )

    available_levels = [
        "high",
        "medium",
        "low",
        "not_analyzed",
    ]

    selected_sources = st.sidebar.multiselect(
        "Sources",
        options=available_sources,
        default=available_sources,
    )

    selected_levels = st.sidebar.multiselect(
        "Relevance levels",
        options=available_levels,
        default=available_levels,
    )

    minimum_score = st.sidebar.slider(
        "Minimum score",
        min_value=0,
        max_value=100,
        value=0,
    )

    relevant_only = st.sidebar.checkbox(
        "Relevant articles only",
        value=False,
    )

    search_query = st.sidebar.text_input(
        "Search",
        placeholder="Title, summary, or keyword",
    )

    filtered_articles = filter_articles(
        articles=articles,
        selected_sources=selected_sources,
        selected_levels=selected_levels,
        minimum_score=minimum_score,
        relevant_only=relevant_only,
        search_query=search_query,
    )

    # Step 10: display metrics and ranked articles.
    render_metrics(
        filtered_articles
    )

    st.divider()

    st.subheader(
        "Ranked regulatory news"
    )

    if not filtered_articles:
        st.info(
            "No articles match the selected filters."
        )
        return

    for position, article in enumerate(
        filtered_articles,
        start=1,
    ):
        render_article(
            article=article,
            position=position,
        )


# Run main() when Streamlit loads this file.
if __name__ == "__main__":
    main()