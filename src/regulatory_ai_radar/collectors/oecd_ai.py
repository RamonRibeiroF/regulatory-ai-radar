from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import requests
from bs4 import BeautifulSoup

from regulatory_ai_radar.entities import NewsItem


OECD_AI_DOMAIN = "oecd.ai"

OECD_AI_PUBLICATIONS_URL = (
    "https://oecd.ai/en/ai-publications"
)

OECD_AI_API_URL = (
    "https://wp.oecd.ai/wp-json/wp/v2/ai-publications"
)

OECD_AI_SLUG_PATTERN = re.compile(
    r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
)


def clean_text(text: str) -> str:
    """Remove unnecessary whitespace from text."""

    return " ".join(text.split())


@dataclass(frozen=True, slots=True)
class OECDAIPublicationCandidate:
    """Represent one publication returned by OECD.AI."""

    title: str
    url: str
    published_at: str
    summary: str | None
    body: str | None


class OECDAICollector:
    """Collect recent papers from the official OECD.AI platform."""

    def __init__(self) -> None:
        # Step 1: create a reusable HTTP session.
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "RegulatoryAIRadar/0.1 "
                    "(educational and portfolio project)"
                ),
                "Accept": "application/json",
            }
        )

    def _get_json(
        self,
        url: str,
        params: dict[str, object],
    ) -> list[dict[str, Any]]:
        """Request and validate one official OECD.AI JSON list."""

        # Step 2: request the public OECD.AI publication endpoint.
        response = self.session.get(
            url,
            params=params,
            timeout=(10, 30),
        )

        response.raise_for_status()

        payload = response.json()

        if not isinstance(payload, list):
            raise ValueError(
                "The OECD.AI API returned an invalid publication list."
            )

        return [
            item
            for item in payload
            if isinstance(item, dict)
        ]

    def _parse_publication_date(
        self,
        date_value: str,
    ) -> str | None:
        """Validate and normalize an OECD.AI publication date."""

        try:
            publication_date = datetime.fromisoformat(
                date_value.strip().replace("Z", "+00:00")
            )
        except ValueError:
            return None

        # Step 3: keep the publication date in ISO format.
        return publication_date.date().isoformat()

    def _build_publication_url(
        self,
        slug: str,
    ) -> str | None:
        """Build one canonical public OECD.AI publication URL."""

        clean_slug = slug.strip().lower()

        if OECD_AI_SLUG_PATTERN.fullmatch(clean_slug) is None:
            return None

        # Step 4: expose the public frontend instead of the API URL.
        return (
            f"https://{OECD_AI_DOMAIN}/en/ai-publications/"
            f"{clean_slug}"
        )

    def _extract_plain_text(
        self,
        html: str,
    ) -> str | None:
        """Convert a short HTML fragment into normalized plain text."""

        text = clean_text(
            BeautifulSoup(
                html,
                "html.parser",
            ).get_text(
                " ",
                strip=True,
            )
        )

        return text or None

    def _extract_body(
        self,
        html: str,
    ) -> str | None:
        """Extract meaningful paragraphs from publication content."""

        content = BeautifulSoup(
            html,
            "html.parser",
        )

        text_blocks: list[str] = []
        seen_blocks: set[str] = set()

        # Step 5: retain meaningful paragraphs and list items.
        for element in content.select("p, li"):
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

            seen_blocks.add(text_block)
            text_blocks.append(text_block)

        return (
            "\n\n".join(text_blocks)
            if text_blocks
            else None
        )

    def _extract_candidates(
        self,
        payload: list[dict[str, Any]],
    ) -> list[OECDAIPublicationCandidate]:
        """Normalize publication records returned by OECD.AI."""

        candidates_by_url: dict[
            str,
            OECDAIPublicationCandidate,
        ] = {}

        # Step 6: inspect every structured publication record.
        for item in payload:
            raw_slug = item.get("slug")
            raw_date = item.get("date")
            title_container = item.get("title")
            excerpt_container = item.get("excerpt")
            content_container = item.get("content")

            if (
                not isinstance(raw_slug, str)
                or not isinstance(raw_date, str)
                or not isinstance(title_container, dict)
            ):
                continue

            raw_title = title_container.get("rendered")

            if not isinstance(raw_title, str):
                continue

            publication_url = self._build_publication_url(
                raw_slug
            )

            published_at = self._parse_publication_date(
                raw_date
            )

            title = self._extract_plain_text(raw_title)

            raw_summary = (
                excerpt_container.get("rendered")
                if isinstance(excerpt_container, dict)
                else None
            )

            summary = (
                self._extract_plain_text(raw_summary)
                if isinstance(raw_summary, str)
                else None
            )

            raw_body = (
                content_container.get("rendered")
                if isinstance(content_container, dict)
                else None
            )

            body = (
                self._extract_body(raw_body)
                if isinstance(raw_body, str)
                else None
            )

            if (
                publication_url is None
                or published_at is None
                or title is None
            ):
                continue

            if summary is None and body:
                summary = body.split("\n\n", maxsplit=1)[0]

            candidate = OECDAIPublicationCandidate(
                title=title,
                url=publication_url,
                published_at=published_at,
                summary=summary,
                body=body,
            )

            # Step 7: remove duplicates through canonical URLs.
            candidates_by_url[publication_url] = candidate

        candidates = list(candidates_by_url.values())

        # Step 8: explicitly sort candidates from newest to oldest.
        candidates.sort(
            key=lambda candidate: candidate.published_at,
            reverse=True,
        )

        return candidates

    def _to_news_item(
        self,
        candidate: OECDAIPublicationCandidate,
    ) -> NewsItem:
        """Convert one candidate into the shared news structure."""

        # Step 9: create the normalized cross-source structure.
        return NewsItem(
            source="OECD_AI",
            title=candidate.title,
            url=candidate.url,
            published_at=candidate.published_at,
            summary=candidate.summary,
            body=candidate.body,
            collected_at=datetime.now(
                timezone.utc
            ).isoformat(),
        )

    def collect(
        self,
        limit: int = 5,
    ) -> list[NewsItem]:
        """Collect the most recent official OECD.AI publications."""

        if limit <= 0:
            return []

        # Step 10: request enough recent records for validation.
        request_size = min(
            max(limit * 2, 10),
            100,
        )

        payload = self._get_json(
            OECD_AI_API_URL,
            params={
                "per_page": request_size,
                "page": 1,
                "orderby": "date",
                "order": "desc",
                "_fields": (
                    "id,date,slug,title,excerpt,content"
                ),
            },
        )

        candidates = self._extract_candidates(payload)

        # Step 11: select only the requested recent publications.
        selected_candidates = candidates[:limit]

        news_items = [
            self._to_news_item(candidate)
            for candidate in selected_candidates
        ]

        # Step 12: preserve newest-to-oldest ordering.
        news_items.sort(
            key=lambda item: item.published_at or "",
            reverse=True,
        )

        return news_items
