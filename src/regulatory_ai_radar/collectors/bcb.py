from __future__ import annotations

from datetime import datetime, timezone
from urllib.parse import urlparse
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup

from regulatory_ai_radar.entities import NewsItem


BCB_NEWS_FEED_URL = (
    "https://www.bcb.gov.br/api/feed/"
    "sitebcb/sitefeeds/noticias"
)

ATOM_NAMESPACE = {
    "atom": "http://www.w3.org/2005/Atom"
}

ALLOWED_BCB_DOMAINS = {
    "bcb.gov.br",
    "www.bcb.gov.br",
}


def clean_text(text: str) -> str:
    """Remove unnecessary whitespace from text."""

    return " ".join(
        text.split()
    )


class BCBCollector:
    """Collect news published by the Central Bank of Brazil."""

    def __init__(self) -> None:
        # Step 1: create a reusable HTTP session.
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "RegulatoryAIRadar/0.1 "
                    "(educational and portfolio project)"
                ),
                "Accept": (
                    "application/atom+xml, "
                    "application/xml"
                ),
            }
        )

    def _get_feed(
        self,
        year: int,
    ) -> ElementTree.Element:
        """Download and parse the official BCB Atom feed."""

        # Step 2: request the official feed for the selected year.
        response = self.session.get(
            BCB_NEWS_FEED_URL,
            params={
                "ano": year,
            },
            timeout=(10, 30),
        )

        response.raise_for_status()

        # Step 3: convert the XML response into an element tree.
        try:
            return ElementTree.fromstring(
                response.content
            )
        except ElementTree.ParseError as error:
            raise ValueError(
                "The BCB feed returned invalid XML."
            ) from error

    def _extract_link(
        self,
        entry: ElementTree.Element,
    ) -> str | None:
        """Extract and validate the official article URL."""

        link_element = entry.find(
            "atom:link[@rel='alternate']",
            ATOM_NAMESPACE,
        )

        if link_element is None:
            return None

        article_url = link_element.get(
            "href"
        )

        if not article_url:
            return None

        parsed_url = urlparse(
            article_url
        )

        if parsed_url.netloc not in ALLOWED_BCB_DOMAINS:
            return None

        # Step 4: remove query parameters and URL fragments.
        return (
            f"{parsed_url.scheme}://"
            f"{parsed_url.netloc}"
            f"{parsed_url.path.rstrip('/')}"
        )

    def _extract_content(
        self,
        entry: ElementTree.Element,
    ) -> tuple[str | None, str | None]:
        """Extract a summary and body from embedded HTML."""

        content_element = entry.find(
            "atom:content",
            ATOM_NAMESPACE,
        )

        if (
            content_element is None
            or not content_element.text
        ):
            return (
                None,
                None,
            )

        # Step 5: parse the HTML embedded in the Atom feed.
        soup = BeautifulSoup(
            content_element.text,
            "html.parser",
        )

        text_blocks: list[str] = []
        seen_blocks: set[str] = set()

        for text_node in soup.stripped_strings:
            text_block = clean_text(
                str(text_node)
            )

            if len(text_block) < 20:
                continue

            if text_block in seen_blocks:
                continue

            seen_blocks.add(
                text_block
            )

            text_blocks.append(
                text_block
            )

        if not text_blocks:
            return (
                None,
                None,
            )

        # Step 6: use the first meaningful block as the summary.
        summary = text_blocks[0]

        # Step 7: preserve all meaningful blocks as the article body.
        body = "\n\n".join(
            text_blocks
        )

        return (
            summary,
            body,
        )

    def _extract_entry(
        self,
        entry: ElementTree.Element,
    ) -> NewsItem | None:
        """Convert one Atom entry into a normalized news item."""

        title_element = entry.find(
            "atom:title",
            ATOM_NAMESPACE,
        )

        updated_element = entry.find(
            "atom:updated",
            ATOM_NAMESPACE,
        )

        article_url = self._extract_link(
            entry
        )

        if (
            title_element is None
            or not title_element.text
            or article_url is None
        ):
            return None

        # Step 8: normalize the entry title and publication date.
        title = clean_text(
            title_element.text
        )

        published_at = (
            updated_element.text.strip()
            if (
                updated_element is not None
                and updated_element.text
            )
            else None
        )

        summary, body = self._extract_content(
            entry
        )

        # Step 9: create the shared normalized news structure.
        return NewsItem(
            source="BCB",
            title=title,
            url=article_url,
            published_at=published_at,
            summary=summary,
            body=body,
            collected_at=datetime.now(
                timezone.utc
            ).isoformat(),
        )

    def collect(
        self,
        limit: int = 5,
        year: int | None = None,
    ) -> list[NewsItem]:
        """Collect the latest news from the official BCB feed."""

        if limit <= 0:
            return []

        selected_year = (
            year
            if year is not None
            else datetime.now(
                timezone.utc
            ).year
        )

        # Step 10: download the feed and locate its entries.
        feed = self._get_feed(
            year=selected_year
        )

        entries = feed.findall(
            "atom:entry",
            ATOM_NAMESPACE,
        )

        news_items: list[NewsItem] = []

        # Step 11: normalize every valid entry from the feed.
        for entry in entries:
            news_item = self._extract_entry(
                entry
            )

            if news_item is None:
                continue

            news_items.append(
                news_item
            )

        # Step 12: explicitly sort articles from newest to oldest.
        news_items.sort(
            key=lambda item: (
                item.published_at or ""
            ),
            reverse=True,
        )

        # Step 13: return only the most recent requested articles.
        return news_items[:limit]