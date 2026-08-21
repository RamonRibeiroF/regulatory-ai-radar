from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from regulatory_ai_radar.entities import NewsItem


BIS_DOMAIN = "www.bis.org"

BIS_ALLOWED_DOMAINS = {
    "bis.org",
    "www.bis.org",
}

BIS_PUBLICATIONS_API_URL = (
    "https://www.bis.org/api/document_lists/"
    "bisih_publications.json"
)

BIS_PUBLICATION_PATH_PATTERN = re.compile(
    r"^/publ/[a-z0-9_-]+$"
)


def clean_text(text: str) -> str:
    """Remove unnecessary whitespace from text."""

    return " ".join(text.split())


@dataclass(frozen=True, slots=True)
class BISPublicationCandidate:
    """Represent a publication found in the official BIS list."""

    title: str
    path: str
    url: str
    published_at: str


class BISCollector:
    """Collect publications from the BIS Innovation Hub."""

    def __init__(self) -> None:
        # Step 1: create a reusable HTTP session.
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "RegulatoryAIRadar/0.1 "
                    "(educational and portfolio project)"
                ),
            }
        )

    def _get_json(
        self,
        url: str,
    ) -> dict[str, Any]:
        """Download and validate one official BIS JSON response."""

        # Step 2: request structured data from the official BIS API.
        response = self.session.get(
            url,
            headers={
                "Accept": "application/json",
            },
            timeout=(10, 30),
        )

        response.raise_for_status()

        payload = response.json()

        if not isinstance(
            payload,
            dict,
        ):
            raise ValueError(
                "The BIS API returned an invalid response."
            )

        return payload

    def _get_page(
        self,
        url: str,
    ) -> BeautifulSoup:
        """Download and parse one official BIS publication page."""

        # Step 3: request one official HTML publication page.
        response = self.session.get(
            url,
            headers={
                "Accept": (
                    "text/html,"
                    "application/xhtml+xml"
                ),
            },
            timeout=(10, 30),
        )

        response.raise_for_status()
        response.encoding = "utf-8"

        return BeautifulSoup(
            response.text,
            "html.parser",
        )

    def _normalize_path(
        self,
        publication_path: str,
    ) -> str | None:
        """Validate one official BIS publication path."""

        clean_path = publication_path.strip()

        if (
            BIS_PUBLICATION_PATH_PATTERN.fullmatch(
                clean_path
            )
            is None
        ):
            return None

        return clean_path

    def _build_publication_url(
        self,
        publication_path: str,
    ) -> str | None:
        """Build and validate an official BIS publication URL."""

        normalized_path = self._normalize_path(
            publication_path
        )

        if normalized_path is None:
            return None

        publication_url = (
            f"https://{BIS_DOMAIN}"
            f"{normalized_path}.htm"
        )

        parsed_url = urlparse(
            publication_url
        )

        if (
            parsed_url.scheme != "https"
            or parsed_url.netloc
            not in BIS_ALLOWED_DOMAINS
        ):
            return None

        # Step 4: return a canonical URL without parameters or fragments.
        return publication_url

    def _parse_publication_date(
        self,
        date_value: str,
    ) -> str | None:
        """Validate and normalize an ISO publication date."""

        try:
            publication_date = datetime.strptime(
                date_value.strip(),
                "%Y-%m-%d",
            )
        except ValueError:
            return None

        return publication_date.date().isoformat()

    def _extract_candidates(
        self,
        payload: dict[str, Any],
    ) -> list[BISPublicationCandidate]:
        """Extract publication candidates from the BIS API."""

        raw_publications = payload.get(
            "list"
        )

        if not isinstance(
            raw_publications,
            dict,
        ):
            return []

        candidates_by_url: dict[
            str,
            BISPublicationCandidate,
        ] = {}

        # Step 5: inspect every publication returned by the API.
        for raw_publication in raw_publications.values():
            if not isinstance(
                raw_publication,
                dict,
            ):
                continue

            raw_path = raw_publication.get(
                "path"
            )

            raw_title = raw_publication.get(
                "short_title"
            )

            raw_date = raw_publication.get(
                "publication_start_date"
            )

            if not all(
                isinstance(value, str)
                for value in (
                    raw_path,
                    raw_title,
                    raw_date,
                )
            ):
                continue

            publication_url = self._build_publication_url(
                raw_path
            )

            published_at = self._parse_publication_date(
                raw_date
            )

            title = clean_text(
                raw_title
            )

            if (
                publication_url is None
                or published_at is None
                or not title
            ):
                continue

            normalized_path = self._normalize_path(
                raw_path
            )

            if normalized_path is None:
                continue

            candidate = BISPublicationCandidate(
                title=title,
                path=normalized_path,
                url=publication_url,
                published_at=published_at,
            )

            # Step 6: remove duplicates through canonical official URLs.
            candidates_by_url[publication_url] = (
                candidate
            )

        candidates = list(
            candidates_by_url.values()
        )

        # Step 7: explicitly sort candidates from newest to oldest.
        candidates.sort(
            key=lambda candidate: (
                candidate.published_at,
                candidate.path,
            ),
            reverse=True,
        )

        return candidates

    def _extract_publication(
        self,
        candidate: BISPublicationCandidate,
    ) -> NewsItem | None:
        """Download and normalize one BIS publication."""

        publication_page = self._get_page(
            candidate.url
        )

        title_element = publication_page.find(
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

        summary_element = publication_page.select_one(
            'meta[name="description"]'
        )

        summary_value = (
            summary_element.get(
                "content"
            )
            if summary_element is not None
            else None
        )

        summary = (
            clean_text(
                str(summary_value)
            )
            if summary_value
            else None
        )

        content_container = publication_page.select_one(
            "#cmsContent"
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

        if summary is None and text_blocks:
            summary = text_blocks[0]

        # Step 9: create the shared normalized news structure.
        return NewsItem(
            source="BIS",
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
        """Collect the latest BIS Innovation Hub publications."""

        if limit <= 0:
            return []

        # Step 10: request the official BIS publication list.
        payload = self._get_json(
            BIS_PUBLICATIONS_API_URL
        )

        candidates = self._extract_candidates(
            payload
        )

        news_items: list[NewsItem] = []

        # Step 11: open candidates until the limit is reached.
        for candidate in candidates:
            news_item = self._extract_publication(
                candidate
            )

            if news_item is None:
                continue

            news_items.append(
                news_item
            )

            if len(news_items) >= limit:
                break

        # Step 12: preserve newest-to-oldest ordering.
        news_items.sort(
            key=lambda item: (
                item.published_at or "",
                item.url,
            ),
            reverse=True,
        )

        return news_items