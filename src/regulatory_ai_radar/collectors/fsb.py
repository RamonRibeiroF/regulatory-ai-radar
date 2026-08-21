from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from regulatory_ai_radar.entities import NewsItem


FSB_DOMAIN = "www.fsb.org"

FSB_ALLOWED_DOMAINS = {
    "fsb.org",
    "www.fsb.org",
}

FSB_FINANCIAL_INNOVATION_URL = (
    "https://www.fsb.org/"
    "policy_areas/financial-innovation/"
)

FSB_PUBLICATION_PATH_PATTERN = re.compile(
    r"^/\d{4}/\d{2}/"
)


def clean_text(text: str) -> str:
    """Remove unnecessary whitespace from text."""

    return " ".join(text.split())


@dataclass(frozen=True, slots=True)
class FSBPublicationCandidate:
    """Represent a publication found on the official FSB listing."""

    title: str
    url: str
    published_at: str
    summary: str | None


class FSBCollector:
    """Collect financial innovation publications from the FSB."""

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
    ) -> BeautifulSoup:
        """Download and parse one official FSB page."""

        # Step 2: request one official HTML page.
        response = self.session.get(
            url,
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
        publication_url: str,
    ) -> str | None:
        """Build and validate one official FSB publication URL."""

        absolute_url = urljoin(
            FSB_FINANCIAL_INNOVATION_URL,
            publication_url,
        )

        parsed_url = urlparse(
            absolute_url
        )

        if (
            parsed_url.scheme != "https"
            or parsed_url.netloc
            not in FSB_ALLOWED_DOMAINS
            or FSB_PUBLICATION_PATH_PATTERN.match(
                parsed_url.path
            )
            is None
        ):
            return None

        # Step 4: remove query parameters and URL fragments.
        return (
            f"{parsed_url.scheme}://"
            f"{FSB_DOMAIN}"
            f"{parsed_url.path.rstrip('/')}/"
        )

    def _extract_candidates(
        self,
        listing_page: BeautifulSoup,
    ) -> list[FSBPublicationCandidate]:
        """Extract candidates from the financial innovation listing."""

        candidates_by_url: dict[
            str,
            FSBPublicationCandidate,
        ] = {}

        # Step 5: locate publication cards in the official listing.
        for card in listing_page.select(
            "main .post-excerpt.post-excerpt-default"
        ):
            title_link = card.select_one(
                ".post-title a"
            )

            date_element = card.select_one(
                ".post-date"
            )

            summary_element = card.select_one(
                ".media-excerpt"
            )

            if (
                title_link is None
                or date_element is None
            ):
                continue

            raw_url = title_link.get(
                "href"
            )

            if not raw_url:
                continue

            publication_url = self._normalize_url(
                raw_url
            )

            published_at = self._parse_publication_date(
                date_element.get_text(
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

            if (
                publication_url is None
                or published_at is None
                or not title
            ):
                continue

            candidate = FSBPublicationCandidate(
                title=title,
                url=publication_url,
                published_at=published_at,
                summary=summary,
            )

            # Step 6: remove repeated cards through official URLs.
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
        candidate: FSBPublicationCandidate,
    ) -> NewsItem | None:
        """Download and normalize one FSB publication."""

        article_page = self._get_page(
            candidate.url
        )

        title_element = article_page.find(
            "h1"
        )

        title = (
            clean_text(
                title_element.get_text(
                    " ",
                    strip=True,
                )
            )
            if title_element is not None
            else candidate.title
        )

        if not title:
            return None

        content_container = article_page.select_one(
            "main article section.post-content"
        )

        if content_container is None:
            content_container = article_page.select_one(
                "main article"
            )

        text_blocks: list[str] = []
        seen_blocks: set[str] = set()

        # Step 8: extract meaningful paragraphs and list items.
        if content_container is not None:
            for element in content_container.select(
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

        summary = candidate.summary

        if summary is None and text_blocks:
            summary = text_blocks[0]

        # Step 9: create the shared normalized news structure.
        return NewsItem(
            source="FSB",
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
        """Collect the latest FSB financial innovation publications."""

        if limit <= 0:
            return []

        # Step 10: request the official financial innovation listing.
        listing_page = self._get_page(
            FSB_FINANCIAL_INNOVATION_URL
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