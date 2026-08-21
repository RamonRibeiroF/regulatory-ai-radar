from __future__ import annotations

from datetime import datetime

import streamlit as st

from regulatory_ai_radar.database.dashboard_repository import (
    DashboardArticle,
    DashboardPipelineRun,
    DashboardRepository,
    DashboardSourceRun,
)
from regulatory_ai_radar.database.session import (
    SessionFactory,
    initialize_database,
)


# Step 1: load dashboard and pipeline data with a short cache.
@st.cache_data(ttl=60)
def load_dashboard_data() -> tuple[
    list[DashboardArticle],
    DashboardPipelineRun | None,
    list[DashboardSourceRun],
]:
    """Load articles, analyses, and pipeline monitoring data."""

    initialize_database()

    with SessionFactory() as session:
        repository = DashboardRepository(
            session
        )

        articles = repository.list_articles()
        pipeline_run = repository.get_latest_pipeline_run()
        source_runs = repository.list_latest_source_runs()

    return (
        articles,
        pipeline_run,
        source_runs,
    )


# Step 2: format dates for dashboard display.
def format_datetime(
    date_value: datetime | None,
) -> str:
    """Format a date or return a fallback value."""

    if date_value is None:
        return "Not available"

    return date_value.strftime(
        "%Y-%m-%d %H:%M:%S"
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


# Step 5: display pipeline monitoring information.
def render_pipeline_monitoring(
    pipeline_run: DashboardPipelineRun | None,
    source_runs: list[DashboardSourceRun],
) -> None:
    """Render the latest pipeline execution and source statuses."""

    st.subheader(
        "Pipeline monitoring"
    )

    if pipeline_run is None:
        st.info(
            "No automated pipeline execution has been recorded yet."
        )
        return

    successful_sources = sum(
        source_run.status == "success"
        for source_run in source_runs
    )

    monitoring_columns = st.columns(
        4
    )

    monitoring_columns[0].metric(
        "Last pipeline run",
        f"#{pipeline_run.id}",
    )

    monitoring_columns[1].metric(
        "Pipeline status",
        pipeline_run.status.title(),
    )

    monitoring_columns[2].metric(
        "Healthy sources",
        f"{successful_sources}/{len(source_runs)}",
    )

    monitoring_columns[3].metric(
        "Execution errors",
        pipeline_run.error_count,
    )

    st.caption(
        "Last completed at: "
        f"{format_datetime(pipeline_run.finished_at)}"
    )

    # Step 6: display detailed observability for every source.
    with st.expander(
        "Source execution details",
        expanded=False,
    ):
        source_rows = [
            {
                "Source": source_run.source,
                "Status": source_run.status.title(),
                "Finished at": format_datetime(
                    source_run.finished_at
                ),
                "Duration (seconds)": round(
                    source_run.duration_seconds,
                    2,
                ),
                "Collected": source_run.collected_count,
                "Inserted": source_run.inserted_count,
                "Duplicates": source_run.skipped_count,
            }
            for source_run in source_runs
        ]

        st.dataframe(
            source_rows,
            hide_index=True,
            use_container_width=True,
        )

        failed_source_runs = [
            source_run
            for source_run in source_runs
            if source_run.status == "failed"
        ]

        for source_run in failed_source_runs:
            st.error(
                f"{source_run.source}: "
                f"{source_run.error_message or 'Unknown error'}"
            )


# Step 7: display summary metrics for the current selection.
def render_article_metrics(
    articles: list[DashboardArticle],
) -> None:
    """Render article summary metrics."""

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


# Step 8: display one regulatory news card.
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
            f"{format_datetime(article.published_at)}"
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

    # Step 9: configure the browser tab and dashboard layout.
    st.set_page_config(
        page_title="Regulatory AI Radar",
        page_icon="⚖️",
        layout="wide",
    )

    # Step 10: display the dashboard title and description.
    st.title(
        "Regulatory AI Radar"
    )

    st.caption(
        "Regulatory intelligence for Artificial Intelligence, "
        "data protection, governance, and financial regulation."
    )

    (
        articles,
        pipeline_run,
        source_runs,
    ) = load_dashboard_data()

    # Step 11: display automation and source health information.
    render_pipeline_monitoring(
        pipeline_run=pipeline_run,
        source_runs=source_runs,
    )

    st.divider()

    if not articles:
        st.warning(
            "No articles are currently stored. "
            "Run the automated pipeline before opening the dashboard."
        )
        return

    # Step 12: create the interactive sidebar filters.
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

    # Step 13: display article metrics and ranked publications.
    render_article_metrics(
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