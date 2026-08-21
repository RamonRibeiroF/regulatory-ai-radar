from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from regulatory_ai_radar.entities import NewsItem


IAPP_DOMAIN = "iapp.org"

IAPP_ALLOWED_DOMAINS = {
    "iapp.org",
    "www.iapp.org",
}

IAPP_NEWS_URL = "https://iapp.org/news"

IAPP_INITIAL_RESULTS_PREFIX = (
    'window[Symbol.for("InstantSearchInitialResults")] = '
)

IAPP_ARTICLE_PATH_PATTERN = re.compile(
    r"^/news/a/[a-z0-9][a-z0-9-]*$"
)


def clean_text(text: str) -> str:
    """Remove unnecessary whitespace from text."""

    return " ".join(text.split())


@dataclass(frozen=True, slots=True)
class IAPPNewsCandidate:
    """Represent one publication found in the IAPP news page."""

    title: str
    url: str
    published_at: str
    summary: str | None
    body: str | None
    is_member_gated: bool


class IAPPCollector:
    """Collect recent news from the official IAPP website."""

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
        """Download and parse one official IAPP page."""

        # Step 2: request the public IAPP news page.
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

    def _extract_initial_payload(
        self,
        news_page: BeautifulSoup,
    ) -> dict[str, Any]:
        """Extract the structured search results from the page."""

        # Step 3: locate the public structured results block.
        for script in news_page.find_all(
            "script"
        ):
            script_text = (
                script.string
                or script.get_text()
            )

            if (
                IAPP_INITIAL_RESULTS_PREFIX
                not in script_text
            ):
                continue

            payload_text = script_text.split(
                IAPP_INITIAL_RESULTS_PREFIX,
                maxsplit=1,
            )[1].strip()

            if payload_text.endswith(";"):
                payload_text = payload_text[:-1]

            try:
                payload = json.loads(
                    payload_text
                )
            except json.JSONDecodeError as error:
                raise ValueError(
                    "The IAPP news page returned invalid "
                    "structured data."
                ) from error

            if not isinstance(
                payload,
                dict,
            ):
                break

            return payload

        raise ValueError(
            "The IAPP structured news results were not found."
        )

    def _extract_hits(
        self,
        payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Return valid news hits from the structured payload."""

        search_result = payload.get(
            "all_article_date_desc"
        )

        if not isinstance(
            search_result,
            dict,
        ):
            return []

        result_groups = search_result.get(
            "results"
        )

        if (
            not isinstance(
                result_groups,
                list,
            )
            or not result_groups
            or not isinstance(
                result_groups[0],
                dict,
            )
        ):
            return []

        raw_hits = result_groups[0].get(
            "hits"
        )

        if not isinstance(
            raw_hits,
            list,
        ):
            return []

        # Step 4: retain only dictionary-shaped news records.
        return [
            hit
            for hit in raw_hits
            if isinstance(
                hit,
                dict,
            )
        ]

    def _normalize_url(
        self,
        article_url: str,
    ) -> str | None:
        """Build and validate one official IAPP article URL."""

        absolute_url = urljoin(
            IAPP_NEWS_URL,
            article_url,
        )

        parsed_url = urlparse(
            absolute_url
        )

        if (
            parsed_url.scheme != "https"
            or parsed_url.netloc
            not in IAPP_ALLOWED_DOMAINS
            or IAPP_ARTICLE_PATH_PATTERN.fullmatch(
                parsed_url.path
            )
            is None
        ):
            return None

        # Step 5: remove parameters and use one canonical domain.
        return (
            f"https://{IAPP_DOMAIN}"
            f"{parsed_url.path}"
        )

    def _parse_publication_date(
        self,
        date_value: str,
    ) -> str | None:
        """Validate and normalize one publication date."""

        try:
            publication_date = datetime.strptime(
                date_value.strip(),
                "%Y-%m-%d",
            )
        except ValueError:
            return None

        return publication_date.date().isoformat()

    def _extract_body(
        self,
        article_body: object,
    ) -> str | None:
        """Extract public text from structured article sections."""

        if not isinstance(
            article_body,
            list,
        ):
            return None

        text_blocks: list[str] = []
        seen_blocks: set[str] = set()

        # Step 6: read public rich-text sections from the article.
        for section in article_body:
            if not isinstance(
                section,
                dict,
            ):
                continue

            rich_text_container = section.get(
                "rte"
            )

            if not isinstance(
                rich_text_container,
                dict,
            ):
                continue

            rich_text = rich_text_container.get(
                "rich_text_editor"
            )

            if not isinstance(
                rich_text,
                str,
            ):
                continue

            content = BeautifulSoup(
                rich_text,
                "html.parser",
            )

            for element in content.select(
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

        return (
            "\n\n".join(text_blocks)
            if text_blocks
            else None
        )

    def _extract_candidates(
        self,
        payload: dict[str, Any],
    ) -> list[IAPPNewsCandidate]:
        """Normalize the publications found in the IAPP results."""

        candidates_by_url: dict[
            str,
            IAPPNewsCandidate,
        ] = {}

        # Step 7: inspect every recent result.
        for hit in self._extract_hits(
            payload
        ):
            article_details = hit.get(
                "article_details"
            )

            if not isinstance(
                article_details,
                dict,
            ):
                continue

            raw_title = article_details.get(
                "headline"
            )

            raw_date = article_details.get(
                "date"
            )

            raw_url = hit.get(
                "url"
            )

            if not all(
                isinstance(value, str)
                for value in (
                    raw_title,
                    raw_date,
                    raw_url,
                )
            ):
                continue

            title = clean_text(
                raw_title
            )

            published_at = self._parse_publication_date(
                raw_date
            )

            article_url = self._normalize_url(
                raw_url
            )

            raw_summary = hit.get(
                "entry_summary"
            )

            summary = (
                clean_text(
                    raw_summary
                )
                if isinstance(
                    raw_summary,
                    str,
                )
                and raw_summary.strip()
                else None
            )

            is_member_gated = bool(
                hit.get(
                    "member_gated",
                    False,
                )
            )

            # Step 8: avoid extracting protected member-only bodies.
            body = (
                None
                if is_member_gated
                else self._extract_body(
                    hit.get(
                        "article_body"
                    )
                )
            )

            if (
                not title
                or published_at is None
                or article_url is None
            ):
                continue

            candidate = IAPPNewsCandidate(
                title=title,
                url=article_url,
                published_at=published_at,
                summary=summary,
                body=body,
                is_member_gated=is_member_gated,
            )

            # Step 9: remove duplicates through canonical URLs.
            candidates_by_url[article_url] = (
                candidate
            )

        candidates = list(
            candidates_by_url.values()
        )

        # Step 10: explicitly sort candidates from newest to oldest.
        candidates.sort(
            key=lambda candidate: (
                candidate.published_at
            ),
            reverse=True,
        )

        return candidates

    def _to_news_item(
        self,
        candidate: IAPPNewsCandidate,
    ) -> NewsItem:
        """Convert one IAPP candidate into the shared structure."""

        # Step 11: create the shared normalized news structure.
        return NewsItem(
            source="IAPP",
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
        """Collect the most recent official IAPP news articles."""

        if limit <= 0:
            return []

        # Step 12: request and decode the official news listing.
        news_page = self._get_page(
            IAPP_NEWS_URL
        )

        payload = self._extract_initial_payload(
            news_page
        )

        candidates = self._extract_candidates(
            payload
        )

        # Step 13: select only the requested recent publications.
        selected_candidates = candidates[
            :limit
        ]

        news_items = [
            self._to_news_item(
                candidate
            )
            for candidate in selected_candidates
        ]

        # Step 14: preserve newest-to-oldest ordering.
        news_items.sort(
            key=lambda item: (
                item.published_at or ""
            ),
            reverse=True,
        )

        return news_items