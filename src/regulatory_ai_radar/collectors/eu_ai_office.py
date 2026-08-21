from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from regulatory_ai_radar.entities import NewsItem


EU_DIGITAL_STRATEGY_DOMAIN = (
    "digital-strategy.ec.europa.eu"
)

EU_AI_NEWS_URL = (
    "https://digital-strategy.ec.europa.eu/en/news"
)

EU_AI_TOPIC_ID = 119


def clean_text(text: str) -> str:
    """Remove unnecessary whitespace from text."""

    return " ".join(text.split())


@dataclass(frozen=True, slots=True)
class EUNewsCandidate:
    """Represent a publication found on the official listing page."""

    title: str
    url: str
    published_at: str


class EUAIOfficeCollector:
    """Collect AI publications from the European Commission."""

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
                    "text/html,application/xhtml+xml"
                ),
            }
        )

    def _get_page(
        self,
        url: str,
        params: dict[str, object] | None = None,
    ) -> BeautifulSoup:
        """Download and parse one official European Commission page."""

        # Step 2: request one official HTML page.
        response = self.session.get(
            url,
            params=params,
            timeout=(10, 30),
        )

        response.raise_for_status()
        response.encoding = "utf-8"

        return BeautifulSoup(
            response.text,
            "html.parser",
        )

    def _parse_publication_date(
        self,
        date_text: str,
    ) -> str | None:
        """Convert an English publication date into ISO format."""

        clean_date = clean_text(
            date_text
        )

        try:
            publication_date = datetime.strptime(
                clean_date,
                "%d %B %Y",
            )
        except ValueError:
            return None

        # Step 3: normalize the publication date.
        return publication_date.date().isoformat()

    def _normalize_url(
        self,
        relative_url: str,
    ) -> str | None:
        """Build and validate one official publication URL."""

        absolute_url = urljoin(
            EU_AI_NEWS_URL,
            relative_url,
        )

        parsed_url = urlparse(
            absolute_url
        )

        if (
            parsed_url.scheme != "https"
            or parsed_url.netloc
            != EU_DIGITAL_STRATEGY_DOMAIN
            or not parsed_url.path.startswith(
                "/en/news/"
            )
        ):
            return None

        # Step 4: remove query parameters and fragments.
        return (
            f"{parsed_url.scheme}://"
            f"{parsed_url.netloc}"
            f"{parsed_url.path.rstrip('/')}"
        )

    def _extract_candidates(
        self,
        listing_page: BeautifulSoup,
    ) -> list[EUNewsCandidate]:
        """Extract publication candidates from the AI listing."""

        candidates_by_url: dict[
            str,
            EUNewsCandidate,
        ] = {}

        # Step 5: locate publication cards on the official listing.
        for card in listing_page.select(
            "article.ecl-content-item"
        ):
            title_link = card.select_one(
                "a[data-ecl-title-link]"
            )

            metadata = card.select(
                ".ecl-content-block__primary-meta-item"
            )

            if (
                title_link is None
                or len(metadata) < 2
            ):
                continue

            relative_url = title_link.get(
                "href"
            )

            if not relative_url:
                continue

            publication_url = self._normalize_url(
                relative_url
            )

            published_at = self._parse_publication_date(
                metadata[-1].get_text(
                    " ",
                    strip=True,
                )
            )

            title = clean_text(
                title_link.get_text(
                    " ",
                    strip=True,
                )
            )

            if (
                publication_url is None
                or published_at is None
                or not title
            ):
                continue

            candidate = EUNewsCandidate(
                title=title,
                url=publication_url,
                published_at=published_at,
            )

            # Step 6: remove repeated cards through their official URLs.
            candidates_by_url[publication_url] = (
                candidate
            )

        candidates = list(
            candidates_by_url.values()
        )

        # Step 7: explicitly sort candidates from newest to oldest.
        candidates.sort(
            key=lambda candidate: (
                candidate.published_at
            ),
            reverse=True,
        )

        return candidates

    def _extract_article(
        self,
        candidate: EUNewsCandidate,
    ) -> NewsItem | None:
        """Download and normalize one European AI publication."""

        article_page = self._get_page(
            candidate.url
        )

        title_element = article_page.find(
            "h1"
        )

        if title_element is None:
            return None

        title = clean_text(
            title_element.get_text(
                " ",
                strip=True,
            )
        )

        if not title:
            return None

        summary_element = article_page.select_one(
            "p.ecl-page-header-standardised__description"
        )

        summary = (
            clean_text(
                summary_element.get_text(
                    " ",
                    strip=True,
                )
            )
            if summary_element is not None
            else None
        )

        body_container = article_page.select_one(
            ".cnt-main-body"
        )

        text_blocks: list[str] = []
        seen_blocks: set[str] = set()

        # Step 8: extract meaningful paragraphs and list items.
        if body_container is not None:
            for element in body_container.select(
                "p, li"
            ):
                text_block = clean_text(
                    element.get_text(
                        " ",
                        strip=True,
                    )
                )

                if (
                    len(text_block) < 20
                    or text_block in seen_blocks
                ):
                    continue

                seen_blocks.add(
                    text_block
                )

                text_blocks.append(
                    text_block
                )

        body = (
            "\n\n".join(text_blocks)
            if text_blocks
            else None
        )

        if summary is None and text_blocks:
            summary = text_blocks[0]

        # Step 9: create the shared normalized news structure.
        return NewsItem(
            source="EU_AI_OFFICE",
            title=title,
            url=candidate.url,
            published_at=candidate.published_at,
            summary=summary,
            body=body,
            collected_at=datetime.now(
                timezone.utc
            ).isoformat(),
        )

    def collect(
        self,
        limit: int = 5,
    ) -> list[NewsItem]:
        """Collect the latest official European AI publications."""

        if limit <= 0:
            return []

        # Step 10: request the official Artificial Intelligence listing.
        listing_page = self._get_page(
            EU_AI_NEWS_URL,
            params={
                "topic": EU_AI_TOPIC_ID,
            },
        )

        candidates = self._extract_candidates(
            listing_page
        )

        news_items: list[NewsItem] = []

        # Step 11: download candidates until the limit is reached.
        for candidate in candidates:
            news_item = self._extract_article(
                candidate
            )

            if news_item is None:
                continue

            news_items.append(
                news_item
            )

            if len(news_items) >= limit:
                break

        # Step 12: preserve explicit newest-to-oldest ordering.
        news_items.sort(
            key=lambda item: (
                item.published_at or ""
            ),
            reverse=True,
        )

        return news_items