from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from regulatory_ai_radar.entities import NewsItem


FCA_SEARCH_URL = "https://www.fca.org.uk/search-results"
FCA_ALLOWED_HOSTS = {"fca.org.uk", "www.fca.org.uk"}
FCA_AI_PATTERN = re.compile(
    r"artificial intelligence|machine learning|\bAI\b|AI Lab|agentic",
    re.IGNORECASE,
)


def clean_text(text: str) -> str:
    """Normalize whitespace in text extracted from HTML."""

    return " ".join(text.split())


@dataclass(frozen=True, slots=True)
class FCAPublicationCandidate:
    """Represent one FCA publication about artificial intelligence."""

    title: str
    url: str
    published_at: str
    summary: str | None


class FCAAiLabCollector:
    """Collect recent AI publications from the official FCA search."""

    def __init__(self) -> None:
        # Passo 1: reutilizar uma sessão HTTP identificada.
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "RegulatoryAIRadar/0.1 "
                    "(educational and portfolio project)"
                )
            }
        )

    def _get_page(
        self, url: str, params: dict[str, object] | None = None
    ) -> BeautifulSoup:
        """Request one official FCA page."""

        response = self.session.get(
            url, params=params, timeout=(10, 30)
        )
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def _normalize_url(self, href: str) -> str | None:
        """Accept only canonical FCA HTTPS URLs."""

        parsed = urlparse(href)
        if (
            parsed.scheme != "https"
            or parsed.netloc.lower() not in FCA_ALLOWED_HOSTS
        ):
            return None
        return parsed._replace(query="", fragment="").geturl()

    def _parse_date(self, text: str) -> str | None:
        """Convert an FCA published date to ISO format."""

        match = re.search(r"(\d{2}/\d{2}/\d{4})", text)
        if match is None:
            return None
        try:
            return datetime.strptime(
                match.group(1), "%d/%m/%Y"
            ).date().isoformat()
        except ValueError:
            return None

    def _extract_candidates(
        self, pages: list[BeautifulSoup]
    ) -> list[FCAPublicationCandidate]:
        """Extract strict AI matches from FCA search results."""

        candidates_by_url: dict[str, FCAPublicationCandidate] = {}

        # Passo 2: filtrar resultados com termos explícitos de IA.
        for page in pages:
            for item in page.select("li.search-item"):
                title_node = item.select_one("a.search-item__clickthrough")
                date_node = item.select_one(".published-date")
                summary_node = item.select_one(".search-item__body")
                type_node = item.select_one(".meta-item.type")

                if title_node is None or date_node is None:
                    continue

                title = clean_text(title_node.get_text(" ", strip=True))
                summary = (
                    clean_text(summary_node.get_text(" ", strip=True))
                    if summary_node is not None
                    else None
                )
                result_type = (
                    clean_text(type_node.get_text(" ", strip=True)).lower()
                    if type_node is not None
                    else ""
                )

                if (
                    result_type == "warnings"
                    or FCA_AI_PATTERN.search(f"{title} {summary or ''}")
                    is None
                ):
                    continue

                url = self._normalize_url(title_node.get("href", ""))
                published_at = self._parse_date(
                    date_node.get_text(" ", strip=True)
                )
                if url is None or published_at is None:
                    continue

                candidates_by_url[url] = FCAPublicationCandidate(
                    title=title,
                    url=url,
                    published_at=published_at,
                    summary=summary or None,
                )

        candidates = list(candidates_by_url.values())
        candidates.sort(key=lambda item: item.published_at, reverse=True)
        return candidates

    def _extract_body(self, soup: BeautifulSoup) -> str | None:
        """Extract meaningful paragraphs from an FCA publication."""

        paragraphs: list[str] = []
        seen: set[str] = set()
        root = soup.select_one("[role=main]") or soup

        # Passo 3: preservar parágrafos informativos sem duplicação.
        for node in root.select("article p"):
            paragraph = clean_text(node.get_text(" ", strip=True))
            if len(paragraph) < 30 or paragraph in seen:
                continue
            seen.add(paragraph)
            paragraphs.append(paragraph)

        return "\n\n".join(paragraphs) if paragraphs else None

    def collect(self, limit: int = 5) -> list[NewsItem]:
        """Collect the latest official FCA AI publications."""

        if limit <= 0:
            return []

        pages: list[BeautifulSoup] = []
        start = 1

        # Passo 4: consultar páginas recentes até atingir o limite.
        while len(self._extract_candidates(pages)) < limit and start <= 41:
            pages.append(
                self._get_page(
                    FCA_SEARCH_URL,
                    params={
                        "search_term": "artificial intelligence",
                        "sort_by": "dmetaZ",
                        "start": start,
                    },
                )
            )
            start += 10

        candidates = self._extract_candidates(pages)[:limit]
        collected_at = datetime.now(timezone.utc).isoformat()
        news_items: list[NewsItem] = []

        # Passo 5: enriquecer cada resultado com o texto oficial.
        for candidate in candidates:
            page = self._get_page(candidate.url)
            news_items.append(
                NewsItem(
                    source="FCA_AI_LAB",
                    title=candidate.title,
                    url=candidate.url,
                    published_at=candidate.published_at,
                    summary=candidate.summary,
                    body=self._extract_body(page),
                    collected_at=collected_at,
                )
            )

        return news_items
